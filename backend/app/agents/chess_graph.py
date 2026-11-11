from typing import TypedDict, Literal

from langgraph.graph import StateGraph, START, END

from backend.app.services.fen_service import validate_fen
from backend.app.services.lichess_service import get_opening_moves
from backend.app.services.stockfish_service import analyze_position
from backend.app.services.vector_search_service import search_wikichess


# 1. État partagé du graphe
class ChessState(TypedDict, total=False):
    fen: str
    question: str | None
    source: str
    moves: list
    evaluation_cp: int | None
    best_move: str | None
    wikichess_context: list
    result: dict
    opening_name: str | None


# 2. Validation FEN
def validate_position(state: ChessState) -> dict:
    validated = validate_fen(state["fen"])

    return {
        "fen": validated["fen"]
    }


# 3. Recherche des coups théoriques
def search_lichess(state: ChessState) -> dict:
    data = get_opening_moves(state["fen"])

    return {
        "moves": data.get("moves", [])
    }


# 4. Choix de la source
def choose_source(
    state: ChessState,
) -> Literal["lichess", "stockfish"]:

    if state.get("moves"):
        return "lichess"

    return "stockfish"


# 5. Résultat Lichess
def lichess_result(state: ChessState) -> dict:
    return {
        "source": "lichess",
        "result": {
            "fen": state["fen"],
            "source": "lichess",
            "moves": state["moves"],
        },
    }


# 6. Analyse Stockfish
def stockfish_analysis(state: ChessState) -> dict:
    analysis = analyze_position(
        fen=state["fen"],
        depth=12,
        multipv=3,
    )

    return {
        "source": "stockfish",
        "evaluation_cp": analysis["evaluation_cp"],
        "best_move": analysis["best_move"],
        "result": {
            "fen": state["fen"],
            "source": "stockfish",
            "evaluation_cp": analysis["evaluation_cp"],
            "best_move": analysis["best_move"],
            "candidates": analysis["candidates"],
        },
    }


# 7. Recherche contextuelle Wikichess

def identify_opening(state: ChessState) -> dict:
    """
    Identifier une ouverture à partir des résultats Lichess.

    Attention : le nom provient des métadonnées d'un coup
    proposé par Lichess, et non nécessairement de la
    position FEN elle-même.
    """

    for move in state.get("moves", []):
        opening = move.get("opening") or {}

        name = opening.get("name")

        if name:
            return {"opening_name": name}

    return {"opening_name": None}


def search_wikichess_context(state: ChessState) -> dict:
    """
    Recherche contextuelle dans Milvus.

    Priorité :
    1. Question explicite de l'utilisateur.
    2. Ouverture candidate identifiée via Lichess.
    3. Aucun contexte si les deux sont absents.
    """

    question = state.get("question")
    opening_name = state.get("opening_name")

    if question and question.strip():
        search_query = question.strip()

    elif opening_name:
        search_query = f"What is the {opening_name} chess opening?"

    else:
        return {"wikichess_context": []}

    passages = search_wikichess(
        question=search_query,
        top_k=3,
    )

    return {"wikichess_context": passages}


# 8. Construction du résultat enrichi
def enrich_result(state: ChessState) -> dict:

    result = state["result"].copy()

    result["opening_name"] = state.get("opening_name")

    result["wikichess_context"] = state.get(
        "wikichess_context", []
    )

    return {"result": result}


# 9. Construction du graphe
builder = StateGraph(ChessState)

builder.add_node("validate_fen", validate_position)
builder.add_node("search_lichess", search_lichess)
builder.add_node("lichess_result", lichess_result)
builder.add_node("stockfish_analysis", stockfish_analysis)
builder.add_node("search_wikichess", search_wikichess_context)
builder.add_node("enrich_result", enrich_result)
builder.add_node("identify_opening", identify_opening)

builder.add_edge(START, "validate_fen")
builder.add_edge("validate_fen", "search_lichess")

builder.add_conditional_edges(
    "search_lichess",
    choose_source,
    {
        "lichess": "lichess_result",
        "stockfish": "stockfish_analysis",
    },
)

builder.add_edge("lichess_result", "identify_opening")
builder.add_edge("stockfish_analysis", "identify_opening")

builder.add_edge("identify_opening", "search_wikichess")

builder.add_edge("search_wikichess", "enrich_result")
builder.add_edge("enrich_result", END)

chess_graph = builder.compile()


# 10. Fonction principale
def run_chess_agent(
    fen: str,
    question: str | None = None,
) -> dict:

    state = chess_graph.invoke({
        "fen": fen,
        "question": question,
    })

    return state["result"]