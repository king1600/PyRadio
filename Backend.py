from SettingsConf import SettingsConf

#http://docs.gstreamer.com/media/sintel_trailer-480p.webm

import threading
import random

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

		self.done = True

	def startThread(self, func, *args):
		t = threading.Thread(target=func,args=args)
		t.daemon = True
		t.start()

	# other actions

	def getNextSong(self):
		choice = str(self.info.data['Player']['choice_style'])
		if choice == 'random':
			return random.choice(self.urls)
		else:
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
		except:
			pass

	def getVolume(self):
		try:
			return self.pipeline.get_property('volume')
		except:
			return 0

