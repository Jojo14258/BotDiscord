import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

db = mysql.connector.connect(
    host="badge.o2switch.net",
    user="jipu4543_jordan",
    password=os.getenv('DB_PASSWORD'),
    database="jipu4543_ChallengeDiscord"
)

cursor = db.cursor()