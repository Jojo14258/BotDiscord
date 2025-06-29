# fonctions.py
from datetime import datetime
import database
import os
import mysql.connector
import asyncio
from dotenv import load_dotenv
load_dotenv()


# Fonction pour générer une question de spécialité
async def generer_question_et_reponse(client, model_name):
    """Génère une question et réponse en utilisant le client OpenAI et le modèle spécifié."""
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Tu es un assistant qui génère des questions de quiz pour le lycée."},
            {"role": "user", "content": "Génère une question de quiz courte et réalisable sans trop réfléchir pour un élève de lycée en terminale dans une spécialité choisie au hasard parmi : Maths, NSI, Physique-Chimie, SVT ou SES, HGGSP. ATTENTION : le choix du type de question doit bien être aléatoire ! Donne uniquement la question suivie de sa réponse attendue, dans ce format :\n\nSujet: [Nom de la spécialité]\nQuestion: [Le texte de la question]\nRéponse: [La bonne réponse]"}
        ],
       #  temperature=0.5,
      #  max_tokens=500,
        model=model_name
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

def enregistrer_challenge_en_base(texte):
    verifier_connexion_mysql()
    # Coupe les lignes
    lignes = texte.split("\n")

    sujet = ""
    question = ""
    reponse = ""

    # Cherche les valeurs
    for ligne in lignes:
        if ligne.startswith("Sujet:"):
            sujet = ligne.replace("Sujet:", "").strip()
        elif ligne.startswith("Question:"):
            question = ligne.replace("Question:", "").strip()
        elif ligne.startswith("Réponse:"):
            reponse = ligne.replace("Réponse:", "").strip()

    titre = f"Quiz - {sujet}"

    database.cursor.execute(
        "INSERT INTO challenges (title, question, answer_expected, subject, difficulty, published_at) VALUES (%s, %s, %s, %s, %s, %s)",
        (titre, question, reponse, sujet, 1, datetime.now().date())
    )
    database.db.commit()

    return question, reponse  # Pour l'afficher ensuite dans Discord

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
    print(reponse_utilisateur)
    invite = f"""
Tu es un assistant chargé d'évaluer si la réponse d'un utilisateur est correcte à une question de quiz. Sois tolérant sur la réponse.

Voici la question posée :
{question}

Voici la bonne réponse attendue :
{bonne_reponse}

Voici la réponse donnée par l'utilisateur :
{reponse_utilisateur.content}

Ta tâche :
1. Détermine si la réponse est correcte ou incorrecte.
2. Commence toujours par "✅ Correct :" ou "❌ Incorrect :".
3. En cas de mauvaise réponse, **donne la bonne réponse correcte avec une explication simple**.
4. Termine toujours par [OK=true] si la réponse est correcte, sinon [OK=false].
5. Adresse-toi directement à l’utilisateur avec un ton clair et bienveillant.

Exemple attendu :
❌ Incorrect : La réponse "..." est incorrecte. La bonne réponse est : ...
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

