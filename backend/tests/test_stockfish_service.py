import chess
import pytest

from backend.app.services.stockfish_service import (
    analyze_position,
    get_stockfish_path,
    StockfishServiceError,
)


def test_stockfish_executable_exists():
    """Vérifie que l'exécutable Stockfish est disponible."""
    assert get_stockfish_path().is_file()


def test_stockfish_initial_position():
    """Vérifie une analyse réelle de la position initiale."""
    result = analyze_position(
        chess.STARTING_FEN,
        depth=8,
        multipv=2,
    )

    assert result["fen"] == chess.STARTING_FEN
    assert result["requested_depth"] == 8

    board = chess.Board(chess.STARTING_FEN)

    best_move = chess.Move.from_uci(result["best_move"])

    assert best_move in board.legal_moves

    assert len(result["candidates"]) >= 1
    assert len(result["candidates"]) <= 2

    assert isinstance(result["evaluation_cp"], int)


def test_stockfish_invalid_fen():
    """Vérifie le rejet d'une position FEN invalide."""
    with pytest.raises(ValueError):
        analyze_position("invalid_fen")


def test_stockfish_invalid_depth():
    """Vérifie le rejet d'une profondeur invalide."""
    with pytest.raises(ValueError):
        analyze_position(chess.STARTING_FEN, depth=0)


def test_stockfish_invalid_multipv():
    """Vérifie le rejet d'un nombre de candidats invalide."""
    with pytest.raises(ValueError):
        analyze_position(chess.STARTING_FEN, multipv=0)


def test_stockfish_missing_executable(monkeypatch):
    """Vérifie la gestion d'un exécutable introuvable."""
    monkeypatch.setenv(
        "STOCKFISH_PATH",
        "engines/stockfish/inexistant.exe",
    )

    with pytest.raises(StockfishServiceError):
        analyze_position(chess.STARTING_FEN, depth=4)