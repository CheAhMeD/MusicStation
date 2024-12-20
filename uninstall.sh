#!/bin/bash
#https://github.com/CheAhMeD/MusicStation.git

MUSIC_STATION_USER_DIR=/home/volumio/MusicStation

#Coloring 
GREEN="32"
YELLOW="33"
BOLDGREEN="\e[1;${GREEN}m"
ITALICYELLOW="\e[3;${YELLOW}m"
ENDCOLOR="\e[0m"

echo -e "${BOLDGREEN}Uninstalling MusicStation...${ENDCOLOR}"
echo -e "${ITALICYELLOW}NOTE:${ENDCOLOR}"
echo -e "${ITALICYELLOW}This script will not remove the installed Linux packages nor the installed python packages...${ENDCOLOR}"

echo -e "${BOLDGREEN}Disabling MusicStation service...${ENDCOLOR}"
systemctl stop musicstation.service
systemctl disable musicstation.service
systemctl daemon-reload

echo -e "${BOLDGREEN}Removing start scripts...${ENDCOLOR}"
sudo rm -rf /opt/musicstation.sh
sudo rm -rf /lib/systemd/system/musicstation.service

echo -e "${BOLDGREEN}Finished...${ENDCOLOR}"
