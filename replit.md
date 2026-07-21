# Complaint Intelligence

A RAG (retrieval-augmented generation) chatbot for exploring consumer complaints data. Built with FastAPI + React/Vite + Tailwind CSS.

## Stack

- **Backend**: FastAPI (Python 3.12), served on port 8000
- **Frontend**: React + Vite + Tailwind CSS, served on port 5173
- **Vector DB**: Pinecone
- **Embeddings**: Voyage AI (`voyage-3`)
- **LLM**: OpenRouter (primary: `meta-llama/llama-3.2-3b-instruct:free`, with fallbacks)

## How to run

Two workflows handle the app:

- **Backend** — `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- **Frontend** — `cd frontend && npm run dev`

The frontend proxies `/api` requests to the backend (port 8000) via Vite's dev proxy.

## Required secrets

Add these in Replit Secrets before the RAG features will work:

| Secret | Where to get it |
|---|---|
| `OPENROUTER_API_KEY` | https://openrouter.ai — free tier available |
| `VOYAGE_API_KEY` | https://www.voyageai.com |
| `PINECONE_API_KEY` | https://www.pinecone.io |

The app starts without them, but chat/retrieval endpoints will fail until all three are set.

## Project structure

```
backend/
  app/
    api/        — FastAPI route handlers (chat, retrieval, evaluation, health)
    config/     — Settings (pydantic-settings, reads from env)
    core/       — Logging, exceptions
    rag/        — RAG pipeline
    vector_store/ — Pinecone helpers
    evaluation/ — BLEU/ROUGE, Recall@K/MRR metrics
    optimization/ — Experiment helpers
  data/         — CSV corpus data
frontend/
  src/          — React components
```

## User preferences

_None recorded yet._
