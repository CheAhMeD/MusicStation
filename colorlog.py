#!/usr/bin/env python3
'''
    Python module format & colorize the logs using 
    logging and colorama packages

    Author: Ahmed Chehaibi (https://github.com/CheAhMeD)

    Local Control Classes
        ColorFormatter(...)

        ColorLogger(...)
            inherits from logging.Logger
        

'''
import logging
from colorama import init, Fore, Back

init(autoreset=True)


class ColorFormatter(logging.Formatter):
    # Change this dictionary to suit your coloring needs!
    COLORS = {
        "WARNING": Fore.RED,
        "ERROR": Fore.RED + Back.WHITE,
        "DEBUG": Fore.WHITE,
        "INFO": Fore.GREEN,
        "CRITICAL": Fore.BLACK + Back.YELLOW
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        if color:
            record.name = color + record.name
            record.levelname = color + record.levelname
            record.msg = color + record.msg
        return logging.Formatter.format(self, record)


class ColorLogger(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.DEBUG)
        color_formatter = ColorFormatter("%(name)-10s %(levelname)-18s %(message)s")
        console = logging.StreamHandler()
        console.setFormatter(color_formatter)
        self.addHandler(console)
