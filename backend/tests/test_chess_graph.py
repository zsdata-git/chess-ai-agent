import chess
import pytest

import importlib

graph_module = importlib.import_module(
    "backend.app.agents.chess_graph"
)

from backend.app.agents.chess_graph import (
    run_chess_agent,
    choose_source,
)
from backend.app.services.fen_service import FenValidationError


STARTING_FEN = chess.STARTING_FEN


# 1. Test du choix Lichess
def test_choose_lichess():
    state = {
        "fen": STARTING_FEN,
        "moves": [{"uci": "e2e4"}],
    }

    assert choose_source(state) == "lichess"


# 2. Test du choix Stockfish
def test_choose_stockfish():
    state = {
        "fen": STARTING_FEN,
        "moves": [],
    }

    assert choose_source(state) == "stockfish"


# 3. Test complet avec Lichess simulé
def test_agent_lichess(monkeypatch):

    def fake_lichess(fen):
        return {
            "fen": fen,
            "moves": [
                {
                    "uci": "e2e4",
                    "san": "e4",
                }
            ],
        }

    monkeypatch.setattr(
        graph_module,
        "get_opening_moves",
        fake_lichess,
    )

    result = run_chess_agent(STARTING_FEN)

    assert result["source"] == "lichess"
    assert result["moves"][0]["uci"] == "e2e4"


# 4. Test complet avec Stockfish simulé
def test_agent_stockfish(monkeypatch):

    def fake_lichess(fen):
        return {
            "fen": fen,
            "moves": [],
        }

    def fake_stockfish(fen, depth=12, multipv=3):
        return {
            "fen": fen,
            "evaluation_cp": 30,
            "best_move": "e2e4",
            "candidates": [
                {
                    "move_uci": "e2e4",
                    "move_san": "e4",
                    "score_cp": 30,
                }
            ],
        }

    monkeypatch.setattr(
        graph_module,
        "get_opening_moves",
        fake_lichess,
    )

    monkeypatch.setattr(
        graph_module,
        "analyze_position",
        fake_stockfish,
    )

    result = run_chess_agent(STARTING_FEN)

    assert result["source"] == "stockfish"
    assert result["evaluation_cp"] == 30
    assert result["best_move"] == "e2e4"


# 5. Test FEN invalide
def test_agent_invalid_fen():

    with pytest.raises(FenValidationError):
        run_chess_agent("invalid_fen")


# 6. Test erreur réseau Lichess
def test_agent_lichess_error(monkeypatch):

    def fake_lichess(fen):
        raise RuntimeError("Connexion à Lichess impossible")

    monkeypatch.setattr(
        graph_module,
        "get_opening_moves",
        fake_lichess,
    )

    with pytest.raises(RuntimeError):
        run_chess_agent(STARTING_FEN)


from unittest.mock import patch

from backend.app.agents.chess_graph import search_wikichess_context


def test_wikichess_question_priority():
    state = {
        "question": "Qu'est-ce que la défense sicilienne ?",
        "opening_name": "King's Pawn Game",
    }

    with patch(
        "backend.app.agents.chess_graph.search_wikichess",
        return_value=[],
    ) as mock_search:

        search_wikichess_context(state)

        mock_search.assert_called_once_with(
            question="Qu'est-ce que la défense sicilienne ?",
            top_k=3,
        )


def test_wikichess_automatic_opening():
    state = {
        "question": None,
        "opening_name": "King's Pawn Game",
    }

    with patch(
        "backend.app.agents.chess_graph.search_wikichess",
        return_value=[],
    ) as mock_search:

        search_wikichess_context(state)

        mock_search.assert_called_once_with(
            question="What is the King's Pawn Game chess opening?",
            top_k=3,
        )