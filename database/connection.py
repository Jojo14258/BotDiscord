"""
Gestion de la connexion à la base de données
"""
import mysql.connector
from config.settings import settings

class DatabaseConnection:
    """Gestionnaire de connexion à la base de données"""
    
    def __init__(self):
        self.db = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """Établit la connexion à la base de données"""
        try:
            self.db = mysql.connector.connect(
                host=settings.DB_HOST,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME
            )
            self.cursor = self.db.cursor()
            print("[SUCCÈS] Connexion à la base de données établie")
        except mysql.connector.Error as e:
            print(f"[ERREUR] Erreur de connexion à la base de données: {e}")
    
    def verify_connection(self):
        """Vérifie et rétablit la connexion si nécessaire"""
        try:
            self.db.ping(reconnect=True)
        except mysql.connector.Error:
            print("[RECONNEXION] Reconnexion à la base de données...")
            self.connect()
    
    def close(self):
        """Ferme la connexion à la base de données"""
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()
        print("[FERMETURE] Connexion à la base de données fermée")

# Instance globale
db_connection = DatabaseConnection()
