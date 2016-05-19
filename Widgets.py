from PySide.QtGui import *
from PySide.QtCore import *

import os

class URLViewer(QTableWidget):
	def __init__(self,row,col):
		super(URLViewer, self).__init__(row,col)

class VolumeSlider(QSlider):
	def __init__(self):
		super(VolumeSlider, self).__init__()
		self.setOrientation(Qt.Horizontal)

class VersionLabel(QLabel):
	def __init__(self,text=''):
		super(VersionLabel, self).__init__(text)
		self.setAlignment(Qt.AlignRight)

class StatusLabel(QLabel):
	def __init__(self,text=''):
		super(StatusLabel, self).__init__(text)
		self.setAlignment(Qt.AlignLeft)

class SongTitle(QLabel):
	def __init__(self,text=''):
		super(SongTitle, self).__init__(text)
		self.setAlignment(Qt.AlignCenter)
		self.limit = 45

	def _setText(self, text):
		if len(text) > self.limit:
			text = text[:self.limit] + "..."
		self.setText(text)


class ImageButton(QLabel):
	clicked = Signal(str)
	return_str = ''

	def __init__(self):
		super(ImageButton, self).__init__()

	def setImage(self, path, size=None, keep=True):
		if '/' in path:
			dirs = path.split('/')
			path = os.path.join(*dirs)
		image = QImage(path)
		if size == None:
			pixmap = QPixmap.fromImage(image)
		else:
			if keep:
				pixmap = QPixmap.fromImage(image).scaled(size[0],size[1],
									Qt.KeepAspectRatio)
			else:
				pixmap = QPixmap.fromImage(image).scaled(size[0],size[1])
		self.setPixmap(pixmap)

	def setReturnString(self, _string):
		self.return_str = _string

	def mousePressEvent(self, event):
		if self.return_str != None:
			self.clicked.emit(self.return_str)

class NavigationBar(QHBoxLayout):
	def __init__(self):
		super(NavigationBar, self).__init__()

class SearchBar(QLineEdit):
	def __init__(self):
		super(SearchBar, self).__init__()

class SearchButton(QPushButton):
	def __init__(self,text=''):
		super(SearchButton, self).__init__(text)