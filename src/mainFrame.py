__author__ = 'Salstat2 team - selobu at gmail do t com'

# --------- IMPORT FROM THE STANDARD LIBRARY ----------- #
#from local import GetLocaleDict, GetAvailLocales
from encoding.windows32 import killProcess # to exit the app
#from collections import OrderedDict
import sys
import os
from threading import Thread
# -------- END IMPORT FROM THE STANDARD LIBRARY -------- #

# --------------- EXTERNAL LIBRARY IMPORT ---------------#
# wx
# numpy
# scipy
# statlib
# adodbapi
# scikits
# matplotlib

import numpy
import scipy
import wx
from wx.grid import GridCellAttr  # to used the cellattr
#import wx.py # to be used as the script panel
import wx.lib.agw.aui as aui          # advanced user interface manager
from statlib import stats # statistical packages
import adodbapi
import scikits.statsmodels.api as sm ##import statsmodels.api as sm            


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
        import matplotlibbow
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
# ------------- END EXTERNAL LIBRARY IMPORT -------------#


#######-------------------LOCAL IMPORT------------------#######
import sei_glob
from dialogs import formulaBar, Tb1
from newXml.interpretXml import readArchivoGruposAsDict
from plotFunctions import pltobj as plot

# spreadSheet
from gridLib.ntbSheet import NoteBookSheet, CustomNoteBook 
from gridLib import floatRenderer

# import modules to be used into the script panel
from slbTools import homogenize, GroupData # GroupData is used to treat data a a pivot table
from easyDialog import Dialog as dialog # dialog creation
from easyDialog import Ctrl #the controls of the dialog

# statistical functions
import statFunctions

from script import ScriptPanel
from imagenes import imageEmbed
from helpSystem import Navegator
from TreeCtrl import TreePanel,  baseItem

from dialogs import SaveDialog, SaveOneGridDialog, VariablesFrame
from calculator import MyFrame1 as TransformFrame
from dialogs import createPlotSelectionPanel, TbScriptPnl

from encoding.readDongle import readDongleKey
from encoding.basicEncoding import rc4, FromSerialToProgramer
import plotFunctions
#######---------------END LOCAL IMPORT------------------#######


## import some events
from dialogs import EVT_TB1_COPY, EVT_TB1_CUT, EVT_TB1_PASTE
from dialogs import EVT_TB1_UNDO, EVT_TB1_REDO, EVT_TB1_SAVE
from dialogs import EVT_TB1_NEW, EVT_TB1_SAVEAS, EVT_TB1_RESTARTSHELL
from dialogs import EVT_TB1_OPEN, EVT_TB1_OPENWORKDIR, EVT_TB1_HELP
from dialogs import EVT_TB1_CHANGELANG

from dialogs import EVT_TB2_COPY, EVT_TB2_CUT, EVT_TB2_FIND
from dialogs import EVT_TB2_OPEN, EVT_TB2_PASTE, EVT_TB2_REDO
from dialogs import EVT_TB2_NEW, EVT_TB2_RUN, EVT_TB2_SAVE
from dialogs import EVT_TB2_SAVEAS, EVT_TB2_UNDO, EVT_TB2_OPEN

##---------------------------------
## END LIBRARY DEPENDENCIES
##---------------------------------

imagenes = imageEmbed()

def hlp(param):
    # replace the help function
    # it's needed into the script to corectly diplay the
    # help of the statistical functions
    try:
        print param.__doc__
    except:
        return help(param)

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

class LogPanel(wx.Panel):
    def _numLine(self):
        i = 1
        while True:
            yield i
            i += 1

    def __init__( self, parent, *args, **params ):
        self.numLinea = self._numLine()
        wx.Panel.__init__(self, parent, *args, **params)
        bSizer8 = wx.BoxSizer(wx.VERTICAL)
        self.log = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        bSizer8.Add(self.log, 1, wx.EXPAND, 5)
        wx.Log_SetActiveTarget(_MyLog(self.log))
        self.SetSizer(bSizer8)
        self.Layout()

    def writeLine(self, lineaTexto, writem=True):
        '''it writes a text line'''
        #texto= str(self.numLinea.next()) + " >> "
        texto = ''
        #if writem:
        #    texto= str( ">>> ")
        texto += lineaTexto # + "\n"
        # se escribe el texto indicado
        self.log.AppendText(texto)

    def write(self, obj, writem=True):
        if isinstance(obj, (str, unicode)):
            lineaTexto = obj
        else:
            lineaTexto = obj.__str__()
            #if lineaTexto.endswith('\n'):
        #    lineaTexto= lineaTexto[:-1]
        self.writeLine(lineaTexto, writem)

    def clearLog(self):
        self.log.SetValue('')

    def __del__( self ):
        pass

class _checkSum(Thread):
    def run(self, *args, **params):
        ## extracted from iep the Interactive Editor for Python
        """ Check whether a newer version is available. """
        # Get versions available
        self.njhwef2d3()

    def njhwef2d3(self, p=0, j=901):
        import math
        j -= 1
        if j < 1:
            return p
        for i in range(j):
            try:
                p += round(math.sin(( i * 1 + 0) / float(95)), 8)
            except:
                p -= round(j + 5 - j * 1 - 5) ** 2 / float(2)
            finally:
                p += (2 - 3 + 4 * j / j - 2 + 3) / 2 - 2
            self.njhwef2d3(p, i)
        return p
#---------------------------------------------------------------------------
# This is the main interface of application
class MainFrame(wx.Frame):
    from easyDialog.easyDialog import getPath
    def __init__( self, parent, appname ):
        ##from scipy.special import _ufuncs
        """ Main panel """
        # check if the path of the modules exist
        # getting the current path
        currPath= sys.argv[0].decode(sys.getfilesystemencoding())
        self.__env = None
        
        directory= os.path.join( os.path.split(currPath)[0], 'Modules')
        directory= os.path.abspath( directory)
        if not os.path.exists( directory):
            os.makedirs( directory)

        directoryModule= os.path.join(directory,'Custom')
        directoryModule= os.path.abspath(directoryModule)
        if not os.path.exists( directoryModule):
            os.makedirs( directoryModule)

        sys.path.append( directory)
        app= wx.GetApp()
        setattr(app, 'pathDirectoryModule', directoryModule)
        self.path =  None
        self.window = self

        # setting an appropriate size to the frame
        ca = wx.Display().GetClientArea()
        wx.Frame.__init__(self, parent, -1, sei_glob.PROG_NAME,
                          size=wx.Size(ca[2], ca[-1]),
                          pos=( ca[0], ca[1]))

        ########################################
        ####  setting the AUI frame manager ####
        self.m_mgr = aui.AuiManager()
        self.m_mgr.SetManagedWindow(self)
        self.m_mgr.SetArtProvider(aui.AuiDefaultDockArt())
        ########################################

        self.appObj = app

        #set icon for frame needs x-platform separator!
        self.Icon = appname.icon24
        self.DECIMAL_POINT = appname.DECIMAL_POINT

        # creating toolbars
        self.tb1 = Tb1(self, -1, wx.DefaultPosition, wx.DefaultSize, style=0,
                   agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_HORZ_LAYOUT,)
        self.formulaBarPanel = formulaBar(self, -1)
        self.tb2= TbScriptPnl(self, -1, wx.DefaultPosition, wx.DefaultSize, style=0,
                   agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_HORZ_LAYOUT,)

        # creating the status bar
        self.StatusBar = self._createStatusBar()

        # creating the logPanel
        self.log = self.logPanel = LogPanel(self, wx.ID_ANY,
                                            wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.defaultDialogSettings = {'Title': None,
                                      'icon': imagenes.logo16}
        # database explorer panel
        # self.db = SqlSimpleGrid( self, size=(1, 1), firstColEditable= False) # prevent the edition of the __id Column ####

        # set up the datagrid
        self.grid = NoteBookSheet(self)
        self.grid.addPage(gridSize=(1, 1)) #to shown the outputpanel

        # response panel
        self._outputPanel = NoteBookSheet(self)
        self._outputPanel.addPage(gridSize=(1, 1))

        # script panel
        self._scriptPanel = ScriptPanel(self)

        # Redirecting the error messages and the std output to the logPanel
        if not __debug__:
            sys.stderr = self.logPanel
            sys.stdout = self.logPanel

        # Shell
        self.shellPanel = wx.py.sliceshell.SlicesShell(self,
                                                       introText= '#** '+sei_glob.PROG_NAME+' **#',
                                                       showPySlicesTutorial = False,
                                                       showInterpIntro = False,
                                                       enableShellMode = True)

        # put the references into the main app
        appname.setItems(Logg= self.logPanel, grid= self.grid, output= self._outputPanel, plot= plot)
        
        # create the three panels
        self.treePanel = TreePanel( self, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN )
        
        # create menubar
        self.__createMenuUpdadteTree()

        # create plot selection panel
        grapHplotData = self.__autoCreateMenu( plotFunctions, twoGraph=True )
        self.plotSelection = createPlotSelectionPanel( self, size=wx.Size(320, 480) )
        self.plotSelection.createPanels( grapHplotData )

        ###################################
        #########     Toolbars    #########
        # toolbar 1
        self.m_mgr.AddPane(self.tb1, aui.AuiPaneInfo().Name("tb1").
                            Caption( __(u"Basic Operations")).
                            ToolbarPane().Top().Row(1).Position(0).
                            CloseButton(False))
        # toolbar 2: script panel
        self.m_mgr.AddPane(self.tb2, aui.AuiPaneInfo().Name("tb2").
                            Caption( __(u"Script Toolbar")).
                            ToolbarPane().Top().Row(1).Position(1).
                            CloseButton(False))
        # formula bar
        self.m_mgr.AddPane(self.formulaBarPanel,
                           aui.AuiPaneInfo().Name("formulaBar").
                           Caption(__(u"Inspection Tool")).
                           ToolbarPane().Top().Row(1).Position(2).
                           CloseButton(False))
        
        ###################################

        ###################################
        ######   explorer panel   #########
        self.m_mgr.AddPane(self.treePanel,
                           aui.AuiPaneInfo().Name("expnl").Left().CaptionVisible(True).
                           Caption( __(u"Explorer")).
                           MaximizeButton(True).MinimizeButton(True).Resizable(True).
                           PaneBorder(False).CloseButton(False).
                           FloatingSize(wx.Size(220, 400)).
                           MinSize(wx.Size(180, -1))
                           )
        ###################################

        ####################################
        ######   data entry panel   ########
        self.m_mgr.AddPane(self.grid,
                           aui.AuiPaneInfo().Name("dataentry").Centre().CaptionVisible(True).
                           Caption( __(u"Data Entry Panel")).
                           MaximizeButton(True).MinimizeButton(False).Resizable(True).
                           PaneBorder(False).CloseButton(False).
                           FloatingSize(wx.Size(400, 400)).
                           MinSize(wx.Size(240, -1)).Position(0))
        ####################################

        ###################################
        ######    other panels    #########
        # chart selection panel
        self.m_mgr.AddPane(self.plotSelection,
                           aui.AuiPaneInfo().Name(u"charts").Show(False).
                           Right().CaptionVisible(True).Caption( __(u"Chart selection panel")).
                           MinimizeButton(True).Resizable(True).MaximizeButton(True).PinButton().
                           PaneBorder(False).CloseButton(False).MinSize(wx.Size(240, -1)),
                           target=self.m_mgr.GetPane(__("expnl")))
        # output panel
        self.m_mgr.AddPane(self._outputPanel,
                           aui.AuiPaneInfo().Name(u"outputPanel").
                           Right().CaptionVisible(True).Caption( __("Output Panel")).
                           MinimizeButton(True).Resizable(True).MaximizeButton(True).PinButton().Show(True).
                           PaneBorder(False).CloseButton(False).MinSize(wx.Size(240, -1)).Show(True),)
        # scripting panel
        self.m_mgr.AddPane(self._scriptPanel,
                           aui.AuiPaneInfo().Name(u'scriptPanel').Caption( __(u"Script Panel")).
                           CaptionVisible(True).PinButton().Show(True).
                           FloatingSize(wx.Size(400, 500)).
                           MinimizeButton(True).Resizable(True).MaximizeButton(True).
                           PaneBorder(False).CloseButton(False).
                           BestSize(wx.Size(400, -1)).MinSize(wx.Size(240, -1)).Show(True),
                           target=self.m_mgr.GetPane(__(u"outputPanel")))
        ###################################

        ###################################
        ######     buttom panels    #######
        # shell panel
        self.m_mgr.AddPane(self.shellPanel,
                           aui.AuiPaneInfo().Name(u"shellpnl").Caption( __(u"Shell panel")).
                           DefaultPane().Bottom().CloseButton(False).MaximizeButton(True).
                           MinimizeButton().PinButton().Resizable(True).
                           Dock().FloatingSize(wx.Size(260, 200)).
                           PaneBorder(False).CaptionVisible(True).
                           BestSize(wx.Size(-1, 150)).Show(True))
        # log panel
        self.m_mgr.AddPane(self.logPanel,
                           aui.AuiPaneInfo().Name(u"lgpnl").Caption( __("Log Panel")).
                           DefaultPane().Bottom().CloseButton(False).MaximizeButton(True).
                           MinimizeButton().PinButton().Resizable(True).
                           Dock().FloatingSize(wx.Size(260, 200)).
                           PaneBorder(False).CaptionVisible(True).
                           BestSize(wx.Size(-1, 150)))
        ###################################

        # to identify the current panel
        self.currPanel = None

        # allowing the shell access to the selected objects
        env= self._sendObj2Shell( self.shellPanel)

        #setting the env into the scriptpanel pages
        self._scriptPanel.setEnv( env)
        self._sendObj2Shell( self._scriptPanel)

        self._BindEvents()

        # check the default preferences for DefaultPerspective Stored value
        _dp = wx.GetApp().GetPreferences("DefaultPerspective")
        if _dp == None:
            # if None then save the default Perspective
            _pp = self.m_mgr.SavePerspective()
            wx.GetApp().SetPreferences({"DefaultPerspective": _pp})
            _dp = wx.GetApp().GetPreferences("DefaultPerspective")
        else:
            self.m_mgr.LoadPerspective(_dp)
            self.m_mgr.Update()

        ###########################################
        ########   Dongle key checking   ##########
        self.timers = list()
        sequence = self._generateSequence()
        sequence = self._fixSequence(sequence)
        for timeval in sequence:
            self.timers.append(wx.PyTimer(self.checkDongle))
            self.timers[-1].Start(timeval)
        ###########################################
        
        self.Center()
        self.m_mgr.Update()

    def _clearLayout(self):
        _pp = None
        _dp = None
        wx.GetApp().SetPreferences({"DefaultPerspective": _pp})
        wx.GetApp().SetPreferences({"currentPerspective": _dp})

    def _showHidePanel(self, panelName):
        """To show or hide the selected panel"""
        panels = self.m_mgr.GetAllPanes()
        found = False
        for panel in panels:
            if panel.name == panelName: #caption
                found = True
                break
        if not found:
            return
            ##self.m_mgr.Update()
        if panel.IsShown():
            panel.Show(False)
        else:
            panel.Show(True)
            ##self.m_mgr.Repaint()
        self.m_mgr.Update()

    def __showAllPanels(self):
        for panel in self.m_mgr.GetAllPanes():
            panel.Show(True)
        self.m_mgr.Repaint()
        self.m_mgr.Update()

    def _fixSequence( self, sequence ):
        newsequence = [sequence.pop(0)]
        for dat in sequence:
            newsequence.append(newsequence[-1] + dat)
        return newsequence

    def _generateSequence(self, lista=None, start=180000):# 180 seconds
        if lista == None:
            lista = list()

        if start > 100:
            lista.append(start)
        elif len(lista) < 35:
            lista.append(1000)
        else:
            lista.append(1000)
            return

        self._generateSequence(lista, start / 2)

        return lista

    def checkDongle(self):
        return True
        if not readDongleKey():
            # The dongle it's not pressent
            thread = _checkSum()
            thread.setDaemon(True)
            thread.start()
            return False
        else:
            # the dongle key is pressent
            return True

    def _updatetree(self, tree, data):
        tree.treelist = data

    def _createStatusBar(self):
        StatusBar= self.CreateStatusBar(3)
        StatusBar.SetStatusText('cells Selected:   ' + 'count:      ' + 'sum:    ', 1)
        StatusBar.SetStatusText(sei_glob.PROG_NAME, 2)
        return StatusBar

    def _gridSetRenderer(self, grid):
        '''setting the renderer to the grid'''
        attr = GridCellAttr()
        #editor= wx.grid.GridCellFloatEditor()
        #attr.SetEditor(editor)
        renderer = floatRenderer(4)
        attr.SetRenderer(renderer)
        self.floatCellAttr = attr

        for colNumber in range(grid.NumberCols):
            grid.SetColAttr(colNumber, self.floatCellAttr)

        if wx.Platform == '__WXMAC__':
            grid.SetGridLineColour("#b7b7b7")
            grid.SetLabelBackgroundColour("#d2d2d2")
            grid.SetLabelTextColour("#444444")

    def _sendObj2Shell(self, shell):
        if self.__env == None:
            # making available useful object to the shell
            import dict2xml
            env = {'cls':    self.logPanel.clearLog,
                   'grid':   self.grid,
                   'col':    self.grid.GetCol,
                   'plot':   self.appObj.plot,
                   'report': self.appObj.output,
                   'numpy':  numpy,
                   'dialog': dialog,
                   'Ctrl':   Ctrl,
                   'group':  GroupData,
                   'OK':     wx.ID_OK,
                   'homogenize': homogenize,
                   'scipy':  scipy,
                   'stats':  stats,
                   'getPath':self.getPath,
                   'help':   hlp,
                   'sm':     sm, # statmodels
                   'adodbapi': adodbapi,
                   'dict2xml': dict2xml,
                   #'db':     self.db, # mdb manipulation
            }
            # path of modules
            pathInit = sys.argv[0].decode( sys.getfilesystemencoding())
            ##pathModules = os.path.join( pathInit, 'Modules')
            ##sys.path.append( pathModules)
            # Add the path of modules

            if wx.Platform == '__WXMSW__':
                #interactively work with ms excel under windows os
                from xl import Xl
                from access import ACCESS
                env['EXCEL'] = Xl
                import win32com.client
                env['ACCESS']= ACCESS
            self.__env = env
        shell.interp.locals = self.__env
        return self.__env

    def _restartShell(self, evt):
        # to restart the shell panel
        self.shellPanel.clear()
        self._sendObj2Shell( self.shellPanel)
        evt.Skip()

    def __autoCreateMenuItemFromModule(self, module, twoGraph=False):
        import importlib
        # automatically creates a menu related with a specified module
        groups = module.__all__
        subgroup = baseItem(text= module.__name__)
        for group in groups:
            try:
                attr= importlib.import_module(module.__name__+'.'+group)
                result = baseItem( text= __(attr.__name__))
            except:
                print "Error importing "+ module.__name__+'.'+group
                continue
            for item in attr.__all__:
                fnc = getattr( attr, item)
                if twoGraph:
                    item= baseItem( text= __(fnc.name), image= fnc.image,
                                    callback= getattr(fnc(), 'showGui'), id= fnc.id)
                else:
                    item= baseItem( text= __(fnc.name), image= fnc.icon,
                                    callback= getattr(fnc(), 'showGui'), id= fnc.id)
                result.addchild(item)
            subgroup.addchild( result)
        return subgroup

    def __autoCreateMenu(self, module, twoGraph=False):
        import importlib
        # automatically creates a menu related with a specified module
        groups = module.__all__
        subgroup = list()
        for group in groups:
            try:
                attr= importlib.import_module(module.__name__+'.'+group)
                #attr = getattr(module, group)
            except:
                continue
            result = list()
            for item in attr.__all__:
                fnc = getattr(attr, item)
                if twoGraph:
                    result.append(( __(fnc.name), fnc.image, getattr(fnc(), 'showGui'), fnc.id))
                else:
                    result.append(( __(fnc.name), fnc.icon, getattr(fnc(), 'showGui'), fnc.id))
            subgroup.append(( __(attr.__name__), result))
        return subgroup

    def __createMenuUpdadteTree(self):
        import importlib
        # Get icons for toolbar
        imag = imageEmbed()
        NewIcon = imag.exporCsv
        OpenIcon = imag.folder
        SaveIcon = imag.disk
        SaveAsIcon = imag.save2disk
        CutIcon = imag.edit_cut
        CopyIcon = imag.edit_copy
        PasteIcon = imag.edit_paste
        ExitIcon = imag.stop
        #set up menus
        menuBar = wx.MenuBar()

        # to be used for statistical menu autocreation
        import statFunctions
        import plotFunctions

        # including the folder modules
        # try to import all the modules from the Modules Ditfrom Modules import Custom

        # creating the first base
        datExplorer = baseItem( text= 'Main',)
        # creating the first group of data
        FileGroup = baseItem(text= __("&File"), image= NewIcon, callback= None)
        # creating the childs of the filegroup
        items = list()
        items.append( baseItem( text= __("&New Data\tCtrl-N"), image= NewIcon, callback= self.grid.createNewTable))
        items.append( baseItem( text= __("&Open...\tCtrl-O"), image= NewIcon, callback= self.grid.LoadFile))
        items.append( baseItem( text= __("&Save\tCtrl-S"), image= SaveIcon, callback= self.grid.onSave))
        items.append( baseItem( text= __("Save &As...\tCtrl-Shift-S"), image= SaveAsIcon, callback= self.grid.SaveXlsAs))
        items.append( baseItem( text= __("E&xit\tCtrl-Q"), image=  ExitIcon, callback= self.Destroy))
        for item in items:
            FileGroup.addchild(item)
        datExplorer.addchild( FileGroup)
        # Edit group:
        EditGroup= baseItem( text= __("Edit"), )
        items= list()
        items.append( baseItem( text= __("Cut"), image= CutIcon, callback= self.tb1.CutData) )
        items.append( baseItem( text= __("Copy"), image= CopyIcon , callback= self.tb1.CopyData) )
        items.append( baseItem( text= __("Paste"), image= PasteIcon, callback= self.tb1.PasteData) )
        items.append( baseItem( text= __("Select All"), callback= self.tb1.SelectAllCells))
        items.append( baseItem( text= __("Delete Current Column"), callback= self.tb1.DeleteCurrentCol))
        items.append( baseItem( text= __("Delete Current Row"), callback= self.tb1.DeleteCurrentRow))
        for item in items:
            EditGroup.addchild(item)
        datExplorer.addchild( EditGroup)
        # Preparaton group:
        PrepGroup= baseItem( text= __("Preparation"), image= NewIcon)
        items= list()
        items.append( baseItem( text=  __("Transform Data"), callback= self.GoTransformData) )
        items.append( baseItem( text= __("short data"), callback= self.shortData) )
        items.append( baseItem( text= __("Pivot Table"), callback= self.GoPivotTable) )
        for item in items:
            PrepGroup.addchild(item)
        datExplorer.addchild( PrepGroup)
        # Edit group:
        HelpGroup= baseItem( text= __("Help"), )
        item1=   baseItem( text= __("Preferences"))
        item1_1= baseItem( text= __("Variables..."), callback= self.GoVariablesFrame)
        item1_2= baseItem( text=  __("Add Columns and Rows..."), callback= self.GoEditGrid)
        item1.addchild( item1_1)
        item1.addchild( item1_2)
        item2= baseItem( text= __("Load default perspective"), callback= self.onDefaultPerspective)
        item3= baseItem( text= __("About..."), image= imag.icon16,callback= self.ShowAbout)
        HelpGroup.addchild( item1)
        HelpGroup.addchild( item2)
        HelpGroup.addchild( item3)

        datExplorer.addchild( self.__autoCreateMenuItemFromModule(statFunctions))
        datExplorer.addchild( self.__autoCreateMenuItemFromModule(plotFunctions))
        # dinamically calling the modules
        modules= baseItem( text= 'Modules')
        import Modules
        for mod in Modules.__all__:
            try:
                subMod= importlib.import_module( Modules.__name__+'.'+mod)
                subMod.__name__= mod
            except AssertionError as e:
                print e.message
                continue
            modules.addchild( self.__autoCreateMenuItemFromModule(subMod))
        datExplorer.addchild( modules)
        datExplorer.addchild( HelpGroup)
        # updating the tree
        self._updatetree( self.treePanel, datExplorer)

        statisticalMenus = self.__autoCreateMenu( statFunctions)
        plotMenus = self.__autoCreateMenu( plotFunctions)
        dat1 = (
                ( __("&File"),
                 ([ __("&New Data\tCtrl-N"), NewIcon, self.grid.createNewTable, wx.ID_NEW],
                  [ __("&Open...\tCtrl-O"), OpenIcon, self.grid.LoadFile, wx.ID_OPEN],
                  [u"--"],
                  [ __("&Save\tCtrl-S"), SaveIcon, self.grid.onSave, wx.ID_SAVE],
                  [ __("Save &As...\tCtrl-Shift-S"), SaveAsIcon, self.grid.onSaveAs, wx.ID_SAVEAS],
                  [u"--"],
                  [ __("E&xit\tCtrl-Q"), ExitIcon, self.Destroy, wx.ID_EXIT],
                 )),

                ( __("&Edit"),
                 ([ __("Cu&t"), CutIcon, self.tb1.CutData, wx.ID_CUT],
                  [ __("&Copy"), CopyIcon, self.tb1.CopyData, wx.ID_COPY],
                  [ __("&Paste"), PasteIcon, self.tb1.PasteData, wx.ID_PASTE],
                  [u"--"],
                  [ __("Select &All\tCtrl-A"), None, self.tb1.SelectAllCells, wx.ID_SELECTALL],
                  ##["&Find and Replace...\\tCtrl-F",  FindRIcon,     self.GoFindDialog,     wx.ID_REPLACE],
                  [u"--"],
                  [ __("Delete Current Column"), None, self.tb1.DeleteCurrentCol, None],
                  [ __("Delete Current Row"), None, self.tb1.DeleteCurrentRow, None],)),

                ( __("P&reparation"),
                 ([ __("Transform Data"), None, self.GoTransformData, None],
                  [ __("short data"), None, self.shortData, None],
                  [ __("Pivot Table"), None, self.GoPivotTable, None],)),

                ( __("S&tatistics"),
                 statisticalMenus),

                ( __("&Graph"),
                 plotMenus),

                ( __("&Help"),
                  (( __("&Preferences"),
                   (( __("Variables..."), None, self.GoVariablesFrame, None ),
                    [ __("Add Columns and Rows..."), None, self.GoEditGrid, None],
                    [__("Change lenguaje"), None, self.GoChangeLenguaje, None],
                    [ __("Load default perspective"), None, self.onDefaultPerspective, None],)),
                  [u"--"],
                  ( __("Check for a new version"), None, wx.GetApp()._checkUpdates, None),
                  ( __("Give us some feedback"), None, wx.GetApp()._getFeedBack, None),
                  [u"--"],
                  ( __("Visit The blog of Sei"), None, wx.GetApp()._visitBlog, None),
                  ( __("&About..."), imag.icon16, self.ShowAbout, wx.ID_ABOUT),
                 )),
                )

        self.__createMenu(dat1, menuBar)
        self.SetMenuBar(menuBar)

    def __createMenu(self, data, parent):
        if len(data) == 1:
            if data[0] == u"--":
                parent.AppendSeparator()
                return
        elif len(data) == 4:
            if not isinstance(data[2], (list, tuple)):
                if data[3] != None:
                    item = wx.MenuItem(parent, data[3], data[0])
                else:
                    item = wx.MenuItem(parent, wx.ID_ANY, data[0])
                if data[1] != None:
                    item.SetBitmap(data[1])
                if data[3] != None and data[2] != None:
                    self.Bind(wx.EVT_MENU, data[2], id=data[3])
                if data[2] != None and data[3] == None:
                    self.Bind(wx.EVT_MENU, data[2], id=item.GetId())
                parent.AppendItem(item)
                return
        for item in data:
            if len(item) in [1, 4]:
                self.__createMenu(item, parent)
                continue
            menu = wx.Menu()
            if type(parent) == type(wx.Menu()):
                parent.AppendSubMenu(menu, item[0])
            elif type(parent) == type(wx.MenuBar()):
                parent.Append(menu, item[0])
            self.__createMenu(item[1], menu)

        if wx.Platform == "__WXMAC__":
            wx.GetApp().SetMacHelpMenuTitleName( __("&Help"))
            # Allow spell checking in cells. While enabled by a wx configuration, this is done by Mac OS X, and appears
            # to have been deprecated by Apple in OS X Mountain Lion according to wxPython Devs. It had been left in
            # since it is still useful for pre-Mountain Lion users. It appears to have been replaced at the OS X level
            # by voice entry (which works well using Siri!)
            wx.SystemOptions.SetOptionInt(u"mac.textcontrol-use-spell-checker", 1)

    def _BindEvents(self):
        #-----------------
        # tb1 toolbar callbacks
        self.Bind(EVT_TB1_CUT,    self.OnCut )
        self.Bind(EVT_TB1_COPY,   self.OnCopy )
        self.Bind(EVT_TB1_PASTE,  self.OnPaste )
        self.Bind(EVT_TB1_UNDO,   self.OnUndo )
        self.Bind(EVT_TB1_REDO,   self.OnRedo )
        self.Bind(EVT_TB1_SAVE,   self.OnSave )
        self.Bind(EVT_TB1_NEW,    self.OnNew )
        self.Bind(EVT_TB1_SAVEAS, self.OnSaveAs )
        self.Bind(EVT_TB1_RESTARTSHELL, self._restartShell)
        self.Bind(EVT_TB1_OPEN,   self.OnOpen )
        self.Bind(EVT_TB1_OPENWORKDIR, self.OpenWorkDir)
        self.Bind(EVT_TB1_HELP,  self.GoOnlyneHelp)
        self.Bind(EVT_TB1_CHANGELANG, self.OnChangeLang)
        
        # tb2 toolbar callbacks
        self.Bind(EVT_TB2_FIND,   self.OnScriptFind )
        self.Bind(EVT_TB2_RUN,   self.OnScriptRun )
        self.Bind(EVT_TB2_CUT,    self.OnScriptCut )
        self.Bind(EVT_TB2_COPY,   self.OnScriptCopy )
        self.Bind(EVT_TB2_PASTE,  self.OnScriptPaste )
        self.Bind(EVT_TB2_UNDO,   self.OnScriptUndo )
        self.Bind(EVT_TB2_REDO,   self.OnScriptRedo )
        self.Bind(EVT_TB2_SAVE,   self.OnScriptSave )
        self.Bind(EVT_TB2_NEW,    self.OnScriptNew )
        self.Bind(EVT_TB2_SAVEAS, self.OnScriptSaveAs )
        self.Bind(EVT_TB2_OPEN,   self.OnScriptOpen )
        
        
        ### self.Bind( wx.EVT_MENU, self.GoVariablesFrame,  id= self.bt9.GetId())
        # controlling the expansion of the notebook
        self._outputPanel.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self._outputPanel.delPage)
        self.grid.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.grid.delPage)
        self.Bind(wx.EVT_CLOSE , self.OnClose)
        self.sig = self.siguiente()
    
    # script toolbar callback
    def OnScriptRun(self, evt):
        self._scriptPanel.runScript(evt)
        evt.Skip()
    def OnScriptFind(self, evt):
        self._scriptPanel.OnshowFindDlg(evt)
        evt.Skip()
    def OnScriptCut(self, evt):
        self._scriptPanel.CutSelection(evt)
        evt.Skip()
    def OnScriptCopy(self, evt):
        self._scriptPanel.CopySelection(evt)
        evt.Skip()
    def OnScriptPaste(self, evt):
        self._scriptPanel.PasteSelection(evt)
        evt.Skip()
    def OnScriptUndo(self, evt):
        self._scriptPanel.undo(evt)
        evt.Skip()
    def OnScriptRedo(self, evt):
        self._scriptPanel.redo(evt)
        evt.Skip()
    def OnScriptSave(self, evt):
        self._scriptPanel.SaveScript(evt)
        evt.Skip()
    def OnScriptNew(self, evt):
        self._scriptPanel.newScript(evt)
        evt.Skip()
    def OnScriptSaveAs(self, evt):
        self._scriptPanel.SaveScriptAs(evt)
        evt.Skip()
    def OnScriptOpen(self, evt):
        self._scriptPanel.loadScript(evt)
        evt.Skip()
    @property
    def lastObject(self):
        grid= self.formulaBarPanel.lastObject
        # check if there is a selectd object also if the object still exist
        if grid== None or str(type(grid)) == "<class 'wx._core._wxPyDeadObject'>":
            grid= self.grid
        return grid

    # toolbar callback
    def OnChangeLang(self, evt):
        allPreferences = dict()
        
        allPreferences["Language"] = evt.lang
        print __("selected languaje %s")%evt.lang
        print __("you have to restart the app to watch the changes")
        app= wx.GetApp()
        app.SetPreferences(allPreferences)
        # clear the saved layout to update the labels
        self._clearLayout()
        app.SetPreferences({"LenguageHasChange": True})
        
    def OpenWorkDir(self, evt):
        path= self.appObj.pathDirectoryModule
        import subprocess
        if sys.platform == 'darwing':
            subprocess.check_call(['open','--', path])
        elif sys.platform == 'linux2':
            subprocess.check_call(['gnome-open','--', path])
        elif sys.platform in ('win32','win64'):
            subprocess.check_call(['explorer', path])
        evt.Skip()
    
    def OnOpen(self, evt):
        self.grid.addPage(gridSize=(1, 1))
        (HasLoad, SheetName) = self.grid.LoadFile(evt)
        if not HasLoad:
            return
        self.grid.changeLabel( newLabel=SheetName)
        evt.Skip()
        
    def OnCut(self, evt):
        grid= self.lastObject
        grid.CutData(evt)
        evt.Skip()
        
    def OnCopy(self, evt):
        grid= self.lastObject
        grid.CopyData(evt)
        evt.Skip()
        
    def OnPaste(self, evt):
        grid= self.lastObject
        grid.OnPaste()
        evt.Skip()
        
    def OnUndo(self, evt):
        grid= self.lastObject
        grid.Undo(evt)
        evt.Skip()
        
    def OnRedo(self, evt):
        grid= self.lastObject
        grid.Redo(evt)
        evt.Skip()
        
    def OnSave(self, evt):
        grid= self.lastObject
        grid.onSave(evt)
        evt.Skip()
        
    def OnSaveAs(self, evt):
        grid= self.lastObject
        grid.SaveXlsAs(evt)
        evt.Skip()
    
    def OnNew(self, evt):
        grid= self.lastObject
        grid.createNewTable( evt)
        evt.Skip()
        
    def __OnitemFileExplorerActivated(self, evt):
        """Once the user select one file of the system"""

        evt.Skip()
    def siguiente(self):
        i = 0
        while 1:
            yield i
            i += 1

    def _evalstat(self, evt, stat):
        stat().showGui()

    def _OnNtbDbClick(self, evt):
        for pane in self.m_mgr.GetAllPanes():
            if pane.caption == __(u"Data Entry Panel"):
                break
        if not pane.IsMaximized():
            self.m_mgr.MaximizePane(pane)
        else:
            self.m_mgr.RestorePane(pane)
        self.m_mgr.Repaint()
        self.m_mgr.Update()

    #def loadMsql(self, evt, *args, **params):
        #structure = list()
        #stxt1 = ('StaticText', (u'Host:      ',))
        #stxt2 = ('StaticText', (u'Port:      ',))
        #stxt3 = ('StaticText', (u'User Name: ',))
        #stxt4 = ('StaticText', (u'Password:  ',))
        #stxt5 = ('StaticText', (u'Database:  ',))
        #txt1 = ('TextCtrl', ('',))
        #txt2 = ('NumTextCtrl', ())

        #structure.append([stxt1, txt1, ])
        #structure.append([stxt2, txt2, ])
        #structure.append([stxt5, txt1, ])
        #structure.append([stxt3, txt1, ])
        #structure.append([stxt4, txt1, ])

        #dlg = dialog(parent=None, struct=structure)
        #if dlg.ShowModal() == wx.ID_OK:
            #values = dlg.GetValue()
            #print values
        #else:
            #dlg.Destroy()
            #return
        #dlg.Destroy()

        #host = values.pop(0).__str__()
        #port = int(values.pop(0)).__str__()
        #user = values.pop(0).__str__()
        #password = values.pop(0).__str__()
        #dbname = values.pop(0).__str__()

        #from sqlalchemy import create_engine
        #import mysql

        #engine = create_engine(
            #"mysql+mysqlconnector://" + user + ":" + password + "@" + host + ":" + port + "/" + dbname,
            #echo=False, encoding='utf8')
        #self._loadDb(engine)

    def onDefaultPerspective(self, evt):
        defaultPerspective = wx.GetApp().GetPreferences(preferenceKey="DefaultPerspective")
        self.m_mgr.LoadPerspective(defaultPerspective)
        wx.GetApp().SetPreferences({"currentPerspective": defaultPerspective})
        evt.Skip()

    def GoClearData(self, evt):
        if not self.grid.hasSaved:
            # display discard dialog
            dlg = wx.MessageDialog(None, __(u"Do you wish to save now?"),
                                   __(u"You have Unsaved Data"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
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
            self.grid.DeleteCols(pos=0, numCols=int(self.grid.NumberCols))
        except wx._core.PyAssertionError:
            pass

        try:
            self.grid.DeleteRows(pos=0, numRows=int(self.grid.NumberRows))
        except wx._core.PyAssertionError:
            pass

        self.grid.AppendRows(500)
        self.grid.AppendCols(50)
        # <p> updating the renderer
        self._gridSetRenderer(self.grid)
        # /<p>

        self.grid.path = None
        self.grid.hasSaved = False
        self.m_mgr.Update()
        # /<p>
        # emptying the undo redo

    def GoFindDialog(self, evt):
        # Shows the find & replace dialog
        # NOTE - this doesn't appear to work on the grid, so I might be missing something...
        data = wx.FindReplaceData()
        dlg = wx.FindReplaceDialog(self.grid, data, __(u"Find and Replace"), \
                                   wx.FR_REPLACEDIALOG)
        dlg.data = data
        dlg.Show(True)
        
    def GoChangeLenguaje(self, evt):
        # shows the gui to change the lenguaje
        bnt1= Ctrl.SpinCtrl(0,100,1)
        pass

    def GoEditGrid(self, evt):
        #shows dialog for editing the data grid
        btn1 = Ctrl.SpinCtrl(0, 5000, 0)
        btn2 = Ctrl.StaticText(__(u"Change Grid Size"))
        btn3 = Ctrl.StaticText(__(u"Add Columns"))
        btn4 = Ctrl.StaticText(__(u"Add Rows"))
        struct = [[btn2],[btn1, btn3],[btn1, btn4]]
        
        dlg = dialog(self)
        dlg.struct= struct
        dlg.title= __(u"Change Grid size")

        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
        else:
            dlg.Destroy()
            return
        colswanted = values[0]
        rowswanted = values[1]
        #editorRederer = wx.GetApp().frame.floatCellAttr
        grid= wx.GetApp().frame.grid
        grid.AppendCols(colswanted)
        grid.AppendRows(rowswanted)#AddNCells(colswanted, rowswanted, attr=editorRederer)

    def GoVariablesFrame(self, evt):
        # shows Variables dialog
        win = VariablesFrame(wx.GetApp().frame, -1)
        # updating the name of the columns
        win.Show(True)

    def GoGridPrefFrame(self, evt):
        # shows Grid Preferences form
        btn1 = ["SpinCtrl", [5, 90, 5]]
        btn2 = ["StaticText", [__(u"Change the cell Size")]]
        btn3 = ["StaticText", [__(u"Column Width")]]
        btn4 = ["StaticText", [__(u"Row Height")]]
        setting = {"Title": __(u"Change the cell size")}

        struct = list()
        struct.append([btn2])
        struct.append([btn1, btn3])
        struct.append([btn1, btn4])
        dlg = dialog(self, settings=setting, struct=struct)

        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
        else:
            dlg.Destroy()
            return
        colwidth = values[0]
        rowheight = values[1]
        wx.GetApp().frame.grid.SetDefaultColSize(colwidth, True)
        wx.GetApp().frame.grid.SetDefaultRowSize(rowheight, True)
        wx.GetApp().frame.grid.ForceRefresh()

    def GoPivotTable(self, evt):
        from Pivot import PivotFrame
        # current source of data
        cs= self.formulaBarPanel.lastObject
        if cs == None:
            cs= self.grid
        self.__pivotFrame = PivotFrame( wx.GetApp().frame, grid= cs)
        self.__pivotFrame.Show(True)
        
    def GoTransformData(self, evt):
        self.__TransformFrame = TransformFrame(wx.GetApp().frame, -1)
        # current source of data
        cs= self.formulaBarPanel.lastObject
        if cs == None:
            cs= self.grid
        gridCol = cs.GetUsedCols()
        columnNames = gridCol[0]
        columnNumbers = gridCol[1]
        self.__TransformFrame.setAvailableColumns(columnNames)
        # send objects to the shell
        self._sendObj2Shell(self.__TransformFrame.scriptPanel)
        # making the callback of the eval button
        self.__TransformFrame.pusButtonList[-1].Bind(wx.EVT_BUTTON, self.__OnTransformPanelEVAL)
        self.__TransformFrame.Show(True)

    def __OnTransformPanelEVAL(self, evt):
        responseCol, expresion, foundVarNames = self.__TransformFrame.GetValue()
        import scikits.statsmodels.api as sm 
        # defining the variables from the current grid
        import shapefile
        import adodbapi
        env = {'cls':    self.logPanel.clearLog,
               'grid':   self.grid,
               'col':    self.grid.GetCol,
               'show':   self.logPanel.write,
               'plot':   self.appObj.plot,
               'report': self.appObj.output,
               'numpy':  numpy,
               'dialog': dialog,
               'group':  GroupData,
               'OK':     wx.ID_OK,
               'homogenize': homogenize,
               'scipy':  scipy,
               'stats':  stats,
               'getPath':self.getPath,
               'help':   hlp,
               'sm':     sm, # statmodels
               'sh':     shapefile,
               'adodbapi': adodbapi, # mdb manipulation
               ##'db':     self.db,
        }

        cs= self.formulaBarPanel.lastObject
        if cs == None:
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

        # removing the nonValid Positions detected
        #nonValidPos.reverse()
        #numListas= len(listcolnames)
        #for poslist in range(numListas):
        #    for pos in nonValidPos:
        #        listcolnames[poslist].pop(pos)

        for colName in allowColumnNames:
            env[colName] = numpy.array(listcolnames.pop(0))

        # evaluating the expresion
        #code = compile(expresion, '<string>', 'exec',globals= env, locals= localVar)
        #ns = {}
        #exec code in ns

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
        from About import AboutDlg
        dlg= AboutDlg(self)
        dlg.ShowModal()

    def GoHelpSystem( self, evt):
        # shows the "wizard" in the help box
        win = Navegator(wx.GetApp().frame, )
        win.Show(True)

    def GoOnlyneHelp( self, evt):
        import webbrowser

        webbrowser.open(
            r"http://code.google.com/p/salstat-statistics-package-2/wiki/Documentation?ts=1344287549&updated=Documentation")

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

    def OnClose(self, evt):
        app= wx.GetApp()
        # check if the lenguaje has changed
        if app.GetPreferences("LenguageHasChange"):
            # clear the default perspective
            app.SetPreferences({"DefaultPerspective": None})
            app.SetPreferences({"LenguageHasChange": False})
        else:
            _pp = self.m_mgr.SavePerspective()
            app.SetPreferences({"DefaultPerspective": _pp})
        self.Destroy(evt) # wx.GetApp().frame.Destroy()
        if self.checkDongle():
            killProcess(sei_glob.PROG_NAME)
        #if len(self.grid) == 0:
        #    wx.GetApp().frame.Destroy()
        #    return
        #try:
        #    saved = self.grid.hasSaved
        #except AttributeError:
        #    # if there aren't active sheets
        #    saved = True
        #if saved == False:
        #    # checking if there is data to be saved
        #    if len(self.grid.GetUsedCols()[0]) != 0:
        #        win = SaveDialog(self)
        #        win.Show(True)
        #    else:
        #        pass ##self.Destroy() # wx.GetApp().frame.Destroy()
        #else:
        #    pass

    def shortData(self, evt):
        functionName = "short"
        useNumpy = False
        requiredcols = None
        group = lambda x, y: (x, y)
        setting = self.defaultDialogSettings
        setting["Title"] = functionName
        setting["_size"] = wx.Size(220, 200)
        ColumnList, colnums = wx.GetApp().frame.grid.GetUsedCols()
        bt1 = group("StaticText", ("Select the column to short",))
        bt2 = group("Choice", (ColumnList,))
        structure = list()
        structure.append([bt1, ])
        structure.append([bt2, ])
        dlg = dialog(settings=setting, struct=structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
            # -------------------
        # changing value strings to numbers
        colNameSelect = values[0]
        if len(colNameSelect) == 0:
            self.logPanel.write("You haven't selected any items!")
            return

        if len(colNameSelect) < None:
            self.logPanel.write("You have to select at least %i columns" % requiredcols)
            return

        values = [[pos for pos, value in enumerate(ColumnList)
                   if value == val
                  ][0]
                  for val in colNameSelect
        ]
        # -------------------
        if useNumpy:
            colums = list()
            for pos in values:
                short = stats.shellsort(self.grid.CleanData(colnums[pos]))[0]
                col = numpy.array(short)
                col.shape = (len(col), 1)
                colums.append(col)
        else:
            colums = stats.shellsort(self.grid.CleanData(colnums[values[0]]))

        # se muestra los resultados
        # wx.GetApp().output.addColData(colNameSelect, functionName)
        # wx.GetApp().output.addColData(colums[0])
        # wx.GetApp().output.addColData(colums[1])
        # wx.GetApp().output.addRowData(['',"shorted Data","original position"], currRow= 0)
        wx.GetApp().grid.PutCol(colNameSelect, colums[0])
        # wx.GetApp().grid.PutCol(colums[0])
        # wx.GetApp().grid.PutCol(colums[1])
        self.logPanel.write(functionName + " successful")

    def Destroy(self, evt, *args, **params):
        self.m_mgr.UnInit()
        super(MainFrame, self).Destroy()
        ## self.Close()
        ## sys.exit()
        evt.Skip()
