#!/usr/bin/env python3
"""
Direct test of Unsplash API integration
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_services import unsplash_service

async def test_unsplash():
    print("🧪 Testing Unsplash API Integration")
    print("=" * 50)
    
    # Test with different search terms
    test_terms = ["photography", "business", "technology"]
    
    for term in test_terms:
        print(f"\n🔍 Searching for: '{term}'")
        try:
            images = await unsplash_service.search_images(term, 3)
            print(f"📸 Found {len(images)} images")
            
            for i, img in enumerate(images[:2]):
                print(f"  {i+1}. {img.get('description', 'No description')}")
                print(f"     📷 By: {img.get('photographer', 'Unknown')}")
                print(f"     🔗 Source: {img.get('source', 'Unknown')}")
                print(f"     🆔 ID: {img.get('id', 'No ID')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ Unsplash test complete")

if __name__ == "__main__":
    asyncio.run(test_unsplash())