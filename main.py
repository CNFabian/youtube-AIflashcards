"""
YouTube Video to Flashcards - Final Working Version
Handles all language code variations properly
"""

from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
import openai
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats"""
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    elif 'youtube.com' in url and 'v=' in url:
        return url.split('v=')[1].split('&')[0]
    return None

def get_video_metadata(url):
    """Get video title and metadata using BeautifulSoup"""
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        title = soup.title.text.replace(' - YouTube', '')
        return title
    except:
        return "Unknown Title"

def get_transcript(video_id):
    """Get transcript using the correct API method"""
    ytt_api = YouTubeTranscriptApi()
    
    # Try Method 1: Use list() to see what's available
    try:
        transcript_list = ytt_api.list(video_id)
        
        # Print available transcripts for debugging
        print("📋 Available transcripts:")
        for t in transcript_list:
            print(f"   - {t.language} ({t.language_code}) - Generated: {t.is_generated}")
        
        # Try to get English transcript (any variant)
        english_codes = ['en', 'en-US', 'en-GB', 'en-AU', 'en-CA', 'en-IN']
        
        for code in english_codes:
            try:
                transcript = transcript_list.find_transcript([code])
                fetched = transcript.fetch()
                print(f"✅ Using transcript: {fetched.language} ({fetched.language_code})")
                return fetched.to_raw_data(), fetched.language_code
            except:
                continue
        
        # If no English found, get the first available
        for transcript in transcript_list:
            try:
                fetched = transcript.fetch()
                print(f"✅ Using transcript: {fetched.language} ({fetched.language_code})")
                return fetched.to_raw_data(), fetched.language_code
            except:
                continue
                
    except Exception as e:
        print(f"❌ Error listing transcripts: {e}")
    
    # Try Method 2: Direct fetch
    try:
        fetched = ytt_api.fetch(video_id)
        return fetched.to_raw_data(), fetched.language_code
    except:
        pass
    
    return None, None

def generate_flashcards(transcript_text, num_cards=10):
    """Generate flashcards using OpenAI"""
    if not openai.api_key or openai.api_key == "your_openai_api_key_here":
        print("⚠️ OpenAI API key not configured")
        return None
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai.api_key)
        
        prompt = f"""Create {num_cards} educational flashcards from this transcript.
        
        Return as JSON array with this format:
        [
            {{
                "question": "Clear, specific question",
                "answer": "Concise, accurate answer",
                "difficulty": "easy|medium|hard"
            }}
        ]
        
        Transcript: {transcript_text[:3000]}"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an educational content creator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # Parse JSON response
        content = response.choices[0].message.content
        # Extract JSON if wrapped in code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        flashcards = json.loads(content)
        return flashcards
        
    except Exception as e:
        print(f"Error generating flashcards: {e}")
        return None

def main():
    """Main function"""
    print("🎓 YouTube to Flashcards Generator")
    print("=" * 50)
    
    # Get URL from user
    url = input("Enter YouTube URL: ").strip()
    if not url:
        url = "https://www.youtube.com/watch?v=0fONene3OIA"
    
    print(f"\n🎥 Processing: {url}\n")
    
    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        print("❌ Invalid YouTube URL")
        return
    
    print(f"🆔 Video ID: {video_id}")
    
    # Get video title
    title = get_video_metadata(url)
    print(f"📌 Title: {title}\n")
    
    # Get transcript
    print("📝 Extracting transcript...")
    transcript_data, language = get_transcript(video_id)
    
    if not transcript_data:
        print("❌ Could not extract transcript")
        return
    
    # Combine transcript text
    full_text = " ".join([segment['text'] for segment in transcript_data])
    
    print(f"✅ Transcript extracted!")
    print(f"   - Language: {language}")
    print(f"   - Length: {len(full_text)} characters")
    print(f"   - Words: {len(full_text.split())}")
    
    # Show preview
    print(f"\n📖 Preview: {full_text[:200]}...")
    
    # Generate flashcards
    num_cards = input("\n💡 How many flashcards to generate? (default: 10): ").strip()
    num_cards = int(num_cards) if num_cards.isdigit() else 10
    
    print(f"\n🤖 Generating {num_cards} flashcards...")
    flashcards = generate_flashcards(full_text, num_cards)
    
    if flashcards:
        print(f"\n✨ Generated {len(flashcards)} flashcards!\n")
        
        # Display flashcards
        for i, card in enumerate(flashcards, 1):
            print(f"📚 Flashcard #{i}")
            print(f"   Difficulty: {card.get('difficulty', 'medium')}")
            print(f"   Q: {card['question']}")
            print(f"   A: {card['answer']}")
            print()
        
        # Save to file
        output_file = f"flashcards_{video_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'video_url': url,
                'video_title': title,
                'video_id': video_id,
                'language': language,
                'flashcards': flashcards,
                'transcript_preview': full_text[:500]
            }, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved to: {output_file}")
    
    # Save HTML version
    with open(f"summary_{video_id}.html", 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #ff0000; padding-bottom: 10px; }}
        .metadata {{ background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .flashcard {{ background: #fff; border: 2px solid #e0e0e0; border-radius: 8px; 
                     padding: 20px; margin: 15px 0; transition: all 0.3s; }}
        .flashcard:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.15); transform: translateY(-2px); }}
        .question {{ font-weight: bold; color: #2c3e50; font-size: 18px; margin-bottom: 10px; }}
        .answer {{ color: #34495e; line-height: 1.6; }}
        .difficulty {{ display: inline-block; padding: 4px 12px; border-radius: 20px; 
                      font-size: 12px; font-weight: bold; text-transform: uppercase; }}
        .easy {{ background: #d4edda; color: #155724; }}
        .medium {{ background: #fff3cd; color: #856404; }}
        .hard {{ background: #f8d7da; color: #721c24; }}
        .transcript {{ background: #f8f9fa; padding: 20px; border-left: 4px solid #007bff; 
                      margin-top: 30px; max-height: 400px; overflow-y: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 {title}</h1>
        <div class="metadata">
            <p><strong>🔗 Video:</strong> <a href="{url}" target="_blank">{url}</a></p>
            <p><strong>🆔 ID:</strong> {video_id}</p>
            <p><strong>🌐 Language:</strong> {language}</p>
            <p><strong>📝 Words:</strong> {len(full_text.split())}</p>
        </div>
        
        <h2>📚 Flashcards</h2>""")
        
        if flashcards:
            for i, card in enumerate(flashcards, 1):
                difficulty = card.get('difficulty', 'medium')
                f.write(f"""
        <div class="flashcard">
            <span class="difficulty {difficulty}">{difficulty}</span>
            <div class="question">❓ Question {i}: {card['question']}</div>
            <div class="answer">✅ Answer: {card['answer']}</div>
        </div>""")
        
        f.write(f"""
        <h2>📜 Transcript Preview</h2>
        <div class="transcript">
            <p>{full_text[:1000]}...</p>
        </div>
    </div>
</body>
</html>""")
    
    print(f"🌐 HTML saved to: summary_{video_id}.html")
    print("\n✨ Done! Open the HTML file in your browser for a nice view.")

if __name__ == "__main__":
    main()