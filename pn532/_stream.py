import serial

from . import Frame, ACK, NACK, Error

class ChecksumError(IOError):
	pass

class TimeoutError(IOError):
	pass

class PN532(object):
	def __init__(self, port):
		self.port = port
		#TODO: Default baud
		self.serial = serial.serial_for_url(self.port)

	@staticmethod
	def _verifychecksum(*args):
		s = 0
		for thing in args:
			if isinstance(thing, bytes):
				s += sum(map(ord, thing))
			else:
				s += thing
		if s != 0:
			raise ChecksumError()

	def send(self, frame):
		"""p.send(Frame)
		Sends the given frame to the connected PN532.
		"""
		self.serial.write(frame.towire())

	def raw_get(self, timeout=None):
		"""p.raw_get() -> Frame
		Reads a frame from the port. Doesn't handle parsing errors (sending
		NACKs).

		FIXME: Timeouts
		"""
		header = ""
		while "\x00\xFF" not in header:
			header += self.serial.read(1)
		# We have the start of a frame, get to work.
		start = header.index("\x00\xFF")
		header = header[start:]
		while len(header) <= 4:
			header += self.serial.read(1)
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
				header += self.serial.read(1)
			LENM, LENL = header[4:6]
			LEN = LENM * 0xFF + LENL
			LCS = header[6]
			self._verifychecksum(LENM, LENL, LCS)
		else:
			# Normal Frame
			self._verifychecksum(LEN, LCS)
		data = self.serial.read(LEN)
		DCS = self.serial.read(1)
		self._verifychecksum(data, DCS)
		TFI = data[0]
		if TFI in "\xD4\xD5":
			ccode = data[1]
			payload = data[2:]
			return Frame.get_class(ccode).fromwire(payload)
		else:
			# Error Frame
			raise Error(TFI)

	def get(self, timeout=None):
		"""p.get() -> Frame
		Reads a frame from the port. DOES handle parsing errors (sending
		NACKs).
		"""
		while True:
			try:
				return self.raw_get(timeout)
			except ChecksumError:
				self.send(NACK())

	def doit(self, frame):
		self.send(frame)
		ack = self.get() #TODO: 15ms timeout
		if isinstance(ack, ACK):
			pass # Continue
		elif isinstance(ack, NACK):
			pass # TODO: Resend

		return self.get()
