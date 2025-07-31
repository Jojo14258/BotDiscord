"""
Bot Discord Quiz - Point d'entrée principal
Version refactorisée avec architecture propre
"""
import discord
from discord.ext import commands
import logging

# Imports de notre architecture
from config.settings import settings
from commands.slash_commands import setup_slash_commands
from commands.prefix_commands import setup_prefix_commands

def main():
    """Fonction principale"""
    # Configuration des intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    
    # Création du bot
    bot = commands.Bot(command_prefix=settings.COMMAND_PREFIX, intents=intents)
    
    # Configuration du logging
    gestionnaire = logging.FileHandler(filename=settings.LOG_FILE, encoding=settings.LOG_ENCODING, mode='w')
    
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
    
    # Configurer les commandes
    setup_slash_commands(bot)
    setup_prefix_commands(bot)
    
    # Lancer le bot
    bot.run(settings.DISCORD_TOKEN, log_handler=gestionnaire, log_level=logging.DEBUG)

if __name__ == "__main__":
    main()
