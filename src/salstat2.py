#!/usr/bin/env python
""" Copyright 2011 - 2014 Sebastian Lopez Buritica, Salstat2 TEAM"""
##-----------------------------
## STANDARD LIBRARY DEPENDENCIES
import os
import sys
import wx
# to be used with translation module
import locale
from threading import Thread
##-----------------------------------
## END STANDARD LIBRARY DEPENDENCIES
##-----------------------------------

##-----------------------------
## EXTERNAL LIBRARY DEPENDENCIES
# http://www.pyinstaller.org/ticket/596
#from scipy.sparse.csgraph import _validation
from wx.html import HtmlHelpData    # create the help data panel
##-----------------------------------
## END EXTERNAL LIBRARY DEPENDENCIES
##-----------------------------------

import __builtin__
__builtin__.__dict__['__']= wx.GetTranslation

##-------------------------------
## INTERNAL LIBRARY DEPENDENCIES
import sei_glob
from CheckLibraries import test
from imagenes import imageEmbed
from mainFrame import MainFrame
from local import GetLangId, GetAvailLocales
##-----------------------------------
## END INTERNAL LIBRARY DEPENDENCIES
##-----------------------------------

inits = {}     # dictionary to hold the config values
missingvalue = None ## It's not used
imagenes = imageEmbed()
HOME = sei_glob.HOME

if wx.Platform == '__WXMSW__':
    # for windows OS
    face1 = 'Courier New'
    face2 = 'Times New Roman'
    face3 = 'Courier New'
    fontsizes = [7, 8, 10, 12, 16, 22, 30]
    pb = 12
    wind = 50
    DOCDIR = os.path.join(os.environ['USERPROFILE'], 'Documents')
    INITDIR = os.getcwd()
else:
    face1 = 'Helvetica'
    face2 = 'Times'
    face3 = 'Courier'
    fontsizes = [10, 12, 14, 16, 19, 24, 32]
    pb = 12
    wind = 0
    DOCDIR = os.environ['HOME']
    INITDIR = DOCDIR

# user can change settings like variable names, decimal places, missing no.s
# using a SimpleGrid Need evt handler - when new name entered, must be
#checked against others so no match each other

#---------------------------------------------------------------------------
class _checkUpdates(Thread):
    def run(self, *args, **params):
        ## extracted from iep the Interactive Editor for Python
        """ Check whether a newer version is available.
        :param args:
        :param params:
        """
        # Get versions available
        from urllib import urlopen
        import re
        url = "http://code.google.com/p/salstat-statistics-package-2/downloads/list"
        try:
            text = str(urlopen(url).read())
        except IOError:
            ## it's not possible to connect with the main site
            return
        pattern = 'salstat2 [V|v](.{1,9}?)\.(.{1,9}?)([A-z0-9]+) ([A-z0-9]+)' #\.exe\.zip
        results = re.findall(pattern, text)
        # getting unique values
        results = set(results)
        results = [(res[0] + '.' + res[1] + u' ' + res[2] + u' ' + res[3]) for res in results]
        # Produce single string with all versions ...
        versions = ', '.join(set(results))
        if not versions:
            versions = '?'
            # Define message
        text = "Your version of salstat2 is: {}\n"
        text += "Available versions are: {}\n\n"
        text = text.format(sei_glob.VERSION, versions)
        print text

class MainApp(wx.App):
    # the main app
    def __init__(self, *args, **kwargs):
        wx.App.__init__(self, *args, **kwargs)
        # checking the libraries
        test()
        wx.EVT_KEY_DOWN(self, self.OnKeypress)
        currPath=  sys.argv[0].decode(sys.getfilesystemencoding())
        directory= os.path.join( os.path.split(currPath)[0], 'Modules')
        directory= os.path.abspath( directory)
        sys.path.append( directory)


    def OnKeypress(self, evt):
        key = evt.GetKeyCode()
        if key == wx.WXK_F11:
            self.frame.tb1.fullScreen(self.frame.tb1._fullScreen)
        elif key == wx.WXK_F8:
            # To hide the toolbars of the main frame
            self.frame.tb1.onShown()
            self.frame.formulaBarPanel.onShown()
        else:
            evt.Skip()

    def OnInit(self):
        # getting the os type
        self.OSNAME = os.name
        self.__version__ = sei_glob.VERSION
        self.missingvalue = missingvalue
        wx.SetDefaultPyEncoding("utf-8")
        self.__ = __
        self.SetAppName(sei_glob.PROG_NAME)
        try:
            installDir = os.path.dirname(os.path.abspath(__file__))
        except:
            installDir = os.path.dirname(os.path.abspath(sys.argv[0]))

        # decoding the path name
        self.installDir = installDir.decode(sys.getfilesystemencoding())

        language = self.GetPreferences("Language")
        if not language:
            language = "Default"
        # Setup Locale
        locale.setlocale(locale.LC_ALL, '')
        lang_id= GetLangId(self.installDir, language)
        self.locale = wx.Locale(lang_id)
        if self.locale.GetCanonicalName() in GetAvailLocales(self.installDir):
            self.locale.AddCatalogLookupPathPrefix(os.path.join(self.installDir, "locale"))
            self.locale.AddCatalog(sei_glob.PROG_NAME)
        else:
            del self.locale
            self.locale = None
        self.getConfigFile()
        self.DECIMAL_POINT = locale.localeconv()['decimal_point']
        #<p> help data
        path = sys.argv[0].decode(sys.getfilesystemencoding())
        helpDir = os.path.abspath(os.path.join(os.path.split(path)[0], 'help'))
        fileName = os.path.join(helpDir, "help.hhp")
        self.HELPDATA = HtmlHelpData()
        if os.path.isfile(fileName):
            self.HELPDATA.AddBook(fileName)
            # help data /<p>
        self.icon = imagenes.logo16
        self.icon16 = imagenes.logo16
        self.icon24 = imagenes.logo24
        self.icon64 = imagenes.logo64

        # setting the lenguaje preference changed to False
        self.SetPreferences({"LenguageHasChange": False})
        self.frame = self.getMainFrame(None, self)
        self.SetTopWindow(self.frame)
        self.frame.Maximize()
        self.frame.Show()
        # check the len of sys.argv and try to open a file for all platforms
        if len(sys.argv) > 1:
            for f in sys.argv[1:]:
                self.OpenFileMessage(f)
        # check for a version update
        self._checkUpdates()
        return True
    
    def setItems(self, **params):
        # params= Logg, grid, output, plot
        for param, value in params.items():
            setattr(self,param, value)

    def getMainFrame( self, *args):
        frame = MainFrame(*args)
        frame.grid.SetFocus()
        return frame

    def BringWindowToFront( self):
        try: # it's possible for this event to come when the frame is closed
            wx.GetApp().GetTopWindow().Raise()
        except:
            pass

    def _visitBlog( self, *args, **params):
        import webbrowser
        webbrowser.open("http://s2statistical.blogspot.com/")

    def _getFeedBack( self, *args, **params):
        import webbrowser
        webbrowser.open("https://docs.google.com/forms/d/1abxr-i0s_5Aftjf0_B5K-jqg_sdDBcyQF_h24usJ7bU/viewform")

    def _checkUpdates( self, *args, **params):
        thread = _checkUpdates()
        thread.setDaemon(True)
        thread.start()
        if len(args) == 0:
            return
            ## Goto webpage if user chose to
        import webbrowser
        webbrowser.open("http://code.google.com/p/salstat-statistics-package-2/downloads/list")

    def OpenFileMessage(self, filename):
        self.BringWindowToFront()
        #junk, filterIndex = os.path.splitext(filename)
        fullPath = filename
        self.frame.grid.load(fullPath)

    def MacOpenFile(self, filename):
        """Called for files dropped on dock icon, or opened via finders context menu"""
        if (os.path.basename(filename).lower()) == "main.py":
            # don't activate when salstat is booting up and initial dock activation sees salstat.py itself!
            # or at any other time, pointing salstat at itself is pointless!
            pass
        else:
            texto = __(u"%s dropped on S2 dock icon") % (filename)
            print texto
            self.OpenFileMessage(filename)

    def MacReopenApp(self):
        """Called when the dock icon is clicked"""
        self.BringWindowToFront()

    def MacNewFile(self):
        pass

    def MacPrintFile(self, file_path):
        pass

    def getDataDir(self):
        '''Getting the config directory'''
        dd = wx.StandardPaths.Get()
        return os.path.abspath(dd.GetUserDataDir())

    def getConfigFile(self):
        """ Returns the configuration """
        if not os.path.exists(self.getDataDir()):
            # Create the data folder, it still doesn't exist
            os.makedirs(self.getDataDir())
        config = wx.FileConfig(localFilename=os.path.join(self.getDataDir(), "options"))
        return config

    def LoadConfig(self):
        """ Checks for the option file in wx.Config. """
        userDir = self.getDataDir()
        fileName = os.path.join(userDir, "options")
        preferences = {}
        # Check for the option configuration file
        if os.path.isfile( fileName):
            options = wx.FileConfig(localFilename=fileName)
            # Check for preferences if they exist
            val = options.Read('Preferences')
            if val:
                # Evaluate preferences
                preferences = eval(val)
        return preferences

    def GetPreferences(self, preferenceKey=None, default=None):
        """
        Returns the user preferences as stored in wx.Config.
        **Parameters:**
        * 'preferenceKey': the preference to load
        * 'default': a possible default value for the preference
        """
        preferences = self.LoadConfig()
        if preferenceKey is None:
            return preferences
        optionVal = None
        if preferenceKey in preferences:
            optionVal = preferences[preferenceKey]
        else:
            if default is not None:
                preferences[preferenceKey] = default
                self.SetPreferences(preferences)
                return default
        return optionVal

    def SetPreferences(self, newPreferences):
        """
        Saves the user preferences in wx.Config.
        **Parameters:**
        * 'newPreferences': the new preferences to save
        """
        preferences = self.LoadConfig()
        config = self.GetConfig()
        for key in newPreferences:
            preferences[key] = newPreferences[key]
        config.Write("Preferences", str(preferences))
        config.Flush()

    def GetConfig(self):
        """ Returns the configuration. """
        if not os.path.exists(self.GetDataDir()):
            # Create the data folder, it still doesn't exist
            os.makedirs(self.GetDataDir())
        config = wx.FileConfig(localFilename=os.path.join(self.GetDataDir(), "options"))
        return config

    def GetDataDir(self):
        """ Returns the option directory for GUI2Exe. """
        sp = wx.StandardPaths.Get()
        return sp.GetUserDataDir()

    def GetVersion(self):
        return sei_glob.VERSION

#--------------------------------------------------------------------------
# main loop
if __name__ == '__main__':
    app = MainApp(0)
    app.frame.Show()
    app.MainLoop()
    # eof