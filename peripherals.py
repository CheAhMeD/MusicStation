#!/usr/bin/env python3

import board
import neopixel
import threading
import RPi.GPIO as GPIO
from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation import color
from tinytuya.Contrib import ColorfulX7Device

GPIO.setmode(GPIO.BCM)

# LEDs thread (for RT animations)
class Leds(threading.Thread):
    """ 
    Provides a way to control two WS2812b strips 
    and display some effects.
    The led strips left and right are hardwired to
    respectively board.D18 and board.D12 pins of the RPI
    @param num_leds: number of LEDs per strip
    """
    def __init__(self, num_leds, *args, **kwargs):
        super(Leds, self).__init__(*args, **kwargs)
        self.num_pixels  = num_leds
        self.left_strip  = neopixel.NeoPixel(board.D18, self.num_pixels, pixel_order=neopixel.RGB)
        self.right_strip = neopixel.NeoPixel(board.D12, self.num_pixels, pixel_order=neopixel.RGB)
        self.curAnim     = 'cycle' #startup animation
        self.blink_left  = Blink(self.left_strip, 0.5, color.RED)
        self.blink_right = Blink(self.right_strip, 0.5, color.RED)
        self.solid_left  = Solid(self.left_strip, color.PURPLE)
        self.solid_right = Solid(self.right_strip, color.PURPLE)
        self.cycle_left  = ColorCycle(self.left_strip, 2.5, [color.MAGENTA, color.ORANGE, color.TEAL])
        self.cycle_right = ColorCycle(self.right_strip, 2.5, [color.MAGENTA, color.ORANGE, color.TEAL])
        self.pulse1_left  = Pulse(self.left_strip, 0.2, color.BLUE, 5)
        self.pulse1_right = Pulse(self.right_strip, 0.2, color.BLUE, 5)
        self.pulse2_left  = Pulse(self.left_strip, 0.1, color.GREEN, 3)
        self.pulse2_right = Pulse(self.right_strip, 0.1, color.GREEN, 3)
        self.seq_left     = AnimationSequence(
            self.solid_left,
            self.blink_left,
            self.cycle_left,
            self.pulse1_left,
            self.pulse2_left,
            advance_interval=5,
            auto_clear=True,
            )
        self.seq_right   = AnimationSequence(
            self.solid_right,
            self.blink_right,
            self.cycle_right,
            self.pulse1_right,
            self.pulse2_right,
            advance_interval=5,
            auto_clear=True,)
        self.animations  = {'blink':(self.blink_left, self.blink_right), 
                            'solid':(self.solid_left, self.solid_right),
                            'cycle':(self.cycle_left, self.cycle_right), 
                            'talking':(self.pulse1_left, self.pulse1_right),
                            'listening':(self.pulse2_left, self.pulse2_right),
                            'sequence':(self.seq_left, self.seq_right)
                            }
    
    def run(self):
        ''' Running the animation forever 
        '''
        while True:
            #animate both strips
            self.animations[self.curAnim][0].animate()
            self.animations[self.curAnim][1].animate()


    def setActiveAnimation(self, anim):
        if anim in self.animations.keys():
            self.curAnim = anim
        else:
            print('[LEDS] Wrong animation key: ' + str(anim))
            print('[LEDS] Available keys: ' + str(self.animations.keys()))

    def clearAll(self):
        """Clear both strips"""
        self.left_strip.deinit()
        self.right_strip.deinit()



class PirSensor():
    """ Motion Sensor PIR
    the sensor is hardwired on board.D5 
    """
    def __init__(self, pin):
        # setup the GPIO pin
        self.status = False
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def start(self):
        print("[PIR Sensor] Motion Detection ON!")
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.sensorRiseCB, bouncetime=300)
    
    # Callback on rising edge
    def sensorRiseCB(self, channel):
        print("[PIR Sensor] Motion detected! Channel: " + str(channel))
        self.status = GPIO.input(self.pin)

    # Get the current status
    def getStatus(self):
        return self.status
    
    def stop(self):
        print("[PIR Sensor] Motion Detection OFF!")
        GPIO.remove_event_detect(self.pin)

class Equilizer():
    """ 
        Sound reactive led equilizer controller
    """
    def __init__(self, relayPin, devId, devAdr, devKey):
        # setup the GPIO pin
        self.isPowered = False
        self.pin = relayPin
        GPIO.setup(relayPin, GPIO.OUT)
        self.controller = ColorfulX7Device.ColorfulX7Device(
            dev_id=devId, 
            address=devAdr, 
            local_key=devKey, 
            version="3.5"
        )
    # Turn on
    def powerOn(self):
        print("[EQUILIZER]: Powering ON!")
        self.isPowered = True
        GPIO.output(self.pin, GPIO.HIGH)

    # Turn OFF
    def powerOff(self):
        print("[EQUILIZER]: Powering OFF!")
        self.isPowered = False
        GPIO.output(self.pin, GPIO.LOW)
    
    # Get the power status
    def getStatus(self):
        return self.isPowered


