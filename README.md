# Enterprise AI Customer Support Platform

[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6.svg)](https://www.typescriptlang.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-orange.svg)](https://www.langchain.com/)
[![CrewAI](https://img.shields.io/badge/CrewAI-3--Agent%20Crew-red.svg)](https://www.crewai.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)

An enterprise-grade, multi-agent AI Customer Support Platform built with **Clean Architecture**, **FastAPI**, **PostgreSQL**, **ChromaDB**, **Google Gemini LLM/VLM/Embeddings**, **LangChain**, **LangGraph**, **CrewAI**, and a modern **React + TypeScript** frontend.

---

## 💡 Key Architectural Features

1. **Clean Architecture Core**:
   - Decoupled into `Domain` (Entities, Value Objects, Domain Exceptions, Interfaces), `Application` (Use Cases, Services), `Infrastructure` (SQLAlchemy 2.x, ChromaDB, Security, Storage, Gemini API), and `Presentation` (FastAPI Routers, Pydantic DTOs, Middleware).

2. **Python 3.12 Target Compatibility**:
   - Explicitly configured with Python 3.12 target compatibility (`pyproject.toml`, `.python-version`, Docker base images `python:3.12-slim`).

3. **Multi-Agent AI Orchestration**:
   - **LangGraph Workflow**: Directed state machine (`SupportState`, `support_graph.py`) with conditional node routing (`should_run_vision`).
   - **CrewAI Specialized 3-Agent Crew**:
     - 🔍 `ResearchAgent`: Knowledge base retrieval & document analysis.
     - 👁️ `VisionAgent`: Technical error screenshot diagnosis via Gemini 1.5 Flash VLM.
     - ✍️ `SynthesisAgent`: Grounded customer response synthesis with citation match formatting.

4. **Multi-Format RAG & Hybrid Vector Search**:
   - Ingestion of PDF, DOCX, PPTX, TXT, CSV, XLSX, and Image files.
   - Vector indexing using Gemini `models/text-embedding-004` (768 dimensions) into ChromaDB.
   - Semantic Cosine Vector search & BM25 Hybrid retrieval.

5. **Security & Monitoring**:
   - OWASP Recommended HTTP Security Headers (`nosniff`, `DENY` framing, `HSTS`, `CSP`).
   - In-memory sliding window Rate Limiter middleware.
   - Liveness (`/api/v1/health/live`), Component Readiness (`/api/v1/health/ready`), and System Resource Metrics (`/api/v1/health/metrics`).

6. **Modern React + TypeScript UI**:
   - Dark mode glassmorphism UI built with custom CSS tokens, Outfit & Inter typography, Lucide Icons, and micro-animations.
   - Interactive Chat Q&A, Drag & Drop Document Ingestion, Semantic Search, Summaries/Analytics Reports, User Profile Management, and System Health Dashboard.

---

## 📁 Repository Structure

```
c:/AI Customer Support platform/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── app.py
│   │   ├── ai/
│   │   │   ├── agents/          # CrewAI Research, Vision & Synthesis Agents
│   │   │   ├── embeddings/      # Gemini Embeddings Service
│   │   │   ├── llm/             # Gemini 1.5 Pro LLM Service
│   │   │   ├── orchestration/   # LangGraph Support State Machine
│   │   │   ├── prompts/         # Anti-Hallucination & Synthesis Prompts
│   │   │   ├── rag/             # RAG Pipeline & ChromaDB Store
│   │   │   └── vlm/             # Gemini 1.5 Flash VLM Service
│   │   ├── application/services/# Auth, Chat, Document, Search, Report, User Services
│   │   ├── domain/              # Entities, Value Objects, Domain Exceptions, Interfaces
│   │   ├── infrastructure/      # SQLAlchemy 2.x, Security, Storage, Repositories
│   │   ├── monitoring/          # HealthService & Resource Metrics
│   │   ├── presentation/        # FastAPI Routers, Schemas, Security & Rate-Limit Middleware
│   │   └── workers/             # Background Document Ingestion Worker
│   └── tests/                   # 73 Unit, Integration, Worker, and E2E Tests
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── vite.config.ts
│   └── src/                     # React 18 + TypeScript SPA
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## 🚀 Quick Start Guide

### Option 1: Run via Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/mubeenah-collab/AI-customer-support-platform.git
   cd AI-customer-support-platform
   ```

2. Copy `.env.example` to `.env` and set your `GEMINI_API_KEY`:
   ```bash
   cp .env.example .env
   ```

3. Launch all services using Docker Compose:
   ```bash
   docker-compose up --build -d
   ```

4. Access the web applications:
   - **React Frontend**: `http://localhost:3000`
   - **FastAPI OpenAPI Docs**: `http://localhost:8000/docs`
   - **System Health Metrics**: `http://localhost:8000/api/v1/health/metrics`

---

### Option 2: Run Locally (Python 3.12 + Node 20)

#### 1. Backend Setup
```bash
# Verify Python 3.12
python --version  # Should display Python 3.12.x

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell

# Install dependencies
pip install -r backend/requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI dev server
python -m uvicorn backend.src.app:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 🧪 Verification & Testing

To execute all 73 automated unit, integration, RAG, CrewAI, LangGraph, API, and E2E tests:

```powershell
$env:PYTHONPATH="c:\AI Customer Support platform"; python -m pytest backend/tests/
```

To run frontend TypeScript build validation:

```powershell
cd frontend
npm run build
```

---

## 🛡️ License

Built for Enterprise AI Support Workflows. All rights reserved.
