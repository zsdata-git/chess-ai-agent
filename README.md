# Chess AI Agent ♟️

## Présentation

Chess AI Agent est un Proof of Concept (POC) d'agent IA destiné à accompagner l'apprentissage des ouvertures aux échecs.

Ce projet est réalisé dans le cadre de la formation IA Engineer d'OpenClassrooms, à partir d'un scénario professionnel pour la Fédération Française des Échecs (FFE).

## Objectifs

L'application vise à :

* Analyser une position d'échecs au format FEN.
* Identifier les coups théoriques grâce à l'API Lichess.
* Évaluer les positions avec Stockfish.
* Fournir des explications grâce à un système RAG utilisant Milvus.
* Recommander des vidéos explicatives via l'API YouTube.
* Proposer une interface interactive avec Angular.
* Orchestrer les différents composants avec LangGraph.

## Technologies

| Technologie           | Rôle                                                    |
| ----------------------| ------------------------------------------------------- |
| Python                | Développement backend                                   |
| FastAPI               | API REST                                                |
| LangGraph             | Orchestration de l'agent                                |
| python-chess          | Validation des positions FEN                            |
| Lichess API           | Recherche de coups théoriques                           |
| Stockfish             | Évaluation des positions                                |
| YouTube Data API v3   | Recherche de vidéos sur les ouvertures                  |
| google-api-python-client | Client Python pour YouTube Data API v3               |
| pytest                | Tests automatisés                                       |
| Milvus                | Base de données vectorielle pour les articles Wikichess |
| sentence-transformers | Génération des embeddings multilingues                  |
| MongoDB               | Stockage applicatif (prévu)                             |
| Angular               | Interface utilisateur (prévue)                          |
| Docker Compose        | Conteneurisation                                        |

## État d'avancement

### Étape 1 — Environnement de développement ✅

* Initialisation du projet avec uv et Git.
* Structuration du backend FastAPI.
* Création de l'endpoint `/api/v1/healthcheck`.
* Mise en place de pytest.
* Conteneurisation du backend avec Docker.

### Étape 2 — Agent LangGraph ✅

* Validation des positions FEN avec python-chess.
* Intégration de l'API Lichess pour récupérer les coups théoriques.
* Intégration de Stockfish pour évaluer les positions.
* Création des endpoints :

  * `GET /api/v1/moves/{fen}`
  * `GET /api/v1/evaluate/{fen}`
* Développement d'un agent LangGraph :

  * Recherche des coups théoriques sur Lichess.
  * Utilisation de Stockfish lorsqu'aucun coup n'est trouvé.
* Création de l'endpoint `POST /api/v1/agent/analyze`.
* Gestion des erreurs et validation des entrées.
* Tests unitaires et tests API avec pytest.

Le routage automatique vers Stockfish a été vérifié avec des services simulés.

### Étape 3 — Intégration du RAG avec Milvus ✅

**Objectif :** enrichir l'agent LangGraph avec des connaissances
textuelles sur les ouvertures d'échecs issues de Wikichess.

#### Collecte et préparation des données

- Collecte des articles Wikichess.
- Nettoyage et prétraitement des contenus textuels.
- Préparation des données pour la recherche vectorielle.

#### Embeddings et indexation

- Génération d'embeddings avec sentence-transformers.
- Comparaison de deux modèles :
  - MiniLM anglais.
  - MiniLM multilingue.
- Évaluation avec Recall@3 et MRR@3.
- Sélection du modèle multilingue.
- Indexation des embeddings dans Milvus.

#### Recherche vectorielle

Création de l'endpoint :

`GET /vector-search`

Cet endpoint permet de rechercher les articles Wikichess
les plus pertinents pour une question donnée.

Les résultats comprennent notamment :

- L'identifiant de l'article.
- Le contenu textuel.
- L'URL de la source.
- Le score de similarité.

#### Intégration dans LangGraph

Le graphe LangGraph a été enrichi avec une recherche Wikichess.

Deux comportements sont pris en charge :

1. Avec une question :
   recherche des informations correspondant à la question.

2. Sans question :
   recherche automatique à partir de l'ouverture identifiée.

Les résultats Wikichess sont ajoutés aux informations
retournées par l'agent.

Le fonctionnement existant de Lichess et Stockfish est conservé.

#### Validation

- Tests de recherche en français et en anglais.
- Tests de l'endpoint FastAPI.
- Tests de l'intégration LangGraph.
- Vérification du fonctionnement avec et sans question.
- 35 tests automatisés réussis sur l'ensemble du backend.

**Résultat :** l'agent dispose désormais d'un enrichissement
documentaire fondé sur une recherche vectorielle dans Milvus.

### Étape 4 — Intégration de l’API YouTube ✅

**Objectif :** proposer des vidéos explicatives associées à une ouverture d’échecs et enrichir automatiquement les résultats de l’agent.

#### Service et endpoint

- Activation de YouTube Data API v3 et création d’une clé API.
- Configuration de `YOUTUBE_API_KEY` dans le fichier local `.env` et transmission au backend via Docker Compose.
- Utilisation de `google-api-python-client` pour effectuer les recherches.
- Création d’un service dédié `backend/app/services/youtube_service.py`.
- Création de la route `GET /api/v1/videos/{opening}` dans `backend/app/api/youtube.py`.
- Retour de métadonnées : identifiant, titre, description, chaîne, date de publication, URL et miniature.
- Paramètre `max_results` pour limiter le nombre de résultats (1 à 10 d’après Swagger).

#### Intégration LangGraph

- Recherche automatique de vidéos lorsque l’agent identifie une ouverture.
- Ajout des vidéos dans le champ `youtube_videos` de la réponse de `POST /api/v1/agent/analyze`.
- Présence du champ `youtube_error` pour signaler une éventuelle erreur de recherche.
- Si aucune ouverture n’est identifiée, l’agent peut retourner une liste `youtube_videos` vide sans interrompre l’analyse.

#### Vérifications réalisées

- Appel réel de l’endpoint YouTube depuis Swagger : HTTP 200 et trois vidéos retournées pour l’ouverture italienne.
- Appel réel de l’agent sur une position d’ouverture : données Lichess, passages Wikichess et trois recommandations vidéo retournées.
- Test de repli sur Stockfish avec la FEN `4k3/8/8/8/8/8/4P3/4K3 w - - 0 1` : `source: stockfish`, trois coups candidats et aucune vidéo en l’absence d’ouverture identifiée.
- **39 tests automatisés réussis** sur le backend après l’intégration.
- Reconstruction de l’image Docker réussie ; lancement du backend et réponse HTTP 200 observés lors des vérifications.

#### Limites et points de vigilance

- Les vidéos ont été jugées pertinentes **sur la base de leurs titres et métadonnées** ; leur contenu et leur qualité pédagogique n’ont pas été vérifiés.
- La gestion effective des erreurs de quota YouTube et les critères de filtrage qualitatif restent à confirmer par des tests ciblés.
- Les liens vidéo sont retournés par l’API ; la lecture intégrée (streaming) relève de l’interface à développer.
- Les résultats RAG ne sont pas toujours directement pertinents pour les positions hors ouverture ; cette amélioration est distincte de l’intégration YouTube.

**Résultat :** l’endpoint demandé et la recommandation automatique de vidéos dans LangGraph sont opérationnels dans les scénarios vérifiés.

### Prochaines étapes

- [x] Étape 1 — Environnement de développement.
- [x] Étape 2 — Développement de l'agent LangGraph.
- [x] Étape 3 — Intégration du RAG avec Milvus.
- [x] Étape 4 — Intégration de l'API YouTube.
- [ ] Étape 5 — Développement de l'interface Angular.
- [ ] Étape 6 — Packaging de l'application.
- [ ] Étape 7 — Étude de faisabilité du système d'analyse vidéo.

## Installation et exécution

### Prérequis

* Python
* uv
* Git
* Docker Desktop

### Installation

Depuis la racine du projet :

```bash
uv sync
```

### Démarrage du backend

```bash
uv run uvicorn backend.app.main:app --reload
```

Documentation Swagger :

`http://localhost:8000/docs`

### Configuration YouTube

Créer un fichier `.env` local à la racine du projet (non versionné) et renseigner notamment :

```dotenv
YOUTUBE_API_KEY=votre_cle_api_youtube
```

Ne jamais publier la clé réelle dans Git ni dans la documentation. La clé est transmise au service backend par Docker Compose.

### Exécution avec Docker Compose

```bash
docker compose up --build -d
```

Arrêt :

```bash
docker compose down
```

## Tests

Exécuter les tests automatisés :

```bash
uv run python -m pytest backend/tests -v
```

**Dernier résultat vérifié : 39 tests réussis.**

Les tests couvrent notamment :

- La validation des positions FEN.
- Les services Lichess et Stockfish.
- Les endpoints FastAPI.
- Le routage de l'agent LangGraph.
- La recherche vectorielle Wikichess.
- L'enrichissement automatique avec ou sans question.
- Les cas d'erreur.
- Le service YouTube (absence d’ouverture, clé manquante, valeur invalide de `max_results` et recherche simulée).

## Structure du projet

```text
chess-ai-agent/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   └── chess_graph.py
│   │   ├── api/
│   │   │   └── youtube.py
│   │   ├── services/
│   │   │   └── youtube_service.py
│   │   ├── rag/
│   │   ├── models/
│   │   ├── core/
│   │   └── main.py
│   ├── scripts/
│   ├── tests/
│   │   └── test_youtube_service.py
│   └── Dockerfile
├── data/
├── docs/
├── engines/
│   └── stockfish/
├── .env.example
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
└── README.md
```

## Statut

✅ Étape 1 — Environnement de développement.

✅ Étape 2 — Agent LangGraph.

✅ Étape 3 — Recherche vectorielle et enrichissement Wikichess.

✅ Étape 4 — Intégration de l'API YouTube.

⏳ Étape 5 — Interface Angular (à développer).
