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

	__id__ = None
	__struct__ = None
	__fields__ = None

	@classmethod
	def fromwire(cls, data):
		pass

	def _bundlefields(self):
		if self.__struct__ not in '@=><!':
			self.__struct__ = '>' + self.__struct__
		return struct.pack(self.__struct__, *[getattr(self, field) for field in self.__fields__])

	@staticmethod
	def _checksum(data):
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
		len_ = len(payload) + 1
		tfi = self.__id__

		msg = "\x00\xFF"
		if len_ <= 0xFF:
			lcs = self._checksum(len_)
			msg += struct.pack(">bbb", len_, lcs, tfi)
			msg += payload
			msg += struct.pack(">b", dcs)
		else:
			lm = struct.pack(">I", len_)
			lcs = self._checksum(lm)
			msg += "\xFF\xFF" + lm
			msg += struct.pack(">bb", lcs, tfi)
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

class Error(Frame):
	"""
	An application error.
	"""
	def towire(self):
		return "\0\xFF\x01\xFF\x7F\x81"
