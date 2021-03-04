# SDA connects to Pin 24.
# SCK connects to Pin 23.
# MOSI connects to Pin 19.
# MISO connects to Pin 21.
# GND connects to Pin 6.
# RST connects to Pin 22.
# 3.3v connects to Pin 1.

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
GPIO.setwarnings(False)

reader = SimpleMFRC522()

def tempel():
    print("tempel kartu")
    id = reader.read()
    return id
    # print("id kartu adalah = {}".format(id))

GPIO.cleanup()