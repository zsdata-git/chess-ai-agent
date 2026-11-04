FROM python:3.11-slim

WORKDIR /app

# Installer uv
COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /uvx /bin/

# Copier les dépendances
COPY pyproject.toml uv.lock ./

# Installer les dépendances de production
RUN uv sync --frozen --no-dev --no-install-project

# Copier le code backend
COPY backend ./backend

# Exposer le port FastAPI
EXPOSE 8000

# Démarrer l'application
CMD ["uv", "run", "--no-sync", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]