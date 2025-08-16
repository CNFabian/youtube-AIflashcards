# YouTube Flashcards AI 🎓

Transform YouTube educational videos into interactive flashcards using AI! This application extracts transcripts from YouTube videos and uses OpenAI's GPT models to generate high-quality educational flashcards.

## Features ✨

- 🎥 **YouTube Transcript Extraction**: Automatically extract transcripts from any YouTube video
- 🤖 **AI-Powered Generation**: Uses OpenAI GPT-4 to create intelligent, contextual flashcards
- 🎯 **Customizable Difficulty**: Generate easy, medium, hard, or mixed difficulty flashcards
- 📚 **Topic Focus**: Optionally focus on specific subjects within the video
- 🌐 **Multi-language Support**: Extract transcripts in different languages
- ⚡ **Fast API**: RESTful API built with FastAPI for high performance
- 📖 **Interactive Documentation**: Auto-generated API docs with Swagger UI

## Quick Start 🚀

### Prerequisites

- Python 3.8+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd youtube-flashcards
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. **Run the application**
```bash
python main.py
# Or use the quick start script
chmod +x run.sh
./run.sh
```

The API will be available at `http://localhost:8000`

## API Usage 📡

### Generate Flashcards

**Endpoint:** `POST /api/v1/flashcards/generate`

**Request Body:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "num_cards": 10,
  "difficulty_level": "mixed",
  "subject_focus": "machine learning",
  "language": "en"
}
```

**Response:**
```json
{
  "id": "uuid",
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "video_title": "Introduction to Machine Learning",
  "video_id": "VIDEO_ID",
  "flashcards": [
    {
      "id": "uuid",
      "question": "What is supervised learning?",
      "answer": "A type of machine learning where the model is trained on labeled data",
      "difficulty": "easy",
      "topic": "Machine Learning Basics",
      "explanation": "The model learns from examples with known outputs"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "transcript_length": 5000,
  "language": "en"
}
```

### API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger documentation.

## Project Structure 📁

```
youtube-flashcards/
├── main.py                 # FastAPI application entry point
├── models.py              # Pydantic data models
├── config.py              # Application configuration
├── services/
│   ├── transcript.py      # YouTube transcript extraction
│   └── ai_processor.py    # AI flashcard generation
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Configuration ⚙️

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | GPT model to use | `gpt-4o-mini` |
| `PORT` | Server port | `8000` |
| `HOST` | Server host | `0.0.0.0` |
| `ENVIRONMENT` | Environment mode | `development` |
| `DEFAULT_NUM_FLASHCARDS` | Default number of flashcards | `10` |
| `MAX_FLASHCARDS_PER_REQUEST` | Maximum flashcards per request | `50` |

## API Endpoints 🔌

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint - API info |
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/flashcards/generate` | Generate flashcards from YouTube video |
| `GET` | `/api/v1/flashcards/sample` | Get sample flashcards for testing |
| `GET` | `/docs` | Swagger UI documentation |
| `GET` | `/redoc` | ReDoc documentation |

## Error Handling 🚨

The API returns structured error responses:

```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

Common error codes:
- `400`: Invalid request (bad YouTube URL, invalid parameters)
- `404`: Transcript not available
- `500`: Server error (AI processing failed)

## Development 🛠️

### Running in Development Mode

```bash
# Install development dependencies
pip install pytest pytest-asyncio black isort

# Format code
black .
isort .

# Run tests
pytest

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing the API

1. **Using curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/flashcards/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "num_cards": 5
  }'
```

2. **Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/flashcards/generate",
    json={
        "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
        "num_cards": 10,
        "difficulty_level": "medium"
    }
)
print(response.json())
```

## Roadmap 🗺️

### Phase 1: Core MVP ✅
- [x] FastAPI application structure
- [x] YouTube transcript extraction
- [x] AI flashcard generation
- [x] REST API endpoints
- [x] Error handling

### Phase 2: Enhancements (Coming Soon)
- [ ] Database integration (PostgreSQL/SQLite)
- [ ] User authentication (JWT)
- [ ] Export formats (Anki, CSV, PDF)
- [ ] Web frontend (React/Vue)
- [ ] Caching layer (Redis)

### Phase 3: Advanced Features
- [ ] Batch processing for playlists
- [ ] Spaced repetition algorithms
- [ ] Custom AI prompts
- [ ] Multi-model support (Claude, Gemini)
- [ ] Real-time progress updates (WebSockets)

## Troubleshooting 🔧

### Common Issues

1. **"OPENAI_API_KEY not found"**
   - Make sure you've created a `.env` file from `.env.example`
   - Add your OpenAI API key to the `.env` file

2. **"No transcript available"**
   - Some videos don't have transcripts enabled
   - Try a different video or check if captions are available

3. **"Rate limit exceeded"**
   - You've hit OpenAI's rate limits
   - Wait a moment and try again, or upgrade your OpenAI plan

4. **"Invalid YouTube URL"**
   - Make sure the URL is a valid YouTube video link
   - Supported formats: youtube.com/watch?v=ID, youtu.be/ID

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

MIT License - feel free to use this project for your own purposes.

## Support 💬

For issues, questions, or suggestions, please open an issue on GitHub.

---

Built with ❤️ using FastAPI and OpenAI