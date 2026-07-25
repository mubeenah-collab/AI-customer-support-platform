# AI Customer Support Platform

Enterprise-Grade RAG + LangGraph + CrewAI + Gemini Customer Support Platform.

## Overview
An enterprise AI customer support platform where organizations upload knowledge base documents and customers ask questions using natural language. The system synthesizes answers using RAG, Google Gemini (LLM & Vision), ChromaDB, and CrewAI specialized agents managed by a stateful LangGraph workflow.

## Key Features
- **Clean Architecture Backend**: FastAPI, Pydantic v2, SQLAlchemy 2.x, PostgreSQL.
- **RAG & Vector Search**: ChromaDB vector store powered by Google Gemini Embeddings.
- **Stateful AI Workflow**: LangGraph state machine orchestrating Research, Vision, and Synthesis agents.
- **Specialized CrewAI Agents**: Research Agent, Vision Agent, Synthesis Agent.
- **Multimodal Support**: Gemini Vision (VLM) for processing diagrams, charts, and product images.
- **JWT Authentication**: Password hashing, refresh tokens, and role-based route protection.
- **Modern Frontend**: React, TypeScript, Tailwind CSS with streaming SSE support.

## Technology Stack
- **Backend**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic
- **Database**: PostgreSQL
- **Vector Database**: ChromaDB
- **AI/LLM**: Google Gemini LLM (`gemini-1.5-pro`), Gemini Vision (`gemini-1.5-flash`), Gemini Embeddings (`text-embedding-004`)
- **AI Frameworks**: LangChain, LangGraph, CrewAI
- **Frontend**: React, TypeScript, Tailwind CSS
- **Infrastructure**: Docker, Docker Compose

## Repository Structure
```
AI Customer Support Platform/
├── backend/
│   ├── src/
│   │   ├── app.py
│   │   ├── config/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   ├── presentation/
│   │   ├── ai/
│   │   ├── workers/
│   │   └── monitoring/
│   ├── tests/
│   └── requirements.txt
├── uploads/
│   ├── raw/
│   ├── processed/
│   └── cache/
├── .env.example
├── .gitignore
└── README.md
```

## Quick Start
1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in required environment variables.
3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Run the API server:
   ```bash
   uvicorn backend.src.app:app --reload
   ```

## License
MIT License
