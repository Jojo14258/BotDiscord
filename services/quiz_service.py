"""
Service de gestion des quiz
"""
from database.models import User, Challenge, Submission
from services.ai_service import ai_service
from utils.exceptions import DifficulteInvalide

class QuizService:
    """Service pour la gestion des quiz"""
    
    @staticmethod
    def parse_ai_response(ai_response: str) -> tuple[str, str, str]:
        """Parse la réponse de l'IA pour extraire sujet, question et réponse"""
        lines = ai_response.split("\n")
        
        subject = ""
        question = ""
        answer = ""
        capture_question = False
        question_lines = []
        
        for line in lines:
            if line.startswith("Sujet:"):
                subject = line.replace("Sujet:", "").strip()
            elif line.startswith("Question:"):
                question_lines.append(line.replace("Question:", "").strip())
                capture_question = True
            elif line.startswith("Réponse:"):
                answer = line.replace("Réponse:", "").strip()
                capture_question = False
            elif capture_question:
                question_lines.append(line)
        
        question = "\n".join(question_lines).strip()
        
        return subject, question, answer
    
    @staticmethod
    async def create_quiz(difficulty: int, speciality: str) -> tuple[str, str, int]:
        """Crée un nouveau quiz et retourne question, réponse attendue, et ID du défi"""
        
        # Validation de la difficulté
        if difficulty not in [1, 2, 3]:
            raise DifficulteInvalide()
        
        # Générer la question via l'IA
        ai_response = await ai_service.generate_question(difficulty, speciality)
        print(f"QUESTION COMPLÈTE : {ai_response}")
        
        # Parser la réponse
        subject, question, answer = QuizService.parse_ai_response(ai_response)
        
        # Créer le défi en base
        title = f"Quiz - {subject}"
        challenge_id = Challenge.create(title, question, answer, subject, difficulty)
        
        return question, answer, challenge_id
    
    @staticmethod
    async def submit_answer(user_id: int, username: str, challenge_id: int, question: str, expected_answer: str, user_answer: str) -> tuple[str, bool, int]:
        """Soumet une réponse et retourne le commentaire, si c'est correct, et les points gagnés"""
        
        # S'assurer que l'utilisateur existe
        is_new_user = User.create_or_update(user_id, username)
        
        # Vérifier la réponse via l'IA
        comment, is_correct = await ai_service.verify_answer(question, expected_answer, user_answer)
        
        # Enregistrer la soumission
        Submission.create(user_id, challenge_id, user_answer, is_correct)
        
        # Ajouter des points si correct
        points_earned = 0
        if is_correct:
            points_earned = Challenge.get_points_value(challenge_id)
            User.add_points(user_id, points_earned)
        
        return comment, is_correct, points_earned
    
    @staticmethod
    def get_user_score(user_id: int, username: str) -> int:
        """Récupère le score d'un utilisateur"""
        User.create_or_update(user_id, username)
        return User.get_score(user_id)

# Instance globale
quiz_service = QuizService()
