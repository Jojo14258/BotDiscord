"""
Slash commands pour Discord
"""
import discord
from discord import app_commands
from discord.app_commands import Choice
from services.quiz_service import quiz_service
from ui.views import QuizView
from utils.exceptions import SpecialiteInvalide, DifficulteInvalide, SyntaxeInvalide
from config.settings import settings

def setup_slash_commands(bot):
    """Configure les slash commands du bot"""
    
    @bot.tree.command(name="score", description="Affiche ton score total de points")
    async def slash_score(interaction: discord.Interaction):
        """Commande /score"""
        try:
            score = quiz_service.get_user_score(interaction.user.id, str(interaction.user))
            await interaction.response.send_message(f"{interaction.user.mention} tu as {score} points ! 🥳")
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur : {e}")
            print(f"Erreur dans slash_score: {e}")

    @bot.tree.command(name="aide", description="Affiche l'aide pour toutes les commandes disponibles")
    async def slash_aide(interaction: discord.Interaction):
        """Commande /aide"""
        embed = discord.Embed(
            title="🧠 Aide - Commandes Quiz",
            description="Voici toutes les commandes disponibles :",
            color=0x3498db
        )
        
        embed.add_field(
            name="📝 /quizz <difficulté> <spécialité>",
            value="Lance un quiz dans la spécialité choisie\n"
                  "**Difficultés :** 1 (facile), 2 (moyen), 3 (difficile)\n"
                  f"**Spécialités :** {', '.join(settings.SPECIALITES)}, random",
            inline=False
        )
        
        embed.add_field(
            name="🏆 /score",
            value="Affiche ton score total de points",
            inline=False
        )
        
        embed.add_field(
            name="📚 Exemples d'utilisation",
            value="`/quizz difficulte:2 specialite:Maths` - Quiz moyen en Maths\n"
                  "`/quizz difficulte:1 specialite:random` - Quiz facile aléatoire\n"
                  "`/quizz difficulte:3 specialite:NSI` - Quiz difficile en NSI",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="quizz", description="Lance un quiz dans la spécialité de ton choix")
    async def slash_quizz(interaction: discord.Interaction, difficulte: int, specialite: str):
        """Commande /quizz"""
        try:
            await interaction.response.defer()  # Indique que le bot travaille
            
            # Créer le quiz via le service
            question, expected_answer, challenge_id = await quiz_service.create_quiz(difficulte, specialite)
            
            # Créer l'embed et la vue
            embed = discord.Embed(
                title="🧠 Quiz - Cliquez pour répondre",
                description=f"**Question :**\n{question}",
                color=0x3498db
            )
            
            view = QuizView(
                question, 
                expected_answer, 
                challenge_id, 
                interaction.user.id, 
                str(interaction.user),
                timeout=settings.TIMEOUT_QUIZ
            )
            
            await interaction.followup.send(embed=embed, view=view)
                
        except (SpecialiteInvalide, DifficulteInvalide, SyntaxeInvalide) as e:
            if interaction.response.is_done():
                await interaction.followup.send(str(e))
            else:
                await interaction.response.send_message(str(e))
            
        except Exception as e:
            error_msg = (
                "❌ **Une erreur inattendue s'est produite !**\n\n"
                "Essaie à nouveau avec la syntaxe :\n"
                "`/quizz difficulte:<1-3> specialite:<spécialité>`\n\n"
                "**Exemple :** `/quizz difficulte:1 specialite:Maths`"
            )
            if interaction.response.is_done():
                await interaction.followup.send(error_msg)
            else:
                await interaction.response.send_message(error_msg)
            print(f"Erreur dans slash_quizz: {e}")

    # Autocomplétion pour les paramètres
    @slash_quizz.autocomplete('difficulte')
    async def difficulte_autocomplete(interaction: discord.Interaction, current: str):
        choices = [
            Choice(name="1 - Facile", value=1),
            Choice(name="2 - Moyen", value=2),
            Choice(name="3 - Difficile", value=3)
        ]
        return choices

    @slash_quizz.autocomplete('specialite')
    async def specialite_autocomplete(interaction: discord.Interaction, current: str):
        specialites = settings.SPECIALITES + ["random"]
        choices = [Choice(name=spec, value=spec) for spec in specialites if current.lower() in spec.lower()]
        return choices[:25]  # Discord limite à 25 choix
