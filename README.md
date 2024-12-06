# MusicStation (For VolumioOS)

A RaspberryPi 4 powered simple yet smart music station.




## Installation
#### Downlaod and install Volumio OS on your Raspberry pi 4

https://volumio.com/get-started/


#### Install Touch Display plugin on Volumio OS

Follow instructions:
https://developers.volumio.com/plugins/plugins-overview

#### Connect to the unit (using ssh)

https://developers.volumio.com/SSH%20Connection

#### Navigate to home directory

```bash
  cd
```

#### Download the install script

```bash
  wget 'https://raw.githubusercontent.com/CheAhMeD/MusicStation/refs/heads/main/install.sh?token=GHSAT0AAAAAAC3Q7ZNVGPYC3ZZHUT2HJA5CZ2S36HQ' -O install.sh
```

#### Install MusicStation with the provided script

```bash
  sudo ./install.sh
```

#### follow the steps in the terminal.
    
## Manual Installation

#### Manual installation assmuing you already have a Volumio OS installed on a raspberry pi 4 and touch display plugin is also installed!

Connect to your raspberry pi

https://developers.volumio.com/SSH%20Connection

follow the steps in install.sh file.



## Deployment

To deploy MusicStation run

```bash
  cd $install_directory
  sudo python3 main.py
```


## Requirements
#### Linux Drivers 
- v4l-utils
- bluetooth
- bluez
#### Python Packages 
- pygame (with apt-get)
- pip3 (with apt-get)
- smbus2
- colorama
- adafruit-circuitpython-neopixel
- rpi_ws281x
- RPi.GPIO
- bmp280
- pvporcupine
- pyaudio
- SpeechRecognition
- sounddevice
- openai==1.39.0 (version required!!!)
- pycountry
- picamera
- adafruit-circuitpython-led-animation
- socketIO-client
- bleak
- tinytuya
- pycryptodome

#### USB Sound Card (if used)
If you require using an external USB Sound card it needs to be set properly:
- remove pulseaudio 
```bash
  sudo apt-get remove pulseaudio
```
- Check sound hardware
```bash
  cat /proc/asound/cards
```
this should return <card number>
example output:
```
 0 [Headphones     ]: bcm2835_headpho - bcm2835 Headphones
                      bcm2835 Headphones
 5 [Device         ]: USB-Audio - USB PnP Sound Device
                      C-Media Electronics Inc. USB PnP Sound Device at usb-0000:01:00.0-1.3
```
<card number> is 5
- Update the sound defaults
in ~/.asoundrc :
```
pcm.!default {
  type asym
  capture.pcm "mic"
}
pcm.mic {
  type plug
  slave {
    pcm "hw:<card number>,0"
  }
}
```
- Disable the internal (Broadcom) sound card
```
  sudo nano /boot/config.txt
```
update to the following
```
#Enable audio (loads snd_bcm2835)
#dtparam=audio=on
dtparam=audio=off
```
- Set USB Card to default
```
  sudo nano /usr/share/alsa/alsa.conf
```
then replace:
```
#defaults.ctl.card 0
#defaults.pcm.card 0
```
with:
```
defaults.ctl.card <card number>
defaults.pcm.card <card number>
```

## Usage/Examples

MusicStation is voice controlled only...

    1. Say the wake word 'jarvis'
    2. Ask anything from Jarvis...



## Authors

- [@CheAhmed](https://github.com/CheAhMeD)


## Badges

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
## License

[MIT](https://choosealicense.com/licenses/mit/)

