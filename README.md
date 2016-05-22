# PyRadio
Python Application for playing Youtube music in a playlist fashion.
current version: 0.5.0

## Installation

#### Windows:
* Download Python 2.7:
	* 32/64 bit: [Python Download](https://www.python.org/ftp/python/2.7.11/python-2.7.11.msi)
* Download GStreamer:
	* 32 bit: [32bit Download](https://gstreamer.freedesktop.org/data/pkg/windows/1.8.1/gstreamer-1.0-x86-1.8.1.msi)
	* 64 bit: [64bit Download](https://gstreamer.freedesktop.org/data/pkg/windows/1.8.1/gstreamer-1.0-x86_64-1.8.1.msi)
* Download GStreamer bindings: 
	* rev7: [Download](https://sourceforge.net/projects/pygobjectwin32/files/pygi-aio-3.18.2_rev7-setup.exe/download)

###### PyGi-Aio Installation
1. It will ask for portable python installation. Normally, just say no
2. Choose your python destination (should be C:\\Python27\\Lib\\site-packages)
3. *Important* Make sure to check these packages:
4. ![alt text](http://i.imgur.com/CYifiaW.png "Image of packages to download")
5. If you don't want anything else, continue with the installation


### Linux:
* Python:
	* should already have it
* GStreamer / Python bindings:
	* should already have it, if not:
	`sudo apt-get install gstreamer-1.0*`

## Use & info

* run PyRadio.py (or Main.py if you want)
* it should automatically load the backup songs
* to add your own list, copy it to the resource folder
* to add custom css, copy it to resource/css folder
* when adding a style/list select and apply from settings menu
* volume surpressor is the ratio which the volume is lowered (higher = lower volume)

## Bug Fixes

1. Problem: Initializing causes GUI to lock

Solution: launch init from signal -> thread

2. Problem: DBScene widgets lock on refresh

Solution: set isSearching bool for no refresh overlap

3. Problem: Next song playing over original

Solution: set isLoading bool for no stream overlap

4. Problem: stream wouldn't init until list refresh complete

Solution: wait 0.5s and get list rather than wait for refresh complete

5. Problem: GUI hangs when refreshing big list

Solution: set Tree items from tuple signal

6. Problem: Slow Database info fetching

Solution: chunk list for multi-threaded fetching