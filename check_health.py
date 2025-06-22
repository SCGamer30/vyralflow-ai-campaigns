#!/usr/bin/env python3
"""
Vyralflow AI Health Check Script
Quick script to verify system health and configuration
"""
import sys
import requests
import json
from pathlib import Path
import os

def check_env_file():
    """Check if .env file exists and has required keys."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    print("✅ .env file exists")
    
    # Check for required keys
    required_keys = [
        "GOOGLE_CLOUD_PROJECT",
        "GEMINI_API_KEY", 
        "UNSPLASH_ACCESS_KEY"
    ]
    
    missing_keys = []
    with open(env_file) as f:
        content = f.read()
        for key in required_keys:
            if f"{key}=" not in content or f"{key}=your-" in content:
                missing_keys.append(key)
    
    if missing_keys:
        print(f"⚠️  Missing or unconfigured API keys: {', '.join(missing_keys)}")
        return False
    else:
        print("✅ All required API keys appear to be configured")
        return True

def check_server_running(port=8080):
    """Check if the server is running."""
    try:
        response = requests.get(f"http://localhost:{port}/ping", timeout=5)
        if response.status_code == 200:
            print(f"✅ Server is running on port {port}")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Server is not running on port {port}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Server connection timed out on port {port}")
        return False

def check_api_health(port=8080):
    """Check API health endpoint."""
    try:
        response = requests.get(f"http://localhost:{port}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ API health check passed")
            print(f"   Status: {data.get('status', 'unknown')}")
            
            services = data.get('services', {})
            for service, status in services.items():
                icon = "✅" if status == "healthy" else "❌"
                print(f"   {icon} {service}: {status}")
            
            return True
        else:
            print(f"❌ API health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check failed: {e}")
        return False

def check_agents_status(port=8080):
    """Check individual agents status."""
    try:
        response = requests.get(f"http://localhost:{port}/api/agents/status", timeout=10)
        if response.status_code == 200:
            agents = response.json()
            print("✅ Agents status check passed")
            
            for agent in agents:
                name = agent.get('agent_name', 'unknown')
                healthy = agent.get('is_healthy', False)
                icon = "✅" if healthy else "❌"
                print(f"   {icon} {name}: {'healthy' if healthy else 'unhealthy'}")
            
            return True
        else:
            print(f"❌ Agents status check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Agents status check failed: {e}")
        return False

def test_campaign_creation(port=8080):
    """Test campaign creation endpoint."""
    print("\n🧪 Testing campaign creation...")
    
    test_campaign = {
        "business_name": "Test Coffee Shop",
        "industry": "food & beverage",
        "campaign_goal": "Test campaign for health check",
        "target_platforms": ["instagram", "twitter"],
        "brand_voice": "friendly",
        "target_audience": "Coffee lovers",
        "keywords": ["coffee", "test"]
    }
    
    try:
        response = requests.post(
            f"http://localhost:{port}/api/campaigns/create",
            json=test_campaign,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            campaign_id = data.get('campaign_id')
            print(f"✅ Campaign creation test passed")
            print(f"   Campaign ID: {campaign_id}")
            print("   Note: This is a test campaign that will process in the background")
            return True
        else:
            print(f"❌ Campaign creation test failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Campaign creation test failed: {e}")
        return False

def main():
    """Main health check function."""
    print("🔍 Vyralflow AI Health Check")
    print("=" * 40)
    
    # Check configuration
    print("\n📋 Configuration Check:")
    env_ok = check_env_file()
    
    # Check server
    print("\n🖥️  Server Check:")
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number, using default 8080")
    
    server_ok = check_server_running(port)
    
    if not server_ok:
        print("\n❌ Server is not running. Start it with: python start.py")
        sys.exit(1)
    
    # Check API health
    print("\n🏥 API Health Check:")
    api_ok = check_api_health(port)
    
    # Check agents
    print("\n🤖 Agents Check:")
    agents_ok = check_agents_status(port)
    
    # Optional: Test campaign creation
    if "--test-campaign" in sys.argv:
        test_campaign_creation(port)
    
    # Summary
    print("\n" + "=" * 40)
    all_checks = [env_ok, server_ok, api_ok, agents_ok]
    
    if all(all_checks):
        print("🎉 All health checks passed!")
        print("🚀 Vyralflow AI is ready for action!")
    else:
        print("⚠️  Some health checks failed")
        print("📖 Check the logs above for details")
        sys.exit(1)

if __name__ == "__main__":
    main()