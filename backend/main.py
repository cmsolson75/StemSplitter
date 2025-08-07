from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from contextlib import asynccontextmanager
from config import settings
from api.separate import router
from infra.demucs_model import DemucsModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    if settings.DEBUG:
        print("🎵 Audio Separation API starting in development mode")
    else:
        print("🎵 Audio Separation API starting in production mode")
    
    yield
    
    # Shutdown
    print("🎵 Audio Separation API shutting down")


# Create FastAPI app with production metadata
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
    lifespan=lifespan,
)

# CORS middleware - ADD THIS SECTION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Security middleware for production
# if not settings.DEBUG:
#     app.add_middleware(
#         TrustedHostMiddleware,
#         allowed_hosts=[
#             "localhost",
#             "127.0.0.1",
#             "*.run.app",  # Cloud Run domains
#             "your-domain.com",  # Your custom domain
#         ]
#     )

# Health check endpoint for Cloud Run
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "healthy", "service": "audio-separation-api"}

@router.get("/model-status")
async def model_status():
    try:
        # This will trigger model loading if not already loaded
        model = DemucsModel()
        return {"status": "model loaded", "info": model.get_model_info()}
    except Exception as e:
        return {"status": "model failed", "error": str(e)}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Audio Stem Separation API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "disabled in production"
    }

# Include API routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    
    # Local development server
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )