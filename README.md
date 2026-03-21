# Système de recommandation agricole
## Sommaire

1. [Présentation](#présentation)
2. [Organisation](#organisation)
3. [Analyse exploratoire des fichiers sources](#analyse-exploratoire-des-fichiers-sources)

## Présentation

Ce projet a pour but de réaliser une développer une application web simple et intuitive pour aider les agriculteurs à prendre de meilleurs décisions.
L'application aura deux fonctions au sein de la même interface :

1. Fonction de prédiction : Permettre à un utilisateur de sélectionner une culture spécifique, de renseigner les conditions de sa parcelle (température, usage de pesticides, etc.) et d'obtenir une estimation chiffrée du rendement attendu.

2. Fonction de recommandation : L'utilisateur renseigne uniquement les conditions de sa parcelle, et l'application lui recommande la culture la plus rentable en simulant le rendement pour toutes les cultures possibles et en affichant un classement.

Nous avons eu à disposition deux datasets :
- Agriculture Crop Yield.zip
    - Fichier crop_yield.csv
- Crop Yield Prediction Dataset.zip
    - pesticides.csv
    - rainfall.csv
    - temp.csv
    - yield_df.csv
    - yield.csv

## Organisation

```
├── data/                                      # Dossier contenant nos fichiers csv bruts et transformés
│   └── processed/                             # Création des nouveaux fichiers csv 
│       ├──yield_df_final.csv                
│   └── raw/                                   # Les éléments de base du projet
│       ├──crop_yield.csv                      
│       ├──pesticides.csv                       
│       ├──rainfall.csv                   
│       ├──temp.csv                     
│       ├──yield.csv                   
├── scripts/                                   # Scripts généraux
│   ├──config.py                         
│   ├──data_cleaning.py               
├── notebooks/                                 # Notebook pour l'analyse des données & dossier graph
│   ├──notebook_analyse_exploratoire.ipynb
│   ├──graph                                           
├── .gitignore                                 # Permet de ne pas afficher les éléments sélectionnés sur GitHub
├── poetry.lock                                # Pas versionné sur Git
├── pyproject.toml                             # Gestion des dépendances Poetry
├── README.md                                  # Documentation du projet
```

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

#### Analyse des composantes principales

Étant donnée que nous avons beaucoup de données dans ce fichier, nous allons utiliser la méthode ACP pour nous permettre d'aller un peu plus loin dans l'analyse exploratoire.

- Réduction des dimensions :

Nos variables sont indépendantes, ce qui nous permet de pouvoir avoir une bonne réduction des dimensions. Nous avons étudié avec 5 composantes principales, elles sont autour des 10% pour chaque.

- Identification des variables clés :
    - **Même si l’ACP ne réduit pas beaucoup la dimension, elle reste très utile pour comprendre les relations.**
    - PC1 :
        - conditions/intensité de croissance plus fortes” vs “cycle plus long
    - PC2 :
        - PC2 est surtout un axe lié à la pluie, opposé à un bloc de variables agricoles/cycle
    - PC3 :
        - irrigation vs température
    - PC4 :
        - fertilisation et autres conditions de croissance
    - PC5 : 
        - cycle plus long et environnement plus humide

- Cercle de corrélation :

![alt text](notebooks/graph/cercle_correlation.png)

- Les variables alignées, elles pointent dans la même direction :
    - Fertilizer_Used
    - Temperature_Celsius
    - Irrigation_Used
    - Ces variables sont positivement corrélées entre elles
- Variable opposée : Days_to_Harvest est négativement correlé avec celles du dessus
    - plus d’engrais / température / irrigation = moins de jours jusqu’à récolte
- Variable isolée :
    - Rainfall : Rainfall est faiblement corrélée aux autres variables

- 3 dimensions réelles : intensité agricole / durée de culture / conditions climatiques

### Proxy

Un proxy est une variable qui remplace quelque chose qu'il ne peut pas être mesuré directement.

Variable, proxy de :
- Rainfall_mm : disponibilité en eau
- Irrigation_Used : gestion de l’eau
- Fertilizer_Used : fertilité du sol
- Temperature_Celsius : conditions climatiques
- pesticides_tonnes : intensité agricole

Les variables utilisées dans le modèle sont des proxies permettant d’approcher des phénomènes agronomiques complexes, tels que la disponibilité en eau ou la fertilité du sol.

2. Fichiers présents dans Crop Yield Prediction Dataset

### Fichier pesticides.csv

On retrouve dans ce fichier l'utilisation en tonne de pestice par pays et par année.

Après analyse du fichier :
- Pas de doublons
- Pas de valeurs manquantes
- Présence de valeurs extrêmes

La présence de valeur extrême est expliqué par un gros écart entre les gros utilisateurs de pesticide et les petits utilisateurs.
**Le top 5 des plus gros utilisateurs de pesticide représente 66% de la valeur globale.**

### Fichier rainfall.csv

On retrouve dans ce fichier les précipitations en mm par pays et par année.

Après analyse du fichier :
- Pas de doublons
- + de 11% de valeurs manquantes dans la variable des précipitations.
- Identification de 25 pays sans valeur, sans aucune valeur par année.
- **Choix d'imputer par la moyenne global les pays pour ne pas perdre trop de données.**

### Fichier temp.csv

On retrouve dans ce fichier les températures moyennes par pays et par année.

Après analyse du fichier :
- Doublons trouvés
- 3% de données manquantes pour la variable température

### Fichier yield.csv

On retouve dans ce fichier un dataset central par pays, par année, par type de culture ainsi que les valeurs de rendements.
Ce fichier comporte plus de données que les 2 autres datasets et il serait intéressant de les consolider avec ce fichier.

Distribution de la variable de rendement :

![alt text](notebooks/graph/distribution_variable_cible_fichier_yield.png)

On voit un étalement vers la gauche. Les données se suivent pas une distribution quasi normale comme le premier dataset. Le fichier est plus déséquilibré.

### Fichier yield_df.csv

On retouve dans ce fichier un dataset déjà consolidé entre yield et les 3 fichiers concernant les conditions météos.

Après analyse du fichier :
- Difficulté de savoir comment a été traité le fichier
- Pas de valeurs manquantes
- Doublons trouvés sur les températures notamment.

Pour une meilleure analyse, nous allons consolider un nouveau fichier yield_df.

### Nouveau fichier consolidé :

Avant de pouvoir étudier correctement les relations entre les différentes conditions météoroliques, nous devons consilider les fichiers suivants :
- yield.csv
- pesticides.csv
- rainfall.csv
- temp.csv

Le fichier central est yield, nous allons donc faire des jointures sur ce fichier.
Il y a plusieurs problématiques :
- Pas exactement les mêmes noms pour tous les pays
- Un nombre d'années différent entre les fichiers
- Impact potentiel, un nombre de NaN conséquent pour certains pays et certaines années.

Choix méthodoliques :

- On a identifié quelques pays avec des noms mal orthographiés, on change les noms, il y a sûrement quelques trous dans la raquette..
- On prend uniquement un certain nombre d'année pour être cohérent. Dans yield on ve retenir que les années à partir des années 1990 jusqu'aux années les plus récentes.
- Après la fusion des datasets, on fait le choix d'une imputation par la médiane pour éviter de supprimer trop facilement des données.
    - Imputation par pays ou par culture. Si un pays a déjà des données pour une année, on va prendre cette moyenne.
    - Imputation par la médiane sur l'ensemble des données si pas de moyenne du tout.
(Matrice de corrélation dans le notebook)

- Premiers résulats :

    - On note une corrélation assez forte entre les températures moyennes et les précipitations
    - Avec la valeur cible c'est la valeur des pesticides qui a un lien + fort que les autres
    - Relation négative entre les températures et les pesticides ainsi qu'entre les rendements et les températures

### Matrice corrélation

![alt text](notebooks/graph/matrice_correlation_spearman.png)

### Comparaison ACP vs dataset prediction

L’ACP montre que la variance est répartie de manière homogène entre les composantes, ce qui indique l’absence de structure dominante et de fortes corrélations entre les variables explicatives.
La matrice de corrélation confirme ce constat, avec des coefficients globalement faibles, traduisant des relations linéaires limitées entre variables, ainsi qu’avec la variable cible.

Il n'y a de relation directe entre notre premier dataset (celui pour l'ACP) et les autres datasets.
- Le premier fichier est par grande région et culture
- Le deuxième fichier est par pays, par année puis par culture
- Le rapprochement des données serait très bancal.