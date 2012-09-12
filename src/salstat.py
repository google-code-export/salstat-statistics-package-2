#!/usr/bin/env python

""" Copyright 2012 Sebastian Lopez Buritica, S2 Team,  licensed under GPL 3

SalStat Statistics Package. Copyright 2002 Alan James Salmoni. Licensed
under the GNU General Public License (GPL 2) """

import wx
import os
import sys
import wx.grid

# -----------------
# to use the sash
# import  wx.lib.multisash as sash
# import  wx.gizmos as gizmos
# -----------------

import wx.html
import wx.lib.agw.aui as aui

if wx.Platform != '__WXMSW__':
    # -----------------
    # these imports just for py2app
    import wx.lib.agw.aui.aui_constants
    import wx.lib.agw.aui.aui_utilities
    import wx.lib.agw.aui.auibar
    import wx.py.buffer
    import wx.py.crust
    #import wx.py.crustslices
    import matplotlib.tri.triangulation
    import matplotlib.delaunay.triangulate
    import matplotlib.tri.tricontour
    import matplotlib.tri.tripcolor
    import matplotlib.projections.geo
    import matplotlib.projections.polar
    import matplotlib.backends.backend_macosx
    import matplotlib.backends._macosx
    
    # -----------------

import webbrowser # online Help

import wx.lib.wxpTag
import string, os, os.path

import numpy
import wx.py
import traceback

# translation module
import locale
import glob
# system of graphics
from plotFrame import MpltFrame as plot
from ntbSheet import NoteBookSheet, SimpleGrid

from slbTools import  homogenize, GroupData # GroupData is used to treat data a a pivot table 
from easyDialog import Dialog as dialog
from statlib import stats

from script import ScriptPanel
from imagenes import imageEmbed

from helpSystem import Navegator

from dialogs import SaveDialog, VariablesFrame, DescriptivesFrame
from dialogs import TransformFrame
from dialogs import createPlotSelectionPanel

from gridCellRenderers import floatRenderer #, AutoWrapStringRenderer
from wx.combo import BitmapComboBox # translation control
import wx.lib.langlistctrl as langlist

import statsmodels.api as sm
import scipy

import plotFunctions
import statFunctions

APPNAME= 'S2'

inits ={}    # dictionary to hold the config values
ColsUsed= []
RowsUsed= []
missingvalue= None
HOME= os.getcwd()
imagenes = imageEmbed()

# Define the translation class
class translate(unicode):
    def __new__(cls, original=''):
        new = unicode.__new__(cls, wx.GetTranslation( original ))
        new.original = original
        return new

if wx.Platform == '__WXMSW__':
    # for windows OS
    face1 = 'Courier New'
    face2 = 'Times New Roman'
    face3 = 'Courier New'
    fontsizes = [7,8,10,12,16,22,30]
    pb = 12
    wind = 50
    DOCDIR = 'c:\My Documents'
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
        if writem:
            texto= str( ">> ")
        texto+= lineaTexto + "\n"
        # se escribe el texto indicado
        self.log.AppendText(texto)

    def write(self, obj, writem= True):
        if isinstance(obj, (str, unicode)):
            lineaTexto= obj
        else:
            lineaTexto= obj.__str__()
        if lineaTexto.endswith('\n'):
            lineaTexto= lineaTexto[:-1]
        self.writeLine(lineaTexto, writem)

    def clearLog(self):
        self.log.SetValue('')

    def __del__( self ):
        pass

#---------------------------------------------------------------------------
# class to wx.GetApp().output the results of several "descriptives" in one table
#---------------------------------------------------------------------------
# grid preferences - set row & col sizes
def GridPrefs(parent):
#shows dialog for editing the data grid
    btn1=  ['SpinCtrl',   [0,5000,0]]
    btn2=  ['StaticText', [translate(u"Change the cell Size")]]
    btn3=  ['StaticText', [translate(u"Column Width")]]
    btn4=  ['StaticText', [translate(u"Row Height")]]
    setting= {'Title': translate(u"Change the cell size")}

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
class formulaBar ( wx.Panel ):

    def __init__( self, parent , *args,**params):
        wx.Panel.__init__ ( self, parent, *args, **params)

        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
        self.m_textCtrl1 = wx.TextCtrl( self, wx.ID_ANY,
                                        wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                        wx.TE_CHARWRAP|wx.TE_MULTILINE|wx.TE_RICH2|
                                        wx.TE_WORDWRAP ) #|wx.NO_BORDER

        self.m_textCtrl1.SetMinSize( wx.Size( 220,25 ) )
        bSizer1.Add( self.m_textCtrl1, 0, 0, 5 )
        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )

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
        
        lang_ids = GetLocaleDict( GetAvailLocales( wx.GetApp().installDir)).values()
        lang_items = langlist.CreateLanguagesResourceLists( langlist.LC_ONLY, \
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
        the_path = os.path.join(path, "LC_MESSAGES", "S2.mo")
        if os.path.exists(the_path):
            avail_loc.append(os.path.basename(path))
    return avail_loc

class SalStat2App(wx.App):
    # the main app
    def __init__(self, *args, **kwargs):
        wx.App.__init__(self, *args, **kwargs)

        # This catches events on Mac OS X when the app is asked to activate by some other
        # process
        # TODO: Check if this interferes with non-OS X platforms. If so, wrap in __WXMAC__ block!
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)

    def OnInit(self):
        # getting the os type
        self.OSNAME = os.name
        self.VERSION= '2.1 beta 3'
        self.missingvalue= missingvalue
        wx.SetDefaultPyEncoding( "utf-8")
        self.translate= translate
        self.SetAppName( APPNAME)
        try:
            installDir = os.path.dirname( os.path.abspath( __file__))
        except:
            installDir = os.path.dirname( os.path.abspath( sys.argv[0]))
        self.installDir= installDir # to be used in the nice bar plot
        
        language = self.GetPreferences( "Language")
        if not language:
            language = "Default"
            
        # Setup Locale
        locale.setlocale( locale.LC_ALL, '')
        self.locale = wx.Locale( GetLangId( installDir, language))
        if self.locale.GetCanonicalName() in GetAvailLocales( installDir):
            self.locale.AddCatalogLookupPathPrefix( os.path.join( installDir, "locale"))
            self.locale.AddCatalog( APPNAME)
        else:
            del self.locale
            self.locale = None

        self.getConfigFile()
        self.DECIMAL_POINT=  locale.localeconv()['decimal_point']
        #<p> help data
        from wx.html import HtmlHelpData
        path= os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], 'help'))
        fileName= os.path.join(path, "help.hhp")
        self.HELPDATA= HtmlHelpData()
        if os.path.isfile(fileName):
            self.HELPDATA.AddBook(fileName)
        # help data /<p>
        self.icon= imagenes.logo16()
        self.icon16= imagenes.logo16()
        self.icon24= imagenes.logo24()
        self.icon64= imagenes.logo64()
        self.frame = MainFrame(None, self)
        # let the main app known the input Grid
        ### self.inputGrid = self.frame.grid
        self.SetTopWindow(self.frame)
        self.frame.grid.SetFocus()
        ###self.Logg= self.frame.logPanel
        ###self.output = self.frame.answerPanel
        # referencing the plot system
        
        if wx.Platform == '__WXGTK__':
            self.frame.Show()
        elif wx.Platform == '__WXMSW__' :
            self.frame.ShowFullScreen(True,False)
        else:   # mac platform
            self.frame.Maximize()
            self.frame.Show()
            for f in  sys.argv[1:]:
                self.OpenFileMessage(f)
        return True

    def BringWindowToFront(self):
        try: # it's possible for this event to come when the frame is closed
            wx.GetApp().GetTopWindow().Raise()
        except:
            pass

    def OnActivate(self, event):
        # if this is an activate event, rather than something else, like iconize.
        if event.GetActive():
            self.BringWindowToFront()
        event.Skip()

    def OpenFileMessage(self, filename):
        self.BringWindowToFront()
        filterIndex = filename[len(filename)-3:len(filename)]
        fullPath=filename
        if not filename.endswith(filterIndex):
            fullPath+= '.' + filterIndex
        if filterIndex == 'xls':
            return self.frame.grid.LoadXls(fullPath)
        elif filterIndex in ('txt', 'csv'):
            return self.frame.grid.loadCsvTxt(fullPath)
        else:
            self.frame.logPanel.write(translate(u"The file %s could not be opened. ")%filename +
                           translate(u"Please check file type and extension!") )

    def MacOpenFile(self, filename):
        """Called for files dropped on dock icon, or opened via finders context menu"""
        self.frame.logPanel.write(translate(u"%s dropped on S2 dock icon")%(filename))
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
        userDir = self.getDataDir()
        fileName = os.path.join(userDir, "options")
        preferences = {}

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

        config.Write("Preferences", str(preferences))
        config.Flush()
        
    def GetConfig(self):
        """ Returns the configuration for GUI2Exe. """
        
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
        return '2.1'

#---------------------------------------------------------------------------
# This is main interface of application
class MainFrame(wx.Frame, wx.FileDropTarget):
    def __init__(self, parent, appname ):
        self.path= None
        # to allow the user to drop allowed files into the Data Entry Panel
        wx.FileDropTarget.__init__( self)
        self.translate= translate
        self.window= self
        wx.Frame.__init__(self,parent,-1,"S2",
                          size = wx.Size(640,480 ), pos = wx.DefaultPosition)

        self.m_mgr= aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )
        self.appname= appname
        #set icon for frame (needs x-platform separator!
        self.Icon= appname.icon24
        self.DECIMAL_POINT= appname.DECIMAL_POINT
        #----------------------
        # create toolbars
        tb1= self._createTb1()
        self.formulaBarPanel= formulaBar( self, wx.ID_ANY)
        #------------------------
        # create small status bar
        self.StatusBar= self.CreateStatusBar( 3)
        self.StatusBar.SetStatusText( 'cells Selected:   '+'count:      '+'sum:    ', 1 )
        self.StatusBar.SetStatusText( 'S2', 2)

        self.m_notebook1= wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.logPanel= LogPanel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.log = self.logPanel # self.log = self.logPanel

        self.defaultDialogSettings = {'Title': None,
                                      'icon': imagenes.logo16()}


        #self.sash = gizmos.DynamicSashWindow(self, -1, style =  wx.CLIP_CHILDREN)
        #--------------------
        #< set up the datagrid
        self.grid= SimpleGrid( self, self.log)
        # let />
        self.grid.hasSaved= True
        self.grid.SetDefaultColSize( 60, True)
        self.grid.SetRowLabelSize( 40)
        self.grid.SetDefaultCellAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTER )
        
        ## adjust the renderer
        self._gridSetRenderer(self.grid)
        #-----------------------

        # response panel
        self.answerPanel= NoteBookSheet(self, fb = self.formulaBarPanel)
        self.answerPanel2= ScriptPanel(self, self.logPanel, self.grid, self.answerPanel)
        #--------------------------------------------
        self.m_notebook1.AddPage( self.logPanel, translate(u"Log"), True )
        # Redurecting the error messages to the logPanel
        sys.stderr= self.logPanel
        sys.stdout= self.logPanel
        self.scriptPanel=  wx.py.crust.Shell( self.m_notebook1) # wx.py.shell.Shell( self.m_notebook1)
        ##self.scriptPanel.stderr= self.logPanel
        
        #self.scriptPanel.wrap( True)
        self.m_notebook1.AddPage( self.scriptPanel , translate(u"Shell"), False )

        # put the references into the main app
        appname.inputGrid= self.grid
        appname.Logg= self.logPanel
        appname.output= self.answerPanel
        appname.plot= plot

        # create menubar
        self._createMenu()
        
        # create plot selection panel
        grapHplotData= self._autoCreateMenu( plotFunctions, twoGraph= True)
        # grapHplotData= [(label, image, callback, id), ]
        self.plotSelection= createPlotSelectionPanel(self, size= wx.Size(320, 480) )
        self.plotSelection.createPanels( grapHplotData)
        #pltFrame.Show(True)
        # grapHplotData= [(label, image, callback, id), ]
        
        #------------------------
        # organizing panels
        self.auiPanels = dict()
        
        self.m_mgr.AddPane( self.formulaBarPanel,
                            aui.AuiPaneInfo().Name("tb2").Caption(translate(u"Inspection Tool")).ToolbarPane().Top().Row(1).
                            Position(1).CloseButton( False ))

        self.m_mgr.AddPane(self.grid,
                           aui.AuiPaneInfo().Centre().
                           CaptionVisible(True).Caption(translate(u"Data Entry Panel")).
                           MaximizeButton(True).MinimizeButton(False).
                           CloseButton( False ).MinSize( wx.Size( 240,-1 )))

        self.m_mgr.AddPane(self.answerPanel,
                           aui.AuiPaneInfo().Centre().Right().
                           CaptionVisible(True).Caption(translate(u"Output Panel")).
                           MinimizeButton(True).Resizable(True).MaximizeButton(True).
                           CloseButton( False ).MinSize( wx.Size( 240,-1 )))

        self.m_mgr.AddPane( tb1, aui.AuiPaneInfo().Name("tb1").Caption(translate(u"Basic Operations")).
                            ToolbarPane().Top().Row(1).CloseButton( False ))

        self.m_mgr.AddPane(self.answerPanel2,
                           aui.AuiPaneInfo().Centre().Right().
                           CaptionVisible(True).Caption((translate(u"Script Panel"))).
                           MinimizeButton().Resizable(True).MaximizeButton(True).
                           CloseButton( False ).MinSize( wx.Size( 240,-1 )))

        self.panelNtb = self.m_mgr.AddPane( self.m_notebook1,
                                            aui.AuiPaneInfo() .Bottom() .
                                            CloseButton( False ).MaximizeButton( True ).
                                            Caption((translate(u"Log / Shell Panel"))).
                                            MinimizeButton().PinButton( False ).
                                            Dock().Resizable().FloatingSize( wx.DefaultSize ).
                                            CaptionVisible(True).
                                            DockFixed( False ).BestSize(wx.Size(-1,150)))
        
        
        self.m_mgr.AddPane(self.plotSelection,
                           aui.AuiPaneInfo().Centre().Left().Show(False).
                           CaptionVisible(True).Caption((translate(u"Plot selection panel"))).
                           MinimizeButton().Resizable(True).MaximizeButton(True).
                           CloseButton( True ).MinSize( wx.Size( 240,-1 )))
        self.currPanel = None
        self._sendObj2Shell(self.scriptPanel)
        self._BindEvents()
        self.m_mgr.Update()
        # Saving the perspective
        self._defaultPerspective= self.m_mgr.SavePerspective()
        self.Center()
        
    def _gridSetRenderer(self, grid):
        '''setting the renderer to the grid'''
        attr=   wx.grid.GridCellAttr()
        #editor= wx.grid.GridCellFloatEditor()
        #attr.SetEditor(editor)
        renderer = floatRenderer( 4)
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
        env= {'grid':       self.grid,
              'show':       self.appname.Logg,
              'plot':       self.appname.plot,
              'report':     self.appname.output,
              'numpy':      numpy,
              'dialog':     dialog,
              'group':      GroupData,
              'OK':         wx.ID_OK,
              'homogenize': homogenize,
              'sm':         sm,
              'scipy':      scipy,
              }
#'stats': self.stats,
#'statistics':statistics,
              
        shell.interp.locals= env
    
    def _createTb1(self):
        # Get icons for toolbar
        imag = imageEmbed()
        NewIcon =    imag.exporCsv()
        OpenIcon =   imag.folder()
        SaveIcon =   imag.disk()
        SaveAsIcon = imag.save2disk()
        PrintIcon =  imag.printer()
        CutIcon =    imag.edit_cut()
        CopyIcon =   imag.edit_copy()
        PasteIcon =  imag.edit_paste()
        PrefsIcon =  imag.preferences()
        HelpIcon =   imag.about()
        UndoIcon =   imag.edit_undo()
        RedoIcon =   imag.edit_redo()

        if wx.version() < "2.9":
            tb1= aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                                style = aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_HORZ_LAYOUT)
        else:
            tb1= aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, style = 0,
                                agwStyle = aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_HORZ_LAYOUT)

        self.bt1 = tb1.AddSimpleTool(10, translate(u"New"),  NewIcon,     translate(u"New"))
        self.bt2 = tb1.AddSimpleTool(20, translate(u"Open"), OpenIcon,    translate(u"Open"))
        self.bt3 = tb1.AddSimpleTool(30, translate(u"Save"), SaveIcon,    translate(u"Save"))
        self.bt4 = tb1.AddSimpleTool(40, translate(u"Save As"), SaveAsIcon, translate(u"Save As"))
        ##self.bt5 = tb1.AddSimpleTool(50, "Print",PrintIcon,"Print")
        tb1.AddSeparator()
        self.bt11= tb1.AddSimpleTool(wx.ID_ANY, translate(u"Undo"), UndoIcon, translate(u"Undo"))
        self.bt12= tb1.AddSimpleTool(wx.ID_ANY, translate(u"Redo"), RedoIcon, translate(u"Redo"))
        tb1.AddSeparator()
        self.bt6 = tb1.AddSimpleTool(60, translate(u"Cut"),  CutIcon, translate(u"Cut"))
        self.bt7 = tb1.AddSimpleTool(70, translate(u"Copy"), CopyIcon, translate(u"Copy"))
        self.bt8 = tb1.AddSimpleTool(80, translate(u"Paste"),PasteIcon, translate(u"Paste"))
        tb1.AddSeparator()
        self.bt9 = tb1.AddSimpleTool(85, translate(u"Preferences"),PrefsIcon, translate(u"Preferences"))
        ##self.bt10= tb1.AddSimpleTool(90, "Help", HelpIcon, "Help")
        self.bt10= tb1.AddSimpleTool(95, translate(u"OnlineHelp"), HelpIcon, translate(u"Online Help"))
        
        # to the languaje
        language = wx.GetApp().GetPreferences( "Language")
        if not language:
            language = "Default"
            
        self.languages= LangListCombo( tb1 , language)
        self.translateBtn= tb1.AddControl( self.languages, label= "Languaje")

        tb1.SetToolBitmapSize( (24,24))
        tb1.Realize()
        
        self.languages.Bind( wx.EVT_COMBOBOX, self._changeLanguaje) # id= self.languages.GetId()
        return tb1
    
    def _changeLanguaje(self, evt):
        allPreferences= dict()
        allPreferences["Language"] = self.languages.GetValue()
        print "you have to restart te app to see the changes"
        wx.GetApp().SetPreferences(allPreferences)

    def _autoCreateMenu(self, module, twoGraph = False):
        # automatically creates a menu related with an specified module
        groups= module.__all__
        subgroup= list()
        for group in groups:
            attr= getattr( module, group)
            result= list()
            for item in attr.__all__:
                fnc= getattr( attr, item)
                if twoGraph:
                    result.append( ( translate( fnc.name), fnc.image, getattr( fnc(), 'showGui'), fnc.id))
                else:
                    result.append( ( translate( fnc.name), fnc.icon, getattr( fnc(), 'showGui'), fnc.id))
            subgroup.append( ( translate( attr.__name__), result))
        return subgroup

    def _createMenu(self):
        # Get icons for toolbar
        imag = imageEmbed()
        NewIcon =    imag.exporCsv()
        OpenIcon =   imag.folder()
        SaveIcon =   imag.disk()
        SaveAsIcon = imag.save2disk()
        PrintIcon =  imag.printer()
        CutIcon =    imag.edit_cut()
        CopyIcon =   imag.edit_copy()
        PasteIcon =  imag.edit_paste()
        PrefsIcon =  imag.preferences()
        HelpIcon =   imag.about()
        UndoIcon =   imag.edit_undo()
        RedoIcon =   imag.edit_redo()
        ExitIcon =   imag.stop()
        FindRIcon =  imag.findr()
        sixsigma =   imag.sixsigma16()
        #set up menus
        menuBar = wx.MenuBar()

        # to be used for statistical menu autocreation
        from statFunctions import *
        from plotFunctions import *
        
        statisticalMenus= self._autoCreateMenu( statFunctions)
        plotMenus= self._autoCreateMenu( plotFunctions)
        #add contents of menu
        dat1= (
            (translate(u"&File"),
             ([translate(u"&New Data\tCtrl-N"),   NewIcon,    self.GoClearData,     wx.ID_NEW],
              [translate(u"&Open...\tCtrl-O"),    OpenIcon,   self.grid.LoadFile,    wx.ID_OPEN], # LoadXls
              [u"--"],
              [translate(u"&Save\tCtrl-S"),       SaveIcon,   self.grid.SaveXls,     wx.ID_SAVE],
              [translate(u"Save &As...\tCtrl-Shift-S"), SaveAsIcon, self.grid.SaveXlsAs,     wx.ID_SAVEAS],
              ##["&Print...\tCtrl-P",   PrintIcon,  None,     None],
              [u"--"],
              [translate(u"E&xit\tCtrl-Q"),       ExitIcon,   self.EndApplication,     wx.ID_EXIT],
              )),
            (translate(u"&Edit"),
             ([translate(u"Cu&t"),           CutIcon,         self.grid.CutData,     wx.ID_CUT],
              [translate(u"&Copy"),          CopyIcon,        self.grid.CopyData,     wx.ID_COPY],
              [translate(u"&Paste"),         PasteIcon,       self.grid.PasteData,     wx.ID_PASTE],
              [u"--"],
              [translate(u"Select &All\tCtrl-A"),    None,            self.grid.SelectAllCells,     wx.ID_SELECTALL],
              ##["&Find and Replace...\tCtrl-F",  FindRIcon,     self.GoFindDialog,     wx.ID_REPLACE],
              [u"--"],
              [translate(u"Delete Current Column"), None,  self.grid.DeleteCurrentCol,     None],
              [translate(u"Delete Current Row"),    None,  self.grid.DeleteCurrentRow,     None],)),
            (translate(u"&Preferences"),
             ((translate(u"Variables..."),             None,  self.GoVariablesFrame,     None ),
              [translate(u"Add Columns and Rows..."),  None,  self.GoEditGrid,     None],
              [translate(u"Change Cell Size..."),      None,  self.GoGridPrefFrame,     None],
              [translate(u"Change the Font..."),       None,  self.GoFontPrefsDialog,     None],
              [u"--"],
              [translate(u"Load default perspective"),      None, self.onDefaultPerspective, None],)),
            (translate(u"P&reparation"),
             ([translate(u"Descriptive Statistics"),   None,  self.GoContinuousDescriptives,     None],
              [translate(u"Transform Data"),           None,  self.GoTransformData,     None],
              [translate(u"short data"),               None,  self.shortData,     None],)),
            (translate(u"S&tatistics"),
             statisticalMenus),
            (translate(u"&Graph"),
             [ (translate(u"Show/Hide the plot panel"), None, self.showPlotPanel,       None),] +
               [plotMenu for plotMenu in plotMenus]),
            (translate(u"&Help"),
             (##("Help\tCtrl-H",       imag.about(),  self.GoHelpSystem,  wx.ID_HELP),
              (translate(u"&About..."),          imag.icon16(), self.ShowAbout,     wx.ID_ABOUT),)),
        )
        self.__createMenu(dat1, menuBar)
        self.SetMenuBar(menuBar)

    def __createMenu(self,data,parent):
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
            app = wx.GetApp()
            wx.App_SetMacHelpMenuTitleName(translate(u"&Help"))
            # Allow spell checking in cells
            # TODO Still need to add this to the Edit menu once we add Mac menu options
            spellcheck = u"mac.textcontrol-use-spell-checker"
            wx.SystemOptions.SetOptionInt(spellcheck, 1)

    def _BindEvents(self):
        # grid callback
        self.grid.Bind( wx.grid.EVT_GRID_CMD_SELECT_CELL, self._cellSelectionChange )
        self.grid.Bind( wx.grid.EVT_GRID_SELECT_CELL, self._cellSelectionChange )
        self.grid.Bind( wx.grid.EVT_GRID_RANGE_SELECT, self._gridRangeSelect )
        #-----------------
        # para el toolbar
        self.Bind(wx.EVT_MENU, self.GoClearData,        id= self.bt1.GetId())
        self.Bind(wx.EVT_MENU, self.grid.LoadFile,       id= self.bt2.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SaveXls,       id= self.bt3.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SaveXlsAs,     id= self.bt4.GetId())
        ##self.Bind(wx.EVT_MENU, self.grid.PrintPage,    id = self.bt5.GetId())
        self.Bind(wx.EVT_MENU, self.grid.CutData,       id= self.bt6.GetId())
        self.Bind(wx.EVT_MENU, self.grid.CopyData,      id= self.bt7.GetId())
        self.Bind(wx.EVT_MENU, self.grid.PasteData,     id= self.bt8.GetId())
        self.Bind(wx.EVT_MENU, self.GoVariablesFrame,   id= self.bt9.GetId())
        ##self.Bind(wx.EVT_MENU, self.GoHelpSystem,       id= self.bt10.GetId())
        self.Bind(wx.EVT_MENU, self.GoOnlyneHelp,       id= self.bt10.GetId())
        self.Bind(wx.EVT_MENU, self.grid.Undo,          id= self.bt11.GetId())
        self.Bind(wx.EVT_MENU, self.grid.Redo,          id= self.bt12.GetId())

        # controlling the expansion of the notebook
        self.m_notebook1.Bind( wx.EVT_LEFT_DCLICK, self._OnNtbDbClick )
        # self.Bind( wx.EVT_CLOSE, self.EndApplication )
        self.grid.setPadreCallBack(self)
        self.sig= self.siguiente()

    def siguiente(self):
        i= 0
        while 1:
            yield i
            i+= 1
    def _evalstat(self, evt, stat):
        stat().showGui()

    def _gridRangeSelect(self, evt):
        # displays the count and the sum of selected values

        selectedCells= self.grid.get_selection()
        # Count the selected cells
        # getting the cell values:
        selectedCellText= list()
        selectedNumerical= list()
        emptyText= 0
        for rowi, coli in selectedCells:
            currText= self.grid.GetCellValue( rowi, coli)
            if currText == u"":
                emptyText+= 1
            try:
                selectedNumerical.append( float( currText.replace( self.DECIMAL_POINT, ".")))
            except:
                pass
            selectedCellText.append( currText)
        self.StatusBar.SetStatusText( translate(u"cells Selected: %.0f  count: %.0f  sum: %.4f ")%(len(selectedCells),len(selectedCells)-emptyText,sum(selectedNumerical)),1 )

    def _cellSelectionChange( self, evt):
        # se lee el contenido de la celda seleccionada
        row= evt.GetRow()
        col= evt.GetCol()
        texto= u""
        try:
            texto= self.grid.GetCellValue( row, col)
        except wx._core.PyAssertionError:
            pass
        self.formulaBarPanel.m_textCtrl1.SetValue( texto)
        evt.Skip()

    def _OnNtbDbClick(self,evt):
        for pane in self.m_mgr.GetAllPanes():
            if pane.caption == self.translate(u"Log / Shell Panel"):
                break
        if not pane.IsMaximized():
            self.m_mgr.MaximizePane(pane)
        else:
            self.m_mgr.RestorePane(pane)
	    #pane.MinimizeButton(True)
	self.m_mgr.Update()
    
    def OnDropFiles( self, x, y, filenames):
        if isinstance( filenames, (str, unicode)):
            filenames= [filenames]
            
        if len( filenames) == 0:
            return
        
        # taking the first element as the selected file
        filename= filenames[0]
        sys.stderr.write( translate(u"the file %d was dropped")%filename)
        
    
    def onDefaultPerspective(self, evt):
        self.m_mgr.LoadPerspective(self._defaultPerspective)
        
    def GoClearData(self, evt):
        if not self.grid.hasSaved:
            # display discard dialog
            dlg = wx.MessageDialog(None, translate(u"Do you wish to save now?"),
                                   translate(u"You have Unsaved Data"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
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
        # NOTE - this doesn"t appear to work on the grid, so I might be missing something...
        data = wx.FindReplaceData()
        dlg = wx.FindReplaceDialog(self.grid, data, translate(u"Find and Replace"), \
                                   wx.FR_REPLACEDIALOG)
        dlg.data = data
        dlg.Show(True)

    def GoEditGrid(self, evt):
        #shows dialog for editing the data grid
        btn1=  ["SpinCtrl",   [0,5000,0]]
        btn2=  ["StaticText", [translate(u"Change Grid Size")]]
        btn3=  ["StaticText", [translate(u"Add Columns")]]
        btn4=  ["StaticText", [translate(u"Add Rows")]]
        setting= {"Title": translate(u"Change Grid size")}

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
        btn2=  ["StaticText", [translate(u"Change the cell Size")]]
        btn3=  ["StaticText", [translate(u"Column Width")]]
        btn4=  ["StaticText", [translate(u"Row Height")]]
        setting= {"Title": translate(u"Change the cell size")}

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
        icon = imagenes.logo16()
        self.SetIcon(icon)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            self.grid.SetDefaultCellTextColour(data.GetColour())
            self.grid.SetDefaultCellFont(data.GetChosenFont())
        dlg.Destroy()

    def GoContinuousDescriptives(self, evt):
        # shows the continuous descriptives dialog
        win = DescriptivesFrame(wx.GetApp().frame, -1)
        win.Show(True)

    def GoTransformData(self, evt):
        win = TransformFrame(wx.GetApp().frame, -1)
        win.Show(True)

    def ShowAbout(self, evt):
        info= wx.AboutDialogInfo()
        info.Name= u"S2 SalStat Statistics Package 2"
        info.Version= u"V" + wx.GetApp().VERSION
        info.Copyright= u"(C) 2012 Sebastian Lopez Buritica, S2 Team"
        info.Icon= wx.GetApp().icon64
        from wx.lib.wordwrap import wordwrap
        info.Description = wordwrap(
            translate(u"This is a newer version of the SalStat Statistics Package ")+
            translate(u"originally developed by Alan James Salmoni and Mark Livingstone. ")+
            translate(u"There have been minor bug corrections, and new improvements:\n\n")+
            translate(u"*You can cut, copy, and paste multiple cells,\n")+
            translate(u"*You can undo and redo some actions.\n")+
            translate(u"*The calculations are faster than the original version.\n\n")+
            translate(u"The plot system can draw:\n\n")+
            translate(u"*Scatter charts\n*line chart of all means\n*bar chart of all means\n")+
            translate(u"*Histogram chart\n")+
            translate(u"*Line charts of the data,\n*box and whisker chart\n*Ternary chart\n")+
            translate(u"*Linear regression plot (show the equation and the correlation inside the chart),\n")+
            translate(u"\nThe input data can be saved to, and loaded from an xls format file.\n\n")+
            translate(u"Salstat2 can be scripted by using Python.\n\n")+
            translate(u"All the numerical results are send to a sheet in a different panel where you can cut, copy, paste, and edit them.\n\n")+
            translate(u"and much more!"),
            460, wx.ClientDC( self))
        info.WebSite = ( u"http://code.google.com/p/salstat-statistics-package-2/", u"S2 home page")
        info.Developers = [ u"Sebastian Lopez Buritica", "Mark Livingstone --" + translate("MAC & LINUX  Translator"),]

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
        panels = self.m_mgr.GetAllPanes()
        for panel in panels:
            if panel.caption == translate(u"Plot selection"):
                break
        self.m_mgr.Update()
        if not panel.IsShown():
            panel.Show(True)
            
        else:
            panel.Show(False)
            
        self.m_mgr.Update()    
    def EndApplication(self, evt):
        if self.grid.hasSaved == False:
            # checking if there is a data to be saved
            if len(self.grid.GetUsedCols()[0]) != 0:
                win = SaveDialog(self)
                win.Show(True)
            else:
                wx.GetApp().frame.Destroy()
        else:
            wx.GetApp().frame.Destroy()

    def shortData(self,evt):
        functionName = "short"
        useNumpy = False
        requiredcols= None
        allColsOneCalc = False,
        dataSquare= False
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting["Title"] = functionName
        setting["_size"] = wx.Size(220, 200)
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()
        bt1= group("StaticText", ("Select the column to short",) )
        bt2 = group("Choice",    (ColumnList,))
        structure = list()
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
            self.logPanel.write("You haven't select any items!")
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
	
    def __del__( self ):
	pass
#--------------------------------------------------------------------------
# main loop
if __name__ == '__main__':
    app = SalStat2App(0)
    app.frame.Show()
    app.MainLoop()
# eof