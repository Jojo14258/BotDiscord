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
    print(f"Bot activé :  {bot.user.name}")


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


