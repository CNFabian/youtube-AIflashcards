"""
Data models for YouTube Flashcards AI application
"""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, validator
import re
from uuid import uuid4


class FlashcardRequest(BaseModel):
    """Request model for flashcard generation"""
    youtube_url: str = Field(..., description="YouTube video URL")
    num_cards: int = Field(10, ge=1, le=50, description="Number of flashcards to generate")
    difficulty_level: Literal["easy", "medium", "hard", "mixed"] = Field(
        "mixed", 
        description="Difficulty level of flashcards"
    )
    subject_focus: Optional[str] = Field(
        None, 
        max_length=100,
        description="Specific subject or topic to focus on"
    )
    language: str = Field("en", description="Language code for transcript")
    
    @validator('youtube_url')
    def validate_youtube_url(cls, v):
        """Validate YouTube URL format"""
        youtube_regex = (
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        if not re.match(youtube_regex, v):
            raise ValueError('Invalid YouTube URL format')
        return v
    
    @validator('num_cards')
    def validate_num_cards(cls, v):
        """Ensure reasonable number of flashcards"""
        if v < 1:
            raise ValueError('Must generate at least 1 flashcard')
        if v > 50:
            raise ValueError('Cannot generate more than 50 flashcards per request')
        return v


class Flashcard(BaseModel):
    """Individual flashcard model"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    question: str = Field(..., min_length=10, description="Question text")
    answer: str = Field(..., min_length=5, description="Answer text")
    difficulty: Literal["easy", "medium", "hard"] = Field(..., description="Difficulty level")
    topic: Optional[str] = Field(None, description="Topic or category")
    explanation: Optional[str] = Field(None, description="Additional explanation or context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the capital of France?",
                "answer": "Paris",
                "difficulty": "easy",
                "topic": "Geography",
                "explanation": "Paris has been the capital of France since 987 AD."
            }
        }


class FlashcardSet(BaseModel):
    """Collection of flashcards from a video"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    video_url: str
    video_title: str
    video_id: str
    channel_name: Optional[str] = None
    duration: Optional[int] = None  # in seconds
    flashcards: List[Flashcard]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    transcript_length: int = 0
    language: str = "en"
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_url": "https://youtube.com/watch?v=abc123",
                "video_title": "Introduction to Python",
                "video_id": "abc123",
                "flashcards": [
                    {
                        "question": "What is Python?",
                        "answer": "A high-level programming language",
                        "difficulty": "easy"
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TranscriptSegment(BaseModel):
    """Transcript segment from YouTube"""
    text: str
    start: float
    duration: float
    
    
class VideoTranscript(BaseModel):
    """Complete video transcript"""
    video_id: str
    video_title: Optional[str] = None
    segments: List[TranscriptSegment]
    full_text: str
    language: str
    duration: float  # Total duration in seconds