import streamlit as st
import pandas as pd

# Titre de l'application
st.title("MCP : Model Context Protocol")

# Introduction
st.write("Le MCP est un protocole qui permet d'intégrer différents outils et services pour fournir une plateforme flexible et extensible.")

# Diagramme de l'architecture MCP
st.write("### Architecture MCP")
st.image("mcp_architecture.png")  # Image de l'architecture MCP

# Explication des composants MCP
st.write("### Composants MCP")
st.write("Le MCP est composé de plusieurs éléments :")
st.write("* **MCP Server** : Le serveur MCP qui gère les requêtes et les réponses entre les clients et les outils/services.")
st.write("* **Tool** : Les outils qui fournissent des fonctionnalités spécifiques, telles que le traitement de langage naturel, le stockage de données, etc.")
st.write("* **LLM** : Le modèle de langage qui fournit des capacités de traitement de langage naturel.")
st.write("* **Storage** : Le stockage de données qui permet de stocker et de récupérer des données.")

# Animation de l'interaction entre les composants MCP
st.write("### Interaction entre les composants MCP")
st.write("Voici une animation qui montre comment les composants MCP interagissent :")

# Animation
def animate_mcp_interaction():
    st.write("1. Le client envoie une requête au MCP Server")
    st.image("mcp_request.png")
    st.write("2. Le MCP Server dirige la requête vers l'outil approprié")
    st.image("mcp_tool.png")
    st.write("3. L'outil traite la requête et renvoie une réponse au MCP Server")
    st.image("mcp_response.png")
    st.write("4. Le MCP Server renvoie la réponse au client")
    st.image("mcp_client_response.png")

animate_mcp_interaction()

# Conclusion
st.write("En résumé, le MCP est un protocole qui permet d'intégrer différents outils et services pour fournir une plateforme flexible et extensible.")
