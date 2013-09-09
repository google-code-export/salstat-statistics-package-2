#!/usr/bin/env python

#RELEASE 2.1 rc2

""" Copyright 2012 - 2013 Sebastian Lopez Buritica, S2 Team,  licensed under GPL 3

SalStat Statistics Package. Copyright 2002 Alan James Salmoni. Licensed
under the GNU General Public License (GPL 2) """

##-----------------------------
## STANDARD LIBRARY DEPENDENCIES
import os
import sys
import webbrowser # online Help
import string
import traceback
# to be used with translation module
import locale
import glob

from threading import Thread
##---------------------------------
## END STANDARD LIBRARY DEPENDENCIES
##---------------------------------

##-----------------------------
## EXTERNAL LIBRARY DEPENDENCIES
# http://www.pyinstaller.org/ticket/596
from scipy.sparse.csgraph import _validation
#----
try:
    sys.modules['wx']
except KeyError:
    # check the required version
    try:
        import wx
        if wx.__version__ < '2.9.4':
            raise ImportError("Required wx 2.9.4 at least")
    except ImportError:
        raise ImportError("Required wx 2.9.4")
# -----------------
# to use the sash
# import  wx.lib.multisash as sash
# -----------------
from   wx.grid  import GridCellAttr    # to used the cellattr
from   wx.html  import HtmlHelpData    # create the help data panel
from   wx.combo import BitmapComboBox # translation control
import wx.lib.agw.aui as aui          # advanced user interface manager
import wx.lib.langlistctrl as langlist
import wx.py # to be used as the script panel

if wx.Platform != '__WXMSW__':
    # -----------------
    # these imports just for py2app
    import wx.lib.agw.aui.aui_constants
    import wx.lib.agw.aui.aui_utilities
    import wx.lib.agw.aui.auibar
    import wx.py.buffer
    import wx.py.crust
    #import wx.py.crustslices
    try:
        import matplotlib
        if matplotlib.__version__ < '1.1':
            raise ImportError("matplotlib >= 1.1.0 required")
    except ImportError:
        raise
    import matplotlib.tri.triangulation
    import matplotlib.delaunay.triangulate
    import matplotlib.tri.tricontour
    import matplotlib.tri.tripcolor
    import matplotlib.projections.geo
    import matplotlib.projections.polar
    import matplotlib.backends.backend_macosx
    import matplotlib.backends._macosx

    # -----------------
try:
    import numpy
except ImportError:
    raise ImportError("numpy required")

# import statsmodels.api as sm
try:
    import scipy
    if scipy.__version__ < '0.11':
        raise ("scipy >= 0.11.0 required")
except ImportError:
    raise ("scipy >= 0.11.0 required")
##---------------------------------
## END EXTERNAL LIBRARY DEPENDENCIES
##---------------------------------

##-----------------------------
## INTERNAL LIBRARY DEPENDENCIES
import salstat2_glob
# graphics system
from plotFunctions import pltobj as plot

# spreadSheet
from ntbSheet import NoteBookSheet, NoteBookSql
from gridLib  import floatRenderer

# import modules to be used into the script panel
from slbTools   import  homogenize, GroupData # GroupData is used to treat data a a pivot table
from easyDialog import Dialog as dialog # dialog creation

# statistical functions
from statlib import stats # statistical packages
import statFunctions

from script     import ScriptPanel
from imagenes   import imageEmbed
from helpSystem import Navegator
from TreeCtrl   import TreePanel

from dialogs import SaveDialog, SaveOneGridDialog, VariablesFrame #, DescriptivesFrame
from calculator import MyFrame1 as TransformFrame
from dialogs import createPlotSelectionPanel

import plotFunctions
##---------------------------------
## END INTERNAL LIBRARY DEPENDENCIES
##---------------------------------

inits= {}    # dictionary to hold the config values
missingvalue= None ## It's not used
imagenes= imageEmbed()
HOME= os.getcwd()

# Define the translation class
import __builtin__
__builtin__.__dict__['_']= wx.GetTranslation
if wx.Platform == '__WXMSW__':
    # for windows OS
    face1 = 'Courier New'
    face2 = 'Times New Roman'
    face3 = 'Courier New'
    fontsizes = [7,8,10,12,16,22,30]
    pb = 12
    wind = 50
    DOCDIR = os.path.join( os.environ['USERPROFILE'], 'Documents')
    INITDIR = os.getcwd()
else:
    face1 = 'Helvetica'
    face2 = 'Times'
    face3 = 'Courier'
    fontsizes = [10,12,14,16,19,24,32]
    pb = 12
    wind = 0
    DOCDIR = os.environ['HOME']
    INITDIR = DOCDIR

class _MyLog(wx.PyLog):
    def __init__(self, textCtrl, logTime=0):
        wx.PyLog.__init__(self)
        self.tc = textCtrl
        self.logTime = logTime

    def DoLogString(self, message, timeStamp):
        #print message, timeStamp
        #if self.logTime:
        #    message = time.strftime("%X", time.localtime(timeStamp)) + \
        #              ": " + message
        if self.tc:
            self.tc.AppendText(message + '\n')

class LogPanel( wx.Panel ):
    def _numLine(self):
        i = 1
        while True:
            yield i
            i+= 1
    def __init__( self, parent,*args,**params ):
        self.numLinea = self._numLine()
        wx.Panel.__init__ ( self, parent,*args, **params)
        bSizer8 = wx.BoxSizer( wx.VERTICAL )
        self.log = wx.TextCtrl( self, wx.ID_ANY, style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL )
        bSizer8.Add( self.log, 1, wx.EXPAND, 5 )
        wx.Log_SetActiveTarget(_MyLog(self.log))
        self.SetSizer( bSizer8 )
        self.Layout()

    def writeLine(self, lineaTexto, writem= True):
        '''it writes a text line'''
        #texto= str(self.numLinea.next()) + " >> "
        texto= ''
        #if writem:
        #    texto= str( ">>> ")
        texto+= lineaTexto # + "\n"
        # se escribe el texto indicado
        self.log.AppendText(texto)

    def write(self, obj, writem= True):
        if isinstance(obj, (str, unicode)):
            lineaTexto= obj
        else:
            lineaTexto= obj.__str__()
        #if lineaTexto.endswith('\n'):
        #    lineaTexto= lineaTexto[:-1]
        self.writeLine(lineaTexto, writem)

    def clearLog(self):
        self.log.SetValue('')

    def __del__( self ):
        pass

#---------------------------------------------------------------------------
# grid preferences - set row & col sizes
def GridPrefs(parent):
#shows dialog for editing the data grid
    btn1=  ['SpinCtrl',   [0,5000,0]]
    btn2=  ['StaticText', [_(u"Change the cell Size")]]
    btn3=  ['StaticText', [_(u"Column Width")]]
    btn4=  ['StaticText', [_(u"Row Height")]]
    setting= {'Title': _(u"Change the cell size")}

    struct= list()
    struct.append([btn2])
    struct.append([btn1, btn3])
    struct.append([btn1, btn4])
    dlg= dialog(self, settings = setting, struct = struct)

    if dlg.ShowModal() == wx.ID_OK:
        values= dlg.GetValue()
    else:
        dlg.Destroy()
        return

    colwidth= values[0]
    rowheight= values[1]
    wx.GetApp().frame.grid.SetDefaultColSize(colwidth, True)
    wx.GetApp().frame.grid.SetDefaultRowSize(rowheight, True)
    wx.GetApp().frame.grid.ForceRefresh()

#---------------------------------------------------------------------------
# user can change settings like variable names, decimal places, missing no.s
# using a SimpleGrid Need evt handler - when new name entered, must be
#checked against others so no match each other
class formulaBar ( wx.Panel ):#aui.AuiToolBar
    def __init__( self, parent , *args,**params):
        wx.Panel.__init__(self,  parent,   #aui.AuiToolBar
                                id=    wx.ID_ANY,
                                pos=   wx.DefaultPosition,
                                size=  wx.DefaultSize,)
                                #style= 0,
                                #agwStyle= aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_HORZ_LAYOUT)

        bSizer1=         wx.BoxSizer( wx.HORIZONTAL )
        self._text=      u''
        self.lastParent= None
        self.textCtrl1=  wx.TextCtrl( self, wx.ID_ANY,
                                      wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                      wx.TE_CHARWRAP|wx.TE_MULTILINE|wx.TE_RICH2|
                                      wx.TE_WORDWRAP|wx.NO_BORDER )

        self.textCtrl1.SetMinSize( wx.Size( 600, 28 ) )
        self.textCtrl1.SetSize( wx.Size( 600, 28 ) )

        bSizer1.Add( self.textCtrl1, 0, wx.ALL, 5 )
        #self.AddControl( self.textCtrl1, label= "Text control")

        imag= imageEmbed()
        self.arrowUp=   imag.arrowUp
        self.arrowDown= imag.arrowDown
        #self.m_toggleBtn1= wx.BitmapButton( self, wx.ID_ANY,
                                            #self.arrowDown,
                                            #wx.DefaultPosition,
                                            #wx.DefaultSize,
                                            #wx.BU_AUTODRAW )

        #bSizer1.Add( self.m_toggleBtn1, 0, wx.ALL, 5 )
        #self.AddControl(self.m_toggleBtn1, label= "v")

        #self.m_toggleBtn1.Bind( wx.EVT_BUTTON, self._ontogle )
        self.originalSize= self.Size
        self.SetSizer( bSizer1 )
        self.toggle= True
        self.Layout()

    def _ontogle(self, evt):
        if self.toggle:
            auisize=self.GetSize()
            self.SetSize((auisize[0], auisize[1]+28))
            self.textCtrl1.SetMinSize( wx.Size( 600, 28*2 ) )
            self.textCtrl1.SetSize( wx.Size( 600, 28*2 ) )
            self.Layout()
            self.m_toggleBtn1.Bitmap= self.arrowUp
        else:
            auisize=self.GetSize()
            self.SetSize((auisize[0], auisize[1]-28))
            self.textCtrl1.SetMinSize( wx.Size( 600, 28 ) )
            self.textCtrl1.SetSize( wx.Size( 600, 28 ) )
            self.Layout()
            self.m_toggleBtn1.Bitmap= self.arrowDown
        self.toggle= not self.toggle
        #app= wx.GetApp()
        #app.frame.m_mgr.Update()
        evt.Skip()

    @property
    def value(self):
        return self._text
    @value.setter
    def value(self, texto):
        # try to fix to interactibely change the contents of the las selected cell
        if not isinstance( texto, (str, unicode)):
            raise StandardError("only accept string values")
        self._text= texto
        self.textCtrl1.SetValue(texto)
#---------------------------------------------------------------------------
#---- Language List Combo Box----#
class LangListCombo(BitmapComboBox):
    """
    Combines a langlist and a BitmapComboBox.

    **Note:**

    *  from Editra.dev_tool
    """

    def __init__(self, parent, default=None):
        """
        Creates a combobox with a list of all translations for S2
        as well as displaying the countries flag next to the item
        in the list.

        **Parameters:**

        * default: The default item to show in the combo box
        """
        self.MainFrame = parent.Parent.Parent

        lang_ids=   GetLocaleDict( GetAvailLocales( wx.GetApp().installDir)).values()
        lang_items= langlist.CreateLanguagesResourceLists( langlist.LC_ONLY, \
                                                            lang_ids)
        BitmapComboBox.__init__( self, parent,
                                 size = wx.Size( 150, 26),
                                 style = wx.CB_READONLY)
        for lang_d in lang_items[1]:
            bit_m = lang_items[0].GetBitmap(lang_items[1].index(lang_d))
            self.Append(lang_d, bit_m)

        if default:
            self.SetValue(default)

def GetLocaleDict(loc_list, opt=0):
    """
    Takes a list of canonical locale names and by default returns a
    dictionary of available language values using the canonical name as
    the key. Supplying the Option OPT_DESCRIPT will return a dictionary
    of language id's with languages description as the key.


    **Parameters:**

    * loc_list: list of locals

    **Keywords:**

    * opt: option for configuring return data

    **Returns:**

    *  dict of locales mapped to wx.LANGUAGE_*** values

    **Note:**

    *  from Editra.dev_tool
    """
    lang_dict = dict()
    for lang in [x for x in dir(wx) if x.startswith("LANGUAGE")]:
        loc_i = wx.Locale(wx.LANGUAGE_DEFAULT).\
            GetLanguageInfo(getattr(wx, lang))
        if loc_i:
            if loc_i.CanonicalName in loc_list:
                if opt == 1:
                    lang_dict[loc_i.Description] = getattr(wx, lang)
                else:
                    lang_dict[loc_i.CanonicalName] = getattr(wx, lang)
    return lang_dict

def GetLangId(installDir, lang_n):
    """
    Gets the ID of a language from the description string. If the
    language cannot be found the function simply returns the default language


    **Parameters:**

    * lang_n: Canonical name of a language

    **Returns:**

    *  wx.LANGUAGE_*** id of language

    **Note:**

    *  from Editra.dev_tool
    """

    lang_desc = GetLocaleDict(GetAvailLocales(installDir), 1)
    return lang_desc.get(lang_n, wx.LANGUAGE_DEFAULT)

def GetAvailLocales(installDir):
    """
    Gets a list of the available locales that have been installed.
    Returning a list of strings that represent the
    canonical names of each language.


    **Returns:**

    *  list of all available local/languages available

    **Note:**

    *  from Editra.dev_tool
    """

    avail_loc = []
    langDir = installDir
    loc = glob.glob(os.path.join(langDir, "locale", "*"))
    for path in loc:
        the_path = os.path.join(path, "LC_MESSAGES", salstat2_glob.APPNAME+".mo")
        if os.path.exists(the_path):
            avail_loc.append(os.path.basename(path))
    return avail_loc

class Tb1(aui.AuiToolBar):
    def __init__(self, *args, **params):
        # emulating [F11]
        self._fullScreen= False

        imageEmbed=   params.pop('imageEmbed')
        _=    params.pop('translation')
        aui.AuiToolBar.__init__(self, *args, **params)
        # Get icons for toolbar
        imag =       imageEmbed()
        NewIcon =    imag.exporCsv
        OpenIcon =   imag.folder
        SaveIcon =   imag.disk
        SaveAsIcon = imag.save2disk
        #PrintIcon =  imag.printer
        CutIcon =    imag.edit_cut
        CopyIcon =   imag.edit_copy
        PasteIcon =  imag.edit_paste
        PrefsIcon =  imag.preferences
        HelpIcon =   imag.about
        UndoIcon =   imag.edit_undo
        RedoIcon =   imag.edit_redo
        #closePage=   imag.cancel
        self._iconMax= imag.maximize
        self._iconMin= imag.minimize

        self.bt1 = self.AddSimpleTool(10, _(u"New"),     NewIcon,    _(u"New"))
        self.bt2 = self.AddSimpleTool(20, _(u"Open"),    OpenIcon,   _(u"Open"))
        self.bt3 = self.AddSimpleTool(30, _(u"Save"),    SaveIcon,   _(u"Save"))
        self.bt4 = self.AddSimpleTool(40, _(u"Save As"), SaveAsIcon, _(u"Save As"))
        ##self.bt5 = self.AddSimpleTool(50, "Print",PrintIcon,"Print")
        self.AddSeparator()
        self.bt11= self.AddSimpleTool(wx.ID_ANY, _(u"Undo"), UndoIcon, _(u"Undo"))
        self.bt12= self.AddSimpleTool(wx.ID_ANY, _(u"Redo"), RedoIcon, _(u"Redo"))
        self.AddSeparator()
        self.bt6 = self.AddSimpleTool(60, _(u"Cut"),  CutIcon,   _(u"Cut"))
        self.bt7 = self.AddSimpleTool(70, _(u"Copy"), CopyIcon,  _(u"Copy"))
        self.bt8 = self.AddSimpleTool(80, _(u"Paste"),PasteIcon, _(u"Paste"))
        self.AddSeparator()
        self.bt9 = self.AddSimpleTool(85, _(u"Preferences"),PrefsIcon, _(u"Preferences"))
        ##self.bt10= selfAddSimpleTool(90, "Help", HelpIcon, "Help")
        self.bt10= self.AddSimpleTool(95, _(u"OnlineHelp"), HelpIcon, _(u"Online Help"))
        self.btnMax= self.AddSimpleTool(100, _(u"Maximize"), self._iconMax, _(u"Maximize"))
        ##self.bt13= self.AddSimpleTool(100, _(u"Close"), closePage, _(u"Close Current Page"))

        # to the language
        language = wx.GetApp().GetPreferences( "Language")
        if not language:
            language = "Default"
        self.languages= LangListCombo( self , language)
        self._Btn= self.AddControl( self.languages, label= "Language")
        self.SetToolBitmapSize( (24,24))
        self.Realize()
        self.languages.Bind( wx.EVT_COMBOBOX, self._changeLanguage) # id= self.languages.GetId()

    def fullScreen(self, bool):
        self._fullScreen= not bool
        bitmap= [self._iconMax, self._iconMin][self._fullScreen]
        self.btnMax.SetBitmap( bitmap)
        app= wx.GetApp()
        app.frame.ShowFullScreen( self._fullScreen)

    @property
    def grid(self):
        return wx.GetApp().grid

    def _changeLanguage(self, evt):
        allPreferences= dict()
        allPreferences["Language"] = self.languages.GetValue()
        print "you have to restart the app to see the changes"
        wx.GetApp().SetPreferences( allPreferences)
        # force next restart to redraw the panel labels
        wx.GetApp().SetPreferences({"DefaultPerspective": None})
        wx.GetApp().SetPreferences({"currentPerspective": None})

    def LoadFile(self, evt):
        self.grid.addPage( gridSize= (1,1))
        (HasLoad, SheetName)= self.grid.LoadFile(evt)
        if not HasLoad:
            # delete the current sheet
            return
        self.grid.changeLabel(newLabel= SheetName)
        evt.Skip()

    def SaveXls(self, evt):
        if len(self.grid.pageNames) == 0:
            return
        self.grid.SaveXls()
        evt.Skip()

    def SaveXlsAs(self, evt):
        if len(self.grid.pageNames) == 0:
            return
        self.grid.SaveXlsAs(evt)
        evt.Skip()

    def CutData(self, evt):
        if len(self.grid) == 0:
            return
        self.grid.CutData(evt)
        evt.Skip()

    def CopyData(self, evt):
        if len(self.grid) == 0:
            return
        self.grid.CopyData(evt)
        evt.Skip()

    def PasteData(self, evt):
        if len(self.grid) == 0:
            return
        self.grid.PasteData(evt)
        evt.Skip()

    def Undo(self, evt):
        if len(self.grid) == 0:
            return
        self.grid.Undo(evt)
        evt.Skip()

    def Redo(self, evt):
        if len(self.grid) == 0:
            return
        self.grid.Redo(evt)
        evt.Skip()

    def NewPage(self, evt):
        self.grid.addPage( gridSize= (1,1))
        evt.Skip()

    def DeleteCurrentCol(self, evt):
        self.grid.DeleteCurrentCol(evt)
        evt.Skip()

    def DeleteCurrentRow(self, evt):
        self.grid.DeleteCurrentRow(evt)
        evt.Skip()

    def SelectAllCells(self, evt):
        self.grid.SelectAllCells(evt)
        evt.Skip()

class _checkUpdates(Thread):
    def run(self, *args, **params):
        ## extracted from iep the Interactive Editor for Python
        """ Check whether a newer version is available. """
        # Get versions available
        from urllib import urlopen
        import re
        url = "http://code.google.com/p/salstat-statistics-package-2/downloads/list"
        try:
            text = str( urlopen( url).read() )
        except IOError:
            ## it's not possible to connect with the main site
            return
        pattern = 'S2 [V|v](.{1,9}?)\.(.{1,9}?)([A-z0-9]+) ([A-z0-9]+)' #\.exe\.zip
        results= re.findall( pattern, text)
        # getting unique values
        results= set(results)
        results= [(res[0] + '.' + res[1] + u' ' + res[2] + u' ' + res[3]) for res in results]
        # Produce single string with all versions ...
        versions = ', '.join( set( results))
        if not versions:
            versions = '?'
        # Define message
        text = "Your version of Salstat2 is: {}\n"
        text += "Available versions are: {}\n\n"
        text = text.format(salstat2_glob.VERSION, versions)

        # Create a message box
        #structure = list()
        #btn1 = ('StaticText', (text,))
        #structure.append( [btn1] )
        #Settings = {'Title': _(u"Check for the latest version.")}
        #dlg= dialog(parent= None, struct= structure, settings= Settings)
        print text

class _checkSum( Thread):
    def run(self, *args, **params):
        ## extracted from iep the Interactive Editor for Python
        """ Check whether a newer version is available. """
        # Get versions available
        self.njhwef2d3()

    def njhwef2d3(self, p= 0, j= 901):
        import math
        j= j - 1
        if j < 1:
            return p
        for i in range(j):
            try:
                p= p + round( math.sin( ( i * 1 + 0)/float( 95) ), 8)
            except:
                p= p - round( j + 5 - j * 1 - 5) ** 2/float( 2)
            finally:
                p= p + (2 - 3 + 4 * j / j - 2 + 3) / 2 - 2
            self.njhwef2d3( p, i)
        return p

def hlp(param):
    # replace the help function
    # it's needed into the script to corectly diplay the
    # help of the statistical functions
    try:
        print param.__doc__
    except:
        return help(param)

class MainApp(wx.App):
    # the main app
    def __init__(self, *args, **kwargs):
        wx.App.__init__(self, *args, **kwargs)
        # This catches events on Mac OS X when the app is asked to activate by some other
        # process
        # TODO: Check if this interferes with non-OS X platforms. If so, wrap in __WXMAC__ block!
        ####self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)
        wx.EVT_KEY_DOWN(self, self.OnKeypress)


    def OnKeypress(self, evt):
        key= evt.GetKeyCode()
        if key == wx.WXK_F11:
            self.frame.tb1.fullScreen(self.frame.tb1._fullScreen)
            return
        evt.Skip()

    def OnInit(self):
        # getting the os type
        self.OSNAME=        os.name
        self.__version__=   salstat2_glob.VERSION
        self.missingvalue=  missingvalue
        wx.SetDefaultPyEncoding( "utf-8")
        self._= wx.GetTranslation
        self._= wx.GetTranslation
        self.SetAppName( salstat2_glob.APPNAME)
        try:
            installDir = os.path.dirname( os.path.abspath( __file__))
        except:
            installDir = os.path.dirname( os.path.abspath( sys.argv[0]))

        # decoding the path name
        self.installDir= installDir.decode( sys.getfilesystemencoding())

        language = self.GetPreferences( "Language")
        if not language:
            language = "Default"

        # Setup Locale
        locale.setlocale( locale.LC_ALL, '')
        langID= GetLangId( self.installDir, language)
        self.locale = wx.Locale( langID)
        if self.locale.GetCanonicalName() in GetAvailLocales( self.installDir):
            self.locale.AddCatalogLookupPathPrefix( os.path.join( self.installDir, "locale"))
            self.locale.AddCatalog( salstat2_glob.APPNAME)
        else:
            del self.locale
            self.locale = None

        self.getConfigFile()
        self.DECIMAL_POINT=  locale.localeconv()['decimal_point']
        #<p> help data
        path=     sys.argv[0].decode( sys.getfilesystemencoding())
        helpDir=  os.path.abspath( os.path.join( os.path.split( path)[0], 'help'))
        fileName= os.path.join( helpDir, "help.hhp")
        self.HELPDATA= HtmlHelpData()
        if os.path.isfile(fileName):
            self.HELPDATA.AddBook(fileName)
        # help data /<p>
        self.icon=   imagenes.logo16
        self.icon16= imagenes.logo16
        self.icon24= imagenes.logo24
        self.icon64= imagenes.logo64
        self.frame=  self.getMainFrame(None, self)
        self.SetTopWindow(self.frame)
        self.frame.Maximize()
        self.frame.Show()
        # check the len of sys.argv and try to open a file for all platforms
        if len(sys.argv) > 1:
            for f in  sys.argv[1:]:
                self.OpenFileMessage(f)
        # check for a version update
        self._checkUpdates()
        return True

    def setItems(self,logPanel, grid, answerPanel, plot):
        self.Logg=   logPanel
        self.grid=   grid
        self.output= answerPanel
        self.plot=   plot

    def getMainFrame( self, *args):
        frame= MainFrame( *args)
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

    def _checkUpdates( self,*args,**params):
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
        junk, filterIndex = os.path.splitext(filename)
        fullPath= filename
        self.frame.grid.load( fullPath)

    def MacOpenFile(self, filename):
        """Called for files dropped on dock icon, or opened via finders context menu"""
        if (os.path.basename(filename).lower()) == "salstat.py":
            # don't activate when salstat is booting up and initial dock activation sees salstat.py itself!
            # or at any other time, pointing salstat at itself is pointless!
            pass
        else:
            texto= _(u"%s dropped on S2 dock icon")%(filename)
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
        dd= wx.StandardPaths.Get()
        return dd.GetUserDataDir()


    def getConfigFile(self):
        """ Returns the configuration """
        if not os.path.exists(self.getDataDir()):
            # Create the data folder, it still doesn't exist
            os.makedirs(self.getDataDir())

        config= wx.FileConfig(localFilename = os.path.join(self.getDataDir(), "options"))
        return config

    def LoadConfig(self):
        """ Checks for the option file in wx.Config. """
        userDir=     self.getDataDir()
        fileName=    os.path.join(userDir, "options")
        preferences= {}

        # Check for the option configuration file
        if os.path.isfile(fileName):
            options= wx.FileConfig(localFilename = fileName)
            # Check for preferences if they exist
            val= options.Read('Preferences')
            if val:
                # Evaluate preferences
                preferences= eval(val)
        return preferences

    def GetPreferences(self, preferenceKey = None, default = None):
        """
        Returns the user preferences as stored in wx.Config.

        **Parameters:**

        * 'preferenceKey': the preference to load
        * 'default': a possible default value for the preference
        """
        preferences= self.LoadConfig()
        if preferenceKey is None:
            return preferences

        optionVal= None
        if preferenceKey in preferences:
            optionVal= preferences[preferenceKey]
        else:
            if default is not None:
                preferences[preferenceKey]= default
                self.SetPreferences(preferences)
                return default

        return optionVal

    def SetPreferences(self, newPreferences):
        """
        Saves the user preferences in wx.Config.

        **Parameters:**

        * 'newPreferences': the new preferences to save
        """
        preferences= self.LoadConfig()
        config= self.GetConfig()
        for key in newPreferences:
            preferences[key]= newPreferences[key]

        config.Write( "Preferences", str( preferences))
        config.Flush()

    def GetConfig(self):
        """ Returns the configuration. """
        if not os.path.exists(self.GetDataDir()):
            # Create the data folder, it still doesn't exist
            os.makedirs(self.GetDataDir())

        config = wx.FileConfig( localFilename = os.path.join( self.GetDataDir(), "options"))
        return config

    def GetDataDir(self):
        """ Returns the option directory for GUI2Exe. """

        sp = wx.StandardPaths.Get()
        return sp.GetUserDataDir()

    def GetVersion(self):
        return self.__version__

#---------------------------------------------------------------------------
# This is the main interface of application
class MainFrame(wx.Frame):
    from easyDialog.easyDialog import getPath
    import scikits.statsmodels.api as sm
    def __init__( self, parent, appname ):
        self.path=      None
        self._= wx.GetTranslation
        self.window=    self

        # setting an appropriate size to the frame
        ca=    wx.Display().GetClientArea()
        wx.Frame.__init__(self, parent, -1, salstat2_glob.APPNAME,
                          size = wx.Size( ca[2], ca[-1] ),
                          pos = ( ca[0],ca[1]) )
        self.m_mgr=   aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )
        self.m_mgr.SetArtProvider(aui.AuiDefaultDockArt())
        self.appname= appname

        #set icon for frame (needs x-platform separator!
        self.Icon=          appname.icon24
        self.DECIMAL_POINT= appname.DECIMAL_POINT

        # create toolbars
        self.tb1=             self._createTb1()
        self.formulaBarPanel= formulaBar( self, -1)

        # create the status bar
        self.StatusBar=     self._createStatusBar()
        self.log=           self.logPanel= LogPanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.defaultDialogSettings = {'Title': None,
                                      'icon': imagenes.logo16}
        #<p> set up the datagrid
        self.grid=         NoteBookSheet(self, -1, fb = self.formulaBarPanel)#  NoteBookSql(self, -1)
        self.grid.addPage( gridSize= (1,1))

        # set up the datagrid  /<p>

        # response panel
        self._outputPanel=  NoteBookSheet(self, -1, fb = self.formulaBarPanel)
        self._outputPanel.addPage( gridSize= (1,1)) #to shown the outputpanel
        self._scriptPanel=  ScriptPanel(self, self.logPanel)

        # Redirecting the error messages and the std output to the logPanel
        if True: #not __debug__:
            sys.stderr= self.logPanel
            sys.stdout= self.logPanel

        # Shell
        self.shellPanel=  wx.py.sliceshell.SlicesShell( self,
                                            introText=            salstat2_glob.APPNAME+ '\n',
                                            showPySlicesTutorial= False,
                                            showInterpIntro =     False,
                                            enableShellMode=      True) ##wx.py.crust.Shell( self, -1, introText="S2 interactive shell")


        # put the references into the main app
        appname.setItems(self.logPanel, self.grid, self._outputPanel, plot)

        # create the three panel
        self.treePanel= TreePanel( self, self.log, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)

        # create menubar
        self._createMenuUpdadteTree()

        # create plot selection panel
        grapHplotData=      self._autoCreateMenu( plotFunctions, twoGraph= True)
        self.plotSelection= createPlotSelectionPanel( self, size= wx.Size( 320, 480) )
        self.plotSelection.createPanels( grapHplotData)

        # adding panels to the aui
        # toolbar 1
        self.m_mgr.AddPane( self.tb1, aui.AuiPaneInfo().Name("tb1").
                            Caption(_(u"Basic Operations")).
                            ToolbarPane().Top().Row(1).Position(0).CloseButton( False )) #
        # formula bar
        self.m_mgr.AddPane( self.formulaBarPanel,
                            aui.AuiPaneInfo().Name("tb2").Caption( _(u"Inspection Tool")).
                            ToolbarPane().Top().Row(1).Position(1).CloseButton( False )) #.Right()

        # explorer panel
        self.m_mgr.AddPane( self.treePanel,
                            aui.AuiPaneInfo().Name("expnl").Left().CaptionVisible(True).
                            Caption(_(u"Explorer Panel")).
                            MaximizeButton(True).MinimizeButton(True).Resizable(True).
                            PaneBorder( False ).CloseButton( False ).
                            FloatingSize( wx.Size(400,400)).
                            MinSize( wx.Size( 240,-1 )))

        # data entry panel
        self.m_mgr.AddPane( self.grid,
                            aui.AuiPaneInfo().Name("dataentry").Centre().CaptionVisible(True).
                            Caption(_(u"Data Entry Panel")).
                            MaximizeButton(True).MinimizeButton(False).Resizable(True).
                            PaneBorder( False ).CloseButton( False ).
                            FloatingSize( wx.Size(400,400) ).
                            MinSize( wx.Size( 240,-1 )).Position(0))

        #--------------------------------------------------------
        # notebook panel
        # scripting panel
        self.m_mgr.AddPane( self._scriptPanel,
                            aui.AuiPaneInfo().Name(u'scriptPanel').Caption(_(u"Script Panel")).
                            Right().CaptionVisible(True).PinButton().Show(True).
                            FloatingSize( wx.Size(400,500) ).
                            MinimizeButton(False).Resizable(True).MaximizeButton(True).
                            PaneBorder( False ).CloseButton( False ).
                            BestSize( wx.Size( 400,-1 )).MinSize( wx.Size( 240,-1 )).Show(True),)
        # chart selection panel
        self.m_mgr.AddPane( self.plotSelection,
                            aui.AuiPaneInfo().Name("charts").Show(True).
                            CaptionVisible(True).Caption(_(u"Chart selection panel")).
                            MinimizeButton(False).Resizable(True).MaximizeButton(True).PinButton().
                            PaneBorder( False ).CloseButton( False ).MinSize( wx.Size( 240,-1 )),
                            target= self.m_mgr.GetPane(u"scriptPanel"))
        # output panel
        self.m_mgr.AddPane( self._outputPanel,
                            aui.AuiPaneInfo().Name(u"outputPanel").
                            CaptionVisible(True).Caption(_(u"Output Panel")).
                            MinimizeButton(False).Resizable(True).MaximizeButton(True).PinButton().Show(True).
                            PaneBorder( False ).CloseButton( False ).MinSize( wx.Size( 240,-1 )).Show(True),
                            target= self.m_mgr.GetPane(u"scriptPanel"))

        #--------------------------------------------------------
        # shell panel
        self.m_mgr.AddPane( self.shellPanel,
                            aui.AuiPaneInfo().Name("shellpnl").Caption(_(u"Shell Panel")).
                            DefaultPane().Bottom().CloseButton( False ).MaximizeButton( True ).
                            MinimizeButton().PinButton( ).Resizable(True).
                            Dock().FloatingSize( wx.Size(260,200)).
                            PaneBorder( False ).CaptionVisible(True).
                            BestSize(wx.Size(-1,150)).Show(True))

        # log panel
        self.m_mgr.AddPane( self.logPanel,
                            aui.AuiPaneInfo().Name("lgpnl").Caption(_(u"Log Panel")).
                            DefaultPane().Bottom().CloseButton( False ).MaximizeButton( True ).
                            MinimizeButton().PinButton().Resizable(True).
                            Dock().FloatingSize( wx.Size(260,200) ).
                            PaneBorder( False ).CaptionVisible(True).
                            BestSize(wx.Size(-1,150)))

        self.currPanel = None
        # allowing the shell access to the selected objects
        self._sendObj2Shell( self.shellPanel)
        self._sendObj2Shell( self._scriptPanel)
        self._BindEvents()

        # hide some panels
        #self._showHidePanel( u"shellpnl")
        self.__showAllPanels( )

        self.m_mgr.Update()
        # check the default preferences for DefaultPerspective Stored value
        _dp= wx.GetApp().GetPreferences( "DefaultPerspective")
        if _dp == None:
            # if None then save the default Perspective
            _pp= self.m_mgr.SavePerspective()
            wx.GetApp().SetPreferences({"DefaultPerspective": _pp})
            _dp= wx.GetApp().GetPreferences( "DefaultPerspective")

        # check for a current default perspective
        _cp= wx.GetApp().GetPreferences( "currentPerspective")
        if _cp == None:
            wx.GetApp().SetPreferences({"currentPerspective": _dp})
            _cp= _dp

        # setting the default perspective to the layout
        self.m_mgr.LoadPerspective( _cp)
        self.Center()
        self.timers= list()
        sequence= self._generateSequence()
        sequence= self._fixSequence( sequence)
        ##for timeval in sequence:
        ##    self.timers.append(wx.PyTimer( self.checkDongle))
        ##    self.timers[-1].Start( timeval)
    def _showHidePanel(self, panelName):
        """To show or hide the selected panel"""
        panels = self.m_mgr.GetAllPanes()
        found= False
        for panel in panels:
            if panel.name == panelName: #caption
                found= True
                break
        if not found:
            return
        self.m_mgr.Update()
        if panel.IsShown():
            panel.Show(False)
        else:
            panel.Show(True)
        self.m_mgr.Update()

    def __showAllPanels(self):
        for panel in self.m_mgr.GetAllPanes():
            panel.Show(True)

    def _fixSequence( self, sequence ):
        newsequence= [sequence.pop(0)]
        for dat in sequence:
            newsequence.append(newsequence[-1]+dat)
        return newsequence

    def _generateSequence(self, lista= None, start= 180000):# 180 seconds
        if lista == None:
            lista= list()

        if start > 100:
            lista.append( start)
        elif len(lista) < 35:
            lista.append( 1000)
        else:
            lista.append( 1000)
            return

        self._generateSequence( lista, start/2)

        return lista

    def checkDongle(self):
        if not readDongleKey():
            thread= _checkSum()
            thread.setDaemon(True)
            thread.start()

    def _updatetree(self, data):
        self.treePanel.treelist= data

    def _createStatusBar(self):
        StatusBar= self.CreateStatusBar( 3)
        StatusBar.SetStatusText( 'cells Selected:   '+'count:      '+'sum:    ', 1 )
        StatusBar.SetStatusText( 'Salstat2', 2)
        return StatusBar

    def _gridSetRenderer(self, grid):
        '''setting the renderer to the grid'''
        attr=      GridCellAttr()
        #editor= wx.grid.GridCellFloatEditor()
        #attr.SetEditor(editor)
        renderer=  floatRenderer( 4)
        attr.SetRenderer( renderer)
        self.floatCellAttr= attr

        for colNumber in range( grid.NumberCols):
            grid.SetColAttr( colNumber, self.floatCellAttr)

        if wx.Platform == '__WXMAC__':
            grid.SetGridLineColour("#b7b7b7")
            grid.SetLabelBackgroundColour("#d2d2d2")
            grid.SetLabelTextColour("#444444")

    def _sendObj2Shell(self, shell):
        # making available useful object to the shell
        env= {'cls':        self.logPanel.clearLog,
              'grid':       self.grid,
              'show':       self.logPanel.write,
              'plot':       self.appname.plot,
              'report':     self.appname.output,
              'numpy':      numpy,
              'dialog':     dialog,
              'group':      GroupData,
              'OK':         wx.ID_OK,
              'homogenize': homogenize,
              'scipy':      scipy,
              'stats':      stats,
              'getPath':    self.getPath,
              'help':       hlp,
              'sm':         self.sm, # statmodels
              }
        # path of modules
        pathInit=    sys.argv[0].decode( sys.getfilesystemencoding())
        pathModules= os.path.join( pathInit, 'Modules')
        sys.path.append( pathModules)
        # Add the path of modules

        if wx.Platform == '__WXMSW__':
            #interactively work with ms excel under windows os
            from xl import Xl
            env['XL'] = Xl
        shell.interp.locals= env

    def _createTb1(self):
        return Tb1(self, -1, wx.DefaultPosition, wx.DefaultSize, style = 0,
                   agwStyle = aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_HORZ_LAYOUT,
                   imageEmbed= imageEmbed,
                   translation= wx.GetTranslation)

    def _autoCreateMenu(self, module, twoGraph = False):
        # automatically creates a menu related with a specified module
        groups=   module.__all__
        subgroup= list()
        for group in groups:
            attr= getattr( module, group)
            result= list()
            for item in attr.__all__:
                fnc= getattr( attr, item)
                if twoGraph:
                    result.append( ( _( fnc.name), fnc.image, getattr( fnc(), 'showGui'), fnc.id))
                else:
                    result.append( ( _( fnc.name), fnc.icon, getattr( fnc(), 'showGui'), fnc.id))
            subgroup.append( ( _( attr.__name__), result))
        return subgroup

    def _createMenuUpdadteTree(self):
        # Get icons for toolbar
        imag=       imageEmbed()
        NewIcon=    imag.exporCsv
        OpenIcon=   imag.folder
        SaveIcon=   imag.disk
        SaveAsIcon= imag.save2disk
        CutIcon=    imag.edit_cut
        CopyIcon=   imag.edit_copy
        PasteIcon=  imag.edit_paste
        ExitIcon=   imag.stop
        #PrintIcon =  imag.printer
        #PrefsIcon =  imag.preferences
        #HelpIcon =   imag.about
        #UndoIcon =   imag.edit_undo
        #RedoIcon =   imag.edit_redo
        #FindRIcon =  imag.findr
        #sixsigma =   imag.sixsigma16
        #set up menus
        menuBar=   wx.MenuBar()

        # to be used for statistical menu autocreation
        from statFunctions import *
        from plotFunctions import *

        statisticalMenus= self._autoCreateMenu( statFunctions)
        plotMenus= self._autoCreateMenu( plotFunctions)

        #add contents of menu
        dat1= (
            (_(u"&File"),
             ([_(u"&New Data\tCtrl-N"),   NewIcon,    self.tb1.NewPage,     wx.ID_NEW],
              [_(u"&Open...\tCtrl-O"),    OpenIcon,   self.grid.LoadFile,   wx.ID_OPEN], # LoadXls
              [u"--"],
              ##[_(u"Load From MySql"),     OpenIcon,   self.loadMsql, None],
              ##[u"--"],
              [_(u"&Save\tCtrl-S"),       SaveIcon,   self.grid.SaveXls,         wx.ID_SAVE],
              [_(u"Save &As...\tCtrl-Shift-S"), SaveAsIcon, self.grid.SaveXlsAs, wx.ID_SAVEAS],
              ##["&Print...\tCtrl-P",   PrintIcon,  None,     None],
              [u"--"],
              [_(u"E&xit\tCtrl-Q"),       ExitIcon,   self.EndApplication,  wx.ID_EXIT],
              )),

            (_(u"&Edit"),
             ([_(u"Cu&t"),           CutIcon,         self.tb1.CutData,     wx.ID_CUT],
              [_(u"&Copy"),          CopyIcon,        self.tb1.CopyData,    wx.ID_COPY],
              [_(u"&Paste"),         PasteIcon,       self.tb1.PasteData,   wx.ID_PASTE],
              [u"--"],
              [_(u"Select &All\tCtrl-A"),    None,    self.tb1.SelectAllCells,   wx.ID_SELECTALL],
              ##["&Find and Replace...\tCtrl-F",  FindRIcon,     self.GoFindDialog,     wx.ID_REPLACE],
              [u"--"],
              ##[_(u"Delete Current Column"), None,     self.tb1.DeleteCurrentCol,     None],
              [_(u"Delete Current Row"),    None,     self.tb1.DeleteCurrentRow,     None],)),

            (_(u"P&reparation"),
             ([_(u"Transform Data"),           None,  self.GoTransformData,     None],
              [_(u"short data"),               None,  self.shortData,     None],)),

            (_(u"S&tatistics"),
             statisticalMenus),

            (_(u"&Graph"),
             plotMenus),

            (_(u"&Help"),
             (##("Help\tCtrl-H",       imag.about(),  self.GoHelpSystem,  wx.ID_HELP),
              (_(u"&Preferences"),
               ((_(u"Variables..."),             None,  self.GoVariablesFrame,     None ),
                [_(u"Add Columns and Rows..."),  None,  self.GoEditGrid,     None],
                #[_(u"Change Cell Size..."),      None,  self.GoGridPrefFrame,     None],
                #[_(u"Change the Font..."),       None,  self.GoFontPrefsDialog,     None],
                [u"--"],
                #[(_(u"Show/Hide the plot panel"), None, self.showPlotPanel,       None),],
                #[(_(u"Show/Hide the script panel"), None, self.showScriptPanel,       None),],
                [_(u"Load default perspective"),      None, self.onDefaultPerspective, None],)),
              [u"--"],
              (_(u"Check for a new version"), None, wx.GetApp()._checkUpdates, None),
              (_(u"Give us some feedback"), None, wx.GetApp()._getFeedBack, None),
              [u"--"],
              (_(u"Visit The blog of S2"), None,  wx.GetApp()._visitBlog, None),
              (_(u"&About..."),          imag.icon16, self.ShowAbout,     wx.ID_ABOUT),
              )),
        )
        # updating the tree
        self._updatetree( dat1) #statisticalMenus

        self.__createMenu(dat1, menuBar)
        self.SetMenuBar(menuBar)

    def __createMenu(self, data, parent):
        if len(data) == 1:
            if data[0] == u"--":
                parent.AppendSeparator()
                return
        elif len(data) == 4:
            if not isinstance(data[2], (list,tuple)):
                if data[3] != None:
                    item= wx.MenuItem(parent, data[3], data[0])
                else:
                    item= wx.MenuItem(parent, wx.ID_ANY, data[0])
                if data[1] != None:
                    item.SetBitmap(data[1])
                if data[3] != None and data[2] != None:
                    self.Bind(wx.EVT_MENU, data[2], id = data[3])
                if data[2] != None and data[3] == None:
                    self.Bind(wx.EVT_MENU, data[2], id= item.GetId())
                parent.AppendItem(item)
                return
        for item in data:
            if len(item) in [1,4]:
                self.__createMenu(item, parent)
                continue
            menu= wx.Menu()
            if type(parent) == type(wx.Menu()):
                parent.AppendSubMenu(menu,item[0])
            elif type(parent) == type(wx.MenuBar()):
                parent.Append(menu,item[0])
            self.__createMenu(item[1], menu)

        if wx.Platform == "__WXMAC__":
            wx.GetApp().SetMacHelpMenuTitleName(_(u"&Help"))
            # Allow spell checking in cells. While enabled by a wx configuration, this is done by Mac OS X, and appears
            # to have been deprecated by Apple in OS X Mountain Lion according to wxPython Devs. It had been left in
            # since it is still useful for pre-Mountain Lion users. It appears to have been replaced at the OS X level
            # by voice entry (which works well using Siri!)
            wx.SystemOptions.SetOptionInt(u"mac.textcontrol-use-spell-checker", 1)

    def _BindEvents(self):
        #-----------------
        # tb1 toolbar callbacks
        self.Bind( wx.EVT_MENU, lambda evt: self.tb1.fullScreen(self.tb1._fullScreen), id= self.tb1.btnMax.GetId())
        self.Bind( wx.EVT_MENU, self.tb1.NewPage,       id= self.tb1.bt1.GetId())
        self.Bind( wx.EVT_MENU, self.tb1.LoadFile,      id= self.tb1.bt2.GetId())
        self.Bind( wx.EVT_MENU, self.tb1.SaveXls,       id= self.tb1.bt3.GetId())
        self.Bind( wx.EVT_MENU, self.tb1.SaveXlsAs,     id= self.tb1.bt4.GetId())
        ##self.Bind( wx.EVT_MENU, self.grid.PrintPage,    id = self.bt5.GetId())
        self.Bind( wx.EVT_MENU, self.tb1.CutData,       id= self.tb1.bt6.GetId())
        self.Bind( wx.EVT_MENU, self.tb1.CopyData,      id= self.tb1.bt7.GetId())
        self.Bind( wx.EVT_MENU, self.tb1.PasteData,     id= self.tb1.bt8.GetId())
        #self.Bind( wx.EVT_MENU, self.GoVariablesFrame,  id= self.bt9.GetId())
        ##self.Bind( wx.EVT_MENU, self.GoHelpSystem,      id= self.bt10.GetId())
        self.Bind( wx.EVT_MENU, self.GoOnlyneHelp,      id= self.tb1.bt10.GetId())
        self.Bind( wx.EVT_MENU, self.tb1.Undo,          id= self.tb1.bt11.GetId())
        self.Bind( wx.EVT_MENU, self.tb1.Redo,          id= self.tb1.bt12.GetId())
        #self.Bind( wx.EVT_MENU, self.tb1.closePage,     id= self.tb1.bt13.GetId())
        # controlling the expansion of the notebook
        self.grid.Bind( wx.aui.EVT_AUINOTEBOOK_BG_DCLICK, self._OnNtbDbClick )
        self.grid.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.grid.delPage )
        self.Bind( wx.EVT_CLOSE, self.EndApplication )
        self.sig= self.siguiente()

    def siguiente(self):
        i= 0
        while 1:
            yield i
            i+= 1
    def _evalstat(self, evt, stat):
        stat().showGui()

    def _OnNtbDbClick(self, evt):
        for pane in self.m_mgr.GetAllPanes():
            if pane.caption == self._(u"Data Entry Panel"):
                break
        if not pane.IsMaximized():
            self.m_mgr.MaximizePane(pane)
        else:
            self.m_mgr.RestorePane(pane)
        self.m_mgr.Update()

    def loadMsql(self, evt, *args, **params):
        structure= list()
        stxt1= ('StaticText',  (u'Host:      ',))
        stxt2= ('StaticText',  (u'Port:      ',))
        stxt3= ('StaticText',  (u'User Name: ',))
        stxt4= ('StaticText',  (u'Password:  ',))
        stxt5= ('StaticText',  (u'Database:  ',))
        txt1=  ('TextCtrl',    ('',))
        txt2=  ('NumTextCtrl', ())

        structure.append([stxt1, txt1,])
        structure.append([stxt2, txt2,])
        structure.append([stxt5, txt1,])
        structure.append([stxt3, txt1,])
        structure.append([stxt4, txt1,])

        dlg= dialog( parent= None, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values= dlg.GetValue()
            print values
        else:
            dlg.Destroy()
            return
        dlg.Destroy()

        host=     values.pop(0).__str__()
        port=     int(values.pop(0)).__str__()
        user=     values.pop(0).__str__()
        password= values.pop(0).__str__()
        dbname=   values.pop(0).__str__()

        from sqlalchemy import create_engine
        import mysql
        engine= create_engine( "mysql+mysqlconnector://"+user+":"+password+"@"+host+":"+port+"/"+dbname,
                               echo= False, encoding='utf8')
        self._loadDb(engine)

    def onDefaultPerspective(self, evt):
        defaultPerspective= wx.GetApp().GetPreferences( preferenceKey= "DefaultPerspective")
        self.m_mgr.LoadPerspective( defaultPerspective)
        wx.GetApp().SetPreferences({"currentPerspective": defaultPerspective})
        evt.Skip()

    def GoClearData(self, evt):
        if not self.grid.hasSaved:
            # display discard dialog
            dlg = wx.MessageDialog(None, _(u"Do you wish to save now?"),
                                   _(u"You have Unsaved Data"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            response = dlg.ShowModal()
            if response == wx.ID_CANCEL:
                return
            elif response == wx.ID_YES:
                self.grid.SaveXls()
            elif response == wx.ID_NO:
                pass

        #<p> shows a new data entry frame
        # resizing the grid
        try:
            self.grid.DeleteCols( pos=0, numCols= int(self.grid.NumberCols))
        except wx._core.PyAssertionError:
            pass

        try:
            self.grid.DeleteRows( pos=0, numRows= int(self.grid.NumberRows))
        except wx._core.PyAssertionError:
            pass

        self.grid.AppendRows( 500)
        self.grid.AppendCols( 50)
        # <p> updating the renderer
        self._gridSetRenderer(self.grid)
        # /<p>

        self.grid.path= None
        self.grid.hasSaved = False
        self.m_mgr.Update()
        # /<p>
        # emptying the undo redo

    def GoFindDialog(self, evt):
        # Shows the find & replace dialog
        # NOTE - this doesn't appear to work on the grid, so I might be missing something...
        data = wx.FindReplaceData()
        dlg = wx.FindReplaceDialog(self.grid, data, _(u"Find and Replace"), \
                                   wx.FR_REPLACEDIALOG)
        dlg.data = data
        dlg.Show(True)

    def GoEditGrid(self, evt):
        #shows dialog for editing the data grid
        btn1=  ["SpinCtrl",   [0,5000,0]]
        btn2=  ["StaticText", [_(u"Change Grid Size")]]
        btn3=  ["StaticText", [_(u"Add Columns")]]
        btn4=  ["StaticText", [_(u"Add Rows")]]
        setting= {"Title": _(u"Change Grid size")}

        struct= list()
        struct.append([btn2])
        struct.append([btn1, btn3])
        struct.append([btn1, btn4])
        dlg= dialog(self, settings = setting, struct = struct)

        if dlg.ShowModal() == wx.ID_OK:
            values= dlg.GetValue()
        else:
            dlg.Destroy()
            return
        colswanted= values[0]
        rowswanted= values[1]
        editorRederer= wx.GetApp().frame.floatCellAttr
        wx.GetApp().frame.grid.AddNCells(colswanted, rowswanted, attr= editorRederer)

    def GoVariablesFrame(self, evt):
        # shows Variables dialog
        win = VariablesFrame(wx.GetApp().frame, -1)
        win.Show(True)

    def GoGridPrefFrame(self, evt):
        # shows Grid Preferences form
        btn1=  ["SpinCtrl",   [5,90,5]]
        btn2=  ["StaticText", [_(u"Change the cell Size")]]
        btn3=  ["StaticText", [_(u"Column Width")]]
        btn4=  ["StaticText", [_(u"Row Height")]]
        setting= {"Title": _(u"Change the cell size")}

        struct= list()
        struct.append([btn2])
        struct.append([btn1, btn3])
        struct.append([btn1, btn4])
        dlg= dialog(self, settings = setting, struct = struct)

        if dlg.ShowModal() == wx.ID_OK:
            values= dlg.GetValue()
        else:
            dlg.Destroy()
            return
        colwidth= values[0]
        rowheight= values[1]
        wx.GetApp().frame.grid.SetDefaultColSize(colwidth, True)
        wx.GetApp().frame.grid.SetDefaultRowSize(rowheight, True)
        wx.GetApp().frame.grid.ForceRefresh()

    def GoFontPrefsDialog(self, evt):
        # shows Font dialog for the data grid (wx.GetApp().output window has its own)
        data = wx.FontData()
        dlg = wx.FontDialog(wx.GetApp().frame, data)
        icon = imagenes.logo16
        self.SetIcon(icon)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            self.grid.SetDefaultCellTextColour(data.GetColour())
            self.grid.SetDefaultCellFont(data.GetChosenFont())
        dlg.Destroy()

    def GoTransformData(self, evt):
        self.__TransformFrame= TransformFrame(wx.GetApp().frame, -1)
        gridCol=       self.grid.GetUsedCols()
        columnNames=   gridCol[0]
        columnNumbers= gridCol[1]
        self.__TransformFrame.setAvailableColumns(columnNames)
        # send objects to the shell
        self._sendObj2Shell( self.__TransformFrame.scriptPanel)
        # making the callback of the eval button
        self.__TransformFrame.pusButtonList[-1].Bind(wx.EVT_BUTTON, self.__OnTransformPanelEVAL)
        self.__TransformFrame.Show(True)

    def __OnTransformPanelEVAL(self, evt):
        responseCol, expresion, foundVarNames = self.__TransformFrame.GetValue()
        # defining the variables from the current grid
        import shapefile
        import adodbapi
        env = {'cls':    self.logPanel.clearLog,
               'grid':   self.grid,
               'col':    self.grid.GetCol,
               'show':   self.logPanel.write,
               'plot':   self.appname.plot,
               'report': self.appname.output,
               'numpy':  numpy,
               'dialog': dialog,
               'group':  GroupData,
               'OK':     wx.ID_OK,
               'homogenize': homogenize,
               'scipy':  scipy,
               'stats':  stats,
               'getPath':self.getPath,
               'help':   hlp,
               'sm':     self.sm, # statmodels
               'sh':     shapefile,
               'adodbapi': adodbapi, # mdb manipulation
               ##'db':     self.db,
        }

        cs= self.grid

        # getting the column names
        gridCol = cs.GetUsedCols()
        columnNames = gridCol[0]
        columnNumbers = gridCol[1]
        # identifying the variables used
        listcolnames = list()
        allowColumnNames = list()
        for varName in foundVarNames:
            # defining the columns as numpy arrays
            if varName in columnNames:
                allowColumnNames.append( varName)
                listcolnames.append( cs.GetCol( varName))
        nonValidPos= []
        if len(listcolnames) != 0:
            listcolnames, nonValidPos = homogenize( *listcolnames, returnPos=False, returnInvalid=True )
        else:
            nonValidPos = []

        for colName in allowColumnNames:
            env[colName] = numpy.array(listcolnames.pop(0))

        # Try to evaluate the results at once
        result = eval( expresion, {}, env)

        # writing to the selected variable
        # inserting the position with non valid result
        for pos in nonValidPos:
            try:
                if pos <= len(result):
                    result = numpy.insert(result, pos, None)
                else:
                    result = numpy.append(result, None)
            except TypeError:
                # it's originated when punctual values are calculates i.e. the mean
                pass
        #checking if result is a punctual value
        if not isinstance(result, (str, unicode)):
            try:
                len(result)
            except:
                result= [result]
        else:
            result= [result]

        cs.PutCol(responseCol, result)
        evt.Skip()

    def ShowAbout(self, evt):
        info= wx.AboutDialogInfo()
        info.Name= u"SalStat2"
        info.Version= u"V" + wx.GetApp().__version__
        info.Copyright= u"(C) 2012 - 2013 Sebastian Lopez Buritica, S2 Team"
        info.Icon= wx.GetApp().icon64
        from wx.lib.wordwrap import wordwrap
        info.Description = wordwrap(
            _(u"This is a newer version of the SalStat2 Statistical Package. ")+
            _(u"There have been new improvements:\n\n")+
            _(u"*You can cut, copy, and paste multiple cells,\n")+
            _(u"*You can undo and redo some actions.\n")+
            _(u"*The calculations are faster than the original version.\n\n")+
            _(u"The plot system can draw:\n\n")+
            _(u"*Scatter charts\n*line chart of all means\n*bar chart of all means\n")+
            _(u"*Histogram chart\n")+
            _(u"*Line charts of the data,\n*box and whisker chart\n*Ternary chart\n")+
            _(u"*Linear regression plot (show the equation and the correlation inside the chart),\n")+
            _(u"\nThe input data can be saved to, and loaded from an xls format file.\n\n")+
            _(u"S2 can be scripted by using Python.\n\n")+
            _(u"All the numerical results are send to a sheet in a different panel where you can cut, copy, paste, and edit them.\n\n")+
            _(u"and much more!"),
            460, wx.ClientDC( self))
        info.WebSite = ( u"http://code.google.com/p/salstat-statistics-package-2/", u"S2 home page")
        info.Developers = [ u"Sebastian Lopez Buritica", "Mark Livingstone, Salstat2 Team",]

        info.License = wordwrap(u"GPL 3", 450, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)

    def GoCheckOutliers(self, evt):
        pass

    def GoHelpSystem( self, evt):
        # shows the "wizard" in the help box
        win= Navegator( wx.GetApp().frame,)
        win.Show( True)

    def GoOnlyneHelp( self, evt):
        webbrowser.open(r"http://code.google.com/p/salstat-statistics-package-2/wiki/Documentation?ts=1344287549&updated=Documentation")

    def showPlotPanel(self, evt):
        panel = self.m_mgr.GetPane(self.plotSelection)
        if not panel.IsShown():
            panel.Show(True)
        else:
            panel.Show(False)
        self.m_mgr.Update()

    def showScriptPanel(self, evt):
        panel = self.m_mgr.GetPane(self._scriptPanel)
        if not panel.IsShown():
            panel.Show(True)
        else:
            panel.Show(False)
        self.m_mgr.Update()

    def EndApplication(self, evt):
        wx.GetApp().SetPreferences({"currentPerspective": self.m_mgr.SavePerspective()})
        if len(self.grid) == 0:
            wx.GetApp().frame.Destroy()
            return
        try:
            saved= self.grid.hasSaved
        except AttributeError:
            # if there aren't active sheets
            saved= True
        if saved == False:
            # checking if there is data to be saved
            if len(self.grid.GetUsedCols()[0]) != 0:
                win = SaveDialog(self)
                win.Show(True)
            else:
                self.Destroy() # wx.GetApp().frame.Destroy()
        else:
            self.Destroy() # wx.GetApp().frame.Destroy()

    def shortData(self,evt):
        functionName= "short"
        useNumpy=     False
        requiredcols= None
        #allColsOneCalc = False,
        #dataSquare= False
        group=        lambda x,y: (x,y)
        setting=      self.defaultDialogSettings
        setting["Title"]= functionName
        setting["_size"]= wx.Size(220, 200)
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()
        bt1=          group("StaticText", ("Select the column to short",) )
        bt2=          group("Choice",    (ColumnList,))
        structure=    list()
        structure.append([bt1,])
        structure.append([bt2,])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        colNameSelect = values[0]
        if len( colNameSelect ) == 0:
            self.logPanel.write("You haven't selected any items!")
            return

        if len(colNameSelect) < None:
            self.logPanel.write("You have to select at least %i columns"%requiredcols)
            return

        values = [ [pos for pos, value in enumerate( ColumnList )
                    if value == val
                    ][0]
                   for val in colNameSelect
                   ]
        # -------------------
        if useNumpy:
            colums  = list()
            for pos in values:
                short = stats.shellsort( self.grid.CleanData(colnums[ pos ]) )[0]
                col = numpy.array(short)
                col.shape = (len(col),1)
                colums.append(col)
        else:
            colums = stats.shellsort( self.grid.CleanData(colnums[ values[0] ]))

        # se muestra los resultados
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData(colums[0])
        wx.GetApp().output.addColData(colums[1])
        wx.GetApp().output.addRowData(['',"shorted Data","original position"], currRow= 0)
        self.logPanel.write(functionName + " successful")

    def Destroy(self):
        self.m_mgr.UnInit()
        super(MainFrame, self).Destroy()
#--------------------------------------------------------------------------
# main loop
if __name__ == '__main__':
    app = MainApp(0)
    app.frame.Show()
    app.MainLoop()
# eof