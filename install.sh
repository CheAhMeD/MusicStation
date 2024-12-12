#!/bin/bash
#https://github.com/CheAhMeD/MusicStation.git

MUSIC_STATION_RUN_SCRIPT=/home/volumio/MusicStation/main.py
MUSIC_STATION_API_SCRIPT=/home/volumio/MusicStation/api_keys.py
MUSIC_STATION_USER_DIR=/home/volumio/MusicStation
MUSIC_STATION_GPIO_PATH=/sys/class/gpio

X7_GPIO=19
ON="1"
OFF="0"

# Utility functions to control GPIOs
exportPin()
{
  if [ ! -e $MUSIC_STATION_GPIO_PATH/gpio$1 ]; then
    echo "$1" > $MUSIC_STATION_GPIO_PATH/export
  fi
}

unexportPin()
{
  if [ ! -e $MUSIC_STATION_GPIO_PATH/gpio$1 ]; then
    echo "$1" > $MUSIC_STATION_GPIO_PATH/unexport
  fi
}

setOutput()
{
  echo "out" > $MUSIC_STATION_GPIO_PATH/gpio$1/direction
}

setGpioState()
{
  echo $2 > $MUSIC_STATION_GPIO_PATH/gpio$1/value
}

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

# Install fonts
echo "Installing fonts..."
sudo cp $MUSIC_STATION_USER_DIR/fonts/*.ttf /usr/share/fonts

# Make volumio owner
echo "Setting ownership..."
sudo chown volumio:volumio $MUSIC_STATION_USER_DIR
sudo chown volumio:volumio $MUSIC_STATION_API_SCRIPT

# Make jarvis script executable
echo "Making $MUSIC_STATION_RUN_SCRIPT executable..."
sudo chmod +x $MUSIC_STATION_RUN_SCRIPT

read -p "Do you want to setup a Colorful-X7 device? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
echo "Starting TinyTuya Setup Wizard..."
echo "  Before continuing make sure the steps 1 & 3 described in "
echo "  https://github.com/jasonacox/tinytuya/tree/master?tab=readme-ov-file#setup-wizard---getting-local-keys"
echo "  are followed..."
read -p "Continue? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
# Turn On the Device
exportPin $X7_GPIO
setOutput $X7_GPIO
setGpioState $X7_GPIO $ON
# Start tinytuya wizard
sudo python3 -m tinytuya wizard
# Turn Off the device
setGpioState $X7_GPIO $OFF
unexportPin $X7_GPIO

echo "Don't forget to update $MUSIC_STATION_API_SCRIPT with the API Keys"
echo "Finished..."

# TODO: finish this later
# TODO: Make jarvis script autostart
