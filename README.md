# 🧠 Bot Discord Quiz

Un bot Discord interactif pour créer des quiz éducatifs dans différentes spécialités de lycée, utilisant l'intelligence artificielle pour générer des questions personnalisées.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Technologies utilisées](#-technologies-utilisées)
- [Architecture du projet](#-architecture-du-projet)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Commandes disponibles](#-commandes-disponibles)
- [Structure du projet](#-structure-du-projet)
- [Contribution](#-contribution)
- [Licence](#-licence)

## ✨ Fonctionnalités

- 🎯 **Quiz interactifs** dans 6 spécialités de lycée
- 🤖 **Génération automatique** de questions via IA (Groq/Mistral)
- 📊 **Système de points** avec 3 niveaux de difficulté
- 💬 **Support complet** des slash commands (`/`) et commandes préfixe (`!`)
- 🔄 **Interface moderne** avec boutons et modals Discord
- 📱 **Compatible DM et serveurs** Discord
- 🗄️ **Persistance des données** avec MySQL
- 📈 **Suivi des scores** et historique des réponses

## 🛠 Technologies utilisées

- **Python 3.8+** - Langage principal
- **Discord.py** - Bibliothèque pour l'API Discord
- **OpenAI/Groq API** - Génération de questions via IA
- **MySQL** - Base de données pour la persistance
- **python-dotenv** - Gestion des variables d'environnement

## 🏗 Architecture du projet

Le projet suit une **architecture modulaire** pour une maintenance facile :

```
📁 Services métier    → Logique applicative
📁 Commandes         → Interface Discord  
📁 UI               → Composants visuels
📁 Database         → Accès aux données
📁 Config           → Configuration centralisée
```

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- MySQL Server
- Un bot Discord configuré
- Une clé API Groq

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/Jojo14258votre-username/BotDiscord
cd BotDiscord
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer la base de données**
```sql
-- Créer la base de données et les tables nécessaires
CREATE DATABASE discord_quiz;
-- (Voir le fichier .erd pour la structure complète)
```

4. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer le fichier .env avec vos valeurs
```

## ⚙️ Configuration

Créez un fichier `.env` à la racine du projet :

```env
# Discord
DISCORD_TOKEN=votre_token_discord_ici

# Base de données
DB_PASSWORD=votre_mot_de_passe_mysql

# Intelligence Artificielle
IA_TOKEN=votre_clé_groq_ici
```

### Configuration Discord

1. Créer une application sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Créer un bot et récupérer le token
3. Configurer les **scopes OAuth2** :
   - `bot`
   - `applications.commands`
4. Configurer les **permissions** :
   - Send Messages
   - Use Slash Commands
   - Add Reactions
   - Read Message History
5. Activer les **intents** :
   - Message Content Intent
   - Server Members Intent

### Configuration IA

1. Créer un compte sur [Groq](https://groq.com/)
2. Générer une clé API
3. L'ajouter dans votre fichier `.env`

## 🎮 Utilisation

### Lancement du bot

```bash
# Version refactorisée
python main_new.py

```

### Première utilisation

1. Inviter le bot sur votre serveur avec l'URL OAuth2
2. Tester avec `/aide` ou `!aide`
3. Lancer votre premier quiz avec `/quizz difficulte:1 specialite:Maths`

## 📝 Commandes disponibles

### Slash Commands (modernes)

| Commande | Description | Exemple |
|----------|-------------|---------|
| `/quizz` | Lance un quiz interactif | `/quizz difficulte:2 specialite:NSI` |
| `/score` | Affiche votre score total | `/score` |
| `/aide` | Aide et documentation | `/aide` |

### Commandes préfixe (compatibilité)

| Commande | Description | Exemple |
|----------|-------------|---------|
| `!quizz` | Lance un quiz (mode texte) | `!quizz 2 NSI` |
| `!score` | Affiche votre score total | `!score` |
| `!aide` | Aide et documentation | `!aide` |

### Paramètres

**Difficultés :**
- `1` - Facile (5 points)
- `2` - Moyen (10 points)  
- `3` - Difficile (15 points)

**Spécialités disponibles :**
- `Maths` - Mathématiques
- `NSI` - Numérique et Sciences Informatiques
- `Physique-Chimie` - Physique et Chimie
- `SVT` - Sciences de la Vie et de la Terre
- `SES` - Sciences Économiques et Sociales
- `HGGSP` - Histoire-Géographie, Géopolitique et Sciences Politiques
- `random` - Spécialité aléatoire

## 📁 Structure du projet

```
BotDiscord/
├── main_new.py              # Point d'entrée refactorisé
├── main.py                  # Version originale (legacy)
├── requirements.txt         # Dépendances Python
├── .env                     # Variables d'environnement
├── README.md               # Documentation
│
├── config/                 # Configuration
│   ├── __init__.py
│   └── settings.py         # Paramètres centralisés
│
├── database/               # Accès aux données  
│   ├── __init__.py
│   ├── connection.py       # Connexion MySQL
│   └── models.py          # Modèles de données
│
├── commands/               # Commandes Discord
│   ├── __init__.py
│   ├── slash_commands.py   # Commandes /
│   └── prefix_commands.py  # Commandes !
│
├── services/               # Logique métier
│   ├── __init__.py
│   ├── quiz_service.py     # Gestion des quiz
│   └── ai_service.py       # Service IA
│
├── ui/                     # Interface utilisateur
│   ├── __init__.py
│   ├── modals.py          # Fenêtres popup
│   └── views.py           # Boutons et vues
│
├── utils/                  # Utilitaires
│   ├── __init__.py
│   └── exceptions.py       # Exceptions personnalisées
│
└── logs/                   # Journaux
    └── discord.log
```

## 🎯 Exemple d'utilisation

### Quiz avec slash command (moderne)

1. Tapez `/quizz` dans Discord
2. Sélectionnez la difficulté et la spécialité
3. Cliquez sur "📝 Répondre" 
4. Saisissez votre réponse dans la popup
5. Recevez la correction et vos points !

### Quiz avec commande préfixe (classique)

1. Tapez `!quizz 2 Maths`
2. Lisez la question affichée
3. Répondez dans le chat
4. Recevez la correction et vos points !

## 🔧 Développement

### Ajouter une nouvelle spécialité

1. Modifier `config/settings.py` :
```python
SPECIALITES = ["Maths", "NSI", "Physique-Chimie", "SVT", "SES", "HGGSP", "Nouvelle-Spé"]
```

2. L'IA s'adaptera automatiquement aux nouvelles spécialités !

### Modifier le système de points

1. Ajuster dans `config/settings.py` :
```python
POINTS_PAR_DIFFICULTE = {1: 5, 2: 10, 3: 15, 4: 20}  # Exemple avec difficulté 4
```

## 🐛 Dépannage

### Le bot ne répond pas

1. Vérifier que le token Discord est valide
2. S'assurer que les intents sont activés
3. Vérifier la connexion à la base de données

### Les slash commands n'apparaissent pas

1. Vérifier les scopes OAuth2 (`applications.commands`)
2. Ré-inviter le bot avec les bonnes permissions
3. Attendre la synchronisation (jusqu'à 1h pour les DMs)

### Erreurs de base de données

1. Vérifier la connexion MySQL
2. S'assurer que les tables existent
3. Contrôler les permissions de l'utilisateur DB

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

- **Jordan** - Développeur principal

## 🙏 Remerciements

- Discord.py pour l'excellente bibliothèque
- Groq pour l'API IA performante
- La communauté Discord pour les retours

---

**⭐ N'hésitez pas à m'envoyer votre retour si ce projet vous a aidé !**
