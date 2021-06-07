#!/usr/bin/python3

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
        text = input('Enter the user\'s name:')
        print("Now place the user's tag on the reader")
        reader.write(text)
        print("Tag setup complete!")
finally:
        GPIO.cleanup()
