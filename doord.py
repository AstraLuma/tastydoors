#!/usr/bin/python

import couchdb
from pn532 import *

# Configuration Options
SERIAL_PORT = "/dev/ttyS0"
DATABASE = "http://localhost/cards"

# Status contstants
OFF = intern('off')
IDLE = intern('idle')
WORKING = intern('working')
SUCCESS = intern('success')
FAILURE = intern('failure')

def setStatus(reader, status):
	"""
	Sets the status LED(s).
	"""

def openDoor():
	"""
	Opens door, waits, closes door.
	"""

try:
	with PN532(SERIAL_PORT) as reader:
		cards = couchdb.Database(DATABASE)
		while True:
			# AutoPoll until card is found
			# Query for card
			# Unlock A
			# Unlock B
			# Read data
			# Hash & Compare
			# Open Door
			pass
except (KeyboardInterrupt, SystemExit):
	pass
