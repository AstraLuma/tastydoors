#!/usr/bin/python

import couchdb
from time import sleep
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

with PN532(SERIAL_PORT) as reader:
	setStatus(OFF)
	# Configure PN532:
	#  - Disable pre/postamble
	try:
		cards = couchdb.Database(DATABASE)
		while True:
			# AutoPoll until card is found
			setStatus(reader, IDLE)
			poll = reader.doit(In.AutoPoll(...))
			for target in poll.Targets:
				setStatus(reader, WORKING)
				# Query for card
				# Unlock A
				# Unlock B
				# Read data
				# Hash & Compare
				if ok:
					# Open Door
					setStatus(reader, SUCCESS)
					openDoor()
				else:
					setStatus(reader, FAILURE)
					sleep(1.0)
	except (KeyboardInterrupt, SystemExit):
		# Suppress traceback on normal exiting
		pass
	finally:
		setStatus(reader, OFF)
