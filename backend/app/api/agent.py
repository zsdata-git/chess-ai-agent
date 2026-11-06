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


@router.post("/analyze")
def analyze_chess_position(request: AgentRequest):
    """
    Analyse une position FEN avec LangGraph.

    - Recherche les coups théoriques sur Lichess.
    - Utilise Stockfish si aucun coup n'est trouvé.
    """

    try:
        return run_chess_agent(request.fen)

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