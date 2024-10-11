from youtube_transcript_api import YouTubeTranscriptApi

video_id = 'dQw4w9WgXcQ'  # Example video ID

try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = ' '.join([item['text'] for item in transcript])
    print(transcript_text)
except Exception as e:
    print(f"Error: {e}")
