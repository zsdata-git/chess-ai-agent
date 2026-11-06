import os
from pathlib import Path

import chess
import chess.engine
from dotenv import load_dotenv

from backend.app.services.fen_service import validate_fen


# Racine du projet
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Chargement des variables d'environnement
load_dotenv(PROJECT_ROOT / ".env")


class StockfishServiceError(Exception):
    """Erreur lors de l'utilisation du moteur Stockfish."""


def get_stockfish_path() -> Path:
    """
    Récupère et vérifie le chemin de l'exécutable Stockfish.
    """
    configured_path = os.getenv("STOCKFISH_PATH")

    if not configured_path:
        raise StockfishServiceError(
            "STOCKFISH_PATH est absent du fichier .env."
        )

    path = Path(configured_path)

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    if not path.is_file():
        raise StockfishServiceError(
            f"Exécutable Stockfish introuvable : {path}"
        )

    return path


def analyze_position(
    fen: str,
    depth: int = 12,
    multipv: int = 3,
) -> dict:
    """
    Analyse une position FEN avec Stockfish.

    Retourne :
    - la position FEN ;
    - la profondeur d'analyse demandée ;
    - le meilleur coup ;
    - l'évaluation ;
    - plusieurs coups candidats.
    """

    validate_fen(fen)

    if not isinstance(depth, int) or isinstance(depth, bool) or depth < 1:
        raise ValueError("depth doit être un entier positif.")

    if not isinstance(multipv, int) or isinstance(multipv, bool) or multipv < 1:
        raise ValueError("multipv doit être un entier positif.")

    board = chess.Board(fen)

    if board.is_game_over(claim_draw=True):
        raise StockfishServiceError(
            "La partie est terminée : aucun coup à recommander."
        )

    stockfish_path = get_stockfish_path()

    engine = None

    try:
        engine = chess.engine.SimpleEngine.popen_uci(
            str(stockfish_path),
            timeout=15.0,
        )

        results = engine.analyse(
            board,
            chess.engine.Limit(depth=depth),
            multipv=min(multipv, board.legal_moves.count()),
        )

        candidates = []

        for result in results:
            pv = result.get("pv", [])

            if not pv:
                continue

            move = pv[0]

            score = result["score"].pov(board.turn)

            candidates.append(
                {
                    "move_uci": move.uci(),
                    "move_san": board.san(move),
                    "score_cp": score.score(mate_score=100000),
                    "mate": score.mate(),
                    "depth": result.get("depth"),
                }
            )

        if not candidates:
            raise StockfishServiceError(
                "Stockfish n'a retourné aucun coup."
            )

        return {
            "fen": board.fen(),
            "requested_depth": depth,
            "best_move": candidates[0]["move_uci"],
            "evaluation_cp": candidates[0]["score_cp"],
            "candidates": candidates,
        }

    except (chess.engine.EngineError, chess.engine.EngineTerminatedError, OSError) as exc:
        raise StockfishServiceError(
            f"Erreur du moteur Stockfish : {exc}"
        ) from exc

    finally:
        if engine is not None:
            try:
                engine.quit()
            except (chess.engine.EngineError, OSError):
                pass