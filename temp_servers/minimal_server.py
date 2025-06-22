#!/usr/bin/env python3
"""
Minimal server for testing
"""
import sys
from pathlib import Path
import uvicorn

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def run_minimal():
    """Run minimal server."""
    try:
        print("🚀 Starting minimal Vyralflow AI server...")
        print("📖 Documentation: http://localhost:8080/docs")
        print("🔍 Health Check: http://localhost:8080/api/health")
        print("Press Ctrl+C to stop\n")
        
        # Import our app
        from app.main import app
        
        # Run directly with uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8080,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_minimal()