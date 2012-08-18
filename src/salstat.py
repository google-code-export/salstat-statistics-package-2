#!/usr/bin/env python

""" Copyright 2012 Sebastian Lopez Buritica, S2 Team,  licensed under GPL 3

SalStat Statistics Package. Copyright 2002 Alan James Salmoni. Licensed
under the GNU General Public License (GPL 2). See the file COPYING for full
details of this license. """

import wx
import os

import wx.grid

# -----------------
# to use the sash
import  wx.lib.multisash as sash
import  wx.gizmos as gizmos
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
import string, os, os.path, pickle

from imagenes import imageEmbed
import numpy
import wx.py
import traceback

# translation module
import locale
import glob
import sys
import time

from xml.dom import minidom
# system of graphics
from plotFrame import MpltFrame as plot
from multiPlotDialog import data2Plotdiaglog, selectDialogData2plot, scatterDialog
from ntbSheet import NoteBookSheet, SimpleGrid

from openStats import statistics, normProb, normProbInv

from slbTools import  homogenize, GroupData # GroupData is used to treat data a a pivot table 
from easyDialog import Dialog as dialog
from statlib import stats

from script import ScriptPanel
from imagenes import imageEmbed

from helpSystem import Navegator

from dialogs import CheckListBox
from dialogs import SaveDialog, VariablesFrame, DescriptivesFrame
from dialogs import TransformFrame

from gridCellRenderers import floatRenderer, AutoWrapStringRenderer

APPNAME= 'S2'

inits ={}    # dictionary to hold the config values
ColsUsed= []
RowsUsed= []
missingvalue= None
HOME= os.getcwd()
imagenes = imageEmbed()

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
    btn2=  ['StaticText', ["Change the cell Size"]]
    btn3=  ['StaticText', ["Column Width"]]
    btn4=  ['StaticText', ["Row Height"]]
    setting= {'Title': 'Change the cell size'}

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
        the_path = os.path.join(path, "LC_MESSAGES", "GUI2Exe.mo")
        if os.path.exists(the_path):
            avail_loc.append(os.path.basename(path))
    return avail_loc

def FormatTrace(etype, value, trace):
    """Formats the given traceback

    **Returns:**

    *  Formatted string of traceback with attached timestamp

    **Note:**

    *  from Editra.dev_tool
    """

    exc = traceback.format_exception(etype, value, trace)
    exc.insert(0, "*** %s ***%s" % ( now(), os.linesep))
    return "".join(exc)


class SalStat2App(wx.App):
    # the main app
    def __init__(self, *args, **kwargs):
        wx.App.__init__(self, *args, **kwargs)

        # This catches events on Mac OS X when the app is asked to activate by some other
        # process
        # TODO: Check if this interferes with non-OS X platforms. If so, wrap in __WXMAC__ block!
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)

    def OnInit(self):
        import sys
        # getting the os type
        self.OSNAME = os.name
        self.VERSION= '2.1 beta 2'
        self.missingvalue= missingvalue
        wx.SetDefaultPyEncoding("utf-8")
        self.SetAppName(APPNAME)
        try:
            installDir = os.path.dirname(os.path.abspath(__file__))
        except:
            installDir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.installDir= installDir # to be used in the nice bar plot
        language = self.GetPreferences("Language")
        if not language:
            language = "Default"
        # Setup Locale
        locale.setlocale(locale.LC_ALL, '')
        self.locale = wx.Locale(GetLangId(installDir, language))
        if self.locale.GetCanonicalName() in GetAvailLocales(installDir):
            self.locale.AddCatalogLookupPathPrefix(os.path.join(installDir, "locale"))
            self.locale.AddCatalog(APPNAME)
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
            self.frame.logPanel.write("The file %s could not be opened. "
                           "Please check file type and extension!" % filename)

    def MacOpenFile(self, filename):
        """Called for files dropped on dock icon, or opened via finders context menu"""
        self.frame.logPanel.write("%s dropped on S2 dock icon"%(filename))
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

    def GetVersion(self):
        return '2.1'

#---------------------------------------------------------------------------
# This is main interface of application
class MainFrame(wx.Frame, wx.FileDropTarget):
    def __init__(self, parent, appname ):
        self.path= None
        # to allow the user to drop allowed files into the Data Entry Panel
        wx.FileDropTarget.__init__( self)
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
        self.grid.Saved= True
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
        self.m_notebook1.AddPage( self.logPanel, u"Log", True )
        # Redurecting the error messages to the logPanel
        sys.stderr= self.logPanel
        sys.stdout= self.logPanel
        self.scriptPanel=  wx.py.crust.Shell( self.m_notebook1) # wx.py.shell.Shell( self.m_notebook1)
        ##self.scriptPanel.stderr= self.logPanel
        
        #self.scriptPanel.wrap( True)
        self.m_notebook1.AddPage( self.scriptPanel , u"Shell", False )

        # put the references into the main app
        appname.inputGrid= self.grid
        appname.Logg= self.logPanel
        appname.output= self.answerPanel
        appname.plot= plot

        # create menubar
        self._createMenu()

        #------------------------
        # organizing panels
        self.m_mgr.AddPane( self.formulaBarPanel,
                            aui.AuiPaneInfo().Name("tb2").Caption("Inspection Tool").ToolbarPane().Top().Row(1).
                            Position(1).CloseButton( False ))

        self.m_mgr.AddPane(self.grid,
                           aui.AuiPaneInfo().Centre().
                           CaptionVisible(True).Caption("Data Entry Panel").
                           MaximizeButton(True).MinimizeButton(True).
                           CloseButton( False ).MinSize( wx.Size( 240,-1 )))

        self.m_mgr.AddPane(self.answerPanel,
                           aui.AuiPaneInfo().Centre().Right().
                           CaptionVisible(True).Caption(("Output Panel")).
                           MinimizeButton(True).Resizable(True).MaximizeButton(True).
                           CloseButton( False ).MinSize( wx.Size( 240,-1 )))

        self.m_mgr.AddPane( tb1, aui.AuiPaneInfo().Name("tb1").Caption("Basic Operations").
                            ToolbarPane().Top().Row(1).CloseButton( False ))

        self.m_mgr.AddPane(self.answerPanel2,
                           aui.AuiPaneInfo().Centre().Right().
                           CaptionVisible(True).Caption(("Script Panel")).
                           MinimizeButton().Resizable(True).MaximizeButton(True).
                           CloseButton( False ).MinSize( wx.Size( 240,-1 )))

        self.panelNtb = self.m_mgr.AddPane( self.m_notebook1,
                                            aui.AuiPaneInfo() .Bottom() .
                                            CloseButton( False ).MaximizeButton( True ).
                                            Caption(('Log / Shell Panel')).
                                            MinimizeButton().PinButton( False ).
                                            Dock().Resizable().FloatingSize( wx.DefaultSize ).
                                            CaptionVisible(True).
                                            DockFixed( False ).BestSize(wx.Size(-1,150)))
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
              }
#'stats': self.stats,
#'dialog':Dialog,
#'OK':    wx.ID_OK,
#'statistics':statistics,
#'homogenize':homogenize,
              
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

        self.bt1 = tb1.AddSimpleTool(10, "New",  NewIcon,"New")
        self.bt2 = tb1.AddSimpleTool(20, "Open", OpenIcon,"Open")
        self.bt3 = tb1.AddSimpleTool(30, "Save", SaveIcon,"Save")
        self.bt4 = tb1.AddSimpleTool(40, "Save As",SaveAsIcon,"Save As")
        ##self.bt5 = tb1.AddSimpleTool(50, "Print",PrintIcon,"Print")
        tb1.AddSeparator()
        self.bt11= tb1.AddSimpleTool(wx.ID_ANY,"Undo",UndoIcon,"Undo")
        self.bt12= tb1.AddSimpleTool(wx.ID_ANY,"Redo",RedoIcon,"Redo")
        tb1.AddSeparator()
        self.bt6 = tb1.AddSimpleTool(60, "Cut",  CutIcon, "Cut")
        self.bt7 = tb1.AddSimpleTool(70, "Copy", CopyIcon, "Copy")
        self.bt8 = tb1.AddSimpleTool(80, "Paste",PasteIcon, "Paste")
        tb1.AddSeparator()
        self.bt9 = tb1.AddSimpleTool(85, "Preferences",PrefsIcon, "Preferences")
        ##self.bt10= tb1.AddSimpleTool(90, "Help", HelpIcon, "Help")
        self.bt10= tb1.AddSimpleTool(95, "OnlineHelp", HelpIcon, "Online Help")
        tb1.SetToolBitmapSize((24,24))
        tb1.Realize()
        return tb1

    def _autoCreateMenu(self, module):
        # automatically creates a menu related with an specified module
        groups= module.__all__
        subgroup= list()
        for group in groups:
            attr= getattr( module, group) # central tendency
            result= list()
            for item in attr.__all__:
                fnc= getattr( attr, item)
                result.append( (fnc.name, fnc.icon, getattr( fnc(), 'showGui'), fnc.id))
            subgroup.append( (attr.__name__, result))
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
        import statFunctions
        from statFunctions import *
        statisticalMenus= self._autoCreateMenu( statFunctions)
        import plotFunctions
        from plotFunctions import *
        plotMenus= self._autoCreateMenu( plotFunctions)
        #add contents of menu
        dat1= (
            ('&File',
             (['&New Data\tCtrl-N',   NewIcon,    self.GoClearData,     wx.ID_NEW],
              ['&Open...\tCtrl-O',    OpenIcon,   self.grid.LoadFile,    wx.ID_OPEN], # LoadXls
              ['--'],
              ['&Save\tCtrl-S',       SaveIcon,   self.grid.SaveXls,     wx.ID_SAVE],
              ['Save &As...\tCtrl-Shift-S', SaveAsIcon, self.grid.SaveXlsAs,     wx.ID_SAVEAS],
              ##['&Print...\tCtrl-P',   PrintIcon,  None,     None],
              ['--'],
              ['E&xit\tCtrl-Q',       ExitIcon,   self.EndApplication,     wx.ID_EXIT],
              )),
            ('&Edit',
             (['Cu&t',           CutIcon,         self.grid.CutData,     wx.ID_CUT],
              ['&Copy',          CopyIcon,        self.grid.CopyData,     wx.ID_COPY],
              ['&Paste',         PasteIcon,       self.grid.PasteData,     wx.ID_PASTE],
              ['--'],
              ['Select &All\tCtrl-A',    None,            self.grid.SelectAllCells,     wx.ID_SELECTALL],
              ##['&Find and Replace...\tCtrl-F',  FindRIcon,     self.GoFindDialog,     wx.ID_REPLACE],
              ['--'],
              ['Delete Current Column', None,  self.grid.DeleteCurrentCol,     None],
              ['Delete Current Row',    None,  self.grid.DeleteCurrentRow,     None],)),
            ('&Preferences',
             (('Variables...',             None,  self.GoVariablesFrame,     None ),
              ['Add Columns and Rows...',  None,  self.GoEditGrid,     None],
              ['Change Cell Size...',      None,  self.GoGridPrefFrame,     None],
              ['Change the Font...',       None,  self.GoFontPrefsDialog,     None],
              ['--'],
              ['Load default perspective',      None, self.onDefaultPerspective, None],)),
            ('P&reparation',
             (['Descriptive Statistics',   None,  self.GoContinuousDescriptives,     None],
              ['Transform Data',           None,  self.GoTransformData,     None],
              ['short data',               None,  self.shortData,     None],)),
            ('S&tatistics',
             statisticalMenus),
            ('&Graph',
             ( plotMenus[0],
               ('Line Chart of All Means', None, self.GoChartWindow,     None),
               ('Bar Chart of All Means',  None, self.GoMeanBarChartWindow,     None),
               ('Bar Chart',               None, self.GoBarChartWindow,     None),
               ('Lines',                   None, self.GoLinesPlot,     None),
               ('Scatter',                 None, self.GoScatterPlot,     None),
               ('Box & Whisker',           None, self.GoBoxWhiskerPlot,     None),
               ('Linear Regression',       None, self.GoLinRegressPlot,     None),
               ('Ternary',                 None, self.GoTernaryplot,     None),
               ('Probability',             None, self.GoProbabilityplot,     None),
               ('Adaptative BMS',          None, self.GoAdaptativeBMS,     None),)),
            ('&Help',
             (##('Help\tCtrl-H',       imag.about(),  self.GoHelpSystem,  wx.ID_HELP),
              ('&About...',          imag.icon16(), self.ShowAbout,     wx.ID_ABOUT),)),
        )
        self.__createMenu(dat1, menuBar)
        self.SetMenuBar(menuBar)

    def __createMenu(self,data,parent):
        if len(data) == 1:
            if data[0] == u'--':
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

        if wx.Platform == '__WXMAC__':
            app = wx.GetApp()
            wx.App_SetMacHelpMenuTitleName("&Help")
            # Allow spell checking in cells
            # TODO Still need to add this to the Edit menu once we add Mac menu options
            spellcheck = "mac.textcontrol-use-spell-checker"
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
            if currText == u'':
                emptyText+= 1
            try:
                selectedNumerical.append( float( currText.replace( self.DECIMAL_POINT, '.')))
            except:
                pass
            selectedCellText.append( currText)
        self.StatusBar.SetStatusText( 'cells Selected: %.0f  count: %.0f  sum: %.4f '%(len(selectedCells),len(selectedCells)-emptyText,sum(selectedNumerical)),1 )

    def _cellSelectionChange( self, evt):
        # se lee el contenido de la celda seleccionada
        row= evt.GetRow()
        col= evt.GetCol()
        texto= u''
        try:
            texto= self.grid.GetCellValue( row, col)
        except wx._core.PyAssertionError:
            pass
        self.formulaBarPanel.m_textCtrl1.SetValue( texto)
        evt.Skip()

    def _OnNtbDbClick(self,evt):
        for pane in self.m_mgr.AllPanes:
            if pane.name == 'Bottom Panel':
                break
        if not pane.IsMaximized():
            self.mm_mgr.MaximizePane(pane)
        else:
            pane.MinimizeButton(True)
    
    def OnDropFiles( self, x, y, filenames):
        if isinstance( filenames, (str, unicode)):
            filenames= [filenames]
            
        if len( filenames) == 0:
            return
        
        # taking the first element as the selected file
        filename= filenames[0]
        sys.stderr.write('the file %d was dropped'%filename)
        
    
    def onDefaultPerspective(self, evt):
        self.m_mgr.LoadPerspective(self._defaultPerspective)
        
    def GoClearData(self, evt):
        if not self.grid.Saved:
            # display discard dialog
            dlg = wx.MessageDialog(None, 'Do you wish to save now?',
                                   'You have Unsaved Data', wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
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
        self.grid.Saved = False
        self.m_mgr.Update()
        # /<p>
        # emptying the undo redo

    def GoFindDialog(self, evt):
        # Shows the find & replace dialog
        # NOTE - this doesn't appear to work on the grid, so I might be missing something...
        data = wx.FindReplaceData()
        dlg = wx.FindReplaceDialog(self.grid, data, 'Find and Replace', \
                                   wx.FR_REPLACEDIALOG)
        dlg.data = data
        dlg.Show(True)

    def GoEditGrid(self, evt):
        #shows dialog for editing the data grid
        btn1=  ['SpinCtrl',   [0,5000,0]]
        btn2=  ['StaticText', ["Change Grid Size"]]
        btn3=  ['StaticText', ["Add Columns"]]
        btn4=  ['StaticText', ["Add Rows"]]
        setting= {'Title': 'Change Grid size'}

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
        btn1=  ['SpinCtrl',   [5,90,5]]
        btn2=  ['StaticText', ["Change the cell Size"]]
        btn3=  ['StaticText', ["Column Width"]]
        btn4=  ['StaticText', ["Row Height"]]
        setting= {'Title': 'Change the cell size'}

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
        info.Name= "S2 SalStat Statistics Package 2"
        info.Version= "V" + wx.GetApp().VERSION
        info.Copyright= "(C) 2012 Sebastian Lopez Buritica, S2 Team"
        info.Icon= wx.GetApp().icon64
        from wx.lib.wordwrap import wordwrap
        info.Description = wordwrap(
            "This is a newer version of the SalStat Statistics Package "
            "originally developed by Alan James Salmoni and Mark Livingstone. "
            "There have been minor bug corrections, and new improvements:\n\n"
            "*You can cut, copy, and paste multiple cells,\n"
            "*You can undo and redo some actions.\n"
            "*The calculations are faster than the original version.\n\n"
            "The plot system can draw:\n\n"
            "*Scatter charts\n*line chart of all means\n*bar chart of all means\n"
            "*Histogram chart\n"
            "*Line charts of the data,\n*box and whisker chart\n*Ternary chart\n"
            "*Linear regression plot (show the equation and the correlation inside the chart),\n"
            "\nThe input data can be saved to, and loaded from an xls format file.\n\n"
            "Salstat2 can be scripted by using Python.\n\n"
            "All the numerical results are send to a sheet in a different panel where you can cut, copy, paste, and edit them.\n\n"
            "and much more!",
            460, wx.ClientDC(self))
        info.WebSite = ("http://code.google.com/p/salstat-statistics-package-2/", "S2 home page")
        info.Developers = [ "Sebastian Lopez Buritica", "Mark Livingstone -- MAC & LINUX  Translator",]

        info.License = wordwrap("GPL 3", 450, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)

    def GoCheckOutliers(self, evt):
        pass

    def GoHelpSystem( self, evt):
        # shows the "wizard" in the help box
        win= Navegator( wx.GetApp().frame,)
        win.Show( True)
        
    def GoOnlyneHelp( self, evt):
        webbrowser.open(r'http://code.google.com/p/salstat-statistics-package-2/wiki/Documentation?ts=1344287549&updated=Documentation')
        
    ################
    ### chart init
    ################
    def GoChartWindow(self, evt):
        self.log.write('''Line chart of all means''')
        waste, colnums = self.grid.GetUsedCols()
        self.log.write('''waste, colnums = grid.GetUsedCols()''', False)
        if colnums == []:
            self.SetStatusText( 'You need some data to draw a graph!')
            return
        selection= data2Plotdiaglog( self,waste)
        if selection.ShowModal() != wx.ID_OK:
            selection.Destroy()
            return
        selectedcols= selection.getData()
        self.log.write( 'selectedcols=' + selectedcols.__str__(), False)
        selection.Destroy()
        if len( selectedcols) == 0:
            self.SetStatusText( 'You need to select some data to draw a graph!')
            return
        self.log.write('''data = [statistics(grid.CleanData(cols), 'noname',None) for cols in [colnums[m] for m in selectedcols]]''', False)
        data = [statistics(self.grid.CleanData(cols), 'noname',None) for cols in [colnums[m] for m in selectedcols]]
        self.log.write('''data = [data[i].mean for i in range(len(data))]''', False)
        data = [data[i].mean for i in range(len(data))]
        self.log.write('''plt= plot(parent = None, typePlot= 'plotLine',
                  data2plot= ((range(len(data)),data,'Mean'),),
                  xlabel = 'variable',
                  ylabel= 'mean',
                  title= 'Line Chart of all means',
                  xtics= [waste[i] for i in selectedcols])''', False)
        plt= plot(parent = self, typePlot= 'plotLine',
                  data2plot= ((range(len(data)),data,'Mean'),),
                  xlabel = 'variable',
                  ylabel= 'mean',
                  title= 'Line Chart of all means',
                  xtics= [waste[i] for i in selectedcols])
        self.log.write('''plt.Show()''', False)
        plt.Show()

    def GoTernaryplot(self, evt):
        self.log.write('Ternary')
        waste, colnums= self.grid.GetUsedCols()
        self.log.write('waste, colnums= grid.GetUsedCols()', False)

        if colnums == []:
            self.SetStatusText('You need some data to draw a graph!')
            return

        txt1= ['StaticText', ['Left Corner Label']]
        txt2= ['StaticText', ['Right Corner Label']]
        txt3= ['StaticText', ['Upper Corner Label']]
        btn1= ['TextCtrl',   ['A']]
        btn2= ['TextCtrl',   ['B']]
        btn3= ['TextCtrl',   ['C']]
        btn4= ['StaticText', ['Select the pairs of data by rows']]
        btn5= ['makePairs',  [['A Left Corner','C Upper Corner', 'B Right Corner'], [waste]*3, 30]]
        structure= list()
        structure.append( [btn1, txt1])
        structure.append( [btn2, txt2])
        structure.append( [btn3, txt3])
        structure.append( [btn4,])
        structure.append( [btn5,])
        settings = {'Tile': 'Ternary plot dialog' ,
                    '_size': wx.Size(410, 400),}
        dlg= dialog(self, settings= settings, struct= structure)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        values= dlg.GetValue()
        dlg.Destroy()

        Alabel= values[0]
        if Alabel == u'' or Alabel.replace(' ','') == u'':
            Alabel= u'A'
        self.log.write('Alabel= '+"'"+Alabel.__str__()+"'", False)

        Blabel= values[1]
        if Blabel == u'' or Blabel.replace(' ','') == u'':
            Blabel= u'B'
        self.log.write('Blabel= '+"'"+ Blabel.__str__()+"'", False)

        Clabel= values[2]
        if Clabel == u'' or Clabel.replace(' ','') == u'':
            Clabel= u'C'
        self.log.write('Clabel= '+"'"+ Clabel.__str__()+"'", False)

        pairs= values[3]
        if len(pairs) == 0:
            return
        self.log.write('pairs= '+pairs.__str__(), False)

        data= [(self.grid.GetCol(colLeft),
                self.grid.GetCol(colUpper),
                self.grid.GetCol(colRight),
                colLeft+' - '+colUpper+' - '+colRight )
               for (colLeft, colUpper, colRight) in pairs]
        self.log.write('''data= [(grid.GetCol(colLeft),
                grid.GetCol(colUpper),
                grid.GetCol(colRight),
                colLeft+' - '+colUpper+' - '+colRight )
               for (colLeft, colUpper, colRight) in pairs]''', False)

        plt= plot(parent=    self,
                  typePlot=  'plotTrian',
                  data2plot= (data, [Alabel, Blabel, Clabel]),
                  title=     'Ternary Plot')
        self.log.write('''plt= plot(parent=    None,
                  typePlot=  'plotTrian',
                  data2plot= (data, [Alabel, Blabel, Clabel]),
                  title=     'Ternary Plot')''', False)

        plt.Show()
        self.log.write('plt.Show()', False)

    def GoMeanBarChartWindow(self, evt):
        '''this funtcion is used to plot the bar chart of all means'''
        self.log.write('Bar Chart of All Means')
        waste, colnums = self.grid.GetUsedCols()
        self.log.write('''waste, colnums = grid.GetUsedCols()''', False)
        if colnums == []:
            self.SetStatusText('You need some data to draw a graph!')
            return

        colours= ['random', 'white', 'blue', 'black',
                  'red', 'green', 'lightgreen', 'darkblue',
                  'yellow', 'hsv']
        # getting all the available figures
        path=     os.path.join(os.path.split(sys.argv[0])[0], 'nicePlot', 'images', 'barplot')
        figTypes= [fil[:-4] for fil in os.listdir(path) if fil.endswith('.png')]
        txt1= ['StaticText', ['Bar type']]
        txt2= ['StaticText', ['Colour']]
        txt3= ['StaticText', ['Select data to plot']]
        btn1= ['Choice', [figTypes]]
        btn2= ['Choice', [colours]]
        btn3= ['CheckListBox', [waste]]
        btn4= ['CheckBox', ['push the labels up to the bars'] ]
        structure= list()
        structure.append([btn1, txt1])
        structure.append([btn2, txt2])
        structure.append([txt3])
        structure.append([btn3])
        structure.append([btn4])
        setting= {'Title':'Bar chart means of selected columns'}
        dlg= dialog(self, settings= setting, struct= structure)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        values=  dlg.GetValue()
        barType= values[0]
        colour=  values[1]
        selectedcols= values[2]
        showLabels= values[3]

        if barType == None:
            barType= 'redunca'

        if colour == None:
            colour= 'random'
        
        if showLabels:
            labels= selectedcols
        else:
            labels = None

        dlg.Destroy()
        if len( selectedcols) == 0:
            self.SetStatusText( 'You need to select some data to draw a graph!')
            return

        self.log.write( 'barType= '+ "'" + barType.__str__() + "'", False)
        self.log.write( 'colour= '+ "'" + colour.__str__() + "'", False)
        self.log.write( 'selectedcols= '+ selectedcols.__str__(), False)
        self.log.write( '''data= [statistics( grid.GetColNumeric(col),'noname',None).mean for col in selectedcols]''', False)
        data = [statistics( self.grid.GetColNumeric( col),'noname',None).mean
                for col in selectedcols]
        self.log.write( '''plt= plot(parent=   None,
                  typePlot= 'plotNiceBar',
                  data2plot= (numpy.arange(1, len(data)+1), data,  None,  colour, barType,),
                  xlabel=  'variable',
                  ylabel=  'value',
                  title=   'Bar Chart of all means')''', False)
        plt= plot(parent=   self,
                  typePlot= 'plotNiceBar',
                  data2plot= (numpy.arange(1, len(data)+1), data,  None,  colour, barType, labels),
                  xlabel=  'variable',
                  ylabel=  'value',
                  title=   'Bar Chart of all means')
        plt.Show()
        self.log.write('plt.Show()', False)

    def GoBarChartWindow(self, evt):
        '''this funtcion is used to plot the bar chart of the selected column'''
        self.log.write('Bar Chart')
        waste, colnums = self.grid.GetUsedCols()
        self.log.write('''waste, colnums = grid.GetUsedCols()''', False)
        if colnums == []:
            self.SetStatusText('You need some data to draw a graph!')
            return
        colours= ['random', 'white', 'blue', 'black',
                  'red', 'green', 'lightgreen', 'darkblue',
                  'yellow', 'hsv']
        # getting all the available figures
        path=     os.path.join(os.path.split(sys.argv[0])[0], 'nicePlot','images','barplot')
        figTypes= [fil[:-4] for fil in os.listdir(path) if fil.endswith('.png')]
        txt1= ['StaticText', ['Bar type']]
        txt2= ['StaticText', ['Colour']]
        txt3= ['StaticText', ['Select data to plot']]
        btn1= ['Choice', [figTypes]]
        btn2= ['Choice', [colours]]
        btn3= ['Choice', [waste]]
        btn4= ['CheckBox', ['push the labels up to the bars'] ]
        structure= list()
        structure.append([btn1, txt1])
        structure.append([btn2, txt2])
        structure.append([txt3])
        structure.append([btn3])
        structure.append([btn4])
        setting= {'Title':'Bar chart means of selected columns'}
        dlg= dialog(self, settings= setting, struct= structure)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        values=  dlg.GetValue()
        barType= values[0]
        colour=  values[1]
        selectedcol= values[2]
        showLabels= values[3]

        if barType == None:
            barType= 'redunca'

        if colour == None:
            colour= 'random'

        dlg.Destroy()
        if len(selectedcol) == 0:
            self.SetStatusText('You need to select some data to draw a graph!')
            return
        
        if showLabels != False:
            labels= selectedcol
        else:
            labels = None

        self.log.write( 'barType= '+ "'" + barType.__str__() + "'", False)
        self.log.write( 'colour= '+ "'" + colour.__str__() + "'", False)
        self.log.write( 'selectedcol= '+ selectedcol.__str__(), False)
        data = self.grid.GetColNumeric( selectedcol)
        self.log.write( '''data= grid.GetColNumeric(selectedcol)''', False)
        conc= lambda x,y: x + ', ' + y
        newval= list()
        for dat in data:
            if not isinstance(dat, (str, unicode)):
                dat= dat.__str__()
            newval.append(dat)
            
        if len(newval)> 1:
            self.log.write( "labels= " +"[" + reduce(conc, newval[1:], newval[0] ) + "]", False)
        else:
            self.log.write( "labels= " +"[" + newval[0] + "]", False)
        self.log.write( '''plt= plot( parent=   None,
                  typePlot= 'plotNiceBar',
                  data2plot= ( numpy.arange(1, len(data)+1), data,  None,  colour, barType, labels),
                  xlabel=  'variable',
                  ylabel=  'value',
                  title=   'Bar Chart')''', False)
        plt= plot(parent=   self,
                  typePlot= 'plotNiceBar',
                  data2plot= ( numpy.arange(1, len( data)+1), data,  None,  colour, barType, newval),
                  xlabel=  'variable',
                  ylabel=  'value',
                  title=   'Bar Chart')
        plt.Show()
        self.log.write( 'plt.Show()', False)

    def GoScatterPlot(self,evt):
        self.log.write('Scatter')
        waste, colnums = self.grid.GetUsedCols()
        self.log.write('''waste, colnums = grid.GetUsedCols()''', False)
        if colnums == []:
            self.SetStatusText('You need some data to draw a graph!')
            return

        bt1= ['StaticText', ['Select pairs of data by rows']]
        bt2= ['makePairs',  [['X data to plot','Y data to plot'], [waste]*2, 20]]
        structure= list()
        structure.append([bt1,])
        structure.append([bt2,])
        dlg= dialog(self,settings = {'Title': 'Scatter Chart Data' ,
                                     '_size': wx.Size(300,500)},  struct= structure)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        values= dlg.GetValue()
        dlg.Destroy()

        pairs= values[0]
        if len(pairs) == 0:
            return
        self.log.write('pairs= '+ pairs.__str__(), False)

        data= [(self.grid.GetCol(colX), self.grid.GetCol(colY), colX +' VS ' +colY) for (colX,colY) in pairs]
        self.log.write("data= [(grid.GetCol(colX), grid.GetCol(colY), colX +' VS ' +colY) for (colX,colY) in pairs]", False)

        plt= plot(parent= self,
                  typePlot= 'plotScatter',
                  data2plot= data,
                  xlabel= 'X data',
                  ylabel= 'Y data',
                  title= 'Scatter Plot')
        self.log.write('''plt= plot(parent= None,
                  typePlot= 'plotScatter',
                  data2plot= data,
                  xlabel= 'X data',
                  ylabel= 'Y data',
                  title= 'Scatter Plot')''', False)

        plt.Show()
        self.log.write('plt.Show()', False)

    def GoBoxWhiskerPlot(self,evt):
        self.log.write('Box & Whisker')
        waste, colnums = self.grid.GetUsedCols()
        self.log.write('waste, colnums = grid.GetUsedCols()', False)
        if colnums == []:
            self.SetStatusText('You need some data to draw a graph!')
            return
        selection = data2Plotdiaglog(self,waste)
        if selection.ShowModal() != wx.ID_OK:
            selection.Destroy()
            return

        selectedcols = selection.getData()
        selection.Destroy()
        if len(selectedcols) == 0:
            self.SetStatusText('You need to select some data to draw a graph!')
            return
        self.log.write('selectedcols= ' + selectedcols.__str__(), False)

        data = [self.grid.CleanData(cols) for cols in [colnums[m] for m in selectedcols]]
        self.log.write('''data= [grid.CleanData(cols) for cols in [colnums[m] for m in selectedcols]]''', False)

        plt= plot(parent = self, typePlot= 'boxPlot',
                  data2plot= data,
                  xlabel = 'variable',
                  ylabel = 'value',
                  title= 'Box & whisker plot',
                  xtics=  [waste[i] for i in selectedcols] )
        self.log.write('''plt= plot(parent = None, typePlot= 'boxPlot',
                  data2plot= data,
                  xlabel = 'variable',
                  ylabel = 'value',
                  title= 'Box & whisker plot',
                  xtics=  [waste[i] for i in selectedcols] )''', False)

        plt.Show()
        self.log.write('plt.Show()', False)

    def GoAdaptativeBMS(self,evt):
        self.log.write('Adaptative BMS')
        waste, colnums = self.grid.GetUsedCols()
        self.log.write('waste, colnums = grid.GetUsedCols()', False)
        if colnums == []:
            self.SetStatusText('You need some data to draw a graph!')
            return
        selection = data2Plotdiaglog(self,waste)
        if selection.ShowModal() != wx.ID_OK:
            selection.Destroy()
            return
        selectedcols = selection.getData()
        selection.Destroy()
        if len(selectedcols) == 0:
            self.SetStatusText('You need to select some data to draw a graph!')
            return
        self.log.write('selectedcols=  '+selectedcols.__str__(), False)

        data= [self.grid.GetColNumeric(cols) for cols in selectedcols]
        self.log.write('data= [grid.GetColNumeric(cols) for cols in selectedcols]', False)

        plt= plot(parent = self,
                  typePlot = 'AdaptativeBMS',
                  data2plot = data,
                  xlabel = 'variable',
                  ylabel = 'value',
                  title= 'Adaptative BMS plot',
                  xtics=  [waste[i] for i in selectedcols])
        self.log.write('''plt= plot(parent = None,
                  typePlot = 'AdaptativeBMS',
                  data2plot = data,
                  xlabel = 'variable',
                  ylabel = 'value',
                  title= 'Adaptative BMS plot',
                  xtics=  [waste[i] for i in selectedcols])''', False)

        plt.Show()
        self.log.write('plt.Show()', False)

    def GoLinesPlot(self, evt):
        self.log.write('Lines')
        waste, colnums = self.grid.GetUsedCols()
        self.log.write('''waste, colnums = grid.GetUsedCols()''', False)
        if colnums == []:
            self.SetStatusText('You need some data to draw a graph!')
            return
        selection = data2Plotdiaglog(self,waste)
        if selection.ShowModal() != wx.ID_OK:
            selection.Destroy()
            return
        selectedcols = selection.getData()
        self.log.write('selectedcols= ' + selectedcols.__str__(), False)
        selection.Destroy()
        if len(selectedcols) == 0:
            self.SetStatusText('You need to select some data to draw a graph!')
            return

        data = [self.grid.CleanData(cols) for cols in [colnums[m] for m in selectedcols]]
        self.log.write('''data = [grid.CleanData(cols) for cols in [colnums[m] for m in selectedcols]]''', False)

        data = [(range(len(data[i])),data[i],waste[i]) for i in range(len(data))]
        self.log.write('''data = [(range(len(data[i])),data[i],waste[i]) for i in range(len(data))]''', False)

        plt= plot(parent = self, typePlot= 'plotLine',
                  data2plot= data,
                  xlabel = '',
                  ylabel = 'value',
                  title= 'Line plot')
        self.log.write('''plt= plot(parent = None, typePlot= 'plotLine',
                  data2plot= data,
                  xlabel = '',
                  ylabel = 'value',
                  title= 'Line plot')''', False)
        plt.Show()
        self.log.write("plt.Show()", False)

    def GoLinRegressPlot(self, evt):
        self.log.write('Linear Regression')
        waste, colnums = self.grid.GetUsedCols()
        self.log.write('waste, colnums = grid.GetUsedCols()', False)
        if colnums == []:
            self.SetStatusText('You need some data to draw a graph!')
            return
        selection = selectDialogData2plot(self,waste)
        if selection.ShowModal() != wx.ID_OK:
            selection.Destroy()
            return
        (xcol, ycol)= selection.getData()
        self.log.write('(xcol, ycol)= '+ selection.getData().__str__(), False)

        selection.Destroy()

        data= homogenize(*[self.grid.CleanData(cols) for cols in [colnums[i] for i in (xcol,ycol)]])
        self.log.write('''data= homogenize(*[grid.CleanData(cols) for cols in [colnums[i] for i in (xcol,ycol)]])''', False)

        # homogenize data
        data= homogenize(data[0],data[1])
        self.log.write('data= homogenize(data[0],data[1])', False)
        if len(data[0]) != len(data[1]):
            self.SetStatusText('X and Y data must have the same number of elements!')
            return

        plt= plot(parent = self, typePlot= 'plotLinRegress',
                  data2plot= (data[0],data[1],waste[xcol] +u' Vs '+ waste[ycol]),
                  xlabel = waste[xcol], ylabel = waste[ycol],
                  title= 'Linear Regression plot' )
        self.log.write('''plt= plot(parent = None, typePlot= 'plotLinRegress',
                  data2plot= (data[0],data[1],waste[xcol] +u' Vs '+ waste[ycol]),
                  xlabel = waste[xcol], ylabel = waste[ycol],
                  title= 'Linear Regression plot' )''', False)

        plt.Show()
        self.log.write('plt.Show()', False)
        # lin regress removing most disperse data

    def GoProbabilityplot(self, evt):
        self.log.write('Probability')
        ColumnList, colnums= self.grid.GetUsedCols()
        self.log.write('ColumnList, colnums= grid.GetUsedCols()', False)
        if colnums == []:
            self.SetStatusText('You need some data to draw a graph!')
            return
        bt1= ('Choice',(ColumnList,))
        bt2= ('StaticText',('Select The column to analyse',))
        setting= {'Title': "Probability plot"}
        structure= list()
        structure.append([bt1, bt2])
        selection= dialog(settings = setting, struct= structure)
        if selection.ShowModal() != wx.ID_OK:
            selection.Destroy()
            return
        (selectedcol,) = selection.GetValue()
        self.log.write('selectedcols= '+selectedcol.__str__(), False)

        selection.Destroy()
        if selectedcol == None:
            self.SetStatusText('You need to select some data to draw a graph!')
            return

        data = [self.grid.GetColNumeric(selectedcol)]
        self.log.write('data = [grid.GetColNumeric(cols) for cols in selectedcols]', False)

        plt= plot(parent = self, typePlot= 'probabilityPlot',
                  data2plot= data,
                  title=     'Probability Plot',
                  xlabel=    'Order Statistic Medians',
                  ylabel=    'Ordered Values')
        self.log.write('''plt= plot(parent = None, typePlot= 'probabilityPlot',
                  data2plot= data,
                  title=     'Probability Plot',
                  xlabel=    'Order Statistic Medians',
                  ylabel=    'Ordered Values')''', False)

        plt.Show()
        self.log.write('plt.Show()', False)

    ################
    ### chart End
    ################

    def EndApplication(self, evt):
        if self.grid.Saved == False:
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
        setting['Title'] = functionName
        setting['_size'] = wx.Size(220, 200)
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()
        bt1= group('StaticText', ('Select the column to short',) )
        bt2 = group('Choice',    (ColumnList,))
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
                short = stats.shellsort( GetData(colnums[ pos ]) )[0]
                col = numpy.array(short)
                col.shape = (len(col),1)
                colums.append(col)
        else:
            colums = stats.shellsort(GetData(colnums[ values[0] ]))

        # se muestra los resultados
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData(colums[0])
        wx.GetApp().output.addColData(colums[1])
        wx.GetApp().output.addRowData(['','shorted Data','original position'], currRow= 0)
        self.logPanel.write(functionName + ' successful')


#---------------------------------------------------------------------------
# Scripting API is defined here. So far, only basic (but usable!) stuff.
def GetData(column):
    """This function enables the user to extract the data from the data grid.
    The data are "clean" and ready for analysis."""
    return wx.GetApp().frame.grid.CleanData(column)
#--------------------------------------------------------------------------
# main loop
if __name__ == '__main__':
    app = SalStat2App(0)
    app.frame.Show()
    app.MainLoop()
# eof