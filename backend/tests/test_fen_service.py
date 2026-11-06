import pytest
import chess

from backend.app.services.fen_service import (
    validate_fen,
    FenValidationError,
)


def test_valid_initial_position():
    """Une position initiale doit être acceptée."""

    result = validate_fen(chess.STARTING_FEN)

    assert result["fen"] == chess.STARTING_FEN
    assert result["turn"] == "white"
    assert result["fullmove_number"] == 1
    assert result["is_check"] is False
    assert result["is_checkmate"] is False
    assert result["is_stalemate"] is False
    assert result["legal_moves_count"] == 20


def test_empty_fen():
    """Un FEN vide doit être rejeté."""

    with pytest.raises(FenValidationError):
        validate_fen("")


def test_invalid_fen_format():
    """Un format FEN incorrect doit être rejeté."""

    with pytest.raises(FenValidationError):
        validate_fen("position_invalide")


def test_invalid_chess_position():
    """Une position incohérente doit être rejetée."""

    invalid_fen = "8/8/8/8/8/8/8/8 w - - 0 1"

    with pytest.raises(FenValidationError):
        validate_fen(invalid_fen)


def test_black_to_move():
    """Le service doit identifier correctement le joueur."""

    board = chess.Board()
    board.push_san("e4")

    result = validate_fen(board.fen())

    assert result["turn"] == "black"
    assert result["fullmove_number"] == 1
    assert result["legal_moves_count"] == 20