# Deploying AEGIS on Vercel — Architecture & Step-by-Step Guide

## 1. System Architecture Overview

AEGIS is a production-grade Financial Crime & Anti-Money Laundering (AML) platform composed of two main subsystems:

| Layer | Technology | Recommended Hosting | Why? |
| :--- | :--- | :--- | :--- |
| **Frontend** (`apps/web`) | **Next.js 14**, React, TailwindCSS, Lucide, Recharts | **Vercel** | Vercel is the creator and optimal host for Next.js. Supports global Edge CDN, automatic SSG/SSR, and instant builds. |
| **Backend** (`apps/api` + `ml`) | **FastAPI**, PyTorch ML models, NetworkX graph engine, Scikit-learn, PostgreSQL | **Render / Railway / Cloud Run** | Vercel's serverless functions have a 50 MB uncompressed limit and 15–30s timeouts. Heavy ML libraries (PyTorch, PyTorch Geometric, Isolation Forest) and persistent database pools require a containerized backend service. |

---

## 2. Option A: Deploy Frontend to Vercel via GitHub (Recommended)

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Configure Vercel deployment and robust ingestion"
   git push origin main
   ```

2. **Import into Vercel**:
   - Go to [vercel.com](https://vercel.com) and log in.
   - Click **"Add New..."** -> **"Project"**.
   - Select your GitHub repository.

3. **Configure Project Settings on Vercel**:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Click *Edit* and select `apps/web` (or leave default since root `vercel.json` is pre-configured).
   - **Build Command**: `next build` (or default)
   - **Output Directory**: `.next` (default)

4. **Add Environment Variable**:
   In the **Environment Variables** section on Vercel, add:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-backend-api.onrender.com` (your live FastAPI backend URL)

5. **Click "Deploy"**:
   - Vercel will build the frontend and provide your live URL (e.g. `https://aegis-web.vercel.app`).

---

## 3. Option B: Deploy Frontend directly via Vercel CLI

You can deploy directly from your local terminal using the pre-installed Vercel CLI:

```bash
cd "c:\Users\ADMIN\Documents\EDI PROJECT\aegis\apps\web"
npx vercel
```

- When prompted:
  - `Set up and deploy?`: **Y**
  - `Which scope?`: Choose your Vercel account
  - `Link to existing project?`: **N**
  - `What's your project's name?`: `aegis-web`
  - `In which directory is your code located?`: `./`
  - `Want to modify settings?`: **N**

To deploy directly to production:
```bash
npx vercel --prod
```

---

## 4. Hosting the Backend (FastAPI + PyTorch ML)

To connect your Vercel frontend with the live backend, host `apps/api` on a free/affordable container platform using the included `docker-compose.yml` or `docker/api/Dockerfile`:

### Deploying to Render (Free / 1-Click):
1. Go to [render.com](https://render.com) -> **New Web Service**.
2. Connect your GitHub repo.
3. Choose **Docker** environment (Dockerfile path: `docker/api/Dockerfile`).
4. Set Environment Variables:
   - `DATABASE_URL`: Your PostgreSQL connection string (can create a free Postgres instance on Render or Supabase)
   - `SECRET_KEY`: `your_random_32_character_secret_key`
5. Copy your Render URL (e.g., `https://aegis-api.onrender.com`) and set it as `NEXT_PUBLIC_API_URL` in your Vercel project settings!
