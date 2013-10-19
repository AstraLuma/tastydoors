from . import Frame, fields
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

	def __payload__(self):
		if self.InitiatorData is None:
			return self.MaxTg, self.BrTy
		else:
			return self.MaxTg, self.BrTy, self.InitiatorData

@fields('targets')
class ListPassiveTargetResponse(Frame):
	__code__ = ListPassiveTarget.__code__ + 1

	@classmethod
	def __build__(cls, payload):
		NbTg = payload[0]
		# FIXME: Can this be parsed context-free? Or do we need the request packet?

@fields('Tg', 'NFCID3', 'Gi')
class ATR(Frame):
	__code__ = 0x50
	def __payload__(self):
		pl = self.Tg,
		Next = 0
		if self.NFCID3 is not None:
			Next |= 0x01
		if self.Gi is not None:
			Next |= 0x02
		pl += Next,
		if self.NFCID3 is not None:
			pl += self.NFCID3
		if self.Gi is not None:
			pl += self.Gi
		return pl

@fields('Status', 'NFCID3', 'DIDt', 'BSt', 'BRt', 'TO', 'PPt', 'Gt')
class ATRResponse(Frame):
	__code__ = ATR.__code__ + 1

	@classmethod
	def __build__(cls, payload):
		Status = payload[0]
		NFCID3 = payload[1:10]
		DIDt, BSt, BRt, TO, PPt = payload[10:15]
		if len(payload) > 15:
			Gt = payload[15:]
		else:
			Gt = None
		return cls(Status, NFCID3, DIDt, BSt, BRt, TO, PPt, Gt)

@fields('Tg', 'BRit', 'BRti')
class PSL(Frame):
	__code__ = 0x4E

	def __payload__(self):
		return self.Tg, self.BRit, self.BRti

@fields('Status')
class PSLResponse(Frame):
	__code__ = PSL.__code__ + 1

@fields('Tg', 'DataOut')
class DataExchange(Frame):
	__code__ = 0x40
	def __payload__(self):
		if getattr(self, 'DataOut'):
			return (self.Tg,)+tuple(self.DataOut)
		else:
			return self.Tg

@fields('Status', 'DataIn')
class DataExchangeResponse(Frame):
	__code__ = DataExchange.__code__ + 1

	@classmethod
	def __build__(cls, payload):
		if len(payload) == 1:
			return cls(payload[0], None)
		else:
			return cls(payload[0], payload[1:])

@fields('DataOut')
class CommunicateThru(Frame):
	__code__ = 0x42
	def __payload__(self):
		if getattr(self, 'DataOut'):
			return self.DataOut

@fields('Status', 'DataIn')
class CommunicateThruResponse(Frame):
	__code__ = CommunicateThru.__code__ + 1
	@classmethod
	def __build__(cls, payload):
		if len(payload) == 1:
			return cls(payload[0], None)
		else:
			return cls(payload[0], payload[1:])

@fields('Tg')
class Deselect(Frame):
	__code__ = 0x44
	def __payload__(self):
		return self.Tg

@fields('Status')
class DeselectResponse(Frame):
	__code__ = Deselect.__code__

@fields('Tg')
class Release(Frame):
	__code__ = 0x52
	def __payload__(self):
		return self.Tg

@fields('Status')
class ReleaseResponse(Frame):
	__code__ = Release.__code__

@fields('Tg')
class Select(Frame):
	__code__ = 0x54
	def __payload__(self):
		return self.Tg

@fields('Status')
class SelectResponse(Frame):
	__code__ = Select.__code__

@fields('PollNr', 'Period', 'Types')
class AutoPoll(Frame):
	__code__ = 0x60
	def __payload__(self):
		return (self.PollNr, self.Period) + tuple(self.Types)

@fields('Targets')
class AutoPollResponse(Frame):
	__code__ = AutoPoll.__code__ + 1

	Target = namedtuple('Target', ['Type', 'AutoPollTargetData'])
	@classmethod
	def __build__(cls, payload):
		NbTg = payload[0]
		Target1 = cls.Target(payload[1], payload[3:3+payload[2]])
		if NbTg == 1:
			return cls([Target1])
		else: # NbTg == 2
			t2 = payload[3+payload[2]:]
			Target2 = cls.Target(t2[0], t2[2:2+t2[1]])
			return cls([Target1, Target2])
