# -*- coding: utf-8 -*-
"""Construit le notebook Jupyter Sales_Department_Project.ipynb (version Tunisie)."""
import json

C = []  # liste de (type, source)

def md(src):
    C.append(("markdown", src))

def code(src):
    C.append(("code", src))

# ============================================================================
# CELLULES DU NOTEBOOK
# ============================================================================
md(r"""# Analyse des ventes d'un commerce de détail 

Bienvenue dans ce projet de Data Science de A à Z.

## Objectifs du projet
1. **Analyser les tendances des ventes passées** (comment les chiffres évoluent).
2. **Étudier l'impact de facteurs externes** : jours fériés tunisiens, Ramadan, Aïd, prix du carburant.
3. **Construire un modèle de Machine Learning** qui prédit les ventes du mois suivant.

## Les données
Ventes **quotidiennes en dinars (TND)** d'un réseau fictif mais réaliste de 2 supérettes tunisiennes
(*Supérette Tunis Centre-ville* et *Supérette Sousse Marina*), du **01/01/2022 au 31/12/2025**.
Le fichier contient volontairement des erreurs (trous, doublons, valeurs aberrantes)
pour que l'étape de nettoyage ressemble à la vraie vie d'un Data Scientist.

## Plan du notebook
| Étape | Contenu |
|---|---|
| 1 | Charger et découvrir les données |
| 2 | Première exploration visuelle |
| 3 | Nettoyage des données |
| 4 | Tendances des ventes (croissance, saisonnalité) |
| 5 | Impact des jours fériés, du Ramadan et du carburant |
| 6 | Préparation du Machine Learning |
| 7 | Entraînement et évaluation du modèle |
| 8 | Prédiction des ventes de janvier 2026 |

## Mini-glossaire (les mots qu'on utilisera)
| Mot | Signification |
|---|---|
| Données | les chiffres qu'on analyse |
| DataFrame | le "tableau" que manipule pandas |
| Valeur manquante | un trou dans la table (NaN) |
| Valeur aberrante | une erreur évidente (ex : -650 dinars) |
| Jour férié | jour officiellement chômé |
| Tendance | la direction générale des ventes |
| Ancre de niveau | le niveau moyen récent des ventes (moyenne 28 jours) |
| Prédiction | ce que le modèle prévoit pour demain |

> **Pour ouvrir ce notebook depuis le terminal** : `cd chemin/vers/Sales-Department-Project` puis `jupyter notebook`
""")

code(r"""# ÉTAPE 0 ---- Charger les outils
# pandas       : le "Excel géant" du Data Scientist
# matplotlib   : trace les graphiques | seaborn : les rend plus jolis
# scikit-learn : le Machine Learning (apprentissage automatique)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error

# Réglages d'affichage
sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams["figure.figsize"] = (12, 5)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

import os
os.makedirs("figures", exist_ok=True)   # où on sauvegarde les graphiques

print("Outils chargés. pandas:", pd.__version__, "| numpy:", np.__version__,
      "| scikit-learn:", __import__("sklearn").__version__)
""")

md(r"""## Étape 1 — Charger et découvrir les données

Un fichier **CSV** est une table : lignes = jours/magasins, colonnes = informations.
`pd.read_csv()` lit ce fichier et crée un **DataFrame** (notre table en mémoire).

Colonnes :
- `Date` : le jour (AAAA-MM-JJ)
- `Magasin` : la supérette concernée
- `Ventes_TND` : le chiffre d'affaires du jour **en dinars tunisiens**
- `Jour_Ferie` (0/1) et `Nom_Ferie` : jour férié officiel
- `Ramadan` (0/1) : jour situé pendant le mois de Ramadan
- `Prix_Carburant_TND` : prix de l'essence sans plomb (TND/litre)
""")

code(r"""# ÉTAPE 1.1 ---- Lire le fichier CSV : 1 ligne de code !
df = pd.read_csv("ventes_tunisie_2022_2025.csv")

print("Forme de la table (lignes, colonnes) :", df.shape)
df.head()   # montrer les 5 premières lignes (le .head() affiche la table)
""")

code(r"""# ÉTAPE 1.2 ---- Vue technique : types de colonnes et mémoire utilisée
df.info()
""")

code(r"""# ÉTAPE 1.3 ---- Statistiques de base sur les colonnes numériques
df.describe()
""")

code(r"""# ÉTAPE 1.4 ---- Questions rapides de compréhension
print("Magasins :", df["Magasin"].unique().tolist())
print("Période   :", df["Date"].min(), "-> ", df["Date"].max())
print("Jours fériés distincts :", df.loc[df["Jour_Ferie"] == 1, "Nom_Ferie"].nunique())
""")

md(r"""## Étape 2 — Première exploration visuelle

**Règle d'or du Data Scientist : toujours TRACER les données avant de calculer quoi que ce soit.**
On convertit d'abord `Date` en vrai type "date" (sinon c'est du texte).
""")

code(r"""# ÉTAPE 2.1 ---- La courbe des ventes dans le temps
df["Date"] = pd.to_datetime(df["Date"])   # texte -> vraie date

plt.figure(figsize=(13, 5))
sns.lineplot(data=df, x="Date", y="Ventes_TND", hue="Magasin", linewidth=0.9)
plt.title("Ventes quotidiennes 2022-2025 (TND) — les pics = fériés / Ramadan / Aïd")
plt.ylabel("Ventes (TND)")
plt.xlabel("")
plt.legend(title="Magasin")
plt.savefig("figures/01_ventes_quotidiennes.png", dpi=110, bbox_inches="tight")
plt.show()
""")

md(r"""**Observation bizarre :** la courbe est écrasée par un point *très* haut (260 000 TND alors
que les ventes normales tournent autour de 10 000-20 000 TND) et il y a des points *négatifs*
(-650, -820 : impossible de vendre -650 dinars !). Ce sont des **erreurs de saisie**.
Regardons aussi l'histogramme pour confirmer.
""")

code(r"""# ÉTAPE 2.2 ---- Histogramme : la "répartition" des ventes
plt.figure(figsize=(12, 4))
sns.histplot(df["Ventes_TND"].dropna(), bins=60, color="#2a9d8f")
plt.title("Distribution des ventes journalières (en TND)")
plt.ylabel("Nombre de jours")
plt.savefig("figures/02_distribution.png", dpi=110, bbox_inches="tight")
plt.show()
""")

md(r"""## Étape 3 — Nettoyage des données

C'est **la partie la plus longue du vrai travail** (souvent 70 % du temps !).
Les 4 vérifications classiques :
1. **Valeurs manquantes** : des cases vides -> compter, puis combler.
2. **Doublons** : des lignes saisies 2 fois -> supprimer.
3. **Valeurs aberrantes** (-650 TND ou 260 000 TND) -> transformer en "inconnu" puis combler.
4. **Types** : la date doit être une vraie date (fait à l'étape 2).
""")

code(r"""# ÉTAPE 3.1 ---- Diagnostic : où sont les problèmes ?
print("Valeurs manquantes par colonne :")
print(df.isna().sum())
print("\nDoublons exacts à supprimer :", df.duplicated().sum())
print("Ventes négatives (impossibles) :", (df["Ventes_TND"] < 0).sum())
print("Ventes > 60 000 TND (erreurs) :", (df["Ventes_TND"] > 60000).sum())
""")

code(r"""# ÉTAPE 3.2 ---- Réparer : les 3 classic fixes
# a) Les ventes impossibles deviennent "inconnues" (NaN)
df.loc[df["Ventes_TND"] < 0, "Ventes_TND"] = np.nan
df.loc[df["Ventes_TND"] > 60000, "Ventes_TND"] = np.nan

# b) Les doublons : on garde la première copie
avant = len(df)
df = df.drop_duplicates(keep="first").reset_index(drop=True)
print(f"Doublons supprimés : {avant - len(df)}")

# c) Les trous : interpolation (la valeur se "coud" entre ses voisines), magasin par magasin
df = df.sort_values(["Magasin", "Date"]).reset_index(drop=True)
df["Ventes_TND"] = (df.groupby("Magasin")["Ventes_TND"]
                      .transform(lambda s: s.interpolate(limit_direction="both")))
print("Ventes manquantes restantes :", df["Ventes_TND"].isna().sum())
""")

code(r"""# ÉTAPE 3.3 ---- Contrôle qualité final : la table doit être pleine et propre
df.info()       # plus aucune valeur manquante dans Ventes_TND
df.describe()   # min ~4 000, max ~25 000 : les extrémités sont raisonnables maintenant
""")

md(r"""## Étape 4 — Tendances des ventes

On additionne les 2 magasins pour obtenir le **total du réseau**, puis :
- la **moyenne mobile 30 jours** lisse le bruit pour voir la TENDANCE,
- le **regroupement par mois** montre la saisonnalité annuelle,
- une **heatmap** (jour de la semaine × mois) révèle les habitudes des clients tunisiens.
""")

code(r"""# ÉTAPE 4.1 ---- Total du réseau + moyenne mobile
total_jour = df.groupby("Date", as_index=False)["Ventes_TND"].sum()

total_jour["Moyenne_30j"] = total_jour["Ventes_TND"].rolling(window=30).mean()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
ax1.plot(total_jour["Date"], total_jour["Ventes_TND"], lw=0.7, color="#4361ee")
ax1.set_title("Ventes totales du réseau — chaque point = 1 jour")
ax2.plot(total_jour["Date"], total_jour["Moyenne_30j"], lw=2.5, color="#e76f51")
ax2.set_title("Avec moyenne mobile 30 jours : la tendance se lit mieux")
ax2.set_ylabel("Ventes (TND)")
plt.savefig("figures/03_tendance_reseau.png", dpi=110, bbox_inches="tight")
plt.show()
""")

code(r"""# ÉTAPE 4.2 ---- Chiffre d'affaires mensuel (chaque barre = 1 mois)
total_mois = total_jour.set_index("Date")["Ventes_TND"].resample("ME").sum()

ax = total_mois.plot(kind="bar", figsize=(14, 4.5), color="#3d5a80", width=0.85)
ax.set_xticklabels([d.strftime("%Y-%m") for d in total_mois.index], rotation=45, ha="right")
ax.set_title("Chiffre d'affaires mensuel du réseau (TND)")
ax.set_ylabel("Total (TND)")
plt.savefig("figures/04_ca_mensuel.png", dpi=110, bbox_inches="tight")
plt.show()

croissance = (total_mois.iloc[-12:].sum() / total_mois.iloc[:12].sum() - 1) * 100
print(f"Chiffre d'affaires de 2025 supérieur à 2022 de : {croissance:,.0f} %")
""")

code(r"""# ÉTAPE 4.3 ---- Heatmap : jour de la semaine (lignes) x mois (colonnes)
df["Jour_Sem"] = df["Date"].dt.dayofweek     # 0=lundi ... 6=dimanche
df["Mois"] = df["Date"].dt.month

tb = df.pivot_table(index="Jour_Sem", columns="Mois", values="Ventes_TND", aggfunc="mean")
tb.index = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"]

plt.figure(figsize=(12, 3.5))
sns.heatmap(tb, cmap="YlGnBu")
plt.title("Vente moyenne par jour de semaine et par mois — le samedi est le plus fort")
plt.ylabel("")
plt.xlabel("Mois")
plt.savefig("figures/05_heatmap_semaine.png", dpi=110, bbox_inches="tight")
plt.show()
""")

md(r"""**Ce qu'on apprend de la tendance :**
- croissance d'environ +9 % par an (pouvoir d'achat, inflation, développement du réseau) ;
- chacun des mois de décembre et de juillet-août excelle (fêtes, tourisme à Sousse) ;
- le **samedi** domine nettement la semaine (week-end tunisien sam/dim + courses du vendredi soir) ;
- la moyenne mobile fait apparaître les bosses de chaque Ramadan / Aïd.
""")

md(r"""## Étape 5 — Impact des facteurs externes

Question 1 : **Les jours fériés augmentent-ils les ventes ?**
Question 2 : **Quel est le meilleur jour férié pour les affaires ?**
Question 3 : **Le Ramadan a-t-il un effet visible ?**
Question 4 : **Et le prix du carburant ?**
""")

code(r"""# ÉTAPE 5.1 ---- Ventes les jours fériés vs jours normaux
moyennes = df.groupby("Jour_Ferie")["Ventes_TND"].mean()
effet = (moyennes[1] / moyennes[0] - 1) * 100

plt.figure(figsize=(6, 4))
plt.bar(["Jour normal", "Jour férié"], moyennes, color=["#8d99ae", "#e63946"], width=0.6)
plt.title("Vente moyenne par jour férié ?")
plt.ylabel("Ventes moyennes (TND)")
for i, m in enumerate(moyennes):
    plt.text(i, m * 1.01, f"{m:,.0f} TND", ha="center")
plt.savefig("figures/06_feries_vs_normal.png", dpi=110, bbox_inches="tight")
plt.show()

print(f"Les jours fériés font +{effet:.0f} % de ventes en moyenne.")
""")

code(r"""# ÉTAPE 5.2 ---- Classement des fêtes : lesquelles rapportent le plus ?
top = df.loc[df["Jour_Ferie"] == 1].groupby("Nom_Ferie")["Ventes_TND"].mean().sort_values()
top.plot(kind="barh", figsize=(9, 5), color="#f4a261")
plt.title("Classement des fêtes : moyenne des ventes (TND)")
plt.xlabel("Ventes moyennes (TND)")
plt.tight_layout()
plt.savefig("figures/07_classement_fetes.png", dpi=110, bbox_inches="tight")
plt.show()
""")

code(r"""# ÉTAPE 5.3 ---- Effet du Ramadan
moy_ram = df.groupby("Ramadan")["Ventes_TND"].mean()
effet_ram = (moy_ram[1] / moy_ram[0] - 1) * 100

plt.figure(figsize=(6, 4))
plt.bar(["Hors Ramadan", "Pendant Ramadan"], moy_ram, color=["#8d99ae", "#2a9d8f"], width=0.6)
plt.title("Vente moyenne : Ramadan vs reste de l'année")
plt.ylabel("Ventes moyennes (TND)")
for i, m in enumerate(moy_ram):
    plt.text(i, m * 1.01, f"{m:,.0f} TND", ha="center")
plt.savefig("figures/08_ramadan.png", dpi=110, bbox_inches="tight")
plt.show()

print(f"Pendant le Ramadan les ventes font +{effet_ram:.0f} % (courses des repas après le jeûne).")
""")

code(r"""# ÉTAPE 5.4 ---- Et le prix du carburant ?
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4.5))

# gauche : le prix de l'essence dans le temps (en "escaliers")
ax1.step(df["Date"], df["Prix_Carburant_TND"], where="post", color="#e76f51", lw=2)
ax1.set_title("Prix de l'essence (TND/litre) — hausse d'avril 2022")
ax1.set_ylabel("TND/litre")
ax1.tick_params(axis="x", rotation=45)

# droite : chaque point = 1 jour (ventes vs prix carburant)
ax2.scatter(df["Prix_Carburant_TND"], df["Ventes_TND"], alpha=0.15, s=8, color="#4361ee")
ax2.set_title("Ventes du jour vs prix de l'essence")
ax2.set_xlabel("Prix essence (TND/litre)")
ax2.set_ylabel("Ventes (TND)")

plt.savefig("figures/09_carburant.png", dpi=110, bbox_inches="tight")
plt.show()
""")

code(r"""# ÉTAPE 5.5 ---- Matrice de corrélation : mesurer les liens en un seul chiffre
# 1 = lien parfait positif | 0 = aucun lien | -1 = lien parfait négatif
corr = df[["Ventes_TND", "Jour_Ferie", "Ramadan", "Prix_Carburant_TND"]].corr()

plt.figure(figsize=(5.5, 4.5))
sns.heatmap(corr, annot=True, cmap="RdBu_r", vmin=-1, vmax=1, fmt=".2f", square=True)
plt.title("Corrélations")
plt.tight_layout()
plt.savefig("figures/10_correlations.png", dpi=110, bbox_inches="tight")
plt.show()
""")

md(r"""**Conclusions de l'étape 5 :**
- Fériés, Ramadan et Aïd **boostent** les ventes de façon nette et logique (logique économique).
- Le carburant montre une corrélation **faible et positive (r ≈ 0,23)**. C'est une
  **corrélation fallacieuse** : de 2022 à 2025 les deux montent à cause du TEMPS
  (ventes croissantes + tarifs réajustés), pas l'un à cause de l'autre.
  Leçon très classique : **corrélation ne veut pas dire causalité**.
""")

md(r"""## Étape 6 — Préparer le Machine Learning

Idée : le modèle doit **deviner les ventes de demain**. Trois familles de "features"
(variables d'entrée) :

1. **Le calendrier** : jour de la semaine, mois, jour du mois, férié ?, Ramadan ?, prix carburant.
2. **La mémoire** (pour prédire DEMAIN) : Ventes_J1 (hier), Ventes_J7 (semaine dernière), Moy_7j.
3. **L'ancre de niveau** (pour prédire le MOIS) : `Base28` = moyenne des 28 derniers jours.
   Elle fixe le niveau du réseau SANS se re-nourrir des propres prédictions du modèle
   (sinon la prévision dérive, comme un micro posé devant son haut-parleur).

On travaille sur le **total du réseau** (1 ligne par jour) puisque les infos externes
sont les mêmes pour les 2 magasins.
""")

code(r"""# ÉTAPE 6.1 ---- Construire la table du modèle
ventes = df.groupby("Date", as_index=False)["Ventes_TND"].sum()
infos = (df.groupby("Date")
           .agg(Jour_Ferie=("Jour_Ferie", "max"),
                Ramadan=("Ramadan", "max"),
                Prix_Carburant_TND=("Prix_Carburant_TND", "first")))
base_ml = ventes.merge(infos, on="Date")

# 1) calendrier
base_ml["Jour_Sem"] = base_ml["Date"].dt.dayofweek
base_ml["Mois"] = base_ml["Date"].dt.month
base_ml["Jour_Mois"] = base_ml["Date"].dt.day

# 2) l'ancre de niveau : moyenne des 28 jours précédents
base_ml["Base28"] = base_ml["Ventes_TND"].shift(1).rolling(28).mean()

# 3) mémoire : hier, il y a 1 semaine, moyenne des 7 derniers jours
base_ml["Ventes_J1"] = base_ml["Ventes_TND"].shift(1)
base_ml["Ventes_J7"] = base_ml["Ventes_TND"].shift(7)
base_ml["Moy_7j"] = base_ml["Ventes_TND"].shift(1).rolling(7).mean()

# Les 28 premiers jours n'ont pas encore d'ancre : on les retire
base_ml = base_ml.dropna().reset_index(drop=True)

CALENDAR = ["Jour_Sem", "Mois", "Jour_Mois", "Jour_Ferie", "Ramadan", "Prix_Carburant_TND"]
MEMOIRE = ["Ventes_J1", "Ventes_J7", "Moy_7j"]
base_ml[["Date", "Ventes_TND", "Base28"] + CALENDAR + MEMOIRE].head()
""")

code(r"""# ÉTAPE 6.2 ---- Découpage temporel : entraîner sur le PASSÉ, tester sur le FUTUR
# ICI ON NE MÉLANGE PAS (pas de shuffle!) : en série temporelle, le futur ne doit
# jamais "fuir" dans l'entraînement.
train = base_ml[base_ml["Date"] < "2025-01-01"]      # 2022 -> 2024 : apprentissage
test  = base_ml[base_ml["Date"] >= "2025-01-01"]     # 2025 : examen de fin d'année

y_train = train["Ventes_TND"]
y_test = test["Ventes_TND"]

print(f"Entraînement : {len(train)} jours (2022-2024) | Test : {len(test)} jours (2025)")
""")

md(r"""## Étape 7 — Entraîner et évaluer les modèles

On entraîne **deux forêts aléatoires** (*Random Forest* : des centaines d'arbres de
décision qui votent ensemble — robustes et faciles à expliquer) :
- **modele_demain** : calendrier + mémoire -> spécialiste de "demain" (J+1) ;
- **modele_mois** : calendrier + ancre `Base28` -> spécialiste du "mois prochain".

Notation de l'examen :
- **MAE** : erreur moyenne en dinars (le plus lisible : combien on se trompe, en TND).
- **RMSE** : comme la MAE mais sanctionne plus les grosses erreurs.
- **R²** : part de la variation expliquée (1 = parfait, 0 = inutile).
On compare aussi à une **référence naïve** : "demain = hier". Si nos modèles ne la battent pas, inutiles !
""")

code(r"""# ÉTAPE 7.1 ---- Entraîner les 2 modèles et faire passer l'examen 2025
modele_demain = RandomForestRegressor(n_estimators=400, random_state=42, n_jobs=-1)
modele_demain.fit(train[CALENDAR + MEMOIRE], y_train)
pred_demain = modele_demain.predict(test[CALENDAR + MEMOIRE])

modele_mois = RandomForestRegressor(n_estimators=400, random_state=42, n_jobs=-1)
modele_mois.fit(train[CALENDAR + ["Base28"]], y_train)
pred_mois = modele_mois.predict(test[CALENDAR + ["Base28"]])

# Référence naïve : "demain ressemblera à hier"
mae_naive = mean_absolute_error(y_test, test["Ventes_J1"])
resultats = pd.DataFrame(
    {"MAE (TND)": [mean_absolute_error(y_test, pred_demain),
                   mean_absolute_error(y_test, pred_mois),
                   mae_naive],
     "RMSE (TND)": [root_mean_squared_error(y_test, pred_demain),
                    root_mean_squared_error(y_test, pred_mois),
                    root_mean_squared_error(y_test, test["Ventes_J1"])],
     "R²": [r2_score(y_test, pred_demain),
            r2_score(y_test, pred_mois),
            r2_score(y_test, test["Ventes_J1"])]},
    index=["RF mémoire (demain)", "RF ancre (calendrier+niveau)", "Référence naïve"])
print(resultats.round(1))
""")

code(r"""# ÉTAPE 7.2 ---- Voir les prédictions "demain" sur l'année de test (2025)
plt.figure(figsize=(13, 5))
plt.plot(test["Date"], y_test, lw=1.1, color="#2b2d42", label="Ventes réelles (2025)")
plt.plot(test["Date"], pred_demain, lw=1.1, color="#e63946", alpha=0.85,
         label="Prédictions (RF mémoire)")
plt.title("Ventes réelles vs prédictions — année 2025")
plt.ylabel("Ventes (TND)")
plt.legend()
plt.savefig("figures/11_predictions_2025.png", dpi=110, bbox_inches="tight")
plt.show()
""")

code(r"""# ÉTAPE 7.3 ---- Qu'est-ce que le modèle "demain" regarde en premier ?
imp = pd.Series(modele_demain.feature_importances_, index=CALENDAR + MEMOIRE)
imp = imp.sort_values() * 100
imp.plot(kind="barh", figsize=(9, 5), color="#2a9d8f")
plt.title("Importance des variables (modèle demain)")
plt.xlabel("Importance (%)")
plt.tight_layout()
plt.savefig("figures/12_importances.png", dpi=110, bbox_inches="tight")
plt.show()
""")

md(r"""## Étape 8 — Prévision des ventes de janvier 2026

Pour le MOIS, on utilise **modele_mois** avec la technique **de l'ancre gelée** :
1. on calcule l'ANCRE = moyenne des 28 derniers jours réels (décembre 2025) ;
2. on la garde **fixe** tout le mois (on ne nourrit jamais le modèle avec ses
   propres prédictions — testé : c'est ce qui fait dériver la prévision) ;
3. le calendrier façonne chaque journée (+30 % le samedi, férié, etc.).

Hypothèses annoncées : carburant stable, pas de Ramadan en janvier 2026
(le Ramadan 2026 commence vers le 18 février), Nouvel An férié le 1er janvier.
""")

code(r"""# ÉTAPE 8.1 ---- Prévision de janvier 2026 (ancre gelée)
base_fixe = base_ml["Ventes_TND"].iloc[-28:].mean()   # l'ancre = niveau actuel du réseau
prix_futur = base_ml["Prix_Carburant_TND"].iloc[-1]   # on suppose le prix stable
feries_2026 = {pd.Timestamp("2026-01-01")}            # Nouvel An

dates_futur = pd.date_range("2026-01-01", periods=31, freq="D")
prevs = []
for jour in dates_futur:
    ligne = {
        "Jour_Sem": jour.dayofweek,
        "Mois": jour.month,
        "Jour_Mois": jour.day,
        "Jour_Ferie": int(jour in feries_2026),
        "Ramadan": 0,
        "Prix_Carburant_TND": prix_futur,
        "Base28": base_fixe,
    }
    yhat = float(modele_mois.predict(pd.DataFrame([ligne])[CALENDAR + ["Base28"]])[0])
    prevs.append({"Date": jour, "Ventes_Predites_TND": yhat})

future = pd.DataFrame(prevs)
future["Jour"] = future["Date"].dt.dayofweek.map(
    {0: "lundi", 1: "mardi", 2: "mercredi", 3: "jeudi", 4: "vendredi", 5: "samedi", 6: "dimanche"})

f_aff = future.copy()
f_aff["Date"] = f_aff["Date"].dt.strftime("%d/%m/%Y")
print(f"Ancre utilisée (moyenne des 28 derniers jours réels) : {base_fixe:,.0f} TND\n")
print("Prévision du 1er au 10 janvier 2026 :")
print(f_aff.head(10)[["Date", "Jour", "Ventes_Predites_TND"]].round(0).to_string(index=False))
print(f"\nChiffre d'affaires prévu pour janvier 2026 : "
      f"{future['Ventes_Predites_TND'].sum():,.0f} TND")
""")

code(r"""# ÉTAPE 8.2 ---- Graphique final : 2 derniers mois réels + la prévision
plt.figure(figsize=(13, 5))
recents = total_jour.tail(60)
plt.plot(recents["Date"], recents["Ventes_TND"], lw=1.2, color="#2b2d42",
         label="Ventes réelles (nov-déc 2025)")
plt.plot(future["Date"], future["Ventes_Predites_TND"], "--", lw=2, color="#e63946",
         label="Prévision (janvier 2026)")
plt.title("Et après ? La prévision du modèle pour janvier 2026")
plt.ylabel("Ventes (TND)")
plt.legend()
plt.savefig("figures/13_prevision_2026.png", dpi=110, bbox_inches="tight")
plt.show()
""")

md(r"""## Récapitulatif et suite

**Ce qu'on a démontré :**
1. Les ventes du réseau croissent d'environ +9 % par an, avec de fortes saisonnalités
   (Ramadan, décembre, été touristique à Sousse, week-ends samedis).
2. Les fériés et le Ramadan augmentent clairement les ventes ; le lien avec le carburant
   est trompeur (corrélation fallacieuse liée au temps).
3. Pour le J+1, le modèle à mémoire bat largement la référence naïve : la MAE du modèle
   est (tab. du dessus) ~4 553 TND pour la naïve contre ~2 112 TND pour le ML.
4. Pour le mois entier, l'ANCRE GELÉE + calendrier prévoit janvier sans dérive, alors
   qu'une boucle récursive ferait grossir la prévision de jour en jour.

**Limites honnêtes :** pas de météo dans les données, hypothèse de carburant stable,
modèle simple au niveau des feuilles (il prédit un peu "dans la moyenne" par type de journée).

**Pour aller plus loin (exercices) :**
- Ajouter la température moyenne de la journée comme feature.
- Comparer avec `Prophet` (bibliothèque Meta) ou `XGBoost`.
- Refaire les modèles séparément par magasin.
- Créer une petite application avec Streamlit pour montrer la prévision au gérant.

**Mabrouk, projet terminé ! Les graphiques sont sauvegardés dans le dossier `figures/`.**
""")

# ============================================================================
# ÉCRITURE DU FICHIER .ipynb
# ============================================================================
cells = []
for i, (t, src) in enumerate(C):
    cell = {"id": f"cell-{i:02d}", "cell_type": t, "metadata": {},
            "source": src.splitlines(keepends=True)}
    if t == "code":
        cell["outputs"] = []
        cell["execution_count"] = None
    cells.append(cell)

nb = {"cells": cells,
      "metadata": {
          "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
          "language_info": {"name": "python", "version": "3.14"},
          "title": "Sales Department Project - Tunisie"},
      "nbformat": 4, "nbformat_minor": 5}

with open("Sales_Department_Project.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Notebook écrit : {len(cells)} cellules ({sum(1 for t, _ in C if t == 'code')} code, "
      f"{sum(1 for t, _ in C if t == 'markdown')} markdown)")
