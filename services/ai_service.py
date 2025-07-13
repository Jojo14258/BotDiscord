"""
Service IA pour la génération et vérification des questions
"""
import random
from openai import OpenAI
from config.settings import settings
from utils.exceptions import SpecialiteInvalide

class AIService:
    """Service pour les interactions avec l'IA"""
    
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.AI_BASE_URL,
            api_key=settings.AI_TOKEN
        )
        self.model_name = settings.AI_MODEL
    
    async def generate_question(self, difficulty: int, speciality: str) -> str:
        """Génère une question selon la difficulté et spécialité"""
        
        # Choisir la spécialité
        if speciality == "random":
            speciality_chosen = random.choice(settings.SPECIALITES)
        elif speciality in settings.SPECIALITES:
            speciality_chosen = speciality
        else:
            raise SpecialiteInvalide()
        
        # Définir le niveau selon la difficulté
        if difficulty == 1:
            level = "facile et direct"
        elif difficulty == 2:
            level = "moyen, un peu plus piégeux"
        else:
            level = "complexe et demandant plus de réflexion"
        
        # Créer le prompt
        prompt = f"""
Tu es un assistant qui génère des questions de quiz pour aider les lycéens à réviser leur spé.

Génère une question de quiz **{level}**, mais résoluble en moins de 30 secondes, pour un élève de terminale spé, dans la spécialité suivante : {speciality_chosen}.
Attention, la question doit bien faire partie du programme de lycée. 
Donne uniquement la question suivie de sa réponse attendue, dans ce format :

Sujet: {speciality_chosen}
Question: [Texte de la question]
Réponse: [La bonne réponse]
"""
        
        # Appel API
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "Tu es un assistant qui génère des questions de quiz pour des lycéens."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    
    async def verify_answer(self, question: str, expected_answer: str, user_answer: str) -> tuple[str, bool]:
        """Vérifie si la réponse de l'utilisateur est correcte"""
        
        prompt = f"""
Tu es un assistant bienveillant et sympathique chargé d'évaluer si la réponse d'un utilisateur à un quiz est correcte.

Voici la question posée :
{question}

Voici la bonne réponse attendue :
{expected_answer}

Voici ce que l'utilisateur a répondu :
{user_answer}

Ta mission :
1. Indique si la réponse est correcte ou non.
2. Commence toujours par "Bien joué !" si c'est correct, ou "Oups..." si c'est incorrect.
3. Si la réponse est fausse, donne la bonne réponse, avec une explication claire, simple et sans jugement.
4. Termine par [OK=true] si la réponse est correcte, sinon [OK=false].
5. Utilise un ton amical, motivant et encourageant – comme un prof sympa qui veut aider.
6. IMPORTANT: N'utilise pas d'émojis ou de caractères spéciaux Unicode (❌, ✅, etc.) car ils posent des problèmes d'affichage.

Exemples :
Bien joué ! Ta réponse est correcte. (...)
[OK=true]

Oups... Ce n'est pas tout à fait ça. La bonne réponse est : (...). Mais ne t'inquiète pas, tu vas progresser !
[OK=false]
"""
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        
        text = response.choices[0].message.content.strip()
        
        # Détermine si la réponse est correcte
        is_correct = "[OK=true]" in text
        
        # Nettoie le commentaire
        comment = text.replace("[OK=true]", "").replace("[OK=false]", "").strip()
        
        return comment, is_correct

# Instance globale
ai_service = AIService()
