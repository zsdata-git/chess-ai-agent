from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.stockfish_service import (
    analyze_position,
    StockfishServiceError,
)
from backend.app.services.fen_service import FenValidationError


router = APIRouter(tags=["Stockfish"])


class StockfishRequest(BaseModel):
    fen: str
    depth: int = Field(default=12, ge=1, le=20)


def run_stockfish_analysis(fen: str, depth: int = 12):
    """Analyse une position avec Stockfish."""
    try:
        return analyze_position(fen, depth=depth)

    except FenValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except StockfishServiceError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get("/evaluate/{fen:path}")
def evaluate_endpoint(fen: str):
    """Retourne l'évaluation Stockfish en centipawns."""
    result = run_stockfish_analysis(fen)

    return {
        "fen": result["fen"],
        "evaluation_cp": result["evaluation_cp"],
    }


@router.post("/stockfish/analyze")
def stockfish_analyze_endpoint(request: StockfishRequest):
    """Retourne une analyse détaillée de la position."""
    return run_stockfish_analysis(
        request.fen,
        depth=request.depth,
    )