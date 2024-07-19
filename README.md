# Projet de Gestion des Données d'un Distributeur Automatique de Lait (DAL)

## Description

Ce projet permet de traiter les données extraites d'un fichier ZIP et de créer des fichiers CSV via une interface graphique. Il est destiné aux chercheurs de l'INRAE travaillant sur les données d'un distributeur automatique de lait (DAL) de la marque URBAN. 

### Fonctionnalités principales

- Traitement des données contenues dans un fichier ZIP.
- Création de fichiers CSV organisés pour faciliter l'analyse.
- Interface graphique (GUI) pour interagir avec les données et générer les fichiers CSV.

## Structure du Projet

Le projet est structuré comme suit :

- `Data.py` : Gère les fichiers CSV, les modifie et combine les données pour produire un tableau complet.
- `Output.py` : Contient quatre fonctions permettant d'extraire les quatre fichiers CSV de sortie dans le format approprié.
- `utils.py` : Fournit les fonctions nécessaires pour diverses opérations dans les scripts Python.
- `main.py` : Gère l'interface graphique de l'application.
- `languages.json` : Gère les paramètres de langue pour l'interface graphique.

## Installation

Pour installer et exécuter le projet, suivez ces étapes :

1. **Clonez le dépôt** :
   ```bash
   git clone [URL_DU_DEPOT]
