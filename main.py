"""
YouTube to Flashcards AI - FastAPI Backend
Complete main.py with frontend integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import ValidationError
import os
import sys
from datetime import datetime
from typing import Optional
import logging
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import services and models
from services.transcript import TranscriptService
from services.ai_processor import AIProcessor
from models import (
    FlashcardRequest,
    FlashcardSet,
    Flashcard,
    ErrorResponse,
    HealthResponse
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="YouTube to Flashcards AI",
    description="Convert YouTube educational videos into interactive study flashcards using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000",
        "*"  # Allow all origins in development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend (if frontend directory exists)
if os.path.exists("frontend"):
    # Serve CSS files
    if os.path.exists("frontend/css"):
        app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
    
    # Serve JS files
    if os.path.exists("frontend/js"):
        app.mount("/js", StaticFiles(directory="frontend/js"), name="js")
    
    # Serve assets
    if os.path.exists("frontend/assets"):
        app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")
    
    logger.info("Frontend static files mounted successfully")
else:
    logger.warning("Frontend directory not found. API-only mode.")

# Initialize services
transcript_service = TranscriptService()
ai_processor = AIProcessor()

# Root endpoint - serve frontend or API info
@app.get("/", include_in_schema=False)
async def read_root():
    """Serve the frontend index.html if available, otherwise return API info"""
    if os.path.exists("frontend/index.html"):
        return FileResponse('frontend/index.html')
    return {
        "name": "YouTube to Flashcards AI API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "frontend": "Not found - please add frontend files to /frontend directory"
    }

# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check if the API is healthy and running"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow()
    )

# API v1 endpoints
@app.get("/api/v1", tags=["API Info"])
async def api_info():
    """Get API version and endpoints information"""
    return {
        "version": "1.0.0",
        "endpoints": {
            "generate_flashcards": "/api/v1/flashcards/generate",
            "health": "/health",
            "documentation": "/docs"
        },
        "description": "YouTube to Flashcards AI API"
    }

# Main flashcard generation endpoint
@app.post("/api/v1/flashcards/generate", response_model=FlashcardSet, tags=["Flashcards"])
async def generate_flashcards(request: FlashcardRequest):
    """
    Generate flashcards from a YouTube video
    
    Args:
        request: FlashcardRequest containing YouTube URL and preferences
        
    Returns:
        FlashcardSet with generated flashcards
    """
    logger.info(f"Generating flashcards for URL: {request.youtube_url}")
    
    try:
        # Step 1: Extract video ID and validate URL
        video_id = transcript_service.extract_video_id(request.youtube_url)
        if not video_id:
            raise HTTPException(
                status_code=400,
                detail="Invalid YouTube URL. Please provide a valid YouTube video URL."
            )
        
        # Step 2: Get video metadata
        logger.info(f"Fetching metadata for video ID: {video_id}")
        metadata = transcript_service.get_video_metadata(request.youtube_url)
        
        # Step 3: Extract transcript
        logger.info(f"Extracting transcript for video ID: {video_id}")
        transcript_data = transcript_service.get_transcript(
            request.youtube_url,
            language=request.language,
            preserve_formatting=False
        )
        
        if not transcript_data or not transcript_data.get('full_text'):
            raise HTTPException(
                status_code=404,
                detail="Could not extract transcript. The video may not have captions enabled."
            )
        
        # Step 4: Generate flashcards using AI
        logger.info(f"Generating {request.num_cards} flashcards with {request.difficulty_level} difficulty")
        flashcards_data = ai_processor.generate_flashcards(
            transcript=transcript_data['full_text'],
            num_cards=request.num_cards,
            difficulty_level=request.difficulty_level,
            subject_focus=request.subject_focus,
            video_title=transcript_data.get('video_title')
        )
        
        if not flashcards_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate flashcards. Please try again."
            )
        
        # Step 5: Create flashcard objects
        flashcards = []
        for card_data in flashcards_data:
            flashcard = Flashcard(
                question=card_data['question'],
                answer=card_data['answer'],
                difficulty=card_data.get('difficulty', 'medium'),
                topic=card_data.get('topic'),
                explanation=card_data.get('explanation')
            )
            flashcards.append(flashcard)
        
        # Step 6: Create and return FlashcardSet
        flashcard_set = FlashcardSet(
            video_url=request.youtube_url,
            video_title=transcript_data.get('video_title', 'Unknown Title'),
            video_id=video_id,
            channel_name=transcript_data.get('channel_name'),
            duration=transcript_data.get('duration', 0),
            flashcards=flashcards,
            transcript_length=len(transcript_data.get('full_text', '')),
            language=transcript_data.get('language', request.language)
        )
        
        logger.info(f"Successfully generated {len(flashcards)} flashcards for video: {video_id}")
        return flashcard_set
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating flashcards: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

# Sample/demo flashcards endpoint for testing
@app.get("/api/v1/flashcards/sample", response_model=FlashcardSet, tags=["Flashcards"])
async def get_sample_flashcards():
    """Get sample flashcards for testing and demonstration"""
    
    sample_flashcards = [
        Flashcard(
            question="What is machine learning?",
            answer="Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
            difficulty="easy",
            topic="Fundamentals",
            explanation="ML allows computers to learn patterns from data rather than following explicit instructions."
        ),
        Flashcard(
            question="What are the three main types of machine learning?",
            answer="Supervised Learning (learning from labeled data), Unsupervised Learning (finding patterns in unlabeled data), and Reinforcement Learning (learning through rewards and penalties).",
            difficulty="medium",
            topic="ML Types"
        ),
        Flashcard(
            question="Explain the concept of overfitting.",
            answer="Overfitting occurs when a model learns the training data too well, including noise and outliers, resulting in poor generalization to new, unseen data.",
            difficulty="hard",
            topic="Model Evaluation"
        ),
        Flashcard(
            question="What is a neural network?",
            answer="A computational model inspired by the human brain, consisting of interconnected nodes (neurons) organized in layers that process information.",
            difficulty="medium",
            topic="Deep Learning"
        ),
        Flashcard(
            question="What is gradient descent?",
            answer="An optimization algorithm used to minimize the loss function by iteratively adjusting model parameters in the direction of steepest descent.",
            difficulty="hard",
            topic="Optimization"
        )
    ]
    
    return FlashcardSet(
        video_url="https://www.youtube.com/watch?v=demo",
        video_title="Sample Machine Learning Tutorial",
        video_id="demo123",
        channel_name="Demo Channel",
        duration=600,
        flashcards=sample_flashcards,
        transcript_length=5000,
        language="en"
    )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "detail": str(exc),
            "status_code": 422,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later.",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run startup tasks"""
    logger.info("Starting YouTube to Flashcards AI API...")
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        logger.warning("OpenAI API key not configured! Please set OPENAI_API_KEY in .env file")
    else:
        logger.info("OpenAI API key configured ✓")
    
    # Check if frontend exists
    if os.path.exists("frontend/index.html"):
        logger.info("Frontend files found ✓")
    else:
        logger.info("Frontend files not found - API-only mode")
    
    logger.info("API ready at http://localhost:8000")
    logger.info("API documentation available at http://localhost:8000/docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run cleanup tasks"""
    logger.info("Shutting down YouTube to Flashcards AI API...")

# Main entry point
if __name__ == "__main__":
    # Configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    # Log configuration
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Auto-reload: {reload}")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )