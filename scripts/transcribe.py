#!/usr/bin/env python3
"""
Voice message transcription via Groq Whisper API.
Usage: python3 transcribe.py <audio_file_path>
"""

import sys
import os

def transcribe(audio_path: str) -> str:
    api_key_file = os.path.expanduser("~/.openclaw-neuro/.groq_key")
    with open(api_key_file) as f:
        api_key = f.read().strip()

    from groq import Groq
    client = Groq(api_key=api_key)

    with open(audio_path, "rb") as audio_file:
        result = client.audio.transcriptions.create(
            file=(os.path.basename(audio_path), audio_file),
            model="whisper-large-v3-turbo",
            language="ru",
            response_format="text"
        )
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: transcribe.py <audio_file>")
        sys.exit(1)
    text = transcribe(sys.argv[1])
    print(text)
