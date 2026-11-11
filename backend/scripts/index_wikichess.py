"""
Indexation des articles Wikichess dans Milvus.

Étapes :
1. Chargement des articles nettoyés
2. Découpage en chunks
3. Génération des embeddings
4. Création de la collection Milvus
5. Insertion des vecteurs et métadonnées
"""

from pathlib import Path

import pandas as pd
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient

import re


# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_FILE = BASE_DIR / "data" / "wikichess_clean.csv"

MILVUS_URI = "http://localhost:19530"

COLLECTION_NAME = "wikichess_openings_v2"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100


# ============================================================
# 2. DÉCOUPAGE DES ARTICLES
# ============================================================

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Découpe un texte en conservant autant que possible
    les phrases entières.

    Les chunks ont une taille cible de 700 caractères.
    Un chevauchement est conservé entre les chunks.
    """

    if not isinstance(text, str) or not text.strip():
        return []

    if chunk_size <= 0 or not 0 <= overlap < chunk_size:
        raise ValueError("Paramètres de découpage invalides.")

    # Séparation du texte en phrases
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    chunks = []
    current_chunk = ""

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        # Si la phrase tient dans le chunk actuel
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:

            current_chunk = (
                f"{current_chunk} {sentence}".strip()
            )

        else:

            # Enregistrer le chunk précédent
            if current_chunk:
                chunks.append(current_chunk)

            # Récupérer les dernières phrases pour le chevauchement
            overlap_text = ""

            if current_chunk:

                previous_sentences = re.split(
                    r"(?<=[.!?])\s+",
                    current_chunk
                )

                for previous_sentence in reversed(previous_sentences):

                    candidate = (
                        f"{previous_sentence} {overlap_text}".strip()
                    )

                    if len(candidate) > overlap:
                        break

                    overlap_text = candidate

            # Nouveau chunk
            current_chunk = (
                f"{overlap_text} {sentence}".strip()
            )

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# ============================================================
# 3. CHARGEMENT DES DONNÉES
# ============================================================

def load_articles():

    print("Chargement des articles Wikichess...")

    df = pd.read_csv(DATA_FILE)

    required_columns = {
        "article_id",
        "source",
        "url",
        "clean_content",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"Colonnes manquantes : {missing}")

    df = df.dropna(subset=["clean_content"])

    print(f"Articles chargés : {len(df)}")

    return df


# ============================================================
# 4. PRÉPARATION DES CHUNKS
# ============================================================

def prepare_chunks(df):

    records = []

    for _, row in df.iterrows():

        chunks = chunk_text(row["clean_content"])

        for chunk_id, chunk in enumerate(chunks):

            records.append(
                {
                    "article_id": str(row["article_id"]),
                    "source": str(row["source"]),
                    "url": str(row["url"]),
                    "chunk_id": chunk_id,
                    "text": chunk,
                }
            )

    print(f"Nombre total de chunks : {len(records)}")

    return records


# ============================================================
# 5. GÉNÉRATION DES EMBEDDINGS
# ============================================================

def generate_embeddings(records):

    print("Chargement du modèle d'embedding...")

    model = SentenceTransformer(EMBEDDING_MODEL)

    texts = [record["text"] for record in records]

    print("Génération des embeddings...")

    embeddings = model.encode(
        texts,
        batch_size=16,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    print(f"Dimensions des vecteurs : {embeddings.shape[1]}")

    return embeddings


# ============================================================
# 6. INDEXATION DANS MILVUS
# ============================================================

def index_in_milvus(records, embeddings):

    print("Connexion à Milvus...")

    client = MilvusClient(uri=MILVUS_URI)

    if client.has_collection(COLLECTION_NAME):

        raise RuntimeError(
            f"La collection '{COLLECTION_NAME}' existe déjà. "
            "Indexation interrompue pour éviter d'écraser des données."
        )

    print("Création de la collection...")

    client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=embeddings.shape[1],
        metric_type="COSINE",
    )

    data = []

    for i, record in enumerate(records):

        data.append(
            {
                "id": i + 1,
                "vector": embeddings[i].tolist(),
                "article_id": record["article_id"],
                "source": record["source"],
                "url": record["url"],
                "chunk_id": record["chunk_id"],
                "text": record["text"],
            }
        )

    print("Insertion des vecteurs...")

    result = client.insert(
        collection_name=COLLECTION_NAME,
        data=data,
    )

    print(f"Vecteurs insérés : {result['insert_count']}")

    client.load_collection(COLLECTION_NAME)

    print("Collection Milvus prête !")


# ============================================================
# 7. EXÉCUTION
# ============================================================

def main():

    print("=" * 60)
    print("INDEXATION WIKICHESS → MILVUS")
    print("=" * 60)

    df = load_articles()

    records = prepare_chunks(df)

    if not records:
        raise ValueError("Aucun chunk à indexer.")

    embeddings = generate_embeddings(records)

    index_in_milvus(records, embeddings)

    print("=" * 60)
    print("INDEXATION TERMINÉE")
    print("=" * 60)


if __name__ == "__main__":
    main()