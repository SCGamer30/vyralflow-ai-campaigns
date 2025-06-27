from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import time
import uvicorn
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import db_manager
from app.core.exceptions import VyralflowException
from app.core.google_auth import setup_google_auth
from app.api.routes import campaigns, health, agents
from app.utils.logging import setup_logging, get_logger
from app.services.unsplash_service import unsplash_service

# Setup logging
setup_logging(level="DEBUG" if settings.debug else "INFO")
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    
    try:
        # Set up Google authentication
        setup_google_auth()
        
        # Validate API keys
        missing_keys = settings.validate_required_keys()
        if missing_keys:
            logger.error(f"Missing required API keys: {', '.join(missing_keys)}")
            logger.error("Please check your .env file configuration")
            # Don't exit in production, just warn
            if settings.debug:
                logger.warning("Running in debug mode with missing keys - some features may not work")
        else:
            logger.info("✅ All required API keys configured")
        
        # Initialize database
        await db_manager.initialize_collections()
        logger.info("Database initialized successfully")
        
        # Perform initial health checks
        db_health = await db_manager.health_check()
        logger.info(f"Database health: {db_health.get('status', 'unknown')}")
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Application shutdown initiated")
    
    try:
        # Close HTTP clients
        await unsplash_service.close()
        
        # Close database connections
        db_manager.close()
        
        logger.info("Application shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Vyralflow AI",
    description="""
    # Vyralflow AI - Multi-Agent Social Media Campaign Generator

    **Vyralflow AI** is a powerful multi-agent AI system that automatically generates viral social media campaigns using Google Cloud Agent Development Kit (ADK).

    ## 🚀 How It Works

    The system coordinates 4 specialized AI agents that work sequentially:

    1. **Trend Analyzer Agent** - Analyzes social media trends using Google Trends and Reddit API
    2. **Content Writer Agent** - Generates platform-specific content using Google Gemini AI
    3. **Visual Designer Agent** - Suggests visual concepts and finds images using Unsplash API
    4. **Campaign Scheduler Agent** - Optimizes posting times and creates scheduling recommendations

    ## 📝 Quick Start

    1. **Create a Campaign**: POST to `/api/campaigns/create` with your business details
    2. **Track Progress**: GET `/api/campaigns/{campaign_id}/status` to monitor agent progress
    3. **Get Results**: GET `/api/campaigns/{campaign_id}/results` when completed

    ## 🔧 Key Features

    - **Multi-Platform Support**: Instagram, Twitter, LinkedIn, Facebook, TikTok
    - **Real-Time Progress**: Track agent execution progress in real-time
    - **Intelligent Fallbacks**: Robust error handling with fallback mechanisms
    - **Industry-Specific**: Optimized for different business industries
    - **Brand Voice Adaptation**: Customizable brand voice and tone

    ## 📊 Supported Platforms

    - **Instagram**: Optimized for visual content and engagement
    - **Twitter**: Concise, trending content under 280 characters
    - **LinkedIn**: Professional, industry-focused content
    - **Facebook**: Community-building, shareable content
    - **TikTok**: Trendy, entertainment-focused content

    ## 🎯 Industries Supported

    Food & Beverage, Technology, Retail, Healthcare, Finance, Education, Real Estate, Automotive, and more.

    ## 🔗 External APIs Used

    - **Google Gemini AI** (FREE tier) - Content generation
    - **Google Trends** (FREE) - Trend analysis
    - **Reddit API** (FREE) - Additional trend data
    - **Unsplash API** - High-quality images
    - **Google Firestore** - Data storage

    ## 📈 Performance

    - Average campaign generation time: 2-5 minutes
    - Concurrent campaign support: Up to 10 campaigns
    - Rate limiting: 60 requests per minute per IP
    - 99.9% uptime with fallback mechanisms

    ## 🛠️ Monitoring

    Use the `/health` endpoints to monitor system status and agent health.
    """,
    version=settings.version,
    openapi_tags=[
        {
            "name": "campaigns",
            "description": "Campaign creation, management, and results retrieval",
        },
        {
            "name": "health", 
            "description": "System health monitoring and status checks",
        },
        {
            "name": "agents",
            "description": "AI agent status and information endpoints",
        },
    ],
    contact={
        "name": "Vyralflow AI Support",
        "email": "support@vyralflow.ai",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    debug=settings.debug
)


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom schema information
    openapi_schema["info"]["x-logo"] = {
        "url": "https://vyralflow.ai/logo.png"
    }
    
    # Add server information
    openapi_schema["servers"] = [
        {"url": "https://api.vyralflow.ai", "description": "Production server"},
        {"url": "http://localhost:8000", "description": "Development server"},
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
)

# Add trusted host middleware for production
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.vyralflow.ai", "localhost", "127.0.0.1"]
    )


# Request/Response middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time and request ID to response headers."""
    start_time = time.time()
    request_id = f"req_{int(start_time * 1000)}"
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Add headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{process_time:.4f}s"
    
    # Log request
    logger.info(
        f"Request {request_id}: {request.method} {request.url.path} "
        f"completed in {process_time:.4f}s with status {response.status_code}"
    )
    
    return response


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    """Global exception handling middleware."""
    try:
        return await call_next(request)
    except VyralflowException as e:
        logger.error(f"VyralflowException: {e.message} (Code: {e.error_code})")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error_code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        )
    except HTTPException:
        # Re-raise HTTP exceptions to let FastAPI handle them
        raise
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": "An internal error occurred. Please try again later.",
                "details": {"error": str(e)} if settings.debug else {}
            }
        )


# Include routers
app.include_router(
    campaigns.router,
    prefix=settings.api_v1_prefix,
    dependencies=[]
)

app.include_router(
    health.router,
    prefix=settings.api_v1_prefix,
    dependencies=[]
)

app.include_router(
    agents.router,
    prefix=settings.api_v1_prefix,
    dependencies=[]
)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.version,
        "documentation": "/docs",
        "health_check": "/api/health",
        "api_prefix": settings.api_v1_prefix,
        "status": "operational"
    }


# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error_code": "NOT_FOUND",
            "message": "The requested resource was not found",
            "path": str(request.url.path),
            "method": request.method
        }
    )


@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc: HTTPException):
    """Custom 405 handler."""
    return JSONResponse(
        status_code=405,
        content={
            "success": False,
            "error_code": "METHOD_NOT_ALLOWED",
            "message": f"Method {request.method} not allowed for this endpoint",
            "path": str(request.url.path),
            "allowed_methods": exc.headers.get("Allow", "").split(", ") if exc.headers else []
        }
    )


@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    """Custom validation error handler."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": exc.errors() if hasattr(exc, 'errors') else str(exc)
        }
    )


# Health check for load balancers
@app.get("/ping")
async def ping():
    """Simple ping endpoint for load balancer health checks."""
    return {"status": "ok", "timestamp": time.time()}


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
        access_log=True,
        loop="asyncio"
    )