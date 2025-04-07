from mcp.server import Server
import datetime

# Initialisation du serveur MCP avec un namespace unique
mcp = Server("mon_namespace")

# Définition d'un outil MCP pour obtenir l'heure actuelle
@mcp.tool()
def obtenir_heure_actuelle() -> str:
    """
    Renvoie l'heure actuelle sous forme de chaîne de caractères.
    """
    heure_actuelle = datetime.datetime.now().strftime("%H:%M:%S")
    return f"L'heure actuelle est {heure_actuelle}."

# Démarrage du serveur MCP
if __name__ == "__main__":
    mcp.run()
