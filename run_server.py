#!/usr/bin/env python3
"""
Simple server runner - bypasses environment checks
"""
import subprocess
import sys

def main():
    """Run the server directly."""
    try:
        print("🚀 Starting Vyralflow AI server...")
        print("📖 Documentation: http://localhost:8080/docs")
        print("🔍 Health Check: http://localhost:8080/api/health")
        print("Press Ctrl+C to stop\n")
        
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8080",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except FileNotFoundError:
        print("❌ uvicorn not found. Install with: pip install uvicorn")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()