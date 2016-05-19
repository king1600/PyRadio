from PyQt4.QtGui import *
from PyQt4.QtCore import *

from Widgets import *

import sys
import os
import threading
import time
import unicodedata

UPDATE_THREADS = 5

class ViewScene(QFrame):
	def __init__(self, win):
		super(ViewScene, self).__init__(win)
		self.win = win
		self.initUI()

	def initUI(self):
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self.createWidgets()

		self.done = False

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
		self.tree.setMinimumHeight(340)

		self.add_btn = QPushButton("Add link")
		self.remove_btn = QPushButton("Remove link")
		self.clear_btn = QPushButton("Clear all")

		btn_layout = QHBoxLayout()

		btn_layout.addWidget(self.add_btn)
		btn_layout.addWidget(self.remove_btn)
		btn_layout.addWidget(self.clear_btn)
		btn_layout.addStretch(1)

		self.layout.addWidget(self.tree)
		self.layout.addLayout(btn_layout)

		self.final_info = []
		self.fetched = 0

	def _disable(self):
		self.add_btn.setEnabled(False)
		self.remove_btn.setEnabled(False)
		self.clear_btn.setEnabled(False)
	def _enable(self):
		self.add_btn.setEnabled(True)
		self.remove_btn.setEnabled(True)
		self.clear_btn.setEnabled(True)

	def chunks(self, l, n):
		for i in range(0, len(l), n):
			yield l[i:i+n]

	def initFetcher(self):
		self.startThread(self.startFetcher)

	def startFetcher(self):
		self.done = False
		self._disable()
		self.win.status.emit("Fetching URL info...")
		self.fetched = 0

		# Get Url list
		file_path = os.path.join('resources',
			self.backend.info.data['Player']['backup'])

		# Read Url list
		with open(file_path, 'r') as f:
			self.urls = f.read().splitlines()
		for x in self.urls:
			place = self.urls.index(x)
			if 'youtu' not in x:
				self.urls.remove(x)

		# Get URLS to fetch
		self.fetchlist = []
		for x in range(len(self.urls)-1):
			url = self.urls[x]
			self.fetchlist.append( [ x , url ] )

		# Populate Table
		self.tree.setRowCount(len(self.fetchlist))

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

				# Get Title
				_title = self.backend.yi.getTitle(_id)

				self.tree.setItem( x[0], 0, QTableWidgetItem( str(_title) ))
				self.tree.setItem( x[0], 1, QTableWidgetItem( str(_id) ))

			except Exception as e:
				print str(e)

		self.fetched += 1