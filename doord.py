#!/usr/bin/python

import couchdb
from time import sleep
from pn532 import *

# Configuration Options
SERIAL_PORT = "/dev/ttyAMA0"
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

def openDoor(reader):
	"""
	Opens door, waits, closes door.
	"""
	setStatus(reader, SUCCESS)

def reject(reader):
	"""
	Rejects card.
	"""
	setStatus(reader, FAILURE)
	sleep(1.0)

with PN532(SERIAL_PORT) as reader:
	reader.send(ACK()) # Probably ignored?
	setStatus(OFF)
	# Configure PN532:
	#  - Disable pre/postamble
	try:
		cards = couchdb.Database(DATABASE)
		while True:
			# AutoPoll until card is found
			setStatus(reader, IDLE)
			poll = reader.doit(In.AutoPoll(...))
			for Tg, target in enumerate(poll.Targets):
				setStatus(reader, WORKING)
				# Query for card
				card = ...
				if card is None:
					reject()
					continue
				# Unlock A
				auth = reader.doit(In.DataExchange(Tg, [0x60, card.block, card.key[:6]]))
				# Unlock B
				auth = reader.doit(In.DataExchange(Tg, [0x61, card.block, card.key[6:]]))
				# Read data
				data = reader.doit(In.DataExchange(Tg, 0x30, card.block))
				# Hash & Compare
				if ok:
					# Open Door
					openDoor()
				else:
					reject()
	except (KeyboardInterrupt, SystemExit):
		# Suppress traceback on normal exiting
		pass
	finally:
		setStatus(reader, OFF)
		reader.doit(PowerDown(...))
