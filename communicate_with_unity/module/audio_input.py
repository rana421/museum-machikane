# API経由のwhisperのテスト
import os
import openai
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = '../.env'

load_dotenv(dotenv_path)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def recognize_audio(audio_file):
    with open(audio_file, "rb") as f:
        transcript = openai.Audio.transcribe("whisper-1", f, language="ja")
    return transcript["text"]
