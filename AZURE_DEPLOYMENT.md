# Microsoft Azure Production Deployment Guide

This guide provides end-to-end instructions for deploying the **AI Customer Support Platform** to production on **Microsoft Azure** using your **Azure for Students** credits ($100 free credit, zero mandatory credit card requirement).

---

## 🏗️ Production Azure Architecture

```
                                  ┌───────────────────────────┐
                                  │   Azure Static Web Apps   │
                                  │  React 18 / Vite SPA      │
                                  └─────────────┬─────────────┘
                                                │
                                       HTTPS API Requests
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Azure App Service (Linux Python 3.12 - FastAPI Backend)                                │
│                                                                                        │
│  ┌────────────────────┐    ┌────────────────────┐    ┌──────────────────────────────┐  │
│  │ FastAPI App        │    │ Alembic Migrations │    │ Security & CORS Middleware   │  │
│  │ (Python 3.12)      │    │ (Startup Script)   │    │ (JWT, bcrypt, Rate Limiting) │  │
│  └─────────┬──────────┘    └────────────────────┘    └──────────────────────────────┘  │
│            │                                                                           │
│            ├─── Database ORM ──────────► Azure Database for PostgreSQL Flexible Server  │
│            │                             (SSL sslmode=require)                         │
│            │                                                                           │
│            ├─── Persistent Files ──────► App Service Persistent Disk (/home/site/data) │
│            │                             ├── /home/site/data/chroma (ChromaDB)         │
│            │                             └── /home/site/data/uploads (Uploaded PDFs)   │
│            │                                                                           │
│            └─── AI Engine ─────────────► Google AI Studio (Gemini 2.5 Pro & Embeddings)│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 💰 Azure for Students Cost Breakdown

Using the **Azure for Students** subscription ($100 credit + free tier resources):

| Resource | Service & Pricing Tier | Estimated Monthly Cost | Student Credit Covered |
| :--- | :--- | :---: | :---: |
| **Frontend** | Azure Static Web Apps (Free Tier) | **$0.00** | 100% Free |
| **Backend** | Azure App Service (Basic B1 / Free F1) | **$0.00 – $13.00** | 100% Covered |
| **Database** | Azure Database for PostgreSQL (Burstable B1ms) | **$0.00 – $15.00** | 100% Covered |
| **Storage** | App Service Persistent Disk (`/home`) | **$0.00** | Included in App Service |
| **Vector DB** | ChromaDB Persistent Storage (`/home/site/data`) | **$0.00** | Included in App Service |
| **Total Estimated Cost** | | **$0.00 / month** | **Fully Covered by Credits** |

---

## 📋 Step-by-Step Azure Deployment Guide

### Step 1: Create Azure Database for PostgreSQL Flexible Server

1. Open [Azure Portal PostgreSQL Flexible Servers](https://portal.azure.com/#blade/HubsExtension/BrowseResource/Microsoft.DBforPostgreSQL%2FflexibleServers).
2. Click **+ Create**.
3. Fill in the parameters:
   - **Subscription**: Azure for Students
   - **Resource Group**: `rg-ai-customer-support`
   - **Server Name**: `psql-ai-customer-support`
   - **Region**: *East US* or *West Europe*
   - **Workload Type**: Development
   - **Compute + Storage**: Standard B1ms (1 vCore, 2 GiB RAM)
   - **Admin Username**: `psqladmin`
   - **Password**: `<your-secure-password>`
4. Under **Networking**:
   - Check **Allow public access from any Azure service within Azure to this server**.
   - Add your client IP address to firewall rules.
5. Click **Review + create** $\rightarrow$ **Create**.

---

### Step 2: Create Azure App Service (FastAPI Backend)

1. Open [Azure Portal App Services](https://portal.azure.com/#blade/HubsExtension/BrowseResource/Microsoft.Web%2Fsites).
2. Click **+ Create** $\rightarrow$ **Web App**.
3. Fill in details:
   - **Resource Group**: `rg-ai-customer-support`
   - **Name**: `app-ai-customer-support-backend` (creates `https://app-ai-customer-support-backend.azurewebsites.net`)
   - **Publish**: Code
   - **Runtime stack**: Python 3.12
   - **Operating System**: Linux
   - **Pricing Plan**: Basic B1 (or Free F1)
4. Click **Review + create** $\rightarrow$ **Create**.

---

### Step 3: Configure App Service Environment Variables & Startup

1. Open your App Service `app-ai-customer-support-backend` in Azure Portal.
2. Navigate to **Settings** $\rightarrow$ **Configuration** (or **Environment Variables**).
3. Under **General settings**:
   - Set **Startup Command**: `bash startup.sh`
4. Under **Application settings**, add:

| Environment Variable | Value |
| :--- | :--- |
| `APP_ENV` | `production` |
| `DEBUG` | `false` |
| `PYTHONPATH` | `.` |
| `SECRET_KEY` | `<generate-64-char-random-hex-key>` |
| `JWT_SECRET_KEY` | `<generate-64-char-random-hex-key>` |
| `DATABASE_URL` | `postgresql+asyncpg://psqladmin:<password>@psql-ai-customer-support.postgres.database.azure.com:5432/customer_support_db?sslmode=require` |
| `GOOGLE_API_KEY` | `<your-google-ai-studio-api-key>` |
| `GEMINI_LLM_MODEL` | `gemini-2.5-pro` |
| `GEMINI_EMBEDDING_MODEL` | `models/text-embedding-004` |
| `CHROMA_PERSIST_DIRECTORY` | `/home/site/data/chroma` |
| `UPLOAD_BASE_DIR` | `/home/site/data/uploads` |
| `ALLOWED_ORIGINS` | `https://<your-static-web-app-name>.azurestaticapps.net` |

5. Click **Save**.

---

### Step 4: Create Azure Static Web Apps (React Frontend)

1. Open [Azure Portal Static Web Apps](https://portal.azure.com/#blade/HubsExtension/BrowseResource/Microsoft.Web%2FstaticSites).
2. Click **+ Create**.
3. Fill in details:
   - **Resource Group**: `rg-ai-customer-support`
   - **Name**: `swa-ai-customer-support`
   - **Plan type**: Free ($0/month)
   - **Deployment Details**: Source GitHub
   - **Organization / Repository**: `mubeenah-collab/AI-customer-support-platform`
   - **Branch**: `main`
   - **Build Presets**: Custom
   - **App location**: `/frontend`
   - **Api location**: *(leave blank)*
   - **Output location**: `dist`
4. Click **Review + create** $\rightarrow$ **Create**.
5. Once created, open **Environment variables** on your Static Web App and set:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://app-ai-customer-support-backend.azurewebsites.net/api/v1`

---

## 🧪 Step 5: Verify Production Deployment

### 1. Backend Health Check
```bash
curl -i https://app-ai-customer-support-backend.azurewebsites.net/health
```
**Expected Response**:
```json
{
  "status": "healthy",
  "service": "AI Customer Support Platform API",
  "version": "1.0.0"
}
```

### 2. Readiness Check (PostgreSQL + ChromaDB)
```bash
curl -i https://app-ai-customer-support-backend.azurewebsites.net/api/v1/health/ready
```

### 3. Feature Verification Checklist
- [x] **Registration**: `POST /api/v1/auth/register`
- [x] **Login & JWT**: `POST /api/v1/auth/login`
- [x] **PDF Ingestion**: `POST /api/v1/documents/upload`
- [x] **Embeddings**: Gemini `models/text-embedding-004`
- [x] **ChromaDB**: Persisted under `/home/site/data/chroma`
- [x] **RAG Retrieval**: `POST /api/v1/search`
- [x] **AI Chat**: `POST /api/v1/chat`
- [x] **Report Generation**: `POST /api/v1/reports`
- [x] **Frontend SPA**: `https://<your-static-web-app-name>.azurestaticapps.net`
