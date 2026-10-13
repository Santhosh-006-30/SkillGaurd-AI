# Deployment Guide — SkillGuard AI

## 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- CPU or CUDA-capable GPU (CPU is default)

## 2. Local Development Setup
1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 3. Production Deployment Notes
- Backend can run behind NGINX or reverse proxy.
- Frontend builds into static assets via `npm run build`.
- PostgreSQL can be configured via `DATABASE_URL` in `.env`.
