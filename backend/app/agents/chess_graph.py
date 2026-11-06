from typing import TypedDict, Literal

from langgraph.graph import StateGraph, START, END

from backend.app.services.fen_service import validate_fen
from backend.app.services.lichess_service import get_opening_moves
from backend.app.services.stockfish_service import analyze_position


class ChessState(TypedDict, total=False):
    fen: str
    source: str
    moves: list
    evaluation_cp: int | None
    best_move: str | None
    result: dict


# 1. Validation de la position FEN
def validate_position(state: ChessState) -> dict:
    validated = validate_fen(state["fen"])

    return {
        "fen": validated["fen"]
    }


# 2. Recherche des coups théoriques sur Lichess
def search_lichess(state: ChessState) -> dict:
    data = get_opening_moves(state["fen"])

    return {
        "moves": data.get("moves", [])
    }


# 3. Choix de la source
def choose_source(
    state: ChessState,
) -> Literal["lichess", "stockfish"]:

    if state.get("moves"):
        return "lichess"

    return "stockfish"


# 4. Résultat Lichess
def lichess_result(state: ChessState) -> dict:
    return {
        "source": "lichess",
        "result": {
            "fen": state["fen"],
            "source": "lichess",
            "moves": state["moves"],
        },
    }


# 5. Analyse Stockfish
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


# 6. Construction du graphe
builder = StateGraph(ChessState)

builder.add_node("validate_fen", validate_position)
builder.add_node("search_lichess", search_lichess)
builder.add_node("lichess_result", lichess_result)
builder.add_node("stockfish_analysis", stockfish_analysis)

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

builder.add_edge("lichess_result", END)
builder.add_edge("stockfish_analysis", END)

chess_graph = builder.compile()


# 7. Fonction principale de l'agent
def run_chess_agent(fen: str) -> dict:
    state = chess_graph.invoke({"fen": fen})

    return state["result"]