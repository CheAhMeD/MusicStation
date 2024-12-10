#!/usr/bin/env python3
import sys
from openai import OpenAI
import logging
import colorlog

# Logger (Color):
logging.setLoggerClass(colorlog.ColorLogger)
log = logging.getLogger("MusicStation")

open_ai_key = "YOUR_OPEANAI_API_KEY_GOES_HERE"
client = OpenAI(api_key=open_ai_key)

PROMPT = ["How may I assist you?",
    "How may I help?"]

BYES = ["Goodbye",
    "Bye"]

def downlaodSentences():
    '''
        donwloads all the sentences in PROMPT, BYES
        and others
    '''
    log.info("[SpeechDownloader] Downloading PROMPT sentences")
    for text in PROMPT:
        # get the audio file
        response = client.audio.speech.create(
            model="tts-1",
            voice="echo",
            input=text
        )
        response.stream_to_file(text +".mp3")

    log.info("[SpeechDownloader] Downloading byes sentences")
    for text in BYES:
        # get the audio file
        response = client.audio.speech.create(
            model="tts-1",
            voice="echo",
            input=text
        )
        response.stream_to_file(text +".mp3")
    
    log.info("[SpeechDownloader] Downloading the rest of sentences")
    response = client.audio.speech.create(
            model="tts-1",
            voice="echo",
            input='Smile!'
        )
    response.stream_to_file("Smile!.mp3")

    response = client.audio.speech.create(
            model="tts-1",
            voice="echo",
            input='Starting timer!'
        )
    response.stream_to_file("Starting timer!.mp3")

    response = client.audio.speech.create(
            model="tts-1",
            voice="echo",
            input='Stopping timer!'
        )
    response.stream_to_file("Stopping timer!.mp3")

    

if __name__ == "__main__":
    # download sentences
    try:
        downlaodSentences()
    except Exception as e_:
        log.error("[SpeechDownloader] Exception: " + str(e_))
    finally:
        sys.exit()
