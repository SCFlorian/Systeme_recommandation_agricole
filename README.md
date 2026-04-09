---
title: Agritech Interface
emoji: 🌾
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
---

# Système de recommandation agricole 
## Sommaire

1. [Présentation](#présentation)
2. [Organisation](#organisation)
3. [Fonctionnalités](#fonctionnalités)
3. [Prérequis](#prérequis)
4. [Installation](#installation)
5. [Analyse exploratoire des fichiers sources](#analyse-exploratoire-des-fichiers-sources)
6. [Enrichissement du fichier consolidé](#enrichissement-du-fichier-consolidé)
7. [Feature engineering sur le fichier enrichi](#feature-engineering-sur-le-fichier-enrichi)
8. [Feature engineering sur le fichier consolidé](#feature-engineering-sur-le-fichier-consolidé)
9. [Modélisation](#modélisation)
10. [Interprétabilité du modèle feature importance et SHAP values](#interprétabilité-du-modèle-feature-importance-et-shap-values)
11. [Perspectives](#perspectives)

## Présentation

Ce projet a pour but de réaliser une application web simple et intuitive pour aider les agriculteurs à prendre de meilleurs décisions.
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
├── .github/workflows/                         # Configuration de la CI/CD
│   ├──cicd.yaml
├── data/                                      # Dossier contenant nos fichiers csv bruts et transformés
│   └── processed/                             # Création des nouveaux fichiers csv 
│       ├──yield_df_final.csv
│       ├──yield_df_enriched.csv                  
│   └── raw/                                   # Les éléments de base du projet
│       ├──crop_yield.csv
│       ├──FAOSTAT_data_en_4-6-2026.csv        # Fichier pour récupérer les régions                 
│       ├──pesticides.csv                      
│       ├──rainfall.csv                   
│       ├──temp.csv 
│       ├──UNSD — Methodology.csv              # Fichier pour récupérer les prix par type de culture
│       ├──yield.csv   
├── model/                                     # Dossier contenant le meilleur modèle retenu
├── notebooks/                                 # Notebook & dossier graph
│   ├──notebook_analyse_exploratoire.ipynb
│   ├──notebook_feature_engineering.ipynb
│   ├──notebook_feature_modelisation.ipynb
│   ├──graph
├── scripts/                                   # Scripts généraux
│   ├──config.py                         
│   ├──data_cleaning.py 
│   ├──preprocessing_pipeline.py
├── tests/                                     # Tests unitaires et fonctionnels
│   ├──test_endpoint.py                         
│   ├──test_logic.py 
│   test_simple.py
├── .env                                       # Code secret HF pas versionné 
├── .gitignore                                 # Permet de ne pas afficher les éléments sélectionnés sur GitHub
├── app.py                                     # L'application FastAPI
├── Dockerfile                                 # Description étape pour création d'une image de conteneur
├── poetry.lock                                # Pas versionné sur Git
├── pyproject.toml                             # Gestion des dépendances Poetry
├── README.md                                  # Documentation du projet
├── streamlit.py                               # Interface du projet
```
## Fonctionnalités

- Pipeline ML de bout en bout
- Tracking des expérimentations avec MLFlow
- API en local avec FastAPI
- Déploiement de l'interface sur Hugging Face Spaces
- Hebergement du model de ML sous Hugging Face Models
- Interface avec streamlit
- 1 fonction de prédiction et 1 fonction de recommandation

## Prérequis

- Python 3.12+
- Avoir un compte sur Hugging Face
- Token Hugging Face (se diriger vers https://huggingface.co/settings)
- Avoir le token HF sur Github et Hugging Face afin de créer le lien entre eux

## Installation

1. **Cloner le dépôt**

```
git clone git@github.com:SCFlorian/Systeme_recommandation_agricole.git
cd Systeme_recommandation_agricole
```

2. **Installez les dépendances : Le projet utilise pyproject.toml pour la gestion des dépendances :**
```
poetry install --no-root
```
3. **Ouvrir le projet dans VS Code :**
```
code .
```
4. **Configurez l’environnement Python dans VS Code**
    1.	Installez l’extension Python (si ce n’est pas déjà fait).
    2.	Appuyez sur Ctrl+Shift+P (Windows/Linux) ou Cmd+Shift+P (Mac).
    4.	Recherchez “Python: Select Interpreter”.
    5.	Sélectionnez l’environnement créé par Poetry ou celui dans lequel tu as installé le projet.

5. **Configurez le token Hugging Face**

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```
HF_TOKEN=votre_token_hf
```

6. Génération d'un modèle depuis le notebook de modélisation
    1. Enregistrement du modèle retenu avec joblib
    2. Déposez le modèle dans votre compte HF dans models
    3. Changez dans config le nom de votre repo HF pour effectuer les bons liens
7. Génération de l'interface
    - Push sur main et le déploiement s'effectue

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

### Fichier crop_yield.csv

#### Description

On retrouve des informations importantes :
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
- **Variable cible** : le rendement en tonne par hectare -> variable cible
- On retrouve 10 colonnes pour 1 million de lignes
- Le fichier semble avoir des données synthétiques
- Valeur unique par variable catégorielle :
```
Nombre de valeur unique : Soil_Type: 6
Nombre de valeur unique : Crop: 6
Nombre de valeur unique : Fertilizer_Used: 2
Nombre de valeur unique : Irrigation_Used: 2
Nombre de valeur unique : Weather_Condition: 3
```

La distibution de notre variable cible :

<img width="800" height="400" alt="Image" src="https://github.com/user-attachments/assets/cdc01b6a-ac60-4681-9b00-60ebe629978d" />

Notre distribution ressemble à une cloche, donc à une distribution normale même si on ne peut pas la considérer comme telle car on voit quelques petits dépassements.


#### Nettoyage

- Boxplot pour analyser le type de culture par rapport au rendement.

<img width="640" height="480" alt="Image" src="https://github.com/user-attachments/assets/b9390456-6099-4587-88f3-6fd2dcbf7d60" />

- On retrouve quelques valeurs aberrantes sur notre variable cible. On peut voir des rendements négatifs donc nous avons décidé de les supprimer car cela concerne uniquement 231 lignes sur les 1 million.
- Les valeurs "extrêmes" supérieurs sont moins présents et ne présentent pas d'anomalies statistiques.
- Afin de préparer le fichier pour l'ACP, on décide de mettre les variables **Fertilizer_Used** et **Irrigation_Used** en numérique (0 ou 1 car les valeurs étaient True or False).

#### Analyse des composantes principales

Étant donnée que nous avons beaucoup de données dans ce fichier, nous allons utiliser la méthode ACP pour nous permettre d'aller un peu plus loin dans l'analyse exploratoire.

- Réduction des dimensions :

Nos variables sont indépendantes, ce qui nous ne permet pas de réaliser une bonne réduction des dimensions. Nous avons étudié avec 5 composantes principales, elles sont autour des 20% pour chaque.

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

<img width="800" height="800" alt="Image" src="https://github.com/user-attachments/assets/c5fc4b07-70b3-44d4-8106-71a2384e9c99" />

- Les variables alignées, elles pointent dans la même direction :
    - Fertilizer_Used
    - Temperature_Celsius
    - Irrigation_Used
- Variable opposée : Days_to_Harvest est négativement correlé avec celles du dessus
    - plus d’engrais / température / irrigation = moins de jours jusqu’à récolte
- Variable isolée :
    - Rainfall : Rainfall est faiblement corrélée aux autres variables

- 3 dimensions réelles : intensité agricole / durée de culture / conditions climatiques

### Proxy

Un proxy est une variable qui remplace quelque chose qu'il ne peut pas être mesuré directement.

Variable, proxy de :
- Irrigation_Used : gestion de l’eau
- Fertilizer_Used : fertilité du sol

Les variables utilisées dans le modèle sont des proxies permettant d’approcher des phénomènes agronomiques complexes, tels que la disponibilité en eau ou la fertilité du sol.

On réalise alors que nous allons se servir des éléments que nous avons ici pour enrichir notre futur fichier pour la modélisation. Voici les éléments que nous chercherons à ajouter :

- Irrigation_Used
- Fertilizer_Used
- Weather_Condition
- Soil_Type

2. Fichiers présents dans Crop Yield Prediction Dataset

### Fichier pesticides.csv

On retrouve dans ce fichier l'utilisation en tonne de pestice par pays et par année.

Après analyse du fichier :
- Pas de doublons
- Pas de valeurs manquantes
- Présence de valeurs extrêmes

La présence de valeur extrême est expliquée par un gros écart entre les gros utilisateurs de pesticide et les petits utilisateurs.
**Le top 5 des plus gros utilisateurs de pesticide représente 66% de la valeur globale.**

On a analysé les pays en "écart", rien ne semble anormal, ce sont des pays qui peuvent être des gros utilisateurs.

**Évolution de l'utilisation des pesticides dans le temps**

<img width="1000" height="600" alt="Image" src="https://github.com/user-attachments/assets/e0fcb6ba-2ec4-4d83-8c8f-7b63686f2621" />

- Depuis les années 2000 jusqu'en 2006, on remarque une croissance de l'utilisation des pesticides de manière globale.
- Une petite en chute en 2009 avec une légère progression ensuite mais depuis 2011, l'utilisation reste constante.

### Fichier rainfall.csv

On retrouve dans ce fichier les précipitations en mm par pays et par année.

Après analyse du fichier :
- Pas de doublons
- + de 11% de valeurs manquantes dans la variable des précipitations.
- Identification de 25 pays sans valeur, sans aucune valeur par année.
```
Liste des pays avec des valeurs nulles : 
<StringArray>
[           'American Samoa',                     'Aruba',
                   'Bermuda',    'British Virgin Islands',
            'Cayman Islands',           'Channel Islands',
                   'Curacao',             'Faroe Islands',
          'French Polynesia',                 'Gibraltar',
                 'Greenland',                      'Guam',
      'Hong Kong SAR, China',               'Isle of Man',
                    'Kosovo',          'Macao SAR, China',
                    'Monaco',             'New Caledonia',
  'Northern Mariana Islands',                'San Marino',
 'Sint Maarten (Dutch part)',  'St. Martin (French part)',
                     'Tonga',  'Turks and Caicos Islands',
     'Virgin Islands (U.S.)']
Length: 25, dtype: str

============================

Liste des pays avec au moins une valeur non nulle : 
        Area  Year average_rain_fall_mm_per_year
4061  Monaco  1985                            ..
```

### Fichier temp.csv

On retrouve dans ce fichier les températures moyennes par pays et par année.

Après analyse du fichier :
- Doublons trouvés : il y a une répétition de plusieurs années par pays.
- 3% de données manquantes pour la variable température.
- On retrouve des dates très anciennes, à partir de 1743.
- Les valeurs de la température vont de -14 à 30 degrès.

### Fichier yield.csv

On retouve dans ce fichier un dataset central par pays, par année, par type de culture ainsi que les valeurs de rendements.
Ce fichier est central et sera donc le fichier à consolidé avec les fichiers des conditions climatiques.

**Distribution de la variable de rendement :**

<img width="800" height="400" alt="Image" src="https://github.com/user-attachments/assets/2c793cd5-abe9-4cad-8d37-4197ea4ac319" />

On voit un étalement vers la gauche. Les données se suivent pas une distribution quasi normale comme le premier dataset. Le fichier est + déséquilibré.

**Boxplot par type de culture et rendement :**

<img width="1400" height="700" alt="Image" src="https://github.com/user-attachments/assets/e651fc71-b238-4fac-959c-d243b3d31f22" />

- On peut voir quelques valeurs à 0. Difficile de savoir si on les supprime ou non car théoriquement un rendement à 0 c'est possible si les conditions ne sont pas réunies pour une production. Mais certaines valeurs ressemblantes ont des données de rendement. Nous avons seulement 8 valeurs à 0 alors on peut les supprimer.
- On voit une valeur énorme pour Plaintains and more
    - La valeur extrême date de 1964, nous irons pas dans des dates aussi antérieures donc elle sera enlevée par défaut par la suite.
- On voit un fort déséquilibre entre les types de culture. On peut noter que la catégorie Potatoes semble avoir avoir des rendements plus élevés que les autres. Ce sont des valeurs extrêmes mais pas aberrantes car elles sont réelles alors nous devons les laisser. 

### Fichier yield_df.csv

On retouve dans ce fichier un dataset déjà consolidé entre yield et les 3 fichiers concernant les conditions météos.

Après analyse du fichier :
- Difficulté de savoir comment a été traité le fichier
- Pas de valeurs manquantes
- Doublons trouvés sur les températures notamment.

Pour une meilleure analyse, nous allons consolider un nouveau fichier yield_df car nous ne savons pas comment ce fichier a été construit.

### Nouveau fichier consolidé :

Avant de pouvoir étudier correctement les relations entre les différentes conditions météorologiques, nous devons consolider les fichiers suivants :
- yield.csv
- pesticides.csv
- rainfall.csv
- temp.csv

Le fichier central est yield, nous allons donc faire des jointures sur ce fichier.
Il y a plusieurs problématiques :
- Pas exactement les mêmes noms pour tous les pays
- Un nombre d'années différent entre les fichiers
- Impact potentiel, un nombre de NaN conséquent pour certains pays et certaines années.

Choix méthodologiques :

- Harmonisation des noms de pays pour assurer la compatibilité entre les différentes sources
- Restriction à la période commune (1990–2016) afin d’éviter des valeurs manquantes excessives, notamment sur les données de température et avoir des années récentes
- Fusion progressive des datasets en conservant yield.csv comme base principale
- Ajout de la région par pays afin d'avoir un détail plus fin.
- Création de variables indicatrices (région/item/condition climatique) de valeurs manquantes pour conserver l’information liée à l’absence de données --> utilisation des quartiles
- Imputation des valeurs manquantes en fonction des "bins" afin de ne pas imputer des valeurs globales qui pourraient fausser les données
- Cela va nous permettre de limiter la suppression des données

1. Harmonisation du nom des pays

- Extraction de chaque pays uniques dans les 4 fichiers.
- Envoie des pays à un LLM pour lui demander plusieurs noms possibles par pays
- Mapping des fichiers avec un nom de pays standardisé
- Identification d'un doublon supplémentaire grâce à l'harmonisation
- **TOTAL : 44 pays uniques ont été harmonisés sur l'ensemble du projet. Exemple pour un fichier :**
```
--- Rapport pour Yield ---
Nombre total de pays uniques : 212
Nombre de pays modifiés : 28
Exemples de modifications :
  - The former Yugoslav Republic of Macedonia -> North Macedonia
  - Occupied Palestinian Territory -> Palestine
  - Saint Lucia -> St. Lucia
  - China, Taiwan Province of -> Taiwan
  - Cabo Verde -> Cape Verde
  ```

2. Harmonisation du nom des variables et restriction de la temporalité
- Ajout de nom de varibale cohérent
- Temporalité commune : 1990 -> 2016
    - Avoir en tête que le fichier temp s'arrêtait en 2013

3. Gestion des doublons sur le fichier temp

- Regroupement des pays par année et par pays en effectuant la médiane de la température

4. Fusion des datasets à partir de yield
- Merge des fichiers un à un
- Passage à 7 colonnes et 29 151 lignes avec des valeurs manquantes pour les conditions climatiques. Valeurs manquantes :
    - avg_temp -> 0.363521
    - pesticides_tonnes -> 0.171452
    - rainfall_mm -> 0.102261

5. Imputation sur les valeurs manquantes
- Ensuite nous voulons améliorer la distinction des pays alors nous avons sélectionné un dataset afin d'ajouter les grandes régions par pays
    - https://unstats.un.org/unsd/methodology/m49/overview/ : dataset sélectionné
    - Pour cela nous devons faire matcher encore une fois le noms des pays avec le dataset, nous devons modifier "à la main" 37 pays qui ne correspondaient pas
    - Exemple de région :

```
    Sub-region Name                  area                           
Australia and New Zealand        Australia                          189
                                 New Zealand                        108
Central Asia                     Kazakhstan                         150
                                 Kyrgyzstan                         150
                                 Tajikistan                         149
                                 Turkmenistan                       100
                                 Uzbekistan                         125
Eastern Asia                     China                              216
                                 Hong Kong                           47
                                 Japan                              189
                                 Mongolia                            54
                                 North Korea                        189
                                 South Korea                        189
                                 Taiwan                             216
```

- Création de groupe climatique :
    - les variables climatiques divisées en quartiles
    - puis création d'une nouvelle variable avec la région, le type de culture et le numéro de catégorie de chaque variable climatique, exemple : **Central Asia_Wheat_3_2_3**
- Imputation des NaN en fonction de la nouvelle variable

6. Fichier consolidé

**Tableau final**
```
area	     region	        year	item   avg_temp  rainfall_mm  pesticides_tonnes	 yield
Afghanistan	 Southern Asia	1990	Maize  15.45	 327.0	      1594.5	         17582
Afghanistan	 Southern Asia	1991	Maize  14.57	 327.0	      1594.5	         16800
Afghanistan	 Southern Asia	1992	Maize  14.35	 327.0	      1594.5	         15000
Afghanistan	 Southern Asia	1993	Maize  14.96	 327.0	      1594.5	         16786
Afghanistan	 Southern Asia	1994	Maize  14.94	 327.0	      1594.5	         16667

```

Cet exemple est pertinent :

- On voit des données de température différente par année pour un même pays : les données étaient ainsi dans le fichier temp
- La région est bien rajoutée
- Pour rainfall les données de base sont répetées par année
- Pour ce pays en particulier il n'y avait pas d'informations pour les pesticides, ces données ont été imputé
- On observe bien un rendement différent par année pour un même pays

**Matrice corrélation**

<img width="800" height="600" alt="Image" src="https://github.com/user-attachments/assets/e2b81dff-484e-46b6-94be-60a312ba165f" />

- On note une corrélation assez forte entre les températures moyennes et les précipitations
- Avec la valeur cible c'est la valeur des pesticides qui a un lien + fort que les autres
- Relation négative entre les températures et les pesticides ainsi qu'entre les rendements et les températures

### Comparaison ACP vs dataset prediction

L’ACP montre que la variance est répartie de manière homogène entre les composantes, ce qui indique l’absence de structure dominante et de fortes corrélations entre les variables explicatives.
La matrice de corrélation confirme ce constat, avec des coefficients globalement faibles, traduisant des relations linéaires limitées entre variables, ainsi qu’avec la variable cible.

## Enrichissement du fichier consolidé

Il n'y a de relation directe entre notre premier dataset (celui pour l'ACP) et les autres datasets.
- Le premier fichier est par grande région et culture
- Le deuxième fichier est par pays, par année puis par culture
- Le rapprochement des données serait très bancal.

**Mais nous avons identifié des variables proxy qui pourraient enrichir notre dataset :**
- Irrigation_Used
- Fertilizer_Used
- Weather_Condition
- Soil_Type

Le fichier crop_yield semble être un fichier synthétique :
- Pas de corrélation entre les variables explicatives
- Répartition à quasi 50/50 des valeurs pour chaque variables 

Plusieurs méthodes d'enrichissement ont été effectué :
- Modèle de régression logistique afin de prédire les différentes variables sur le nouveau fichier
    - Variables explicative : précipitation et température
    - Après un test, le modèle n'arrive pas à généraliser, les variables explicatives sont indépendantes entre elles Les données sont "plates" (sans corrélations fortes), le modèle de ML essayait de trouver une règle là où il n'y en a pas
    - Par exemple, la balanced_accuracy était à 0,50 pour le fertilisant et l'irrigation
```
============================================================
RÉSUMÉ GLOBAL
============================================================
target             accuracy   balanced_accuracy   f1_macro   log_loss
Fertilizer_Used    0.501995   0.501995            0.501987   0.693143
Irrigation_Used    0.499895   0.499747            0.489134   0.693148
Weather_Condition  0.334300   0.334245            0.333182   1.098607
Soil_Type          0.166765   0.166608            0.142119   1.791780
```

- Méthode de stratification par catégorie afin de faire le rapprochement sur le nouveau fichier en utilisation la valeur la plus fréquente (mode())
    - La mise en place de la stratification était simple (en quartiles)
    - Le problème est l'utilisation de la valeur fréquente. Quand il y a une valeur qui se démarque, cela fonctionne bien. Cependant sur une égalité, le mode choisit aléatoirement
- Méthode de sampling conditionnel afin d'attribuer la distribution de crop_yield par culture/clé climatique puis choix statistique de la valeur avec une fonction random
    - Méthode retenue

### Méthode du sampling conditionnel

- Standardisation des noms des types de culture entre les fichiers
- Autre problématique : nous avons uniquement 4 cultures en communs entre les 2 fichiers

**Méthode**

1. Construction des groupes

Les données sont segmentées selon :
- climate_key (quantiles température + pluie)
- crop (type de culture)

2. Calcul des distributions

Pour chaque variable cible et chaque groupe :
```
P(valeur | climate_key, crop)
```

Exemple :
```
Maize + T2_R4 → Fertilizer_Used :
True  = 70%
False = 30%
```

3. Imputation par sampling

Pour chaque valeur manquante :
- Récupération de la distribution du groupe
- Tirage aléatoire pondéré :
```
np.random.choice(values, p=probabilities)
```

4. Gestion des cas manquants
- crop
- climate_key
- global

5. Conclusion 

Les avantages ici sont :
- le respoect des distributions réelles
- évite les biais
- conserve la variabilité des données

Les limites sont :
- que c'est non déterministe
- que la cohérence individuelle n'est pas garantie

La méthode est validée par :
- une comapraison des distributions avant / après enrichissement
- faible écart global
- absence de biais sur les catégories

Exemple de comparaison par nouvelle variable :
```
=== Fertilizer_Used ===
Source (crop_yield):
Fertilizer_Used
False    0.50006
True     0.49994
Name: proportion, dtype: float64

Final (yield_df_final):
Fertilizer_Used
False    0.501252
True     0.498748
Name: proportion, dtype: float64

=== Irrigation_Used ===
Source (crop_yield):
Irrigation_Used
False    0.500509
True     0.499491
Name: proportion, dtype: float64

Final (yield_df_final):
Irrigation_Used
True     0.503482
False    0.496518
Name: proportion, dtype: float64
```
Exemple de comparaison par type de culture :

```
=== Fertilizer_Used par crop ===
                                        source     final
                     Fertilizer_Used                    
Barley               False            0.500741       NaN
                     True             0.499259       NaN
Cotton               True             0.500609       NaN
                     False            0.499391       NaN
Maize                False            0.501547  0.497063
                     True             0.498453  0.502937
Rice                 True             0.500384  0.500473
                     False            0.499616  0.499527
Soybean              False            0.500219  0.502883
                     True             0.499781  0.497117
Wheat                True             0.501155  0.501368
                     False            0.498845  0.498632
Cassava              False                 NaN  0.508120
                     True                  NaN  0.491880
Plantains and others False                 NaN  0.506292
                     True                  NaN  0.493708
Potatoes             True                  NaN  0.511170
                     False                 NaN  0.488830
Sorghum              False                 NaN  0.519462
                     True                  NaN  0.480538
```

## Feature engineering sur le fichier enrichi

Nous avons désormais consolidé notre dataset :
- Une première fois avec 3 variables climatiques puis imputer de manière rigoureuse pour les données manquantes.
- Une deuxième fois en enrichissant le dataset avec des variables approximatives qui devraient aider notre modèle à mieux généraliser

Nous devons maintenant continuer l'amélioration de nos données en ajoutant des données si possibles,et en transformant nos données pour être compréhensible pour un modèle.

**Nouvelles variables**

```
Ratio climatique - indice d'irrigation critique :
yield_df_enriched['irrigation_impact'] = yield_df_enriched['Irrigation_Used'].astype(int) / (yield_df_enriched['rainfall_mm'] + 1)

Flag de sécheresse (Binaire) :
yield_df_enriched['is_drought'] = (yield_df_enriched['rainfall_mm'] < 200).astype(float)

Déséquilibre intrants/eau (Ecart log) :
yield_df_enriched['input_imbalance'] = np.abs(np.log1p(yield_df_enriched['pesticides_tonnes']) - np.log1p(yield_df_enriched['rainfall_mm']))

Stress thermique simple :
yield_df_enriched['thermal_stress'] = np.abs(yield_df_enriched['avg_temp'] - 20)

On fixe l'année de référence 2016 pour l'interface future :
year_ref = 2016

On crée un score de maturité technologique. Plus l'écart est grand, plus les semences et machines sont supposées performantes :
yield_df_enriched['years_from_now'] = year_ref - yield_df_enriched['year']
```
- Pas relation forte entre nos variables mais on voit que l'ajout des nouvelles variables ne sont pas redondantes avec les features d'origine.

## Feature engineering sur le fichier consolidé

Afin de s'assurer de la pertinence de l'enrichissement de nos données, on va devoir comparer la modélisation entre le fichier enrichi et le fichier consolidé sans enrichissement.

Pour réaliser cela, nous devons effectuer le même feature engineering.

Nous devons maintenant continuer l'amélioration de nos données en ajoutant des données si possibles.

**Nouvelles variables**

```
Flag de sécheresse (Binaire) :
yield_df_final_conso['is_drought'] = (yield_df_final_conso['rainfall_mm'] < 200).astype(float)

Déséquilibre intrants/eau (Ecart log) :
yield_df_final_conso['input_imbalance'] = np.abs(np.log1p(yield_df_final_conso['pesticides_tonnes']) - np.log1p(yield_df_final_conso['rainfall_mm']))

Stress thermique simple :
yield_df_final_conso['thermal_stress'] = np.abs(yield_df_final_conso['avg_temp'] - 20)

On fixe l'année de référence 2016 pour l'interface future :
year_ref = 2016

On crée un score de maturité technologique. Plus l'écart est grand, plus les semences et machines sont supposées performantes :
yield_df_final_conso['years_from_now'] = year_ref - yield_df_final_conso['year']
```

Sans avoir enrichi notre fichier, on ne peut pas ajouter la variable irrigation_impact qui dépend de Irrigation_Used.

**Matrice des corrélations**

<img width="2277" height="1772" alt="Image" src="https://github.com/user-attachments/assets/dff6af55-5ed6-4d2f-9c80-a65fd5ed0faf" />

Nous n'avons pas ici des variables trop corrélées ensemble, nous n'avons pas à enlever d'autres variables.

- Sur ces premiers tests on ne voit pas des meilleurs résultats pour le fichier enrichi, les informations rajoutées ne semblent pas apporter quelque chose d'utile pour nos modèles.
- On voit que le modèle de RandomForest a des meilleurs résulats (sans optimisation des meilleurs paramètres) mais suivi de très près par XGBoost et LightGBM.
- N'ayant pas une distribution linéaire, on voit que la regression linéraire ne généralise pas.

## Modélisation

Dans la phase d'analyse exploratoire et de prétraitement, nous avons fait le choix de tester dans un premier temps les 2 fichiers consolidés que nous avons réalisé :
- dataset consolidé sans enrichissement
- dataset consolidé avec enrichissement (à l'aide du fichier crop_yield)

Suivi de la modélisation avec des pratiques de MLOps, nous utilisons **MLFlow** pour suivre les expérimentations. L'ensemble des tests ont été réalisé dans le notebook dédié à la modélisation. À l'intérieur on va retouver plusieurs blocs :
- un suivi MLFlow de 5 modèles sur le fichier consolidé
- un suivi MLFlow de 5 modèles sur le fichier consolidé avec enrichissement
- un suivi MLFlow pour l'optimisation des hyperparamètres du modèle retenu

### Schéma MLOPs

<img width="1028" height="523" alt="Image" src="https://github.com/user-attachments/assets/6ed0d34a-02ec-4e66-8bb8-ea0f8cb1d1af" />

### Choix des modèles

On a testé 5 modèles différents :
- DummyRegressor
- LinearRegression
- RandomForestRegressor
- XGBRegressor
- LGBMRegressor

**Pourquoi ces modèles ?**

- D’abord, une baseline minimale avec DummyRegressor. Le but était d’avoir un point de comparaison naïf. Ça permet de vérifier que le pipeline apprend réellement quelque chose et qu’on ne se satisfait pas d’un score “bon en apparence”.
- Ensuite, une baseline linéaire avec LinearRegression. Utilisation pour tester l’hypothèse la plus simple : si le rendement s’explique surtout par des relations linéaires entre climat, intrants et culture.
- Ensuite on a testé 3 trois familles d'arbres car le problème mélange :
    - des variables numériques comme avg_temp, rainfall_mm, pesticides_tonnes, thermal_stress etc
    - des variables catégorielles comme region, item, is_drought
    - et potentiellement des relations non linéaires et des interactions fortes entre climat, zone géographique et type de culture.

**Choix du pipeline**

- Pipeline scikit-learn : le préprocessing et le modèle sont encapsulés ensemble, donc on évite les écarts entre train et test.
- Cross-validation : les scores ne reposent pas sur un seul split.
- random_state=42 sur les modèles et le KFold : les résultats sont reproductibles.
- MLflow : chaque run conserve paramètres, métriques et version du modèle.
- Le meilleur pipeline est sauvegardé avec joblib, ce qui facilite la réutilisation et l’audit.
- Les analyses SHAP et feature importance renforcent l’explicabilité en plus de la feature importance.
- Schéma du pipeline :

<img width="399" height="177" alt="Image" src="https://github.com/user-attachments/assets/0a7cc810-5cae-4773-aa07-e965ed55b0e0" />

**Robustesse du pipeline**
- GridSearchCV(..., error_score="raise") : si un entraînement échoue, l’erreur remonte immédiatement.
- si MLflow n’est pas disponible, le tracking peut échouer.
- si un fichier CSV ou un artefact .joblib manque, le notebook s’arrête.
- les cellules SHAP dépendent du pipeline sauvegardé, donc si le modèle n’est pas exporté avant, cette partie casse.

**Métriques des performance des modèles**
- Coefficient de détermination (R2) : mesure la part de variance expliquée par le modèle.
- Erreur quadratique moyenne (RMSE) : mesure l'erreur moyenne en donnant plus de poids aux grosses erreurs.
- Erreur absolue moyenne (MAE) : moyenne des erreurs en valeur absolue
- Erreur relative (MAPE) : erreur en pourcentage
- Erreur économique (economic_error_usd_ha) : c'ets une métrique métier personnalisée, elle convertit l'erreur de prédiction en perte financière par hectare

### Résultats des performances sur le fichier consolidé

Les expérimentations montrent que les modèles d’arbres surpassent nettement les baselines simples.  
Le **RandomForestRegressor** obtient les meilleures performances globales sur le dataset consolidé, avec un **R² test de 0,9436**, un **RMSE de 1712,47 kg/ha** et un **MAE de 804.54 kg/ha**.  

L’enrichissement du dataset à partir du fichier `crop_yield` n’a pas permis d’améliorer les performances de manière significative. Le choix final s’est donc porté sur le **dataset consolidé sans enrichissement**, plus simple, plus lisible et tout aussi performant.

#### **Dans le détail** 

**Sur les 2 modèles "simples"**
- Sur le DummyRegressor et le LinearRegression les résultats ne sont pas bons, c'était attendu. Le Dummy nous sert comme base pour comparer et nous ne sommes pas face à une distribution linéaire alors LinearRegression ne généralise pas bien. Les modèles linéaires montrent leurs limites sur ce problème, ce qui confirme la présence de relations non linéaires entre les variables explicatives et le rendement.

- DummyRegressor :
```
=== Résultats métriques ===
CV RMSE : 7604.3730 (± 187.80)
CV MAE  : 5578.7140 (± 93.2737)
CV R2   : -0.0002 (± 0.0002)
Test RMSE : 7216.6343
Test R2   : -0.0013
Test MAE  : 5378.3028
Test economic_error_usd_ha : 1680.7060
```
- LinearRegression :
```
=== Résultats métriques ===
CV RMSE : 4840.4290 (± 55.16)
CV MAE  : 3233.5153 (± 58.2632)
CV R2   : 0.5943 (± 0.0143)
Test RMSE : 4805.9227
Test R2   : 0.5559
Test MAE  : 3201.1100
Test economic_error_usd_ha : 1033.3629
```
**Comparaison sur tous les modèles**
- Résultats des tests du R2

<img width="1200" height="600" alt="Image" src="https://github.com/user-attachments/assets/f0f6cc35-c0c5-4e31-a8e9-178fb543aff4" />

- Résultats des tests du MAPE 

<img width="1200" height="600" alt="Image" src="https://github.com/user-attachments/assets/2bf8ee15-1d92-4ea4-b43b-0fbf440f6f21" />

Les modèles d’arbres obtiennent des performances nettement supérieures aux modèles de référence.

Par exemple le RandomForest a "seulement" 17% d'erreur en valeur absolue, en comparaison d'une erreur sur 2 pour le LGBMRegressor.


**Petit focus sur ces 2 modèles**
**RandomForestRegressor**
```
=== Résultats métriques ===
CV RMSE : 1893.0226 (± 45.34)
CV MAE  : 894.9234 (± 4.1971)
CV R2   : 0.9378 (± 0.0051)
Test RMSE : 1729.6763
Test R2   : 0.9425
Test MAE  : 796.4869
Test economic_error_usd_ha : 273.6834
```
- Sur la validation croisée on voit que l'écart-type entre les différents folds est petit, les résultats restent stables.
- Le MAE peut est à 796 par kg/ha sur le test. Cela peut sembler haut mais il faut prendre en compte le contexte métier ici où on sait que les rendements dépendent de beaucoup de facteurs et que les prédictions sont à ajuster avec sa connsaissance terrain.


**XGBRegressor**
```
=== Résultats métriques ===
CV RMSE : 2152.0037 (± 71.11)
CV MAE  : 1292.0533 (± 24.5055)
CV R2   : 0.9195 (± 0.0082)
Test RMSE : 2040.8158
Test R2   : 0.9199
Test MAE  : 1226.2530
Test economic_error_usd_ha : 406.6547
```
- Même si les résultats ne sont pas mauvais ils restent bien en-dessous sur toutes les métriques.

**Analyse du MAE par type de culture et du economic_error_usd_ha sur notre meilleur modèle**

- Nous avons vu dans la partie exploratoire un déséquilibre assez fort entre certains type de culture et le rendement. Par exemple on a noté la présence de gros rendement sur la catégorie des pommes de terre. Ces gros écart tirent les erreurs du MAE vers le haut.

<img width="428" height="402" alt="Image" src="https://github.com/user-attachments/assets/d12e1acd-b4eb-49c1-9ab5-333013ff74ae" />

On remarque que les erreurs sont variables entre type de culture, on note par exemple qu'en kg/ha c'est la catégorie avec les plus gros rendements qui a le plus d'erreur.


- Au-delà des métriques de modélisation classiques, une métrique métier a été introduite : `economic_error_usd_ha`.

<img width="1200" height="600" alt="Image" src="https://github.com/user-attachments/assets/566411aa-95aa-4b04-9cf5-13a91fc68ac8" />

- Pour le meilleur modèle, cette erreur est estimée à **273,7 USD/ha**. Le coût n'est pas négligeable selon la taille des champs mais cela reste une estimation et elle est la plus optimisée pour le moment. 
- C’est très utile pour un exploitant agricole, parce qu’on traduit l’erreur de prédiction en impact financier moyen par hectare. Donc on peut répondre non seulement à “le modèle est-il précis ?”, mais surtout à :
    - combien coûte une mauvaise estimation de rendement
    - si une recommandation est économiquement exploitable

- Le Random Forest présente le meilleur compromis entre précision, stabilité et interprétabilité.

### Comparaison des performances des modèles sur le fichier consolidé et le fichier enrichi


<img width="707" height="765" alt="Image" src="https://github.com/user-attachments/assets/1a36ec71-d4b9-471c-a34f-f77f3a9061d1" />

Un second dataset a été construit en enrichissant le fichier consolidé avec des variables proxy issues du fichier `crop_yield`.  
L’objectif était d’évaluer si cet enrichissement permettait d’améliorer la capacité de généralisation des modèles.

Les résultats obtenus montrent toutefois que cet enrichissement n’apporte pas de gain mesurable sur les performances, et peut même légèrement dégrader certaines métriques.  

Ce résultat suggère que :
- soit les variables ajoutées ne contiennent pas d’information suffisamment discriminante,
- soit leur caractère indirect / approximatif limite leur contribution au modèle.

Le choix final s’est donc porté sur le **dataset consolidé sans enrichissement**, afin de privilégier un pipeline plus simple et plus robuste.

### Optimisation des hyperparamètres

Le **RandomForestRegressor** a été retenu comme modèle final pour trois raisons principales :

1. Il obtient les meilleures performances globales sur le dataset consolidé.
2. Il présente une bonne stabilité en validation croisée, avec une faible variabilité entre les folds.
3. Il offre un bon niveau d’interprétabilité via les analyses de feature importance et SHAP.

Ce choix répond donc à un compromis équilibré entre **performance prédictive**, **robustesse** et **lisibilité métier**.

Une phase d’optimisation par `GridSearchCV` a été menée sur ce dernier.  

Les meilleurs hyperparamètres retenus sont les suivants (en comparaison avec la baseline):

<img width="683" height="213" alt="Image" src="https://github.com/user-attachments/assets/41e9e461-1af9-40e7-995a-243cf86e069a" />

Les gains observés après optimisation restent toutefois limités.  
Ce comportement suggère que le modèle se situe déjà proche de son optimum sur les données disponibles. En conséquence, les marges de progression futures semblent davantage liées à l’enrichissement des données qu’à une optimisation algorithmique supplémentaire.

## Interprétabilité du modèle feature importance et SHAP values

Afin de mieux comprendre les mécanismes de prédiction du modèle retenu, deux approches complémentaires d’interprétabilité ont été utilisées :
- la feature importance native du Random Forest
- les SHAP values, qui permettent d’analyser la contribution réelle de chaque variable aux prédictions.

Ces deux lectures ne mesurent pas exactement la même chose :

- la feature importance indique quelles variables sont le plus utilisées par le modèle pour réduire l’erreur lors des splits
- les SHAP values montrent dans quel sens et avec quelle intensité chaque variable fait varier une prédiction.

L’intérêt de croiser les deux approches est de distinguer :
- les variables structurellement importantes pour le modèle 
- les variables qui ont l’impact le plus fort sur les prédictions individuelles.

1. **Feature importance globale du Random Forest**

- Top 15 des variables les plus importantes :

<img width="989" height="590" alt="Image" src="https://github.com/user-attachments/assets/d002baf4-cef7-42e4-85ff-91ca443fbed0" />

La variable la plus importante est de très loin item_Potatoes, avec un poids supérieur à 31 %. Cela signifie que le fait d’être sur la culture Potatoes structure fortement les décisions du modèle. Ce résultat est cohérent avec l’analyse exploratoire, qui montrait déjà que certaines cultures, notamment les pommes de terre, présentaient des niveaux de rendement beaucoup plus élevés que les autres.

On observe ensuite un second bloc de variables très influentes :
- pesticides_tonnes
- rainfall_mm
- input_imbalance
- avg_temp
- thermal_stress
- years_from_now

Ce groupe montre que le modèle ne repose pas uniquement sur le type de culture : il intègre aussi fortement les conditions agro-climatiques, les intrants et une dimension temporelle.
Enfin, plusieurs variables de région apparaissent dans le top 15, ce qui confirme que le contexte géographique joue un rôle significatif dans l’estimation des rendements.

2. Importance par familles de variables

Pour rendre l’analyse plus lisible métier, les variables ont été regroupées en grandes familles.

<img width="790" height="390" alt="Image" src="https://github.com/user-attachments/assets/89b56b1b-4611-4934-a877-9fa4cf6600d7" />

- Le modèle s’appuie d’abord sur le type de culture, qui représente près de 49,4 % de l’importance totale. C’est le signal principal.
- Les variables climatiques et techniques représentent ensuite environ 34% de l’importance totale. Cela montre que la prédiction ne dépend pas uniquement du choix de culture, mais aussi des conditions de production : pluie, température, pression d’intrants et déséquilibres entre eau et pesticides.
- La région pèse environ 16,6 %, ce qui confirme qu’un même type de culture ne se comporte pas de la même manière selon le contexte géographique.
- Cette répartition est cohérente d’un point de vue métier :
    - la culture fixe un potentiel de rendement de base
    - le climat et les intrants modulent ce potentiel
    - la zone géographique ajoute un effet structurel supplémentaire.

3. Analyse des SHAP values

L’analyse SHAP affine cette lecture en montrant non seulement quelles variables comptent le plus, mais aussi dans quel sens elles influencent la prédiction.

**Variables les plus influentes selon SHAP**
Les variables ressortant le plus fortement en contribution moyenne absolue sont :

<img width="784" height="940" alt="Image" src="https://github.com/user-attachments/assets/6fb6d2f9-146a-4e62-9ff0-d56fb0c5f23a" />

- Les SHAP values confirment que certaines cultures déplacent fortement la prédiction :
    - item_Potatoes a l’effet positif le plus fort du modèle
    - item_Sweet potatoes, item_Cassava, item_Yams et item_Plantains and others ont également des contributions positives marquées 
    - à l’inverse, des cultures comme item_Soybean, item_Sorghum ou item_Wheat apparaissent davantage associées à des contributions négatives ou plus faibles.
    - Le modèle apprend qu’à conditions comparables, certaines cultures sont associées à des niveaux de rendement structurellement plus élevés que d’autres.

- Les SHAP values montrent aussi des effets géographiques différenciés :
    - region_Sub-Saharan Africa contribue fréquemment négativement aux prédictions
    - region_Western Europe, region_Western Asia, region_Northern Europe et region_Eastern Asia ont plutôt des contributions positives.

- Effet du climat et de l'intrant. Plusieurs variables numériques ont un rôle important :
    - pesticides_tonnes : les valeurs élevées tendent globalement à pousser la prédiction vers le haut
    - rainfall_mm : son effet est important mais dépend du contexte
    - avg_temp : la température moyenne influence bien la prédiction, mais avec une intensité plus modérée que la pluie ou les pesticides
    - thermal_stress : un stress thermique élevé a plutôt un effet négatif
    - years_from_now : les valeurs élevées de cette variable, correspondant aux années les plus anciennes, ont tendance à tirer la prédiction vers le bas, tandis que les années plus récentes contribuent davantage positivement.
        Le modèle capte une tendance dans le temps avec l’idée d’une amélioration progressive des rendements au fil du temps, possiblement liée à l’évolution des pratiques, des intrants, des techniques ou des variétés.

4. Analyse d'une prédiction avec waterfall plot

Cela part d'une prédiction moyenne du modèle sur le dataset d'entraînement, ensuite selon les contributions de certaines variables, le modèle va pousser la prédiction vers le haut ou vers le bas.

<img width="1008" height="600" alt="Image" src="https://github.com/user-attachments/assets/3ebbe111-a79a-4ec1-94f1-14e7e53d9086" />

Dans ce cas précis on voit qu'une large partie de la contribution positive du model vient de la catégorie plantains and others et dans une moindre mesure la variable des pesticides. Les autres variables vont pousser la prédiction vers le bas.

## Perspectives

Les résultats pour la fonction de prédiction et de recommandation sont cohérents par rapport au dataset utilisé, c'est à dire un fichier déséquilibré par type de culture. Actuellement nous sommes capable de donner un rendement par une culture spécifique mais également de propsoer un classement des rendements les plus profitables à partir des conditions climatiques et de la région.

Pour aller plus loin nous aurons besoin de pouvoir enrichir nos données de manière plus précise. Actuellement le dataset enrichi n'est pas utilisé car les variables rajoutées n'apportent rien au modèle. Nous avons donc besoin :

- d'éléments similaires à crop_yield mais non synthétique où il serait possible de rapprocher ces informations par région ou pays.
- avoir des éléments supplémentaires sur les parcelles 
- d'aller plus loin dans les fonctions de prédiction et de proposer un CA potentiel / ajout d'un prix de vente par pays/région