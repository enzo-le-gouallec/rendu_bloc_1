# rendu_bloc_1

## Description
Ce projet combine du web scraping,des requêtes api, requêtes SPARQL sur Wikidata, et une API REST développée avec FastAPI. Il utilise plusieurs bibliothèques pour automatiser des tâches de scraping, traiter des données. le but et de pouvoir trouver des salons de coiffure qui n'est pas chez une application concurente pour le démarchage.

## Dépendances
Les principales dépendances du projet sont :

- **FastAPI** : Framework pour créer l'API.
- **uvicorn** : Serveur ASGI pour exécuter l'application FastAPI.
- **selenium** : Pour l'automatisation de navigateur et le scraping.
- **beautifulsoup4** : Pour parser et extraire des informations depuis le HTML.
- **pandas** : Pour la manipulation et l'analyse de données.
- **requests** : Pour effectuer des requêtes HTTP.
- **python-dotenv** : Pour charger les variables d'environnement depuis un fichier `.env`.
- **pymysql** : Pour se connecter à une base de données MySQL.
- **pymongo** : Pour se connecter à une base de données MongoDB.
- **PyJWT** : Pour créer et gérer les tokens JWT.
- **passlib** : Pour hacher et vérifier les mots de passe.
- **pydantic** : Pour la validation et la gestion des données (utilisé par FastAPI).
- **SPARQLWrapper** : Pour interroger le service SPARQL de Wikidata.
- **crontab** : Pour planifier l'exécution régulière de scripts (la configuration se fait côté système).

## Installation

Il est recommandé d'utiliser un environnement virtuel. Voici comment installer toutes les dépendances avec `pip` :

```bash
# Créer un environnement virtuel (optionnel mais recommandé)
python -m venv venv

# Activer l'environnement virtuel
# Sous Windows :
venv\Scripts\activate
# Sous macOS/Linux :
source venv/bin/activate

# Installer les dépendances
# Installer les dépendances
pip install fastapi uvicorn selenium beautifulsoup4 pandas requests python-dotenv pymysql pymongo pyjwt passlib pydantic SPARQLWrapper webdriver-manager

```


## Structure de la Base de Données

La conception de la base de données a été réalisée à l'aide de [MOCODO](https://mocodo.net/). Vous trouverez ci-dessous deux diagrammes illustrant la structure de la base de données :

### Modèle Conceptuel de Données (MCD)
![MCD](structure_bdd/MCD.png)

### Modèle Physique de Données (MPD)
![MPD](structure_bdd/MPD.png)

Ces diagrammes offrent une vue détaillée de la structure et de l'organisation de la base de données du projet.