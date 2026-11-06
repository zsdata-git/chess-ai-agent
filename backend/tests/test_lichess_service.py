import httpx
import pytest
import chess

from unittest.mock import patch

from backend.app.services.lichess_service import get_opening_moves


FEN = chess.STARTING_FEN


def test_lichess_success(monkeypatch):
    """Vérifie le traitement d'une réponse API valide."""

    monkeypatch.setenv("LICHESS_API_TOKEN", "fake_test_token")

    mock_data = {
        "white": 100,
        "draws": 50,
        "black": 80,
        "moves": [
            {
                "uci": "e2e4",
                "san": "e4",
                "white": 60,
                "draws": 20,
                "black": 30,
            }
        ],
        "opening": None,
    }

    with patch("httpx.get") as mock_get:

        mock_response = mock_get.return_value
        mock_response.json.return_value = mock_data

        result = get_opening_moves(FEN)

    assert result["white"] == 100
    assert result["draws"] == 50
    assert result["black"] == 80
    assert len(result["moves"]) == 1

    assert result["moves"][0]["uci"] == "e2e4"

    # Vérification de la présence du token
    headers = mock_get.call_args.kwargs["headers"]

    assert headers["Authorization"] == "Bearer fake_test_token"


def test_lichess_missing_token(monkeypatch):
    """Vérifie le comportement sans token."""

    monkeypatch.delenv("LICHESS_API_TOKEN", raising=False)

    with pytest.raises(ValueError, match="LICHESS_API_TOKEN"):
        get_opening_moves(FEN)


def test_lichess_http_error(monkeypatch):
    """Vérifie le traitement d'une erreur HTTP 401."""

    monkeypatch.setenv("LICHESS_API_TOKEN", "fake_test_token")

    request = httpx.Request(
        "GET",
        "https://explorer.lichess.ovh/lichess",
    )

    response = httpx.Response(
        status_code=401,
        request=request,
    )

    with patch("httpx.get") as mock_get:

        mock_get.return_value = response

        with pytest.raises(RuntimeError, match="401"):
            get_opening_moves(FEN)