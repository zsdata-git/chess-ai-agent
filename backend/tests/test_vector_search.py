"""
Tests de l'API de recherche vectorielle.
"""

from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.app.main import app


client = TestClient(app)


def test_vector_search_success():

    fake_results = [
        {
            "article_id": "3",
            "text": "The Sicilian Defense is a chess opening.",
            "url": "https://ficgs.com/wikichess_3.html",
            "score": 0.642
        }
    ]

    with patch(
        "backend.app.api.vector_search.search_wikichess",
        return_value=fake_results
    ):

        response = client.get(
            "/vector-search",
            params={
                "question": "Qu'est-ce que la défense sicilienne ?",
                "top_k": 3
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total_results"] == 1
    assert data["results"][0]["article_id"] == "3"


def test_vector_search_invalid_top_k():

    response = client.get(
        "/vector-search",
        params={
            "question": "Sicilian Defense",
            "top_k": 0
        }
    )

    assert response.status_code == 422


def test_vector_search_empty_question():

    response = client.get(
        "/vector-search",
        params={
            "question": "",
            "top_k": 3
        }
    )

    assert response.status_code == 422