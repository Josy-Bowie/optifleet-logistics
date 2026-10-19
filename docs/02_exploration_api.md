
# Mission B — Exploration de l'API des prix des carburants

## Projet : OptiFleet Logistics

**Date d'exploration :** 14 octobre 2026

**Objectif :** évaluer une source de données publique pour
analyser les prix du Gazole dans la Métropole de Lyon.

**Méthode :**
1. Lire la fiche officielle.
2. Examiner les données et leur schéma.
3. Tester les requêtes API.
4. Synthétiser les résultats.

---


## Phase 1 — Identification de la source

### 1.1 Métadonnées du jeu de données

| Information | Valeur observée |
|---|---|
| Titre | Prix des carburants en France - Flux instantané - v2 |
| Producteur / créateur | DGCCRF |
| Licence | Mention générale du portail : Licence Ouverte 2.0, sauf indication contraire |
| Fréquence de mise à jour | Flux : toutes les 10 minutes ; récupération par le portail : toutes les 15 minutes |
| Dernière mise à jour observée | 14/10/2026 à 16 h 17 |

**Source :**
https://data.economie.gouv.fr/explore/dataset/prix-des-carburants-en-france-flux-instantane-v2/

**Date de consultation :** 14 octobre 2026.

### 1.2 Description de la source

Ce jeu de données est publié sur le portail
data.economie.gouv.fr.

Il présente les informations issues du système
d'information officiel des prix des carburants.

Les données comprennent notamment :

- Les informations générales des stations-service.
- Les adresses et coordonnées géographiques.
- Les carburants proposés.
- Les prix des carburants.
- Les dates de mise à jour des prix.
- Les informations sur les ruptures de carburant.

### 1.3 Fréquence et actualisation

La fiche indique que le flux instantané est mis
à jour toutes les 10 minutes.

Le portail programme la récupération des données
toutes les 15 minutes.

Cependant, cela ne signifie pas que chaque station
met à jour son prix à cette fréquence.

Pour vérifier la fraîcheur du prix du Gazole,
nous utiliserons le champ `gazole_maj`.

### 1.4 Intérêt pour OptiFleet Logistics

Cette source permet d'identifier les stations-service
et de comparer les prix du Gazole selon leur
localisation.

Elle constitue une base pertinente pour notre
projet d'optimisation des dépenses de carburant.

Une collecte quotidienne permettra de construire
notre propre historique et d'analyser les
évolutions de prix.


## Phase 2 — Profilage des données

### 2.1 Volumétrie et méthode

| Mesure | Valeur | Méthode |
|---|---:|---|
| Champs du jeu de données | 47 | Onglet Schéma |
| Enregistrements France entière | 9 817 | Aucun filtre, observation du 14/10/2026 |
| Enregistrements avec département 69 | À mesurer | API : `code_departement="69"` |
| Département 69 + Gazole disponible | 191 | Filtres visuels : Département Rhône + Carburants disponibles Gazole |
| Département 69 + prix Gazole renseigné | À mesurer | API : `code_departement="69" AND gazole_prix IS NOT NULL` |

**Attention :** « Gazole disponible » et
« Prix Gazole renseigné » ne sont pas nécessairement
des conditions équivalentes.

### 2.2 Champs utiles

| Champ API | Type observé | Utilité métier |
|---|---|---|
| id | Entier | Identifier une station |
| adresse | Texte | Localiser la station |
| ville | Texte | Comparer les communes |
| cp | Texte | Identifier le code postal |
| geom | Point géographique | Cartographier les stations |
| gazole_prix | Décimal | Calculer les prix et les KPI |
| gazole_maj | Date et heure | Mesurer la fraîcheur |
| code_departement | Texte | Préfiltrer la zone 69 |

### 2.3 Contrôles de qualité à effectuer

- Prix du Gazole manquants : à mesurer.
- Prix nuls ou négatifs : à vérifier.
- Dates de mise à jour manquantes : à vérifier.
- Prix datant de plus de 48 heures : à mesurer.
- Variations dans l'écriture des communes : à observer.
- Stations en rupture de Gazole : à examiner.

---

## Phase 3 — Exploration de l'API


### 3.1 Première requête API

**Objectif :** récupérer cinq enregistrements
du département 69.

**Endpoint :** `/records`

**Filtre :** `code_departement="69"`

**Paramètre :** `limit=5`

**Résultat observé :**

- `total_count` : **200**
- Nombre d'enregistrements demandés : **5**
- Format de réponse : **JSON**

**Observation :**

La première station retournée possède un prix
de Gazole non renseigné (`gazole_prix: null`).

Cela montre qu'un filtre géographique ne suffit pas
pour obtenir uniquement des prix exploitables.

Un contrôle des valeurs manquantes sera donc
nécessaire avant le calcul des KPI.



### 3.2 Exemple de réponse JSON

La requête retourne des informations sur les
stations-service du département 69.

Extrait d'un enregistrement réel de la station
située à Lyon (sélection des champs utiles) :

```json
{
  "id": 69009003,
  "cp": "69009",
  "adresse": "69 AVENUE DU 25EME RTS",
  "ville": "Lyon",
  "geom": {
    "lon": 4.801,
    "lat": 45.781
  },
  "gazole_maj": "2026-10-14T07:31:00+00:00",
  "gazole_prix": 2.401,
  "code_departement": "69"
}
```


### 3.3 Deuxième requête — Prix Gazole renseigné

#### Objectif

Identifier le nombre de stations-service du département 69
disposant d'un prix de Gazole renseigné.

#### Filtre API utilisé

```sql
code_departement = "69" AND gazole_prix IS NOT NULL
```

Paramètre : `limit=5`

#### Résultats observés le 14 octobre 2026

| Indicateur | Valeur |
|---|---:|
| Total des stations du département 69 | 200 |
| Stations avec prix Gazole renseigné | 192 |
| Stations sans prix Gazole | 8 |
| Taux de prix renseignés | 96 % |
| Taux de prix manquants | 4 % |

#### Calculs

Nombre de prix manquants :

200 - 192 = 8 stations

Taux de valeurs manquantes :

(8 / 200) × 100 = 4 %

Taux de complétude :

(192 / 200) × 100 = 96 %

#### Interprétation métier

L'exploration de l'API montre que 96 % des stations
du département 69 disposent d'un prix de Gazole
renseigné lors de la consultation.

Les 4 % de stations sans prix devront être exclues
des calculs de prix et des classements.

Cependant, un prix renseigné ne garantit pas
qu'il soit récent ou que le carburant soit disponible.

Avant d'utiliser les données dans le tableau de bord
OptiFleet Logistics, des contrôles complémentaires
seront nécessaires sur la fraîcheur des prix,
leur cohérence et les éventuelles ruptures.

#### Limite méthodologique

Ces résultats correspondent à deux requêtes effectuées
sur un flux instantané le 14 octobre 2026.

Les effectifs peuvent évoluer au cours de la journée.
Le périmètre exploré est le département 69 ;
il ne représente pas nécessairement la Métropole de Lyon.



### 3.4 Vérification des limites de l'API

#### Objectif

Vérifier le nombre maximal d'enregistrements
accepté par l'endpoint `/records`.

#### Test réalisé

J'ai testé le paramètre `limit=200` avec le filtre :

`code_departement="69" AND gazole_prix IS NOT NULL`

#### Réponse exacte de l'API

```json
{
  "error_code": "InvalidRESTParameterError",
  "message": "Invalid value for limit API parameter: 200 was found but -1 <= limit <= 100 is expected."
}
```

#### Interprétation

Le serveur refuse la requête car la valeur 200
dépasse la limite maximale autorisée de 100.

L'API indique que le paramètre `limit` doit
être compris entre -1 et 100 inclus.

Pour notre pipeline de collecte, nous utiliserons
`limit=100` afin de récupérer les données
en plusieurs requêtes.

#### Conséquence métier

Notre filtre a identifié 192 stations avec un
prix Gazole renseigné dans le département 69.

Une seule requête avec `limit=100` ne permet
donc pas de récupérer toutes les stations.

Nous devrons utiliser la pagination pour obtenir
les enregistrements restants.



## Phase 4 — Synthèse

### Points forts de la source

L'API des prix des carburants fournit des données
structurées sur les stations-service françaises.

Elle contient plusieurs informations utiles pour
OptiFleet Logistics :

- L'identifiant et l'adresse des stations.
- Leur localisation géographique.
- Le prix du Gazole.
- La date de mise à jour du prix.
- Les informations sur les ruptures de carburant.

Ces informations permettent de comparer les prix
entre stations et d'identifier des possibilités
d'économies sur les dépenses de carburant.

### Limites et anomalies

L'exploration a mis en évidence plusieurs limites :

1. Sur 200 stations du département 69, 8 ne disposent
   pas d'un prix Gazole renseigné, soit 4 %.

2. Certains prix peuvent être anciens.
   La présence d'un prix ne garantit donc pas
   sa fraîcheur.

3. L'endpoint `/records` refuse `limit=200`.
   La récupération complète nécessite une pagination.

4. Le département 69 ne correspond pas exactement
   au périmètre de la Métropole de Lyon.

Ces limites nécessitent des contrôles de qualité
avant l'exploitation des données.

### Conséquence du flux instantané

Le jeu de données représente un état des informations
disponibles au moment de la consultation.

Pour analyser l'évolution des prix dans le temps,
OptiFleet Logistics devra conserver des collectes
successives.

Chaque enregistrement collecté devra contenir :

- L'identifiant de la station.
- Le prix du Gazole.
- La date de mise à jour du prix (`gazole_maj`).
- La date de collecte (`date_collecte`).

Il faudra distinguer la date de collecte de la date
de mise à jour du prix.

La collecte quotidienne permettra de constituer
progressivement un historique exploitable.

### Décision pour OptiFleet Logistics

L'API est retenue comme source principale de données
pour le projet, sous réserve de contrôles de qualité.

Les prochaines étapes consisteront à :

- Automatiser la collecte avec Python.
- Récupérer toutes les pages de résultats.
- Nettoyer et valider les données avec Pandas.
- Filtrer les stations de la Métropole de Lyon.
- Conserver un historique quotidien.
- Stocker les données dans BigQuery.
- Construire un tableau de bord dans Looker Studio.

L'objectif final est d'aider OptiFleet Logistics
à identifier les stations les plus intéressantes
pour le ravitaillement de sa flotte diesel.


### Points de vigilance complémentaires

#### Disponibilité et prix renseigné

Le filtre visuel « Gazole disponible » retourne
191 stations, contre 192 stations avec un prix
Gazole renseigné dans l'API.

Cet écart doit être vérifié au niveau des stations.
Un prix renseigné ne prouve pas à lui seul que
le carburant est disponible.

#### Prix potentiellement atypiques

Une station de Lyon 9e affiche un prix de
2,401 €/L lors de notre exploration.

Ce prix respecte les bornes de plausibilité
absolues (0,50 à 4,00 €/L), mais son caractère
atypique devra être évalué par rapport à la
distribution des prix du marché.

Nous utiliserons notamment les quartiles
et l'écart interquartile (IQR).

#### Gestion des fuseaux horaires

Le champ `gazole_maj` contient un horodatage UTC.

Exemple : `2026-10-14T07:31:00+00:00`
correspond à 09:31 à Lyon le 14 octobre 2026.

Les calculs de fraîcheur seront effectués
sur des horodatages cohérents, en UTC.

#### Paramètre limit=-1

La documentation de l'Explore API v2.1
présente -1 comme une valeur spéciale.

Pour les endpoints d'export, elle permet
de demander tous les enregistrements.

Pour l'endpoint `/records`, nous retenons
la pagination avec `limit=100` et `offset`.

Source : https://help.opendatasoft.com/apis/ods-explore-v2/explore_v2.1.html



#### Différence entre actualisation et fraîcheur

Deux horloges doivent être distinguées :

- L'actualisation du portail : récupération programmée
  des données toutes les 15 minutes.
- `gazole_maj` : date et heure de la dernière mise
  à jour déclarée du prix du Gazole.

Un portail récemment actualisé peut donc contenir
des prix dont la dernière déclaration est ancienne.

Un prix ancien n'est pas nécessairement erroné :
il peut être resté inchangé.

Cependant, son ancienneté augmente l'incertitude
sur son utilisation pour une décision immédiate.

Pour OptiFleet Logistics, nous appliquerons
une règle métier de fraîcheur de 48 heures
pour le classement des stations recommandées.

Les prix plus anciens pourront être conservés
pour l'analyse, mais signalés ou exclus
des recommandations opérationnelles.
