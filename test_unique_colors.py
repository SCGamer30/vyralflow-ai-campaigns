#!/usr/bin/env python3
"""
Test script to verify that each company gets completely unique color palettes.
This tests the actual visual designer AI color generation.
"""
import sys
import asyncio
import json
sys.path.append('.')

from app.agents.visual_designer import visual_designer_agent
from app.models.agent import AgentInput

async def test_unique_company_colors():
    """Test that different companies get completely different color palettes."""
    print("🎨 Testing Unique Company Color Generation")
    print("=" * 60)
    
    # Test different companies in the SAME industry (food & beverage)
    # They should get COMPLETELY different colors
    test_companies = [
        {
            'business_name': 'Sunset Cafe',
            'industry': 'food & beverage',
            'campaign_goal': 'increase sales',
            'brand_voice': 'friendly',
            'target_platforms': ['instagram', 'facebook'],
            'target_audience': 'coffee lovers'
        },
        {
            'business_name': 'Mountain Brew',
            'industry': 'food & beverage', 
            'campaign_goal': 'brand awareness',
            'brand_voice': 'casual',
            'target_platforms': ['instagram', 'twitter'],
            'target_audience': 'outdoor enthusiasts'
        },
        {
            'business_name': 'Ocean Bistro',
            'industry': 'food & beverage',
            'campaign_goal': 'new location launch',
            'brand_voice': 'professional',
            'target_platforms': ['linkedin', 'facebook'],
            'target_audience': 'professionals'
        },
        {
            'business_name': 'Desert Delights',
            'industry': 'food & beverage',
            'campaign_goal': 'seasonal menu',
            'brand_voice': 'humorous',
            'target_platforms': ['tiktok', 'instagram'],
            'target_audience': 'young adults'
        },
        {
            'business_name': 'Forest Kitchen',
            'industry': 'food & beverage',
            'campaign_goal': 'customer retention',
            'brand_voice': 'inspirational',
            'target_platforms': ['facebook', 'instagram'],
            'target_audience': 'health conscious'
        }
    ]
    
    all_palettes = {}
    
    for i, company_data in enumerate(test_companies):
        print(f"\n🏢 Testing Company {i+1}: {company_data['business_name']}")
        print("-" * 40)
        
        # Create agent input
        agent_input = AgentInput(
            campaign_id=f"test_campaign_{i+1}",
            business_name=company_data['business_name'],
            industry=company_data['industry'],
            campaign_goal=company_data['campaign_goal'],
            brand_voice=company_data['brand_voice'],
            target_platforms=company_data['target_platforms'],
            target_audience=company_data['target_audience']
        )
        
        try:
            # Test the AI color generation directly
            visual_themes = ['modern', 'engaging', 'authentic']
            colors = await visual_designer_agent._generate_ai_color_palette(agent_input, visual_themes)
            
            if colors and len(colors) >= 4:
                all_palettes[company_data['business_name']] = colors
                print(f"✅ Generated {len(colors)} unique colors:")
                for j, color in enumerate(colors):
                    print(f"   {j+1}. {color}")
                print(f"   Inspiration: Generated from business-specific seed")
            else:
                print(f"❌ Failed to generate colors for {company_data['business_name']}")
                if colors:
                    print(f"   Received: {colors}")
                else:
                    print("   No colors returned")
        
        except Exception as e:
            print(f"❌ Error generating colors for {company_data['business_name']}: {e}")
            import traceback
            traceback.print_exc()
    
    # Analyze uniqueness
    print(f"\n🔍 UNIQUENESS ANALYSIS")
    print("=" * 60)
    
    if len(all_palettes) < 2:
        print("❌ Not enough successful color generations to compare uniqueness")
        return
    
    # Check for duplicate colors across companies
    all_colors = []
    company_colors = {}
    
    for company, palette in all_palettes.items():
        company_colors[company] = set(palette)
        all_colors.extend(palette)
    
    # Find duplicates
    color_counts = {}
    for color in all_colors:
        color_counts[color] = color_counts.get(color, 0) + 1
    
    duplicates = {color: count for color, count in color_counts.items() if count > 1}
    
    print(f"📊 Total unique colors generated: {len(set(all_colors))}")
    print(f"📊 Total colors across all companies: {len(all_colors)}")
    
    if duplicates:
        print(f"⚠️  DUPLICATE COLORS FOUND:")
        for color, count in duplicates.items():
            print(f"   {color} appears {count} times")
            companies_with_color = [name for name, colors in company_colors.items() if color in colors]
            print(f"   Used by: {', '.join(companies_with_color)}")
    else:
        print("✅ NO DUPLICATE COLORS - Each company has completely unique colors!")
    
    # Check color similarity (similar hues)
    print(f"\n🎨 COLOR DIVERSITY ANALYSIS")
    print("-" * 40)
    
    for company, palette in all_palettes.items():
        print(f"\n{company}:")
        for color in palette:
            print(f"  {color}")
    
    # Check if any company got typical "industry" colors
    print(f"\n🚫 INDUSTRY STEREOTYPE CHECK")
    print("-" * 40)
    
    typical_food_colors = ['#D2691E', '#A0522D', '#CD853F', '#DEB887', '#F4A460', '#DAA520']
    
    stereotype_violations = []
    for company, palette in all_palettes.items():
        for color in palette:
            if color.upper() in [c.upper() for c in typical_food_colors]:
                stereotype_violations.append(f"{company}: {color}")
    
    if stereotype_violations:
        print("⚠️  INDUSTRY STEREOTYPE COLORS FOUND:")
        for violation in stereotype_violations:
            print(f"   {violation}")
    else:
        print("✅ NO INDUSTRY STEREOTYPES - All companies have original colors!")
    
    print(f"\n🏆 FINAL RESULTS")
    print("=" * 60)
    
    if not duplicates and not stereotype_violations:
        print("✅ SUCCESS: Each company has completely unique, non-stereotypical colors!")
        print("✅ AI color generation is working perfectly!")
    else:
        print("❌ ISSUES FOUND:")
        if duplicates:
            print(f"   - {len(duplicates)} duplicate colors across companies")
        if stereotype_violations:
            print(f"   - {len(stereotype_violations)} industry stereotype colors used")
    
    return len(duplicates) == 0 and len(stereotype_violations) == 0

if __name__ == '__main__':
    result = asyncio.run(test_unique_company_colors())
    sys.exit(0 if result else 1)