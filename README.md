# WORK ON PROGRESS #

# Disclaimer #

#### Since this "project" was created without any prior preparation, it is just a collection of Python scripts that have been placed on top of one another to make it work. 
#### The MusicStation project began as a tiny script that used voice commands to control volumio music player, and it eventually developed into what it is today. 
#### Because some elements were added after the fact to the original script, you might notice some discrepancies in the scripts.


# MusicStation (For VolumioOS)

![splash](img/misc/logo.png)

A RaspberryPi 4 powered simple yet smart music station.


## System Overview
#### Architecture

![arch](music_station_arch.png)

#### Used Hardware

*MusicStation is a custom build music unit, from the wood box to the amplifier... it is not necessary to use the same setup I used to make your MusicStation*


##### Minimal
- Raspberry Pi 4:
  minimum 4Gb.
- A Touch Screen:
  The Official Raspberry Pi touch screen was used (800x480).
- A USB DAC:
  Any cheap usb based dac should work.
- A microphone (Any jack or usb microphone)
- An amplifier:
  I used a tube amplifier that I had custom-built a few years ago. Regretfully, I misplaced the schematics for it.
  However, any amplifier ought to function well with the setup.
- Passive speakers
- Power supply (5VDC)

##### Optional
- 12V to 5V DC step down convertor:
  If a 12V amplifier is being utilized, this is **necessary**; if not, a 5V DC power supply can be used to power the
  system. Just make sure it has enough amps to power everything, especially the LED controller if it's being utilized.
- Pir Sensor (presence detection)
- AHT20 Humidity and temperature sensor
- Colorful-X7 music controller
- WS2812b led strip (or something similar)
- 5VDC Relay
- RaspberryPi Camera (or any usb camera)
- Cables for external connectors (USB male to female, Ethernet male to female and any 3 pins connector for external LED strips if used)

**As long as you have the bare minimum of hardware (minimal section), you can build whatever system you want. You don't have to adhere to my setup.** 
**Please get in touch if you need any assistance setting up a system.***


## Installation
#### Downlaod and install Volumio OS on your Raspberry pi 4

https://volumio.com/get-started/


#### Install Touch Display plugin on Volumio OS

Follow the instructions here:

https://developers.volumio.com/plugins/plugins-overview

#### Connect to the unit (using ssh)

https://developers.volumio.com/SSH%20Connection

#### Navigate to home directory

```bash
cd
```

#### Clone MusicStation repo

```bash
sudo git clone https://github.com/CheAhMeD/MusicStation.git
```

#### Navigate to the user directory

```bash
cd /home/volumio/MusicStation
```

#### Make the install script executable

```bash
sudo chmod +x install.sh
```

#### Install MusicStation with the provided script

```bash
sudo ./install.sh
```

#### When prompted accept running tinytuya wizard

*!!!This step is required if you have a [Colorful-X7](https://www.aliexpress.com/item/1005007870851528.html) device in your music system!!!*
Follow the steps in install.sh file and make sure you accepted to run the last step (tinytuya wizard).
if not run:
```bash
sudo python3 -m tinytuya wizard
```
More info: https://github.com/jasonacox/tinytuya?tab=readme-ov-file#setup-wizard---getting-local-keys

## Deployment

To deploy MusicStation 
**Make sure you have the required API keys.**
- The API Keys are collected during installation but in case of error (there is no checks done on the keys)
- you can paste the correct keys in api_keys.py file (located in /home/volumio/MusicStation/api_keys.py)
```python
# To change accordingly
weather_key  = "OpenWeather_API_KEY_GOES_HERE"  # https://openweathermap.org/api
weather_city = "OpenWeather_CITY_GOES_HERE"     # format "City,COUNTRYCODE" eg : "Gent,BE"
open_ai_key  = "OpenAI_API_KEY_GOES_HERE"       # https://openai.com/index/openai-api/
picovice_key = "PICO_API_KEY_GOES_HERE"         # https://picovoice.ai/docs/api/picovoice-python/
colorful_id  = "TUYA_DEVICE_ID_GOES_HERE"       # Get it after running tinytuya wizard
colorful_ip  = "TUYA_DEVICE_IP_GOES_HERE"       # Get it after running tinytuya wizard
colorful_key = "TUYA_DEVICE_KEY_GOES_HERE"      # Get it after running tinytuya wizard
```
- run the following:
```bash
cd /home/volumio/MusicStation
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
card number is 5
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

MusicStation is voice mostly controlled only... Unless the Volumio UI is enabled then you can control the player as normal

    1. Say the wake word 'Jarvis'
    2. Ask specific command (from list below)...
    or ask Jarvis anything (Response from OpenAi)

TODO: finish the command list in here
| Phrase | Command       | Type          | Description                     |
| -------------- | ------------- | ------------- | ------------------------------- |
| Hey Jarvis! | Wake Up | JARVIS | Wake word for personal assitant. (The wake word is required to start a "conversation")|
| *********** | Ask OpenAI | JARVIS | Any phrase that doesn't compare to the preprogrammed sentences gets send to OpenAI. |
| Stop listening! | Sleep | JARVIS | Stops the personal assistance until next wake word. |
| Start a timer for **n time** | Start Timer | TIMER | Starts a timer for the specified time (eg: "Start a timer for 10 minutes 5 seconds"). |
| Stop timer! | Stop Timer | TIMER | Stops current timer. |
| Take a photo! | Take Photo | CAMERA | Takes a photo after 5 seconds. |
| ***** | ***** | ***** | ***** |
| ***** | ***** | ***** | ***** |
| ***** | ***** | ***** | ***** |



## Authors

- [@CheAhmed](https://github.com/CheAhMeD)


## Badges

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contribution

In addition to the built-in functions, the community is encouraged to contribute.
[How to?](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project)



