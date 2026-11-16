from fastapi import APIRouter, HTTPException, Query

from backend.app.services.youtube_service import (
    search_youtube_videos,
    YouTubeServiceError,
)


router = APIRouter(
    prefix="/videos",
    tags=["YouTube"],
)


@router.get("/{opening}")
def get_opening_videos(
    opening: str,
    max_results: int = Query(
        default=3,
        ge=1,
        le=10,
    ),
):
    """
    Recherche des vidéos explicatives
    pour une ouverture d'échecs.
    """

    if not opening.strip():
        raise HTTPException(
            status_code=422,
            detail="Le nom de l'ouverture est vide.",
        )

    try:
        videos = search_youtube_videos(
            opening=opening,
            max_results=max_results,
        )

        return {
            "opening": opening,
            "count": len(videos),
            "videos": videos,
        }

    except YouTubeServiceError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc