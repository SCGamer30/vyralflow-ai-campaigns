#!/usr/bin/env python3
"""
Demo server - simplified for hackathon demo
"""
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def create_demo_app():
    """Create a demo FastAPI app with minimal dependencies."""
    app = FastAPI(
        title="Vyralflow AI - Demo Mode",
        description="Multi-Agent Social Media Campaign Generator (Demo Mode)",
        version="1.0.0"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Vyralflow AI - Demo Mode",
            "version": "1.0.0",
            "documentation": "/docs",
            "status": "running"
        }
    
    @app.get("/ping")
    async def ping():
        return {"status": "ok", "mode": "demo"}
    
    @app.get("/api/health")
    async def health():
        return {
            "status": "healthy",
            "mode": "demo",
            "message": "Demo server running without database",
            "services": {
                "api": "healthy",
                "demo_mode": "active"
            }
        }
    
    @app.post("/api/campaigns/create")
    async def create_demo_campaign():
        return {
            "campaign_id": "demo_12345",
            "status": "processing",
            "message": "Demo campaign created - connect real database for full functionality",
            "demo_mode": True
        }
    
    return app

def main():
    """Run demo server."""
    try:
        print("🎬 Starting Vyralflow AI Demo Server...")
        print("📖 Documentation: http://localhost:8080/docs")
        print("🔍 Health Check: http://localhost:8080/api/health")
        print("✨ Demo Mode - Database optional")
        print("Press Ctrl+C to stop\n")
        
        app = create_demo_app()
        
        # Run on localhost specifically
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8080,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Demo server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()