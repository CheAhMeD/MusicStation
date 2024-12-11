#!/usr/bin/env python3
from api_keys import *

# Do not change unless you know what you are doing...
# Colorful-X7
EQUILIZER_DEVICE_ID  = colorful_id
EQUILIZER_DEVICE_IP  = colorful_ip
EQUILIZER_DEVICE_KEY = colorful_key

# Weather API
WEATHER_API_KEY = weather_key
WEATHER_CITY    = weather_city
WEATHER_FETCHING_RATE = 1800 # Fetch the weather every 1/2 hour

# Jarvis
APP_NAME                 = "[Music Station]"
APP_VERSION              = "V1.0_Beta"
JARVIS_NAME              = "[Jarvis]"
JARVIS_OPENAI_API_KEY    = open_ai_key
JARVIS_PICOVOICE_KEY     = picovice_key
JARVIS_GPT_MODEL         = "gpt-4"
JARVIS_TTS_MODEL         = "tts-1"
JARVIS_MIC_INDEX         = 2 # should be 1 (USB audio device)
JARVIS_SPEAKER_RATE      = 175
JARVIS_LISTENING_TIMEOUT = 20 # in seconds

JARVIS_PROMPT = ["How may I assist you?",
    "How may I help?",
    "What can I do for you?",
    "Ask me anything.",
    "Yes?",
    "I'm here.",
    "I'm listening.",
    "Ahah?",
    "Yes Tchi?",
    "What would you like me to do?"]

JARVIS_BYES = ["Roger that!",
    "Sir yes sir!",
    "Glad to be of service",
    "Okey!",
    "Will do!"]

JARVIS_LOG = [
    {"role": "system", 
     "content": "Your name is Jarvis. You do not have a namesake. You are a helpful AI-based assistant. Reply always with a short sentence."},
    ]

JARVIS_MOOD = [
    "Speaking",
    "Confusing",
    "Happy",
    "Sad",
    "Boring",
    "Angry",
    "Rage",
    "Curious",
    "Wating"]

JARVIS_MOOD_GIFS = [
    "listening",
    "loading",
    "speaking",
    "wakeup",
    "confusing",
    "happy",
    "sad",
    "boring",
    "angry",
    "rage",
    "curious",
    "wating"]

# Misc
NUM_TUBE_LEDS = 3
I2C_BUS = 1
BMP280_I2C_ADDR = 0x77
SENSORS_READINGS_RATE = 30   # Read the sensors every 30 sec
PIR_PIN = 5
DEFAULT_TIMER_VALUE = 30 # Default timer value in seconds

# GUI Generic
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 480
SCREEN_FPS    = 60

# GUI Colors
GUI_BLACK   = (0,0,0)
GUI_WHITE   = (255,255,255)
GUI_ORANGE  = (255,179,0)
GUI_BLUE    = (48,105,162)

# Splash Screen
SPLASH_LOGO_POS   = (160,75)
SPLASH_TEXT_SIZE  = 22
SPLASH_TEXT_POS   = (50,430)
SPLASH_TEXT_COLOR = (255,255,255)
SPLASH_TEXT_RECT  = 50,430,700,50

# GUI Fonts
MAIN_FONT       = "SF Port McKenzie"
JARVIS_FONT_1   = "Lucida Console"
JARVIS_FONT_2   = "LUNARLIGHT Trial"
# GUI Labels: 
##Time
TIME_TEXT_SIZE  = 250
TIME_TEXT_COLOR = (145, 234, 252)
TIME_TEXT_POS   = (140,90)
##Date 
DATE_TEXT_SIZE  = 50
DATE_TEXT_COLOR = (145, 234, 252)
DATE_TEXT_POS   = (10,430)
##Conditions
COND_ICON_POS   = (525,110)
COND_TEXT_SIZE  = 30
COND_TEXT_yPOS  = 260 #Xpos is dynamically calculated
##Temperature
TEMP_TEXT_SIZE  = 60
TEMP_TEXT_yPOS  = 323
##Location
LOC_ICON_POS    = (140,345)
LOC_TEXT_SIZE   = 32
LOC_TEXT_POS    = (190,345)
##Precipitation & Humidity & Wind & SENSORS
INFO_TEXT_SIZE   = 30
PREC_ICON_POS   = (10,10)
PREC_TEXT_POS   = (60,10)
HUM_ICON_POS    = (135,10)
HUM_TEXT_POS    = (185,10)
WIND_ICON_POS   = (235,10)
WIND_TEXT_POS   = (285,10)
S_TEMP_ICON_POS = (610,10)
S_TEMP_TEXT_POS = (650,10)
S_HUM_ICON_POS  = (700,10)
S_HUM_TEXT_POS  = (740,10)

# GUI Countdown timer screen
TIMER_TEXT_SIZE  = 300
TIMER_TEXT_COLOR = (145, 234, 252)
TIMER_TEXT_yPOS  = 90
TIMER_ALARM_FILE = "./misc/warning.wav"
CAM_SHUTTER_FILE = "./misc/shutter.wav"
# GUI Talking screen
TALKING_TEXT_SIZE  = 22
TALKING_TEXT_COLOR = (0, 0, 0)
TALKING_TEXT_X     = 50
TALKING_TEXT_Y     = 350
TALKING_TEXT_W     = 700
TALKING_TEXT_H     = 200
MOOD_EYE_1_POS     = (290,75)
MOOD_EYE_2_POS     = (400,75)

