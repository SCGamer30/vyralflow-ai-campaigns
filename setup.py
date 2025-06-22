#!/usr/bin/env python3
"""
Vyralflow AI Setup Script
Automated setup for development environment
"""
import sys
import os
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"Current version: {sys.version}")
        print("Please install Python 3.9+ and try again")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def create_virtual_environment():
    """Create virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def get_venv_python():
    """Get the Python executable from virtual environment."""
    if os.name == 'nt':  # Windows
        return Path("venv/Scripts/python.exe")
    else:  # Unix-like
        return Path("venv/bin/python")

def install_dependencies():
    """Install dependencies in virtual environment."""
    print("📦 Installing dependencies...")
    venv_python = get_venv_python()
    
    try:
        subprocess.run([
            str(venv_python), "-m", "pip", "install", "--upgrade", "pip"
        ], check=True)
        
        subprocess.run([
            str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment_file():
    """Set up environment file from template."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    # Copy example to .env
    shutil.copy(env_example, env_file)
    print("✅ Created .env file from template")
    
    print("\n🔑 IMPORTANT: Configure your API keys in .env file:")
    print("   - GOOGLE_CLOUD_PROJECT=your-project-id")
    print("   - GEMINI_API_KEY=your-gemini-api-key")
    print("   - UNSPLASH_ACCESS_KEY=your-unsplash-access-key")
    print("   - (Optional) Reddit API credentials")
    
    return True

def check_api_requirements():
    """Display API requirements and setup instructions."""
    print("\n📋 API Requirements Checklist:")
    print("=" * 40)
    
    print("\n1. 🔗 Google Gemini API (FREE)")
    print("   • Visit: https://ai.google.dev")
    print("   • Sign up and get your free API key")
    print("   • Add to .env: GEMINI_API_KEY=your_key_here")
    
    print("\n2. 🖼️  Unsplash API (FREE)")
    print("   • Visit: https://unsplash.com/developers")
    print("   • Create a new application")
    print("   • Add to .env: UNSPLASH_ACCESS_KEY=your_access_key")
    
    print("\n3. ☁️  Google Cloud Project")
    print("   • Visit: https://console.cloud.google.com")
    print("   • Create a new project or use existing")
    print("   • Enable Firestore database")
    print("   • Create service account key (JSON)")
    print("   • Add to .env: GOOGLE_CLOUD_PROJECT=your-project-id")
    print("   • Add to .env: GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json")
    
    print("\n4. 🔴 Reddit API (Optional)")
    print("   • Visit: https://www.reddit.com/prefs/apps")
    print("   • Create script app")
    print("   • Add credentials to .env (optional)")

def create_run_scripts():
    """Create convenient run scripts."""
    # Create run script for Unix-like systems
    run_script_unix = Path("run.sh")
    with open(run_script_unix, 'w') as f:
        f.write("""#!/bin/bash
# Vyralflow AI Quick Start Script

echo "🤖 Starting Vyralflow AI..."
source venv/bin/activate
python start.py "$@"
""")
    
    # Make it executable
    os.chmod(run_script_unix, 0o755)
    
    # Create run script for Windows
    run_script_win = Path("run.bat")
    with open(run_script_win, 'w') as f:
        f.write("""@echo off
REM Vyralflow AI Quick Start Script

echo 🤖 Starting Vyralflow AI...
call venv\\Scripts\\activate
python start.py %*
""")
    
    print("✅ Created run scripts (run.sh / run.bat)")

def main():
    """Main setup function."""
    print("🤖 Vyralflow AI - Development Environment Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Setup steps
    if not create_virtual_environment():
        sys.exit(1)
    
    if not install_dependencies():
        sys.exit(1)
    
    if not setup_environment_file():
        sys.exit(1)
    
    create_run_scripts()
    
    # Display API requirements
    check_api_requirements()
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Configure API keys in .env file")
    print("2. Run: python start.py (or ./run.sh)")
    print("3. Open: http://localhost:8080/docs")
    print("\n🚀 Ready for your hackathon demo!")

if __name__ == "__main__":
    main()