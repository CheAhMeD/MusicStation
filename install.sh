#!/bin/bash
#https://github.com/CheAhMeD/MusicStation.git

MUSIC_STATION_RUN_SCRIPT=/home/volumio/MusicStation/main.py
MUSIC_STATION_EXIT_SCRIPT=/home/volumio/MusicStation/cleanup.py
MUSIC_STATION_API_SCRIPT=/home/volumio/MusicStation/api_keys.py
MUSIC_STATION_USER_DIR=/home/volumio/MusicStation
MUSIC_STATION_GPIO_PATH=/sys/class/gpio

#Coloring 
RED="31"
GREEN="32"
YELLOW="33"
BOLDGREEN="\e[1;${GREEN}m"
ITALICYELLOW="\e[3;${YELLOW}m"
ITALICRED="\e[3;${RED}m"
ENDCOLOR="\e[0m"

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

echo -e "${BOLDGREEN}Installing Linux packages...${ENDCOLOR}"
sudo apt-get update
# camera tools
sudo apt-get install v4l-utils
# bluetooth tools
sudo apt-get install bluetooth bluez

# Install Python packages
echo -e "${BOLDGREEN}Installing Python packages...${ENDCOLOR}"
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
echo -e "${BOLDGREEN}Installing fonts...${ENDCOLOR}"
sudo cp $MUSIC_STATION_USER_DIR/fonts/*.ttf /usr/share/fonts

# Make volumio owner
echo -e "${BOLDGREEN}Setting ownership...${ENDCOLOR}"
sudo chown volumio:volumio $MUSIC_STATION_USER_DIR
sudo chown volumio:volumio $MUSIC_STATION_API_SCRIPT

# Make jarvis script executable
echo -e "${BOLDGREEN}Making $MUSIC_STATION_RUN_SCRIPT executable...${ENDCOLOR}"
sudo chmod +x $MUSIC_STATION_RUN_SCRIPT

echo -e "${BOLDGREEN}Starting TinyTuya Setup Wizard...${ENDCOLOR}"
echo -e "  ${ITALICYELLOW} Before continuing make sure the steps 1 & 3 described in ${ENDCOLOR}"
echo "  https://github.com/jasonacox/tinytuya/tree/master?tab=readme-ov-file#setup-wizard---getting-local-keys"
echo -e "  ${ITALICYELLOW}are followed...${ENDCOLOR}"
read -p $'\e[1;34mContinue? (Y/N): \e[0m' confirm
if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then 
echo -e "  ${ITALICYELLOW}Setting up tuya device...${ENDCOLOR}"
# Turn On the Device
exportPin $X7_GPIO
setOutput $X7_GPIO
setGpioState $X7_GPIO $ON
# Start tinytuya wizard
sudo python3 -m tinytuya wizard
# Turn Off the device
setGpioState $X7_GPIO $OFF
unexportPin $X7_GPIO
else 
echo -e "${ITALICRED}Skipping Tuya Setup Wizard...${ENDCOLOR}"
fi


echo -e "${BOLDGREEN}Collecting MusicStation API Keys...${ENDCOLOR}"
read -p $'\e[1;34mOpenWeatherMap API Key: \e[0m' owmKey
read -p $'\e[1;34mOpenWeatherMap City: \e[0m' owmCity
read -p $'\e[1;34mOpenAI API Key: \e[0m' oaiKey
read -p $'\e[1;34mPicovice API Key: \e[0m' pvKey
read -p $'\e[1;34mColorful X7 Device ID: \e[0m' x7Id
read -p $'\e[1;34mColorful X7 IP Address: \e[0m' x7Ip
read -p $'\e[1;34mColorful X7 Device Key: \e[0m' x7Key

cat > $MUSIC_STATION_API_SCRIPT << EOL
weather_key  = "${owmKey}"
weather_city = "${owmCity}"
open_ai_key  = "${oaiKey}"
picovice_key = "${pvKey}"
colorful_id  = "${x7Id}"
colorful_ip  = "${x7Ip}"
colorful_key = "${x7Key}"
EOL

echo -e "${BOLDGREEN}Collected API Keys...${ENDCOLOR}"
cat $MUSIC_STATION_API_SCRIPT

# echo -e "${BOLDGREEN}Disabling Volumio Kiosk service ...${ENDCOLOR}"
# systemctl stop volumio-kiosk.service
# systemctl daemon-reload

echo -e "${BOLDGREEN}Fixing MusicStation authentification issue...${ENDCOLOR}"
sudo echo "#%PAM-1.0
# Fixing ssh 'auth could not identify password for [username]'
auth       sufficient   pam_permit.so

@include common-auth
@include common-account
@include common-session-noninteractive" > /etc/pam.d/sudo

echo -e "${BOLDGREEN}Creating MusicStation start script...${ENDCOLOR}"
sudo echo "#!/bin/bash
openbox-session &
while true; do
  PYTHONUNBUFFERED=1 /usr/bin/sudo /usr/bin/python3 $MUSIC_STATION_RUN_SCRIPT
done" > /opt/musicstation.sh
sudo /bin/chmod +x /opt/musicstation.sh

echo -e "${BOLDGREEN}Creating Systemd Unit for MusicStation...${ENDCOLOR}"
sudo echo "[Unit]
Description=Music Station
Wants=volumio.service
After=volumio.service
[Service]
Type=simple
User=volumio
Group=volumio
ExecStart=/usr/bin/startx /etc/X11/Xsession /opt/musicstation.sh -- -nocursor
ExecStop=PYTHONUNBUFFERED=1 /usr/bin/sudo /usr/bin/python3 $MUSIC_STATION_EXIT_SCRIPT
[Install]
WantedBy=multi-user.target
" > /lib/systemd/system/musicstation.service
sudo chmod 644 /lib/systemd/system/musicstation.service 
sudo systemctl daemon-reload
sudo systemctl enable musicstation.service
sudo systemctl start musicstation.service

echo -e "${BOLDGREEN}Restarting Volumio...${ENDCOLOR}"
volumio vrestart

echo -e "${BOLDGREEN}Finished...${ENDCOLOR}"

# TODO: finish this later
# TODO: Make jarvis script autostart
