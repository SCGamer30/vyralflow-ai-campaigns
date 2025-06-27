#!/usr/bin/env python3
"""
Vyralflow AI Server Launcher
Simplified launcher for localhost development
"""
import os
import sys
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("   Please copy .env.example to .env and add your API keys")
        return False
    
    # Check if venv is activated (optional but recommended)
    if not sys.prefix != sys.base_prefix:
        print("⚠️  Virtual environment not detected")
        print("   Consider activating venv: source venv/bin/activate")
    
    print("✅ Requirements check passed")
    return True

def main():
    """Main launcher function"""
    print("🚀 Vyralflow AI - Campaign Generator")
    print("=" * 50)
    
    if not check_requirements():
        sys.exit(1)
    
    print()
    print("🌐 Starting server on localhost:8080...")
    print("📖 API Documentation: http://localhost:8080/docs")
    print("🔍 Health Check: http://localhost:8080/api/health")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Import and run the enhanced server
    try:
        from vyralflow_enhanced import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="localhost",
            port=8080,
            log_level="info",
            reload=True,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()