import serial

from . import Frame, ACK, NACK, Error

class PN532(object):
	def __init__(self, port):
		self.port = port
		#TODO: Default baud
		self.serial = serial.serial_for_url(self.port)

	def send(self, frame):
		"""p.send(Frame)
		Sends the given frame to the connected PN532.
		"""
		self.serial.write(frame.towire())

	def raw_get(self):
		"""p.raw_get() -> Frame
		Reads a frame from the port. Doesn't handle parsing errors (sending
		NACKs).

		FIXME: Timeouts
		"""
		header = ""
		while "\x00\xFF" not in header:
			header += self.serial.read()
		# We have the start of a frame, get to work.
		start = header.index("\x00\xFF")
		header = header[start:]
		while len(header) <= 4:
			header += self.serial.read()
		# Now we have enough to begin parsing it out
		LEN = header[2]
		LCS = header[3]
		if LEN == 0 and LCS == 0xFF:
			return ACK()
		elif LEN == 0xFF and LCS = 0:
			return NACK()
		elif LEN == 0xFF and LCS = 0xFF:
			# Extended length
			while len(header) <= 7:
				header += self.serial.read()
			LENM, LENL = header[4:6]
			LEN = LENM * 0xFF + LENL
			LCS = header[6]
			#FIXME: Verify length
		else:
			# Normal Frame
			#FIXME: Verify length
		data = self.serial.read(LEN)
		TFI = data[0]
		if TFI in "\xD4\xD5":
			ccode = data[1]
			payload = data[2:]
			return Frame.get_class(ccode).fromwire(payload)
		else:
			# Error Frame
			raise Error(TFI)

	def get(self):
		"""p.get() -> Frame
		Reads a frame from the port. DOES handle parsing errors (sending
		NACKs).

		FIXME: Timeouts
		"""
		#FIXME: handle parsing errors?
		return self.get()

	def doit(self, frame):
		self.send(frame)
		ack = self.get() #TODO: 15ms timeout
		if isinstance(ack, ACK):
			pass # Continue
		elif isinstance(ack, NACK):
			pass # TODO: Resend

		return self.get()
