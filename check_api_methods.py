"""
Check what methods are available in YouTubeTranscriptApi
"""

from youtube_transcript_api import YouTubeTranscriptApi
import inspect

print("Available methods in YouTubeTranscriptApi:")
print("=" * 50)

# Get all methods
for name in dir(YouTubeTranscriptApi):
    if not name.startswith('_'):
        attr = getattr(YouTubeTranscriptApi, name)
        if callable(attr):
            print(f"  - {name}")
            
print("\n" + "=" * 50)
print("Checking for specific methods:")
print("  - get_transcript:", hasattr(YouTubeTranscriptApi, 'get_transcript'))
print("  - list_transcripts:", hasattr(YouTubeTranscriptApi, 'list_transcripts'))
print("  - get_transcripts:", hasattr(YouTubeTranscriptApi, 'get_transcripts'))

# Test the correct way to get transcripts
print("\n" + "=" * 50)
print("Testing transcript extraction:")

video_id = "0fONene3OIA"

try:
    # Method 1: list_transcripts (this should work)
    print(f"\nMethod 1: Using list_transcripts('{video_id}')")
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    
    # Get the first available transcript
    for transcript in transcript_list:
        print(f"  Found: {transcript.language_code} (generated: {transcript.is_generated})")
        
        # Fetch the transcript
        data = transcript.fetch()
        print(f"  ✅ Success! Got {len(data)} segments")
        
        # Show how to use it
        output = ""
        for segment in data:
            output += segment['text'] + " "
        
        print(f"  Total text length: {len(output)} characters")
        print(f"  Preview: {output[:100]}...")
        break
        
except Exception as e:
    print(f"  ❌ Error: {e}")

# Try alternative import
print("\n" + "=" * 50)
print("Alternative import method:")

try:
    from youtube_transcript_api import YouTubeTranscriptApi as YT
    print("Methods available via YT alias:")
    for name in dir(YT):
        if not name.startswith('_') and callable(getattr(YT, name)):
            print(f"  - YT.{name}")
except Exception as e:
    print(f"Error with alternative import: {e}")