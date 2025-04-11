# azure_openai_client.py
import os
from openai import AzureOpenAI
from typing import Dict, List, Optional

class AzureOpenAIClient:
    def __init__(self):
        self.client = AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY")
        )
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo")

    def chat_completion(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 800
    ) -> Dict:
        """Simplified Azure OpenAI chat completion"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Format response to match your existing structure
            message = response.choices[0].message
            return {
                "message": {
                    "role": message.role,
                    "content": message.content,
                    "tool_calls": [
                        {
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments
                            }
                        } for call in (message.tool_calls or [])
                    ]
                }
            }
        except Exception as e:
            raise RuntimeError(f"Azure OpenAI error: {str(e)}")

# Alternative minimal version for direct function calling
def azure_openai_call(
    messages: List[Dict],
    tools_schema: Optional[List[Dict]] = None
) -> Dict:
    """
    Minimal Azure OpenAI call matching your existing interface
    Returns dict with structure:
    {
        "message": {
            "role": str,
            "content": Optional[str],
            "tool_calls": Optional[List]
        }
    }
    """
    client = AzureOpenAI(
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY")
    )
    
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=messages,
        tools=tools_schema or []
    )
    
    msg = response.choices[0].message
    return {
        "message": {
            "role": msg.role,
            "content": msg.content,
            "tool_calls": [
                {
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments
                    }
                } for call in (msg.tool_calls or [])
            ]
        }
    }
