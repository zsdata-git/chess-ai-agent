import os

import httpx
from dotenv import load_dotenv

from backend.app.services.fen_service import validate_fen


load_dotenv()

LICHESS_URL = "https://explorer.lichess.ovh/lichess"


def get_opening_moves(fen: str) -> dict:
    """
    Récupère les statistiques des coups d'ouverture
    depuis la base de parties Lichess.

    La position FEN est validée avant l'appel API.
    """

    # 1. Validation de la position
    validate_fen(fen)

    # 2. Récupération du token
    token = os.getenv("LICHESS_API_TOKEN")

    if not token:
        raise ValueError(
            "LICHESS_API_TOKEN manquant dans le fichier .env"
        )

    # 3. Paramètres de la requête
    params = {
        "variant": "standard",
        "fen": fen,
        "speeds": "blitz,rapid,classical",
        "ratings": "1600,1800,2000,2200,2500",
        "topGames": 0,
        "recentGames": 0,
    }

    # 4. Authentification
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    # 5. Appel à l'API
    try:
        response = httpx.get(
            LICHESS_URL,
            params=params,
            headers=headers,
            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Erreur API Lichess : {exc.response.status_code}"
        ) from exc

    except httpx.RequestError as exc:
        raise RuntimeError(
            f"Connexion à Lichess impossible : {exc}"
        ) from exc

    # 6. Retour des statistiques
    return {
        "fen": fen,
        "white": data.get("white", 0),
        "draws": data.get("draws", 0),
        "black": data.get("black", 0),
        "moves": data.get("moves", []),
        "opening": data.get("opening"),
    }