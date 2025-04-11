from fastapi import FastAPI, HTTPException, Request
from typing import Dict, List, Any, Optional
import importlib.util
import os
import glob
import json
import ollama
from pydantic import BaseModel
import uvicorn

# Constants
TOOL_DIR = 'tool'
MODEL_NAME = 'llama3.1'
PORT = 8000
HOST = "0.0.0.0"

app = FastAPI(title="Modular Chatbot Platform (MCP) Server",
              description="Serveur MCP pour exécuter des conversations avec LLM et outils externes")

# Models
class UserMessage(BaseModel):
    content: str
    session_id: Optional[str] = None

class BotResponse(BaseModel):
    content: str
    session_id: str
    tool_used: Optional[str] = None
    tool_result: Optional[Any] = None

class ToolRegistration(BaseModel):
    tool_path: str

# State
active_sessions: Dict[str, List[Dict]] = {}
available_tools: Dict[str, Dict[str, Any]] = {}

# Utility functions
def load_module(module_path: str) -> Dict[str, Any]:
    """Loads a module from a file path and returns its function and schema."""
    spec = importlib.util.spec_from_file_location(os.path.basename(module_path), module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    return {
        'function': mod.function_call,
        'schema': getattr(mod, 'function_schema', {
            "type": "object",
            "properties": {},
            "required": []
        })
    }

def load_tool_modules() -> Dict[str, Dict[str, Any]]:
    """Loads all tool modules from the tool directory."""
    modules = {}
    for module_path in glob.glob(os.path.join(TOOL_DIR, 'tool-*.py')):
        try:
            module_name = os.path.splitext(os.path.basename(module_path))[0].replace('tool-', '')
            modules[module_name] = load_module(module_path)
        except Exception as e:
            print(f"Error loading tool {module_path}: {str(e)}")
    return modules

def initialize_tools() -> List[Dict]:
    """Initialize the tools schema for LLM conversation."""
    return [
        {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": f"Executes the {tool_name} tool",
                "parameters": tool_info['schema']
            }
        } for tool_name, tool_info in available_tools.items()
    ]

def call_llm(messages: List[Dict], session_id: str) -> dict:
    """Calls the LLM with the given messages."""
    try:
        tools_schema = initialize_tools()
        return ollama.chat(
            model=MODEL_NAME, 
            messages=messages, 
            tools=tools_schema, 
            stream=False
        )
    except ollama.ResponseError as e:
        print(f"Ollama error ({e.status_code}): {e.error}")
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def process_tool_calls(tool_calls: List[Dict], session_id: str) -> List[Dict]:
    """Process tool calls and return results."""
    results = []
    for call in tool_calls:
        tool_name = call['function']['name']
        print(f"Tool call detected: {tool_name}")
        
        if tool_name in available_tools:
            tool_func = available_tools[tool_name]['function']
            try:
                args_str = call['function'].get('arguments', '{}')
                args = json.loads(args_str) if isinstance(args_str, str) else args_str
                
                print(f"Executing tool {tool_name} with args: {args}")
                
                result = tool_func(**args)
                print(f"Tool result: {result}")
                
                results.append({
                    "tool_name": tool_name,
                    "content": str(result),
                    "args": args
                })
            except Exception as e:
                print(f"Tool execution failed: {str(e)}")
                results.append({
                    "tool_name": tool_name,
                    "content": f"Error: {str(e)}",
                    "args": args
                })
        else:
            print(f"Tool {tool_name} not implemented")
            results.append({
                "tool_name": tool_name,
                "content": "Tool not found",
                "args": {}
            })
    
    # Format tool responses for the conversation
    return [{
        'role': 'tool',
        'content': f"{res['tool_name']} returned: {res['content']}",
        'name': res['tool_name']
    } for res in results]

def get_session(session_id: str) -> List[Dict]:
    """Get or create a conversation session."""
    if session_id not in active_sessions:
        active_sessions[session_id] = []
    return active_sessions[session_id]

# API Endpoints
@app.get("/status")
async def status():
    """Check server status."""
    return {
        "status": "running",
        "model": MODEL_NAME,
        "loaded_tools": list(available_tools.keys()),
        "active_sessions": len(active_sessions)
    }

@app.post("/register_tool")
async def register_tool(tool: ToolRegistration):
    """Register a new tool dynamically."""
    try:
        tool_name = os.path.splitext(os.path.basename(tool.tool_path))[0].replace('tool-', '')
        available_tools[tool_name] = load_module(tool.tool_path)
        return {"message": f"Tool {tool_name} registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Tool registration failed: {str(e)}")

@app.post("/chat")
async def chat(user_msg: UserMessage) -> BotResponse:
    """Handle a chat message with optional tool use."""
    session_id = user_msg.session_id or "default"
    conversation = get_session(session_id)
    
    # Add user message to conversation
    conversation.append({'role': 'user', 'content': user_msg.content})
    
    # Get initial response from LLM
    response = call_llm(conversation, session_id)
    
    if not response:
        raise HTTPException(status_code=500, detail="Failed to get LLM response")
    
    # Handle tool calls if any
    if tool_calls := response['message'].get('tool_calls'):
        conversation.append(response['message'])
        
        # Process tool calls
        tool_responses = process_tool_calls(tool_calls, session_id)
        
        # Add tool responses to conversation
        for resp in tool_responses:
            conversation.append(resp)
        
        # Get final response after tool execution
        final_response = call_llm(conversation, session_id)
        if final_response:
            conversation.append(final_response['message'])
            content = final_response['message']['content']
        else:
            raise HTTPException(status_code=500, detail="Failed to get final response after tool execution")
        
        return BotResponse(
            content=content,
            session_id=session_id,
            tool_used=tool_calls[0]['function']['name'],
            tool_result=tool_responses[0]['content']
        )
    else:
        # Direct response without tools
        conversation.append(response['message'])
        return BotResponse(
            content=response['message']['content'],
            session_id=session_id
        )

@app.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get the full conversation for a session."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return active_sessions[session_id]

@app.delete("/conversation/{session_id}")
async def delete_conversation(session_id: str):
    """Delete a conversation session."""
    if session_id in active_sessions:
        del active_sessions[session_id]
    return {"message": f"Session {session_id} deleted"}

# Initialization
def initialize_server():
    """Initialize the server with tools and configuration."""
    global available_tools
    available_tools = load_tool_modules()
    
    print(f"Starting MCP server with {len(available_tools)} tools loaded:")
    for tool_name in available_tools:
        print(f" - {tool_name}")

    if not os.path.exists(TOOL_DIR):
        os.makedirs(TOOL_DIR)
        print(f"Created tool directory: {TOOL_DIR}")

if __name__ == "__main__":
    initialize_server()
    uvicorn.run(app, host=HOST, port=PORT)
