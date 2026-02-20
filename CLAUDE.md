# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EDT (Explore, Discover, Travel) is a RAG-based, persona-driven travel itinerary system. Users select a group type, travel vibes, pacing, and budget, then the system retrieves POIs via pgvector cosine similarity search and assembles personalized day-by-day itineraries. No LLM is used for generation — it's a retrieval + scoring + assembly pipeline.

## Common Commands

### Backend
```bash
# Start local PostgreSQL with pgvector
docker-compose up -d

# Run migrations
alembic upgrade head

# Run the API server (dev with hot reload)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run all tests
pytest tests/ -v

# Run a single test
pytest tests/test_api.py::test_function_name -v

# Lint
ruff check . --ignore E501,F401

# Create a new migration after model changes
alembic revision --autogenerate -m "description"
```

### Flutter App (`travel_itinerary_app/`)
```bash
cd travel_itinerary_app
flutter pub get
dart run build_runner build --delete-conflicting-outputs
flutter run --dart-define=ENV=development
```

## Architecture

### Core Pipeline (RAG without LLM)
1. **Retriever** (`app/services/rag/retriever.py`) — Generates query embedding from persona + vibes + destination, runs pgvector cosine similarity
2. **Scorer** (`app/services/rag/scorer.py`) — Re-ranks POIs using persona-specific multipliers defined in `app/core/config.py` (PERSONA_DURATION_MULTIPLIERS)
3. **Assembler** (`app/services/rag/assembler.py`) — Builds day-by-day itineraries respecting pacing rules, breaks, and timing

### Multi-City Planning
`app/services/country_planner.py` handles country-level trips using city metadata from `app/core/country_config.py` (COUNTRY_DATABASE with min/max days, highlights, vibes for each city). Allocates days across cities, then calls per-city itinerary generation.

### Knowledge Graph + Vector Search
Two complementary query modes: vector search for "find POIs matching this vibe" and knowledge graph (`app/services/knowledge_graph.py`) for "what pairs well / what's nearby" using `poi_relationships` and `neighborhood_connections` tables.

### Database
- PostgreSQL 16 with pgvector extension; 384-dim embeddings from `BAAI/bge-small-en-v1.5`
- FastAPI uses async engine (`asyncpg`); Alembic uses sync engine (`psycopg2`)
- Both share the same SQLAlchemy `Base` from `app/core/database.py`

### City Intelligence (`city_intelligence/`)
Standalone scraping pipeline (Reddit, TripAdvisor, blogs) that populates travel intelligence. Can run as a Python module, CLI (`python -m city_intelligence.generator Tokyo`), standalone FastAPI service, or via the main API's `/api/v1/pipeline/intel-crawl` endpoint.

## Key Conventions

- All FastAPI route handlers must be `async def` with `await` on the async session
- New SQLAlchemy models must be imported in `alembic/env.py` for autogenerate to detect them
- Vector dimension is fixed at 384 — changing it requires recreating the `pois` table
- After modifying `@freezed` or `@riverpod` annotated Flutter files, re-run: `dart run build_runner build --delete-conflicting-outputs`
- API routes are prefixed with `/api/v1`; routers registered in `app/api/routes/__init__.py`
- CI runs tests with `DATABASE_URL=sqlite+aiosqlite:///:memory:` — keep tests compatible with SQLite
- `pytest.ini` sets `asyncio_mode = auto` — no `@pytest.mark.asyncio` needed on tests

## Tech Stack

- **Backend**: Python 3.10, FastAPI, SQLAlchemy 2.0 (async), Alembic, pgvector, sentence-transformers
- **Flutter**: Dart >=3.2, Riverpod, go_router, Dio, Freezed + json_serializable, Hive, flutter_map
- **Infra**: Docker Compose (local), Google Cloud Run (prod), GitHub Actions CI
