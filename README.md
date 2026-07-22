# Complaint Intelligence

An end-to-end **Retrieval-Augmented Generation (RAG)** chatbot for exploring and analyzing consumer complaints using semantic search and Large Language Models.

The system combines **React**, **FastAPI**, **Pinecone**, **Voyage AI Embeddings**, and **OpenRouter LLMs** to deliver accurate, context-aware answers from complaint data.

---

# Features

- Semantic search over consumer complaints
- Retrieval-Augmented Generation (RAG)
- FastAPI REST API
- Modern React + Vite frontend
- Pinecone vector database
- Voyage AI embeddings
- OpenRouter LLM with automatic fallback models
- Evaluation metrics (BLEU, ROUGE, Recall@K, MRR)
- Modular architecture for experimentation and optimization

---

# Tech Stack

| Layer | Technology |
|---------|------------|
| Frontend | React + Vite + Tailwind CSS |
| Backend | FastAPI (Python 3.12) |
| Vector Database | Pinecone |
| Embedding Model | Voyage AI (`voyage-3`) |
| LLM Provider | OpenRouter |
| Primary Model | GPT-OSS 20B |
| Fallback Models | Automatic OpenRouter fallback |
| Evaluation | BLEU, ROUGE, Recall@K, MRR |

---

# RAG Architecture

```
                    User
                      │
                      ▼
      Frontend (React + Vite)
                      │
                      ▼
          FastAPI Backend API
                      │
                      ▼
              Query Processing
                      │
                      ▼
               Voyage Embedding
                      │
                      ▼
                  Pinecone
             Vector Search (Top K)
                      │
                      ▼
              Top 3 Retrieved Chunks
                      │
                      ▼
               Prompt Builder
                      │
                      ▼
             OpenRouter API
                      │
                      ▼
                GPT-OSS 20B
                      │
          (Automatic Fallback)
                      │
                      ▼
              Generated Answer
                      │
                      ▼
        Frontend (React + Vite)
```

---

# Request Flow

```
User Question
      │
      ▼
React Frontend
      │
      ▼
FastAPI Backend
      │
      ▼
Generate Embedding
      │
      ▼
Search Pinecone
      │
      ▼
Retrieve Top 3 Chunks
      │
      ▼
Build Prompt
      │
      ▼
GPT-OSS 20B
      │
      ▼
Fallback Models (if needed)
      │
      ▼
Final Response
```

---

# Project Structure

```
Complaint-Intelligence/
│
├── backend/
│   │
│   ├── app/
│   │   ├── api/
│   │   ├── config/
│   │   ├── core/
│   │   ├── rag/
│   │   ├── vector_store/
│   │   ├── evaluation/
│   │   └── optimization/
│   │
│   ├── data/
│   ├── requirements.txt
│   └── main.py
│
├── frontend/
│   │
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── utils/
│   │   └── App.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

# Running the Project

## Backend

```bash
cd backend

uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
```

Backend URL

```
http://localhost:8000
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend URL

```
http://localhost:5173
```

The frontend automatically proxies all `/api` requests to the FastAPI backend.

---

# Environment Variables

Create a `.env` file (or Replit Secrets) with:

```env
OPENROUTER_API_KEY=your_key

VOYAGE_API_KEY=your_key

PINECONE_API_KEY=your_key
```

Without these keys, the application starts successfully but RAG retrieval and chat endpoints will not function.

---

# Retrieval Pipeline

```
User Query
      │
      ▼
Voyage Embedding
      │
      ▼
Pinecone Similarity Search
      │
      ▼
Top 3 Chunks
      │
      ▼
Prompt Builder
      │
      ▼
GPT-OSS 20B
      │
      ▼
Generated Answer
```

---

# Evaluation

The project supports:

- BLEU
- ROUGE
- Recall@K
- Mean Reciprocal Rank (MRR)

for evaluating retrieval quality and generated responses.

---

# Models

## Embedding

- Voyage AI
  - `voyage-3`

## Primary LLM

- GPT-OSS 20B

## Fallback Models

If the primary model is unavailable, the backend automatically switches to predefined OpenRouter fallback models.

---

# API Overview

| Endpoint | Description |
|-----------|-------------|
| `/api/chat` | Chat with the RAG assistant |
| `/api/retrieve` | Retrieve relevant complaint chunks |
| `/api/evaluate` | Run evaluation metrics |
| `/health` | Health check |

---

# System Workflow

```
Question
    │
    ▼
Frontend (React + Vite)
    │
    ▼
FastAPI
    │
    ▼
Retriever
    │
    ▼
Pinecone
    │
    ▼
Top 3 Chunks
    │
    ▼
Prompt Builder
    │
    ▼
OpenRouter
    │
    ▼
GPT-OSS 20B
    │
Fallback Models
    │
    ▼
Answer
```
