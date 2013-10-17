from . import Frame

class JumpForDEP(Frame):
	__code__ = 0x56

	def __init__(self, ActPass, BR, PassiveInitiatorData=None, NFCID3=None, Gi=None):
		self.ActPass = ActiPass
		self.BR = BR
		self.PassiveInitiatorData = PassiveInitiatorData
		self.NFCID3 = NFCID3
		self.Gi = Gi

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

class JumpForDEPResponse(Frame):
	__code__ = InJumpForDEP.__code__ + 1

	def __init__(self, Status, Tg, NFCID3, DIDt, BSt, BRt, TO, PPt, Gt=None):
		self.Status = Status
		self.Tg = Tg
		self.NFCID3 = NFCID3
		self.DIDt = DIDt
		self.BSt = BSt
		self.BRt = BRt
		self.TO = TO
		self.PPt = PPt
		self.Gt = Gt

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
