from PySide.QtGui import *
from PySide.QtCore import *

from Widgets import *

import threading
import urllib2
import time

IMG_WIDTH = 480
IMG_HEIGHT = 360

class MainWindow(QFrame):
	newPicture = Signal(str)

	def __init__(self, win):
		super(MainWindow, self).__init__(win)
		self.win = win
		self.initUI()

	def initUI(self):
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self.createWidgets()

		self.songs = []
		self.queue_songs = []
		self.currentVolume = 50
		self.isLoading = False
		self.isPlaying = False

	def setBackend(self, bg):
		self.backend = bg

		self.newPicture.connect(self.setImage)

	def setImage(self, imglink):
		imglink = str(imglink)
		data = urllib2.urlopen( imglink ).read()
		image = QImage()
		image.loadFromData(data)
		pixmap = QPixmap(image).scaled(
			IMG_WIDTH, IMG_HEIGHT)
		self.song_image.setPixmap( pixmap )

	def startThread(self, func, *args):
		t = threading.Thread(target=func,args=args)
		t.daemon = True
		t.start()

	# Create Widgets	

	def createWidgets(self):
		first_layer = QHBoxLayout()
		top_layer = QHBoxLayout()

		# First Layer

		self.search_bar = SearchBar()
		self.search_btn = SearchButton("Search")

		first_layer.addWidget(self.search_bar)
		first_layer.addWidget(self.search_btn)

		# Top layer

		self.start_btn = ImageButton()
		self.back_btn = ImageButton()
		self.skip_btn = ImageButton()

		self.start_btn.setImage("resources/pictures/pause.png",[48,48])
		self.back_btn.setImage("resources/pictures/rewind.png",[48,48])
		self.skip_btn.setImage("resources/pictures/forward.png",[48,48])

		self.start_btn.clicked.connect(self.changeState)
		self.back_btn.clicked.connect(self.rewind)
		self.skip_btn.clicked.connect(self.forward)

		top_layer.addWidget(self.back_btn)
		top_layer.addWidget(self.start_btn)
		top_layer.addWidget(self.skip_btn)

		self.volume = VolumeSlider()
		self.currentVolume = 50
		self.volume.setValue(50)
		self.volume.valueChanged.connect(self.changeVolume)
		self.volume_btn = ImageButton()
		self.volume_btn.setImage("resources/pictures/vol_on.png",[24,24])

		top_layer.addStretch(1)
		top_layer.addWidget(self.volume_btn)
		top_layer.addWidget(self.volume)

		# the Rest

		self.title = SongTitle("Hello")
		self.song_image = ImageButton()
		self.song_image.setAlignment(Qt.AlignCenter)

		# add to layout

		self.layout.addLayout(first_layer)
		self.layout.addLayout(top_layer)
		self.layout.addWidget(self.title)
		self.layout.addWidget(self.song_image)

	# Stream actions

	def newStream(self):
		if self.songs != []:
			if self.backend.place < len(self.songs):
				info = self.songs[self.backend.place]
				self.backend.place += 1
				self.setupStream(info)
				return True

		if self.queue_songs != []:
			info = self.queue_songs[-1]
			self.songs.append(info)

			self.queue_songs.pop(-1)
			self.backend.place += 1
			self.setupStream(info)
			return True

		else:
			url = self.backend.getNextSong()
			info = self.backend.yi.getInfo(url)
			self.backend.place += 1
			self.songs.append(info)
			self.setupStream(info)


	def setupStream(self, info):
		self.isLoading = True

		self.title._setText( info[0] )
		self.newPicture.emit( info[1] )
		self.backend.stream( info[-1] )

		self.backend.play()
		self.backend.pipeline.connect('about-to-finish',
			self.startStream)

		surpressor = int(self.backend.info.data['Player']['vol_supp_ratio'])
		time.sleep(0.5)
		self.backend.setVolume( self.currentVolume / surpressor / 100.0 )

		self.isPlaying = True
		self.isLoading = False

	def startStream(self, *args):
		self.title._setText("Loading...")
		self.startThread(self.newStream)

	def rewind(self):
		if self.isLoading: return False

		if self.backend.place != -1:
			if self.backend.place == 1:
				self.backend.place = 0
			else:
				self.backend.place -= 2

		self.startStream()

	def forward(self):
		if self.isLoading: return False

		self.startStream()

	# update functions

	def changeVolume(self, val):
		surpressor = int(self.backend.info.data['Player']['vol_supp_ratio'])
		self.currentVolume = val
		self.backend.info.changeValue('Player','volume',self.currentVolume)
		self.backend.setVolume( val / surpressor / 100.0 )

	def changeState(self):
		if self.isPlaying:
			try:
				self.backend.pause()
				self.start_btn.setImage("resources/pictures/play.png",[48,48])
				self.isPlaying = False
			except Exception as e:
				print str(e)
		else:
			try:
				self.backend.play()
				self.start_btn.setImage("resources/pictures/pause.png",[48,48])
				self.isPlaying = True
			except:
				pass