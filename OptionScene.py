from PySide.QtGui import *
from PySide.QtCore import *
from Widgets import *

import os

class OptionScene(QFrame):
	def __init__(self, win):
		super(OptionScene, self).__init__(win)
		self.win = win
		self.initUI()

	def initUI(self):
		self.layout = QVBoxLayout()
		self.layout.setSpacing(80)
		self.setLayout(self.layout)

		self.createWidgets()

	def setBackend(self, bg):
		self.backend = bg

		self.loadSettings()

	def loadSettings(self):
		self.vol_sup_.setText(str(self.backend.info.data['Player']['vol_supp_ratio']))

		# One line file lister
		style_path = os.path.join('resources','css')
		files_in_css = [f for f in os.listdir(style_path) if os.path.isfile(os.path.join(style_path, f))]

		# display styles
		for css in files_in_css:
			self.style_.addItem( str(css).replace('.css','') )

		# display themes
		themes = QStyleFactory.keys()
		for theme in themes:
			self.theme_.addItem( str(theme) )

		# image bool
		for opt in [ "True", "False "]:
			self.img_.addItem( opt )
		# set last value
		if bool(self.backend.info.data['Player']['getimage']):
			self.img_.setCurrentIndex(0)
		else:
			self.img_.setCurrentIndex(1)


		# song choice style
		for opt in [ "Random", "List" ]:
			self.cs_.addItem(opt)
		# set last value
		if str(self.backend.info.data['Player']['choice_style']).lower() == "random":
			self.img_.setCurrentIndex(0)
		else:
			self.img_.setCurrentIndex(1)

		# load backup list location
		data_path = os.path.abspath('resources')
		data_list = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]
		_index = 0
		for data in data_list:
			self.backup_.addItem( str(data) )
			if data == str(self.backend.info.data['Player']['backup']):
				_index = data_list.index(data)
				self.last_file = data
		self.backup_.setCurrentIndex(_index)

	def createWidgets(self):
		_vol_sup = OptionLabel("Volume Suppression Ratio:")
		_style = OptionLabel("Stylesheet / CSS:")
		_theme = OptionLabel("Application Theme:")
		_backup = OptionLabel("Default URL list:")
		_img = OptionLabel("Get Thumbnail Image:")
		_cs = OptionLabel("Song Choice Style:")

		self.vol_sup_ = QLineEdit()
		self.style_ = QComboBox()
		self.theme_ = QComboBox()
		self.img_ = QComboBox()
		self.cs_ = QComboBox()
		self.backup_ = QComboBox()
		self.last_file = ""

		# bind comboboxes
		self.style_.activated[str].connect(self.changeStyle)
		self.theme_.activated[str].connect(self.changeTheme)
		self.img_.activated[str].connect(self.changeImage)
		self.cs_.activated[str].connect(self.changeChoice)

		self.apply_btn = QPushButton("Apply")
		self.apply_btn.clicked.connect(self.saveInfo)

		top_layout = QGridLayout()
		bottom_layout = QHBoxLayout()

		top_layout.addWidget(_vol_sup, 0, 0)
		top_layout.addWidget(self.vol_sup_, 0, 1)
		top_layout.addWidget(_style, 1, 0)
		top_layout.addWidget(self.style_, 1, 1)
		top_layout.addWidget(_theme, 2, 0)
		top_layout.addWidget(self.theme_, 2, 1)
		top_layout.addWidget(_img, 3, 0)
		top_layout.addWidget(self.img_, 3, 1)
		top_layout.addWidget(_cs, 4, 0)
		top_layout.addWidget(self.cs_, 4, 1)
		top_layout.addWidget(_backup, 5, 0)
		top_layout.addWidget(self.backup_, 5, 1)
		top_layout.setSpacing(30)

		bottom_layout.addStretch(1)
		bottom_layout.addWidget(self.apply_btn)

		self.layout.addLayout(top_layout)
		self.layout.addStretch(1)
		self.layout.addLayout(bottom_layout)

	# Change actions

	def changeTheme(self, text):
		self.win.app.setStyle(text)
		self.backend.info.changeValue('Player','theme',str(self.theme_.currentText()))

	def changeStyle(self, text):
		self.backend.info.changeValue('Player','style',str(self.style_.currentText()))
		CSS = self.backend.info.data['Player']['style']
		with open( os.path.join('resources','css', text + '.css'), 'r') as f:
			self.win.setStyleSheet( f.read() )

	def changeChoice(self, *args):
		self.backend.info.changeValue('Player','choice_style',str(self.cs_.currentText()))

	def changeImage(self, *args):
		self.backend.info.changeValue('Player','getimage',str(self.img_.currentText()))

	def changeBackup(self, text):
		self.backend.info.changeValue('Player','backup',str(self.backup_.currentText()))
		if self.last_file != text:
			self.win.viewscene.initFetcher()
		self.last_file = text

	#Final changes

	def saveInfo(self):
		# Get Other values
		self.backend.info.changeValue('Player','style',str(self.style_.currentText()))
		self.backend.info.changeValue('Player','theme',str(self.theme_.currentText()))
		self.backend.info.changeValue('Player','getimage',str(self.img_.currentText()))
		self.backend.info.changeValue('Player','choice_style',str(self.cs_.currentText()))
		self.backend.info.changeValue('Player','backup',str(self.backup_.currentText()))

		#Commit changes
		self.backend.info.commit()

		# Get Volume suppressor only in double
		text = str(self.vol_sup_.text())
		try:
			text = float(text)*1.0
			self.backend.info.changeValue('Player','vol_supp_ratio',str(text))
		except:
			MessageBox().showinfo("ValueError","Volume Supressor must be a number")
			return True

		#Commit changes
		self.backend.info.commit()

