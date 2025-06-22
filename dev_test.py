#!/usr/bin/env python3
"""
Vyralflow AI Development Test Script
Quick testing script for development and debugging
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_agents():
    """Test all agents individually."""
    print("🧪 Testing individual agents...")
    
    try:
        from app.agents.trend_analyzer import trend_analyzer_agent
        from app.agents.content_writer import content_writer_agent
        from app.agents.visual_designer import visual_designer_agent
        from app.agents.campaign_scheduler import campaign_scheduler_agent
        from app.models.agent import AgentInput
        
        # Test input
        test_input = AgentInput(
            campaign_id="test_123",
            business_name="Test Coffee Shop",
            industry="food & beverage",
            campaign_goal="Test our new espresso blend",
            target_platforms=["instagram", "twitter"],
            brand_voice="friendly",
            target_audience="Coffee enthusiasts",
            keywords=["coffee", "espresso", "artisan"]
        )
        
        agents = [
            ("Trend Analyzer", trend_analyzer_agent),
            ("Content Writer", content_writer_agent),
            ("Visual Designer", visual_designer_agent),
            ("Campaign Scheduler", campaign_scheduler_agent)
        ]
        
        results = {}
        
        for name, agent in agents:
            print(f"\n🤖 Testing {name}...")
            try:
                # Update input with previous results
                test_input.previous_results = results
                
                output = await agent.execute(test_input)
                
                if output.status.value == "completed":
                    print(f"   ✅ {name} completed successfully")
                    if output.results:
                        results.update(output.results)
                        print(f"   📊 Generated {len(output.results)} result fields")
                else:
                    print(f"   ❌ {name} failed: {output.error_message}")
                
            except Exception as e:
                print(f"   ❌ {name} error: {e}")
        
        print(f"\n📋 Total results collected: {len(results)} fields")
        return results
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
        return {}

async def test_orchestrator():
    """Test the campaign orchestrator."""
    print("\n🎼 Testing Campaign Orchestrator...")
    
    try:
        from app.core.orchestrator import campaign_orchestrator
        from app.models.campaign import CampaignRequest, SupportedPlatform, BrandVoice
        
        # Test campaign request
        test_request = CampaignRequest(
            business_name="Dev Test Café",
            industry="food & beverage",
            campaign_goal="Launch our new seasonal menu",
            target_platforms=[SupportedPlatform.INSTAGRAM, SupportedPlatform.TWITTER],
            brand_voice=BrandVoice.FRIENDLY,
            target_audience="Food lovers and local community",
            keywords=["seasonal", "fresh", "local", "delicious"]
        )
        
        print("📝 Creating test campaign...")
        response = await campaign_orchestrator.create_campaign(test_request)
        
        print(f"✅ Campaign created: {response.campaign_id}")
        print(f"📊 Status: {response.status}")
        print(f"🤖 Agents: {len(response.agent_progress)}")
        
        return response.campaign_id
        
    except Exception as e:
        print(f"❌ Orchestrator error: {e}")
        return None

async def test_services():
    """Test external services."""
    print("\n🌐 Testing External Services...")
    
    try:
        from app.services.gemini_service import gemini_service
        from app.services.trends_service import trends_service
        from app.services.unsplash_service import unsplash_service
        
        # Test Gemini
        print("🤖 Testing Gemini AI...")
        try:
            content = await gemini_service.generate_platform_content(
                business_name="Test Café",
                industry="food & beverage",
                campaign_goal="Test content generation",
                platform="instagram",
                brand_voice="friendly"
            )
            print(f"   ✅ Gemini: Generated {content.get('character_count', 0)} characters")
        except Exception as e:
            print(f"   ❌ Gemini: {e}")
        
        # Test Trends
        print("📈 Testing Google Trends...")
        try:
            trends = await trends_service.get_trending_searches()
            print(f"   ✅ Trends: Found {len(trends)} trending topics")
        except Exception as e:
            print(f"   ❌ Trends: {e}")
        
        # Test Unsplash
        print("🖼️  Testing Unsplash...")
        try:
            photos = await unsplash_service.search_photos("coffee", per_page=3)
            print(f"   ✅ Unsplash: Found {len(photos)} photos")
        except Exception as e:
            print(f"   ❌ Unsplash: {e}")
        
    except ImportError as e:
        print(f"❌ Service import error: {e}")

def check_environment():
    """Check development environment."""
    print("🔧 Environment Check:")
    
    # Check Python version
    if sys.version_info >= (3, 9):
        print(f"   ✅ Python {sys.version.split()[0]}")
    else:
        print(f"   ❌ Python {sys.version.split()[0]} (need 3.9+)")
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("   ✅ .env file exists")
    else:
        print("   ❌ .env file missing")
    
    # Check virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("   ✅ Virtual environment active")
    else:
        print("   ⚠️  Virtual environment not detected")
    
    # Check key dependencies
    try:
        import fastapi
        print(f"   ✅ FastAPI {fastapi.__version__}")
    except ImportError:
        print("   ❌ FastAPI not installed")
    
    try:
        import google.generativeai
        print("   ✅ Google Generative AI installed")
    except ImportError:
        print("   ❌ Google Generative AI not installed")

async def main():
    """Main test function."""
    print("🧪 Vyralflow AI Development Test Suite")
    print("=" * 50)
    
    check_environment()
    
    if "--env-only" in sys.argv:
        return
    
    # Test services
    if "--services" in sys.argv or "--all" in sys.argv:
        await test_services()
    
    # Test agents
    if "--agents" in sys.argv or "--all" in sys.argv:
        await test_agents()
    
    # Test orchestrator
    if "--orchestrator" in sys.argv or "--all" in sys.argv:
        await test_orchestrator()
    
    print("\n" + "=" * 50)
    print("🎉 Development tests completed!")
    print("\n💡 Usage:")
    print("   python dev_test.py --all           # Run all tests")
    print("   python dev_test.py --env-only      # Environment check only")
    print("   python dev_test.py --services      # Test external services")
    print("   python dev_test.py --agents        # Test individual agents")
    print("   python dev_test.py --orchestrator  # Test full orchestrator")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("🧪 Running environment check only...")
        print("Use --help to see all options\n")
        asyncio.run(main())
    else:
        asyncio.run(main())