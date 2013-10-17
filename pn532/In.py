from . import Frame
from collections import namedtuple

@fields('ActPass', 'BR', 'PassiveInitiatorData', 'NFCID3', 'Gi')
class JumpForDEP(Frame):
	__code__ = 0x56

	def __payload__(self):
		Next = 0
		if self.PassiveInitiatorData is not None:
			Next |= 0x01
		if self.NFCID3 is not None:
			Next |= 0x02
		if self.Gi is not None:
			Next |= 0x04

		rv = self.ActPass, self.BR, Next
		if self.PassiveInitiatorData is not None:
			rv += self.PassiveInitiatorData
		if self.NFCID3 is not None:
			rv += self.NFCID3,
		if self.Gi is not None:
			rv += self.Gi,
		return rv

@fields('Status', 'Tg', 'NFCID3', 'DIDt', 'BSt', 'BRt', 'TO', 'PPt', 'Gt')
class JumpForDEPResponse(Frame):
	__code__ = JumpForDEP.__code__ + 1

	@classmethod
	def __build__(cls, payload):
		Status, Tg = payload[:2]
		NFCID3 = payload[2:11]
		DIDt, BSt, BRt, TO, PPt = payload[11:16]
		if len(payload) > 16:
			Gt = payload[16:]
		else:
			Gt = None
		return cls(Status, Tg, NFCID3, DIDt, BSt, BRt, TO, PPt, Gt)

@fields('ActPass', 'BR', 'PassiveInitiatorData', 'NFCID3', 'Gi')
class JumpForPSL(Frame):
	__code__ = 0x46

	def __payload__(self):
		Next = 0
		if self.PassiveInitiatorData is not None:
			Next |= 0x01
		if self.NFCID3 is not None:
			Next |= 0x02
		if self.Gi is not None:
			Next |= 0x04

		rv = self.ActPass, self.BR, Next
		if self.PassiveInitiatorData is not None:
			rv += self.PassiveInitiatorData
		if self.NFCID3 is not None:
			rv += self.NFCID3,
		if self.Gi is not None:
			rv += self.Gi,
		return rv

@fields('Status', 'Tg', 'NFCID3', 'DIDt', 'BSt', 'BRt', 'TO', 'PPt', 'Gt')
class JumpForPSLResponse(Frame):
	__code__ = JumpForPSL.__code__ + 1

	@classmethod
	def __build__(cls, payload):
		Status, Tg = payload[:2]
		NFCID3 = payload[2:11]
		DIDt, BSt, BRt, TO, PPt = payload[11:16]
		if len(payload) > 16:
			Gt = payload[16:]
		else:
			Gt = None
		return cls(Status, Tg, NFCID3, DIDt, BSt, BRt, TO, PPt, Gt)

@fields('MaxTg', 'BrTy', 'InitiatorData')
class ListPassiveTarget(Frame):
	__code__ = 0x4A

	def __init__(self, MaxTg, BrTy, InitiatorData=None):
		self.MaxTg = MaxTg
		self.BrTy = BrTy
