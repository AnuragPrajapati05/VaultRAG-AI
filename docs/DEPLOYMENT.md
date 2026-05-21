# Deployment Guide

## GitHub

```bash
git init
git add .
git commit -m "Prepare VaultRAG AI for production deployment"
git branch -M main
git remote add origin https://github.com/<your-user>/VaultRAG-AI.git
git push -u origin main
```

## Render Backend

Use the `render.yaml` blueprint or configure a Web Service manually.

Settings:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

Environment variables:

```env
GEMINI_API_KEY=<set in Render dashboard>
CORS_ORIGINS=https://your-frontend-url.vercel.app
CHROMA_PERSIST_DIR=/tmp/chroma_db
DATABASE_URL=./datasets/sql/enterprise.db
DEBUG=false
```

## Vercel Frontend

Settings:

- Root directory: `frontend`
- Install command: `npm install`
- Build command: `npm run build`
- Output directory: `dist`

Environment variables:

```env
VITE_API_URL=https://your-render-backend-url.onrender.com
```

After backend deployment, update `CORS_ORIGINS` on Render to include the Vercel frontend URL.
