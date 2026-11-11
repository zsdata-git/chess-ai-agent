from fastapi import FastAPI

from backend.app.api.health import router as health_router
from backend.app.api.fen import router as fen_router
from backend.app.api.lichess import router as lichess_router
from backend.app.api.stockfish import router as stockfish_router

from backend.app.api.agent import router as agent_router

from backend.app.api.vector_search import router as vector_search_router

app = FastAPI(
    title="Chess AI Agent",
    description="Agent IA conversationnel pour l'apprentissage des ouvertures aux échecs.",
    version="0.1.0",
)


app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    fen_router,
    prefix="/api/v1",
)

app.include_router(
    lichess_router,
    prefix="/api/v1",
)

app.include_router(
    stockfish_router,
    prefix="/api/v1",
)



app.include_router(
    agent_router,
    prefix="/api/v1",
)

app.include_router(vector_search_router)