#!/usr/bin/env python3
"""
Working server with demo database fallback
"""
import sys
from pathlib import Path
import uvicorn
import os

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def setup_demo_mode():
    """Set up demo mode environment."""
    # Override database service to use demo database
    import app.services.firestore_service as firestore_module
    from app.core.demo_database import demo_db
    
    # Replace firestore service with demo database
    firestore_module.firestore_service = demo_db
    
    print("✅ Demo mode activated - using in-memory database")

def main():
    """Run working server."""
    try:
        print("🚀 Starting Vyralflow AI Working Server...")
        print("🎬 Demo Mode - In-memory database for hackathon")
        
        # Set up demo mode
        setup_demo_mode()
        
        # Import the main app after demo setup
        from app.main import app
        
        print("📖 Documentation: http://localhost:8080/docs")
        print("🔍 Health Check: http://localhost:8080/api/health")
        print("✨ All 4 AI agents ready!")
        print("Press Ctrl+C to stop\n")
        
        # Run on localhost
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8080,
            log_level="info",
            reload=False  # Disable reload to avoid issues
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()