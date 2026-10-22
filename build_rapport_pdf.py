# -*- coding: utf-8 -*-
"""Génère Sales-Product-Project rapport PDF : document explicatif complet du projet."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

PROJET = Path("/home/yosriii/Desktop/Sales-Department-Project")
PDF_OUT = PROJET / "Sales-Department-Rapport.pdf"

ROUGE = colors.HexColor("#c8392f")
VERT = colors.HexColor("#27867b")
TEXTE = colors.HexColor("#23262b")
GRIS = colors.HexColor("#f4f6f8")
BORD = colors.HexColor("#e2e6ea")

styles = getSampleStyleSheet()
base = ParagraphStyle("base", parent=styles["BodyText"], fontName="Helvetica",
                      fontSize=10.5, leading=15, textColor=TEXTE)
h1 = ParagraphStyle("h1", parent=base, fontName="Helvetica-Bold", fontSize=19,
                    leading=24, textColor=ROUGE, spaceBefore=16, spaceAfter=8)
h2 = ParagraphStyle("h2", parent=base, fontName="Helvetica-Bold", fontSize=14,
                    leading=18, textColor=VERT, spaceBefore=12, spaceAfter=6)
h3 = ParagraphStyle("h3", parent=base, fontName="Helvetica-Bold", fontSize=11.5,
                    leading=15, textColor=TEXTE, spaceBefore=9, spaceAfter=3)
titre_couverture = ParagraphStyle("titre", parent=h1, fontSize=27, leading=34,
                                  alignment=TA_CENTER, spaceBefore=190)
sous_titre = ParagraphStyle("sous", parent=base, fontSize=14, leading=20,
                            alignment=TA_CENTER, textColor=VERT)
centré = ParagraphStyle("cent", parent=base, fontSize=10.5, alignment=TA_CENTER,
                        textColor=colors.HexColor("#565d66"))
code = ParagraphStyle("code", parent=base, fontName="Courier", fontSize=9.5,
                      leading=13, backColor=GRIS, borderPadding=5,
                      borderColor=BORD, borderWidth=0.7)
cell_tete = ParagraphStyle("ct", parent=base, fontName="Helvetica-Bold",
                           fontSize=9.5, leading=12, textColor=colors.white)
cell_txt = ParagraphStyle("cw", parent=base, fontName="Courier", fontSize=9,
                          leading=12)
cell_desc = ParagraphStyle("cd", parent=base, fontSize=9.5, leading=12.5)
legende = ParagraphStyle("leg", parent=base, fontSize=9, leading=12,
                         alignment=TA_CENTER, textColor=colors.HexColor("#565d66"),
                         spaceAfter=10)

def tableau(entete, lignes, largeurs):
    if len(entete) == 1 and isinstance(entete[0], (list, tuple)):
        entete = entete[0]          # accepte [("Colonne", "...")] comme ["Colonne", "..."]
    corps = [[Paragraph(c, cell_tete) for c in entete]]
    for ligne in lignes:
        corps.append([Paragraph(ligne[0], cell_txt),
                      Paragraph(ligne[1], cell_desc)])
    t = Table(corps, colWidths=largeurs, repeatRows=1)
    style = [("BACKGROUND", (0, 0), (-1, 0), ROUGE),
             ("GRID", (0, 0), (-1, -1), 0.6, BORD),
             ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("LEFTPADDING", (0, 0), (-1, -1), 7),
             ("RIGHTPADDING", (0, 0), (-1, -1), 7),
             ("TOPPADDING", (0, 0), (-1, -1), 5),
             ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]
    for i in range(1, len(corps)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), GRIS))
    t.setStyle(TableStyle(style))
    return t

def image(chemin, largeur_cm=16.6):
    p = PROJET / chemin
    if not p.exists():
        return Spacer(0, 10)
    w, h = ImageReader(str(p)).getSize()
    L = largeur_cm * cm
    return Image(str(p), width=L, height=L * h / w)

def bas_de_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORD)
    canvas.line(2 * cm, 1.35 * cm, (21 - 2) * cm, 1.35 * cm)
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(colors.HexColor("#565d66"))
    canvas.drawString(2 * cm, 1 * cm, "Projet Sales-Department-Project (version Tunisie) — rapport explicatif")
    canvas.drawRightString((21 - 2) * cm, 1 * cm, f"Page {doc.page}")
    canvas.restoreState()

contenu = []

# ----------------------------------------------------------------- couverture
contenu += [
    Paragraph("Analyse des ventes d'un commerce de détail<br/>version Tunisie", titre_couverture),
    Spacer(1, 14),
    Paragraph("Projet Sales-Department-Project — rapport explicatif complet", sous_titre),
    Spacer(1, 10),
    Paragraph("Bienvenue : ce document explique chaque fichier du projet,"
              " les 8 étapes du notebook et tous les résultats obtenus.", centré),
    Spacer(1, 30),
    Paragraph("Réseau fictif mais réaliste de 2 supérettes (Tunis et Sousse)<br/>"
              "Ventes quotidiennes en dinars du 01/01/2022 au 31/12/2025<br/>"
              "Machine Learning : modèle de prédiction des ventes", centré),
    Spacer(1, 220),
    Paragraph("Document généré automatiquement — October 22, 2026", legende),
]
contenu.append(PageBreak())

# ------------------------------------------------------------ objectif projet
contenu += [
    Paragraph("1. Objectifs du projet", h1),
    Paragraph("Ce projet suit le standard d'un vrai travail de Data Scientist : partir d'un"
              " fichier de ventes brutes, le comprendre, le nettoyer, l'analyser, puis"
              " construire un modèle qui prédit l'avenir. Trois objectifs précis :", base),
    Paragraph("<b>1.</b> Analyser les <b>tendances</b> des ventes passées (croissance, saisons,"
              " week-ends) ;", base),
    Paragraph("<b>2.</b> Étudier l'impact de <b>facteurs externes</b> : jours fériés tunisiens,"
              " Ramadan, Aïd, prix du carburant ;", base),
    Paragraph("<b>3.</b> Construire un <b>modèle de Machine Learning</b> simple pour prédire les"
              " ventes du mois suivant.", base),

    Paragraph("2. Les données : ventes_tunisie_2022_2025.csv", h1),
    Paragraph("Le dataset est <b>fictif mais réaliste</b> (généré avec un tirage aléatoire fixé"
              ", donc reproductible). Il simule les ventes d'un réseau de supérettes tunisiennes"
              " : 2 magasins, 1 461 jours (4 ans), soit 2 926 lignes :", base),
    tableau(
        [("Colonne", "Signification")],
        [["Date", "le jour (AAAA-MM-JJ) ; 1 ligne = 1 magasin x 1 jour"],
         ["Magasin", "Supérette Tunis Centre-ville ou Supérette Sousse Marina"],
         ["Ventes_TND", "chiffre d'affaires du jour, en dinars tunisiens (TND)"],
         ["Jour_Ferie / Nom_Ferie", "0/1 et nom du férié : 14 janvier, Aïd, 1er mai, 25 juillet..."],
         ["Ramadan", "0/1 : jour situé pendant le mois de jeûne (dates décalées chaque année)"],
         ["Prix_Carburant_TND", "prix de l'essence sans plomb (TND/litre), barèmes illustratifs"]],
        [4.4 * cm, 12.2 * cm]),
    Spacer(1, 2),
    Paragraph("Le fichier contient <b>volontairement</b> des défauts pour rendre l'étape de"
              " nettoyage réaliste : 23 ventes manquantes, 4 doublons de saisie et 3 erreurs"
              " aberrantes (-650 ; -820 ; 260 000 TND). C'est exactement ce qu'on trouve dans"
              " les données d'entreprise.", base),
]

# -------------------------------------------------------------- les fichiers
contenu += [
    Paragraph("3. Tous les fichiers du dossier et leur rôle", h1),
    tableau(
        [("Fichier", "Rôle dans le projet")],
        [["README.md", "Guide de démarrage : ouvrir le projet, résultats principaux, idées pour aller plus loin"],
         ["Sales_Department_Project.ipynb", "LE notebook pédagogique principal : 38 cellules (8 étapes), déjà exécuté, tout commenté pas à pas"],
         ["Sales_Department_Project.html", "La même documentation en une page web stylée : à ouvrir directement dans un navigateur"],
         ["Sales-Department-Rapport.pdf", "Ce rapport explicatif (le PDF que tu lis)"],
         ["ventes_tunisie_2022_2025.csv", "Le dataset de travail (entrée de tout le projet)"],
         ["generate_data.py", "Script Python qui génère le CSV : lance-le pour recréer les données à l'identique"],
         ["build_notebook.py", "Script qui reconstruit le notebook (38 cellules) : utile si tu veux l'adapter"],
         ["build_rapport_pdf.py", "Script qui génère ce PDF"],
         ["figures/ (13 PNG)", "Les 13 graphiques importants du projet, sauvegardés par le notebook"]],
        [6.2 * cm, 10.4 * cm]),
]

# --------------------------------------------------------- étapes du notebook
contenu += [
    Paragraph("4. Le notebook, étape par étape", h1),
    Paragraph("Chaque étape a ses cellules de code commentées (chargement -> analyse -> modèle),"
              " plus des commentaires «que devons-nous apprendre ici ?» :", base),
    Paragraph("<b>Étape 1 — Charger et découvrir les données.</b> On lit le CSV avec pandas :"
              " df.head(), df.info(), df.describe(). Premiers réflexes d'un Data Scientist.", base),
    Paragraph("<b>Étape 2 — Première exploration visuelle.</b> La courbe des ventes et l'histogramme"
              " : on VOIT les pics (fériés, Ramadan) et on remarque les erreurs de saisie qui"
              " écrasent le graphique.", base),
    Paragraph("<b>Étape 3 — Nettoyage.</b> 4 doublons supprimés, ventes aberrantes transformées en"
              " «inconnu» puis comblées par interpolation magasin par magasin. Résultat : 0 trou.", base),
    Paragraph("<b>Étape 4 — Tendances.</b> Total du réseau + moyenne mobile 30 jours + chiffre"
              " d'affaires mensuel + heatmap semaine x mois : croissance, weekend du samedi,"
              " décembre et l'été touristique de Sousse apparents.", base),
    Paragraph("<b>Étape 5 — Facteurs externes.</b> Fériés : +25 % de ventes ; Ramadan : +28 % ;"
              " classement des fêtes ; corrélation gas et ventes quasi nulle (corrélation"
              " fallacieuse : les deux montent avec le TEMPS).", base),
    Paragraph("<b>Étape 6 — Préparer le Machine Learning.</b> 3 familles de variables : calendrier,"
              " mémoire (Ventes_J1, Ventes_J7, Moy_7j) et ancre de niveau (Base28 = moyenne"
              " des 28 jours passés). Découpage temporel : entraînement 2022-2024, test 2025.", base),
    Paragraph("<b>Étape 7 — Deux forêts aléatoires.</b> modele_demain (mémoire, spécialiste J+1) et"
              " modele_mois (ancre + calendrier, spécialiste du mois). Comparés à la référence"
              " naïve «demain = hier».", base),
    Paragraph("<b>Étape 8 — Prévision de janvier 2026.</b> Ancre figée (moyenne des 28 derniers"
              " jours réels) + forme du calendrier : prévision sans dérive.", base),
]

# ------------------------------------------------------------------ résultats
contenu += [
    Paragraph("5. Les résultats en un coup d'oeil", h1),
    tableau(
        [("Question posée", "Réponse trouvée")],
        [["Le réseau grandit-il ?", "+27 % de chiffre d'affaires entre 2022 et 2025 (+9 % par an environ)"],
         ["Le week-end aide-t-il ?", "Le samedi est le meilleur jour (vente moyenne la plus haute)"],
         ["Les fériés augmentent-ils les ventes ?", "Oui : +25 % en moyenne par rapport à un jour normal"],
         ["Effet du Ramadan ?", "+28 % (les courses des repas après le jeûne)"],
         ["Et le prix du carburant ?", "Corrélation quasi nulle : exemple de corrélation fallacieuse"],
         ["Qui prédit bien «demain» ?", "RF mémoire : MAE 2 133 TND contre 4 549 TND pour la naïve (-53 % d'erreurs)"],
         ["Que prévoit janvier 2026 ?", "851 541 TND (ancre figée, validée : écart réel ~(−2 %))"]],
        [6.4 * cm, 10.2 * cm]),
    Spacer(1, 8),
    image("figures/03_tendance_reseau.png"),
    Paragraph("Figure 1 — Ventes du réseau : la courbe brute et la moyenne mobile 30 jours.", legende),
    image("figures/11_predictions_2025.png"),
    Paragraph("Figure 2 — Les prédictions (rouge) collent aux ventes réelles (noir) sur l'année test 2025.", legende),
    PageBreak(),
    image("figures/13_prevision_2026.png"),
    Paragraph("Figure 3 — La prévision (rouge en pointillés) de janvier 2026, sans dérive.", legende),
]

# ---------------------------------------------------------------- utilisation
contenu += [
    Paragraph("6. Comment utiliser le projet", h1),
    Paragraph("Ouvrir une invite de commande (terminal) et entrer :", base),
    Paragraph("cd ~/Desktop/Sales-Department-Project<br/>jupyter notebook", code),
    Spacer(1, 4),
    Paragraph("Le navigateur s'ouvre : cliquer sur Sales_Department_Project.ipynb, puis exécuter"
              " une cellule avec Maj+Entrée, ou tout relancer via Kernel -> Restart &amp; Run All."
              " Sans terminal : double-cliquer sur Sales_Department_Project.html.", base),
    Spacer(1, 6),
    Paragraph("Tout est déjà installé sur cette machine (pandas, matplotlib, seaborn,"
              " scikit-learn, Jupyter) et le noyau Python 3 (Data Science) est enregistré.", base),

    Paragraph("7. Limites honnêtes et suites possibles", h1),
    Paragraph("Limites : pas de météo dans les données ; hypothèse de prix du carburant stable ;"
              " le modèle «dans la moyenne» lisse un peu les extrêmes.", base),
    Paragraph("Pour aller plus loin : ajouter la température ; comparer avec Prophet ou XGBoost ;"
              " refaire un modèle par magasin ; créer une application Streamlit ; importer un vrai"
              " dataset Kaggle (ex. «Store Item Demand») avec la même démarche.", base),
    Spacer(1, 22),
    Paragraph("Mabrouk ! Bonne exploration des ventes !", sous_titre),
]

doc = SimpleDocTemplate(str(PDF_OUT), pagesize=A4,
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                        title="Projet Sales-Department-Project — Rapport",
                        author="Projet Data Science (version Tunisie)")
doc.build(contenu, onFirstPage=bas_de_page, onLaterPages=bas_de_page)
print("PDF écrit :", PDF_OUT)
