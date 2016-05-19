#import StringIO
import urllib2
import os
import socket
import signal
import subprocess
import sys

VERSION_LINK  = "https://raw.githubusercontent.com/king1600/PyRadio/master/VERSION.txt"
TEST_LINK     = "https://github.com/king1600/PyRadio"
VERSION_FILE  = os.path.abspath("VERSION.txt")

CONTENT_LIST = [
"PyRadio.py",
"Backend.py",
"Widgets.py",
"YoutubeExtractor.py",
"SettingsConf.py",
"SETTINGS.ini",
"MainScene.py"
]

class Main:
	def __init__(self):
		print "[*] Initializing Program..."
		self.update()
		self.run_program()
		
	def run_program(self):
		print "[*] Starting Program"

		cmd = 'python PyRadio.py'
		proc = subprocess.Popen(cmd.split(),
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
		output = proc.communicate()
		if output[1] != '':
			print output[1]
		else:
			print "output: "+ output[0]

		print "[*] Exitting ... "

		
	def update(self):
		if self.checkInternet():
			#success, connection!
			self.getVersion()
			self.getLatest()
			if self.version != self.latest:
				#update
				print "[x] Content out of date, performing update..."
				self.DO_UPDATE()
		else:
			#handle no internet exception
			print "[-] Cannot connect to test link, please check internet"
			sys.exit()
		
	def DO_UPDATE(self):
		#### Get new contents straight from repo ###
		for _file in CONTENT_LIST:
			prefix = "https://raw.githubusercontent.com/king1600/PyRadio/master/"
			url_link = prefix + _file

			print "[+] Fetching " + _file

			try:
				with open(_file, 'w') as f:
					f.write( urllib2.urlopen( url_link ).read() )
			except Exception as e:
				print "[x] Error: "+ str(e)
		### ########################## ###

		#save latest version
		with open('VERSION.txt','w') as f:
			f.write(self.latest)

		print "[*] Update complete"
		
	def checkInternet(self):
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

		#Parse URL fore pure DNS name
		try:
			link = TEST_LINK
			if 'http' in link:
				if 'https' in link:
					link = link.replace('https://','')
				else:
					link = link.replace('http://','')
			if 'www.' in link:
				link = link.replace('www.','')
			if '/' in link:
				link = link.split('/')[0]
			print "[?] Testing on link: "+ link

			#Test connection
			s.connect(( link ,80))
			s.close()
			return True

		except Exception as e:
			print "[-] Error: "+ str(e)
			return False
	
	def getVersion(self):
		with open( VERSION_FILE, 'r' ) as f:
			self.version = f.read()
		print "[*] Current Version: "+self.version
			
	def getLatest(self):
		self.latest = urllib2.urlopen(VERSION_LINK).read()
		print "[*] Latest Version: "+self.latest
	
if __name__ == "__main__":
	Main()