from fastapi import FastAPI

from backend.app.api.health import router as health_router

app = FastAPI(
    title="Chess AI Agent",
    description="Agent IA conversationnel pour l'apprentissage des ouvertures aux échecs.",
    version="0.1.0",
)

app.include_router(
    health_router,
    prefix="/api/v1",
)