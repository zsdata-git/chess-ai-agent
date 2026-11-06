from fastapi import APIRouter, HTTPException

from backend.app.services.lichess_service import get_opening_moves
from backend.app.services.fen_service import FenValidationError


router = APIRouter(tags=["Lichess"])


def fetch_opening_moves(fen: str):
    """Récupère les statistiques des coups depuis Lichess."""
    try:
        return get_opening_moves(fen)

    except FenValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Impossible de récupérer les données Lichess.",
        ) from exc


@router.get("/moves/{fen:path}")
def moves_endpoint(fen: str):
    """Endpoint demandé par OpenClassrooms."""
    return fetch_opening_moves(fen)


@router.get("/lichess/openings")
def lichess_openings_endpoint(fen: str):
    """Endpoint complémentaire utilisant un paramètre de requête."""
    return fetch_opening_moves(fen)