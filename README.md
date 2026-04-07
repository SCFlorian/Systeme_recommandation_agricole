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
3. [Analyse exploratoire des fichiers sources](#analyse-exploratoire-des-fichiers-sources)
4. [Enrichissement du fichier consolidé](#enrichissement-du-fichier-consolidé)
5. [Feature engineering sur le fichier enrichi](#feature-engineering-sur-le-fichier-enrichi)
6. [Feature engineering sur le fichier consolidé](#feature-engineering-sur-le-fichier-consolidé)

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
├── notebooks/                                 # Notebook & dossier graph
│   ├──notebook_analyse_exploratoire.ipynb
│   ├──notebook_feature_engineering.ipynb
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

![alt text](notebooks/graph/distribution_variable_cible.png)

Notre distribution ressemble à une cloche, donc à une distribution normale même si on ne peut pas la considérer comme telle car on voit quelques petits dépassements.


#### Nettoyage

- Boxplot pour analyser le type de culture par rapport au rendement.

![alt text](notebooks/graph/boxplot_crop_yield.png)

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

![alt text](notebooks/graph/cercle_correlation.png)

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

La présence de valeur extrême est expliqué par un gros écart entre les gros utilisateurs de pesticide et les petits utilisateurs.
**Le top 5 des plus gros utilisateurs de pesticide représente 66% de la valeur globale.**

On a analysé les pays en "écart", rien ne semble anormal, ce sont des pays qui peuvent être des gros utilisateurs.

**Évolution de l'utilisation des pesticides dans le temps**

![alt text](notebooks/graph/histo_pesticide.png)

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

![alt text](notebooks/graph/distribution_variable_cible_fichier_yield.png)

On voit un étalement vers la gauche. Les données se suivent pas une distribution quasi normale comme le premier dataset. Le fichier est plus déséquilibré.

**Boxplot par type de culture et rendement :**

![alt text](notebooks/graph/boxplot_yield.png)

- On peut voir quelques valeurs à 0. Difficile de savoir si on les supprime ou non car théoriquement un rendement à 0 c'est possible si les conditions ne sont pas réunies pour une production.
- On voit une valeur énorme pour Plaintains and more
    - La valeur extrême date de 1964, nous irons pas dans des dates aussi antérieures donc on l'enlevera par défaut par la suite.
- On voit un fort déséquilibre entre les types de culture. On peut noter que la catégorie Potatoes semble avoir avoir des rendements plus élevés que les autres. Ce sont des valeurs extrêmes mais pas aberrantes car elles sont réelles alors nous devons les laisser. 

### Fichier yield_df.csv

On retouve dans ce fichier un dataset déjà consolidé entre yield et les 3 fichiers concernant les conditions météos.

Après analyse du fichier :
- Difficulté de savoir comment a été traité le fichier
- Pas de valeurs manquantes
- Doublons trouvés sur les températures notamment.

Pour une meilleure analyse, nous allons consolider un nouveau fichier yield_df car nous ne savons pas comment ce fichier a été construit.

### Nouveau fichier consolidé :

Avant de pouvoir étudier correctement les relations entre les différentes conditions météoroliques, nous devons consolider les fichiers suivants :
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
- Passage à 7 colonnes et 29 151 lignes avec des valeurs manquantes pour les conditions climatiques. Valeurs manquantes
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
area	    year	item	avg_temp  rainfall_mm	pesticides_tonnes	yield
Afghanistan	1990	Maize	15.450	  327.0	        1594.50	            7582
Afghanistan	1991	Maize	14.570	  327.0	        1594.50	            16800
Afghanistan	1992	Maize	14.350	  327.0	        1594.50	            15000
Afghanistan	1993	Maize	14.960	  327.0	        1594.50	            16786
Afghanistan	1994	Maize	14.940	  327.0	        1594.50	            16667
```

Cet exemple est pertinent :

- On voit des données de température différente par année pour un même pays : les données étaient ainsi dans le fichier temp
- Pour rainfall les données de base sont répetées par année
- Pour ce pays en particulier il n'y avait pas d'informations pour les pesticides, ces données ont été imputé
- On observe bien un rendmeent différent par année pour un même pays

**Matrice corrélation**

![alt text](notebooks/graph/matrice_correlation_spearman.png)

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

- regroupement des pays : regroupement par grande catégorie pour garder une certaine cohérence
- tech_trend : capte la croissance historique des rendements liée aux innovations technologiques au fil des ans.
- irrigation_impact : mesure l'importance vitale de l'apport d'eau artificiel, particulièrement élevée lorsque les précipitations naturelles sont insuffisantes.
- pest_rain_ratio : évalue l'efficacité potentielle des traitements chimiques en tenant compte du risque de lessivage par les fortes pluies.
- climate_instability : identifie les régions à risque en mesurant la variabilité.
- relative_tech_intensity : indique si l'effort technologique d'une année spécifique est supérieur ou inférieur à la norme historique du pays concerné.

**Matrice de corrélation**

![alt text](notebooks/graph/matrice_correlation_spearman_conso.png)

Pas relation forte entre nos variables mais on voit que l'ajout des nouvelles variables ne sont pas redondantes avec les features d'origine.

### Encodage des variables catégorielles

Un modèle de machine learning ne peut pas comprendre les valeurs non numériques alors nous devons transformer nos variables catégorielles, quitte à avoir des colonnes supplémentaires.

- **Passage des colonnes catégorielles avec One Hot.**

## Feature engineering sur le fichier consolidé

Afin de s'assurer de la pertinence de l'enrichissement de nos données, on va devoir comparer la modélisation entre le fichier enrichi et le fichier consolidé sans enrichissement.

Pour réaliser cela, nous devons effectuer le même feature engineering.

Nous avons désormais consolidé notre dataset :
- Une première fois avec 3 variables climatiques puis imputer de manière rigoureuse pour les données manquantes.
- Une deuxième fois en enrichissant le dataset avec des variables approximatives qui devraient aider notre modèle à mieux généraliser

Nous devons maintenant continuer l'amélioration de nos données en ajoutant des données si possibles,et en transformant nos données pour être compréhensible pour un modèle.

**Nouvelles variables**

- regroupement des pays : regroupement par grande catégorie pour garder une certaine cohérence
- tech_trend : capte la croissance historique des rendements liée aux innovations technologiques au fil des ans.
- pest_rain_ratio : évalue l'efficacité potentielle des traitements chimiques en tenant compte du risque de lessivage par les fortes pluies.
- climate_instability : identifie les régions à risque en mesurant la variabilité.
- relative_tech_intensity : indique si l'effort technologique d'une année spécifique est supérieur ou inférieur à la norme historique du pays concerné.

Sans avoir enrichi notre fichier, on ne peut pas ajouter la variable irrigation_impact qui dépend de Irrigation_Used.

### Encodage des variables catégorielles

Un modèle de machine learning ne peut pas comprendre les valeurs non numériques alors nous devons transformer nos variables catégorielles, quitte à avoir des colonnes supplémentaires.

- **Passage des colonnes catégorielles avec One Hot.**

## Comparaison du fichier avec et sans enrichissement sur plusieurs modèles

Afin de voir si les variables rajoutées du fichier synthétique vers le fichier principal ont du sens, on va comparer sur ces 2 fichiers plusieurs modèles de machine learning.

```
dataset	           model	        n_rows	n_features	cv_rmse_mean  cv_rmse_std	cv_mae_mean	cv_mae_std	cv_r2_mean	cv_r2_std	test_rmse	test_mae	test_r2
Fichier enrichi	   DummyRegressor   29151	38	        75652.6639	  1271.5658	    55591.4405	612.0935	-0.0007	    0.0003	    73864.1004	54567.1261	-0.0012
Fichier consolidé  DummyRegressor   29151	24	        75652.6639	  1271.5658	    55591.4405	612.0935	-0.0007	    0.0003	    73864.1004	54567.1261	-0.0012
Fichier enrichi	   LightGBM	        29151	38	        28195.1980	  830.2414	    17920.1400	314.8971	0.8609	    0.0064	    27703.8593	17454.4365	0.8592
Fichier consolidé  LightGBM	        29151	24	        27954.8256	  876.4924	    17768.2938	310.4446	0.8633	    0.0071	    27956.1463	17625.7264	0.8566
Fichier enrichi	   LinearRegression	29151	38	        51310.2734	  1258.0180	    33432.7746	650.7589	0.5397	    0.0096	    50982.7735	33071.1113	0.5230
Fichier consolidé  LinearRegression	29151	24	        51341.9533	  1271.3610	    33444.5241	675.6013	0.5392	    0.0096	    51047.0116	33133.5267	0.5218
Fichier enrichi	   RandomForest	    29151	38	        20799.5607	  772.1689	    10226.1873	294.6239	0.9243	    0.0051	    19681.5670	9289.9715	0.9289
Fichier consolidé  RandomForest	    29151	24	        20383.3497	  855.5534	    9515.7169	295.8420	0.9272	    0.0056	    19686.6864	8720.9609	0.9289
Fichier consolidé  XGBoost	        29151	24	        22671.0428	  684.7109	    13549.7758	299.5553	0.9101	    0.0046	    22180.2492	12803.4932	0.9097
Fichier enrichi	   XGBoost	        29151	38	        23464.4425	  536.1863	    14145.8625	277.0853	0.9037	    0.0033	    22706.2423	13230.0410	0.9054
```

- Sur ces premiers tests on ne voit pas des meilleurs résultats pour le fichier enrichi, les informations rajoutées ne semblent pas apporter quelque chose d'utile pour nos modèles.
- On voit que le modèle de RandomForest a des meilleurs résulats (sans optimisation des meilleurs paramètres) mais suivi de très près par XGBoost et LightGBM.
- N'ayant pas une distribution linéaire, on voit que la regression linéraire ne généralise pas.