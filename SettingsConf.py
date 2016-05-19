from ConfigParser import ConfigParser


INI_FILE = "SETTINGS.ini"


class SettingsConf(object):

	def __init__(self):
		self.config = ConfigParser()
		self.data = {}

		self.readData()

	def readData(self):
		self.config.read( INI_FILE )
		for x in self.config._sections:
			self.data[x] = self.config._sections[str(x)]

	def writeData(self):
		with open( INI_FILE, 'w') as conf:
			self.config.write(conf)

	def changeValue(self, section, key, value):
		self.config.set(str(section), str(key), value)

	def commit(self):
		self.writeData()
		self.readData()
