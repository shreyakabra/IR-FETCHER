# How to Run IR-FETCHER

## Quick Start

### Option 1: Using the start script (Windows)
Double-click `start.bat` or run:
```bash
start.bat
```

### Option 2: From Command Line

1. **Navigate to the project root** (IR-FETCHER directory):
   ```bash
   cd C:\Users\dell\IR-FETCHER\IR-FETCHER
   ```

2. **Run the application**:
   ```bash
   python run.py
   ```

   OR using uvicorn directly:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8008
   ```

### Option 3: From backend directory

If you're in the `backend` directory, navigate up first:
```bash
cd ..
python run.py
```

## Before Running

Make sure you have installed dependencies:
```bash
pip install -r requirements.txt
```

## Access the Application

Once running, the API will be available at:
- **API Documentation**: http://localhost:8008/docs
- **Health Check**: http://localhost:8008/health
- **Download Endpoint**: http://localhost:8008/download
- **Files List**: http://localhost:8008/files

## Environment Variables (Optional)

Create a `.env` file in the project root and set the values you need:
```
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
DOWNLOAD_ROOT=./data/downloads
METADATA_ROOT=./data/metadata

# Database selection
DATABASE_BACKEND=sqlite          # or supabase
SQLITE_PATH=./data/database.db   # optional override for local file

# Supabase (only if DATABASE_BACKEND=supabase)
SUPABASE_URL=https://xyzcompany.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_TABLE=files             # optional, defaults to "files"
```

