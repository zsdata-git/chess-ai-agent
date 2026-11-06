import chess


class FenValidationError(ValueError):
    """Erreur de validation d'une position FEN."""


def validate_fen(fen: str) -> dict:
    """
    Valide une position FEN et retourne ses informations principales.
    """

    if not isinstance(fen, str) or not fen.strip():
        raise FenValidationError("Le FEN ne peut pas être vide.")

    try:
        board = chess.Board(fen)
    except ValueError as exc:
        raise FenValidationError(
            f"Format FEN invalide : {exc}"
        ) from exc

    if not board.is_valid():
        raise FenValidationError(
            "La position FEN ne représente pas une position valide."
        )

    return {
        "fen": board.fen(),
        "turn": "white" if board.turn == chess.WHITE else "black",
        "fullmove_number": board.fullmove_number,
        "is_check": board.is_check(),
        "is_checkmate": board.is_checkmate(),
        "is_stalemate": board.is_stalemate(),
        "legal_moves_count": board.legal_moves.count(),
    }