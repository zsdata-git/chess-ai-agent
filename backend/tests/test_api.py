import chess

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)

STARTING_FEN = chess.STARTING_FEN


def test_fen_valid():
    response = client.post(
        "/api/v1/fen/validate",
        json={"fen": STARTING_FEN},
    )

    assert response.status_code == 200
    assert response.json()["fen"] == STARTING_FEN
    assert response.json()["turn"] == "white"


def test_fen_invalid():
    response = client.post(
        "/api/v1/fen/validate",
        json={"fen": "invalid_fen"},
    )

    assert response.status_code == 422


def test_lichess_success(monkeypatch):

    fake_result = {
        "fen": STARTING_FEN,
        "white": 100,
        "draws": 20,
        "black": 80,
        "moves": [],
    }

    monkeypatch.setattr(
        "backend.app.api.lichess.get_opening_moves",
        lambda fen: fake_result,
    )

    response = client.get(
        "/api/v1/lichess/openings",
        params={"fen": STARTING_FEN},
    )

    assert response.status_code == 200
    assert response.json()["white"] == 100


def test_stockfish_success(monkeypatch):

    fake_result = {
        "fen": STARTING_FEN,
        "best_move": "e2e4",
        "evaluation_cp": 30,
        "candidates": [],
    }

    monkeypatch.setattr(
        "backend.app.api.stockfish.analyze_position",
        lambda fen, depth: fake_result,
    )

    response = client.post(
        "/api/v1/stockfish/analyze",
        json={
            "fen": STARTING_FEN,
            "depth": 12,
        },
    )

    assert response.status_code == 200
    assert response.json()["best_move"] == "e2e4"


def test_stockfish_invalid_depth():
    response = client.post(
        "/api/v1/stockfish/analyze",
        json={
            "fen": STARTING_FEN,
            "depth": -1,
        },
    )

    assert response.status_code == 422


# ============================================================
# Tests des endpoints demandés dans les consignes
# ============================================================


def test_moves_success(monkeypatch):
    """Vérifie la récupération des coups depuis Lichess."""

    fake_result = {
        "fen": STARTING_FEN,
        "white": 100,
        "draws": 20,
        "black": 80,
        "moves": [
            {
                "uci": "e2e4",
                "san": "e4",
                "averageRating": 1800,
                "white": 50,
                "draws": 10,
                "black": 40,
            }
        ],
    }

    monkeypatch.setattr(
        "backend.app.api.lichess.get_opening_moves",
        lambda fen: fake_result,
    )

    response = client.get(
        f"/api/v1/moves/{STARTING_FEN}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["fen"] == STARTING_FEN
    assert data["moves"][0]["uci"] == "e2e4"


def test_evaluate_success(monkeypatch):
    """Vérifie l'évaluation d'une position par Stockfish."""

    fake_result = {
        "fen": STARTING_FEN,
        "requested_depth": 12,
        "best_move": "e2e4",
        "evaluation_cp": 30,
        "candidates": [],
    }

    monkeypatch.setattr(
        "backend.app.api.stockfish.analyze_position",
        lambda fen, depth: fake_result,
    )

    response = client.get(
        f"/api/v1/evaluate/{STARTING_FEN}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["fen"] == STARTING_FEN
    assert data["evaluation_cp"] == 30


def test_moves_invalid_fen():
    """Vérifie le rejet d'une position FEN invalide."""

    response = client.get(
        "/api/v1/moves/invalid_fen"
    )

    assert response.status_code == 422


def test_evaluate_invalid_fen():
    """Vérifie le rejet d'une position FEN invalide."""

    response = client.get(
        "/api/v1/evaluate/invalid_fen"
    )

    assert response.status_code == 422