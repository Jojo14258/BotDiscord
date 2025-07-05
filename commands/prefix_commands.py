"""
Commandes avec préfixe pour Discord
"""
import discord
from discord.ext import commands
from services.quiz_service import quiz_service
from utils.exceptions import SpecialiteInvalide, DifficulteInvalide, SyntaxeInvalide
from config.settings import settings
import asyncio

def setup_prefix_commands(bot):
    """Configure les commandes avec préfixe du bot"""
    
    @bot.command()
    async def score(ctx):
        """Commande !score"""
        try:
            score = quiz_service.get_user_score(ctx.author.id, str(ctx.author))
            await ctx.send(f"{ctx.author.mention} tu as {score} points ! 🥳")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
            print(f"Erreur dans score: {e}")

    @bot.command()
    async def aide(ctx):
        """Commande !aide"""
        embed = discord.Embed(
            title="🧠 Aide - Commandes Quiz",
            description="Voici toutes les commandes disponibles :",
            color=0x3498db
        )
        
        embed.add_field(
            name="📝 !quizz <difficulté> <spécialité>",
            value="Lance un quiz dans la spécialité choisie\n"
                  "**Difficultés :** 1 (facile), 2 (moyen), 3 (difficile)\n"
                  f"**Spécialités :** {', '.join(settings.SPECIALITES)}, random",
            inline=False
        )
        
        embed.add_field(
            name="🏆 !score",
            value="Affiche ton score total de points",
            inline=False
        )
        
        embed.add_field(
            name="📚 Exemples d'utilisation",
            value="`!quizz 2 Maths` - Quiz moyen en Maths\n"
                  "`!quizz 1 random` - Quiz facile aléatoire\n"
                  "`!quizz 3 NSI` - Quiz difficile en NSI",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @bot.command()
    async def quizz(ctx, difficulte=None, specialite=None):
        """Commande !quizz (version classique avec attente de message)"""
        try:
            # Vérification des paramètres
            if difficulte is None or specialite is None:
                raise SyntaxeInvalide()
            
            # Conversion et vérification de la difficulté
            try:
                difficulte = int(difficulte)
            except ValueError:
                raise DifficulteInvalide()
                
            if difficulte not in [1, 2, 3]:
                raise DifficulteInvalide()
            
            # Créer le quiz
            question, expected_answer, challenge_id = await quiz_service.create_quiz(difficulte, specialite)
            
            # Afficher la question
            await ctx.send(f"🧠 **Défi pour {ctx.author.mention} :**\n{question}")
            
            # Attendre la réponse de l'utilisateur
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            
            try:
                reponse = await bot.wait_for('message', timeout=settings.TIMEOUT_REPONSE, check=check)
                await ctx.send(f"Merci {ctx.author.mention}, tu as répondu : **{reponse.content}**")
                
                # Traiter la réponse
                comment, is_correct, points_earned = await quiz_service.submit_answer(
                    ctx.author.id,
                    str(ctx.author),
                    challenge_id,
                    question,
                    expected_answer,
                    reponse.content
                )
                
                await ctx.send(comment)
                
                if is_correct:
                    await ctx.send(f"🎉 Tu as gagné **{points_earned} points** !")
                    
            except asyncio.TimeoutError:
                await ctx.send("⏱️ Temps écoulé ! Tu n'as pas répondu à temps.")
                
        except (SpecialiteInvalide, DifficulteInvalide, SyntaxeInvalide) as e:
            await ctx.send(str(e))
            
        except Exception as e:
            await ctx.send(
                "❌ **Une erreur inattendue s'est produite !**\n\n"
                "Essaie à nouveau avec la syntaxe :\n"
                "`!quizz <difficulté> <spécialité>`\n\n"
                "**Exemple :** `!quizz 1 Maths`"
            )
            print(f"Erreur dans quizz: {e}")
