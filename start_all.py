#!/usr/bin/env python3
"""
Unified startup script to run both FastAPI backend and Streamlit frontend.
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# Change to project root directory
project_root = Path(__file__).parent
os.chdir(project_root)

def run_backend():
    """Run FastAPI backend server."""
    print("🚀 Starting FastAPI backend on http://localhost:8008")
    return subprocess.Popen(
        [sys.executable, "run.py"],
        cwd=project_root
    )

def run_frontend():
    """Run Streamlit frontend."""
    print("🎨 Starting Streamlit frontend on http://localhost:8501")
    frontend_path = project_root / "frontend" / "app.py"
    return subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(frontend_path), "--server.port=8501"],
        cwd=project_root
    )

def main():
    """Main function to start both services."""
    print("=" * 60)
    print("IR-FETCHER - Starting Backend and Frontend")
    print("=" * 60)
    print()
    
    processes = []
    
    try:
        # Start backend
        backend_process = run_backend()
        processes.append(backend_process)
        time.sleep(2)  # Give backend time to start
        
        # Start frontend
        frontend_process = run_frontend()
        processes.append(frontend_process)
        
        print()
        print("=" * 60)
        print("✅ Both services are running!")
        print("=" * 60)
        print("📡 Backend API: http://localhost:8008")
        print("📡 API Docs: http://localhost:8008/docs")
        print("🎨 Frontend: http://localhost:8501")
        print()
        print("Press Ctrl+C to stop all services")
        print("=" * 60)
        print()
        
        # Wait for processes
        while True:
            time.sleep(1)
            # Check if any process has died
            for proc in processes:
                if proc.poll() is not None:
                    print(f"⚠️  Process {proc.pid} has stopped unexpectedly")
                    raise KeyboardInterrupt
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        for proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            except Exception as e:
                print(f"Error stopping process: {e}")
        print("✅ All services stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()

