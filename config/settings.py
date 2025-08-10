"""
Configuration centralisée du bot Discord Quiz
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuration du bot"""
    
    # Discord
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    COMMAND_PREFIX = '!'
    
    # Base de données
    # Renseignez ces variables dans votre .env pour pointer vers VOTRE base
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', '')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', '')
    
    # IA
    AI_TOKEN = os.getenv('IA_TOKEN')
    AI_MODEL = "gemma2-9b-it"
    AI_BASE_URL = "https://api.groq.com/openai/v1"
    
    # Quiz
    SPECIALITES = ["Maths", "NSI", "Physique-Chimie", "SVT", "SES", "HGGSP"]
    POINTS_PAR_DIFFICULTE = {1: 5, 2: 10, 3: 15}
    TIMEOUT_QUIZ = 60.0
    TIMEOUT_REPONSE = 30.0
    
    # Logging
    LOG_FILE = "logs/discord.log"
    LOG_ENCODING = "utf-8"

# Instance globale
settings = Settings()
