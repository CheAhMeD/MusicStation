#!/bin/bash

MUSIC_STATION_RUN_SCRIPT="/home/volumio/musicstation/main.py"
MUSIC_STATION_REPO="https://github.com/CheAhMeD/MusicStation.git" 
MUSIC_STATION_USER_DIR="/home/volumio/musicstation"

sudo apt-get update
# camera tools
sudo apt-get install v4l-utils
# bluetooth tools
sudo apt-get install bluetooth bluez

# Install Python packages
echo "Installing Python packages..."
sudo apt-get -y install python3-pip
sudo apt-get -y install python3-pygame

# Install Python libs
sudo pip3 install smbus2
sudo pip3 install colorama
sudo pip3 install adafruit-circuitpython-neopixel
sudo pip3 install rpi_ws281x
sudo pip3 install RPi.GPIO
sudo pip3 install bmp280
sudo pip3 install pvporcupine
sudo pip3 install pyaudio
sudo pip3 install SpeechRecognition
sudo pip3 install sounddevice
sudo pip3 install openai==1.39.0 # version 1.39.0 required!!! otherwise it will give an install error
sudo pip3 install pycountry
sudo pip3 install adafruit-circuitpython-led-animation
sudo pip3 install socketIO-client
sudo pip3 install bleak
sudo pip3 install tinytuya
sudo pip3 install pycryptodome


# Create user directories
echo "Creating user directories (if not exist)..."
mkdir -p "${MUSIC_STATION_USER_DIR}"

# Fetch repo
echo "Fetching Jarvis Repo..."
if [ -d "$MUSIC_STATION_USER_DIR" ]; then
    cd "$MUSIC_STATION_USER_DIR"
    echo "Cloning Jarvis repo into $MUSIC_STATION_USER_DIR..."
    git clone $MUSIC_STATION_REPO
else
    echo "Could not create temporary directory for MusicStation repo files!"
fi

# Install fonts
echo "Installing fonts..."
sudo cp "$MUSIC_STATION_USER_DIR"/fonts/*.ttf /usr/share/fonts

# Make volumio owner
echo "Setting ownership..."
chown volumio:volumio "$MUSIC_STATION_USER_DIR"

# Make jarvis script executable
echo "Making $MUSIC_STATION_RUN_SCRIPT executable..."
chmod +x "${MUSIC_STATION_RUN_SCRIPT}"

echo "Starting TinyTuya Setup Wizard..."
echo "  Before continuing make sure the steps 1 & 3 described in "
echo "  https://github.com/jasonacox/tinytuya/tree/master?tab=readme-ov-file#setup-wizard---getting-local-keys"
echo "  are followed..."
read -p "Continue? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
sudo python3 -m tinytuya wizard


echo "Finished..."

# TODO: finish this later
# TODO: Make jarvis script autostart