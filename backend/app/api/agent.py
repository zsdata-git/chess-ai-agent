from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.agents.chess_graph import run_chess_agent
from backend.app.services.fen_service import FenValidationError
from backend.app.services.stockfish_service import StockfishServiceError


router = APIRouter(
    prefix="/agent",
    tags=["Chess Agent"],
)


class AgentRequest(BaseModel):
    fen: str
    question: str | None = None


@router.post("/analyze")
def analyze_chess_position(request: AgentRequest):
    """
    Analyse une position d'échecs avec LangGraph.

        Étapes :
        1. Validation de la position FEN.
        2. Recherche des coups théoriques avec Lichess.
        3. Analyse Stockfish si aucun coup n'est disponible.
        4. Identification d'une ouverture candidate.
        5. Recherche de connaissances dans Milvus (RAG).
        6. Recherche de vidéos pédagogiques sur YouTube.
        7. Construction de la réponse enrichie.
    """

    try:
        return run_chess_agent(
            fen=request.fen,
            question=request.question,
        )

    except FenValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except (StockfishServiceError, RuntimeError) as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc