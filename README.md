# Chess AI Agent ♟️

## Présentation

Chess AI Agent est un Proof of Concept (POC) d'agent IA conversationnel destiné à accompagner l'apprentissage des ouvertures aux échecs.

Ce projet est réalisé dans le cadre de la formation IA Engineer d'OpenClassrooms, à partir d'un scénario professionnel pour la Fédération Française des Échecs (FFE).

## Objectifs

L'application devra permettre de :

- Analyser une position d'échecs au format FEN.
- Identifier les coups théoriques grâce à l'API Lichess.
- Évaluer les positions avec Stockfish.
- Fournir des explications grâce à un système RAG utilisant Milvus.
- Recommander des vidéos explicatives via l'API YouTube.
- Interagir avec un échiquier Angular.
- Orchestrer les différents outils avec LangGraph.

## Architecture cible

| Technologie | Rôle |
|---|---|
| Python | Développement backend |
| FastAPI | API REST |
| LangGraph | Orchestration de l'agent IA |
| Mistral | Modèle de langage envisagé |
| Lichess API | Recherche de coups théoriques |
| Stockfish | Analyse échiquéenne |
| Milvus | Recherche vectorielle |
| MongoDB | Stockage applicatif envisagé |
| Angular | Interface utilisateur |
| Docker Compose | Orchestration des services |

## État d'avancement

### Étape 1 — Environnement de développement

- [x] Initialisation du dépôt Git
- [x] Initialisation du projet Python avec uv
- [x] Création de la structure du projet
- [x] Développement d'un backend FastAPI minimal
- [x] Création de l'endpoint `/api/v1/healthcheck`
- [x] Test automatisé avec pytest
- [x] Conteneurisation du backend
- [x] Exécution avec Docker Compose

### Étapes suivantes

- [ ] Développement de l'agent LangGraph
- [ ] Intégration Lichess et Stockfish
- [ ] Intégration du RAG avec Milvus
- [ ] Intégration de l'API YouTube
- [ ] Développement de l'interface Angular
- [ ] Conteneurisation complète
- [ ] Étude de faisabilité MCP

## Installation

### Prérequis

- Git
- Docker Desktop avec Docker Compose

### Démarrage

Depuis la racine du projet :

```bash
docker compose up --build -d
```

### Vérification

Accéder à :

- API : http://localhost:8000/api/v1/healthcheck
- Swagger : http://localhost:8000/docs

Réponse attendue :

```json
{
  "status": "ok"
}
```

### Arrêt

```bash
docker compose down
```

Cette commande arrête et supprime les conteneurs du projet, sans supprimer les volumes persistants.

## Tests

Pour exécuter les tests localement :

```bash
uv sync
uv run python -m pytest backend/tests -v
```

Résultat actuellement vérifié :

```text
1 passed
```

## Structure du projet

```text
chess-ai-agent/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── services/
│   │   ├── rag/
│   │   ├── models/
│   │   ├── core/
│   │   └── main.py
│   ├── scripts/
│   ├── tests/
│   └── Dockerfile
├── frontend/
├── data/
├── docs/
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
└── README.md
```

## Documentation

La documentation sera enrichie progressivement avec :

- L'architecture LangGraph.
- Les choix techniques.
- Les tests et validations.
- Les instructions de démonstration.
- L'étude de faisabilité MCP.

## Statut

🚧 Projet en cours de développement.