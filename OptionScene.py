from PySide.QtGui import *
from PySide.QtCore import *

class OptionScene(QFrame):
	def __init__(self, win):
		super(OptionScene, self).__init__(win)
		self.win = win
		self.initUI()

	def initUI(self):
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self.layout.addWidget(QLabel("Options"))

	def setBackend(self, bg):
		self.backend = bg