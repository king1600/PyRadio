from PySide.QtGui import *
from PySide.QtCore import *

from Widgets import *

import sys
import os
import threading
import time
import unicodedata

UPDATE_THREADS = 5

class ViewScene(QFrame):
	newTreedata = Signal(tuple)

	def __init__(self, win):
		super(ViewScene, self).__init__(win)
		self.win = win
		self.initUI()

	def initUI(self):
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self.createWidgets()

		self.done = False
		self.isSearching = False

	def setBackend(self, bg):
		self.backend = bg

	def startThread(self, func, *args):
		t = threading.Thread(target=func,args=args)
		t.daemon = True
		t.start()

	def createWidgets(self):
		self.tree = URLViewer(0,2) # id, title, video_id
		self.tree.setHorizontalHeaderLabels(['Title','Video ID'])
		self.tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.tree.setColumnWidth(0,460)
		self.tree.setColumnWidth(1,90)
		self.tree.setMinimumHeight(400)

		self.refresh_btn = QPushButton("Refresh list")

		self.refresh_btn.clicked.connect(self.initFetcher)

		btn_layout = QHBoxLayout()

		btn_layout.addWidget(self.refresh_btn)
		btn_layout.addStretch(1)

		self.layout.addWidget(self.tree)
		self.layout.addLayout(btn_layout)

		self.final_info = []
		self.fetched = 0
		self.running = True
		self.newTreedata.connect(self.addInfo)

	def _disable(self):
		self.refresh_btn.setEnabled(False)
	def _enable(self):
		self.refresh_btn.setEnabled(True)

	def chunks(self, l, n):
		for i in range(0, len(l), n):
			yield l[i:i+n]

	def initFetcher(self):
		if self.isSearching:
			return False
		self.startThread(self.startFetcher)

	def startFetcher(self):
		global UPDATE_THREADS
		self.isSearching = True
		self.done = False
		self._disable()
		self.win.status.emit("Fetching URL info...")
		self.fetched = 0
		self.tree.clear()
		self.tree.setHorizontalHeaderLabels(['Title','Video ID'])

		# Get Url list
		file_name = self.backend.info.data['Player']['backup']
		file_path = os.path.join('resources', file_name)

		# Read Url list
		with open(file_path, 'r') as f:
			self.urls = f.read().splitlines()
		for x in self.urls:
			place = self.urls.index(x)

			# remove non-youtube links
			if 'youtu' not in x:
				self.urls.pop( place )

			# remove empty lines
			if x == '':
				self.urls.pop( place )

		# put list in backend
		self.final_info = self.urls
		self.backend.urls = self.final_info

		# Get URLS to fetch
		self.fetchlist = []
		for x in range(len(self.urls)-1):
			url = self.urls[x]
			self.fetchlist.append( [ x , url ] )

		# Populate Table
		self.tree.setRowCount(len(self.fetchlist))

		if len(self.fetchlist) > 200:
			UPDATE_THREADS = 300

		# Split data to multiple threads for faster loading
		thread_list = list(self.chunks(self.fetchlist, UPDATE_THREADS))
		for thread in thread_list:
			self.startThread(self.threadFetcher, thread)

		# Wait for threads to finish
		while self.fetched != len(thread_list):
			time.sleep(0.1)

		self.win.status.emit("Finished Fetching")
		self._enable()
		self.done = True
		self.isSearching = False
		self.final_info = self.urls
		self.backend.urls = self.final_info

	def threadFetcher(self, fetch_list):
		# Get info
		for x in fetch_list:
			try:
				_id = x[1]

				# Get Video ID only
				if 'watch?v' in _id:
					_id = _id.split('watch?v=')[-1]
				if '&' in _id:
					_id = _id.split('&')[0]

				# make sure program is still on
				if not self.running:
					break

				# Get Title
				_title = self.backend.yi.getTitle(_id,_filter=True)

				# Add to tree
				#self.tree.setItem( x[0], 0, QTableWidgetItem( str(_title) ))
				#self.tree.setItem( x[0], 1, QTableWidgetItem( str(_id) ))
				self.newTreedata.emit((x[0], _title, _id))

			except Exception as e:
				print str(e)

			if not self.running:
				break

		self.fetched += 1

	def addInfo(self, info):
		# (x[0], _title, _id)
		self.tree.setItem( info[0], 0, QTableWidgetItem( str(info[1]) ))
		self.tree.setItem( info[0], 1, QTableWidgetItem( str(info[2]) ))
