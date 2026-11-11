"""
Service de recherche vectorielle multilingue.

Recherche les passages Wikichess pertinents dans Milvus
à partir d'une question en français ou en anglais.
"""

from functools import lru_cache

from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer


MILVUS_URI = "http://localhost:19530"

COLLECTION_NAME = "wikichess_openings_multilingual"

MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


@lru_cache(maxsize=1)
def get_embedding_model():
    """Charger le modèle une seule fois."""
    return SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=1)
def get_milvus_client():
    """Créer un client Milvus réutilisable."""
    return MilvusClient(uri=MILVUS_URI)


def search_wikichess(question: str, top_k: int = 3):
    """
    Rechercher les passages les plus pertinents.

    Args:
        question: Question en français ou en anglais.
        top_k: Nombre maximum de résultats.

    Returns:
        Liste des passages avec leurs métadonnées.
    """

    model = get_embedding_model()
    client = get_milvus_client()

    # Génération de l'embedding de la question
    query_vector = model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    # Recherche dans Milvus
    results = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_vector],
        limit=top_k,
        output_fields=[
            "article_id",
            "text",
            "url"
        ],
        search_params={
            "metric_type": "COSINE",
            "params": {}
        }
    )

    passages = []

    for result in results[0]:

        entity = result["entity"]

        passages.append({
            "article_id": str(entity["article_id"]),
            "text": entity["text"],
            "url": entity["url"],
            "score": round(float(result["distance"]), 3)
        })

    return passages