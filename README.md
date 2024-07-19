# Projet de Gestion des Données d'un Distributeur Automatique de Lait (DAL)

## Description

Ce projet permet de traiter les données extraites d'un fichier ZIP provenant d'un distributeur automatique de lait(DAL) de la marque URBAN et de créer des fichiers CSV via une interface graphique. Il est initalement destiné aux chercheurs de l'INRAE travaillant sur ces données. 

### Fonctionnalités principales

- Traitement des données contenues dans un fichier ZIP.
- Interface graphique (GUI) pour interagir avec les données et générer les fichiers CSV.
- Création de fichiers CSV organisés pour faciliter l'analyse.

## Structure du Projet V1

Le projet est structuré comme suit :

- `dal_graphique.py` : Gère l'interface graphique de l'application.
- `data_day_by_day.py` : Génère les données des veaux jour par jour.
- `data_pass_by_pass.py` : Crée les données avec une buvée par veau.
- `SIGPA.py` : Génère le fichier CSV contenant les données pour la base SIGPA.

## Structure du Projet V2

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
2. **Installez les dépendances** :
   ```bash
    pip install -r requirements.txt
3. **Accédez au répertoire de la version du projet** :
   ```bash
   cd [Version_du_project]
4. **Exécutez le programme principal** :
   ```bash
   python main.py

## Utilisation

1. #### Charger les données :

   Ouvrez l'interface graphique et chargez le fichier ZIP contenant les données du DAL.

2. #### Générer les fichiers CSV :

   Utilisez les options disponibles dans l'interface graphique pour générer les fichiers CSV nécessaires.

3. #### Explorer les fichiers CSV :

   Les fichiers CSV seront créés dans le répertoire de sortie spécifié et peuvent être consultés pour l'analyse.
   
## Exemple d'utilisation de l'interface graphique
-  Lancez le fichier main.py ou dal_graphique.py.
-	Charger le fichier ZIP : Cliquez sur le bouton "Browse/rechercher" pour sélectionner et importer le fichier ZIP contenant les données.
-	Générer les CSV : Remplisez le GUI avec les bouton d’information pour vous guider t cliquez sur "Extract/Extraire" pour extraire les differents fichiers CSV

## Transformer en executable windows (ex:V2)
1. **Installez pyinstaller** :
   ```bash
   pip install pyinstaller
2. **Allez dans le repertoire contenant le GUI** :
   ```bash
    cd v2
3. **creez l'executable** :
   ```bash
   pyinstaller --onefile --noconsole --add-data "languages.json;." main.py


## Licence

Ce projet est sous la General Public License (GPL). Vous êtes libre de modifier et de redistribuer le code, à condition que les versions dérivées soient également sous GPL.

## Auteurs

- Nom : Botté Siméon
- Maître de Stage : Christophe Staub

