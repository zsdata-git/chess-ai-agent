"""
Indexation multilingue des articles Wikichess.

Objectif :
Comparer deux modèles d'embedding en conservant
exactement le même découpage et les mêmes données.
"""

from index_wikichess import (
    load_articles,
    prepare_chunks,
    index_in_milvus,
)

import index_wikichess


# ============================================================
# CONFIGURATION MULTILINGUE
# ============================================================

index_wikichess.EMBEDDING_MODEL = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

index_wikichess.COLLECTION_NAME = (
    "wikichess_openings_multilingual"
)


# ============================================================
# EXÉCUTION
# ============================================================

def main():

    print("=" * 60)
    print("INDEXATION WIKICHESS MULTILINGUE")
    print("=" * 60)

    # Exactement les mêmes articles
    df = load_articles()

    # Exactement le même découpage
    records = prepare_chunks(df)

    if not records:
        raise ValueError("Aucun chunk à indexer.")

    # Seul le modèle d'embedding change
    embeddings = index_wikichess.generate_embeddings(records)

    # Nouvelle collection Milvus
    index_in_milvus(records, embeddings)

    print("=" * 60)
    print("INDEXATION MULTILINGUE TERMINÉE")
    print("=" * 60)


if __name__ == "__main__":
    main()