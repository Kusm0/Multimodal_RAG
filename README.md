# Multimodal RAG for The Batch

A **Multimodal Retrieval‑Augmented Generation (RAG)** system that indexes *The Batch* news articles together with their associated images and lets you ask natural–language questions via a Gradio UI. The stack is container‑first: clone, fill‑in a few environment variables, and spin everything up with a single `docker compose` command.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Environment Variables](#environment-variables)
4. [Running with Docker Compose](#running-with-docker-compose)
5. [Data Ingestion Pipeline](#data-ingestion-pipeline)
6. [Development Workflow (without Docker)](#development-workflow-without-docker)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Clean Up](#clean-up)
10. [License](#license)

---

## Prerequisites

| Requirement        | Minimum Version                         | Why                                 |
| ------------------ | --------------------------------------- | ----------------------------------- |
| **Docker**         | 24.0 (Engine v2)                        | Containers for the API, UI & Qdrant |
| **Docker Compose** | v2.x (built‑in to Docker Desktop / CLI) | Or `docker compose` plugin          |
| **Git**            | any                                     | Clone this repo                     |

> **Tip for Windows users:** enable WSL 2 for best performance.

---

## Quick Start

```bash
# 1️⃣ Clone the repository
$ git clone https://github.com/your‑org/MRAG_The_Batch.git
$ cd MRAG_The_Batch

# 2️⃣ Create your local ENV file
$ cp .env.example .env
# …then open .env in your editor and fill in the placeholders (see next section)

# 3️⃣ Spin up the full stack (API + UI + Qdrant)
$ docker compose up -d --build

# 4️⃣ Open the Gradio UI
# Wait until the containers report "🚀  UI running on http://0.0.0.0:7860"
$ open http://localhost:7860  # macOS
# or simply visit the URL in your browser
```

---

## Environment Variables

All configuration lives in \`\`. Duplicate the template and replace the `<>` placeholders with your own values:

```bash
cp .env.example .env
```

| Variable              | Description                                                |
| --------------------- | ---------------------------------------------------------- |
| `OPENAI_API_KEY`      | Your OpenAI API key (for embeddings & LLM answers)         |
| `QDRANT_URL`          | URL of the Qdrant instance (default: `http://qdrant:6333`) |
| `PORT`                | Host port for the Gradio UI (defaults to `7860`)           |

**Running Qdrant in Docker vs on a separate VM**

* **Same machine (default):** leave `USE_EXTERNAL_QDRANT` blank/`false`. Docker Compose will build and start a `qdrant` service.
* **Separate VM:** set `USE_EXTERNAL_QDRANT=true`, fill `QDRANT_IP` (and `QDRANT_API_KEY` if needed), then *comment out* or remove the `qdrant:` service block in `docker-compose.override.yml`.

---

## Running with Docker Compose

```bash
# Build images (first run only)
docker compose build

# Start in detached mode
docker compose up -d

# View logs
docker compose logs -f --tail=100

# Stop containers
docker compose down
```

Services defined in \`\`:

| Service  | Responsibility                                         |
| -------- | ------------------------------------------------------ |
| `ui`     | Gradio web UI                                          |
| `qdrant` | Vector database (omitted when using external instance) |

---

## Data Ingestion Pipeline

After the containers are running, seed the vector store with *The Batch* articles and images:

```bash
# From the host
docker compose exec api python scripts/pipeline/sync_run_pipeline.py
# or via make (alias)
make sync-data
```

The script will:

1. Crawl/refresh cached HTML under `data/cached_html/`.
2. Extract text chunks & image captions → `data/raw_jsonl/`.
3. Generate embeddings with OpenAI & CLIP.
4. Upsert everything into Qdrant.

---

## Development Workflow (without Docker)

Prefer working directly on your Mac/Linux laptop? Use the virtual‑env setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Load ENV vars
export $(grep -v '^#' .env | xargs)

# Run the API locally
python app/main.py  # Launches Gradio Blocks
```

Linting, formatting & type‑checking:

```bash
make lint   # ruff + isort
make format # black
make type   # mypy
```

---

## Troubleshooting

| Symptom                              | Fix                                                               |
| ------------------------------------ | ----------------------------------------------------------------- |
| `ImportError: No module named …`     | Ensure the virtual‑env is activated or rebuild the Docker images. |
| `Connection refused :6333`           | Check that Qdrant is running ( `docker compose ps` ).             |
| UI shows "No relevant context found" | Try another question.                |

---

## Clean Up

```bash
# Stop containers & remove volumes
docker compose down -v

# Remove all Docker images (optional)
docker image prune -a
```

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
