import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import mysql.connector
import os
from openai import OpenAI
from datetime import datetime
from fonctions import generer_question_et_reponse, enregistrer_challenge_en_base, actualiserBDUtilisateur, obtenirReponseUtilisateur, verifier_reponse_utilisateur
from database import db, cursor  # ✅ pour utiliser si besoin
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
    if(message.author == bot.user):
        return
    if("shit" in message.content.lower()):
        await message.delete()
        await message.channel.send(f"{message.author.mention} n'utilise pas ce mot")

    await bot.process_commands(message) #pour que les autres messages soient lus en parallèle




@bot.command()  #lorsque l'utilisateur veut faire un quizz
async def quizz(ctx):
    await actualiserBDUtilisateur(ctx)
    # Génère la question + réponse
    questionRep = await generer_question_et_reponse(client, model_name)

    # Insère dans la base de données, et récupère juste la question pour l'affichage
    questionEnvoye, reponseAttendu = enregistrer_challenge_en_base(questionRep)
    reponseUtilisateur = await obtenirReponseUtilisateur(ctx, questionEnvoye, bot)
    commentaire, est_correct = await verifier_reponse_utilisateur(client, model_name, questionEnvoye, reponseAttendu, reponseUtilisateur)
    await ctx.send(commentaire)

  
bot.run(token, log_handler=gestionnaire, log_level=logging.DEBUG)


