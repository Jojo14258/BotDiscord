import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import mysql.connector
import os
from datetime import datetime


load_dotenv()  # indispensable

print(os.getenv('DB_PASSWORD'))


