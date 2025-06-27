#!/usr/bin/env python3
"""Test the fixed color palette generation."""
import sys
import asyncio
import os
sys.path.append('.')

from app.agents.visual_designer import VisualDesignerAgent
from app.models.agent import AgentInput

async def test_color_palette_fix():
    """Test the enhanced color palette generation."""
    print("🧪 Testing enhanced color palette generation...")
    
    # Create a test agent input
    agent_input = AgentInput(
        campaign_id="test_campaign_123",
        business_name="TechFlow Solutions",
        industry="technology",
        campaign_goal="Launch innovative productivity app",
        brand_voice="professional",
        target_audience="young professionals",
        target_platforms=["instagram", "linkedin"],
        previous_results={}
    )
    
    # Create visual designer agent
    visual_agent = VisualDesignerAgent()
    
    try:
        # Test AI color palette generation
        print("\n🎨 Testing AI color palette generation...")
        visual_themes = ["modern", "professional", "innovative", "clean"]
        ai_palette = await visual_agent._generate_ai_color_palette(agent_input, visual_themes)
        
        if ai_palette:
            print(f"✅ AI Palette generated: {ai_palette}")
            
            # Test diversity validation
            print("\n🔍 Testing enhanced diversity validation...")
            is_diverse = visual_agent._validate_enhanced_color_diversity(ai_palette)
            print(f"Diversity check: {'✅ PASSED' if is_diverse else '❌ FAILED'}")
            
            # Analyze each color
            print("\n📊 Color analysis:")
            for i, color in enumerate(ai_palette):
                is_brown = visual_agent._is_brown_beige_color(color)
                is_gray = visual_agent._is_gray_color(color)
                is_vibrant = visual_agent._is_vibrant_color(color)
                
                print(f"  {i+1}. {color} - Brown/Beige: {is_brown}, Gray: {is_gray}, Vibrant: {is_vibrant}")
        else:
            print("❌ AI palette generation failed")
            
        # Test fallback generation
        print("\n🔄 Testing fallback color generation...")
        fallback_palette = await visual_agent._generate_color_palette(agent_input, visual_themes)
        print(f"Fallback palette: {fallback_palette}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_color_palette_fix())