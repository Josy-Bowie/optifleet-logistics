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