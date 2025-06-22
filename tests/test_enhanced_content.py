#!/usr/bin/env python3
"""
Test Enhanced Platform-Specific Content Generation
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_gemini_service import enhanced_gemini_service
from platform_content_models import ContentGenerationContext

async def test_enhanced_content():
    print("🚀 Testing Enhanced Platform-Specific Content Generation")
    print("=" * 70)
    
    # Test context
    context = ContentGenerationContext(
        business_name="TechFlow Solutions",
        industry="Technology",
        campaign_goal="Launch innovative AI platform",
        brand_voice="innovative",
        target_audience="tech entrepreneurs",
        trending_topics=["AI innovation", "digital transformation", "startup growth"],
        trending_hashtags=["#AI", "#innovation", "#tech", "#startup"],
        platform="instagram",
        content_type="advanced"
    )
    
    platforms = ["instagram", "twitter", "linkedin", "tiktok"]
    
    for platform in platforms:
        print(f"\n📱 Testing {platform.upper()} Content Generation...")
        context.platform = platform
        
        try:
            advanced_content = await enhanced_gemini_service.generate_platform_content_advanced(context)
            
            print(f"✅ {platform.upper()} Content Generated:")
            print(f"   📝 Text: {advanced_content.text[:100]}...")
            print(f"   🏷️  Hashtags: {advanced_content.hashtags}")
            print(f"   🎯 Content Pillars: {advanced_content.content_pillars}")
            print(f"   💡 Viral Elements: {advanced_content.viral_elements}")
            
            # Check platform-specific formats
            if platform == "instagram" and advanced_content.instagram_stories:
                stories = advanced_content.instagram_stories
                print(f"   📱 Instagram Stories: {len(stories)} slides")
                for story in stories[:2]:
                    print(f"      Slide {story.slide_number}: {story.text_overlay}")
            
            elif platform == "twitter" and advanced_content.twitter_thread:
                thread = advanced_content.twitter_thread
                print(f"   🧵 Twitter Thread: {len(thread)} tweets")
                for tweet in thread[:2]:
                    print(f"      Tweet {tweet.tweet_number}: {tweet.text[:60]}...")
            
            elif platform == "linkedin" and advanced_content.linkedin_article:
                article = advanced_content.linkedin_article
                print(f"   📄 LinkedIn Article: {len(article)} sections")
                for section in article[:2]:
                    print(f"      {section.section_type}: {section.heading}")
            
            elif platform == "tiktok" and advanced_content.tiktok_concept:
                tiktok = advanced_content.tiktok_concept
                print(f"   🎬 TikTok: {tiktok.video_duration}")
                print(f"      Hook: {tiktok.hook}")
                
        except Exception as e:
            print(f"❌ Error generating {platform} content: {e}")
    
    print("\n✅ Enhanced Content Generation Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_content())