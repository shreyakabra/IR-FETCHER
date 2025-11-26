# Quick Start Guide

## 🚀 Run Everything with One Command

### Windows
```bash
start_all.bat
```

### Linux/Mac
```bash
python start_all.py
```

This starts:
- ✅ FastAPI backend on http://localhost:8008
- ✅ Streamlit frontend on http://localhost:8501

## 📦 What's New

### 1. Database Integration ✅
- **SQLite** (default) - No setup required, works out of the box
- **Supabase** (optional) - Set `DATABASE_BACKEND=supabase` and provide Supabase credentials
- All metadata is now stored in a database instead of just JSON files

### 2. Unified Startup Script ✅
- Run both backend and frontend with a single command
- Automatic process management
- Clean shutdown on Ctrl+C

### 3. Next.js Frontend for Vercel ✅
- Modern, responsive UI
- Located in `frontend-next/` directory
- Ready for Vercel deployment

### 4. Improved UI ✅
- Clean, modern design
- Better user experience
- Responsive layout
- Loading states and error handling

## 🗄️ Database Setup

### SQLite (Default)
No setup needed! The database is created automatically at `./data/database.db`

### Supabase (Deployment)
1. Create a Supabase project and table (defaults to `files`)
2. Set environment variables:
   ```bash
   DATABASE_BACKEND=supabase
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=service_role_key_here
   SUPABASE_TABLE=files
   ```

## 🌐 Vercel Deployment

### Step 1: Deploy Backend
Deploy to Railway, Render, or Fly.io:
- Set environment variables
- Get your backend URL

### Step 2: Deploy Frontend
```bash
cd frontend-next
npm install
vercel
```

Set environment variables in Vercel:
- `NEXT_PUBLIC_API_URL`: Your backend URL
- `BACKEND_URL`: Same as above

See `README_DEPLOYMENT.md` for detailed instructions.

## 📁 Project Structure

```
IR-FETCHER/
├── backend/              # FastAPI backend
│   ├── database.py      # Database models (NEW)
│   ├── main.py          # FastAPI app (with CORS)
│   └── ...
├── frontend/            # Streamlit (local dev)
├── frontend-next/       # Next.js (Vercel) (NEW)
│   ├── app/
│   │   ├── page.tsx    # Main UI
│   │   └── api/        # API proxy
│   └── package.json
├── start_all.py        # Unified startup (NEW)
└── vercel.json         # Vercel config (NEW)
```

## 🔧 Environment Variables

Create a `.env` file:
```env
OPENAI_API_KEY=your_key
TAVILY_API_KEY=your_key
DATABASE_BACKEND=sqlite          # switch to "supabase" for deployment
SQLITE_PATH=./data/database.db   # optional override
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=service_role_key_here
```

## 📚 More Information

- **Full Deployment Guide**: See `README_DEPLOYMENT.md`
- **Development Guide**: See `DEVELOPMENT_GUIDE.md`
- **Run Instructions**: See `README_RUN.md`

