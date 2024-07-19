Projet de Gestion des Données d'un Distributeur Automatique de Lait (DAL)
Description
Ce projet permet de traiter les données extraites d'un fichier ZIP et de créer des fichiers CSV via une interface graphique. Il est destiné aux chercheurs de l'INRAE travaillant sur les données d'un distributeur automatique de lait (DAL) de la marque URBAN.

Fonctionnalités principales
Traitement des données contenues dans un fichier ZIP.
Création de fichiers CSV organisés pour faciliter l'analyse.
Interface graphique (GUI) pour interagir avec les données et générer les fichiers CSV.
Structure du Projet
Le projet est structuré comme suit :

Data.py : Gère les fichiers CSV, les modifie et combine les données pour produire un tableau complet.
Output.py : Contient quatre fonctions permettant d'extraire les quatre fichiers CSV de sortie dans le format approprié.
utils.py : Fournit les fonctions nécessaires pour diverses opérations dans les scripts Python.
main.py : Gère l'interface graphique de l'application.
languages.json : Gère les paramètres de langue pour l'interface graphique.
Installation
Pour installer et exécuter le projet, suivez ces étapes :

Clonez le dépôt :

bash
Copier le code
git clone [URL_DU_DEPOT]
Accédez au répertoire du projet :

bash
Copier le code
cd [NOM_DU_REPERTOIRE]
Installez les dépendances (si vous avez un fichier requirements.txt ou une autre méthode pour gérer les dépendances) :

bash
Copier le code
pip install -r requirements.txt
Exécutez le programme principal :

bash
Copier le code
python main.py
Utilisation
Charger les données :

Ouvrez l'interface graphique et chargez le fichier ZIP contenant les données du DAL.
Générer les fichiers CSV :

Utilisez les options disponibles dans l'interface graphique pour générer les fichiers CSV nécessaires.
Explorer les fichiers CSV :

Les fichiers CSV seront créés dans le répertoire de sortie spécifié et peuvent être consultés pour l'analyse.
Exemple d'utilisation de l'interface graphique
Charger le fichier ZIP : Cliquez sur le bouton "Charger" pour sélectionner et importer le fichier ZIP contenant les données.
Générer les CSV : Cliquez sur le bouton "Générer CSV" pour produire les fichiers CSV requis.
Contribuer
Pour contribuer au projet :

Forkez le dépôt.
Créez une branche pour vos modifications (git checkout -b feature-nouvelle-fonctionnalité).
Apportez vos changements et committez (git commit -am 'Ajoute une nouvelle fonctionnalité').
Poussez la branche (git push origin feature-nouvelle-fonctionnalité).
Ouvrez une Pull Request pour proposer vos modifications.
Licence
Ce projet est sous la General Public License (GPL). Vous êtes libre de modifier et de redistribuer le code, à condition que les versions dérivées soient également sous GPL.

Auteurs
Votre Nom : Développeur principal
Nom du Maître de Stage : Superviseur du projet
Remerciements
Je tiens à remercier [Nom du Maître de Stage] pour son soutien et ses conseils tout au long de ce stage. Cette expérience a été extrêmement enrichissante.
