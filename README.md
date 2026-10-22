# Projet : Analyse des ventes d'un commerce de détail (version Tunisie)

Projet de Data Science complet, pensé pour un débutant : toutes les étapes sont
commentées pas à pas, **100 % en français**.

## Objectifs
1. Analyser les **tendances des ventes** d'un réseau de 2 supérettes (2022-2025).
2. Étudier l'impact des **facteurs externes** : jours fériés tunisiens, Ramadan, Aïd, prix du carburant.
3. **Prédire les ventes futures** avec du Machine Learning (janvier 2026).

## Contenu du dossier
| Fichier | Rôle |
|---|---|
| `Sales_Department_Project.ipynb` | Le notebook pédagogique COMPLET (déjà exécuté : toutes les sorties sont visibles) |
| `Sales_Department_Project.html` | La même version en page web stylée : s'ouvre dans n'importe quel navigateur, sans installer Jupyter |
| `Sales-Department-Rapport.pdf` | Rapport explicatif complet du projet en PDF (fichiers et rôles, 8 étapes, résultats) |
| `ventes_tunisie_2022_2025.csv` | Le dataset (2 926 lignes, ventes en dinars TND) |
| `generate_data.py` | Re-génère le CSV à l'identique : `python3 generate_data.py` |
| `build_notebook.py` | Reconstruit le notebook : `python3 build_notebook.py` |
| `build_rapport_pdf.py` | Re-génère le rapport PDF : `python3 build_rapport_pdf.py` |
| `figures/` | Les 13 graphiques sauvegardés par le notebook |

## Comment l'ouvrir
Tout est déjà installé sur cette machine (pandas, matplotlib, seaborn, scikit-learn, Jupyter),
et le noyau `Python 3 (Data Science)` est enregistré.

Dans un terminal :
```bash
cd chemin/vers/Sales-Department-Project
jupyter notebook
```
Puis ouvrir `Sales_Department_Project.ipynb`. Tu peux exécuter chaque cellule avec
`Maj + Entrée` (Shift + Enter), ou bien `Kernel` > `Restart & Run All` pour tout refaire.

Sans Jupyter : double-clic sur `Sales_Department_Project.html` (lecture seule).

## Les données
Chaque ligne = 1 magasin x 1 jour (2022-01-01 -> 31-12-2025) :
- `Date`, `Magasin` (Supérette Tunis Centre-ville / Supérette Sousse Marina)
- `Ventes_TND` : chiffre d'affaires du jour (dinars tunisiens)
- `Jour_Ferie` (0/1), `Nom_Ferie` (fériés tunisiens : 14 janvier, Aïd, 1er mai...)

- `Ramadan` (0/1) : le mois de jeûne (ses dates se décalent d'année en année)
- `Prix_Carburant_TND` : prix de l'essence (TND/litre, barèmes illustratifs inspirés des réels)

Les données sont **fictives mais réalistes** (créées par `generate_data.py`) et contiennent
volontairement des erreurs (trous, doublons, valeurs aberrantes) pour l'étape de nettoyage.

## Résultats obtenus (déjà calculés dans le notebook)
- Croissance du réseau : **+27 %** de chiffre d'affaires en 2025 par rapport à 2022.
- Jours fériés : **+25 %** de ventes en moyenne ; période de Ramadan : **+28 %**.
- Corrélation ventes/carburant : quasi nulle — exemple de **corrélation fallacieuse**.
- Modèle "demain" (Random Forest avec mémoire) : **MAE ~2 133 TND** (jour moyen ~33 000 TND)
  contre **4 549 TND** pour la référence naïve : le ML fait ~53 % d'erreur en moins.
- Prévision janvier 2026 : **851 541 TND** avec la méthode de l'ancre gelée
  (validée : l'écart réel n'est que d'environ -2 % là où une récursion dériverait de +17 %).

## Idées pour aller plus loin
1. Ajouter la météo comme variable.
2. Comparer avec Prophet/XGBoost.
3. Refaire un modèle par magasin.
4. Créer une petite application avec Streamlit.
