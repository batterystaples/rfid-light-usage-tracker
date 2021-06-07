#!/usr/bin/python3
import time
import os
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import sqlite3
from datetime import datetime
import signal

reader = SimpleMFRC522()

BUZZER_PIN = 38
PHOTORESISTOR_PIN = 40
DATABASE = "electricity.db"

GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(PHOTORESISTOR_PIN, GPIO.IN)

c = sqlite3.connect(os.path.dirname(__file__) + "/" +DATABASE)
cur = c.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS usage (name VARCHAR(255), month INT, year INT, time INT)")
c.commit()
c.close()

def buzz(gap):
	GPIO.output(BUZZER_PIN, GPIO.HIGH)
	time.sleep(gap)
	GPIO.output(BUZZER_PIN, GPIO.LOW)
	time.sleep(gap)

def handler(signum, frame):
	raise Exception("Timeout")

def read_rfid():
	signal.signal(signal.SIGALRM, handler)
	signal.alarm(1)
	try:
		id, text = reader.read()
		signal.alarm(0)
		if len(text) > 0:
			return text
		# If there was an error reading the card, buzz for a longer
		# length of time (so the user knows to tap again) and return
		# "ERROR"
		else:
			buzz(1)
			return "ERROR"
	except Exception:
		return "NONE"

def save_elapsed_time(name, time):
	month = datetime.today().strftime("%m")
	year = datetime.today().strftime("%Y")
	c = sqlite3.connect(os.path.dirname(__file__) + "/" + DATABASE)
	cur = c.cursor()
	r = cur.execute("SELECT time FROM usage WHERE name = ? AND month = ? AND year = ?", (name, month, year))
	old_time = r.fetchone()
	if old_time != None:
		new_time = old_time[0] + time
		cur.execute("UPDATE usage SET time = ? WHERE name = ? AND month = ? AND year = ?", (new_time, name, month, year))
	else:
		cur.execute("INSERT INTO usage VALUES (?, ?, ?, ?)", (name, month, year, time))
	c.commit()
	c.close()


current_user = "NONE"
start_time = time.time()

try:
	while 1:
		rfid = read_rfid()
		if rfid == current_user and rfid != "NONE" and rfid != "ERROR":
			save_elapsed_time(current_user, time.time()-start_time)
			current_user = "NONE"
		elif rfid != "NONE" and rfid != "ERROR" and GPIO.input(PHOTORESISTOR_PIN):
			if current_user != "NONE":
				save_elapsed_time(current_user, time.time()-start_time)
			start_time = time.time()
			current_user = rfid
			# Wait until the user removes their card
			while rfid == current_user and rfid != "ERROR":
				rfid = read_rfid()

		# If the light is on and no users have tapped on, make a
		# buzzing sound
		if GPIO.input(PHOTORESISTOR_PIN):
			if current_user == "NONE":
				buzz(0.1)

		# If the light is off and a user forgot to tap off,
		# end their session for them
		elif current_user != "NONE":
			save_elapsed_time(current_user, time.time()-start_time)
			current_user = "NONE"

except KeyboardInterrupt:
	GPIO.cleanup()
