"""
Comparaison de deux modèles d'embedding pour Wikichess.

Modèles :
1. all-MiniLM-L6-v2
2. paraphrase-multilingual-MiniLM-L12-v2

Évaluation :
- 5 questions en anglais
- 5 questions en français
- Recall@3
- MRR@3

Les collections Milvus existantes sont utilisées
sans modification.
"""

from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer


# ============================================================
# 1. CONFIGURATION
# ============================================================

MILVUS_URI = "http://localhost:19530"

TOP_K = 3

MODELS = {
    "MiniLM anglais": {
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "collection": "wikichess_openings_v2",
    },
    "MiniLM multilingue": {
        "model": (
            "sentence-transformers/"
            "paraphrase-multilingual-MiniLM-L12-v2"
        ),
        "collection": "wikichess_openings_multilingual",
    },
}


# ============================================================
# 2. QUESTIONS DE TEST
# ============================================================

QUESTIONS = [
    {
        "question": "What is the Sicilian Defense?",
        "expected": "3",
        "language": "EN",
    },
    {
        "question": "Qu'est-ce que la défense sicilienne ?",
        "expected": "3",
        "language": "FR",
    },
    {
        "question": "How does the Caro-Kann Defense begin?",
        "expected": "22",
        "language": "EN",
    },
    {
        "question": "Comment commence la défense Caro-Kann ?",
        "expected": "22",
        "language": "FR",
    },
    {
        "question": "What are the characteristics of the French Defense?",
        "expected": "21",
        "language": "EN",
    },
    {
        "question": "Quelles sont les caractéristiques de la défense française ?",
        "expected": "21",
        "language": "FR",
    },
    {
        "question": "What is Alekhine's Defense?",
        "expected": "33",
        "language": "EN",
    },
    {
        "question": "Qu'est-ce que la défense Alekhine ?",
        "expected": "33",
        "language": "FR",
    },
    {
        "question": "What is the King's Pawn Game?",
        "expected": "1",
        "language": "EN",
    },
    {
        "question": "Qu'est-ce que l'ouverture du pion roi ?",
        "expected": "1",
        "language": "FR",
    },
]


# ============================================================
# 3. RECHERCHE VECTORIELLE
# ============================================================

def search(client, model, collection, question):

    vector = model.encode(
        question,
        normalize_embeddings=True,
    ).tolist()

    results = client.search(
        collection_name=collection,
        data=[vector],
        anns_field="vector",
        limit=TOP_K,
        output_fields=["article_id"],
        search_params={
            "metric_type": "COSINE",
            "params": {},
        },
    )

    return results[0]


# ============================================================
# 4. ÉVALUATION D'UN MODÈLE
# ============================================================

def evaluate_model(client, model_config):

    model = SentenceTransformer(model_config["model"])

    collection = model_config["collection"]

    if not client.has_collection(collection):
        raise RuntimeError(
            f"Collection introuvable : {collection}"
        )

    results_by_language = {
        "EN": [],
        "FR": [],
    }

    print(f"\nCOLLECTION : {collection}")
    print("=" * 65)

    for item in QUESTIONS:

        question = item["question"]
        expected = item["expected"]
        language = item["language"]

        results = search(
            client,
            model,
            collection,
            question,
        )

        rank_found = None

        print(f"\n[{language}] {question}")
        print(f"Article attendu : {expected}")

        for rank, result in enumerate(results, start=1):

            article_id = str(
                result["entity"]["article_id"]
            )

            score = result["distance"]

            print(
                f"Rang {rank} | "
                f"Article {article_id} | "
                f"Score {score:.3f}"
            )

            if article_id == expected and rank_found is None:
                rank_found = rank

        recall = int(rank_found is not None)

        reciprocal_rank = (
            1 / rank_found
            if rank_found is not None
            else 0
        )

        results_by_language[language].append({
            "recall": recall,
            "rr": reciprocal_rank,
        })

        if rank_found:
            print(f"Article attendu trouvé au rang {rank_found}")
        else:
            print("Article attendu non trouvé")

    return results_by_language


# ============================================================
# 5. CALCUL DES MÉTRIQUES
# ============================================================

def calculate_metrics(results):

    if not results:
        raise ValueError("Aucun résultat à évaluer.")

    recall = sum(
        item["recall"] for item in results
    ) / len(results)

    mrr = sum(
        item["rr"] for item in results
    ) / len(results)

    return recall, mrr


# ============================================================
# 6. COMPARAISON FINALE
# ============================================================

def main():

    client = MilvusClient(uri=MILVUS_URI)

    evaluations = {}

    for model_name, config in MODELS.items():

        print("\n" + "#" * 65)
        print(f"ÉVALUATION : {model_name}")
        print("#" * 65)

        evaluations[model_name] = evaluate_model(
            client,
            config,
        )

    print("\n" + "=" * 75)
    print("COMPARAISON FINALE DES MODÈLES")
    print("=" * 75)

    print(
        f"{'Modèle':<22}"
        f"{'Langue':<10}"
        f"{'Recall@3':<15}"
        f"{'MRR@3':<10}"
    )

    print("-" * 75)

    for model_name, results in evaluations.items():

        for language in ["EN", "FR"]:

            recall, mrr = calculate_metrics(
                results[language]
            )

            print(
                f"{model_name:<22}"
                f"{language:<10}"
                f"{recall:<15.2%}"
                f"{mrr:<10.3f}"
            )

        all_results = (
            results["EN"] + results["FR"]
        )

        recall, mrr = calculate_metrics(all_results)

        print(
            f"{model_name:<22}"
            f"{'GLOBAL':<10}"
            f"{recall:<15.2%}"
            f"{mrr:<10.3f}"
        )

        print("-" * 75)

    print("\nCOMPARAISON TERMINÉE")


if __name__ == "__main__":
    main()