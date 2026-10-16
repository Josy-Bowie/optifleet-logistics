-- ============================================================
-- PROJET : OptiFleet Logistics
-- FICHIER : sql/analyses.sql
-- OBJECTIF : Historisation et analyse des prix du Gazole
-- ============================================================


-- ============================================================
-- C8.2.4 : CREATION DE LA VUE DEDOUBLONNEE
-- ============================================================

-- Objectif métier :
-- Conserver une seule observation par station, carburant
-- et journée de collecte.

-- Source : table historique BigQuery
-- Destination : vue v_prix_gazole

CREATE OR REPLACE VIEW
    `optifleet-logistics2026.optifleet.v_prix_gazole`
AS

SELECT *
FROM `optifleet-logistics2026.optifleet.prix_gazole_historique`

QUALIFY ROW_NUMBER() OVER (
    PARTITION BY cle_observation
    ORDER BY horodatage_collecte DESC
) = 1;



-- ============================================================
-- C8.3.1 : OBSERVER LES STATIONS SUR DEUX JOURNEES
-- ============================================================

-- Objectif :
-- Comparer visuellement les prix et leur validite
-- entre le 15 et le 16 octobre 2026.

SELECT
    id,
    ville,
    date_collecte,
    gazole_prix,
    prix_valide
FROM `optifleet-logistics2026.optifleet.v_prix_gazole`
WHERE date_collecte IN ('2026-10-15', '2026-10-16')
ORDER BY id, date_collecte
LIMIT 20;

-- ============================================================
-- C8.3.2 : CREER DEUX COLONNES POUR COMPARER LES DATES
-- ============================================================

SELECT
id, date_collecte, prix_valide,

IF(date_collecte = '2026-10-15', prix_valide, NULL) AS valide_15, 

IF(date_collecte = '2026-10-16', prix_valide, NULL) AS valide_16

FROM `optifleet-logistics2026.optifleet.v_prix_gazole`

WHERE date_collecte IN ('2026-10-15','2026-10-16')

ORDER BY id, date_collecte

LIMIT 20;


-- ============================================================
-- C8.3.3 : REGROUPER les STATUS PAR STATION
-- ============================================================

SELECT id,

 LOGICAL_OR(
  IF(date_collecte = '2026-10-15' , prix_valide, NULL)) AS valide_15,

 LOGICAL_OR(
  IF (date_collecte = '2026-10-16' , prix_valide, NULL)) AS valide_16

FROM `optifleet-logistics2026.optifleet.v_prix_gazole`

WHERE date_collecte IN ('2026-10-15', '2026-10-16')

GROUP BY id

ORDER BY id

LIMIT 20;



-- ============================================================
-- C8.3.4 : IDENTIFIER LES CHANGEMENTS DE VALIDITE
-- ============================================================

WITH comparaison AS (

    SELECT
        id,

        LOGICAL_OR(
            IF(date_collecte = '2026-10-15', prix_valide, NULL)
        ) AS valide_15,

        LOGICAL_OR(
            IF(date_collecte = '2026-10-16', prix_valide, NULL)
        ) AS valide_16

    FROM `optifleet-logistics2026.optifleet.v_prix_gazole`

    WHERE date_collecte IN ('2026-10-15', '2026-10-16')

    GROUP BY id
)

SELECT
    id,
    valide_15,
    valide_16

FROM comparaison

WHERE valide_15 IS DISTINCT FROM valide_16

ORDER BY id;




-- ============================================================
-- C8.3.5 : ANALYSER LES STATIONS AYANT CHANGE DE STATUT
-- ============================================================

-- Objectif :
-- Identifier les prix et dates de mise à jour des trois
-- stations dont la validité a changé entre le 15 et le 16/10.

-- Résultat observé :
-- Vénissieux : prix manquant -> prix valide.
-- Fontaines-sur-Saône : prix valide -> prix manquant.
-- Feyzin : prix valide -> prix manquant.

SELECT
    id,
    ville,
    date_collecte,
    gazole_prix,
    prix_valide,
    gazole_maj

FROM `optifleet-logistics2026.optifleet.v_prix_gazole`

WHERE id IN ('69200009', '69270004', '69320008')

AND date_collecte IN ('2026-10-15', '2026-10-16')

ORDER BY id, date_collecte;