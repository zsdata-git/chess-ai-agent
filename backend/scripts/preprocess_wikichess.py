from pathlib import Path
import re
import pandas as pd


# ============================================================
# 1. CONFIGURATION
# ============================================================

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

INPUT_FILE = DATA_DIR / "wikichess_articles.csv"
OUTPUT_FILE = DATA_DIR / "wikichess_clean.csv"

# Nombre minimum de caractères pour conserver un article
MIN_TEXT_LENGTH = 150


# ============================================================
# 2. NETTOYAGE DU TEXTE
# ============================================================

def clean_text(text):
    """
    Nettoie les textes extraits de Wikichess.

    Objectifs :
    - supprimer les menus et éléments répétitifs ;
    - conserver les explications des ouvertures ;
    - retirer les statistiques détaillées des parties ;
    - normaliser les espaces.
    """

    if not isinstance(text, str):
        return ""

    # Le contenu éditorial commence généralement après
    # le dernier menu "Fischer random chess".
    marker = "Fischer random chess"

    if marker not in text:
        return ""

    text = text.rsplit(marker, 1)[-1].strip()

    # Supprimer les éventuels blocs de navigation en fin d'article
    text = re.split(
        r"\[\s*Chess forum\s*\]",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    # Supprimer les statistiques détaillées à partir
    # de la première ligne de coups/statistiques.
    text = re.split(
        r"\[ECO\s+[\"']",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    # Supprimer les informations sur les contributeurs
    text = re.split(
        r"Contributors\s*:",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    # Supprimer les liens vers le visualiseur
    text = re.sub(
        r"See this chess line with the javascript viewer",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Normaliser les espaces
    text = re.sub(r"\s+", " ", text)

    # Supprimer les séparateurs résiduels
    text = re.sub(r"={3,}", "", text)

    # Normaliser les espaces après nettoyage
    text = re.sub(r"\s+", " ", text).strip()

    return text.strip()


# ============================================================
# 3. CHARGEMENT ET PRÉTRAITEMENT
# ============================================================

def preprocess_articles():

    print("Chargement des articles Wikichess...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Articles initiaux : {len(df)}")

    # Nettoyer les textes
    df["clean_content"] = df["content"].apply(clean_text)

    # Calculer la longueur du texte nettoyé
    df["clean_length"] = df["clean_content"].str.len()

    # Conserver les articles suffisamment longs
    df_clean = df[
        df["clean_length"] >= MIN_TEXT_LENGTH
    ].copy()

    # Écarter l'article identifié comme non pertinent
    df_clean = df_clean[
        df_clean["article_id"] != 20122
    ].copy()

    # Supprimer les doublons exacts
    df_clean = df_clean.drop_duplicates(
        subset=["clean_content"]
    )

    # Conserver uniquement les colonnes utiles
    df_clean = df_clean[
        [
            "article_id",
            "source",
            "url",
            "clean_content",
            "clean_length",
        ]
    ]

    # Enregistrer le résultat
    df_clean.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print("\n================================")
    print("PRÉTRAITEMENT TERMINÉ")
    print("================================")

    print(f"Articles initiaux : {len(df)}")
    print(f"Articles conservés : {len(df_clean)}")
    print(f"Articles écartés : {len(df) - len(df_clean)}")

    print(f"\nFichier enregistré : {OUTPUT_FILE}")

    print("\n--- APERÇU DES ARTICLES ---")

    for _, row in df_clean.iterrows():

        print(f"\nArticle : {row['article_id']}")
        print(f"Longueur : {row['clean_length']} caractères")

        print("Texte :")
        print(row["clean_content"][:300])

        print("-" * 50)


# ============================================================
# 4. EXÉCUTION
# ============================================================

if __name__ == "__main__":
    preprocess_articles()