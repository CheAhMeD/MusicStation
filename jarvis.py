#!/usr/bin/env python3

import re
import pvporcupine
import pyaudio
import random
import struct
import sys
import time
import speech_recognition as sr
# the following import supresses the error logs of speech_recognition!!!
import sounddevice 
import pygame as pg
from openai import OpenAI
import logging
import colorlog
import aht20
import requests
import json
import pycountry

from smbus2 import SMBus
from bmp280 import BMP280
from peripherals import Leds
from settings import *
from gui import *

# Tube leds thread:
ledsAnimationThread = Leds(NUM_TUBE_LEDS)
# Logger (Color):
logging.setLoggerClass(colorlog.ColorLogger)
log = logging.getLogger(APP_NAME)
# Temperature and humidity sensors:
bus = SMBus(I2C_BUS)
bmp280 = BMP280(i2c_addr=BMP280_I2C_ADDR, i2c_dev=bus)
aht20 = aht20.AHT20(BusNum = I2C_BUS)
# get the path 
py_path = os.path.dirname(os.path.abspath(__file__))
# set current directory
os.chdir(py_path)

gui = MusicStationGUI()

audio_stream = None
porcupine = None

jarvis = OpenAI(api_key=JARVIS_OPENAI_API_KEY)

def ask_jarvis(query):
    user_query = [
        {"role": "user", "content": query},
        ]         
    send_query = (JARVIS_LOG + user_query)
    response = jarvis.chat.completions.create(
        model=JARVIS_GPT_MODEL,
        messages=send_query
    )
    answer = response.choices[0].message.content
    return answer

def get_jarvis_mood():
    query = "From the following list "+ str(JARVIS_MOOD) +". Choose a single word. Respond only with the chosen word." 
    choice = ask_jarvis(query)
    log.info(JARVIS_NAME + " Jarvis mood: " + str(choice))
    # remove the '' from the choice
    return ''.join(char for char in choice if char.isalpha())

def listen_and_recognize():
    """Listen to the user's voice and recognize text."""
    # set led animation
    ledsAnimationThread.setActiveAnimation('listening')
    log.info(JARVIS_NAME + " Listening...")
    gui.talkingScreen.setLoopMood(True)
    gui.talkingScreen.setMood("listening")
    recognizer = sr.Recognizer()
    microphone = sr.Microphone(JARVIS_MIC_INDEX)
    with microphone as src:
        recognizer.adjust_for_ambient_noise(src)
        audio_data = recognizer.listen(src, phrase_time_limit=4)
    try:
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        log.info(JARVIS_NAME + " Sorry, I didn't catch that.")
        return None
    except sr.RequestError:
        log.error(JARVIS_NAME + " Sorry, there was an error with the recognition service.")
        return None

def speak(text):
    '''
        Speak a phrase streamed as a response to a text
        @param text: string to be synthesized using OpenAi tts-1 
                     and displayed on the screen 
    '''
    # set led animation
    ledsAnimationThread.setActiveAnimation('talking')
    # update the mood
    gui.talkingScreen.setMood("loading")
    # get the audio file
    response = jarvis.audio.speech.create(
        model=JARVIS_TTS_MODEL,
        voice="echo",
        input=text
    )
    response.stream_to_file("speech.mp3")

    # set Jarvis "random" mood
    mood = get_jarvis_mood().lower()
    gui.talkingScreen.setMood(mood)
    gui.talkingScreen.setMessageText(text)
    
    # play the response
    pg.mixer.init()
    pg.mixer.music.load("speech.mp3")
    pg.mixer.music.play()

    while pg.mixer.music.get_busy():
        pass

def speak_from_file(text):
    '''
        Speak a phrase stored locally
        @param text: file name and string to be displayed on the screen

    '''
    # set led animation
    ledsAnimationThread.setActiveAnimation('talking')
    # set Jarvis "random" mood
    mood = get_jarvis_mood().lower()
    gui.talkingScreen.setMood(mood)
    gui.talkingScreen.setMessageText(text)
    
    # play the response
    pg.mixer.init()
    pg.mixer.music.load("./speech/" + text + ".mp3")
    pg.mixer.music.play()

    while pg.mixer.music.get_busy():
        pass

# wake word detection (blocking)
def detect_wake_word():
    log.info(JARVIS_NAME + " Waiting for wake word!!")
    porcupine = pvporcupine.create(keywords=["jarvis"],
                            access_key=JARVIS_PICOVOICE_KEY,
                            sensitivities=[0.1], #from 0 to 1.0 - a higher number reduces the miss rate at the cost of increased false alarms
                                   )
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    
    wake_pa = pyaudio.PyAudio()

    porcupine_audio_stream = wake_pa.open(
                    rate=porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=porcupine.frame_length)
    
    isDetecting = True

    while isDetecting:
        porcupine_pcm = porcupine_audio_stream.read(porcupine.frame_length)
        porcupine_pcm = struct.unpack_from("h" * porcupine.frame_length, porcupine_pcm)

        porcupine_keyword_index = porcupine.process(porcupine_pcm)

        if porcupine_keyword_index >= 0:

            log.info(JARVIS_NAME + " Wake word detected!!")
            porcupine_audio_stream.stop_stream
            porcupine_audio_stream.close()
            porcupine.delete()         
            os.dup2(old_stderr, 2)
            os.close(old_stderr)
            isDetecting = False

# Threads:
def runJarvis():
    log.debug("Starting J.A.R.V.I.S")
    while True:
        detect_wake_word() # blocking loop until wake word detected
        gui.talkingScreen.setMood("wakeup")
        pg.event.post(pg.event.Event(startTalkingEvent))
        speak_from_file(random.choice(JARVIS_PROMPT))
        start_time = time.time()
        while True:
            # stop listening after JARVIS_LISTENING_TIMEOUT
            if ((time.time() - start_time) > JARVIS_LISTENING_TIMEOUT) and (gui.gsm.getActiveScreen() == 'talking'):
                log.info(JARVIS_NAME + " ListeningTimeout")
                pg.event.post(pg.event.Event(startMainScreenEvent))
                ledsAnimationThread.setActiveAnimation('solid')
                break
            text = listen_and_recognize() # non blocking & returns text if spoken to otherwise returns error string
            if text:
                # reset the listening timeout
                start_time = time.time()
                log.info(">>> " + text)
                if "stop listening" in text:
                    speak_from_file(random.choice(JARVIS_BYES))
                    pg.mixer.quit()
                    pg.event.post(pg.event.Event(startMainScreenEvent))
                    ledsAnimationThread.setActiveAnimation('solid')
                    break
                elif "timer" in text:
                    if "stop" in text:
                        #return to main screen
                        speak_from_file("Stopping timer!")
                        t_ = 0
                        e_ = startTalkingEvent
                        pg.mixer.quit()
                    elif "set" in text or "start" in text:
                        # this returns a list of numbers in the string
                        # for example set|start a timer for:
                        # 5 minutes and 30 seconds returns ['5', '30']
                        # 3 minutes returns ['3']
                        # 30 seconds returns ['30']
                        lt_ = re.findall(r'\d+', text)
                        #timer_str = str(lt_[0]) + ' minutes.' if len(lt_) < 2 else str(lt_[0]) + ' minutes ' + str(lt_[1]) + ' seconds.'
                        t_ = 0
                        if len(lt_) > 0:
                            # Start a timer for calculated time
                            print(lt_)
                            if "seconds" in text or "second" in text:
                                t_ += int(lt_[-1])
                            if "minutes" in text or "minute" in text:
                                t_ += (int(lt_[1]) * 60) if len(lt_) > 2 else (int(lt_[0]) * 60)
                            if "hours" in text or "hour" in text:
                                t_ += (int(lt_[1]) * 3600) if len(lt_) > 2 else (int(lt_[0]) * 3600)
                        else:
                            # Start a timer for default time
                            t_ = DEFAULT_TIMER_VALUE
                        e_ = startTimerEvent
                        speak_from_file("Starting timer!")

                    gui.setTimerValue(t_)
                    pg.event.post(pg.event.Event(e_))
                
                elif "take" in text and "photo" in text:
                    speak_from_file("Smile!")  
                    pg.event.post(pg.event.Event(startCameraEvent))    
                else:
                    # Get an answer from OpenAI
                    jarvis_response = ask_jarvis(text)
                    log.info("<<< " + str(jarvis_response))
                    speak(jarvis_response)

def sensorsReadings():
    global roomTemperature
    global ahtTemperature
    global roomHumidity
    while True:
        log.info("[THREAD] Readings Sensors")
        roomTemperature = round(bmp280.get_temperature(),1)
        ahtTemperature  = round(aht20.get_temperature(),1)
        roomHumidity    = round(aht20.get_humidity(),1)
        gui.setSenosorsReadings([roomTemperature,roomHumidity])
        time.sleep(SENSORS_READINGS_RATE) # read sensor only every few seconds 

def weatherReadings():
    ''' Connects to openweathermar.org and collects the weather conditions
        of a given city (global var WEATHER_CITY).
        The conditions are then formatted and listed in a global variable
        weatherConditions.
    '''
    global weatherConditions
    while True:
        log.info("[THREAD] Fetching Weather Conditions")
        w_req = requests.get("https://api.openweathermap.org/data/2.5/weather?q="
                               + WEATHER_CITY + "&units=metric&appid="+WEATHER_API_KEY)
        w_api = json.loads(w_req.content)
        w_icon = w_api['weather'][0]['icon'] + '.png'
        w_status = w_api['weather'][0]['main']
        w_desc = w_api['weather'][0]['description']
        w_temp = str(round(w_api['main']['temp'])) + "°C"
        w_hum = str(w_api['main']['humidity']) + "%"
        w_wind = str(w_api['wind']['speed']) + 'mps'
        w_loc = str(w_api['name']) + ", " + pycountry.countries.get(alpha_2=w_api['sys']['country']).name.upper()
        if 'rain' in w_api:
            w_prec = 'R: ' + str( w_api['rain'])
        elif 'snow' in w_api:
            w_prec = 'S: ' + str(w_api['snow'])
        else:
            w_prec = '0mm/h'

        weatherConditions = [w_icon, w_status, w_desc, w_temp, w_hum, w_prec, w_wind, w_loc]
        gui.setConditions(weatherConditions)
        time.sleep(WEATHER_FETCHING_RATE)

