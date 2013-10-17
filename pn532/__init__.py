"""
Handles the wire-level protocol of talking to a PN532 over UART
"""
from __future__ import absolute_import, division
import abc
import numbers
import collections

def bytepack(*nums):
	"""bytepack(num, ...) -> bytes
	Take a series of byte values and convert them to a binary buffer.
	"""
	return ''.join(map(chr, nums))

def tobytes(n, l):
	"""tobytes(int, int) -> bytes
	Breaks a number into a series of bytes, big-endian. Limit to given length.
	"""
	rv = []
	for i in range(l):
		rv.append(n & 0xFF)
		n >>= 8
	return bytepack(rv)

class Frame(object):
	"""
	Abstract class for PN532 data frames, both sent and received.
	"""
	class __metaclass__(abc.ABCMeta):
		def __init__(cls, *p, **kw):
			abc.ABCMeta.__init__(cls, *p, **kw) # Can't use new style because can't get references
			if cls.__code__ is not None:
				if cls.__sent__ is None:
					cls.__sent__ = not (cls.__code__ & 1)
				Frame._types[cls.__code__] = cls

	_types = {}
	__sent__ = None
	__code__ = None

	@staticmethod
	def get_class(code):
		return Frame._types[code]

	@classmethod
	def fromwire(cls, data):
		payload = map(ord, data)
		return cls.__build__(payload)

	@classmethod
	def __build__(cls, payload):
		"""<Frame>.__build__(list(int)) -> <Frame>
		Construct the Frame object from a payload
		"""
		raise NotImplementedError

	def __payload__(self):
		"""f.__payload__() -> [...]
		Returns a sequence of fields to pack into the payload, not including
		TFI or command code.
		"""
		raise NotImplementedError

	def _buildpayload(self):
		"""
		Builds payload, including TFI, command code, and data.
		"""
		if self.__sent__:
			payload = "\xD5"
		else:
			payload = "\xD4"

		payload += tobytes(self.__code__)

		fields = self.__payload__()
		if fields is not None:
			for field in fields:
				if isinstance(field, numbers.Number):
					payload += tobytes(field)
				elif isinstance(field, bytes):
					payload += field
				elif isinstance(field, tuple):
					payload += tobytes(*field)
		return payload

	@staticmethod
	def _checksum(data):
		"""
		Computes checksum, such that:
		[data1 + data2 + ... + dataN + checksum] & 0xFF == 0
		"""
		if isinstance(data, bytes):
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
			msg += bytepack(len_, lcs)
			msg += payload
			msg += bytepack(dcs)
		else:
			lm = tobytes(len_, 2)
			lcs = self._checksum(lm)
			msg += "\xFF\xFF" + lm
			msg += bytepack(lcs)
			msg += payload
			msg += bytepack(dcs)

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

	def _buildpayload(self):
		return tobytes(self.raw_code)

	@property
	def NADPresent(self):
		return bool(self.raw_code & 0x80)

	@property
	def MI(self):
		return bool(self.raw_code & 0x40)

	@property
	def error_code(self):
		return self.raw_code & 0x3F

	@property
	def code_name(self):
		raise NotImplementedError

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
	def __init__(self, NumTst, InParam=None):
		self.NumTst = NumTst
		self.InParam = InParam

	def __payload__(self):
		if self.InParam is None:
			return self.NumTst,
		elif isinstance(self.InParam, collections.Iterable):
			return (self.NumTst,) + tuple(self.InParam)
		else:
			return self.NumTst, self.InParam

class DiagnoseResponse(Frame):
	__code__ = Diagnose.__code__ + 1
	#TODO

class FirmwareVersion(Frame):
	__code__ = 0x02
	def __payload__(self):
		pass

class FirmwareVersionResponse(Frame):
	__code__ = FirmwareVersion.__code__ + 1
	def __init__(self, IC, Ver, Rev, Support):
		self.IC = IC
		self.Ver = Ver
		self.Rev = Rev
		self.Support = Support

	@property
	def ISO18092(self):
		return bool(self.Support & 0x04)

	@property
	def ISOIEC14443TypeA(self):
		return bool(self.Support & 0x02)

	@property
	def ISOIEC14443TypeB(self):
		return bool(self.Support & 0x01)

	def __payload__(self):
		return self.IC, self.Ver, self.Rev, self.Support

class GeneralStatus(Frame):
	__code__ = 0x04

	def __payload__(self):
		pass

class GeneralStatusResponse(Frame):
	__code__ = GeneralStatus.__code__ + 1
	#TODO

class SFR:
	"""
	Enum of the SFR Registers
	"""
	def __init__(self):
		raise RuntimeError("SFR is not intantiable")

	PCON = 0xFF87
	RWL = 0xFF9A
	TWL = 0xFF9B
	FIFOFS = 0xFF9C
	FIFOFF = 0xFF9D
	SFF = 0xFF9E
	FIT = 0xFF9F
	FITEN = 0xFFA1
	FDATA = 0xFFA2
	FSIZE = 0xFFA3
	IE0 = 0xFFA8
	SPIcontrol = 0xFFA9
	SPIstatus = 0xFFAA
	HSU_STA = 0xFFAB
	HSU_CTR = 0xFFAC
	HSU_PRE = 0xFFAD
	HSU_CNT = 0xFFAE
	P3 = 0xFFB0
	IP0 = 0xFFB8
	CIU_COMMAND = 0xFFD1
	IEN1 = 0xFFE8
	P7CFGA = 0xFFF4
	P7CFGB = 0xFFF5
	P7 = 0xFFF7
	IP1 = 0xFFF8
	P3CFGA = 0xFFFC
	P3CFGB = 0xFFFD

class ReadRegister(Frame):
	__code__ = 0x06

	def __init__(self, *addrs):
		self.addrs = addrs

	def __payload__(self):
		return [(addr, 2) for addr in self.addrs]

class ReadRegisterResponse(Frame):
	__code__ = ReadRegister.__code__ + 1

	def __init__(self, *values):
		self.values = values

	def __payload__(self):
		return self.values

class WriteRegister(Frame):
	__code__ = 0x08
	def __init__(self, ops):
		self.ops = dict(ops)

	def __payload__(self):
		rv = []
		for addr, value in self.ops.items():
			rv += [(addr, 2), value]
		return rv

class WriteRegisterResponse(Frame):
	__code__ = WriteRegister.__code__ + 1
	def __payload__(self):
		pass

class ReadGPIO(Frame):
	__code__ = 0x0C
	def __payload__(self):
		pass

class ReadGPIOResponse(Frame):
	__code__ = ReadGPIO.__code__ + 1

	def __init__(self, P3, P7, I0I1):
		self.P3 = P3
		self.P7 = P7
		self.I0I1 = I0I1

	def __payload__(self):
		return self.P3, self.P7, selfI0I1

class WriteGPIO(Frame):
	__code__ = 0x0E

	def __init__(self, P3=None, P7=None):
		self.P3 = P3
		self.P7 = P7

	def __payload__(self):
		return self.P3 or 0, self.P7 or 0

class WriteGPIOResponse(Frame):
	__code__ = WriteGPIO.__code__ + 1
	def __payload__(self):
		pass

class SetSerialBaudRate(Frame):
	__code__ = 0x10
	#TODO

class SetSerialBaudRateResponse(Frame):
	__code__ = SetSerialBaudRate.__code__ + 1
	#TODO

class SetParameters(Frame):
	__code__ = 0x12
	def __init__(self, Flags):
		self.Flags = Flags

	def __payload__(self):
		return self.Flags,

class SetParametersResponse(Frame):
	__code__ = SetParameters.__code__ + 1

	def __payload__(self):
		pass

class SAMConfiguration(Frame):
	__code__ = 0x14
	#TODO

class SAMConfigurationResponse(Frame):
	__code__ = SAMConfiguration.__code__ + 1
	#TODO

class PowerDown(Frame):
	__code__ = 0x16

	def __init__(self, WakeUpEnable, GenerateIRQ=None):
		self.WakeUpEnable = WakeUpEnable
		self.GenerateIRQ = GenerateIRQ

	def __payload__(self):
		if self.GenerateIRQ is None:
			return self.WakeUpEnable,
		else:
			return self.WakeUpEnable, self.GenerateIRQ

class PowerDownResponse(Frame):
	__code__ = PowerDown.__code__ + 1

	def __init__(self, Status):
		self.Status = Status

	def __payload__(self):
		return self.Status,

# Submodules

import Rf, In, Tg
from _stream import PN532
