import streamlit as st
import requests
from datetime import datetime
import time

# Configuration
MCP_SERVER_URL = "http://localhost:8000"  # Adresse de votre serveur MCP
TIMEOUT = 30  # Timeout en secondes

# Initialisation de l'état de session
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
    st.session_state.session_id = f"streamlit-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

# Fonction pour vérifier le serveur
def check_server():
    try:
        response = requests.get(f"{MCP_SERVER_URL}/status", timeout=5)
        return response.status_code == 200
    except:
        return False

# Fonction pour envoyer un message
def send_to_mcp(message: str, session_id: str):
    payload = {
        "content": message,
        "session_id": session_id
    }
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/chat",
            json=payload,
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erreur du serveur: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")
        return None

# Interface utilisateur
st.title("💬 Chat MCP Interface")
st.caption(f"Session ID: {st.session_state.session_id}")

# Vérification du serveur
if not check_server():
    st.error("⚠️ Serveur MCP indisponible. Veuillez démarrer le serveur.")
    st.stop()

# Affichage de l'historique
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("timestamp"):
            st.caption(f"À {message['timestamp']}")

# Gestion du nouvel input
if prompt := st.chat_input("Tapez votre message..."):
    # Ajout du message utilisateur
    user_message = {
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.conversation.append(user_message)
    
    # Affichage immédiat
    with st.chat_message("user"):
        st.write(prompt)
        st.caption(f"À {user_message['timestamp']}")
    
    # Envoi au serveur MCP
    with st.spinner("Le serveur MCP traite votre demande..."):
        start_time = time.time()
        response = send_to_mcp(prompt, st.session_state.session_id)
        elapsed_time = round(time.time() - start_time, 2)
        
        if response:
            assistant_message = {
                "role": "assistant",
                "content": response.get("content", "Pas de réponse"),
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.conversation.append(assistant_message)
            
            # Affichage de la réponse
            with st.chat_message("assistant"):
                st.write(assistant_message["content"])
                st.caption(f"Réponse reçue en {elapsed_time}s à {assistant_message['timestamp']}")
                
                if response.get("tools_used"):
                    st.info(f"Outils utilisés: {', '.join(response['tools_used'])}")
        else:
            st.error("Aucune réponse reçue du serveur MCP")
