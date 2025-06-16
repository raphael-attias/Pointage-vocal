Pointage vocal des participants
===============================

Une application Streamlit permettant de pointer automatiquement la présence des invités par reconnaissance vocale.

Fonctionnalités
---------------

- Import d’un fichier Excel ou CSV avec la liste des invités (Nom, Prénom, Email)
- Reconnaissance vocale avec Google Speech Recognition
- Tolérance d’erreur via fuzzy matching
- Reconnaît "Nom Prénom" ou "Prénom Nom" sans distinction
- Conservation des participants déjà marqués comme présents
- Téléchargement du fichier mis à jour avec la colonne "Présent"

Format du fichier CSV attendu
-----------------------------

Nom,Prénom,Email
Dupont,Jean,jean.dupont@email.com
Martin,Claire,claire.martin@email.com
...

Le programme ajoute automatiquement une colonne "Présent".

Dépendances
-----------

- streamlit
- pandas
- speechrecognition
- pyaudio
- fuzzywuzzy
- openpyxl


