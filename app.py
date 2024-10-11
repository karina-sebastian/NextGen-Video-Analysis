from flask import Flask, render_template, request
import cv2
import numpy as np
from deepface import DeepFace
import yt_dlp
import matplotlib.pyplot as plt
import os
from io import BytesIO
import base64
import threading

app = Flask(__name__)

# Global variables to store emotions
emotions = []
video_processing = False

def process_video(stream_url):
    global emotions, video_processing
    video_processing = True
    cap = cv2.VideoCapture(stream_url)

    while video_processing:
        success, frame = cap.read()
        if success:
            try:
                # Analyze the face in the frame for emotion
                analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                dominant_emotion = analysis[0]["dominant_emotion"]
                emotions.append(dominant_emotion)
            except Exception as e:
                continue
        else:
            break

    cap.release()

@app.route("/", methods=["GET", "POST"])
def index():
    embed_url = ""
    emotion_result = ""
    chart_url = ""

    if request.method == "POST":
        youtube_url = request.form["youtube_link"]

        # Extract video ID for embedding
        try:
            if "youtube.com" in youtube_url or "youtu.be" in youtube_url:
                video_id = youtube_url.split("v=")[-1].split("&")[0] if "v=" in youtube_url else youtube_url.split("/")[-1]
                embed_url = f"https://www.youtube.com/embed/{video_id}"

                # Use yt-dlp to extract direct video stream URL
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',  # Choose the best available format
                    'quiet': True
                }

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(youtube_url, download=False)
                        stream_url = info_dict['url']  # Get the direct stream URL

                    # Start video processing in a separate thread
                    threading.Thread(target=process_video, args=(stream_url,)).start()

                    # Wait for a while to process emotions
                    if emotions:
                        emotion_counts = {emotion: emotions.count(emotion) for emotion in set(emotions)}
                        emotion_labels = list(emotion_counts.keys())
                        emotion_values = list(emotion_counts.values())

                        # Create a sentiment analysis chart
                        plt.figure(figsize=(10, 5))
                        plt.bar(emotion_labels, emotion_values, color='blue')
                        plt.title('Emotion Analysis')
                        plt.xlabel('Emotions')
                        plt.ylabel('Counts')

                        # Save the chart to a BytesIO object
                        img = BytesIO()
                        plt.savefig(img, format='png')
                        img.seek(0)
                        chart_url = base64.b64encode(img.getvalue()).decode('utf8')
                        plt.close()
                    else:
                        emotion_result = "Could not detect any emotions."
                except Exception as e:
                    emotion_result = f"Error extracting video stream: {str(e)}"
            else:
                raise ValueError("Invalid YouTube URL")
        except Exception as e:
            emotion_result = f"Error: {str(e)}"

    return render_template("index.html", embed_url=embed_url, emotion_result=emotion_result, chart_url=chart_url)

@app.route("/stop", methods=["POST"])
def stop_processing():
    global video_processing
    video_processing = False
    return "Video processing stopped."

if __name__ == "__main__":
    app.run(debug=True)
