from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.services.fen_service import (
    validate_fen,
    FenValidationError,
)


router = APIRouter(tags=["FEN"])


class FenRequest(BaseModel):
    fen: str


@router.post("/fen/validate")
def validate_fen_endpoint(request: FenRequest):
    """
    Valide une position FEN et retourne ses informations.
    """
    try:
        return validate_fen(request.fen)

    except FenValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc