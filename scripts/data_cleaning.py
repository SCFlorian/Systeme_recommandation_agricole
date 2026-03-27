# =======================
# Nettoyage des fichiers
# =======================

# Imports
import pandas as pd
import sys, os
import logging
# Chemin pour accèder aux éléments du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Imports du projet
from scripts.config import (csv_file_crop_yield, csv_yield_conso, csv_file_crop_yield_clean, csv_mapping_countries,
                            csv_pesticides, csv_rainfall, csv_temp, csv_yield)
# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fonction de nettoyage du fichier crop_yield
def cleaning_crop_yield():
    """Sur le fichier crop_yield, le problème principal est les valeurs extrêmes.
    On a identifié 231 valeurs négatives sur la variable cible"""
    # On charge le fichier
    df = pd.read_csv(csv_file_crop_yield)
    logging.info(f"Nombre de lignes et de colonnes sans modifs : {df.shape}\n")
    # On ne retient pas les éléments en dessous de 0
    df = df[df['Yield_tons_per_hectare']>=0]
    logging.info(f"Nombre de lignes et de colonnes sans modifs : {df.shape}\n")

    return df

# Fonction d'harmonisation du nom des pays

def harmonization_countries():
    """ Fonction pour harmoniser le nom des pays par fichier"""
    try :
        data_pesticides = pd.read_csv(csv_pesticides)
        data_rainfall = pd.read_csv(csv_rainfall)
        data_temp = pd.read_csv(csv_temp)
        data_yield = pd.read_csv(csv_yield)
        mapping_countries = pd.read_csv(csv_mapping_countries)

    except Exception as e:
        logging.error(f"Erreur critique lors du chargement des fichiers : {e}")
        raise e

    # Chargement de la liste des pays pour harmonisation dans data/processed
    mapping_df = mapping_countries
    # On met les informations dans un dictionnaire afin de pouvoir les mapper
    mapping_dict = dict(zip(mapping_df['Original Name'], mapping_df['Standard Name']))
    # Identification d'une erreur supplémentaire
    mapping_dict.update({"Bosnia And Herzegovina": "Bosnia and Herzegovina"})

    # Mapping des fichiers
    # Fichier yield
    data_yield_map = data_yield
    data_yield_map['Area'] = data_yield_map['Area'].map(mapping_dict).fillna(data_yield_map['Area'])
    # Fichier rainfall
    data_rainfall_map = data_rainfall
    data_rainfall_map[' Area'] = data_rainfall_map[' Area'].map(mapping_dict).fillna(data_rainfall_map[' Area'])
    # Fichier pesticide
    data_pesticides_map = data_pesticides
    data_pesticides_map['Area'] = data_pesticides_map['Area'].map(mapping_dict).fillna(data_pesticides_map['Area'])
    # Fichier temp
    data_temp_map = data_temp
    data_temp_map['country'] = data_temp_map['country'].map(mapping_dict).fillna(data_temp_map['country'])

    logging.info("Nom standardisé des pays par fichier")

    return data_yield_map, data_rainfall_map, data_pesticides_map, data_temp_map

def cleaning_files(data_yield_map, data_pesticides_map, data_rainfall_map, data_temp_map):
    """"Fonction de nettoyage de chaque fichier avant fusion dans un fichier consolidé"""
    # Fichier yield
    # Restriction à la période commune 1990-2016
    data_yield_map = data_yield_map[data_yield_map["Year"].between(1990, 2016)].copy()
    # On garde les colonnes utiles
    # On enlève notamment Domain Code / Area Code / Element Code / Item Code / Unit
    data_yield_map = data_yield_map[["Area", "Item", "Year", "Value"]].copy()

    # On renomme correctement le nom de la variable cible
    data_yield_map = data_yield_map.rename(columns={"Area":"area",
                                                    "Item":"item",
                                                    "Year":"year",
                                                    "Value":"yield"}).copy()
    # On supprime les derniers doublons
    data_yield_map = data_yield_map.drop_duplicates(subset=["area", "item", "year"]).copy()
    logging.info(
        "Doublons sur (Area, Item, Year) dans yield : %s",
        data_yield_map.duplicated(["area", "item", "year"]).sum()
    )
    logging.info(
        "Valeurs manquantes dans yield : %s",
        data_yield_map.isnull().mean()
)

    # Fichier pesticides
    # Restriction à la période commune 1990-2016
    data_pesticides_map = data_pesticides_map[data_pesticides_map["Year"].between(1990, 2016)].copy()
    # On garde les colonnes utiles
    # On enlève notamment Domain Code / Area Code / Element Code / Item Code / Unit
    data_pesticides_map = data_pesticides_map[["Area", "Year", "Value"]].copy()
    # On renomme correctement le nom de la variable cible
    data_pesticides_map = data_pesticides_map.rename(columns={"Area":"area",
                                                            "Year":"year",
                                                            "Value":"pesticides_tonnes"}).copy()
    # Vérification des doublons métier
   
    logging.info(
    "Doublons sur (Area, Year) dans pesticides : %s",
    data_pesticides_map.duplicated(["area", "year"]).sum()
    )
    logging.info(
        "Valeurs manquantes dans pesticides : %s",
        data_pesticides_map.isnull().mean()
    )

    # Fichier rainfall
    # Restriction à la période commune 1990-2016
    data_rainfall_map = data_rainfall_map[data_rainfall_map["Year"].between(1990, 2016)].copy()
    # On renomme correctement 2 variables
    data_rainfall_map = data_rainfall_map.rename(columns={" Area": "area",
                                                        "Year":"year",
                                                        "average_rain_fall_mm_per_year": "rainfall_mm"}).copy()
    # Conversion numérique en forçant malgrés les NaN
    data_rainfall_map["rainfall_mm"] = pd.to_numeric(data_rainfall_map["rainfall_mm"],errors="coerce")
    # Vérification des doublons métier
    logging.info(
        "Doublons sur (Area, Year) dans rainfall : %s",
        data_rainfall_map.duplicated(["area", "year"]).sum()
    )
    logging.info(
        "Valeurs manquantes dans rainfall : %s",
        data_rainfall_map.isnull().mean()
    )

    # Fichier temp
    # Restriction à la période commune 1990-2016
    data_temp_map = data_temp_map[data_temp_map["year"].between(1990, 2016)].copy()
    # On renomme correctement 2 variables
    data_temp_map = data_temp_map.rename(columns={"country": "area"}).copy()
    # Agrégation propre au couple Area-Year
    # Imputation par la moyenne pour les années manquantes par pays / Imputation logique ici avant imputation globale
    data_temp_map = (
        data_temp_map
        .groupby(["area", "year"], as_index=False)["avg_temp"]
        .median()
    ).copy()
    # Vérification des doublons métier
    logging.info(
        "Doublons sur (Area, Year) dans temp : %s",
        data_temp_map.duplicated(["area", "year"]).sum()
    )
    logging.info(
        "Valeurs manquantes dans temp : %s",
        data_temp_map.isnull().mean()
    )
    data_temp_map.head()

    return data_yield_map, data_pesticides_map, data_rainfall_map, data_temp_map

data_yield_map, data_rainfall_map, data_pesticides_map, data_temp_map = harmonization_countries()
data_yield_map, data_pesticides_map, data_rainfall_map, data_temp_map = cleaning_files(data_yield_map, data_pesticides_map, data_rainfall_map, data_temp_map)
logging.info(data_yield_map.head())
logging.info(data_pesticides_map.head())
logging.info(data_rainfall_map.head())
logging.info(data_temp_map.head())