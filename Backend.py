from SettingsConf import SettingsConf

#http://docs.gstreamer.com/media/sintel_trailer-480p.webm

import threading
import random
import time

#declaring module / bad practice
Gst = None

class Backend(object):
	def __init__(self, win):
		self.info = SettingsConf()
		self.win = win

		self.pipeline = None
		self.done = False

		self.place = 0
		self.url_place = 0
		self.urls = []
		self.last_song = ""

	def initServices(self):
		self.startThread(self.Services)

	def Services(self):
		import gi
		gi.require_version('Gst','1.0')
		from gi.repository import Gst as _Gst

		global Gst
		Gst = _Gst
		Gst.init(None)

		from YoutubeExtractor import YoutubeInfoExtractor
		self.yi = YoutubeInfoExtractor()

		# Load audio for gstreamer to get it ready
		self.stream("http://docs.gstreamer.com/media/sintel_trailer-480p.webm")
		time.sleep(1)
		self.stop()

		self.done = True

	def startThread(self, func, *args):
		t = threading.Thread(target=func,args=args)
		t.daemon = True
		t.start()

	# other actions

	def getNextSong(self):
		choice = str(self.info.data['Player']['choice_style'])
		# Random selection
		if choice.lower() == 'random':
			song = random.choice(self.urls)

			# Make sure it doesn't repick a song
			while song == self.last_song:
				song = random.choice(self.urls)
			self.last_song = song

			return song

		# Linear selection
		else:
			# when list ends, restart
			if self.url_place > len(self.urls)-1 :
				self.url_place = 0

			song = self.urls[self.url_place]
			self.url_place += 1
			return song

	def stream(self, url):
		try:
			self.stop()
			del self.pipeline
		except:
			pass
		self.pipeline = Gst.parse_launch("playbin uri=" + url)
		self.pipeline.set_state(Gst.State.PLAYING)

	def play(self):
		try:
			self.pipeline.set_state(Gst.State.PLAYING)
		except:
			pass

	def pause(self):
		try:
			self.pipeline.set_state(Gst.State.PAUSED)
		except:
			pass

	def stop(self):
		try: 
			self.pipeline.set_state(Gst.State.NULL)
		except: 
			pass

	def setVolume(self, vol):
		try:
			self.pipeline.set_property('volume',vol)
		except Exception as e:
			pass

	def getVolume(self):
		try:
			return self.pipeline.get_property('volume')
		except:
			return 0

