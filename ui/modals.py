"""
Modals Discord pour les interactions utilisateur
"""
import discord
from services.quiz_service import quiz_service

class QuizModal(discord.ui.Modal, title='Répondre au Quiz'):
    """Modal pour répondre à un quiz"""
    
    def __init__(self, question: str, expected_answer: str, challenge_id: int, user_id: int, username: str):
        super().__init__()
        self.question = question
        self.expected_answer = expected_answer
        self.challenge_id = challenge_id
        self.user_id = user_id
        self.username = username
        
    # Champ de texte pour la réponse
    reponse = discord.ui.TextInput(
        label='Ta réponse :',
        placeholder='Écris ta réponse ici...',
        required=True,
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            # Soumettre la réponse via le service
            comment, is_correct, points_earned = await quiz_service.submit_answer(
                self.user_id, 
                self.username, 
                self.challenge_id, 
                self.question, 
                self.expected_answer, 
                self.reponse.value
            )
            
            # Envoyer le résultat
            await interaction.followup.send(f"✅ **Ta réponse :** {self.reponse.value}")
            await interaction.followup.send(comment)
            
            if is_correct:
                await interaction.followup.send(f"🎉 Tu as gagné **{points_earned} points** !")
                
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors du traitement : {e}")
            print(f"Erreur dans QuizModal: {e}")
