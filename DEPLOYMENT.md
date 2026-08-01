# Production Deployment Guide: AI Research Copilot / Platform

This guide provides end-to-end instructions for deploying the **AI Research Copilot / AI Customer Support Platform** to production using **Vercel** (Frontend), **Render** (Backend & PostgreSQL), **ChromaDB** (Persistent Disk), and **Google Gemini API**.

---

## 🏗️ Deployment Architecture

```
                                  ┌───────────────────────────┐
                                  │      Vercel (Frontend)    │
                                  │  Vite SPA + React Router  │
                                  └─────────────┬─────────────┘
                                                │
                                       HTTPS API Requests
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Render Web Service (FastAPI Backend)                                                   │
│                                                                                        │
│  ┌────────────────────┐    ┌────────────────────┐    ┌──────────────────────────────┐  │
│  │ FastAPI App        │    │ Alembic Migrations │    │ Security & CORS Middleware   │  │
│  │ (Python 3.12)      │    │ (Startup Hook)     │    │ (JWT, bcrypt, Rate Limiting) │  │
│  └─────────┬──────────┘    └────────────────────┘    └──────────────────────────────┘  │
│            │                                                                           │
│            ├─── Database ORM ──────────► Render PostgreSQL Database                     │
│            │                                                                           │
│            ├─── Vectors & Uploads ─────► Render Persistent Disk (/var/data)            │
│            │                             ├── /var/data/chroma (ChromaDB)               │
│            │                             └── /var/data/uploads (Uploaded PDFs)         │
│            │                                                                           │
│            └─── LLM & RAG Engine ──────► Google AI Studio (Gemini 2.5 Pro & Embeddings)│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Deploy PostgreSQL on Render

1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** $\rightarrow$ **PostgreSQL**.
3. Configure the database details:
   - **Name**: `ai-research-copilot-db`
   - **Database**: `customer_support_db`
   - **User**: `postgres`
   - **Region**: Choose region closest to your users (e.g. *Oregon, USA* or *Frankfurt, EU*).
   - **Instance Type**: **Free** (or Starter for production uptime).
4. Click **Create Database**.
5. Once created, copy the **Internal Database URL** (e.g., `postgres://postgres:password@dpg-xxxx-a.oregon-postgres.render.com/customer_support_db`).

---

## Step 2: Deploy Backend Web Service on Render

### Option A: Automatic Blueprint Deployment (Recommended)
1. Push your repository to GitHub.
2. In Render Dashboard, click **New +** $\rightarrow$ **Blueprint**.
3. Connect your GitHub repository.
4. Render will auto-detect `render.yaml` and prompt you to create:
   - **PostgreSQL Database**: `ai-research-copilot-db`
   - **Web Service**: `ai-research-copilot-backend`
   - **Persistent Disk**: Mounted at `/var/data` (10 GB)

### Option B: Manual Web Service Creation
1. Click **New +** $\rightarrow$ **Web Service**.
2. Connect your GitHub repository.
3. Configure the Web Service settings:
   - **Name**: `ai-research-copilot-backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `alembic upgrade head && uvicorn backend.src.app:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
4. Add a **Persistent Disk** under **Disks**:
   - **Name**: `chroma-data`
   - **Mount Path**: `/var/data`
   - **Size**: `10 GB`

---

## Step 3: Configure Environment Variables

In your Render Backend Web Service settings, navigate to **Environment** and set the following variables:

| Variable Name | Value / Description | Example |
| :--- | :--- | :--- |
| `APP_ENV` | `production` | `production` |
| `DEBUG` | `false` | `false` |
| `PYTHONPATH` | `.` | `.` |
| `SECRET_KEY` | 64-character random hex string | `openssl rand -hex 32` |
| `DATABASE_URL` | Render Internal Database URL | `postgres://postgres:...@dpg-xxx:5432/customer_support_db` |
| `GOOGLE_API_KEY` | Google AI Studio API Key | `AIzaSy...` |
| `GEMINI_LLM_MODEL` | Gemini LLM Model | `gemini-2.5-pro` |
| `GEMINI_EMBEDDING_MODEL` | Gemini Embeddings Model | `models/text-embedding-004` |
| `CHROMA_USE_HTTP_CLIENT` | `false` (uses PersistentClient) | `false` |
| `CHROMA_PERSIST_DIRECTORY` | `/var/data/chroma` | `/var/data/chroma` |
| `UPLOAD_BASE_DIR` | `/var/data/uploads` | `/var/data/uploads` |
| `ALLOWED_ORIGINS` | Your Vercel frontend URL | `https://ai-research-copilot.vercel.app` |

---

## Step 4: Deploy Frontend on Vercel

1. Log into [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** $\rightarrow$ **Project**.
3. Import your GitHub repository.
4. Configure Project Settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend` (or select `./` if deploying root with root `vercel.json`)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Expand **Environment Variables** and add:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://<your-render-backend-name>.onrender.com/api/v1`
6. Click **Deploy**.

---

## Step 5: Verify Production Deployment

Once both services are deployed, perform the verification checklist:

### 1. Health Probe Verification
```bash
curl -i https://<your-render-backend-name>.onrender.com/health
```
**Expected Output:**
```json
{
  "status": "healthy",
  "service": "AI Customer Support Platform API",
  "version": "1.0.0"
}
```

Check detailed readiness status (Database + ChromaDB):
```bash
curl -i https://<your-render-backend-name>.onrender.com/api/v1/health/ready
```

### 2. Feature Verification Matrix

- [x] **Registration**: Register new user account (`POST /api/v1/auth/register`)
- [x] **Login**: Authenticate user and receive JWT bearer tokens (`POST /api/v1/auth/login`)
- [x] **JWT Auth**: Access protected endpoints using `Authorization: Bearer <token>`
- [x] **PDF Upload**: Upload research PDFs (`POST /api/v1/documents/upload`)
- [x] **PDF Processing**: Automatic text extraction, page parsing, and chunking
- [x] **Gemini Embeddings**: Vector embeddings generated via `models/text-embedding-004`
- [x] **ChromaDB Persistence**: Vectors saved to persistent disk at `/var/data/chroma`
- [x] **RAG Retrieval**: Perform semantic search (`POST /api/v1/search`)
- [x] **AI Chat**: Multi-turn research copilot chat with LangGraph (`POST /api/v1/chat`)
- [x] **Source Citations**: Inline references with exact page numbers and document names
- [x] **Report Generation**: Export synthesized research reports (`POST /api/v1/reports`)
- [x] **Responsive UI**: Test React interface across mobile, tablet, and desktop viewports
- [x] **Production Build**: Verify zero compilation warnings on Vercel and Render

---

## 🔒 Security Best Practices Implemented

1. **Strict CORS**: Requests allowed exclusively from configured Vercel frontend origins.
2. **Security Headers**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`.
3. **Rate Limiting**: Rate limiter middleware configured for 120 requests per minute per IP.
4. **Environment Isolation**: No hardcoded secrets or default keys allowed in production mode.
