#!/usr/bin/env python3
"""
Test script to verify API configuration and Gemini integration
"""
import asyncio
import os
from app.core.config import settings
from app.services.gemini_service import gemini_service

async def test_api_configuration():
    """Test API configuration and connectivity"""
    print("🔍 Testing API Configuration...")
    print("=" * 50)
    
    # Test environment variables
    print("📋 Environment Variables:")
    print(f"   GEMINI_API_KEY: {'✅ Set' if settings.gemini_api_key else '❌ Missing'}")
    print(f"   UNSPLASH_ACCESS_KEY: {'✅ Set' if settings.unsplash_access_key else '❌ Missing'}")
    print(f"   GOOGLE_CLOUD_PROJECT: {'✅ Set' if settings.google_cloud_project else '❌ Missing'}")
    
    if settings.gemini_api_key:
        print(f"   Gemini Key Preview: {settings.gemini_api_key[:10]}...{settings.gemini_api_key[-4:]}")
    
    print()
    
    # Test Gemini API
    print("🤖 Testing Gemini API...")
    try:
        test_content = await gemini_service.generate_platform_content(
            business_name="Test Business",
            industry="technology",
            campaign_goal="increase brand awareness",
            platform="instagram",
            brand_voice="professional",
            target_audience="tech professionals",
            trending_topics=["AI", "innovation"],
            keywords=["technology", "growth"]
        )
        
        print("✅ Gemini API: Working!")
        print(f"   Generated text preview: {test_content.get('text', '')[:100]}...")
        print(f"   Generated hashtags: {test_content.get('hashtags', [])}")
        
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
    
    print()
    print("🚀 Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_api_configuration())