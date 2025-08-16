"""
AI-powered Flashcard Generation Service using OpenAI
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AIProcessor:
    """Service for generating flashcards using OpenAI GPT"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
    def generate_flashcards(
        self,
        transcript: str,
        num_cards: int = 10,
        difficulty_level: str = "mixed",
        subject_focus: Optional[str] = None,
        video_title: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate flashcards from transcript using AI
        
        Args:
            transcript: Video transcript text
            num_cards: Number of flashcards to generate
            difficulty_level: Difficulty level (easy, medium, hard, mixed)
            subject_focus: Specific topic to focus on
            video_title: Title of the video for context
            
        Returns:
            List of flashcard dictionaries
        """
        try:
            # Create the system prompt
            system_prompt = self._create_system_prompt()
            
            # Create the user prompt
            user_prompt = self._create_user_prompt(
                transcript=transcript,
                num_cards=num_cards,
                difficulty_level=difficulty_level,
                subject_focus=subject_focus,
                video_title=video_title
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Extract flashcards from response
            flashcards = result.get('flashcards', [])
            
            # Validate and clean flashcards
            validated_flashcards = self._validate_flashcards(flashcards, difficulty_level)
            
            return validated_flashcards
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            raise ValueError("AI response was not valid JSON")
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            raise Exception(f"Failed to generate flashcards: {str(e)}")
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for flashcard generation"""
        return """You are an expert educational content creator specializing in creating effective flashcards for learning and retention.

Your task is to analyze video transcripts and create high-quality flashcards that:
1. Test key concepts and important information from the content
2. Are clear, concise, and unambiguous
3. Follow spaced repetition best practices
4. Include a mix of factual recall, conceptual understanding, and application questions
5. Have appropriate difficulty levels

You must respond with valid JSON in the following format:
{
    "flashcards": [
        {
            "question": "Clear, specific question",
            "answer": "Concise, accurate answer",
            "difficulty": "easy|medium|hard",
            "topic": "Main topic or category",
            "explanation": "Optional additional context or explanation"
        }
    ]
}

Guidelines:
- Questions should be specific and have clear answers
- Avoid yes/no questions unless they test important facts
- Include 'why' and 'how' questions for deeper understanding
- Answers should be concise but complete
- Add explanations for complex topics
- Ensure factual accuracy based on the transcript content"""
    
    def _create_user_prompt(
        self,
        transcript: str,
        num_cards: int,
        difficulty_level: str,
        subject_focus: Optional[str],
        video_title: Optional[str]
    ) -> str:
        """Create the user prompt with transcript and requirements"""
        # Truncate transcript if too long (to stay within token limits)
        max_transcript_length = 8000
        if len(transcript) > max_transcript_length:
            transcript = transcript[:max_transcript_length] + "..."
        
        prompt = f"""Create {num_cards} flashcards from the following video transcript.

Video Title: {video_title or 'Not provided'}
Difficulty Level: {difficulty_level}
{f'Subject Focus: {subject_focus}' if subject_focus else ''}

Transcript:
{transcript}

Requirements:
1. Generate exactly {num_cards} flashcards
2. """
        
        if difficulty_level == "mixed":
            prompt += "Include a mix of easy, medium, and hard difficulty questions"
        else:
            prompt += f"All flashcards should be {difficulty_level} difficulty"
        
        if subject_focus:
            prompt += f"\n3. Focus particularly on topics related to: {subject_focus}"
        
        prompt += """
4. Ensure questions test understanding, not just memorization
5. Make answers clear and self-contained
6. Include topic categorization for each flashcard
7. Add brief explanations where helpful for understanding

Return the flashcards as valid JSON."""
        
        return prompt
    
    def _validate_flashcards(
        self, 
        flashcards: List[Dict], 
        requested_difficulty: str
    ) -> List[Dict[str, Any]]:
        """
        Validate and clean flashcards from AI response
        
        Args:
            flashcards: Raw flashcards from AI
            requested_difficulty: Requested difficulty level
            
        Returns:
            Validated and cleaned flashcards
        """
        validated = []
        
        for card in flashcards:
            # Ensure required fields exist
            if not card.get('question') or not card.get('answer'):
                continue
            
            # Set difficulty if not provided or invalid
            difficulty = card.get('difficulty', 'medium').lower()
            if difficulty not in ['easy', 'medium', 'hard']:
                if requested_difficulty == 'mixed':
                    difficulty = 'medium'
                else:
                    difficulty = requested_difficulty
            
            validated_card = {
                'question': str(card['question']).strip(),
                'answer': str(card['answer']).strip(),
                'difficulty': difficulty,
                'topic': card.get('topic', 'General'),
                'explanation': card.get('explanation', None)
            }
            
            # Skip cards with very short questions or answers
            if len(validated_card['question']) < 10 or len(validated_card['answer']) < 3:
                continue
            
            validated.append(validated_card)
        
        return validated
    
    def enhance_flashcards(
        self,
        flashcards: List[Dict[str, Any]],
        add_hints: bool = False,
        add_mnemonics: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Enhance existing flashcards with additional features
        
        Args:
            flashcards: List of flashcards to enhance
            add_hints: Whether to add hints
            add_mnemonics: Whether to add memory aids
            
        Returns:
            Enhanced flashcards
        """
        # This could be implemented to add hints, mnemonics, or other enhancements
        # For MVP, we'll return as-is
        return flashcards
    
    def categorize_flashcards(
        self,
        flashcards: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group flashcards by topic/category
        
        Args:
            flashcards: List of flashcards
            
        Returns:
            Dictionary of flashcards grouped by topic
        """
        categorized = {}
        
        for card in flashcards:
            topic = card.get('topic', 'General')
            if topic not in categorized:
                categorized[topic] = []
            categorized[topic].append(card)
        
        return categorized