#!/usr/bin/env python3
'''
    Volumio helper functions
'''

import socketio
import time
import os
import logging
import colorlog
from settings import *

# Logger (Color):
logging.setLoggerClass(colorlog.ColorLogger)
log = logging.getLogger(APP_NAME)

volumioState   = None
volumioService = None
volumioURI     = None
volumioPlayList = []

# Client
sio = socketio.Client()

# System commands
def restartVolumio():
    os.system('volumio vrestart')

def startVolumio():
    os.system('volumio vstart')

def stopVolumio():
    os.system('volumio vstop')


# Touch Screen UI commands
def disableTouchScreenUI():
    os.system('systemctl stop volumio-kiosk.service')

def enableTouchScreenUI():
    os.system('systemctl daemon-reload')
    os.system('systemctl start volumio-kiosk.service')

# MISC
# TODO: Test this
def callMethod(endpoint, func_name, func_data):
    '''
        Calls a function in a specified endpoint (plugin)
        @param endpoint: a string used to target the plugin. 
        Its structure is a linux path like string containing the plugin category, 
        a slash and the plugin name. 
        An example: endpoint:'music_service/spop'.
        @param name: a string containing the name of the method to be executed.
        @param data: is a complex value (can be a string or a Json) and is passed 
        as is to the method.
    '''
    payload = {
        "endpoint": str(endpoint),
        "method": str(func_name),
        "data": func_data
    }
    sio.emit('callMethod', payload)
    time.sleep(.01)

def importServicePlaylists():
    '''
        Get current service playlists and adds them to 
        volumio without playing
    '''
    sio.emit('importServicePlaylists')
    time.sleep(.01)

def replaceAndPlay(service, uri):
    '''
        Plays music on a specified service:
        Replaces the current service with a new one 
        and plays a new playlist
        @param service: service type 
    '''
    if service not in ['spop', 'mpd', 'webradio']:
        log.error("[Volumio] Unsupported service: " + str(service))
        return
    
    payload = {
            "service": str(service),
            "uri": uri,
        }
    sio.emit('replaceAndPlay', payload)
    time.sleep(.01)


# Playback Commands
def playMusic():
    ''' 
        Plays the current URI on volumio 
    '''
    #os.system('volumio play')
    sio.emit('play')
    time.sleep(.01)

def stopMusic():
    #os.system('volumio stop')
    sio.emit('stop')
    time.sleep(.01)

def pauseMusic():
    #os.system('volumio pause')
    sio.emit('pause')
    time.sleep(.01)

def clearQueue():
    #os.system('volumio clear')
    sio.emit('clear')
    time.sleep(.01)

def setVolume(vol:int):
    if vol in range(0,100):
        sio.emit('volume', int(vol))
        time.sleep(.01) # needed to register the action 
    else:
        log.error("[Volumio] Cannot set the volume to " + str(vol) +\
                         " Volume accepted range is 0-100!")

# 
def getState():
    sio.emit('getState')
    time.sleep(.01)

def search(query):
    sio.emit('search', "{value:" + str(query) + "}")
    time.sleep(.01)

def getQueue():
    sio.emit('getQueue')
    time.sleep(.01)

def getPlaylists():
    sio.emit('listPlaylist')
    time.sleep(.01)


# SocketIO connection
@sio.on('pushListPlaylist')
def on_message(data):
    volumioPlayList = data
    if len(volumioPlayList) > 0:
        print('Playlist: ' + str(volumioPlayList))
    else:
        log.info("[Volumio] Couldn't find any saved playlist!")

@sio.on('pushQueue')
def on_message(data):
    print('Queue: ' + str(data))

@sio.on('pushState')
def on_message(data):
    volumioState   = data['status']
    volumioService = data['service']
    volumioURI     = data['uri']
    print(f'Volumio: {volumioState}, {volumioURI}, {volumioService}')

@sio.event
def connect():
    log.info("[Volumio] Connection successful!")
    #sio.emit('volume',100)

@sio.event
def disconnect():
    log.info("[Volumio] Disconnected")

def connect():
    sio.connect('http://localhost:3000')

def disconnect():
    sio.disconnect()
