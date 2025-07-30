import os
import json
from typing import Optional
from fastapi import FastAPI, Request
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from google.genai import types
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all origins (for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Gemini API Key
API_KEY = "AIzaSyDojXCBfI9sW1nPQM5p6_m6aohf51ZJsNQ"

# --------------------------------------------
# Gemini Summary Logic
# --------------------------------------------
def summarize_transcript(transcript_text: str) -> dict:
    client = genai.Client(api_key=API_KEY)

    prompt = f"""
You are a helpful assistant.

Below is a transcript from a YouTube video. Generate a short JSON summary with the following format:
{{
  "topic_name": "name of the topic",
  "topic_summary": "brief explanation of the topic"
}}

Transcript:
\"\"\"{transcript_text}\"\"\"
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        ],
        config=types.GenerateContentConfig(temperature=0.5),
    )

    cleaned = response.text.strip()

    # Remove markdown fences ```json ... ```
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"raw_response": cleaned}


# --------------------------------------------
# Extract YouTube video ID
# --------------------------------------------
def extract_youtube_id(url: str) -> str:
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("/")[-1]
    else:
        raise ValueError("Invalid YouTube URL format")


# --------------------------------------------
# Fetch transcript and summarize
# --------------------------------------------
def fetch_and_summarize(video_id: str) -> dict:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-GB'])
        full_text = " ".join([entry["text"] for entry in transcript])
        return summarize_transcript(full_text)
    except Exception as e:
        return {"error": f"❌ Error fetching transcript: {e}"}


# --------------------------------------------
# POST endpoint to avoid 422 issues
# --------------------------------------------
@app.post("/summarize")
async def summarize_post(request: Request):
    try:
        body = await request.json()
        url = body.get("url")

        if not url:
            return {"error": "Missing 'url' field in JSON body."}

        video_id = extract_youtube_id(url)
        summary = fetch_and_summarize(video_id)
        return {"summary": summary}

    except Exception as e:
        return {"error": str(e)}


# --------------------------------------------
# Local Test (Optional)
# --------------------------------------------
if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=zkczDkbaE68"
    video_id = extract_youtube_id(test_url)
    print(fetch_and_summarize(video_id))
