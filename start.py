#!/usr/bin/env python3
"""
Vyralflow AI Startup Script
Simple script to run the Vyralflow AI backend server
"""
import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def check_virtual_environment():
    """Check if virtual environment is active."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is active")
        return True
    else:
        print("⚠️  Virtual environment not detected")
        print("Recommendation: Create and activate a virtual environment")
        print("Commands:")
        print("  python -m venv venv")
        print("  source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        return False

def check_env_file():
    """Check if .env file exists."""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        return True
    else:
        print("❌ .env file not found")
        print("Please copy .env.example to .env and configure your API keys")
        print("Command: cp .env.example .env")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_server(dev_mode=True, port=8080):
    """Start the FastAPI server."""
    print(f"🚀 Starting Vyralflow AI server on port {port}")
    print(f"📖 API Documentation: http://localhost:{port}/docs")
    print(f"🔍 Health Check: http://localhost:{port}/api/health")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        if dev_mode:
            # Development mode with auto-reload
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "app.main:app", 
                "--reload", 
                "--host", "0.0.0.0", 
                "--port", str(port),
                "--log-level", "info"
            ])
        else:
            # Production mode
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "app.main:app", 
                "--host", "0.0.0.0", 
                "--port", str(port),
                "--workers", "1"
            ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def main():
    """Main startup function."""
    print("🤖 Vyralflow AI - Multi-Agent Campaign Generator")
    print("=" * 50)
    
    # Check prerequisites
    check_python_version()
    venv_active = check_virtual_environment()
    env_exists = check_env_file()
    
    if not env_exists:
        sys.exit(1)
    
    # Install dependencies if needed
    try:
        import fastapi
        print("✅ FastAPI already installed")
    except ImportError:
        if not install_dependencies():
            sys.exit(1)
    
    # Parse command line arguments
    dev_mode = "--prod" not in sys.argv
    port = 8080
    
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
            except ValueError:
                print("❌ Invalid port number")
                sys.exit(1)
    
    mode_text = "Development" if dev_mode else "Production"
    print(f"🔧 Mode: {mode_text}")
    
    if not venv_active:
        # Check if we can import required packages anyway
        try:
            import fastapi
            import uvicorn
            print("✅ Required packages available, continuing...")
        except ImportError:
            print("❌ Required packages not found. Please run: python setup.py")
            sys.exit(1)
    
    print()
    start_server(dev_mode, port)

if __name__ == "__main__":
    main()