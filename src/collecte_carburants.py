# C6.1 — Configuration du pipeline OptiFleet Logistics
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timezone
from shapely.geometry import shape, Point
from zoneinfo import ZoneInfo
import requests

# 1. Racine du projet
RACINE = Path(__file__).resolve().parent.parent

# 2. Adresse de l'API carburants
URL_CARBURANTS = (
    "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "prix-des-carburants-en-france-flux-instantane-v2/records"
)

# 3. Paramètres de collecte
FILTRE_COLLECTE = 'code_departement="69"'
TAILLE_PAGE = 100
print("Configuration du pipeline chargée.")

# C6.2 — Collecter les stations depuis l'API

# C6.2.2 — Collecter toutes les stations avec pagination

def collecter_stations():

    stations = []
    offset = 0
    total_annonce = None

    while True:

        params = {
            "where": FILTRE_COLLECTE,
            "order_by": "id ASC",
            "limit": TAILLE_PAGE,
            "offset": offset
        }

        reponse = requests.get(
            URL_CARBURANTS,
            params=params,
            timeout=30
        )

        reponse.raise_for_status()
        donnees = reponse.json()

        if total_annonce is None:
            total_annonce = donnees["total_count"]

        page = donnees["results"]
        stations.extend(page)

        print(f"Page récupérée : {len(page)} stations")

        if not page or len(stations) >= total_annonce:
            break

        offset += TAILLE_PAGE

    return stations, total_annonce

# C6.3 — Sauvegarder les données brutes au format JSON

def sauvegarder_json(stations, horodatage, total):

    # 1. Construire le chemin du dossier raw
    dossier_raw = Path(__file__).resolve().parent.parent / "data" / "raw"

    # 2. Créer le dossier s'il n'existe pas
    dossier_raw.mkdir(parents=True, exist_ok=True)

    # 3. Récupérer la date du jour en UTC
    date_collecte = horodatage.astimezone(
    ZoneInfo("Europe/Paris")
).strftime("%Y-%m-%d_%H%M%S_%f")

    # 4. Construire le nom du fichier
    chemin_fichier = dossier_raw / f"stations_rhone_{date_collecte}.json"

    contenu_raw = {
    "horodatage_collecte": horodatage.isoformat(),
    "filtre": FILTRE_COLLECTE,
    "total_count": total,
    "nombre_collecte": len(stations),
    "results": stations
}
    # 5. Enregistrer les stations
    with open(chemin_fichier, "w", encoding="utf-8") as fichier:
        json.dump(
            contenu_raw,
            fichier,
            ensure_ascii=False,
            indent=2
        )

    # 6. Confirmer la sauvegarde
    print(f"Fichier JSON enregistré : {chemin_fichier}")

    return chemin_fichier
# C6.4 — Transformer les stations en DataFrame Pandas

def creer_dataframe(stations):

    # Convertir les données JSON en tableau Pandas
    df = pd.DataFrame(stations)

    # Vérifier les dimensions
    print("Dimensions du DataFrame :", df.shape)

    # Afficher les cinq premières lignes
    print(df.head())

    return df


# C6.5 — Sélectionner les colonnes utiles

def selectionner_colonnes(df):

    colonnes_utiles = [
        "id",
        "adresse",
        "ville",
        "cp",
        "geom",
        "gazole_prix",
        "gazole_maj",
        "code_departement",
        "pop"
    ]

    df_selection = df[colonnes_utiles].copy()

    print("Dimensions après sélection :", df_selection.shape)

    return df_selection


# C6.6 — Nettoyer les données

def nettoyer_donnees(df):

    # 1. Travailler sur une copie
    df_propre = df.copy()

    # 2. Convertir le prix du Gazole en nombre
    df_propre["gazole_prix"] = pd.to_numeric(
        df_propre["gazole_prix"],
        errors="coerce"
    )

    # 3. Convertir la date de mise à jour
    df_propre["gazole_maj"] = pd.to_datetime(
        df_propre["gazole_maj"],
        errors="coerce",
        utc=True
    )

    # 4. Identifier les prix exploitables sans supprimer les stations
    
    df_propre["prix_valide"] = (
    df_propre["gazole_prix"].notna()
    & df_propre["gazole_prix"].between(0.50, 4.00)
)

    # 5. Afficher le bilan
    print("Stations analysées :", len(df_propre))
    print("Prix valides :", df_propre["prix_valide"].sum())
    print("Prix non valides :", (~df_propre["prix_valide"]).sum())

    return df_propre

# C6.7 — Extraire les coordonnées GPS

def extraire_coordonnees(df):

    df_geo = df.copy()

    # Récupérer les coordonnées depuis geom
    df_geo["latitude"] = df_geo["geom"].apply(
        lambda geo: geo.get("lat") if isinstance(geo, dict) else None
    )

    df_geo["longitude"] = df_geo["geom"].apply(
        lambda geo: geo.get("lon") if isinstance(geo, dict) else None
    )

    # Écarter les coordonnées manquantes
    df_geo = df_geo.dropna(subset=["latitude", "longitude"])

    return df_geo

def charger_contours():
    chemin_geojson = RACINE / "data" / "raw" / "communes_metropole_lyon.geojson"

    if chemin_geojson.exists():
        # Lire le GeoJSON existant
        with open(chemin_geojson, "r", encoding="utf-8") as fichier:
            donnees = json.load(fichier)

    else:
    # 1. Adresse de l'API Géo
     url = "https://geo.api.gouv.fr/epcis/200046977/communes"

    # 2. Paramètres pour récupérer les contours
     params = {
        "fields": "nom,code,contour",
        "format": "geojson",
        "geometry": "contour"
     }

    # 3. Appel de l'API
     reponse = requests.get(url, params=params, timeout=30)
     reponse.raise_for_status()

    # 4. Conversion de la réponse en données Python
     donnees = reponse.json()

    # 5. Sauvegarde locale du GeoJSON
     chemin_geojson.parent.mkdir(parents=True, exist_ok=True)

     with open(chemin_geojson, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=2)

     print("Contours téléchargés depuis l'API Géo.")

    # Vérifier les 58 communes attendues
    assert len(donnees["features"]) == 58, "Nombre de communes inattendu"

    # Convertir les géométries en objets Shapely
    polygones = [
    (
        feature["properties"]["code"],
        feature["properties"]["nom"],
        shape(feature["geometry"])
    )
    for feature in donnees["features"]
]

    return polygones

# C6.8 — Filtrer les stations de la Métropole de Lyon

def filtrer_metropole(df, polygones):



    # 4. Retrouver la commune contenant chaque station
    def trouver_commune(ligne):

        point = Point(ligne["longitude"], ligne["latitude"])

        for code, nom, polygone in polygones:
            if polygone.covers(point):
                return code, nom

        return None, None

    # 5. Appliquer la recherche aux stations
    df_geo = df.copy()

    resultats = df_geo.apply(trouver_commune, axis=1)

    df_geo["code_insee_geo"] = resultats.str[0]
    df_geo["commune_geo"] = resultats.str[1]

    # 6. Conserver les stations situées dans la Métropole
    df_metropole = df_geo.loc[
        df_geo["code_insee_geo"].notna()
    ].copy()

    # 7. Afficher le bilan
    print("Stations avec GPS :", len(df_geo))
    print("Stations dans la Métropole :", len(df_metropole))
    print("Stations hors Métropole :", len(df_geo) - len(df_metropole))

    return df_metropole

# C6.9 — Sauvegarder les stations de la Métropole en CSV
def sauvegarder_csv(df_metropole, date_collecte):
    dossier = RACINE / "data" / "processed"
    dossier.mkdir(parents=True, exist_ok=True)


    df_export = df_metropole.copy()
    df_export["date_collecte"] = date_collecte

    chemin = dossier / f"stations_metropole_{date_collecte}.csv"

    df_export.to_csv(chemin, index=False, encoding="utf-8")

    print(f"CSV enregistré : {chemin}")
    print(f"Stations exportées : {len(df_export)}")

# C6.11 — Préparer les données pour BigQuery

def transformer(df_metropole, horodatage, date_collecte):

    df = df_metropole.copy()

    # 1. Traçabilité de la collecte
    df["horodatage_collecte"] = horodatage.isoformat()

    # 2. Identifier le carburant
    df["carburant"] = "Gazole"

    # 3. Calculer l'âge du prix en heures
    df["age_prix_heures"] = (
        horodatage - df["gazole_maj"]
    ).dt.total_seconds() / 3600

    # 4. Identifier les prix récents et exploitables
    df["prix_recent_48h"] = (
        df["prix_valide"]
        & df["age_prix_heures"].ge(0)
        & df["age_prix_heures"].lt(48)
    )

    # 5. Détecter les prix atypiques avec l'IQR
    prix_valides = df.loc[df["prix_valide"], "gazole_prix"]

    q1 = prix_valides.quantile(0.25)
    q3 = prix_valides.quantile(0.75)
    iqr = q3 - q1

    borne_inf = q1 - 1.5 * iqr
    borne_sup = q3 + 1.5 * iqr

    df["prix_atypique_iqr"] = (
        df["prix_valide"]
        & ~df["gazole_prix"].between(borne_inf, borne_sup)
    )

    # 6. Créer une clé unique par station, carburant et journée
    df["cle_observation"] = (
        df["id"].astype(str)
        + "_"
        + df["carburant"]
        + "_"
        + str(date_collecte)
    )

    # 7. Retirer l'objet géographique brut
    df = df.drop(columns=["geom"], errors="ignore")

    return df

# C6.10 — Contrôles qualité avant export
def controler(df_final, total_annonce, nb_collectees):

    # 1. Vérifier que la collecte API est complète
    assert nb_collectees == total_annonce, (
        "Collecte API incomplète"
    )

    # 2. Vérifier l'absence de doublons
    assert df_final["cle_observation"].is_unique, (
        "Doublons détectés"
    )

    # 3. Vérifier le nombre de stations de la Métropole
    assert 80 <= len(df_final) <= 150, (
        "Nombre de stations inhabituel"
    )

    # 4. Vérifier qu'il existe des prix exploitables
    assert df_final["prix_valide"].sum() > 0, (
        "Aucun prix Gazole valide"
    )

    print("Contrôles qualité OK")

    # Vérifier que toutes les stations annoncées ont été récupérées
    assert nb_collectees == total_annonce, (
        "Collecte incomplète : le nombre de stations ne correspond pas à l'API"
    )

    print("Contrôle 1 OK : collecte API complète")

        # Contrôle 2 — Vérifier l'absence de doublons
    assert df_final["cle_observation"].is_unique, (
        "Doublons détectés dans la colonne cle_observation"
    )

    print("Contrôle 2 OK : aucune observation en double")
        # Contrôle 3 — Vérifier le nombre de stations de la Métropole
    assert 80 <= len(df_final) <= 150, (
        f"Nombre de stations inhabituel : {len(df_final)}"
    )

    print(f"Contrôle 3 OK : {len(df_final)} stations dans la Métropole")

# C6 — Fonction principale du pipeline
def main():


    # Instant unique de la collecte
    horodatage = datetime.now(timezone.utc)

    # Date métier selon le fuseau horaire de Lyon
    date_collecte = horodatage.astimezone(
        ZoneInfo("Europe/Paris")
    ).date()

    
    # 1. Collecte API
    stations, total = collecter_stations()

    print("Stations récupérées :", len(stations))
    print("Total annoncé par l'API :", total)

    # 2. Sauvegarde JSON
    sauvegarder_json(stations, horodatage, total)

    # 3. Création du DataFrame
    df = creer_dataframe(stations)

    # 4. Sélection des colonnes
    df_selection = selectionner_colonnes(df)

    # 5. Nettoyage
    df_propre = nettoyer_donnees(df_selection)

    # 6. Extraction des coordonnées GPS
    df_geo = extraire_coordonnees(df_propre)

    # 7. Charger les contours de la Métropole (fichier local ou API)
    polygones = charger_contours()

# 8. Filtrer les stations situées dans la Métropole
    df_metropole = filtrer_metropole(df_geo, polygones)

    # 9. Préparation des indicateurs BigQuery
    df_final = transformer(df_metropole, horodatage, date_collecte)

    # Contrôle qualité avant sauvegarde
    controler(df_final, total, len(stations))

    # 10. Sauvegarde CSV
    sauvegarder_csv(df_final, date_collecte)

# Exécuter le pipeline uniquement si ce fichier est lancé directement
if __name__ == "__main__":
    main()