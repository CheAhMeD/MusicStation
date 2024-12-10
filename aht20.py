#!/usr/bin/env python3
'''
    Python module to interface with AHT20:
    AHT20 Temperature & Humidity Sensor

 Author: Ahmed Chehaibi (https://github.com/CheAhMeD)

 Local Control Classes
    AHT20(...)
        @param BusNum: I2C Bus number (default 1)

 External helpers:
    The AHT20 class uses crc8_helper module to help 
    calculate the required CRC
'''
from smbus2 import SMBus
import time
from crc8_helper import AHT20_crc8_check

def get_normalized_bit(value, bit_index):
    # Return only one bit from value indicated in bit_index
    return (value >> bit_index) & 1

AHT20_I2CADDR       = 0x38
AHT20_CMD_SOFTRESET = 0xBA
AHT20_CMD_STATUS    = 0x71
AHT20_CMD_INIT_REG  = 0xBE
AHT20_CMD_INIT_DAT  = [0x08, 0x00]
AHT20_CMD_MEASURE_REG = 0xAC
AHT20_CMD_MEASURE_DAT = [0x33, 0x00]
AHT20_STATUSBIT_BUSY       = 7              # The 7th bit is the Busy indication bit. 1 = Busy, 0 = not.
AHT20_STATUSBIT_CALIBRATED = 3              # The 3rd bit is the CAL (calibration) Enable bit. 1 = Calibrated, 0 = not

class AHT20:
    # I2C communication driver for AHT20, using only smbus2

    def __init__(self, BusNum=1):
        # Initialize AHT20
        self.BusNum = BusNum
        self.i2c_bus = SMBus(self.BusNum)
        self.cmd_soft_reset()

        # Check for calibration, if not done then do and wait 10 ms
        if not self.get_status_calibrated == 1:
            self.cmd_initialize()
            while not self.get_status_calibrated() == 1:
                time.sleep(0.01)

    def cmd_soft_reset(self):
        # Send the command to soft reset
        self.i2c_bus.write_byte(AHT20_I2CADDR, AHT20_CMD_SOFTRESET)
        time.sleep(0.04)    # Wait 40 ms after poweron
        return True

    def cmd_initialize(self):
        # Send the command to initialize (calibrate)
        self.i2c_bus.write_i2c_block_data(AHT20_I2CADDR, AHT20_CMD_INIT_REG, AHT20_CMD_INIT_DAT)
        time.sleep(0.01)    # Wait 10ms after sending init command
        return True

    def cmd_measure(self):
        # Send the command to measure
        self.i2c_bus.write_i2c_block_data(AHT20_I2CADDR, AHT20_CMD_MEASURE_REG, AHT20_CMD_MEASURE_DAT)
        time.sleep(0.08)    # Wait 80 ms after measure
        return True

    def get_status(self):
        # Get the full status byte
        return self.i2c_bus.read_i2c_block_data(AHT20_I2CADDR, AHT20_CMD_STATUS, 1)[0]

    def get_status_calibrated(self):
        # Get the calibrated bit
        return get_normalized_bit(self.get_status(), AHT20_STATUSBIT_CALIBRATED)

    def get_status_busy(self):
        # Get the busy bit
        return get_normalized_bit(self.get_status(), AHT20_STATUSBIT_BUSY)

    def get_measure(self):
        # Get the full measure

        # Command a measure
        self.cmd_measure()

        # Check if busy bit = 0, otherwise wait 80 ms and retry
        while self.get_status_busy() == 1:
            time.sleep(0.08) # Wait 80 ns

        # Read data and return it
        return self.i2c_bus.read_i2c_block_data(AHT20_I2CADDR, 0x0, 7)

    def get_measure_CRC8(self):
        """
        This function will calculate crc8 code with G(x) = x8 + x5 + x4 + 1 -> 0x131(0x31), Initial value = 0xFF. No XOROUT.
        return: all_data (1 bytes status + 2.5 byes humidity + 2.5 bytes temperature + 1 bytes crc8 code), isCRC8_pass
        """
        all_data = self.get_measure()
        isCRC8_pass = AHT20_crc8_check(all_data)

        return all_data, isCRC8_pass
        


    def get_temperature(self):
        # Get a measure, select proper bytes, return converted data
        measure = self.get_measure()
        measure = ((measure[3] & 0xF) << 16) | (measure[4] << 8) | measure[5]
        measure = measure / (pow(2,20))*200-50
        return measure
    def get_temperature_crc8(self):
        isCRC8Pass = False
        while (not isCRC8Pass): 
            measure, isCRC8Pass = self.get_measure_CRC8()
            time.sleep(80 * 10**-3)
        measure = ((measure[3] & 0xF) << 16) | (measure[4] << 8) | measure[5]
        measure = measure / (pow(2,20))*200-50
        return measure

    def get_humidity(self):
        # Get a measure, select proper bytes, return converted data
        measure = self.get_measure()
        measure = (measure[1] << 12) | (measure[2] << 4) | (measure[3] >> 4)
        measure = measure * 100 / pow(2,20)
        return measure

    def get_humidity_crc8(self):
        isCRC8Pass = False
        while (not isCRC8Pass): 
            measure, isCRC8Pass = self.get_measure_CRC8()
            time.sleep(80 * 10**-3)
        measure = (measure[1] << 12) | (measure[2] << 4) | (measure[3] >> 4)
        measure = measure * 100 / pow(2,20)
        return measure
