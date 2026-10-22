# -*- coding: utf-8 -*-
"""
Générateur de données pour le projet "Sales-Department-Project" (version Tunisie).

Objectif : créer un dataset PRATIQUE mais RÉALISTE sur les ventes quotidiennes
d'un réseau fictif de supérettes tunisiennes, entre le 01/01/2022 et le 31/12/2025.

Ce que les données simulent :
  - 2 magasins : Tunis Centre-ville et Sousse Marina (Sousse vend plus l
été -> tourisme)
  - une tendance de croissance (inflation + développement du réseau)
  - une saisonnalité hebdomadaire (week-end samedi/dimanche chargé)
  - une saisonnalité annuelle (décembre festif, été touristique, rentrée scolaire)
  - l'effet RAMADAN et des Aïds (les courses augmentent pendant le jeûne)
  - les jours fériés tunisiens (17 décembre, 1er mai, 25 juillet...)
  - le prix du carburant (essence sans plomb, en TND/litre, tarifs illustratifs)

Le dataset contient volontairement des ERREURS de qualité (valeurs manquantes,
doublons, valeurs aberrantes) pour que l'étape de NETTOYAGE dans le notebook
ait un vrai travail à faire, comme dans la vraie vie.
"""
import numpy as np
import pandas as pd

np.random.seed(42)  # Pour que les résultats soient toujours identiques

# ----------------------------------------------------------------------------
# 1) Calendrier : du 1er janvier 2022 au 31 décembre 2025 (1461 jours)
# ----------------------------------------------------------------------------
dates = pd.date_range(start="2022-01-01", end="2025-12-31", freq="D")

# ----------------------------------------------------------------------------
# 2) Jours fériés tunisiens (dates fixes + fêtes religieuses mobiles)
# ----------------------------------------------------------------------------
feries_fixes = {
    (1, 1):   "Nouvel An",
    (3, 20):  "Fête de l'Indépendance",
    (4, 9):   "Journée des Martyrs",
    (5, 1):   "Fête du Travail",
    (7, 25):  "Fête de la République",
    (8, 13):  "Fête de la Femme",
    (10, 15): "Fête de l'Évacuation",
    (12, 17): "Fête de la Révolution",
}

# Fêtes religieuses mobiles (approximations, suffisantes pour un projet éducatif)
aides_fitr = ["2022-05-02", "2023-04-21", "2024-04-10", "2025-03-30"]
aides_idha = ["2022-07-09", "2023-06-28", "2024-06-16", "2025-06-06"]
mouled     = ["2022-10-08", "2023-09-27", "2024-09-16", "2025-09-04"]
ras_el_am  = ["2022-07-30", "2023-07-19", "2024-07-07", "2025-06-26"]
ramadan_debuts = ["2022-04-02", "2023-03-23", "2024-03-11", "2025-03-01"]
ramadan_durées = [30, 29, 30, 29]  # 2022 et 2024 ont compté 30 jours de jeûne

def fenetre_depuis(date_str, nb_jours):
    """Donne la période de N jours qui commence à date_str."""
    d = pd.Timestamp(date_str)
    return pd.date_range(d, periods=nb_jours, freq="D")

def table_jours_speciaux():
    """Retourne 2 dictionnaires : {date: nom} pour fériés, {date: mult} pour Ramadan."""
    nom_ferie, mult_ramadan = {}, {}
    for a in range(2022, 2026):
        for (m, j), nom in feries_fixes.items():
            nom_ferie[pd.Timestamp(a, m, j)] = nom
    for s in aides_fitr:
        for d in fenetre_depuis(s, 2):
            nom_ferie[d] = "Aïd el-Fitr"
    for s in aides_idha:
        for d in fenetre_depuis(s, 2):
            nom_ferie[d] = "Aïd el-Idha"
    for s in ras_el_am:
        nom_ferie[pd.Timestamp(s)] = "Ras-El-Am-Hejri"
    for s in mouled:
        nom_ferie[pd.Timestamp(s)] = "Mouled"
    for deb, duree in zip(ramadan_debuts, ramadan_durées):
        for d in fenetre_depuis(deb, duree):
            mult_ramadan[d] = 1.35
    return nom_ferie, mult_ramadan

nom_ferie_map, mult_ramadan_map = table_jours_speciaux()

# ----------------------------------------------------------------------------
# 3) Prix du carburant (essence sans plomb, TND/litre) - Tarifs INFORMATIFS
#    inspirés des vrais tarifs tunisiens (hausse forte d'avril 2022).
# ----------------------------------------------------------------------------
def prix_carburant(date):
    if date <= pd.Timestamp("2022-03-31"):
        return 2.375
    if date <= pd.Timestamp("2022-12-31"):
        return 2.575   # forte hausse d'avril 2022
    if date <= pd.Timestamp("2024-12-31"):
        return 2.525
    return 2.575       # légère hausse en 2025

# ----------------------------------------------------------------------------
# 4) Coefficients qui façonnent les ventes
# ----------------------------------------------------------------------------
magasins = {
    # nom : (vente journalière de base en TND, bonus été touristique Sousse)
    "Supérette Tunis Centre-ville": (12500, 1.00),
    "Supérette Sousse Marina":      (9000,  1.25),
}
# Lundi=0 ... Dimanche=6. Le samedi (5) est le jour le plus fort en Tunisie.
mult_semaine = [0.85, 0.82, 0.88, 0.95, 1.05, 1.30, 1.15]
# Mois de l'année : décembre festif 1.20, été 1.08-1.15.
mult_mois = {1: 0.95, 2: 0.92, 3: 1.00, 4: 1.05, 5: 1.00, 6: 1.08,
             7: 1.12, 8: 1.15, 9: 1.05, 10: 1.00, 11: 0.98, 12: 1.20}

def croissance_annee(annee, jour_dans_annee):
    base = {2022: 1.00, 2023: 1.09, 2024: 1.18, 2025: 1.28}[annee]
    return base * (1.0 + 0.03 * jour_dans_annee / 365.0)  # léger +3 % dans l'année

# ----------------------------------------------------------------------------
# 5) Fabrication du dataset (chaque ligne = 1 magasin, 1 jour)
# ----------------------------------------------------------------------------
lignes = []
for date in dates:
    f = nom_ferie_map.get(date, "Aucun")
    est_ferie = int(f != "Aucun")
    est_ramadan = int(date in mult_ramadan_map)
    carburant = prix_carburant(date)
    for nom, (base, bonus_ete) in magasins.items():
        mult_ferie = 1.30 if est_ferie else 1.00
        mult_ram = mult_ramadan_map.get(date, 1.00)
        mult_automne_rentrée = 1.12 if (date.month == 9 and date.day >= 15) else 1.00
        mult_ete_tourisme = bonus_ete if date.month in (7, 8) else 1.00
        # si plusieurs effets le même jour, on prend le plus fort
        effets = [mult_ferie, mult_ram, mult_automne_rentrée, mult_ete_tourisme]
        vente = base
        vente *= croissance_annee(date.year, date.dayofyear)
        vente *= mult_semaine[date.dayofweek]
        vente *= mult_mois[date.month]
        vente *= max(effets)
        vente *= np.exp(np.random.normal(0, 0.05))          # bruit normal ~±5 %
        if np.random.rand() < 0.03:                          # 3 % de jours creux
            vente *= 0.65                                    # (pluie, fermeture...)
        lignes.append({
            "Date": date.date().isoformat(),
            "Magasin": nom,
            "Ventes_TND": round(vente, 2),
            "Jour_Ferie": est_ferie,
            "Nom_Ferie": f,
            "Ramadan": est_ramadan,
            "Prix_Carburant_TND": carburant,
        })

df = pd.DataFrame(lignes)
print("Lignes propres générées :", len(df))

# ----------------------------------------------------------------------------
# 6) Injection de DÉFAUTS volontaires (pour l'étape nettoyage du notebook)
# ----------------------------------------------------------------------------
idx_nan = np.random.choice(df.index, size=22, replace=False)
df.loc[idx_nan, "Ventes_TND"] = np.nan            # 22 ventes manquantes

doublons = df.sample(4, random_state=7)           # 4 lignes saisies 2 fois
df = pd.concat([df, doublons], ignore_index=True)

idx_outliers = np.random.choice(df.index, size=3, replace=False)
df.loc[idx_outliers[0], "Ventes_TND"] = -650.0    # erreur de saisie (négatif)
df.loc[idx_outliers[1], "Ventes_TND"] = -820.0    # erreur de saisie (négatif)
df.loc[idx_outliers[2], "Ventes_TND"] = 260000.0  # un "0" en trop (vente folle)

# ----------------------------------------------------------------------------
# 7) Sauvegarde + contrôles qualité affichés dans le terminal
# ----------------------------------------------------------------------------
chemin = "ventes_tunisie_2022_2025.csv"
df.to_csv(chemin, index=False)

lu = pd.read_csv(chemin)
print("Lignes finales (avec défauts) :", len(lu))
print("Ventes manquantes (NaN) :", lu["Ventes_TND"].isna().sum())
print("Doublons exacts :", lu.duplicated().sum())
print("Période :", lu["Date"].min(), "->", lu["Date"].max())
print("\nAperçu :")
print(lu.head())
print("\nVente totale moyenne par jour (TND) :",
      round(lu["Ventes_TND"].mean(), 1))
print("Fichier écrit :", chemin)
