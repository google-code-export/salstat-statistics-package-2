# A diagnostic script to test imports and find version numbers of code being used.
# Written by Mark Livingstone as part of S2 package.
# Released under GPL-2+ license

import sys
import os
import locale
import wx
import xlrd
import xlwt
import wx.lib.agw.aui
import numpy
import scipy
import matplotlib
import gridLib
import nicePlot
import plotFunctions
import statFunctions
import statlib
import PyQt4.QtCore
import matplotlib.pyplot

print "This is the S2 list of imports version numbers.\n\n"
print "If you are having problems and need help, please run this and forward the list below to us!\n\n"

print "This Python interpreter was built for platform:", sys.platform
print "Running on wx Platform:", wx.Platform
print "wxPython Version:", wx.version()
print "wx OS Version:", wx.GetOsVersion()
print "Python Version:", sys.version
print "XLWT Version:", xlwt.__VERSION__
print "XLRD Version:", xlrd.__VERSION__
print "OS Uname:", os.uname()
print "S2 Source Code Location:", os.getcwd()
print "Default Locale:", locale.getdefaultlocale()[1]
print "Default Stdin Encoding:", sys.stdin.encoding
print "Default Stdout Encoding:", sys.stdout.encoding
print "Default Stderr Encoding:", sys.stderr.encoding
print "wx AGW Version:", wx.lib.agw.__version__
print "Matplotlib Version:", matplotlib.__version__
print "Matplotlib Backend Selected:", matplotlib.pyplot.get_backend()
print "SciPy Version:", scipy.__version__
print "Numpy Version:", numpy.__version__
print "gridLib Version:", gridLib.version
print "nicePlot Version:", nicePlot.version
print "plotFunctions Version:", plotFunctions.version
print "statFunctions Version:", statFunctions.version
print "statlib Version:", statlib.version
print "PyQt4 Core Version:", PyQt4.QtCore.PYQT_VERSION_STR
print "\n\nRemember to also include a full description of what your problem is. Screenshots are really helpful, "
print "and if the problem is with a particular file, please feel free to forward it so we can reproduce the "
print "problem. We will treat any files as confidential that you choose to forward to us."

