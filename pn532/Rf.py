from . import Frame

class Configuration(Frame):
	__code__ = 0x32

	def __init__(self, CfgItem, ConfigurationData):
		self.CfgItem = CfgItem
		self.ConfigurationData = ConfigurationData

	def __payload__(self):
		if self.InParam is None:
			return self.CfgItem,
		elif isinstance(self.InParam, collections.Iterable):
			return (self.CfgItem,) + tuple(self.InParam)
		else:
			return self.CfgItem, self.InParam

class ConfigurationResponse(Frame):
	__code__ = Configuration.__code__ + 1

	def __payload__(self):
		pass

class RegulationTest(Frame):
	__code__ = 0x58
	#TODO

# RfRegulationTest never ends, so has no response
