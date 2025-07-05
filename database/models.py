"""
Modèles et opérations de base de données
"""
from datetime import datetime
from database.connection import db_connection
from config.settings import settings

class User:
    """Gestion des utilisateurs"""
    
    @staticmethod
    def create_or_update(user_id: int, username: str):
        """Crée ou met à jour un utilisateur"""
        db_connection.verify_connection()
        
        # Vérifier si l'utilisateur existe
        db_connection.cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        result = db_connection.cursor.fetchone()
        
        if result is None:
            # Créer l'utilisateur
            db_connection.cursor.execute(
                "INSERT INTO users (id, username, score, last_participation, created_at) VALUES (%s, %s, %s, %s, %s)",
                (user_id, username, 0, None, datetime.now())
            )
            db_connection.db.commit()
            return True  # Nouvel utilisateur créé
        return False  # Utilisateur existant
    
    @staticmethod
    def get_score(user_id: int) -> int:
        """Récupère le score d'un utilisateur"""
        db_connection.verify_connection()
        db_connection.cursor.execute("SELECT score FROM users WHERE id = %s", (user_id,))
        result = db_connection.cursor.fetchone()
        return result[0] if result else 0
    
    @staticmethod
    def add_points(user_id: int, points: int):
        """Ajoute des points à un utilisateur"""
        db_connection.verify_connection()
        db_connection.cursor.execute(
            "UPDATE users SET score = score + %s, last_participation = %s WHERE id = %s",
            (points, datetime.now(), user_id)
        )
        db_connection.db.commit()

class Challenge:
    """Gestion des défis/questions"""
    
    @staticmethod
    def create(title: str, question: str, answer: str, subject: str, difficulty: int) -> int:
        """Crée un nouveau défi et retourne son ID"""
        db_connection.verify_connection()
        
        points_value = settings.POINTS_PAR_DIFFICULTE.get(difficulty, 5)
        
        db_connection.cursor.execute(
            "INSERT INTO challenges (title, question, answer_expected, subject, difficulty, published_at, points_value) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (title, question, answer, subject, difficulty, datetime.now().date(), points_value)
        )
        db_connection.db.commit()
        
        # Récupérer l'ID du défi créé
        db_connection.cursor.execute("SELECT id FROM challenges ORDER BY id DESC LIMIT 1")
        return db_connection.cursor.fetchone()[0]
    
    @staticmethod
    def get_points_value(challenge_id: int) -> int:
        """Récupère la valeur en points d'un défi"""
        db_connection.verify_connection()
        db_connection.cursor.execute("SELECT points_value FROM challenges WHERE id = %s", (challenge_id,))
        result = db_connection.cursor.fetchone()
        return result[0] if result else 0

class Submission:
    """Gestion des soumissions de réponses"""
    
    @staticmethod
    def create(user_id: int, challenge_id: int, response: str, is_correct: bool):
        """Enregistre une soumission de réponse"""
        db_connection.verify_connection()
        
        db_connection.cursor.execute(
            "INSERT INTO submissions (user_id, challenge_id, response, is_correct, submitted_at) VALUES (%s, %s, %s, %s, %s)",
            (user_id, challenge_id, response, is_correct, datetime.now().date())
        )
        db_connection.db.commit()
