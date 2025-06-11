
![Demo](/image_video/image.jpg)

# Multimodal RAG for The Batch

A **Multimodal Retrieval-Augmented Generation (RAG)** system that indexes *The Batch* news articles together with their associated images and lets you ask natural-language questions via a Gradio UI. The stack is container-first: clone, fill-in a few environment variables, and spin everything up with a single `docker compose` command.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Environment Variables](#environment-variables)
4. [Running with Docker Compose](#running-with-docker-compose)
5. [Data Ingestion Pipeline](#data-ingestion-pipeline)
6. [Technical Documentation](#technical-documentation)
    1. [Background](#background)
    2. [Data Ingestion & Pre-processing](#data-ingestion--pre-processing)
    3. [Embedding Strategy](#embedding-strategy)
    4. [Vector Store: Qdrant](#vector-store-qdrant)
    5. [Retrieval-Augmented Generation Workflow](#retrieval-augmented-generation-workflow)
    6. [Evaluation with RAGAS](#evaluation-with-ragas)
    7. [Key Findings & Future Work](#key-findings--future-work)
7. [Development Workflow (without Docker)](#development-workflow-without-docker)
8. [Troubleshooting](#troubleshooting)
9. [Clean Up](#clean-up)
10. [License](#license)

---

## Prerequisites

| Requirement | Minimum Version | Purpose |
|-------------|-----------------|---------|
| **Docker** | 24.0 (Engine v2) | Containers for the API, UI & Qdrant |
| **Docker Compose** | v2.x (built-in to Docker Desktop / CLI) | Or `docker compose` plugin |
| **Git** | any | To clone this repository |

> **Note for Windows users:** Enable WSL 2 for best performance.

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Kusm0/Multimodal_RAG.git
cd Multimodal_RAG

# Create your local environment file
cp .env.example .env
# Then open .env in your editor and fill in the placeholders (see next section)

# Start the full stack (API + UI + Qdrant)
docker compose up -d --build

# Open the Gradio UI
# Wait until the containers report "UI running on [http://0.0.0.0:7860]"
# On macOS:
open http://localhost:7860
# Or simply visit the URL in your browser
```

---

## Environment Variables

All configuration is managed in the **`.env`** file. Duplicate the template and replace the `<>` placeholders with your own values:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key (for embeddings & LLM answers). |
| `QDRANT_URL` | URL of the Qdrant instance (by defult **LEAVE IT EMPTY!**). |

**Running Qdrant in Docker vs. on a separate VM**

* **Same machine (default):** Leave `USE_EXTERNAL_QDRANT` blank or set to `false`. Docker Compose will build and start a `qdrant` service.
* **Separate VM:** Set `USE_EXTERNAL_QDRANT=true`, fill in `QDRANT_IP` (and `QDRANT_API_KEY` if needed), then comment out or remove the `qdrant:` service block in `docker-compose.override.yml`.

---

## Running with Docker Compose

```bash
# Build images (on first run)
docker compose build

# Start in detached mode
docker compose up -d

# View logs
docker compose logs -f --tail=100

# Stop containers
docker compose down
```

Services defined in **`docker-compose.yml`**:

| Service | Responsibility |
|----------|----------------|
| `ui` | Gradio web UI. |
| `qdrant` | Vector database (omitted when using an external instance). |

---

## Data Ingestion Pipeline

The script:
1.  Crawl and refresh cached HTML under `data/cached_html/`.
2.  Extract text chunks & image captions into `data/raw_jsonl/`.
3.  Generate embeddings with OpenAI.
4.  Upsert all data into Qdrant.

---

## Technical Documentation

### 1. Background
While scraping *The Batch* website, it was observed that nearly every image carries a meaningful accessibility caption (the `alt` attribute). These captions provide short, descriptive text closely tied to the surrounding article narrative. By pairing these captions with article chunks, we can build a multimodal retrieval-augmented generation (MRAG) pipeline that returns both relevant text passages and the exact images referenced in context.

### 2. Data Ingestion & Pre-processing
1.  **Crawler** (asynchronous Python): Downloads raw HTML pages to `cached_html/`.
2.  **Parser**: Implements two code paths—one for `issue_*` pages and one for regular posts—to extract the article title, cleaned body text, and each `<img>` source URL with its `alt` caption.
3.  **Image Downloader**: Stores image files in `cached_images/`, skipping inline base64 data.
4.  **JSONL Builder**: Writes a single `data/batch_multimodal.jsonl` file. Each record is either `type: text` with a text chunk, or `type: image_caption` with a caption and image metadata. Both record types share the same `article_id` and `chunk_index` to maintain their linkage.

### 3. Embedding Strategy
| Modality | Encoder | Rationale |
|----------|---------|-----------|
| Text & Captions | text-embedding-3-small (OpenAI) | A single, universal text model simplifies retrieval and keeps vector dimensions consistent. |
| Visual (for future) | CLIP ViT-L/14 | Reserved for future experiments where the signal from captions may be weak or absent. |

All vectors are created via the OpenAI Python SDK and stored together. Each payload includes the `type`, `source_url`, and the local `image_path` when applicable.

### 4. Vector Store: Qdrant
Qdrant was selected for its:
* **Typed payload filtering**, which enables fetching images belonging to the same article as a given text hit.
* **HNSW and quantization** for sub-second similarity search across over 100,000 vectors.
* **Flexible deployment**: a single Docker container for development, or the managed Qdrant Cloud for production without code changes.
* **Simple REST and gRPC APIs** that can be consumed directly from custom Python code without requiring extra frameworks.

### 5. Retrieval-Augmented Generation Workflow
1.  The user query is embedded using an OpenAI model.
2.  **Primary Search**: The top-k text chunks are retrieved from Qdrant using cosine distance.
3.  **Paired Image Retrieval**: For each returned text chunk, a secondary, filtered search retrieves nearby `image_caption` vectors that share the same `article_id`.
4.  **Answer Synthesis**: The GPT-4o-mini model receives the user's question, the retrieved text contexts, and the selected images and their captions (as tool messages) to produce an answer that references specific images.
5.  The API returns a JSON object containing the `answer`, a list of `images` (with their paths and captions), and a list of `sources`.

### 6. Evaluation with RAGAS
**Pipeline**:
1.  *Question Generation*: For each text chunk, GPT-4o-mini creates one or two question-answer pairs. Results are cached to `qa_cache.jsonl`.
2.  The MRAG pipeline answers the generated questions.
3.  `ragas.evaluate` computes `context_recall`, `context_precision`, `answer_relevancy`, and `faithfulness`.

**Latest Results (10,000 QA pairs)**: 
| Metric | Score |
|---|---|
| Context Recall | 0.925 |
| Context Precision | 0.95 |
| Answer Relevancy | 0.905 |
| Faithfulness | 0.944 |

### 7. Key Findings & Future Work
* Captions alone are often sufficient to identify the correct image, making expensive visual embeddings unnecessary in most cases.
* Qdrant's payload filtering makes text-image synchronization trivial to implement.
* RAGAS analysis highlighted a subset of images with generic captions; these are earmarked for future enhancement using CLIP-based methods.
* **Future Work**: Includes auto-captioning and visual embeddings for images, implementing a cross-encoder for re-ranking to boost answer relevancy, and building a Streamlit UI with a RAGAS metrics dashboard.

---

## Development Workflow (without Docker)

For developers who prefer to work directly on a local machine (macOS/Linux), a virtual environment setup is available:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Run the API locally
python app/main.py # This launches the Gradio Blocks interface
```

Linting, formatting, and type-checking can be run with `make`:
```bash
make lint   # ruff + isort
make format # black
make type   # mypy
```

---

## Troubleshooting
| Symptom | Potential Fix |
|---|---|
| `ImportError: No module named …` | Ensure the virtual environment is activated, or rebuild the Docker images. |
| `Connection refused :6333` | Check that the Qdrant container is running (`docker compose ps`). |
| UI shows "No relevant context found" | Run the data ingestion pipeline to populate the vector store with embeddings. |

---

## Clean Up
```bash
# Stop containers and remove volumes
docker compose down -v

# Remove all Docker images (optional)
docker image prune -a
```

---

## License
Distributed under the MIT License. See `LICENSE` for more information.
