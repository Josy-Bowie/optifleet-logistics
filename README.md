
# 🚛 OptiFleet Logistics — Analyse des prix du gazole

## 📌 Présentation du projet

**OptiFleet Logistics** est un projet de Data Analytics visant à aider une entreprise fictive de livraison à optimiser ses dépenses en carburant dans la Métropole de Lyon.

L'entreprise dispose d'une flotte de **20 véhicules diesel** et souhaite identifier les stations-service les plus avantageuses pour réduire ses coûts d'exploitation.

Ce projet exploite les données publiques des prix des carburants en France afin de construire un pipeline de collecte, de transformation, d'analyse et de visualisation des données.

## 🎯 Problématique métier

**Où et quand les chauffeurs d'OptiFleet Logistics doivent-ils faire le plein de gazole dans la Métropole de Lyon pour réduire la facture carburant de la flotte ?**

Pour répondre à cette problématique, le projet cherche à :

- Comparer les prix du gazole entre les stations-service.
- Identifier les stations proposant les prix les plus bas.
- Vérifier la fraîcheur et la fiabilité des prix affichés.
- Analyser les différences de prix entre les communes.
- Estimer les économies potentielles pour l'entreprise.
- Faciliter la prise de décision grâce à un tableau de bord interactif.



## 🚚 Hypothèses de fonctionnement de la flotte

Pour estimer les économies potentielles, nous retenons les hypothèses suivantes :

| Paramètre | Hypothèse |
|---|---:|
| Nombre de véhicules | 20 |
| Carburant utilisé | Gazole |
| Capacité de référence par plein | 60 litres |
| Nombre de pleins par véhicule | 2 par semaine |
| Consommation hebdomadaire estimée | 2 400 litres |
| Consommation annuelle estimée | 124 800 litres |

### Exemple de simulation d'économies

Une économie de **0,05 € par litre** représenterait :

- **120 € par semaine**
- **520 € par mois en moyenne**
- **6 240 € par an**

Ces résultats sont des estimations théoriques basées sur les hypothèses de consommation. Ils ne correspondent pas à des économies réellement constatées.



## 🏗️ Architecture du projet

Le projet suit un processus de traitement des données, depuis leur collecte jusqu'à leur restitution.

```text
API Open Data — Prix des carburants
                |
                v
      Python + Requests
        Collecte API
                |
                v
       Pandas + Shapely
   Nettoyage et géolocalisation
                |
                v
       Fichiers JSON / CSV
       Stockage intermédiaire
                |
                v
        Google BigQuery
      Analyses et vues SQL
                |
                v
          Looker Studio
    Dashboard d'aide à la décision
```

### Technologies utilisées

| Technologie | Utilisation |
|---|---|
| Python | Automatisation de la collecte |
| Requests | Communication avec l'API REST |
| Pandas | Nettoyage et transformation des données |
| Shapely | Filtrage géographique de la Métropole de Lyon |
| JSON / CSV | Stockage intermédiaire |
| Google BigQuery | Stockage analytique et requêtes SQL |
| Looker Studio | Visualisation et tableau de bord |
| Git / GitHub | Versionnage et documentation |



## 🔄 Méthodologie de traitement des données

### 1. Collecte des données via une API REST

Les données proviennent du jeu de données public :

[Prix des carburants en France — Flux instantané](https://data.economie.gouv.fr/explore/dataset/prix-des-carburants-en-france-flux-instantane-v2/)

Le script Python `src/collecte_carburants.py` utilise la bibliothèque `requests` pour interroger l'API.

**Périmètre initial :**
- Département du Rhône (`code_departement = "69"`).
- Récupération des stations-service par pagination.
- Conservation d'une copie des réponses au format JSON.

Les fichiers bruts sont enregistrés dans `data/raw/`.

### 2. Nettoyage et transformation avec Pandas

Les données récupérées sont transformées en DataFrame Pandas.

Les principales opérations sont :

- Sélection des colonnes utiles à l'analyse.
- Conversion des prix en valeurs numériques.
- Identification des prix valides et non valides.
- Transformation des coordonnées géographiques.
- Traitement des dates de mise à jour des prix.
- Calcul de l'ancienneté des prix en heures.
- Identification des prix actualisés depuis moins de 48 heures.
- Repérage des prix atypiques à l'aide de la méthode IQR.

### 3. Filtrage géographique avec Shapely

Le département du Rhône est plus large que la Métropole de Lyon.

Le pipeline utilise les contours géographiques des 58 communes de la Métropole et la bibliothèque `Shapely` pour identifier les stations situées dans le périmètre d'étude.

En cas d'absence du fichier géographique local, le script prévoit un téléchargement depuis l'API Géo.

### 4. Contrôles qualité des données

Avant l'export, plusieurs vérifications sont effectuées :

| Contrôle | Objectif |
|---|---|
| Complétude de la collecte | Vérifier que toutes les pages API ont été récupérées |
| Validité des prix | Identifier les prix absents ou non conformes |
| Coordonnées GPS | Vérifier la présence de coordonnées exploitables |
| Périmètre géographique | Exclure les stations hors Métropole de Lyon |
| Doublons | Éviter les observations répétées |
| Fraîcheur des prix | Identifier les tarifs mis à jour depuis moins de 48 heures |
| Valeurs atypiques | Repérer les prix nécessitant une vérification |

Une clé d'observation est utilisée pour identifier chaque enregistrement de manière cohérente.

### 5. Export des données préparées

À la fin du traitement, le pipeline produit :

- Un fichier JSON brut dans `data/raw/`.
- Un fichier CSV nettoyé dans `data/processed/`.

Exemple de fichier :

`stations_metropole_2026-10-18.csv`

Les fichiers de données sont exclus du dépôt GitHub grâce au `.gitignore`.

Le CSV préparé est ensuite utilisé pour alimenter Google BigQuery.



### Exemple de résultat — Collecte du 18 octobre 2026

| Indicateur | Résultat |
|---|---:|
| Stations récupérées dans le Rhône | 200 |
| Prix valides dans le Rhône | 184 |
| Prix non valides dans le Rhône | 16 |
| Stations situées dans la Métropole | 111 |
| Stations hors Métropole | 89 |
| Stations exportées | 111 |

**Résultat des vérifications :**
- Collecte API complète.
- Aucune observation en double selon le contrôle du pipeline.
- Filtrage géographique effectué.
- Export CSV généré avec succès.

Ces chiffres correspondent à une exécution datée et peuvent évoluer lors des prochaines collectes.


## 📊 Analyse des données avec Google BigQuery

Les données préparées par Python sont importées dans Google BigQuery afin de réaliser des analyses SQL.

### Organisation des données

- **Projet Google Cloud :** `optifleet-logistics2026`
- **Dataset :** `optifleet`
- **Table principale :** `prix_gazole_historique`
- **Localisation des données :** `EU`

### Vues SQL utilisées

| Vue | Objectif |
|---|---|
| `v_prix_gazole` | Analyser les prix du gazole |
| `v_kpi_quotidien` | Produire les indicateurs quotidiens |
| `v_stations_recommandees` | Identifier les stations répondant aux critères métier |
| `v_top10_stations` | Afficher les 10 stations recommandées |

### Indicateurs clés de performance (KPI)

Les analyses portent notamment sur :

1. **Prix médian du gazole** : prix central de la distribution.
2. **Prix bas (P10)** : seuil correspondant au 10e percentile.
3. **Écart à la médiane** : différence entre le prix d'une station et le prix médian.
4. **Top 10 des stations** : stations recommandées selon les critères de sélection.
5. **Prix médian par commune** : comparaison géographique des tarifs.
6. **Fraîcheur des prix** : identification des tarifs mis à jour depuis moins de 48 heures.
7. **Économies potentielles** : estimation des gains selon la consommation de la flotte.

### Exemple : interprétation d'un écart à la médiane

Une station proposant du gazole à 2,250 €/L,
avec une médiane de référence de 2,369 €/L,
présente un écart de :

`2,250 - 2,369 = -0,119 €/L`

Un écart négatif indique que la station propose un prix inférieur à la médiane de référence.

**Attention :** un prix avantageux ne garantit pas à lui seul une économie réelle. La distance, les détours et les frais de déplacement doivent également être considérés.


## 📈 Dashboard interactif — Looker Studio

Le tableau de bord OptiFleet Logistics permet de visualiser les prix du gazole dans la Métropole de Lyon et d'identifier les stations-service les plus intéressantes pour l'entreprise.

### 🔗 Consulter le dashboard

[👉 Accéder au tableau de bord OptiFleet Logistics](https://datastudio.google.com/reporting/7d90a7d3-9d8b-43ca-878e-5f69e0f907bd)

### Organisation du dashboard

Le rapport est organisé en trois pages complémentaires.

#### Page 1 — Vue d'ensemble

Cette page présente les principaux indicateurs de suivi des prix du gazole et une synthèse de la situation.

**Objectif :** comprendre rapidement les niveaux de prix et les opportunités d'économies.

#### Page 2 — Analyse des prix

Cette page permet d'approfondir l'analyse des prix, de comparer les indicateurs et d'explorer les différences observées.

**Objectif :** expliquer les variations de prix et appuyer les décisions métier.

#### Page 3 — Où faire le plein ?

Cette page présente :

- Une carte géographique des stations-service.
- Les stations proposant des prix récents et valides.
- Le Top 10 des stations recommandées.
- Le prix médian du gazole par commune.
- Une analyse des stations les plus chères.

**Objectif :** aider les chauffeurs et les responsables de flotte à identifier les stations les plus intéressantes.

### Limites de l'analyse

Les recommandations sont fondées sur les prix disponibles au moment des collectes.

Les économies présentées sont des estimations. Elles ne tiennent pas automatiquement compte des détours, du trafic ou du coût supplémentaire de déplacement.



## 💻 Installation et exécution du projet

### Prérequis

Pour exécuter le pipeline localement, vous devez disposer de :

- Python 3
- Git
- Un terminal (Git Bash, PowerShell ou équivalent)
- Un accès Internet pour interroger l'API

### 1. Cloner le dépôt GitHub

Ouvrir un terminal, puis exécuter :

```bash
git clone https://github.com/Josy-Bowie/optifleet-logistics.git
```

Se placer dans le dossier du projet :

```bash
cd optifleet-logistics
```

### 2. Créer un environnement virtuel Python

Depuis le dossier du projet :

```bash
python -m venv .venv
```

Activer l'environnement virtuel.

**Windows — Git Bash :**

```bash
source .venv/Scripts/activate
```

**Windows — PowerShell :**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS :**

```bash
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

Cette commande installe les bibliothèques nécessaires au pipeline.

### 4. Exécuter le pipeline de collecte

```bash
python src/collecte_carburants.py
```

Le script effectue les opérations suivantes :

1. Interroge l'API publique des prix des carburants.
2. Récupère les stations du département du Rhône.
3. Nettoie et transforme les données avec Pandas.
4. Identifie les stations situées dans la Métropole de Lyon.
5. Effectue les contrôles qualité.
6. Exporte les données préparées au format CSV.

### 5. Consulter les fichiers générés

Après une exécution réussie :

- `data/raw/` contient les données JSON récupérées.
- `data/processed/` contient les fichiers CSV préparés.

Les noms des fichiers incluent la date de collecte.

**Remarque :** les fichiers de données sont exclus de GitHub via `.gitignore`. Ils sont générés localement lors de l'exécution du pipeline.

### 6. Désactiver l'environnement virtuel

```bash
deactivate
```

### Stockage et visualisation

Le pipeline Python prépare les fichiers CSV.

L'import dans BigQuery et l'exploitation des vues SQL constituent les étapes suivantes du projet. Le dashboard Looker Studio utilise les données disponibles dans BigQuery.

L'exécution du script Python ne met donc pas automatiquement à jour les données BigQuery ou le dashboard.
