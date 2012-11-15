S2 Statistics Package v2.1 Beta 3 

OS X version for x86_64 platform Macs


Website for bug reports, feature requests, etc:	http://code.google.com/p/salstat-statistics-package-2/

------ Prerequisite Libraries: ------

It should not be necessary to install these if you install from one of the online installers, but will be required if
installing from Source Code. Some can be installed using the Python "pip" or "easy_install" installation utilities.

Library Name			Website
------------			-------------

xlrd					http://www.python-excel.org
xlwt					http://www.python-excel.org
numpy					http://numpy.scipy.org
scipy					http://www.scipy.org
wxython 2.94			http://www.wxpython.org
PIL						http://www.pythonware.com/products/pil/
PyQT4					http://www.riverbankcomputing.co.uk/software/pyqt/download

You can save yourself some time by loading up the Free Enthought Python Distribution (http://enthought.com) which should
install most of the above for you except for {xlrd, xlwt}


------ Installation Notes: ----------

1)	To use this program, unzip the S2.app bundle and drag to your /Applications folder.
2)	If you receive a message from Gate Keeper on OS X Mountain Lion machines regarding this application being unsigned,
	Just right-click S2.app and select "Open". You should only have to do this the first time.


------- Know Bugs: ------------------

1)	The font change dialog will not remain on screen when opened.


------- Future Version Notes: -------

1)	We will create a .DMG drag'n'drop installer.
2)	If you wish to run S2 on other Mac platforms, it should run fine from source code (either download the source code 
	package, or clone our Mercurial repository. It has been tested on 64 bit Mountain Lion, and 32-bit Snow Leopard and Lion
	using either Mac Ports, or the Enthought Python Distribution.)
3)	Help and documentation will be coming in future versions. 

