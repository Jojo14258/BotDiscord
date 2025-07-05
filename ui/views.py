"""
Vues Discord avec boutons et interactions
"""
import discord
from ui.modals import QuizModal

class QuizView(discord.ui.View):
    """Vue avec bouton pour répondre à un quiz"""
    
    def __init__(self, question: str, expected_answer: str, challenge_id: int, user_id: int, username: str, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.question = question
        self.expected_answer = expected_answer
        self.challenge_id = challenge_id
        self.user_id = user_id
        self.username = username
        
    @discord.ui.button(label='📝 Répondre', style=discord.ButtonStyle.primary)
    async def repondre(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour ouvrir le modal de réponse"""
        modal = QuizModal(
            self.question, 
            self.expected_answer, 
            self.challenge_id, 
            self.user_id, 
            self.username
        )
        await interaction.response.send_modal(modal)
        
    async def on_timeout(self):
        """Désactive les boutons après timeout"""
        for item in self.children:
            item.disabled = True
