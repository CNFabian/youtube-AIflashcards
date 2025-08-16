"""
Simple YouTube Video Summarizer Script
Following the approach from the video tutorial:
1. Use BeautifulSoup to get the title
2. Use youtube-transcript-api to get transcript
3. Use OpenAI to summarize and generate tags
"""

from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
import openai
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# URL - you can copy and paste any YouTube URL here
url = "https://www.youtube.com/watch?v=0fONene3OIA"

print(f"Processing: {url}\n")

# Get the page using requests (as shown in video)
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')

# Get the title of the page
title = soup.find('title').text.replace(' - YouTube', '')
print(f"Title: {title}")

# Extract video ID from URL (as shown in video)
video_id = None
if 'youtu.be' in url:
    # Short URL format
    video_id = url.split('/')[-1].split('?')[0]
elif 'youtube.com' in url and 'v=' in url:
    # Standard URL format
    video_id = url.split('v=')[1].split('&')[0]

print(f"Video ID: {video_id}")

# Get transcript using youtube-transcript-api (as shown in video)
try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    
    # Parse transcript (combine all text)
    output = ""
    for segment in transcript:
        output += segment['text'] + " "
    
    print(f"Transcript length: {len(output)} characters")
    print("Processing with ChatGPT...\n")
    
    # Get summary from ChatGPT (as shown in video)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a journalist."},
            {"role": "user", "content": f"Write a 100 word summary of this video: {output[:4000]}"}  # Limit to 4000 chars for token limit
        ],
        max_tokens=200,
        temperature=0.7
    )
    
    summary = response.choices[0].message.content
    print("SUMMARY:")
    print("-" * 50)
    print(summary)
    
    # Get tags from ChatGPT (as shown in video)
    tag_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a content tagger."},
            {"role": "user", "content": f"Output a list of tags for this blog post in a Python list such as ['item1', 'item2', 'item3']: {output[:4000]}"}
        ],
        max_tokens=100,
        temperature=0.5
    )
    
    tags = tag_response.choices[0].message.content
    print("\nTAGS:")
    print("-" * 50)
    print(tags)
    
    # Write to HTML file (as shown in video)
    with open('video_summary.html', 'w') as f:
        f.write(f"<html><head><title>{title}</title></head><body>")
        f.write(f"<h1>{title}</h1>")
        f.write(f"<p><strong>Video ID:</strong> {video_id}</p>")
        f.write(f"<h2>Summary</h2><p>{summary}</p>")
        f.write(f"<h2>Tags</h2><p>{tags}</p>")
        f.write(f"<h2>Full Transcript</h2>")
        
        # Split transcript by lines for better formatting
        for line in output.split('\n'):
            f.write(f"<p>{line}</p>")
        
        f.write("</body></html>")
    
    print("\n✅ HTML file created: video_summary.html")
    print("\nFULL TRANSCRIPT (first 500 chars):")
    print("-" * 50)
    print(output[:500] + "...")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure the video has captions enabled")
    print("2. Check your OpenAI API key in .env")
    print("3. Try a different video URL")