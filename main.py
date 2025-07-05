import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import mysql.connector
import os
from openai import OpenAI
from datetime import datetime
from fonctions import generer_question_et_reponse, enregistrer_challenge_en_base, actualiserBDUtilisateur, obtenirReponseUtilisateur, verifier_reponse_utilisateur, enregistrerReponse, ajouter_points_utilisateur, obtenirScoreUtilisateur
from database import db, cursor 
from Exceptions import *
import asyncio
load_dotenv() #charger le fichier .env


model_name  = "mistral-saba-24b"  # modèle utilisé sur https://models.github.ai/inference
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("IA_TOKEN")  # la clé stockée dans ton fichier .env
)




token = os.getenv('DISCORD_TOKEN')
gestionnaire = logging.FileHandler(filename='discord.log ', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content  = True 
intents.members = True  #activer l'intent members

bot = commands.Bot(command_prefix='!', intents=intents)




@bot.event 
async def on_ready():
    print(f"Bot activé : {bot.user.name}")
    try:
        # Synchroniser les slash commands
        synced = await bot.tree.sync()
        print(f"Synchronisé {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Erreur lors de la synchronisation: {e}")


@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")
    
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Ignore les messages qui commencent par le préfixe des commandes (ex: !quizz)
    ctx = await bot.get_context(message)
    if ctx.command is not None:
        await bot.process_commands(message)
        return

    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} n'utilise pas ce mot")

    await bot.process_commands(message)



@bot.tree.command(name="score", description="Affiche ton score total de points")
async def slash_score(interaction: discord.Interaction):
    # Créer un contexte factice pour réutiliser les fonctions existantes
    class FakeCtx:
        def __init__(self, interaction):
            self.author = interaction.user
    
    ctx = FakeCtx(interaction)
    await actualiserBDUtilisateur(ctx)
    score = obtenirScoreUtilisateur(ctx)
    await interaction.response.send_message(f"{interaction.user.mention} tu as {score} points ! 🥳")


@bot.tree.command(name="aide", description="Affiche l'aide pour toutes les commandes disponibles")
async def slash_aide(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🧠 Aide - Commandes Quiz",
        description="Voici toutes les commandes disponibles :",
        color=0x3498db
    )
    
    embed.add_field(
        name="📝 /quizz <difficulté> <spécialité>",
        value="Lance un quiz dans la spécialité choisie\n"
              "**Difficultés :** 1 (facile), 2 (moyen), 3 (difficile)\n"
              "**Spécialités :** Maths, NSI, Physique-Chimie, SVT, SES, HGGSP, random",
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


# Classe pour le modal de réponse au quiz
class QuizModal(discord.ui.Modal, title='Répondre au Quiz'):
    def __init__(self, question, reponse_attendu, id_challenge, ctx):
        super().__init__()
        self.question = question
        self.reponse_attendu = reponse_attendu
        self.id_challenge = id_challenge
        self.ctx = ctx
        
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
            # Créer un objet réponse factice
            class FakeMessage:
                def __init__(self, content):
                    self.content = content
                    
            reponse_message = FakeMessage(self.reponse.value)
            
            # Vérifier la réponse
            commentaire, estCorrect = await verifier_reponse_utilisateur(
                client, model_name, self.question, self.reponse_attendu, reponse_message
            )
            
            # Enregistrer la réponse
            enregistrerReponse(self.ctx, self.id_challenge, reponse_message, estCorrect)
            
            # Envoyer le résultat
            await interaction.followup.send(f"✅ **Ta réponse :** {self.reponse.value}")
            await interaction.followup.send(commentaire)
            
            if estCorrect:
                points = ajouter_points_utilisateur(self.ctx, self.id_challenge)
                await interaction.followup.send(f"🎉 Tu as gagné **{points} points** !")
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors du traitement : {e}")

@bot.tree.command(name="quizz", description="Lance un quiz dans la spécialité de ton choix")
async def slash_quizz(interaction: discord.Interaction, difficulte: int, specialite: str):
    # Créer un contexte factice pour réutiliser les fonctions existantes
    class FakeCtx:
        def __init__(self, interaction):
            self.author = interaction.user
            self.channel = interaction.channel
    
    ctx = FakeCtx(interaction)
    
    try:
        # Validation de la difficulté
        if difficulte not in [1, 2, 3]:
            raise DifficulteInvalide()
        
        await interaction.response.defer()  # Indique que le bot travaille
        
        await actualiserBDUtilisateur(ctx)
        # Génère la question + réponse
        questionRep = await generer_question_et_reponse(client, model_name, difficulte, specialite)
        print("QUESTION COMPLÈTE :", questionRep)

        # Insère dans la base de données, et récupère juste la question pour l'affichage
        questionEnvoye, reponseAttendu, idChallenge = enregistrer_challenge_en_base(questionRep, difficulte)
        
        # Créer et envoyer le modal
        modal = QuizModal(questionEnvoye, reponseAttendu, idChallenge, ctx)
        
        # Afficher la question avec un bouton pour ouvrir le modal
        embed = discord.Embed(
            title="🧠 Quiz - Cliquez pour répondre",
            description=f"**Question :**\n{questionEnvoye}",
            color=0x3498db
        )
        
        class QuizView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60.0)
                
            @discord.ui.button(label='📝 Répondre', style=discord.ButtonStyle.primary)
            async def repondre(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.send_modal(modal)
                
            async def on_timeout(self):
                for item in self.children:
                    item.disabled = True
        
        view = QuizView()
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
        print(f"Erreur dans quizz: {e}")

# Ajouter des choix pour les paramètres de slash command
from discord.app_commands import Choice

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
    specialites = ["Maths", "NSI", "Physique-Chimie", "SVT", "SES", "HGGSP", "random"]
    choices = [Choice(name=spec, value=spec) for spec in specialites if current.lower() in spec.lower()]
    return choices[:25]  # Discord limite à 25 choix


# Garde les commandes avec préfixe pour compatibilité
@bot.command()  #lorsque l'utilisateur veut afficher son score total
async def score(ctx):
    await actualiserBDUtilisateur(ctx)
    score = obtenirScoreUtilisateur(ctx)
    await ctx.send(f"{ctx.author.mention} tu as {score} points !  🥳" )




@bot.command()  #lorsque l'utilisateur veut faire un quizz
async def quizz(ctx, difficulte = None, specialite = None):
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
        
        await actualiserBDUtilisateur(ctx)
        # Génère la question + réponse
        questionRep = await generer_question_et_reponse(client, model_name, difficulte, specialite)
        print("QUESTION COMPLÈTE :", questionRep)

        # Insère dans la base de données, et récupère juste la question pour l'affichage
        questionEnvoye, reponseAttendu, idChallenge = enregistrer_challenge_en_base(questionRep, difficulte)
        reponseUtilisateur = await obtenirReponseUtilisateur(ctx, questionEnvoye, bot)
        
        if reponseUtilisateur is None:  # Timeout
            return
            
        commentaire, estCorrect = await verifier_reponse_utilisateur(client, model_name, questionEnvoye, reponseAttendu, reponseUtilisateur)
        enregistrerReponse(ctx, idChallenge, reponseUtilisateur, estCorrect)
        await ctx.send(commentaire)

        if estCorrect:
            points = ajouter_points_utilisateur(ctx, idChallenge)
            await ctx.send(f"🎉 Tu as gagné **{points} points** !")
            
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

@bot.command()  #commande d'aide pour le quizz
async def aide(ctx):
    embed = discord.Embed(
        title="🧠 Aide - Commandes Quiz",
        description="Voici toutes les commandes disponibles :",
        color=0x3498db
    )
    
    embed.add_field(
        name="📝 !quizz <difficulté> <spécialité>",
        value="Lance un quiz dans la spécialité choisie\n"
              "**Difficultés :** 1 (facile), 2 (moyen), 3 (difficile)\n"
              "**Spécialités :** Maths, NSI, Physique-Chimie, SVT, SES, HGGSP, random",
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

    
  
bot.run(token, log_handler=gestionnaire, log_level=logging.DEBUG)


