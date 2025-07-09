"""
Commandes avec préfixe pour Discord
"""
import discord
from discord.ext import commands
from services.quiz_service import quiz_service
from database.models import User
from utils.exceptions import SpecialiteInvalide, DifficulteInvalide, SyntaxeInvalide
from config.settings import settings
from services.latex_service import LatexService
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
    async def classement(ctx):
        """Commande !classement pour afficher la liste des joueurs avec le plus de points"""
        try:
            # Récupérer le top 10 des joueurs
            top_players = User.get_ranking(10)
            
            if not top_players:
                await ctx.send("🏆 Aucun joueur n'a encore de points !")
                return
            
            embed = discord.Embed(
                title="🏆 Classement global des participants",
                description="Voici les meilleurs joueurs !",
                color=0xFFD700  # Couleur or
            )
            
            # Afficher le top 3 avec photos de profil
            podium_emojis = ["🥇", "🥈", "🥉"]
            
            for i, (user_id, username, score) in enumerate(top_players[:3]):
                user = bot.get_user(user_id)
                
                embed.add_field(
                    name=f"{podium_emojis[i]} **{i+1}. {username}**",
                    value=f"💎 **{score} points**",
                    inline=True
                )
                
                # Ajouter la photo de profil uniquement pour le 1er et s'il existe
                if i == 0 and user:
                    try:
                        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
                        embed.set_thumbnail(url=avatar_url)
                    except Exception:
                        pass  # Si erreur avec l'avatar, on ignore simplement
            
            # Ajouter le reste du classement (4-10) de manière compacte
            if len(top_players) > 3:
                autres_joueurs = ""
                for i, (user_id, username, score) in enumerate(top_players[3:], 4):
                    autres_joueurs += f"**{i}.** {username} - {score} pts\n"
                
                if autres_joueurs:
                    embed.add_field(
                        name="📊 Reste du classement",
                        value=autres_joueurs,
                        inline=False
                    )
            
            # Ajouter la position de l'utilisateur actuel s'il n'est pas dans le top 10
            user_score = User.get_score(ctx.author.id)
            user_in_top = False  # Initialiser à False par défaut
            
            # Option 1: Avec while (votre approche corrigée)
            i = 0
            while i < len(top_players) and not user_in_top:
                if ctx.author.id == top_players[i][0]:
                    user_in_top = True
                i += 1   
            if not user_in_top and user_score > 0:
                embed.add_field(
                    name="📍 Ta position",
                    value=f"{ctx.author.mention} - {user_score} points",
                    inline=False
                )
            
            embed.set_footer(text="💡 Utilise !quizz pour gagner des points !")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de l'affichage du classement : {e}")
            print(f"Erreur dans classement: {e}")

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
            print(f"Question posée à {ctx.author} : {question}")
            
            # Générer une image si la question contient du LaTeX
            if LatexService.contains_latex(question):
                success = LatexService.latex_to_image(question, 'question_latex.png')
                if success:
                    await ctx.send(file=discord.File('question_latex.png'))
        
                
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
                # Générer une image si la question contient du LaTeX
                if LatexService.contains_latex(comment):
                    success = LatexService.latex_to_image(comment, 'reponse_latex.png')
                if success:
                    await ctx.send(file=discord.File('reponse_latex.png'))
        
                
                # Générer une image si le commentaire contient du LaTeX
                if LatexService.contains_latex(comment):
                    success = LatexService.latex_to_image(comment, 'comment_latex.png')
                    if success:
                        await ctx.send(file=discord.File('comment_latex.png'))
              
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
