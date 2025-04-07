import ollama
import json

# Initialisation du client Ollama avec le modèle de langage local
client = ollama.Client(model="nom_du_modele")

# Fonction pour interagir avec le serveur MCP
def interagir_avec_mcp(outil, arguments):
    # Création de la requête MCP
    requete = {
        "tool": outil,
        "arguments": arguments
    }
    # Envoi de la requête au serveur MCP
    reponse = client.call_tool(json.dumps(requete))
    return reponse

# Exemple d'utilisation
if __name__ == "__main__":
    # Appel de l'outil 'obtenir_heure_actuelle' sans arguments
    resultat = interagir_avec_mcp("obtenir_heure_actuelle", {})
    print(resultat)
