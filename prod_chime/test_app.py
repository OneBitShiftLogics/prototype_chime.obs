from flask import Flask, request, render_template, jsonify
import requests
import openai
import os
from gtts import gTTS
import speech_recognition as sr

app = Flask(__name__)

# Set API keys (replace with actual keys)
LLAMA_API_KEY = "your_llama_api_key"
OPENAI_WHISPER_KEY = "your_openai_whisper_key"
TTS_API_KEY = "your_tts_api_key"

# Initialize speech recognizer
recognizer = sr.Recognizer()

def speech_to_text(audio_file):
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Error: Could not understand audio"
    except sr.RequestError:
        return "Error: Could not request results"

def llama_process(text):
    headers = {"Authorization": f"Bearer {LLAMA_API_KEY}"}
    data = {"input": text}
    response = requests.post("https://api.llama.com/process", json=data, headers=headers)
    return response.json().get("output", "Error processing response")

def text_to_speech(response_text):
    tts = gTTS(text=response_text, lang='en')
    audio_path = "static/response.mp3"
    tts.save(audio_path)
    return audio_path







import requests
import json

url = "https://api.murf.ai/v1/speech/generate"

payload = json.dumps({
  "voiceId": "en-IN-aarav",
  "style": "Conversational",
  "text": "Welcome to the Mental Health Podcast! Join us as we explore ways to improve your mental well-being, share expert advice, and offer tips for managing stress and anxiety. Let’s talk, listen, and grow together.",
  "rate": 0,
  "pitch": -8,
  "sampleRate": 48000,
  "format": "MP3",
  "channelType": "MONO",
  "pronunciationDictionary": {},
  "encodeAsBase64": False,
  "variation": 1,
  "audioDuration": 0,
  "modelVersion": "GEN2",
  "multiNativeLocale": "en-IN"
})
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'api-key': 'YOUR_API_KEY'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
    















@app.route('/', methods=['GET', 'POST'])
def index():
    response_text = ""
    audio_path = ""
    if request.method == 'POST':
        if 'text' in request.form:
            user_input = request.form['text']
        elif 'audio' in request.files:
            audio_file = request.files['audio']
            user_input = speech_to_text(audio_file)
        else:
            user_input = ""
        
        if user_input:
            response_text = llama_process(user_input)
            audio_path = text_to_speech(response_text)
    
    return render_template('index.html', response_text=response_text, audio_path=audio_path)

if __name__ == '__main__':
    app.run(debug=True)
