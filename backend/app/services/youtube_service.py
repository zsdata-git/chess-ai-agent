import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YouTubeServiceError(Exception):
    """Erreur lors de la recherche YouTube."""


def search_youtube_videos(
    opening: str,
    max_results: int = 3,
) -> list[dict]:
    """
    Recherche des vidéos pédagogiques sur une ouverture.

    Retourne les métadonnées des vidéos :
    titre, description, chaîne, identifiant,
    URL et miniature.
    """

    opening = opening.strip()

    if not opening:
        return []

    if not 1 <= max_results <= 10:
        raise ValueError(
            "max_results doit être compris entre 1 et 10."
        )

    api_key = os.getenv("YOUTUBE_API_KEY")

    if not api_key:
        raise YouTubeServiceError(
            "La clé YOUTUBE_API_KEY est absente."
        )

    try:
        youtube = build(
            "youtube",
            "v3",
            developerKey=api_key,
            cache_discovery=False,
        )

        query = f'"{opening}" chess opening tutorial'

        response = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            videoEmbeddable="true",
            videoSyndicated="true",
            relevanceLanguage="en",
            safeSearch="strict",
            maxResults=max_results,
        ).execute()

        videos = []

        for item in response.get("items", []):
            video_id = item.get("id", {}).get(
                "videoId"
            )

            if not video_id:
                continue

            snippet = item.get("snippet", {})

            thumbnails = snippet.get(
                "thumbnails", {}
            )

            thumbnail = thumbnails.get(
                "medium", {}
            ).get("url")

            videos.append({
                "video_id": video_id,
                "title": snippet.get("title"),
                "description": snippet.get(
                    "description"
                ),
                "channel": snippet.get(
                    "channelTitle"
                ),
                "published_at": snippet.get(
                    "publishedAt"
                ),
                "url": (
                    "https://www.youtube.com/watch?v="
                    f"{video_id}"
                ),
                "thumbnail": thumbnail,
            })

        return videos

    except HttpError as exc:
        status = getattr(
            exc.resp, "status", None
        )

        if status == 403:
            raise YouTubeServiceError(
                "Accès YouTube refusé ou quota dépassé."
            ) from exc

        raise YouTubeServiceError(
            f"Erreur API YouTube : HTTP {status}"
        ) from exc

    except YouTubeServiceError:
        raise

    except Exception as exc:
        raise YouTubeServiceError(
            "Impossible de rechercher des vidéos YouTube."
        ) from exc