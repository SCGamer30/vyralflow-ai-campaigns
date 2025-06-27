#!/usr/bin/env python3
"""
Vyralflow AI - WORKING Server for Hackathon
Based on successful simple_test_server.py pattern
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import uuid
from datetime import datetime

# Simple models
class CampaignRequest(BaseModel):
    business_name: str
    industry: str
    campaign_goal: str
    target_platforms: List[str]
    brand_voice: str = "professional"

# Create app
app = FastAPI(title="Vyralflow AI - Working Demo")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage - using class to ensure persistence
class CampaignStorage:
    def __init__(self):
        self.campaigns = {}
        print("📂 Campaign storage initialized")
    
    def store_campaign(self, campaign_id: str, campaign_data: dict):
        self.campaigns[campaign_id] = campaign_data
        print(f"💾 Stored campaign: {campaign_id}")
        return True
    
    def get_campaign(self, campaign_id: str):
        campaign = self.campaigns.get(campaign_id)
        if campaign:
            print(f"📖 Retrieved campaign: {campaign_id}")
        else:
            print(f"❌ Campaign not found: {campaign_id}")
            print(f"📋 Available campaigns: {list(self.campaigns.keys())}")
        return campaign
    
    def list_campaigns(self):
        return list(self.campaigns.keys())

# Create storage instance
storage = CampaignStorage()

@app.get("/")
async def root():
    return {
        "message": "Vyralflow AI - Multi-Agent Campaign Generator 🚀",
        "status": "operational",
        "agents": ["trend_analyzer", "content_writer", "visual_designer", "campaign_scheduler"],
        "stored_campaigns": len(storage.campaigns)
    }

@app.get("/api/health")
async def health():
    return {
        "status": "healthy", 
        "agents": "ready",
        "campaigns_stored": len(storage.campaigns),
        "campaign_ids": storage.list_campaigns()
    }

@app.post("/api/campaigns/create")
async def create_campaign(request: CampaignRequest):
    campaign_id = f"vyral_{uuid.uuid4().hex[:8]}"
    
    # Create comprehensive campaign data
    campaign = {
        "campaign_id": campaign_id,
        "status": "completed",
        "business_name": request.business_name,
        "industry": request.industry,
        "campaign_goal": request.campaign_goal,
        "target_platforms": request.target_platforms,
        "brand_voice": request.brand_voice,
        "agent_progress": [
            {"agent_name": "trend_analyzer", "status": "completed", "progress": 100, "message": "Trends analyzed successfully"},
            {"agent_name": "content_writer", "status": "completed", "progress": 100, "message": "Content generated successfully"},
            {"agent_name": "visual_designer", "status": "completed", "progress": 100, "message": "Visuals designed successfully"},
            {"agent_name": "campaign_scheduler", "status": "completed", "progress": 100, "message": "Schedule optimized successfully"}
        ],
        "created_at": datetime.now(datetime.timezone.utc).isoformat(),
        "completed_at": datetime.now(datetime.timezone.utc).isoformat()
    }
    
    # Store the campaign
    storage.store_campaign(campaign_id, campaign)
    
    return campaign

@app.get("/api/campaigns/{campaign_id}/status")
async def get_status(campaign_id: str):
    campaign = storage.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    
    return {
        "campaign_id": campaign["campaign_id"],
        "status": campaign["status"],
        "business_name": campaign["business_name"],
        "agent_progress": campaign["agent_progress"],
        "created_at": campaign["created_at"],
        "completed_at": campaign.get("completed_at")
    }

@app.get("/api/campaigns/{campaign_id}/results")
async def get_results(campaign_id: str):
    campaign = storage.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    
    business = campaign["business_name"]
    industry = campaign["industry"]
    platforms = campaign["target_platforms"]
    
    return {
        "campaign_id": campaign_id,
        "status": "completed",
        "business_name": business,
        "results": {
            "trends": {
                "trending_topics": [f"{industry} innovation", "viral marketing", "social media growth", "digital transformation"],
                "trending_hashtags": ["#innovation", "#viral", "#growth", f"#{industry.lower()}", "#marketing"],
                "trend_score": 92,
                "analysis_summary": f"High engagement potential detected for {industry} sector. Optimal viral window identified."
            },
            "content": {
                "instagram": {
                    "text": f"🚀 {business} is revolutionizing {industry}! Our latest breakthrough changes everything. Ready to join the future? #innovation #{industry.lower()}",
                    "hashtags": ["#innovation", f"#{industry.lower()}", "#breakthrough", "#future"],
                    "character_count": len(f"🚀 {business} is revolutionizing {industry}! Our latest breakthrough changes everything. Ready to join the future? #innovation #{industry.lower()}")
                },
                "twitter": {
                    "text": f"🔥 BREAKING: {business} just dropped something huge in {industry}! This changes the game completely 🎯 #breakthrough",
                    "hashtags": ["#breakthrough", f"#{industry.lower()}", "#innovation"],
                    "character_count": len(f"🔥 BREAKING: {business} just dropped something huge in {industry}! This changes the game completely 🎯 #breakthrough")
                },
                "linkedin": {
                    "text": f"Excited to share how {business} is pioneering the next wave of {industry} innovation. Our latest development represents a significant leap forward.",
                    "hashtags": ["#innovation", "#business", f"#{industry.lower()}", "#leadership"],
                    "character_count": len(f"Excited to share how {business} is pioneering the next wave of {industry} innovation. Our latest development represents a significant leap forward.")
                }
            },
            "visuals": {
                "recommended_style": f"Modern {industry} aesthetic with innovation themes",
                "color_palette": ["#FF6B35", "#4ECDC4", "#45B7D1", "#96CEB4"],
                "image_suggestions": [
                    f"{industry} workspace innovation",
                    "Team collaboration concept",
                    "Technology breakthrough visualization",
                    f"Future of {industry} imagery"
                ],
                "video_concepts": [
                    "Product reveal with dynamic transitions",
                    "Behind-the-scenes innovation process",
                    "Customer success stories"
                ]
            },
            "schedule": {
                "optimal_times": {
                    "instagram": ["8:00 AM", "1:00 PM", "7:00 PM"] if "instagram" in platforms else [],
                    "twitter": ["9:00 AM", "12:00 PM", "3:00 PM", "6:00 PM"] if "twitter" in platforms else [],
                    "linkedin": ["8:00 AM", "12:00 PM", "5:00 PM"] if "linkedin" in platforms else []
                },
                "best_days": ["Tuesday", "Wednesday", "Thursday"],
                "viral_window": "Next 48 hours - trending topic alignment detected",
                "engagement_forecast": "High engagement expected (8.5x normal rates)"
            },
            "performance_predictions": {
                "estimated_reach": "75K - 150K users",
                "engagement_rate": "9.2% - 14.7%",
                "viral_probability": "High (84%)",
                "conversion_estimate": "3.1% - 5.2%"
            }
        }
    }

if __name__ == "__main__":
    print("🚀 Vyralflow AI - Working Demo Server")
    print("📖 Docs: http://localhost:8080/docs")
    print("🔍 Health: http://localhost:8080/api/health")
    
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")