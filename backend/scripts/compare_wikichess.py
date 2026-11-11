"""
Comparaison de deux stratégies de découpage Wikichess.

V1 : découpage fixe
V2 : découpage par phrases

Évaluation :
- Similarité vectorielle
- Position du document attendu
- Recall@3
- MRR
"""

from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

MILVUS_URI = "http://localhost:19530"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

COLLECTIONS = [
    "wikichess_openings",
    "wikichess_openings_v2",
]


# Questions avec articles attendus
TEST_CASES = [
    {
        "question": "What is the Sicilian Defense?",
        "expected_article": "3",
    },
    {
        "question": "How does the Caro-Kann Defense begin?",
        "expected_article": "22",
    },
    {
        "question": "What are the characteristics of the French Defense?",
        "expected_article": "21",
    },
    {
        "question": "What is Alekhine's Defense?",
        "expected_article": "33",
    },
    {
        "question": "What is the King's Pawn Game?",
        "expected_article": "1",
    },
]


# ============================================================
# ÉVALUATION
# ============================================================

def evaluate_collection(client, model, collection_name):

    print("\n" + "=" * 65)
    print(f"COLLECTION : {collection_name}")
    print("=" * 65)

    hits = 0
    reciprocal_ranks = []

    for test in TEST_CASES:

        question = test["question"]
        expected = test["expected_article"]

        vector = model.encode(
            question,
            normalize_embeddings=True,
        ).tolist()

        results = client.search(
            collection_name=collection_name,
            data=[vector],
            limit=3,
            output_fields=["article_id", "text", "url"],
        )[0]

        print(f"\nQuestion : {question}")
        print(f"Article attendu : {expected}")

        found_rank = None

        for rank, result in enumerate(results, start=1):

            article_id = str(
                result["entity"]["article_id"]
            )

            score = result["distance"]

            print(
                f"  Rang {rank} | "
                f"Article {article_id} | "
                f"Score {score:.3f}"
            )

            if article_id == expected and found_rank is None:
                found_rank = rank

        if found_rank is not None:

            hits += 1
            reciprocal_ranks.append(1 / found_rank)

            print(f"Résultat attendu trouvé au rang {found_rank}")

        else:

            reciprocal_ranks.append(0)

            print("Article attendu absent du TOP 3")

    recall_at_3 = hits / len(TEST_CASES)

    mrr = sum(reciprocal_ranks) / len(TEST_CASES)

    print("\n" + "-" * 65)

    print(f"Recall@3 : {recall_at_3:.2%}")
    print(f"MRR@3    : {mrr:.3f}")

    return {
        "collection": collection_name,
        "recall_at_3": recall_at_3,
        "mrr_at_3": mrr,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("Chargement du modèle d'embedding...")

    model = SentenceTransformer(MODEL_NAME)

    client = MilvusClient(uri=MILVUS_URI)

    results = []

    for collection_name in COLLECTIONS:

        if not client.has_collection(collection_name):
            raise RuntimeError(
                f"Collection absente : {collection_name}"
            )

        result = evaluate_collection(
            client,
            model,
            collection_name,
        )

        results.append(result)

    print("\n" + "=" * 65)
    print("COMPARAISON FINALE")
    print("=" * 65)

    for result in results:

        print(
            f"{result['collection']} : "
            f"Recall@3 = {result['recall_at_3']:.2%} | "
            f"MRR@3 = {result['mrr_at_3']:.3f}"
        )


if __name__ == "__main__":
    main()