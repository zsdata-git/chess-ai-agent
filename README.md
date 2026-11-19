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
| Angular               | Interface utilisateur interactive                       |
| Chessground           | Affichage et interaction avec l'échiquier               |
| chess.js              | Gestion des règles et validation des coups              |
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

### Étape 5 — Développement de l'interface Angular ✅

**Objectif :** développer une interface utilisateur interactive permettant de jouer aux échecs contre l'agent IA et de consulter les recommandations et ressources pédagogiques associées aux positions analysées.

#### Développement de l'interface

- Création d'une application frontend avec Angular 22.
- Intégration d'un échiquier interactif avec Chessground.
- Utilisation de chess.js pour gérer les règles et valider les déplacements.
- Affichage et actualisation de la position au format FEN.
- Gestion des déplacements des pièces et des tours de jeu.
- Intégration d'un bouton permettant de démarrer une nouvelle partie.
- Affichage de l'état de la partie : coup joué, échec, échec et mat ou partie nulle.

#### Communication avec le backend FastAPI

- Configuration de la communication entre Angular et FastAPI.
- Utilisation d'Angular HttpClient pour effectuer les requêtes HTTP.
- Transmission des positions FEN à l'agent IA via l'endpoint `POST /api/v1/agent/analyze`.
- Récupération et affichage des réponses de l'agent.
- Application des coups retournés par l'agent lorsqu'ils sont légaux.
- Vérification de la légalité des coups avant leur application.
- Gestion des réponses contenant un coup illégal afin de préserver la cohérence de l'échiquier.

#### Affichage des recommandations

L'interface présente les informations retournées par l'agent selon la source sélectionnée.

**Lichess :**
- Affichage de l'ouverture identifiée lorsqu'elle est disponible.
- Présentation des coups théoriques proposés.
- Affichage du nombre de parties associées aux coups.
- Ajout d'explications en français indiquant les pièces à déplacer et leurs cases de départ et d'arrivée.

**Stockfish :**
- Affichage du meilleur coup retourné par le moteur.
- Présentation de son évaluation numérique.
- Ajout d'une explication du déplacement proposé.

Les recommandations sont adaptées aux informations disponibles pour la position analysée.

#### Intégration des ressources pédagogiques

**Wikichess :**
- Affichage des passages retrouvés par la recherche vectorielle dans Milvus.
- Présentation des scores de similarité.
- Ajout de liens permettant de consulter les sources originales.
- Conservation des contenus Wikichess en anglais.

**YouTube :**
- Affichage des vidéos pédagogiques retournées par l'agent.
- Présentation des miniatures, titres et chaînes.
- Ajout de liens permettant d'ouvrir les vidéos sur YouTube.

#### Vérifications réalisées

- Compilation réussie de l'application Angular.
- Vérification de l'affichage de l'échiquier et des pièces.
- Tests manuels des déplacements et de la synchronisation FEN.
- Vérification du fonctionnement du bouton « Nouvelle partie ».
- Tests des échanges entre Angular et FastAPI.
- Vérification de l'application des coups retournés par l'agent.
- Tests d'affichage des recommandations Lichess et Stockfish.
- Vérification de l'affichage des ressources Wikichess et YouTube.
- Test de plusieurs parties (notamment jusqu'à une position d'échec et mat).

#### Perspectives d'amélioration

- Les appels HTTP sont actuellement gérés dans le composant Angular ; leur extraction dans un service dédié permettrait d'améliorer la séparation des responsabilités.
- La gestion des erreurs réseau et la reprise après un échec de communication peuvent être renforcées.
- La pertinence des recommandations dépend des données retournées par les différentes sources.
- Le packaging de l'interface Angular avec Docker et Nginx a été réalisé à l'étape 6. Un déploiement sur un environnement distant pourra être envisagé ultérieurement.  

**Résultat :** une interface Angular interactive et connectée à l'agent IA est opérationnelle dans les scénarios testés. Elle permet de jouer aux échecs, de consulter les recommandations Lichess et Stockfish et d'accéder aux ressources pédagogiques Wikichess et YouTube.

### Étape 6 — Packaging et intégration avec Docker Compose ✅

**Objectif :** permettre l'exécution de l'application Chess AI Agent dans un environnement conteneurisé, en réunissant le backend FastAPI, le frontend Angular et la base vectorielle Milvus.

#### Conteneurisation des composants

- Utilisation de Docker pour isoler les composants applicatifs.
- Création d'une image Docker pour le backend FastAPI.
- Création d'une image Docker pour le frontend Angular.
- Compilation de l'application Angular et distribution de ses fichiers statiques avec Nginx.
- Utilisation de Milvus comme base de données vectorielle.
- Orchestration des services avec Docker Compose.

#### Configuration de Docker Compose

Le fichier `docker-compose.yml` définit trois services :

| Service | Rôle | Accès local |
|---|---|---|
| `backend` | API FastAPI et agent LangGraph | Port 8000 |
| `frontend` | Interface Angular distribuée par Nginx | Port 8081 |
| `milvus` | Stockage et recherche vectorielle Wikichess | Port 19531 |

Les services communiquent à travers le réseau Docker Compose.

Le backend utilise le nom du service `milvus` pour accéder à la base vectorielle depuis le réseau Docker.

Les données persistantes de Milvus sont stockées dans un répertoire local dédié, exclu du versionnement Git.

#### Intégration de l'application

L'application permet :

- D'accéder à l'interface Angular depuis un navigateur.
- De jouer une partie d'échecs contre l'agent IA.
- De transmettre les positions FEN au backend FastAPI.
- De récupérer des recommandations issues de Lichess ou Stockfish.
- D'afficher les passages Wikichess retrouvés dans Milvus.
- De consulter les vidéos pédagogiques proposées par YouTube.

#### Vérifications réalisées

Les vérifications fonctionnelles ont notamment confirmé :

- La validité de la configuration Docker Compose.
- Le démarrage des conteneurs backend, frontend et Milvus.
- L'état `healthy` du conteneur Milvus.
- L'accessibilité de Swagger sur le port 8000.
- L'accessibilité de l'interface Angular sur le port 8081.
- Le fonctionnement de l'endpoint `/api/v1/healthcheck`.
- La connexion du backend à Milvus.
- La présence de la collection `wikichess_openings_multilingual`.
- La présence de 8 documents dans cette collection.
- Le fonctionnement de l'agent LangGraph sur une position d'ouverture.
- La récupération des recommandations Lichess.
- La récupération de passages Wikichess et de vidéos YouTube.
- Le recours à Stockfish lorsque les coups théoriques ne sont pas disponibles.
- Le déroulement d'une partie interactive jusqu'à une position d'échec et mat.

Ces vérifications correspondent aux scénarios exécutés dans l'environnement local du projet.

#### Points de vigilance

- Les données vectorielles Milvus doivent être présentes ou réindexées lors d'une installation sur un nouvel environnement.
- Les clés API nécessaires aux services externes doivent être configurées localement.
- La pertinence des ressources Wikichess et YouTube dépend des résultats retournés par les services de recherche.
- La disponibilité des services externes et leurs éventuelles limites de quota peuvent influencer les résultats.

**Résultat :** une application Chess AI Agent conteneurisée, accessible localement et intégrant les composants principaux du système.

### Avancement du projet

- [x] Étape 1 — Environnement de développement.
- [x] Étape 2 — Développement de l'agent LangGraph.
- [x] Étape 3 — Intégration du RAG avec Milvus.
- [x] Étape 4 — Intégration de l'API YouTube.
- [x] Étape 5 — Développement de l'interface Angular.
- [x] Étape 6 — Packaging et intégration avec Docker Compose.
- [ ] Étape 7 — Étude de faisabilité du système d'analyse vidéo.

## Installation et démarrage

Cette section présente la procédure d'installation et de lancement de Chess AI Agent.

L'exécution avec Docker Compose est la méthode recommandée pour utiliser l'application complète.

### 1. Prérequis

Les logiciels suivants sont nécessaires :

- Git.
- Docker Desktop avec Docker Compose.
- Un navigateur web.

Pour le développement local sans Docker, Python, uv, Node.js et npm sont également nécessaires.

### 2. Récupération du projet

Cloner le dépôt Git :

```bash
git clone https://github.com/zsdata-git/chess-ai-agent.git
cd chess-ai-agent
```

### 3. Configuration des variables d'environnement

Créer un fichier `.env` à la racine du projet à partir du fichier `.env.example`.

Sous PowerShell :

```powershell
Copy-Item .env.example .env
```

Configurer les variables nécessaires, notamment :

```dotenv
LICHESS_API_TOKEN=votre_token_lichess
YOUTUBE_API_KEY=votre_cle_api_youtube
```

Les variables doivent correspondre à celles utilisées par le fichier `docker-compose.yml`.

Le fichier `.env` contient des informations sensibles et ne doit pas être ajouté au dépôt Git.

### 4. Démarrage de l'application

Démarrer Docker Desktop.

Depuis la racine du projet, exécuter :

```powershell
docker compose config --quiet
docker compose up -d --build
```

La première commande vérifie la validité de la configuration Docker Compose.

La seconde construit les images nécessaires et démarre les services en arrière-plan.

Le premier démarrage peut prendre plusieurs minutes.

### 5. Vérification des conteneurs

Afficher l'état des services :

```powershell
docker compose ps -a
```

Les services attendus sont :

- `backend`
- `frontend`
- `milvus`

Le service Milvus dispose d'un contrôle de santé Docker.

Pour consulter les journaux :

```powershell
docker compose logs --tail=50 backend
docker compose logs --tail=50 frontend
docker compose logs --tail=50 milvus
```

### 6. Accès à l'application

Une fois les services démarrés :

| Composant | Adresse |
|---|---|
| Interface Angular | `http://localhost:8081/` |
| Documentation Swagger | `http://localhost:8000/docs` |
| Vérification de santé du backend | `http://localhost:8000/api/v1/healthcheck` |

L'interface Angular permet de jouer aux échecs contre l'agent IA et de consulter les recommandations associées aux positions analysées.

Swagger permet de consulter et de tester les endpoints FastAPI.

### 7. Données vectorielles Wikichess

Le système RAG utilise Milvus pour rechercher des connaissances relatives aux ouvertures d'échecs.

La collection utilisée lors des vérifications est :

`wikichess_openings_multilingual`

Dans l'environnement de développement validé, cette collection contient 8 documents.

Les données Milvus sont persistées dans un répertoire local.

**Important :** le démarrage des conteneurs ne garantit pas, à lui seul, que la collection Wikichess existe sur une nouvelle machine.

Une procédure d'indexation doit être exécutée si les données vectorielles ne sont pas présentes.

Le projet contient notamment le script :

`backend/scripts/index_wikichess_multilingual.py`

La procédure exacte d'indexation doit être vérifiée avant une installation sur un environnement vierge.

### 8. Arrêt et redémarrage

Arrêter les services :

```powershell
docker compose down
```

Cette commande arrête et supprime les conteneurs du projet, sans supprimer automatiquement les répertoires de données persistantes.

Redémarrer :

```powershell
docker compose up -d
```

Pour reconstruire les images après modification du code :

```powershell
docker compose up -d --build
```

### 9. Développement local sans Docker

Cette méthode est facultative et principalement destinée au développement.

#### Backend FastAPI

Depuis la racine du projet :

```powershell
uv sync
uv run uvicorn backend.app.main:app --reload
```

Documentation Swagger :

`http://localhost:8000/docs`

#### Frontend Angular

Dans un second terminal :

```powershell
cd frontend
npm.cmd ci
npm.cmd start
```

Interface Angular :

`http://localhost:4200/`

Le backend doit être accessible pour que l'interface puisse communiquer avec l'agent IA.

#### Compilation Angular

Depuis le dossier `frontend` :

```powershell
npm.cmd run build
```

### 10. Dépannage

Si l'interface ne répond pas :

1. Vérifier que Docker Desktop est démarré.
2. Vérifier l'état des conteneurs avec `docker compose ps -a`.
3. Consulter les journaux du service concerné.
4. Vérifier que les ports nécessaires sont disponibles.

Si les recommandations Wikichess sont absentes :

1. Vérifier que Milvus est démarré.
2. Vérifier la connexion du backend à Milvus.
3. Vérifier la présence de la collection vectorielle.
4. Vérifier que les documents ont été indexés.

Si les vidéos YouTube sont absentes :

1. Vérifier la configuration de `YOUTUBE_API_KEY`.
2. Vérifier que l'ouverture a été identifiée.
3. Vérifier les éventuelles erreurs retournées par le service YouTube.

### 11. Sécurité et données locales

Ne pas publier :

- Les fichiers `.env` contenant les clés API.
- Les identifiants et jetons d'authentification.
- Les données locales persistantes de Milvus.
- Les fichiers temporaires et environnements virtuels.

Les fichiers nécessaires à la configuration doivent être documentés sans divulguer de secrets.


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
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── .dockerignore
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.ts
│   │   │   ├── app.html
│   │   │   ├── app.scss
│   │   │   └── app.config.ts
│   │   ├── main.ts
│   │   └── styles.scss
│   ├── package.json
│   ├── package-lock.json
│   ├── proxy.conf.json
│   └── angular.json
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

✅ Étape 5 — Interface Angular interactive et intégration avec l'agent IA.

✅ Étape 6 — Packaging et intégration avec Docker Compose.

⏳ Étape 7 — Étude de faisabilité du système d'analyse vidéo.
