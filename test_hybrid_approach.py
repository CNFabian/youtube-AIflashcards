"""
Test script to demonstrate the hybrid approach:
- BeautifulSoup for metadata
- youtube-transcript-api for transcript
- Fallback to BeautifulSoup scraping if needed
"""

from services.transcript import TranscriptService
import json

def test_video(url):
    """Test transcript extraction for a video"""
    print("=" * 60)
    print(f"Testing URL: {url}")
    print("=" * 60)
    
    # Initialize the service
    service = TranscriptService()
    
    try:
        # Step 1: Get metadata with BeautifulSoup
        print("\n📝 Step 1: Extracting metadata with BeautifulSoup...")
        metadata = service.get_video_metadata(url)
        print(f"✅ Title: {metadata.get('video_title', 'Unknown')}")
        print(f"✅ Video ID: {metadata.get('video_id', 'Unknown')}")
        if metadata.get('channel_name'):
            print(f"✅ Channel: {metadata.get('channel_name')}")
        
        # Step 2: Get full transcript data
        print("\n📜 Step 2: Extracting transcript...")
        result = service.get_transcript(url)
        
        print(f"✅ Transcript extracted successfully!")
        print(f"   - Language: {result['language']}")
        print(f"   - Auto-generated: {result['is_generated']}")
        print(f"   - Word count: {result['word_count']}")
        print(f"   - Duration: {result['duration']:.2f} seconds")
        print(f"   - Segments: {len(result['segments'])}")
        
        # Show first 3 segments as sample
        print("\n📖 Sample transcript segments:")
        for i, segment in enumerate(result['segments'][:3], 1):
            print(f"\n   Segment {i}:")
            print(f"   Time: {segment['start']:.2f}s")
            print(f"   Text: {segment['text'][:100]}...")
        
        # Show first 500 characters of full text
        print("\n📄 Full transcript preview:")
        print("-" * 40)
        print(result['full_text'][:500] + "...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Test multiple videos with the hybrid approach"""
    
    test_urls = [
        # The video from your original test
        "https://www.youtube.com/watch?v=0fONene3OIA",
        
        # Known good videos
        "https://www.youtube.com/watch?v=rfscVS0vtbw",  # Python tutorial
        "https://youtu.be/8jLOx1hD3_o",  # Short URL format
        
        # Test a potentially problematic video
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll (music video)
    ]
    
    print("🚀 Testing Hybrid Transcript Extraction Approach")
    print("=" * 60)
    print("This script demonstrates:")
    print("1. BeautifulSoup for getting video title and metadata")
    print("2. youtube-transcript-api for getting transcripts")
    print("3. BeautifulSoup fallback for difficult cases")
    print("=" * 60)
    
    success_count = 0
    
    for url in test_urls:
        if test_video(url):
            success_count += 1
        
        print("\n" + "=" * 60)
        input("Press Enter to test next video (or Ctrl+C to quit)...")
    
    print(f"\n✅ Successfully extracted {success_count}/{len(test_urls)} transcripts")
    
    # Test the simple extraction method
    print("\n" + "=" * 60)
    print("Testing direct API method (as shown in video):")
    print("=" * 60)
    
    from youtube_transcript_api import YouTubeTranscriptApi
    import requests
    from bs4 import BeautifulSoup
    
    url = "https://www.youtube.com/watch?v=0fONene3OIA"
    
    # Get title with BeautifulSoup
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    title = soup.find('title').text.replace(' - YouTube', '')
    print(f"Title: {title}")
    
    # Extract video ID
    video_id = url.split('v=')[1].split('&')[0] if 'v=' in url else url.split('/')[-1]
    print(f"Video ID: {video_id}")
    
    # Get transcript
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        print(f"✅ Got {len(transcript)} segments")
        
        # Combine text
        output = " ".join([seg['text'] for seg in transcript])
        print(f"Total length: {len(output)} characters")
        print(f"Preview: {output[:200]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()