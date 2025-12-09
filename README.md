# 🚌 Datappy : Application Mobile d'Affichage Temps Réel

**Datappy** est un projet visant à fournir une **application mobile** permettant aux utilisateurs de visualiser le trafic en temps réel des transports en commun. Nous exploitons les flux de données **GTFS-RT (General Transit Feed Specification - Realtime)** ouverts, en commençant par le réseau de la ville de **Montpellier**.

## 🎯 Objectif du Projet

L'objectif principal est de développer une application mobile offrant :

* **Affichage de Panneaux Numériques :** Visualisation des prochains départs pour un arrêt donné, à la manière des panneaux d'affichage physiques.
* **Carte Temps Réel :** Affichage dynamique des positions actuelles des bus et tramways sur une carte.
* **Aperçu du Trafic :** Informations instantanées sur l'état général du réseau et les éventuelles perturbations.

## ⚙️ Stack Technique

Bien que le produit final soit une application mobile, le cœur de la gestion et du traitement des données GTFS-RT reste un **backend performant** pour alimenter l'application.

| Composant | Technologie | Rôle Principal |
| :--- | :--- | :--- |
| **Backend API** | **FastAPI** (Python) | Serveur ultra-rapide traitant les flux GTFS-RT et servant les données en temps réel à l'application mobile. |
| **Gestionnaire de Paquets** | **`uv` (par astral-sh)** | Gestionnaire de dépendances et installateur de paquets ultra-rapide. |
| **Linter & Formateur** | **Ruff** | Outil unifié et performant pour l'analyse statique et le formatage du code Python. |
| **Source de Données** | **GTFS-RT** | Standard pour les données de transport en temps réel. |
| **Frontend** | (À déterminer : Flutter, React Native, ou Natif) | L'application mobile elle-même qui consommera l'API Datappy. |

## 🚀 Démarrage du Backend Datappy

Cette section explique comment lancer l'API backend qui sera la source des données temps réel pour l'application mobile.

### 1. Prérequis

Assurez-vous que Python 3.13+ est installé sur votre système.

### 2. Cloner le Dépôt

```bash
git clone [https://github.com/votre-utilisateur/datappy.git](https://github.com/terencebon1n/datappy.git)
cd datappy
