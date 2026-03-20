# Système de recommandation agricole
## Sommaire

[Analyse exploratoire des fichiers sources](#analyse-exploratoire-des-fichiers-sources)

## Analyse exploratoire des fichiers sources

Nous avons eu à disposition deux datasets :
- Agriculture Crop Yield.zip
    - Fichier crop_yield.csv
- Crop Yield Prediction Dataset.zip
    - pesticides.csv
    - rainfall.csv
    - temp.csv
    - yield_df.csv
    - yield.csv

La première chose réalisée a été l'analyse exploratoire de l'ensemble des fichiers.

### 1. Fichier identifié comme source principale pour la modélisation : crop_yield.csv

#### Description

On retrouve des informations cruciales pour le projet :
- Type de culture : riz, coton etc
- Grande région : west, south etc
- Conditions climatiques :
    - précipitation
    - température
    - nombre de jours de récolte
    - conditions météorologiques (cloudy, rainy etc)
- Type d'utilisation agricole :
    - utilisation de fertilisant
    - utilisation d'irrigation
- **Variable cible** : le rendement en tonne par hectare -> variable recherchée par le modèle

La distibution de notre variable cible :

![alt text](notebooks/graph/distribution_variable_cible.png)

Notre distribution ressemble à une cloche, donc à une distribution normale même si on ne peut pas la considérer comme telle car on voit quelques petits dépassements.

#### Nettoyage

- On retrouve également quelques valeurs aberrantes sur notre variable cible. On peut voir des rendements négatifs donc nous avons décidé de les suppirmer car cela concerne uniquement 231 lignes sur les 1 million.
- Afin de préparer le fichier pour l'ACP, on décide de mettre les variables **Fertilizer_Used** et **Irrigation_Used** en numérique (0 ou 1 car les valeurs étaient True or False).