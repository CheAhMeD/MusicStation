#!/usr/bin/env python3

import jarvis
import threading
import sys
import time
import logging
import colorlog
import pygame as pg
from settings import *
from peripherals import PirSensor
from tinytuya.Contrib import ColorfulX7Device

logging.setLoggerClass(colorlog.ColorLogger)
log = logging.getLogger(APP_NAME)

# Music Controller
x7 = ColorfulX7Device.ColorfulX7Device(
        dev_id=EQUILIZER_DEVICE_ID, 
        address=EQUILIZER_DEVICE_IP, 
        local_key=EQUILIZER_DEVICE_KEY, 
        version="3.5"
)
# Start Motion Sensor:
pirSensor = PirSensor(PIR_PIN)

# This is totally unecessary since we can load all the gifs 
# during __init__ of the gui (MusicStationGUI()) it just gives 
# a much nicer effect 
def init():
    # Start the GUI splash screen
    jarvis.gui.splashScreen.show()
    jarvis.gui.splashScreen.updateProgressMessage(APP_NAME + " Loading Jarvis moods")
    jarvis.gui.loadMoods()

def startMusicStation():
    jarvis.gui.splashScreen.updateProgressMessage(APP_NAME + " Stating threads")
    # Create Jarvis thread
    jarvisThread = threading.Thread(target=jarvis.runJarvis)
    jarvisThread.daemon = True
    jarvisThread.start()
    # Starting PIR Sensor
    pirSensor.start()
    # Turn on the colorful-x7
    x7.switch_on()
    # Start LEDs animations thread
    jarvis.ledsAnimationThread.start()
    # create a thread to read sensors
    sensorsReadingsThread = threading.Thread(target=jarvis.sensorsReadings)
    sensorsReadingsThread.daemon = True
    sensorsReadingsThread.start()
    # Create a weather fetching thread
    weatherReadingsThread = threading.Thread(target=jarvis.weatherReadings)
    weatherReadingsThread.daemon = True
    weatherReadingsThread.start()
    # GUI main screen
    jarvis.gui.splashScreen.updateProgressMessage(APP_NAME + " Initialization Done!")
    time.sleep(2)
    jarvis.gui.mainLoop()


def cleanUp():
    # Clean up and exit
    jarvis.ledsAnimationThread.clearAll()
    pirSensor.stop()
    x7.switch_off()
    pg.mixer.quit()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    # initilialise the system
    init()
    # Start Music Station threads
    try:
        startMusicStation()
    except Exception as e_:
        log.error(APP_NAME + " Exception: " + str(e_))
    finally:
        cleanUp()
