# Deployment Guide

This guide covers deploying IR-FETCHER to Vercel and setting up the database.

## Prerequisites

1. Node.js 18+ installed
2. Python 3.8+ installed
3. Vercel account (free tier works)
4. Database (SQLite for local, Supabase for deployment)

## Quick Start - Local Development

### Option 1: Run Everything with One Command

```bash
# Windows
start_all.bat

# Linux/Mac
python start_all.py
```

This will start:
- FastAPI backend on http://localhost:8008
- Streamlit frontend on http://localhost:8501

### Option 2: Run Separately

```bash
# Terminal 1: Backend
python run.py

# Terminal 2: Frontend (Streamlit)
cd frontend
streamlit run app.py

# OR Next.js frontend
cd frontend-next
npm install
npm run dev
```

## Database Setup

### SQLite (Default - No Setup Required)

SQLite is used by default. The database file will be created automatically at `./data/database.db` on first run.

### Supabase (Deployment)

1. Create a Supabase project (https://supabase.com) – the free tier works.
2. In the SQL editor, create a `files` table (or reuse an existing one) with columns that match the metadata schema (`company`, `doc_type`, `year`, `file_path`, `filename`, `url`, `sha256`, `mimetype`, `source`, `indexed_at`, `created_at`).
3. Grab the project `SUPABASE_URL` and the **service role** key from Project Settings → API.
4. Set the following environment variables in your deployment target:
   ```
   DATABASE_BACKEND=supabase
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=service_role_key_here
   SUPABASE_TABLE=files   # optional if you used a different table name
   ```

When `DATABASE_BACKEND` is set to `supabase`, all reads/writes go through Supabase.

## Vercel Deployment

### Step 1: Deploy FastAPI Backend

You have two options:

#### Option A: Deploy Backend Separately (Recommended)

Deploy the FastAPI backend to a service that supports Python:
- **Railway**: https://railway.app
- **Render**: https://render.com
- **Fly.io**: https://fly.io
- **Heroku**: https://heroku.com

1. Push your code to GitHub
2. Connect your repository to the service
3. Set environment variables:
   - `OPENAI_API_KEY`
   - `TAVILY_API_KEY`
   - `DATABASE_BACKEND` (set to `supabase` in deployment)
   - `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_TABLE` (if using Supabase)
4. Deploy

#### Option B: Use Vercel Serverless Functions

The Next.js frontend includes API proxy routes that can forward requests to your backend.

### Step 2: Deploy Next.js Frontend to Vercel

1. **Install Vercel CLI** (optional):
   ```bash
   npm i -g vercel
   ```

2. **Deploy from frontend-next directory**:
   ```bash
   cd frontend-next
   vercel
   ```

   Or connect your GitHub repository to Vercel:
   - Go to https://vercel.com
   - Click "New Project"
   - Import your repository
   - Set root directory to `frontend-next`
   - Add environment variables:
     - `NEXT_PUBLIC_API_URL`: Your backend API URL (e.g., `https://your-backend.railway.app`)
     - `BACKEND_URL`: Same as above (for API proxy)

3. **Environment Variables in Vercel**:
   - Go to your project settings → Environment Variables
   - Add:
     - `NEXT_PUBLIC_API_URL`: Your deployed backend URL
     - `BACKEND_URL`: Same as above

### Step 3: Configure CORS (if needed)

If your backend is on a different domain, update `backend/main.py` to allow CORS:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Environment Variables

### Backend (.env file)

```env
# API Keys
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key

# Storage
DOWNLOAD_ROOT=./data/downloads
METADATA_ROOT=./data/metadata

# Database selection
DATABASE_BACKEND=sqlite          # or "supabase"
SQLITE_PATH=./data/database.db   # optional override

# Supabase (required if DATABASE_BACKEND=supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=service_role_key_here
SUPABASE_TABLE=files
```

### Frontend (Vercel Environment Variables)

```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
BACKEND_URL=https://your-backend-url.com
```

## Project Structure

```
IR-FETCHER/
├── backend/              # FastAPI backend
│   ├── main.py          # FastAPI app
│   ├── database.py      # Database models
│   └── ...
├── frontend/            # Streamlit frontend (local dev)
│   └── app.py
├── frontend-next/       # Next.js frontend (Vercel)
│   ├── app/
│   │   ├── page.tsx    # Main page
│   │   └── api/        # API proxy routes
│   └── package.json
├── start_all.py        # Unified startup script
└── vercel.json         # Vercel configuration
```

## Troubleshooting

### Database Issues

- **SQLite locked**: Make sure only one process is accessing the database
- **Supabase connection failed**: Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`

### Vercel Deployment Issues

- **API proxy not working**: Check that `BACKEND_URL` is set correctly
- **CORS errors**: Update CORS settings in `backend/main.py`
- **Build fails**: Make sure all dependencies are in `package.json`

### Backend Not Starting

- Check that port 8008 is not in use
- Verify all environment variables are set
- Check logs for errors

## Production Checklist

- [ ] Set up Supabase project/table
- [ ] Configure environment variables
- [ ] Deploy backend to Railway/Render/Fly.io
- [ ] Deploy frontend to Vercel
- [ ] Configure CORS properly
- [ ] Set up monitoring/logging
- [ ] Configure custom domain (optional)
- [ ] Set up SSL certificates (automatic on Vercel)

## Support

For issues or questions, check the main README or open an issue on GitHub.

