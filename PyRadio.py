from PySide.QtGui import *
from PySide.QtCore import *

from MainScene import MainWindow
from DBScene import ViewScene
from OptionScene import OptionScene
from Backend import Backend
from Widgets import *

import sys
import os
import subprocess
import time
import threading

WIDTH = 640
HEIGHT = 500

#Globalize/Declare application
app = None

class StartDelay(QThread):
	def __init__(self):
		super(StartDelay, self).__init__()

	def run(self):
		time.sleep(0.2)
		self.emit( SIGNAL("start_app()") )

class PyRadio(QWidget):
	status = Signal(str)

	def __init__(self):
		super(PyRadio, self).__init__()
		self.initUI()

		# ~ Initialize services without making GUI hang
		self.s_delay = StartDelay()
		self.connect(self.s_delay, SIGNAL("start_app()"), self.initStart)

	def _createBottom(self):
		self.layout.addStretch(1)
		bottom_layout = QHBoxLayout()

		# Set Status Label
		self.status_bar = StatusLabel()
		self.status.connect(self.updateStatus)
		bottom_layout.addWidget(self.status_bar)

		# Set Version Label
		bottom_layout.addStretch(1)
		bottom_layout.addWidget(VersionLabel("version: "+self.version))

		self.layout.addLayout(bottom_layout)

	def initUI(self):
		self.resize( WIDTH, HEIGHT )
		self.setMaximumWidth( WIDTH )
		self.setMaximumHeight( HEIGHT )
		self.setMinimumWidth( WIDTH )
		self.setMinimumHeight( HEIGHT )
		self.setWindowTitle("PyRadio")

		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self._getSettings()
		self._createWindows()
		self._createBottom()

		self.connect(self, SIGNAL('triggered()'), self.closeEvent)

	def closeEvent(self, event):
		global app
		
		#save all data
		self.backend.info.commit()
		self.backend.stop()

		self.destroy()
		app.quit()

	def _getSettings(self):
		self.backend = Backend(self)

		CSS = self.backend.info.data['Player']['style']
		with open( os.path.join('resources','css',CSS + '.css'), 'r') as f:
			self.setStyleSheet( f.read() )

		with open("VERSION.txt",'r') as f:
			self.version = f.read()

	def _createWindows(self):
		self.mainwin = MainWindow(self)
		self.viewscene = ViewScene(self)
		self.optscene = OptionScene(self)

		self.views = [self.mainwin, self.viewscene, self.optscene]

		self.createNavigationBar()

		for frame in self.views:
			if frame == self.mainwin:
				frame.show()
			else:
				frame.hide()

			frame.setBackend(self.backend)
			self.layout.addWidget(frame)

	def createNavigationBar(self):
		self.nav_bar = NavigationBar()

		self.home_icon = ImageButton()
		self.list_icon = ImageButton()
		self.conf_icon = ImageButton()
		self.git_icon = ImageButton()

		self.home_icon.setImage('resources/pictures/home.png',[44,44],False)
		self.list_icon.setImage('resources/pictures/listing.png',[36,36])
		self.conf_icon.setImage('resources/pictures/settings.png',[36,36])
		self.git_icon.setImage('resources/pictures/github.png',[36,36])

		self.home_icon.setReturnString('home')
		self.list_icon.setReturnString('list')
		self.conf_icon.setReturnString('conf')

		self.home_icon.clicked.connect(self.changeWindow)
		self.list_icon.clicked.connect(self.changeWindow)
		self.conf_icon.clicked.connect(self.changeWindow)
		self.git_icon.clicked.connect(self.visit_github)

		self.nav_bar.addWidget(self.home_icon)
		self.nav_bar.addWidget(self.list_icon)
		self.nav_bar.addWidget(self.conf_icon)
		self.nav_bar.addStretch(1)
		self.nav_bar.addWidget(self.git_icon)

		self.layout.addLayout(self.nav_bar)


	### Actions ###

	def changeWindow(self, win=None):
		if win == "home":
			self.mainwin.show()
			self.viewscene.hide()
			self.optscene.hide()

		elif win == "list":
			self.mainwin.hide()
			self.viewscene.show()
			self.optscene.hide()

		else:
			self.mainwin.hide()
			self.viewscene.hide()
			self.optscene.show()

	def visit_github(self, *args):
		link = "https://github.com/king1600/PyRadio"
		if 'nt' in os.name:
			cmd = "start " + link
		else:
			cmd = "xdg-open " + link
		subprocess.call(cmd,shell=True)

	def updateStatus(self, message):
		msg = str(message)
		self.status_bar.setText(msg)

	def initStart(self):
		t = threading.Thread(target=self._Start)
		t.daemon = True
		t.start()

	def _Start(self):
		self.backend.initServices()
		while not self.backend.done:
			time.sleep(0.1)
		self.viewscene.initFetcher()

		while not self.viewscene.done:
			time.sleep(0.1)

		self.mainwin.startStream()
		self.status.emit("Ready!")

if __name__ == '__main__':
	app = QApplication(sys.argv)

	win = PyRadio()
	win.show()

	win.status.emit("Initializing GStreamer...")
	win.s_delay.start()

	sys.exit(app.exec_())
