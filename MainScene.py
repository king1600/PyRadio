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

		# create settings
		self.songs = []
		self.queue_songs = []
		self.currentVolume = 50
		self.isLoading = False
		self.isPlaying = False
		self.isMute = False

	# preload Settings

	def loadSettings(self):
		pass

	# set Functions

	def setBackend(self, bg):
		self.backend = bg

		# get last volume
		self.currentVolume = int(self.backend.info.data['Player']['volume'])
		self.volume.setValue(self.currentVolume)

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
		self.search_bar.returnPressed.connect(self.addToQueue)
		self.search_btn.clicked.connect(self.addToQueue)

		first_layer.addWidget(self.search_bar)
		first_layer.addWidget(self.search_btn)

		# Top layer

		# buttons
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

		# volume
		self.volume = VolumeSlider()
		self.currentVolume = 50
		self.volume.setRange(0,100)
		self.volume.setPageStep(1)
		self.volume.setValue(50)
		self.volume.setMinimumWidth(80)
		self.volume.valueChanged.connect(self.changeVolume)
		self.volume_btn = ImageButton()
		self.volume_btn.setImage("resources/pictures/vol_on.png",[24,24])
		self.volume_btn.clicked.connect(self.changeMute)

		top_layer.addStretch(1)
		top_layer.addWidget(self.volume_btn)
		top_layer.addWidget(self.volume)

		# the Rest

		self.title = SongTitle("Initializing...")
		self.song_image = ImageButton()
		self.song_image.setAlignment(Qt.AlignCenter)

		# add to layout

		self.layout.addLayout(first_layer)
		self.layout.addLayout(top_layer)
		self.layout.addWidget(self.title)
		self.layout.addWidget(self.song_image)

	# Stream actions

	def newStream(self):
		# For rewind
		if self.songs != []:
			if self.backend.place < len(self.songs):
				info = self.songs[self.backend.place]
				self.backend.place += 1
				self.setupStream(info)
				return True

		# For songs in queue
		if self.queue_songs != []:
			info = self.queue_songs[-1]
			self.songs.append(info)

			self.queue_songs.pop(-1)
			self.backend.place += 1
			self.setupStream(info)
			return True

		# For normal operations
		else:
			url = self.backend.getNextSong()
			info = self.backend.yi.getInfo(url)
			self.backend.place += 1
			self.songs.append(info)
			self.setupStream(info)


	def setupStream(self, info):
		if self.isLoading:
			return False

		self.isLoading = True

		print "Playing: " + str(info[0])
		print "YoutubeID: " + str(info[1].split('/')[-2])

		# Set info
		self.title._setText( info[0] )
		if bool(self.backend.info.data['Player']['getimage']):
			self.newPicture.emit( info[1] )
		self.backend.stream( info[-1] )

		# When stream is done, move on
		
		self.backend.pipeline.connect('about-to-finish',
			self.startStream)

		# Get volume suppressor
		surpressor = float(self.backend.info.data['Player']['vol_supp_ratio'])*1.0
		
		# Keep setting stream volume (Bug with GStreamer)
		for i in range(10):
			self.backend.setVolume( self.currentVolume / surpressor / 100.0 )
			time.sleep(0.1)

		self.isPlaying = True
		self.isLoading = False

	def startStream(self, *args):
		self.title._setText("Loading...")
		self.startThread(self.newStream)

	def rewind(self):
		# Dont Spam
		if self.isLoading:
			return False

		# Rewind array
		if self.backend.place != -1:
			if self.backend.place == 1:
				self.backend.place = 0
			else:
				self.backend.place -= 2

		self.startStream()

	def forward(self):
		# Dont spam
		if self.isLoading:
			return False

		self.startStream()

	# update functions

	def changeVolume(self, val):
		# supress volume because its originally loud
		surpressor = float(self.backend.info.data['Player']['vol_supp_ratio'])*1.0

		if not self.isMute:
			self.currentVolume = val
			self.backend.info.changeValue('Player','volume',self.currentVolume)
			self.backend.setVolume( val / surpressor / 100.0 )

	def changeMute(self):
		if self.isMute:
			self.isMute = False
			self.volume_btn.setImage("resources/pictures/vol_on.png",[24,24])

			surpressor = float(self.backend.info.data['Player']['vol_supp_ratio'])*1.0
			self.backend.setVolume( self.currentVolume / surpressor / 100.0 )
		else:
			self.isMute = True
			self.volume_btn.setImage("resources/pictures/vol_off.png",[24,24])
			self.backend.setVolume(0.0)

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

	# Playlist functions

	def addToQueue(self, *args):
		self.startThread(self.QueueInfo)

	def QueueInfo(self):
		text = str(self.search_bar.text())
		self.search_bar.clear()

		# No whitespace / empty search
		if text == '' or text.isspace():
			return False

		# Get info and add to queue
		self.title._setText("Loading search...")
		video_id = self.backend.yi.getSearchResults( text )
		info = self.backend.yi.getInfo( video_id )
		self.queue_songs.append( info )

		# Get all video ids for reference
		all_ids = []
		for x in self.backend.urls:
			# Get only video id
			_id = x
			if 'watch?v' in _id:
				_id = _id.split('watch?v=')[-1]
			if '&' in _id:
				_id = _id.split('&')[0]
			all_ids.append(_id)

		# If not already in list, add to database
		if video_id not in all_ids:
			# Add to backup file
			path = self.backend.info.data['Player']['backup']
			with open(os.path.join('resources',path), 'a') as f:
				f.write("\nhttps://www.youtube.com/watch?v=" + video_id)

		# Start
		self.startThread(self.newStream)