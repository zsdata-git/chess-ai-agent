"""
API de recherche vectorielle Wikichess.

Permet de rechercher des passages pertinents
en français ou en anglais.
"""

from fastapi import APIRouter, HTTPException, Query

from backend.app.services.vector_search_service import (
    search_wikichess
)


router = APIRouter(
    tags=["Vector Search"]
)


@router.get(
    "/vector-search",
    summary="Recherche vectorielle multilingue",
    description=(
        "Recherche les passages Wikichess les plus pertinents "
        "à partir d'une question en français ou en anglais."
    )
)
def vector_search(
    question: str = Query(
        ...,
        min_length=3,
        description="Question sur une ouverture d'échecs"
    ),
    top_k: int = Query(
        3,
        ge=1,
        le=10,
        description="Nombre de passages à retourner"
    )
):

    try:

        results = search_wikichess(
            question=question,
            top_k=top_k
        )

        return {
            "question": question,
            "total_results": len(results),
            "results": results
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la recherche vectorielle."
        ) from exc