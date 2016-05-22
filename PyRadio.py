import sys
import os
import subprocess
import time
import threading

# Check for requirements ###
try:
	import PySide
	import pafy
	import bs4
except:
	if 'nt' in os.name:
		update_command = "C:\\Python27\\Scripts\\pip install -r requirements.txt"
	else:
		update_command = "pip install -r requirements.txt"
	os.system(update_command)
#############################

from PySide.QtGui import *
from PySide.QtCore import *

from MainScene import MainWindow
from DBScene import ViewScene
from OptionScene import OptionScene
from Backend import Backend
from Widgets import *

WIDTH = 640
HEIGHT = 540

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

		# Get application
		global app
		self.app = app

		# Handle Close event
		self.connect(self, SIGNAL('triggered()'), self.closeEvent)

	def closeEvent(self, event):
		# save all data
		self.backend.info.commit()
		self.backend.stop()

		# delete resources

		del self.mainwin
		del self.viewscene
		del self.backend
		del self.optscene

		self.destroy()
		self.app.quit()

	def _getSettings(self):
		self.backend = Backend(self)

		# Load Styling
		CSS = self.backend.info.data['Player']['style']
		with open( os.path.join('resources','css',CSS + '.css'), 'r') as f:
			self.setStyleSheet( f.read() )

		# Get version
		with open("VERSION.txt",'r') as f:
			self.version = f.read()

	def _createWindows(self):
		# Create Windows
		self.mainwin = MainWindow(self)
		self.viewscene = ViewScene(self)
		self.optscene = OptionScene(self)

		# For organization
		self.views = [self.mainwin, self.viewscene, self.optscene]

		self.createNavigationBar()

		# Display home screen first
		for frame in self.views:
			if frame == self.mainwin:
				frame.show()
			else:
				frame.hide()

			# allow windows to communicate with backend
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
		# Window Switcher
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
		# Cross-platform URL Opener
		link = "https://github.com/king1600/PyRadio"
		if 'nt' in os.name:
			cmd = "start " + link
		else:
			cmd = "xdg-open " + link
		subprocess.call(cmd,shell=True)

	def updateStatus(self, message):
		# Custom QStatus
		msg = str(message)
		self.status_bar.setText(msg)

	def initStart(self):
		# start a daemon Thread
		t = threading.Thread(target=self._Start)
		t.daemon = True
		t.start()

	def _Start(self):
		# Seperate thread to start services

		self.backend.initServices()

		# wait for GStreamer to init
		while not self.backend.done:
			time.sleep(0.1)
		self.viewscene.initFetcher()

		''' Not needed '''
		# Wait for list to be scanned 
		#while not self.viewscene.done:
		#	time.sleep(0.1)
		time.sleep(0.5)

		# start playing music
		self.mainwin.startStream()

		self.status.emit("Ready!")

if __name__ == '__main__':
	app = QApplication(sys.argv)

	win = PyRadio()
	win.show()

	win.status.emit("Initializing GStreamer...")
	win.s_delay.start()

	sys.exit(app.exec_())
