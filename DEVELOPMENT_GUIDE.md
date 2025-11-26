# Development Guide - Auto-Reload & Testing

## Auto-Reload Feature

The server is now configured with **auto-reload enabled**. This means:

✅ **Automatic Restart**: When you save changes to any Python file in the `backend/` directory, the server will automatically detect the change and restart itself.

✅ **No Manual Restart Needed**: Just save your file and wait 1-2 seconds for the server to reload.

## How It Works

The `run.py` file now includes `reload=True`:
```python
uvicorn.run(app, host="0.0.0.0", port=8008, reload=True)
```

Uvicorn watches for file changes in the project directory and automatically restarts the server when it detects modifications.

## Manual Restart (if needed)

If you need to manually restart the server:

### Option 1: Use the restart script
```bash
RESTART_SERVER.bat
```

### Option 2: Stop and start manually
1. **Stop the server**: Press `Ctrl+C` in the terminal where it's running, or:
   ```powershell
   Get-Process python | Stop-Process -Force
   ```

2. **Start the server**:
   ```bash
   python run.py
   ```
   or
   ```bash
   start.bat
   ```

## Testing Endpoints

After making changes, test your endpoints:

1. **Health check**: `http://localhost:8008/health`
2. **Root endpoint**: `http://localhost:8008/`
3. **API docs**: `http://localhost:8008/docs`
4. **Run test script**: `python test_main.py`

## Tips

- The server will show "Reloading..." in the console when it detects changes
- If auto-reload doesn't work, check that you're saving files in the `backend/` directory
- For production, remove `reload=True` from `run.py`

