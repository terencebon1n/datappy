# 🚌 Datappy : Application Mobile d'Affichage Temps Réel

**Datappy** est un projet visant à fournir une **application mobile** permettant aux utilisateurs de visualiser le trafic en temps réel des transports en commun. Nous exploitons les flux de données **GTFS-RT (General Transit Feed Specification - Realtime)**.
## 🎯 Objectif du Projet

L'objectif principal est de développer une application mobile offrant :

* **Affichage de Panneaux Numériques :** Visualisation des prochains départs pour un arrêt donné, à la manière des panneaux d'affichage physiques.

## ⚙️ Stack Technique

Bien que le produit final soit une application mobile, le cœur de la gestion et du traitement des données GTFS-RT reste un **backend performant** pour alimenter l'application.

| Composant | Technologie | Rôle Principal |
| :--- | :--- | :--- |
| **Architecture** | **DDD & Principe SOLID** | Architecture hautement scalable, robuste et maintenable. |
| **Backend API** | **FastAPI** (Python) | Serveur ultra-rapide traduisant les demandes et servant les données en temps réel à l'application mobile. |
| **Database** | **Postgres** (SQLAlchemy) | Base de données de stockage des données statiques GTFS. |
| **Data Broker** | **Kafka** (aiokafka) | Distribution des données GTFS-RT aux différents services. |
| **Data Consumer** | **Spark** (PySpark) | Traitement des données en temps réel et production des panneaux numériques. |
| **Data Sink** | **Redis** | BDD No-SQL Ultra performant, idéal pour les websockets. |
| **Gestionnaire de Paquets** | **`uv` (par astral-sh)** | Gestionnaire de dépendances et installateur de paquets ultra-rapide. |
| **Linter & Formateur** | **Ruff** | Outil unifié et performant pour l'analyse statique et le formatage du code Python. |
| **Source de Données** | **GTFS-RT** | Standard pour les données de transport en temps réel. https://transport.data.gouv.fr|
| **Frontend** | (À déterminer : Flutter, React Native, ou Natif) | L'application mobile elle-même qui consommera l'API Datappy. |

## 🚀 Démarrage du Backend Datappy

Cette section explique comment lancer l'API backend qui sera la source des données temps réel pour l'application mobile.

### 1. Prérequis

Assurez-vous que Python 3.13+ et uv sont installés sur votre système.
Assurez-vous que Docker et Docker Compose sont installés sur votre système.

### 2. Cloner le Dépôt

```bash
git clone [https://github.com/votre-utilisateur/datappy.git](https://github.com/terencebon1n/datappy.git)
cd datappy
```

### 3. Lancer les conteneurs Docker

```bash
docker compose up -d
```

### 4. Remplir la base de données Postgres (avec les données de Montpellier ici par exemple)

```bash
uv run datappy populate montpellier
```

### 5. Lancer tout les process de traitement temps réel et le backend

```bash
uv run datappy api
uv run datappy producer montpellier
uv run datappy consumer
```

### 6. Lancer le front

À venir
