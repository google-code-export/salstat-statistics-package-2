# Copyrigth 2014 Sebastian Lopez Buritica selobu@gmail.com

import  wx
import wx.aui
from imagenes import imageEmbed
from openStats import statistics # used in descriptives frame
import math # to be used in transform pane
import numpy
import scipy
import wx.lib.agw.aui as aui
import wx.lib.langlistctrl as langlist
import sys
from sei_glob import *

import wx.lib.newevent

Tb1_New_evt,    EVT_TB1_NEW =    wx.lib.newevent.NewCommandEvent()
Tb1_Save_evt,   EVT_TB1_SAVE =   wx.lib.newevent.NewCommandEvent()
Tb1_SaveAs_evt, EVT_TB1_SAVEAS = wx.lib.newevent.NewCommandEvent()
Tb1_Copy_evt,   EVT_TB1_COPY =   wx.lib.newevent.NewCommandEvent()
Tb1_Paste_evt,  EVT_TB1_PASTE =  wx.lib.newevent.NewCommandEvent()
Tb1_Cut_evt,    EVT_TB1_CUT =    wx.lib.newevent.NewCommandEvent()
Tb1_Undo_evt,   EVT_TB1_UNDO =   wx.lib.newevent.NewCommandEvent()
Tb1_Redo_evt,   EVT_TB1_REDO =   wx.lib.newevent.NewCommandEvent()
Tb1_Open_evt,   EVT_TB1_OPEN =   wx.lib.newevent.NewCommandEvent()
Tb1_Help_evt,   EVT_TB1_HELP =   wx.lib.newevent.NewCommandEvent()
Tb1_ChanLan_evt, EVT_TB1_CHANGELANG =        wx.lib.newevent.NewCommandEvent()
Tb1_OpenWorkDir_evt,  EVT_TB1_OPENWORKDIR =  wx.lib.newevent.NewCommandEvent()
Tb1_RestartShell_evt, EVT_TB1_RESTARTSHELL = wx.lib.newevent.NewCommandEvent()
evtIDOpenWorkDir= wx.NewEventType()
evtIDNew =    wx.NewEventType()
evtIDSave =   wx.NewEventType()
evtIDSaveAs = wx.NewEventType()
evtIDCopy =   wx.NewEventType()
evtIDPaste =  wx.NewEventType()
evtIDCut =    wx.NewEventType()
evtIDUndo =   wx.NewEventType()
evtIDRedo =   wx.NewEventType()
evtIDOpen =   wx.NewEventType()
evtIDHelp =   wx.NewEventType()
evtIDChanLan= wx.NewEventType()
evtIDRestartShell =   wx.NewEventType()

Tb2_Run_evt,    EVT_TB2_RUN =    wx.lib.newevent.NewCommandEvent()
Tb2_New_evt,    EVT_TB2_NEW =    wx.lib.newevent.NewCommandEvent()
Tb2_Load_evt,   EVT_TB2_LOAD =   wx.lib.newevent.NewCommandEvent()
Tb2_Save_evt,   EVT_TB2_SAVE =   wx.lib.newevent.NewCommandEvent()
Tb2_SaveAs_evt, EVT_TB2_SAVEAS = wx.lib.newevent.NewCommandEvent()
Tb2_Undo_evt,   EVT_TB2_UNDO =   wx.lib.newevent.NewCommandEvent()
Tb2_Redo_evt,   EVT_TB2_REDO =   wx.lib.newevent.NewCommandEvent()
Tb2_Cut_evt,    EVT_TB2_CUT =    wx.lib.newevent.NewCommandEvent()
Tb2_Copy_evt,   EVT_TB2_COPY =   wx.lib.newevent.NewCommandEvent()
Tb2_Paste_evt,  EVT_TB2_PASTE =  wx.lib.newevent.NewCommandEvent()
Tb2_Find_evt,   EVT_TB2_FIND =   wx.lib.newevent.NewCommandEvent()
Tb2_Open_evt,   EVT_TB2_OPEN =   wx.lib.newevent.NewCommandEvent()
evtIDTb2Run =   wx.NewEventType()
evtIDTb2New =   wx.NewEventType()
evtIDTb2Load =  wx.NewEventType()
evtIDTb2Save =  wx.NewEventType()
evtIDTb2SaveAs = wx.NewEventType()
evtIDTb2Undo =  wx.NewEventType()
evtIDTb2Redo =  wx.NewEventType()
evtIDTb2Cut =   wx.NewEventType()
evtIDTb2Copy =  wx.NewEventType()
evtIDTb2Paste = wx.NewEventType()
evtIDTb2Find =  wx.NewEventType()

if wx.__version__ != '2.9.4.0':
    from wx import ComboBox as BitmapComboBox # translation control
else:
    from  wx.combo import BitmapComboBox # translation control

from local import GetAvailLocales, GetLangId, GetLocaleDict
from easyDialog.easyDialog import CheckListBox

if wx.Platform == '__WXMSW__':
    wind = 50
else:
    wind = 0

# creating a class to make pairs
#<p> INIT MAKE PAIRS
import  wx.grid as gridlib
class _CustomDataTable( gridlib.PyGridTableBase):
    def __init__( self, columnNames, choiceNames, rowNumber):
        gridlib.PyGridTableBase.__init__( self)

        if isinstance( choiceNames, (str, unicode)):
            choiceNames= [choiceNames]*len( columnNames)

        self.colLabels = columnNames
        group= lambda x,y: x+','+y

        if len( choiceNames) >= 1:
            colsResume= list()
            for choice in choiceNames:
                try:
                    if choice == None:
                        # the selected form correspond to a text editor
                        colsResume.append(None)
                        continue
                except:
                    pass
                colsResume.append( reduce( group,  choice[1:],  choice[0]))

        elif len( choiceNames) == 1:
            colsResume= choiceNames[0]*len(columnNames)
        else:
            raise StandardError( __(u'You input bad type data as choiceNames variable'))

        gvalue= gridlib.GRID_VALUE_CHOICE
        self.dataTypes= list()
        for colResume in colsResume:
            if colResume != None:
                self.dataTypes.append( [gvalue + ":,"+colResume for i in range(len(columnNames))])
            else:
                self.dataTypes.append('string')
        self.data= [[u'' for i in range(len(columnNames))] for j in range(rowNumber)]

    #--------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberRows(self):
        return  len(self.data)

    def GetNumberCols(self):
        return len(self.data[0])

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return True

    # Get/Set values in the table.  The Python version of these
    # methods can handle any data-type, (as long as the Editor and
    # Renderer understands the type too,) not just strings as in the
    # C++ version.
    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        def innerSetValue(row, col, value):
            try:
                self.data[row][col] = value
            except IndexError:
                # add a new row
                self.data.append([''] * self.GetNumberCols())
                innerSetValue(row, col, value)

                # tell the grid we've added a row
                msg = gridlib.GridTableMessage(self,            # The table
                                               gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                                               1                                       # how many
                                               )

                self.GetView().ProcessTableMessage(msg)
        innerSetValue(row, col, value)

    #--------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return self.colLabels[col]

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        return self.dataTypes[col][col]

    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, typeName):
        prev= self.dataTypes[col]
        if prev != 'string':
            prev= prev[col]
            colType = prev.split(':')[0]
        else:
            colTpe= 'string'
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)

class _CustTableGrid(gridlib.Grid):
    def __init__(self, parent, colNames, choices, rowNumber):
        gridlib.Grid.__init__(self, parent, -1)
        table = _CustomDataTable(colNames, choices, rowNumber)
        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(table, True)
        # self.SetRowLabelSize(0)
        self.SetMargins(0,0)
        self.SetRowLabelSize( 40 )
        self.AutoSizeColumns(False)

        gridlib.EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)


    ## I do this because I don't like the default behaviour of not starting the
    ## cell editor on double clicks, but only a second click.
    def OnLeftDClick(self, evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

class makePairs(wx.Panel):
    def __init__(self, parent, id, colNames, choices, rowNumber= 20):
        wx.Panel.__init__(self, parent, id, style=0)

        self.grid = _CustTableGrid(self, colNames, choices, rowNumber)
        #b = wx.Button(self, -1, "Another Control...")
        #b.SetDefault()
        bs = wx.BoxSizer(wx.VERTICAL)
        bs.Add(self.grid, 1, wx.GROW|wx.ALL, 5)
        #bs.Add(b)
        self.SetSizer(bs)

    def GetValue(self ):
        # reading the data by rows and check consistency
        result= list()
        numCols= self.grid.GetNumberCols()
        for row in range(self.grid.GetNumberRows()):
            rowdata= [self.grid.GetCellValue(row,col) for col in range(numCols)]
            if numCols == sum([1 for value in rowdata if value != u'']):
                result.append(rowdata)
        return result

#  END MAKE PAIRS /<p>

# aui notebook wrapper
class auiNotebookWrap( wx.Panel):
    def numPage(self):
        i=1
        while True:
            yield i
            i+= 1
    def __init__( self, parent,id= wx.ID_ANY, *args, **params):
        '''parent, *args of the panel'''
        wx.Panel.__init__(self, parent, id, *args, **params)

        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        self.m_notebook= wx.aui.AuiNotebook( self, wx.ID_ANY,
                                             wx.DefaultPosition, wx.DefaultSize,
                                             wx.aui.AUI_NB_SCROLL_BUTTONS|wx.aui.AUI_NB_TAB_MOVE|
                                             wx.aui.AUI_NB_WINDOWLIST_BUTTON|wx.aui.AUI_NB_BOTTOM|
                                             wx.aui.AUI_NB_TAB_SPLIT)


        self.m_mgr.AddPane( self.m_notebook, wx.aui.AuiPaneInfo().CenterPane().Dock().
                            Resizable(True).FloatingSize( wx.DefaultSize ).
                            DockFixed( True ).Centre().
                            CloseButton(False ) )
        self.npage = self.numPage()
        self.currentPage = None
        self.pageNames= dict()

        self.m_notebook.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnNotebookPageChange)
        self.m_notebook.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.delPage)

        self.Bindded() # call your custom callbacks
        self.Layout()
        self.m_mgr.Update()
        self.Center( )

    # <p> you should override this
    def Bindded(self):
        # add some custom callbacks
        pass
    def addOnePage(self, id= wx.ID_ANY):
        #overwrite this method to create your own custom widget
        return wx.TextCtrl( self, id)
    # end override this /<p>

    # implementing a wrap to the current notebook
    def __getattribute__( self, name):
        '''wraps the funtions to the grid
        emulating a grid control'''
        try:
            return object.__getattribute__( self, name)
        except AttributeError:
            if self.GetPageCount( ) != 0:
                if str(type(self.currentPage)) == "<class 'wx._core._wxPyDeadObject'>":
                    self.currentPage == None
                    return
                currPage= self.currentPage
                return currPage.__getattribute__( name)
            raise AttributeError

    def getPageNames( self):
        return self.pageNames.keys()

    def getHeader( self,pageName):
        if not (pageName in self.pageNames.keys()):
            raise StandardError('The page does not exist')
        page= self.pageNames[pageName]
        return page.getHeader()

    def OnNotebookPageChange( self,evt):
        self.currentPage= self.m_notebook.GetPage( evt.Selection)

    def GetPageCount( self):
        # 21/04/2011
        # retorna el numero de paginas que hay en el notebook
        return self.m_notebook.PageCount

    def addPage( self, data= dict()):
        defaultData = {'name': u''}
        for key, value in data.items():
            if defaultData.has_key(key):
                defaultData[key] = value
        # adiciona una pagina al notebook grid
        newName= defaultData['name'] +'_'+ str(self.npage.next())
        self.pageNames[newName]= self.addOnePage( )
        self.currentPage=  self.pageNames[newName]
        ntb= self.pageNames[newName]
        self.m_notebook.AddPage(ntb, newName, False )
        # se hace activo la pagina adicionada
        self.m_notebook.SetSelection(self.m_notebook.GetPageCount()-1)
        return ntb # retorna el objeto ntb

    def delPage( self, evt, page= None):
        # si no se ingresa un numero de pagina se
        #     considera que se va a borrar la pagina actual
        # las paginas se numeran mediante numeros desde el cero
        if page == None:
            # se considera que la pagina a borrar es la pagina actual
            #self.m_notebook.GetCurrentPage().Destroy() # borra el contenido de la pagina
            if self.m_notebook.GetSelection() > -1:
                self.m_notebook.DeletePage(self.m_notebook.GetSelection())
            return
        page = int(page)
        if page <0:
            return
        if page > self.GetPageCount():
            raise IndexError(__("Page doesn't exist"))
        parent = self.pages[page].GetParent()
        parent.DeletePage(page)

    def newScript(self, event):
        self.addPage()
#

class TbScriptPnl(aui.AuiToolBar):
    def __init__(self, *args,**params):
        aui.AuiToolBar.__init__(self, *args, **params)
        repend_items, append_items = [], []
            
        #self.SetKind(wx.ITEM_SEPARATOR)
        #self.SetKind(wx.ITEM_NORMAL)
        #self.SetId(wx.ID_ANY)
        self.SetLabel(__("Customize..."))
        #if wx.version < "2.9":
        #    tb1= aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
        #                        style = aui.AUI_TB_OVERFLOW | aui.AUI_TB_VERTICAL)
        #else:
        #    tb1= aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
        #                        agwStyle = aui.AUI_TB_OVERFLOW | aui.AUI_TB_VERTICAL)
        imagenes = imageEmbed()
        self.SetToolBitmapSize(wx.Size(16, 16))
        self.bt1= self.AddSimpleTool(wx.ID_ANY, __(u"Run Script") , imagenes.runIcon, __(u"Run Script"), )
        self.AddSeparator()
        self.bt2= self.AddSimpleTool(wx.ID_ANY, __(u"New Script") , imagenes.documentNew, __(u"New Script") )
        self.bt4= self.AddSimpleTool(wx.ID_ANY, __(u"Load Script") , imagenes.folderOpen, __(u"Load Script") )
        self.AddSeparator()
        self.btSave= self.AddSimpleTool(wx.ID_ANY, __(u"Save Script") , imagenes.disk, __(u"Save Script") )
        self.bt3= self.AddSimpleTool(wx.ID_ANY, __(u"Save Script As") , imagenes.save2disk, __(u"Save Script as") )
        self.AddSeparator()
        self.bt8= self.AddSimpleTool(wx.ID_ANY, __(u"Undo"), imagenes.edit_undo, __(u"Undo") )
        self.bt9= self.AddSimpleTool(wx.ID_ANY, __(u"Redo"), imagenes.edit_redo, __(u"Redo") )
        self.AddSeparator()
        self.bt5= self.AddSimpleTool(wx.ID_ANY, __(u"Cut"), imagenes.edit_cut, __(u"Cut") )
        self.bt6= self.AddSimpleTool(wx.ID_ANY, __(u"Copy"), imagenes.edit_copy, __(u"Copy") )
        self.bt7= self.AddSimpleTool(wx.ID_ANY, __(u"Paste"), imagenes.edit_paste, __(u"Paste") )
        self.AddSeparator()
        self.bt10= self.AddSimpleTool(wx.ID_ANY, __(u"Find"), imagenes.find, __(u"Find") )
        #self.SetCustomOverflowItems( prepend_items, append_items)
        #self.SetToolDropDown(wx.ID_ANY, True)
        self.Realize()
        self.Bind(wx.EVT_MENU, self.RunScript,    id= self.bt1.GetId())
        self.Bind(wx.EVT_MENU, self.NewScript,    id= self.bt2.GetId())
        self.Bind(wx.EVT_MENU, self.LoadScript,   id= self.bt4.GetId())
        self.Bind(wx.EVT_MENU, self.SaveScript,   id= self.btSave.GetId())
        self.Bind(wx.EVT_MENU, self.SaveAsScript, id= self.bt3.GetId())
        self.Bind(wx.EVT_MENU, self.Undo,      id= self.bt8.GetId())
        self.Bind(wx.EVT_MENU, self.Redo,      id= self.bt9.GetId())
        self.Bind(wx.EVT_MENU, self.Cut,       id= self.bt5.GetId())
        self.Bind(wx.EVT_MENU, self.Copy,      id= self.bt6.GetId())
        self.Bind(wx.EVT_MENU, self.Paste,     id= self.bt7.GetId())
        self.Bind(wx.EVT_MENU, self.Find,      id= self.bt10.GetId())

    def RunScript(self, evt):
        event = Tb2_Run_evt(evtIDTb2Run)
        wx.PostEvent(self.GetEventHandler(), event)
        evt.Skip()
    def NewScript(self, evt):
        event = Tb2_New_evt(evtIDTb2New)
        wx.PostEvent(self.GetEventHandler(), event)
        evt.Skip()
    def LoadScript(self, evt):
        event = Tb2_Load_evt(evtIDTb2Load)
        wx.PostEvent(self.GetEventHandler(), event)
        evt.Skip()
    def SaveScript(self, evt):
        event = Tb2_Save_evt(evtIDTb2Save)
        wx.PostEvent(self.GetEventHandler(), event)
        evt.Skip()
    def SaveAsScript(self, evt):
        event = Tb2_SaveAs_evt(evtIDTb2SaveAs)
        wx.PostEvent(self.GetEventHandler(), event)
        evt.Skip()
    def Undo(self, evt):
        event = Tb2_Undo_evt(evtIDTb2Undo)
        wx.PostEvent(self.GetEventHandler(), event)
        evt.Skip()
    def Redo(self, evt):
        event = Tb2_Redo_evt(evtIDTb2Redo)
        wx.PostEvent(self.GetEventHandler(), event)
        evt.Skip()
    def Cut(self, evt):
        event = Tb2_Cut_evt(evtIDTb2Cut)
        wx.PostEvent(self.GetEventHandler(), event)
        evt.Skip()
    def Copy(self, evt):
        event = Tb2_Copy_evt(evtIDCopy)
        wx.PostEvent(self.GetEventHandler(), event)
        evt.Skip()
    def Paste(self, evt):
        event = Tb2_Paste_evt(evtIDTb2Paste)
        wx.PostEvent(self.GetEventHandler(), event)
        evt.Skip()
    def Find(self, evt):
        event = Tb2_Find_evt(evtIDTb2Find)
        wx.PostEvent(self.GetEventHandler(), event)
        evt.Skip()


class formulaBar(wx.Panel):#aui.AuiToolBar
    def __init__( self, parent, *args, **params):
        wx.Panel.__init__(self, parent, #aui.AuiToolBar
                          id=wx.ID_ANY,
                          pos=wx.DefaultPosition,
                          size=wx.DefaultSize, )
        self.__LastObject= None # indicate the las object that call this objet
        bSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self._text = u''
        self.lastParent = None
        self.textCtrl1 = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                     wx.TE_CHARWRAP | wx.TE_MULTILINE | wx.TE_RICH2 |
                                     wx.TE_WORDWRAP | wx.NO_BORDER)

        self.textCtrl1.SetMinSize(wx.Size(500, -1))
        self.textCtrl1.SetSize(wx.Size(500, -1))

        bSizer1.Add(self.textCtrl1, 0, 0, 5)

        imag = imageEmbed()
        self.arrowUp = imag.arrowUp
        self.arrowDown = imag.arrowDown
        self.originalSize = self.Size
        self.SetSizer(bSizer1)
        self.toggle = True
        self.Layout()

    def onShown(self):
        fbName = "tb2"
        app= wx.GetApp()
        app.frame._showHidePanel( fbName)

    def _ontogle(self, evt):
        if self.toggle:
            auisize = self.GetSize()
            self.SetSize((auisize[0], auisize[1] + 28))
            self.textCtrl1.SetMinSize(wx.Size(600, 28 * 2))
            self.textCtrl1.SetSize(wx.Size(600, 28 * 2))
            self.Layout()
            self.m_toggleBtn1.Bitmap = self.arrowUp
        else:
            auisize = self.GetSize()
            self.SetSize((auisize[0], auisize[1] - 28))
            self.textCtrl1.SetMinSize(wx.Size(600, 28))
            self.textCtrl1.SetSize(wx.Size(600, 28))
            self.Layout()
            self.m_toggleBtn1.Bitmap = self.arrowDown
        self.toggle = not self.toggle
        evt.Skip()
    @property
    def lastObject(self):
        return self.__LastObject
    @lastObject.setter
    def lastObject(self, lastobj):
        self.__LastObject= lastobj
    @property
    def value(self):
        return self._text
    @value.setter
    def value(self, texto, *args, **params):
        # try to fix to interactibely change the contents of the las selected cell
        if not isinstance(texto, (str, unicode)):
            raise StandardError("only accept string values")
        self._text = texto
        self.textCtrl1.SetValue(texto)

class Tb1(aui.AuiToolBar):
    def __init__(self, *args, **params):
        # emulating [F11]
        self._fullScreen = False
        self._shown =   True

        aui.AuiToolBar.__init__(self, *args, **params)
        # Get icons for toolbar
        imag =      imageEmbed()
        NewIcon =   imag.exporCsv
        OpenIcon =  imag.folder
        SaveIcon =  imag.disk
        SaveAsIcon = imag.save2disk
        CutIcon =   imag.edit_cut
        CopyIcon =  imag.edit_copy
        PasteIcon = imag.edit_paste
        PrefsIcon = imag.preferences
        HelpIcon =  imag.about
        UndoIcon =  imag.edit_undo
        RedoIcon =  imag.edit_redo
        Restart =   imag.refresh

        #closePage=   imag.cancel
        self._iconMax = imag.maximize
        self._iconMin = imag.minimize

        self.bt1 =   self.AddSimpleTool(10, __(u"New"), NewIcon, __(u"New"))
        self.bt2 =   self.AddSimpleTool(20, __(u"Open"), OpenIcon, __(u"Open"))
        self.bt3 =   self.AddSimpleTool(30, __(u"Save"), SaveIcon, __(u"Save"))
        self.bt4 =   self.AddSimpleTool(40, __(u"Save As"), SaveAsIcon, __(u"Save As"))
        ##self.bt5 = self.AddSimpleTool(50, "Print",PrintIcon,"Print")
        self.AddSeparator()
        self.bt11 =  self.AddSimpleTool(wx.ID_ANY, __(u"Undo"), UndoIcon, __(u"Undo"))
        self.bt12 =  self.AddSimpleTool(wx.ID_ANY, __(u"Redo"), RedoIcon, __(u"Redo"))
        self.AddSeparator()
        self.bt6 =   self.AddSimpleTool(60, __(u"Cut"), CutIcon, __(u"Cut"))
        self.bt7 =   self.AddSimpleTool(70, __(u"Copy"), CopyIcon, __(u"Copy"))
        self.bt8 =   self.AddSimpleTool(80, __(u"Paste"), PasteIcon, __(u"Paste"))
        self.AddSeparator()
        self.bt9 =   self.AddSimpleTool(85, __(u"Preferences"), PrefsIcon, __(u"Preferences"))
        self.bt10 =  self.AddSimpleTool(95, __(u"OnlineHelp"), HelpIcon, __(u"Online Help"))
        self.btnMax= self.AddSimpleTool(100, __(u"Maximize"), self._iconMax, __(u"Maximize"))
        self.bt13=   self.AddSimpleTool(105, __(u"Modules"), OpenIcon, __(u"Open Module Dict"))
        self.bt14=   self.AddSimpleTool(115, __(u"RestartShell"), Restart, __(u"Restart the shell"))

        # to the language
        language = wx.GetApp().GetPreferences("Language")
        if not language:
            language = "Default"
        self.languages = LangListCombo(self, language)
        self.translateBtn = self.AddControl(self.languages, label="Language")

        self.SetToolBitmapSize((24, 24))
        self.Realize()

        self.Bind(wx.EVT_MENU, lambda evt: self.fullScreen(self._fullScreen), id=self.btnMax.GetId())
        self.Bind(wx.EVT_MENU, self.CutData,      id= self.bt6.GetId())
        self.Bind(wx.EVT_MENU, self.CopyData,     id= self.bt7.GetId())
        self.Bind(wx.EVT_MENU, self.PasteData,    id= self.bt8.GetId())
        self.Bind(wx.EVT_MENU, self.Undo,         id= self.bt11.GetId())
        self.Bind(wx.EVT_MENU, self.Redo,         id= self.bt12.GetId())
        self.Bind(wx.EVT_MENU, self.Save,         id= self.bt3.GetId())
        self.Bind(wx.EVT_MENU, self.New,          id= self.bt1.GetId())
        self.Bind(wx.EVT_MENU, self.SaveAs,       id= self.bt4.GetId())
        self.Bind(wx.EVT_MENU, self.RestartShell, id= self.bt14.GetId())
        self.Bind(wx.EVT_MENU, self.Open,         id= self.bt2.GetId())
        self.Bind(wx.EVT_MENU, self.OpenWorkingDirectory, id=self.bt13.GetId())
        self.Bind(wx.EVT_MENU, self.Help,         id= self.bt10.GetId())
        self.Bind(wx.EVT_COMBOBOX,self.ChangeLanguaje, id= self.languages.GetId())

    def onShown(self):
        tb1Name = "tb1"
        wx.GetApp().frame._showHidePanel( tb1Name)

    def fullScreen(self, bool):
        self._fullScreen = not bool
        bitmap = [self._iconMax, self._iconMin][self._fullScreen]
        self.btnMax.SetBitmap(bitmap)
        app = wx.GetApp()
        app.frame.ShowFullScreen(self._fullScreen)

    @property
    def grid(self):
        # load the last datapanel selected
        cs= wx.GetApp().frame.formulaBarPanel.lastObject
        if cs == None:
            cs= wx.GetApp().frame.grid
        return cs


###########################################
    def ChangeLanguaje(self, evt):
        event = Tb1_ChanLan_evt(evtIDChanLan)
        setattr(event, 'lang', self.languages.GetValue())
        wx.PostEvent(self.GetEventHandler(), event)

    def Help(self, evt):
        event = Tb1_Help_evt(evtIDHelp)
        wx.PostEvent(self.GetEventHandler(), event)

    def OpenWorkingDirectory(self, evt):
        event = Tb1_OpenWorkDir_evt(evtIDOpenWorkDir)
        wx.PostEvent(self.GetEventHandler(), event)

    def Open(self, evt):
        event = Tb1_Open_evt(evtIDOpen)
        wx.PostEvent(self.GetEventHandler(), event)

    def Save(self, *args, **params):
        event = Tb1_Save_evt(evtIDSave)
        wx.PostEvent(self.GetEventHandler(), event)

    def SaveAs(self, evt):
        event = Tb1_SaveAs_evt(evtIDSaveAs)
        wx.PostEvent(self.GetEventHandler(), event)

    def CutData(self, evt):
        event = Tb1_Cut_evt(evtIDCut)
        wx.PostEvent(self.GetEventHandler(), event)

    def CopyData(self, evt):
        event = Tb1_Copy_evt(evtIDCopy)
        wx.PostEvent(self.GetEventHandler(), event)

    def PasteData(self, evt):
        event = Tb1_Paste_evt(evtIDPaste)
        wx.PostEvent(self.GetEventHandler(), event)

    def Undo(self, evt):
        event = Tb1_Undo_evt(evtIDUndo)
        wx.PostEvent(self.GetEventHandler(), event)

    def Redo(self, evt):
        event = Tb1_Redo_evt(evtIDRedo)
        wx.PostEvent(self.GetEventHandler(), event)

    def New(self, evt):
        event = Tb1_New_evt(evtIDNew)
        wx.PostEvent(self.GetEventHandler(), event)
    def RestartShell(self, evt):
        event = Tb1_RestartShell_evt(evtIDRestartShell)
        wx.PostEvent(self.GetEventHandler(), event)
###########################################        

    def DeleteCurrentCol(self, evt):
        self.grid.DeleteCurrentCol(evt)
        evt.Skip()

    def DeleteCurrentRow(self, evt):
        self.grid.DeleteCurrentRow(evt)
        evt.Skip()

    def SelectAllCells(self, evt):
        self.grid.SelectAllCells()
        evt.Skip()

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

        lang_ids = GetLocaleDict(GetAvailLocales(wx.GetApp().installDir)).values()
        lang_items = langlist.CreateLanguagesResourceLists(langlist.LC_ONLY, \
                                                           lang_ids)
        BitmapComboBox.__init__(self, parent,
                                size=wx.Size(150, 26),
                                style=wx.CB_READONLY)
        for lang_d in lang_items[1]:
            bit_m = lang_items[0].GetBitmap(lang_items[1].index(lang_d))
            self.Append(lang_d, bit_m)

        if default:
            self.SetValue(default)


#<p> INIT SELECT A TYPE OF CHART
class _panelSubPlot(wx.ScrolledWindow):
    def __init__(self, *args, **param):
        wx.ScrolledWindow.__init__(self, *args, **param)
        self.SetScrollRate( 5, 5 )
        self.sizer = wx.WrapSizer( )
        self.SetSizer( self.sizer )

    def createButtons( self, buttonsData):
        # buttonsData = [(label, image, callback, id), (...), ...]
        for label, image, callback, id in buttonsData:
            self._createbutton( image, label, callback)
        self.Layout()
        self.Centre( wx.BOTH )

    def _createbutton( self, img, label, callback= None):
        if len(label) > 20:
            label= label[:20] + '\n' + label[20:]

        newSizer=   wx.BoxSizer( wx.VERTICAL )
        button=     wx.BitmapButton( self, wx.ID_ANY, img,
                                     wx.DefaultPosition, wx.DefaultSize,
                                     wx.BU_AUTODRAW )
        newSizer.Add( button, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        staticText= wx.StaticText( self, wx.ID_ANY, label,
                                   wx.DefaultPosition, wx.DefaultSize, 0 )
        staticText.Wrap( -1 )
        newSizer.Add( staticText, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        self.sizer.Add( newSizer, 0, 0, 5 )
        button.Bind(wx.EVT_BUTTON, callback)

class createPlotSelectionPanel( wx.Panel):
    def __init__( self, *args, **params):
        wx.Panel.__init__( self, *args, **params)
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        self.notebook = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                            wx.aui.AUI_NB_SCROLL_BUTTONS|wx.aui.AUI_NB_TAB_MOVE|wx.aui.AUI_NB_WINDOWLIST_BUTTON|
                                            wx.aui.AUI_NB_BOTTOM)
        # wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

        bSizer1.Add( self.notebook, 1, wx.EXPAND, 5 )
        self.SetSizer( bSizer1 )
        self.Layout()
        self.Centre( wx.BOTH )

    def createPanels(self, dataPanels):
        for dat in dataPanels:
            panel = _panelSubPlot( self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize)
            panel.createButtons( dat[-1])
            self.notebook.AddPage( panel, dat[0], False )

        self.Layout()
        self.Centre( wx.BOTH )

#  END SELECT A TYPE OF CHART /<p>

class SaveDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = __(u"Save data?"), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, __(u"You have unsaved data!"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        bSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, __(u"Do you wish to save it?"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        bSizer1.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_button1 = wx.Button( self, wx.ID_ANY, __(u"Save"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.m_button1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_button2 = wx.Button( self, wx.ID_ANY, __(u"Discard"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.m_button2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_button3 = wx.Button( self, wx.ID_ANY, __(u"Cancel"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.m_button3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        bSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )

        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )

        self.Centre( wx.BOTH )

        self.Bind(wx.EVT_BUTTON, self.SaveData,     id = self.m_button1.GetId())
        self.Bind(wx.EVT_BUTTON, self.DiscardData,  id = self.m_button2.GetId())
        self.Bind(wx.EVT_BUTTON, self.CancelDialog, id = self.m_button3.GetId())

    def SaveData(self, evt):
        wx.GetApp().frame.grid.hasSaved = True
        wx.GetApp().frame.grid.SaveXlsAs(self) # will it be ASCII or XML?
        # wx.GetApp().output.Close(True)
        self.Destroy()
        wx.GetApp().frame.Close(True)

    def DiscardData(self, evt):
        self.Destroy()
        wx.GetApp().frame.grid.hasSaved = True
        wx.GetApp().frame.Close(True)


    def CancelDialog(self, evt):
        self.Destroy()

class SaveOneGridDialog(SaveDialog):
    def __init__(self, *args, **params):
        self.grid= args[0]
        SaveDialog.__init__(self, *args, **params)

    def SaveData(self, evt):
        try:
            wx.GetApp().frame.grid.hasSaved = True
            wx.GetApp().frame.grid.SaveXlsAs(self)
            self.grid.delPage()
        except:
            raise
        finally:
            self.Close(True)

    def DiscardData(self, evt):
        try:
            self.grid.delPage()
        except:
            raise
        finally:
            self.Close(True)

    def CancelDialog(self, evt):
        self.Close(True)


class VariablesFrame(wx.Dialog):
    def __init__(self,parent,id):
        wx.Dialog.__init__(self, parent,id,"S2 - Variables", \
                           size=(380, 480,))
        if len(wx.GetApp().frame.grid) == 0:
            self.Close(True)
            return
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        okaybutton = wx.Button(self.m_panel1 ,   2001, __( "Okay"), wx.DefaultPosition, wx.DefaultSize, 0 )
        cancelbutton = wx.Button(self.m_panel1 , 2002, __( "Cancel"), wx.DefaultPosition, wx.DefaultSize, 0 )

        bSizer2.Add( okaybutton, 0, wx.ALL, 5 )
        bSizer2.Add( cancelbutton , 0, wx.ALL, 5 )

        self.m_panel1.SetSizer( bSizer2 )
        self.m_panel1.Layout()
        bSizer2.Fit( self.m_panel1 )
        self.m_mgr.AddPane( self.m_panel1, wx.aui.AuiPaneInfo().Bottom().
                            CaptionVisible( False ).CloseButton( False ).PaneBorder( False ).
                            Dock().Resizable().FloatingSize( wx.Size( 170,54 ) ).
                            DockFixed( False ).LeftDockable( False ).RightDockable( False ).
                            MinSize( wx.Size( -1,30 ) ).Layer( 10 ) )

        self.vargrid = wx.grid.Grid( self,-1,)
        self.vargrid.SetDefaultColSize( 140, True)
        maxRows= wx.GetApp().frame.grid.GetNumberCols()
        self.vargrid.CreateGrid( maxRows, 1) # 3->2 REMOVING THE MISSING VALUE CHANGE BY THE USER
        inputGrid= wx.GetApp().frame.grid
        for i in range( maxRows):
            oldlabel = inputGrid.GetColLabelValue( i)
            self.vargrid.SetCellValue( i, 0, oldlabel)

        self.vargrid.SetDefaultCellAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        if wx.Platform == '__WXMAC__':
            self.vargrid.SetGridLineColour( "#b7b7b7")
            self.vargrid.SetLabelBackgroundColour( "#d2d2d2")
            self.vargrid.SetLabelTextColour( "#444444")

        self.vargrid.SetColLabelValue( 0, __( u"Variable Name"))
        self.vargrid.SetColLabelValue( 1, __( u"Decimal Places"))

        self.m_mgr.AddPane( self.vargrid,
                            wx.aui.AuiPaneInfo().Center().
                            CaptionVisible( False ).PaneBorder( False ).
                            Dock().Resizable().FloatingSize( wx.DefaultSize ).
                            DockFixed( True ))

        self.m_mgr.Update()
        self.Centre( wx.BOTH )

        self.Bind(wx.EVT_BUTTON, self.OnOkayVariables, id= 2001)
        self.Bind(wx.EVT_BUTTON, self.OnCloseVariables, id =  2002)

    # this method needs to work out the other variables too
    def _checkVariables(self, data):
        newData= set( data[:])
        if len(data) != len(newData):
            return False
        if u'' in newData:
            return False
        return True

    def OnOkayVariables(self, evt):
        newlabels= [self.vargrid.GetCellValue(i, 0) for i in range( self.vargrid.GetNumberRows())]
        if not self._checkVariables( newlabels):
            return
        for i in range( wx.GetApp().frame.grid.GetNumberCols()-1):
            newlabel = newlabels[i]
            if (newlabel != ''):
                wx.GetApp().frame.grid.SetColLabelValue( i, newlabel)
            #newsig = self.vargrid.GetCellValue( i, 1)
            #if  not (newsig in ('',u'')):
                #try:
                    #wx.GetApp().frame.grid.SetColFormatFloat( i, -1, int(newsig))
                #except ZeroDivisionError:
                    #pass

        wx.GetApp().frame.grid.ForceRefresh()
        self.Close(True)

    def OnCloseVariables(self, evt):
        self.Close(True)


#---------------------------------------------------------------------------
# instance of the tool window that contains the test buttons
# note this is experimental and may not be final
#---------------------------------------------------------------------------
class TransformFrame(wx.Dialog):
    def __init__(self, parent, id= wx.ID_ANY):
        wx.Dialog.__init__( self, parent, id, __(u"Transformations"),
                            size=(500,400+wind))
        #set icon for frame (needs x-platform separator!
        self.parent= parent
        #self._= parent._
        x= self.GetClientSize()
        winheight= x[1]
        icon= imageEmbed().logo16
        self.SetIcon(icon)
        self.transform= ""
        self.transformName= ""
        self.ColumnList, self.colnums= wx.GetApp().frame.grid.GetUsedCols()
        self.cols=      wx.GetApp().frame.grid.NumberCols
        l0 = wx.StaticText( self, -1, __(u"Select Column(s) to Transform"), pos=(10,10))
        self.ColChoice=        wx.CheckListBox( self,1102, wx.Point(10,30), \
                                                wx.Size(230,(winheight * 0.8)), self.ColumnList)
        self.okaybutton=       wx.Button( self, wx.ID_ANY, __(u"Okay"), wx.Point(10,winheight-35))
        self.cancelbutton=     wx.Button( self, wx.ID_ANY, __(u"Cancel"),wx.Point(100,winheight-35))
        # common transformations:
        l1= wx.StaticText( self, -1, __(u"Common Transformations:"), pos=(250,30))
        self.squareRootButton= wx.Button( self, wx.ID_ANY, __(u"Square Root"), wx.Point(250, 60))
        self.logButton=        wx.Button( self, wx.ID_ANY, __(u"Logarithmic"),wx.Point(250, 100))
        self.reciprocalButton= wx.Button( self, wx.ID_ANY, __(u"Reciprocal"), wx.Point(250,140))
        self.squareButton=     wx.Button( self, wx.ID_ANY, __(u"Square"), wx.Point(250,180))
        l2 = wx.StaticText( self, -1, __(u"Function :"), wx.Point(250, 315))
        self.transformEdit=    wx.TextCtrl( self, 1114,pos=(250,335),size=(150,20))
        self.Bind( wx.EVT_BUTTON, self.OnOkayButton,        id = self.okaybutton.GetId())
        self.Bind( wx.EVT_BUTTON, self.OnCloseFrame,        id = self.cancelbutton.GetId())
        self.Bind( wx.EVT_BUTTON, self.squareRootTransform, id = self.squareRootButton.GetId())
        self.Bind( wx.EVT_BUTTON, self.logTransform,        id = self.logButton.GetId())
        self.Bind( wx.EVT_BUTTON, self.reciprocalTransform, id = self.reciprocalButton.GetId())
        self.Bind( wx.EVT_BUTTON, self.squareTransform,     id = self.squareButton.GetId())

    def squareRootTransform(self, evt):
        self.transform = "math.sqrt(x)"
        self.transformEdit.SetValue(self.transform)
        self.transformName =  __(u" Square Root")

    def logTransform(self, evt):
        self.transform = "math.log(x)"
        self.transformEdit.SetValue(self.transform)
        self.transformName = __(u" Logarithm")

    def reciprocalTransform(self, evt):
        self.transform = "1 / x"
        self.transformEdit.SetValue(self.transform)
        self.transformName = __(u" Reciprocal")

    def squareTransform(self, evt):
        self.transform = "x * x"
        self.transformEdit.SetValue(self.transform)
        self.transformName = __(u" Square")

    def OnOkayButton(self, evt):
        # start transforming!
        # process: collect each selected column, then pass the contents through the self.transform function
        # then put the resulting column into a new column, and retitle it with the original variable
        # name plus the function.
        frame=  wx.GetApp().frame
        self.transform= self.transformEdit.GetValue()
        cols= range(frame.grid.NumberCols)
        emptyCols= []
        for i in cols:
            if cols[i] not in self.colnums:
                emptyCols.append( cols[i])

        # count the number of needed columns
        neededCols= sum( [1 for i in range(len(self.colnums)) if self.ColChoice.IsChecked(i)])
        cols2add=   len(self.colnums) + neededCols - frame.grid.NumberCols
        if cols2add > 0:
            # adding the needed cols
            editorRederer= frame.floatCellAttr
            frame.grid.AddNCells(cols2add, 0, attr= editorRederer)
            emptyCols.extend( range(len(cols), frame.grid.NumberCols))
            cols= frame.grid.NumberCols

        for i in range( len( self.colnums)):
            if self.ColChoice.IsChecked( i):
                newColi= self.colnums[i]
                oldcol= frame.grid.GetCol( newColi)
                newcol= [0]*len( oldcol)
                # trying to made the evaluation by using numpy
                try:
                    arr= numpy.array(oldcol)
                    local= {'x': numpy.ravel(arr),'math': math,'scipy': scipy}
                    # posibly change by wx.GetApp().frame.scriptPanel.interp.runcode( mainscript)
                    newcol= eval( self.transform, {}, local)
                except:
                    for j in range( len( oldcol)):
                        x= oldcol[j]
                        try:
                            newcol[j]= eval( self.transform)
                        except: # which exception would this be?
                            newcol[j]= u''

                posNewCol= emptyCols.pop(0)
                frame.grid.PutCol( posNewCol, newcol)
                # put in a nice new heading
                oldHead= frame.grid.GetColLabelValue(self.colnums[i])
                if self.transformName == "":
                    self.transformName = ' ' + self.transform
                oldHead= oldHead + self.transformName
                frame.grid.SetColLabelValue(posNewCol, oldHead)

        self.Close(True)

    def OnCloseFrame(self, evt):
        self.Close(True)

class NumTextCtrl(wx.TextCtrl):
    '''a text ctrl that only accepts numbers'''
    def __init__( self, parent, *args, **params):
        wx.TextCtrl.__init__( self, parent, *args, **params)
        self.Bind( wx.EVT_TEXT, self._textChange)
        self.allowed = [ str( x) for x in range( 10)]
        self.allowed.extend([ wx.GetApp().DECIMAL_POINT, '-'])

    def _textChange(self, evt):
        texto = self.Value

        if len(texto) == 0:
            return

        newstr= [ x for x in texto if x in self.allowed]

        if len(newstr) == 0:
            newstr = u''
        else:
            func = lambda x,y: x+y
            newstr= reduce(func, newstr)
        # prevent infinite recursion
        if texto == newstr:
            return

        self.SetValue(newstr)
        evt.Skip()
    def GetAsNumber(self):
        prevResult = self.Value
        if len(prevResult) == 0:
            prevResult = None
        else:
            try:
                prevResult = float(prevResult.replace(wx.GetApp().DECIMAL_POINT, '.'))
            except:
                prevResult = None
        return prevResult

    def GetValue(self):
        return self.GetAsNumber()

class IntTextCtrl( NumTextCtrl):
    '''a text ctrl that only accepts numbers'''
    def __init__( self, parent, *args, **params):
        wx.TextCtrl.__init__( self, parent, *args, **params)
        self.Bind( wx.EVT_TEXT, self._textChange)
        self.allowed = [ str( x) for x in range( 10)]

    def _textChange( self, evt):
        texto = self.Value

        newstr= [ x for x in texto if x in self.allowed]

        if len( newstr) == 0:
            newstr = u''
        else:
            func = lambda x,y: x+y
            newstr= reduce( func, newstr)

        # prevent infinite recursion
        if texto == newstr:
            return

        self.SetValue( newstr)
        evt.Skip()

    def GetAsNumber( self):
        prevResult = self.Value
        if len( prevResult) == 0:
            prevResult = None
        else:
            try:
                prevResult = int( prevResult)
            except:
                prevResult = None

        return prevResult


class SixSigma( wx.Dialog ):
    def __init__( self, parent, colNames ):
        ''' colNames: a list of column Names'''
        if not isinstance(colNames, (list, tuple)):
            return list()
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = __(u"Six Sigma Pack"), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer3 = wx.BoxSizer( wx.VERTICAL )

        sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, __(u"Select Column(s) to analyse") ), wx.VERTICAL )

        m_checkList2Choices = colNames
        self.m_checkList2 = CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,70 ), m_checkList2Choices, 0 )
        sbSizer2.Add( self.m_checkList2, 0, wx.ALL|wx.EXPAND, 5 )

        bSizer3.Add( sbSizer2, 0, wx.EXPAND, 5 )

        sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, __(u"Limits") ), wx.VERTICAL )

        bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_textCtrl1 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer5.Add( self.m_textCtrl1, 0, wx.ALL, 5 )

        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, __(u"Upper Control Limit"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        bSizer5.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sbSizer1.Add( bSizer5, 1, wx.EXPAND, 5 )

        bSizer6 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_textCtrl3 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer6.Add( self.m_textCtrl3, 0, wx.ALL, 5 )

        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, __(u"Lower Control Limit"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        bSizer6.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sbSizer1.Add( bSizer6, 1, wx.EXPAND, 5 )

        bSizer7 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_textCtrl4 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer7.Add( self.m_textCtrl4, 0, wx.ALL, 5 )

        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, __(u"Target value"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        bSizer7.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sbSizer1.Add( bSizer7, 1, wx.EXPAND, 5 )


        bSizer3.Add( sbSizer1, 1, wx.EXPAND, 5 )

        sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )

        bSizer8 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_spinCtrl1 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), wx.SP_ARROW_KEYS, 1, 10, 6 )
        bSizer8.Add( self.m_spinCtrl1, 0, wx.ALL, 5 )

        self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, __(u"Use tolerance of  k  in  k*Sigma"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )
        bSizer8.Add( self.m_staticText6, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sbSizer3.Add( bSizer8, 0, wx.EXPAND, 5 )

        bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_spinCtrl2 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), wx.SP_ARROW_KEYS, 2, 15, 2)
        bSizer9.Add( self.m_spinCtrl2, 0, wx.ALL, 5 )

        self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, __(u"Subgroup Size"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )
        bSizer9.Add( self.m_staticText7, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sbSizer3.Add( bSizer9, 0, wx.EXPAND, 5 )


        bSizer3.Add( sbSizer3, 0, wx.EXPAND, 5 )

        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        m_sdbSizer2 = wx.StdDialogButtonSizer()
        self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
        self.m_sdbSizer2Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer2.AddButton( self.m_sdbSizer2Cancel )
        m_sdbSizer2.Realize();

        bSizer4.Add( m_sdbSizer2, 1, wx.EXPAND, 5 )


        bSizer3.Add( bSizer4, 0, wx.ALL|wx.EXPAND, 5 )

        self.SetSizer( bSizer3 )
        self.Layout()
        bSizer3.Fit( self )

        self.Centre( wx.BOTH )
        self._BindEvents()

    def _BindEvents(self):
        self.Bind(wx.EVT_CHECKLISTBOX, self.lstboxChange)

    def lstboxChange(self, event):
        if len(self.m_checkList2.Checked) < 2:
            self.m_spinCtrl2.Enabled= True
        else:
            self.m_spinCtrl2.Enabled= False

    def GetValue(self):
        result= list()
        if len(self.m_checkList2.Checked) == 0:
            result.append([])
        else:
            result.append([self.m_checkList2.Items[pos] for pos in self.m_checkList2.Checked])
        result.append(self.m_textCtrl1.GetAsNumber())
        result.append(self.m_textCtrl3.GetAsNumber())
        result.append(self.m_textCtrl4.GetAsNumber())
        result.append(self.m_spinCtrl1.Value)
        result.append(self.m_spinCtrl2.Value)
        return result

class _MyFrame1 ( wx.Frame ):
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY,
                            title = wx.EmptyString, pos = wx.DefaultPosition,
                            size = wx.Size( -1, -1 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer10 = wx.BoxSizer( wx.VERTICAL )

        self.m_button8 = wx.Button( self, wx.ID_ANY, __(u"Show Dialog"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer10.Add( self.m_button8, 0, wx.ALL, 5 )


        self.SetSizer( bSizer10 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_button8.Bind( wx.EVT_BUTTON, self.showDialog )


    # Virtual event handlers, override them in your derived class
    def showDialog( self, event ):

        dlg = SixSigma(self,[str(i) for i in range(20)])
        if dlg.ShowModal() == wx.ID_OK:
            print "ok"
        dlg.Destroy()


if __name__ == '__main__':
    app = wx.App()
    frame = _MyFrame1(None)
    frame.Show()
    app.MainLoop()