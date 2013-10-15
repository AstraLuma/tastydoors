"""
Handles the wire-level protocol of talking to a PN532 over UART
"""
from __future__ import absolute_import, division
import abc

class Frame(object):
	"""
	Abstract class for PN532 data frames, both sent and received.
	"""
	__metaclass__ = abc.ABCMeta

	__sent__ = None
	__code__ = None
	__struct__ = None
	__fields__ = None

	@classmethod
	def fromwire(cls, data):
		pass

	def _buildpayload(self):
		"""
		Builds payload, including TFI, command code, and data.
		"""
		if self.__sent__ is None:
			self.__sent__ = not (self.__code__ & 1)
		if self.__sent__:
			payload = "\xD5"
		else:
			payload = "\xD4"

		if self.__struct__[0] in '@=><!':
			o = self.__struct__[0]
			fmt = self.__struct__[1:]
		else:
			o = '>'
			fmt = self.__struct__
		return payload + struct.pack(o + b + fmt, self.__code__, *[getattr(self, field) for field in self.__fields__])

	@staticmethod
	def _checksum(data):
		"""
		Computes checksum, such that:
		[data1 + data2 + ... + dataN + checksum] & 0xFF == 0
		"""
		if isinstance(data, str):
			data = map(ord, data)
		s = sum(data)
		return -s & 0xFF

	def towire(self):
		"""f.towire() -> blob
		Returns the frame as it is to be transmitted over the wire, excluding pre/postable.
		"""
		payload = self._bundlefields()
		dcs = self._checksum(payload)
		len_ = len(payload)

		msg = "\x00\xFF"
		if len_ <= 0xFF:
			lcs = self._checksum(len_)
			msg += struct.pack(">bb", len_, lcs)
			msg += payload
			msg += struct.pack(">b", dcs)
		else:
			lm = struct.pack(">I", len_)
			lcs = self._checksum(lm)
			msg += "\xFF\xFF" + lm
			msg += struct.pack(">b", lcs)
			msg += payload
			msg += struct.pack(">b", dcs)

		return msg

class ACK(Frame):
	"""
	An ACK frame.
	"""
	def towire(self):
		return "\0\xFF\0\xFF"

class NACK(Frame):
	"""
	A NACK frame.
	"""
	def towire(self):
		return "\0\xFF\xFF\0"

class Error(Exception, Frame):
	"""
	An application error.
	"""
	def __init__(self, code):
		self.raw_code = code
		super(Error, self).__init__(code)

	@property
	def NADPresent(self):
		return bool(self.raw_code & 0x80)

	@property
	def MI(self):
		return bool(self.raw_code & 0x40)

	@property
	def error_code(self):
		return self.raw_code & 0x3F

	def _buildpayload(self):
		return chr(self.raw_code & 0xFF)

	@property
	def code_name(self):
		#TODO

	TIMEOUT = 0x01
	CRC = 0x02
	PARITY = 0x03
	SELECT_BIT_COUNT = 0x04
	MIFARE_FRAMING = 0x05
	BIT_COLLISION = 0x06
	BUFFER_TOO_SMALL = 0x07
	RF_BUFFER_OVERFLOW = 0x09
	RF_SWITCH_ON_TIMEOUT = 0x0A
	RF_PROTOCOL = 0x0B
	TOO_HOT = 0x0D
	BUFFER_OVERFLOW = 0x0E
	INVALID_PARAMETER = 0x10
	DEP_COMMAND_UNKNOWN= 0x12
	DEP_BAD_FORMAT = 0x13
	MIFARE_AUTH = 0x14
	UID_CHECK_BYTE = 0x23
	DEP_INVALID_STATE = 0x25
	OPERATION_NOT_ALLOWED = 0x26
	WRONG_CONTEXT = 0x27
	BEEN_RELEASED = 0x29
	CARD_ID_MISMATCH = 0x2A
	CARD_GONE = 0x2B
	NFCID_INIT_PASS_MISMATCH = 0x2C
	OVER_CURRENT = 0x2D
	NAD_MISSING = 0x2E

class Diagnose(Frame):
	__code__ = 0x00
	#TODO

class DiagnoseResponse(Frame):
	__code__ = Diagnose.__code__ + 1
	#TODO

class FirmwareVersion(Frame):
	__code__ = 0x02
	#TODO

class FirmwareVersionResponse(Frame):
	__code__ = FirmwareVersion.__code__ + 1
	#TODO

class GeneralStatus(Frame):
	__code__ = 0x04
	#TODO

class GeneralStatusResponse(Frame):
	__code__ = GeneralStatus.__code__ + 1
	#TODO

class ReadRegister(Frame):
	__code__ = 0x06
	#TODO

class ReadRegisterResponse(Frame):
	__code__ = ReadRegister.__code__ + 1
	#TODO

class WriteRegister(Frame):
	__code__ = 0x08
	#TODO

class WriteRegisterResponse(Frame):
	__code__ = WriteRegister.__code__ + 1
	#TODO

class ReadGPIO(Frame):
	__code__ = 0x0C
	#TODO

class ReadGPIOResponse(Frame):
	__code__ = ReadGPIO.__code__ + 1
	#TODO

class WriteGPIO(Frame):
	__code__ = 0x0E
	#TODO

class WriteGPIOResponse(Frame):
	__code__ = WriteGPIO.__code__ + 1
	#TODO

class SetSerialBaudRate(Frame):
	__code__ = 0x10
	#TODO

class SetSerialBaudRateResponse(Frame):
	__code__ = SetSerialBaudRate.__code__ + 1
	#TODO

class SetParameters(Frame):
	__code__ = 0x12
	#TODO

class SetParametersResponse(Frame):
	__code__ = SetParameters.__code__ + 1
	#TODO

class SAMConfiguration(Frame):
	__code__ = 0x14
	#TODO

class SAMConfigurationResponse(Frame):
	__code__ = SAMConfiguration.__code__ + 1
	#TODO

class PowerDown(Frame):
	__code__ = 0x16
	#TODO

class PowerDownResponse(Frame):
	__code__ = PowerDown.__code__ + 1
	#TODO

