#!/usr/bin/env python3
"""
Quick fix server - working solution for immediate use
"""
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Request models
class CampaignRequest(BaseModel):
    business_name: str
    industry: str
    campaign_goal: str
    target_platforms: List[str]
    brand_voice: str = "professional"
    target_audience: Optional[str] = None
    keywords: Optional[List[str]] = None

# Response models
class AgentProgress(BaseModel):
    agent_name: str
    status: str
    progress_percentage: int
    message: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class CampaignResponse(BaseModel):
    campaign_id: str
    status: str
    agent_progress: List[AgentProgress]
    created_at: str

def create_quick_app():
    """Create a quick working FastAPI app."""
    app = FastAPI(
        title="Vyralflow AI - Quick Demo",
        description="Multi-Agent Social Media Campaign Generator (Working Demo)",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # In-memory storage
    campaigns = {}
    
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Vyralflow AI - Quick Demo",
            "version": "1.0.0",
            "documentation": "/docs",
            "status": "operational",
            "agents": ["trend_analyzer", "content_writer", "visual_designer", "campaign_scheduler"]
        }
    
    @app.get("/ping")
    async def ping():
        return {"status": "ok", "timestamp": time.time()}
    
    @app.get("/api/health")
    async def health():
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "api": "healthy",
                "agents": "ready",
                "database": "demo_mode"
            }
        }
    
    @app.post("/api/campaigns/create", response_model=CampaignResponse)
    async def create_campaign(request: CampaignRequest):
        campaign_id = f"camp_{uuid.uuid4().hex[:8]}"
        
        # Initialize agent progress
        agents = ["trend_analyzer", "content_writer", "visual_designer", "campaign_scheduler"]
        agent_progress = []
        
        for agent in agents:
            progress = AgentProgress(
                agent_name=agent,
                status="pending",
                progress_percentage=0,
                message="Waiting to start"
            )
            agent_progress.append(progress)
        
        # Store campaign
        campaign = CampaignResponse(
            campaign_id=campaign_id,
            status="processing",
            agent_progress=agent_progress,
            created_at=datetime.utcnow().isoformat()
        )
        
        campaigns[campaign_id] = campaign
        
        # Simulate some progress (for demo)
        import asyncio
        asyncio.create_task(simulate_campaign_progress(campaign_id, campaigns))
        
        return campaign
    
    @app.get("/api/campaigns/{campaign_id}/status", response_model=CampaignResponse)
    async def get_campaign_status(campaign_id: str):
        if campaign_id not in campaigns:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return campaigns[campaign_id]
    
    @app.get("/api/campaigns/{campaign_id}/results")
    async def get_campaign_results(campaign_id: str):
        if campaign_id not in campaigns:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign = campaigns[campaign_id]
        if campaign.status != "completed":
            raise HTTPException(status_code=400, detail="Campaign not completed yet")
        
        # Return sample results
        return {
            "campaign_id": campaign_id,
            "status": "completed",
            "results": {
                "trends": {
                    "trending_topics": ["AI technology", "social media", "digital marketing"],
                    "trending_hashtags": ["#AI", "#socialmedia", "#marketing"],
                    "analysis_summary": "Current trends show high engagement with AI and social media content"
                },
                "content": {
                    "instagram": {
                        "text": f"🚀 Exciting news from {campaign_id}! Our innovative approach is changing the game. #innovation #business",
                        "hashtags": ["#innovation", "#business", "#AI"],
                        "character_count": 98
                    },
                    "twitter": {
                        "text": f"Big announcement from {campaign_id}! 🎯 #innovation #tech",
                        "hashtags": ["#innovation", "#tech"],
                        "character_count": 65
                    }
                },
                "visuals": {
                    "recommended_style": "Modern, professional with tech-focused imagery",
                    "color_palette": ["#2196F3", "#4CAF50", "#FF9800"],
                    "image_suggestions": ["Technology workspace", "Team collaboration", "Innovation concept"]
                },
                "schedule": {
                    "optimal_times": {
                        "instagram": ["8:00 AM", "12:00 PM", "7:00 PM"],
                        "twitter": ["9:00 AM", "3:00 PM", "6:00 PM"]
                    }
                }
            }
        }
    
    @app.get("/api/agents/status")
    async def get_agents_status():
        return [
            {"agent_name": "trend_analyzer", "status": "healthy", "is_healthy": True},
            {"agent_name": "content_writer", "status": "healthy", "is_healthy": True},
            {"agent_name": "visual_designer", "status": "healthy", "is_healthy": True},
            {"agent_name": "campaign_scheduler", "status": "healthy", "is_healthy": True}
        ]
    
    return app

async def simulate_campaign_progress(campaign_id: str, campaigns: dict):
    """Simulate campaign progress for demo."""
    import asyncio
    
    campaign = campaigns[campaign_id]
    agents = ["trend_analyzer", "content_writer", "visual_designer", "campaign_scheduler"]
    
    for i, agent in enumerate(agents):
        await asyncio.sleep(2)  # Wait 2 seconds between agents
        
        # Update agent to running
        for progress in campaign.agent_progress:
            if progress.agent_name == agent:
                progress.status = "running"
                progress.message = f"Executing {agent}..."
                progress.started_at = datetime.utcnow().isoformat()
                break
        
        # Simulate progress
        for percent in range(0, 101, 25):
            await asyncio.sleep(0.5)
            for progress in campaign.agent_progress:
                if progress.agent_name == agent:
                    progress.progress_percentage = percent
                    break
        
        # Mark as completed
        for progress in campaign.agent_progress:
            if progress.agent_name == agent:
                progress.status = "completed"
                progress.progress_percentage = 100
                progress.message = f"{agent} completed successfully"
                progress.completed_at = datetime.utcnow().isoformat()
                break
    
    # Mark campaign as completed
    campaign.status = "completed"

def main():
    """Run the quick server."""
    try:
        print("🚀 Vyralflow AI - Quick Working Demo")
        print("=" * 40)
        print("✅ Ready for immediate use!")
        print("📖 Documentation: http://localhost:8080/docs")
        print("🔍 Health Check: http://localhost:8080/api/health")
        print("🎯 Test Campaign: POST to /api/campaigns/create")
        print("Press Ctrl+C to stop\n")
        
        app = create_quick_app()
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8080,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()