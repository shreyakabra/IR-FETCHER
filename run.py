#!/usr/bin/env python3
"""
Entry point for running the IR-FETCHER FastAPI application.
"""
import uvicorn

if __name__ == "__main__":
    # Enable reload for development - automatically restarts on code changes
    # Note: reload=True requires app as import string, not object
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8008, reload=True)

