# 🧠 Bot Discord Quiz

Un bot Discord de quiz scolaire avec IA, slash commands et rendu LaTeX, persistant les scores en MySQL.

## 📋 Sommaire

- Fonctionnalités
- Prérequis
- Installation (Windows/macOS/Linux)
- Configuration (.env)
- Base de données (schema.sql)
- Lancer le bot
- Commandes (slash et préfixe)
- Rendu LaTeX (optionnel)
- Structure du projet
- Dépannage

## ✨ Fonctionnalités

- 🤖 Génération de questions via IA (Groq/OpenAI API) selon la difficulté et la spécialité
- 🧩 6 spécialités supportées (+ random) et 3 niveaux de difficulté
- �️ Persistance MySQL des utilisateurs, défis et réponses
- 🏆 Score cumulé, classement global, mention de votre position
- 💬 Deux modes d’utilisation: slash commands modernes et commandes préfixe `!`
- �️ Rendu d’énoncés/corrections contenant du LaTeX en image (affichage propre dans Discord)
- 🧰 Architecture modulaire (services, database, ui, commands)
- � Logs dans `logs/discord.log`

## 🧱 Prérequis

- Python 3.10+ recommandé
- MySQL/MariaDB accessible (identifiants dans `config/settings.py` et `.env`)
- Un bot créé sur le Discord Developer Portal (token)
- Une clé API Groq (utilisée via le SDK OpenAI)
- Optionnel pour LaTeX: une distribution LaTeX installée (MiKTeX/TeX Live) + matplotlib

## 🚀 Installation

1) Cloner le dépôt et se placer dans le dossier

2) (Recommandé) Créer un environnement virtuel et installer les dépendances
    - Windows PowerShell:
       - python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
    - macOS/Linux:
       - python3 -m venv .venv; source .venv/bin/activate; pip install -r requirements.txt

3) Copier l’exemple d’environnement et complétez vos secrets
    - Copier `.env.example` en `.env` puis renseigner les valeurs

4) Créer la base et les tables
    - Importer le contenu de `schema.sql` dans votre MySQL (via client/GUI)

## ⚙️ Configuration (.env)

Le bot lit les variables d’environnement via `python-dotenv`. Exemple minimal:

```
DISCORD_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DB_PASSWORD=votre_mot_de_passe_mysql
IA_TOKEN=cle_api_groq
```

Autres paramètres par défaut (voir `config/settings.py`):
- Préfixe commandes: `!`
- Hôte MySQL: `badge.o2switch.net` (modifiez si besoin)
- Utilisateur DB: `jipu4543_jordan`
- Base DB: `jipu4543_ChallengeDiscord`
- Modèle IA: `gemma2-9b-it`, Base URL: `https://api.groq.com/openai/v1`
- Spécialités: Maths, NSI, Physique-Chimie, SVT, SES, HGGSP
- Points: {1:5, 2:10, 3:15}
- Timeout quiz: 60s, Timeout réponse: 30s

## 🗄️ Base de données

Les tables requises se trouvent dans `schema.sql` (users, challenges, submissions). Importez ce fichier dans votre base.

## ▶️ Lancer le bot

- Windows PowerShell:
   - .\.venv\Scripts\Activate.ps1; python .\main.py
- macOS/Linux:
   - source .venv/bin/activate; python3 main.py

Le bot synchronise les slash commands au démarrage. Les logs sont écrits dans `logs/discord.log`.

## 📝 Commandes

Slash commands:
- /quizz difficulte:<1|2|3> specialite:<Maths|NSI|Physique-Chimie|SVT|SES|HGGSP|random>
- /score — Affiche votre score
- /classement — Top 10 et votre position
- /aide — Récapitulatif

Commandes préfixe:
- !quizz <difficulté> <spécialité>
- !score
- !classement
- !aide

Barème des points:
- 1 = 5 points, 2 = 10 points, 3 = 15 points (configurable dans `config/settings.py`)

## 🧮 Rendu LaTeX (optionnel)

Si une question ou une correction contient du LaTeX, le bot tente de générer une image pour un affichage propre.

Dépendances supplémentaires déjà listées dans `requirements.txt`:
- matplotlib (nécessite une distribution LaTeX si `text.usetex=True`)
- ipython

Sous Windows: installez MiKTeX (ou TeX Live) pour activer `usetex` dans matplotlib.

## � Structure

```
BotDiscord/
├── main.py
├── requirements.txt
├── .env (à créer)
├── .env.example
├── README.md
├── schema.sql
├── config/
│   └── settings.py
├── database/
│   ├── connection.py
│   └── models.py
├── commands/
│   ├── slash_commands.py
│   └── prefix_commands.py
├── services/
│   ├── ai_service.py
│   ├── quiz_service.py
│   └── latex_service.py
├── ui/
│   ├── views.py
│   └── modals.py
├── utils/
│   └── exceptions.py
└── logs/
      └── discord.log
```

## 🛠️ Dépannage

- Slash commands absentes: vérifier les scopes (`applications.commands`) et réinviter le bot; attendre la propagation (jusqu’à 1h en DM).
- Connexion DB: vérifiez hôte/utilisateur/mot de passe; importez `schema.sql`; droits utilisateur.
- IA: assurez-vous que `IA_TOKEN` est valide et que l’API Groq est accessible.
- LaTeX: si l’image n’apparaît pas, installez une distribution LaTeX; sinon, le bot enverra le texte brut.

---

Made with ❤️ pour apprendre et réviser plus facilement.
