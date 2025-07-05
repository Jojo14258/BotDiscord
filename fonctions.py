# fonctions.py
from datetime import datetime
import database
import os
import mysql.connector
import asyncio
import random
from dotenv import load_dotenv
from Exceptions import *
load_dotenv()


# Fonction pour générer une question de spécialité
import random

async def generer_question_et_reponse(client, model_name, difficulte, specialite):
    """Génère une question et réponse selon une difficulté (1 à 3) pour une spécialité choisie aléatoirement."""

    specialites = ["Maths", "NSI", "Physique-Chimie", "SVT", "SES", "HGGSP"]
    if(specialite == "random"):
        specialite_choisie = random.choice(specialites)
    elif specialite in specialites:
        specialite_choisie = specialite
    else:
        raise SpecialiteInvalide

    # Définir le niveau selon la difficulté
    if difficulte == 1:
        niveau = "facile et direct"
    elif difficulte == 2:
        niveau = "moyen, un peu plus piégeux"
    else:
        niveau = "complexe et demandant plus de réflexion"

    # Créer le prompt
    prompt = f"""
Tu es un assistant qui génère des questions de quiz pour aider les lycéens à réviser leur spé.

Génère une question de quiz **{niveau}**, mais résoluble en moins de 30 secondes, pour un élève de terminale spé, dans la spécialité suivante : {specialite_choisie}.
Attention, la question doit bien faire partie du programme de lycée.
Donne uniquement la question suivie de sa réponse attendue, dans ce format :

Sujet: {specialite_choisie}
Question: [Texte de la question]
Réponse: [La bonne réponse]
"""

    # Appel API
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "Tu es un assistant qui génère des questions de quiz pour des lycéens."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()

def verifier_connexion_mysql():
    try:
        database.db.ping(reconnect=True)
    except mysql.connector.Error:
        database.db = mysql.connector.connect(
            host="badge.o2switch.net",
            user="jipu4543_jordan",
            password=os.getenv('DB_PASSWORD'),
            database="jipu4543_ChallengeDiscord"
        )
        database.cursor = database.db.cursor() 

def enregistrer_challenge_en_base(texte, difficulte):
    verifier_connexion_mysql()
    # Coupe les lignes
    lignes = texte.split("\n")

    sujet = ""
    question = ""
    reponse = ""
    capture_question = False
    question_lignes = []
    valeurPoints = difficulte*5 #difficulté 1  : 5 pts, difficulte 2 : 10 pts et difficulté 3 : 15 pts
    # Cherche les valeurs
    for ligne in lignes:
        if ligne.startswith("Sujet:"):
            sujet = ligne.replace("Sujet:", "").strip()
        elif ligne.startswith("Question:"):
            question_lignes.append(ligne.replace("Question:", "").strip())
            capture_question = True
        elif ligne.startswith("Réponse:"):
            reponse = ligne.replace("Réponse:", "").strip()
            capture_question = False
        elif capture_question:
            question_lignes.append(ligne)
            
    question = "\n".join(question_lignes).strip()
    titre = f"Quiz - {sujet}"

    database.cursor.execute(
        "INSERT INTO challenges (title, question, answer_expected, subject, difficulty, published_at, points_value) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (titre, question, reponse, sujet, difficulte, datetime.now().date(), valeurPoints)
    )
    database.db.commit()

    database.cursor.execute("SELECT id FROM challenges ORDER BY id DESC LIMIT 1;")
    idChallenge = database.cursor.fetchone()[0]

    return question, reponse, idChallenge  # Pour l'afficher ensuite dans Discord et le stockage dans les autres bases de données

def enregistrerReponse(ctx, idChallenge, reponseUtilisateur, estCorrect):
    idUtilisateur = ctx.author.id
    dateEnvoi = datetime.now().date()

    database.cursor.execute(
        "INSERT INTO submissions (user_id, challenge_id, response, is_correct, submitted_at) VALUES (%s, %s, %s, %s, %s)",
        (idUtilisateur, idChallenge, reponseUtilisateur.content, estCorrect, dateEnvoi)
    )
    database.db.commit()

def obtenirScoreUtilisateur(ctx):
    database.cursor.execute("SELECT score FROM users WHERE id = %s;", (ctx.author.id,))
    score = database.cursor.fetchone()[0]
    return score

async def obtenirReponseUtilisateur(ctx, question, bot):
      # Affiche la question dans le canal Discord
    await ctx.send(f"🧠 **Défi pour {ctx.author.mention} :**\n{question}")

    def check(m):  #m est le message reçu
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        reponse = await bot.wait_for('message', timeout=30.0, check=check)
        await ctx.send(f"Merci {ctx.author.mention}, tu as répondu : **{reponse.content}**")
        return reponse
    except asyncio.TimeoutError:
        await ctx.send("⏱️ Temps écoulé ! Tu n'as pas répondu à temps.")

    return None


async def verifier_reponse_utilisateur(client, nom_modele, question, bonne_reponse, reponse_utilisateur):
    invite = f"""
Tu es un assistant bienveillant et sympathique chargé d'évaluer si la réponse d'un utilisateur à un quiz est correcte.

Voici la question posée :
{question}

Voici la bonne réponse attendue :
{bonne_reponse}

Voici ce que l'utilisateur a répondu :
{reponse_utilisateur.content}

Ta mission :
1. Indique si la réponse est correcte ou non.
2. Commence toujours par "✅ Bien joué !" si c'est correct, ou "❌ Oups..." si c'est incorrect.
3. Si la réponse est fausse, donne la bonne réponse, avec une explication claire, simple et sans jugement.
4. Termine par [OK=true] si la réponse est correcte, sinon [OK=false].
5. Utilise un ton amical, motivant et encourageant – comme un prof sympa qui veut aider.

Exemples :
✅ Bien joué ! Ta réponse est correcte. (...)
[OK=true]

❌ Oups... Ce n’est pas tout à fait ça. La bonne réponse est : (...). Mais ne t’inquiète pas, tu vas progresser ! 💪
[OK=false]
"""

    reponse = client.chat.completions.create(
        model=nom_modele,
        messages=[{"role": "user", "content": invite}],
        temperature=0.2,
    )

    texte = reponse.choices[0].message.content.strip()

    # Détermine si la réponse est correcte en cherchant le tag [OK=true]
    est_correcte = "[OK=true]" in texte

    # Nettoie le commentaire en enlevant les balises de validation
    commentaire = texte.replace("[OK=true]", "").replace("[OK=false]", "").strip()

    return commentaire, est_correcte

def ajouter_points_utilisateur(ctx, idChallenge):
    """Ajoute des points à l'utilisateur en fonction de la difficulté."""
    database.cursor.execute("SELECT points_value FROM challenges WHERE id = %s", (idChallenge,))
    pts = database.cursor.fetchone()[0]
    id_utilisateur = ctx.author.id
    maintenant = datetime.now()

    database.cursor.execute(
        "UPDATE users SET score = score + %s, last_participation = %s WHERE id = %s",
        (pts, maintenant, id_utilisateur)
    )
    database.db.commit()

    return pts

async def actualiserBDUtilisateur(ctx):
    verifier_connexion_mysql()
    database.cursor.execute("SELECT * FROM users WHERE id = %s", (ctx.author.id,))
    resultat = database.cursor.fetchone()

    user_id = ctx.author.id
    username = str(ctx.author)
    score = 0  # score initial
    last_participation = None  # ou datetime.now() selon le cas
    created_at = datetime.now()  # date d’ajout
    if(resultat is None):
          # Ajouter l'utilisateur
        database.cursor.execute("INSERT INTO users (id, username, score, last_participation, created_at)VALUES (%s, %s, %s, %s, %s)", (user_id, username, score, last_participation, created_at))
          
        database.db.commit()
        await ctx.send(f"{ctx.author.mention}, tu as été ajouté à la base de données ! ✅")

