#!/usr/bin/env python3
"""
Debug startup issues
"""
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all imports step by step."""
    try:
        print("🔍 Testing imports...")
        
        print("1. Testing pydantic...")
        from pydantic import Field
        from pydantic_settings import BaseSettings
        print("✅ Pydantic imports OK")
        
        print("2. Testing FastAPI...")
        from fastapi import FastAPI
        print("✅ FastAPI import OK")
        
        print("3. Testing config...")
        from app.core.config import settings
        print(f"✅ Config loaded - App name: {settings.app_name}")
        
        print("4. Testing database...")
        from app.core.database import db_manager
        print("✅ Database manager OK")
        
        print("5. Testing services...")
        from app.services.gemini_service import gemini_service
        from app.services.trends_service import trends_service
        print("✅ Services OK")
        
        print("6. Testing agents...")
        from app.agents.trend_analyzer import trend_analyzer_agent
        from app.agents.content_writer import content_writer_agent
        print("✅ Agents OK")
        
        print("7. Testing main app...")
        from app.main import app
        print("✅ Main app OK")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_server():
    """Test if we can create a simple FastAPI server."""
    try:
        print("\n🚀 Testing simple FastAPI server...")
        from fastapi import FastAPI
        
        app = FastAPI(title="Test App")
        
        @app.get("/")
        def read_root():
            return {"message": "Hello World"}
        
        print("✅ Simple FastAPI app created successfully")
        return app
        
    except Exception as e:
        print(f"❌ Simple server test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main debug function."""
    print("🐛 Vyralflow AI Startup Debugging")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        return
    
    # Test simple server
    simple_app = test_simple_server()
    if not simple_app:
        return
    
    print("\n✅ All tests passed!")
    print("The issue might be with environment configuration or API keys.")
    
    # Check API keys
    print("\n🔑 Checking API keys...")
    try:
        from app.core.config import settings
        missing_keys = settings.validate_required_keys()
        if missing_keys:
            print(f"❌ Missing API keys: {', '.join(missing_keys)}")
        else:
            print("✅ All required API keys configured")
    except Exception as e:
        print(f"❌ API key check failed: {e}")

if __name__ == "__main__":
    main()