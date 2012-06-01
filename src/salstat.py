#!/usr/bin/env python

""" Copyright 2012 Sebastian Lopez Buritica

SalStat Statistics Package. Copyright 2002 Alan James Salmoni. Licensed
under the GNU General Public License (GPL). See the file COPYING for full
details of this license. """

import wx
import os

import wx.html
import wx.lib.agw.aui as aui

import wx.lib.wxpTag
import string, os, os.path, pickle
# import SalStat specific modules
import images
import numpy, math
import wx.py
import xlrd
import traceback

from xml.dom import minidom
# system of graphics
from plotFrame import MpltFrame as plot
from multiPlotDialog import data2Plotdiaglog, selectDialogData2plot, scatterDialog
from ntbSheet import NoteBookSheet

from openStats import statistics

from slbTools import ReportaExcel
from easyDialog import Dialog as dialog
from statlib import stats
from ntbSheet import MyGridPanel as MyGrid

from script import ScriptPanel
from imagenes import imageEmbed

STATS = {'Central Tendency': ('geometricmean','harmonicmean','mean',
                              'median','medianscore','mode'),
         'Moments': ('moment', 'variation', 'skew', 'kurtosis',
                     'skewtest', 'kurtosistest', 'normaltest',),
         'Frequency Stats': ('itemfreq', 'scoreatpercentile', 'percentileofscore',
                             'histogram', 'cumfreq', 'relfreq',),
         'Variability': ( 'samplevar', 'samplestdev', #'obrientransform'
                          'signaltonoise', 'var', 'stdev', 'sterr',
                          'sem','z','zs',), # 'zmap'
         'Trimming Fcns': ('threshold', 'trimboth', 'trim1', ), #'round',
         'Correlation Fcns': ( 'paired', 'pearsonr', # 'covariance', 'correlation'
                               'spearmanr', 'pointbiserialr', 'kendalltau', 'linregress',),
         'Inferential Stats': ('ttest_1samp', 'ttest_ind', 'ttest_rel', 'chisquare',
                               'ks_2samp', 'mannwhitneyu', 'ranksums', 'wilcoxont',
                               'kruskalwallish', 'friedmanchisquare',),
         'Probability Calcs': ('chisqprob', 'erfcc', 'zprob',   # 'ksprob'
                               'betacf', 'gammln', 'betai',), # 'fprob'
         'Anova Functions': ( 'F_oneway', )} # 'F_value'


DescList=['N','Sum','Mean','missing',
          'Variance','Standard Deviation','Standard Error',
          'Sum of Squares',#'Sum of Squared Devs',
          'Coefficient of Variation','Minimum',
          'Maximum','Range','Number Missing',
          'Geometric Mean','Harmonic Mean',
          'Skewness','Kurtosis', 'Median',        #'Median Absolute Deviation',
          'Mode', 'Interquartile Range'] #, 'Number of Unique Levels']

inits={}    # dictionary to hold the config values
ColsUsed = []
RowsUsed = []
missingvalue = None
global filename # ugh
filename = 'UNTITLED'
global BWidth, BHeight # ugh again!
BWidth = 80
BHeight = 25
HOME = os.getcwd()

if os.name == 'nt':
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

    def writeLine(self, lineaTexto):
        '''escribe una linea de texto'''
        #texto= str(self.numLinea.next()) + " >> "
        texto= str( ">> ")
        texto+= lineaTexto + "\n"
        # se escribe el texto indicado
        self.log.AppendText(texto)

    def write(self,lineaTexto):
        if len(lineaTexto) > 1:
            last= lineaTexto[-1:]
            if last =='\n':
                lineaTexto = lineaTexto[:-2]
        self.writeLine(lineaTexto)

    def clearLog(self):
        self.log.SetValue('')

    def __del__( self ):
        pass


class SaveDialog(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Save Data?", \
                           size=(270+wind,100+wind), style = wx.DIALOG_EX_METAL)
        icon = images.getIconIcon()
        self.SetIcon(icon)
        self.Choice = 'none'
        vbox = wx.BoxSizer(wx.VERTICAL)
        l1 = wx.StaticText(self, -1, 'You have unsaved Data')
        l2 = wx.StaticText(self, -1, 'Do you wish to save it?')
        vbox.Add(l1,1, wx.ALIGN_CENTER)
        vbox.Add(l2,1, wx.ALIGN_CENTER)
        hbox = wx.BoxSizer(wx.VERTICAL)
        saveButton = wx.Button(self,    wx.ID_ANY, "Save...", size=(BWidth, BHeight))
        discardButton = wx.Button(self, wx.ID_ANY, "Discard", size=(BWidth, BHeight))
        CancelButton = wx.Button(self,  wx.ID_ANY, "Cancel",  size=(BWidth, BHeight))
        hbox.Add(saveButton, 0, wx.ALL, 5)
        hbox.Add(discardButton, 0, wx.ALL, 5)
        hbox.Add(CancelButton, 0, wx.ALL, 5)
        vbox.Add(hbox,1)
        self.SetAutoLayout(True)
        self.SetSizer(vbox)
        self.Layout()
        self.Bind(wx.EVT_BUTTON, self.SaveData,     id = saveButton.GetId())
        self.Bind(wx.EVT_BUTTON, self.DiscardData,  id = discardButton.GetId())
        self.Bind(wx.EVT_BUTTON, self.CancelDialog, id = CancelButton.GetId())

    def SaveData(self, event):
        frame.grid.Saved = True
        frame.grid.SaveXlsAs(self) # will it be ASCII or XML?
        # output.Close(True)
        frame.Close(True)
        self.Close(True)

    def DiscardData(self, event):
        # output.Close(True)
        frame.Close(True)
        self.Close(True)

    def CancelDialog(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# class to output the results of several "descriptives" in one table
class ManyDescriptives:
    def __init__(self, source, ds):
        __x__ = len(ds)
        if __x__ == 0:
            return
        data= {'name': "Many Descriptives",
               'size': (0,0),
               'nameCol': list(),
               'data': []}
        data['nameCol'].append('Statistic')
        data['nameCol'].extend([ds[i].Name for i in range(__x__)])
        funcTrans= {'N': 'N',
                    'Sum': 'suma',
                    'Mean': 'mean',
                    'missing': 'missing',
                    'Variance': 'samplevar',
                    'Standard Deviation': 'stddev',
                    'Standard Error': 'stderr',
                    'Sum of Squares': 'sumsquares',
                    'Sum of Squared Devs': 'ssdevs',
                    'Coefficient of Variation': 'coeffvar',
                    'Minimum': 'minimum',
                    'Maximum': 'maximum',
                    'Range': 'range',
                    'Number Missing': 'missing',
                    'Geometric Mean': 'geomean',
                    'Harmonic Mean': 'harmmean',
                    'Skewness': 'skewness',
                    'Kurtosis': 'kurtosis',
                    'Median': 'median',
                    'Median Absolute Deviation': 'mad',
                    'Mode': 'mode',
                    'Interquartile Range': None,
                    'Number of Unique Levels': 'numberuniques'}
        items = source.DescChoice.GetItems()
        itemsSelected = source.DescChoice.GetChecked()
        if len(itemsSelected ) == 0:
            return
        itemsSelected= [items[pos] for pos in itemsSelected]
        for aliasParamName in itemsSelected:
            realParamName = funcTrans[aliasParamName]
            if realParamName == None:
                continue
            res=[aliasParamName]
            if hasattr(ds[i],realParamName):
                res.extend([getattr(ds[i],realParamName) for i in range(__x__)])
                data['data'].append(res)
        data['size'] = (len(data['data']), len(data['nameCol']))
        output.upData(data)

#---------------------------------------------------------------------------
# class for grid - used as datagrid.
class SimpleGrid(MyGrid):# wxGrid
    def __init__(self, parent, log, size= (1000,100)):
        self.NumSheetReport = 0
        self.log = log
        self.path = None
        MyGrid.__init__(self, parent, -1, size)
        self.Saved = True
        self.moveTo = None
        
        self.m_grid.setPadreCallBack(self)
        self.m_grid.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        for i in range(self.m_grid.NumberCols):
            self.m_grid.SetColFormatFloat(i, 8, 4)
        ##self.m_grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.AlterSaveStatus)
        self.m_grid.Bind(wx.grid.EVT_GRID_CMD_LABEL_RIGHT_DCLICK, self.RangeSelected)
        self.m_grid.wildcard = "Any File (*.*)|*.*|" \
                               "SalStat Format (*.xls)|*.xls"
        ## se ajusta el render
        attr = wx.grid.GridCellAttr()
        editor = wx.grid.GridCellFloatEditor()
        attr.SetEditor(editor)
        renderer = wx.grid.GridCellFloatRenderer(0, 5)
        attr.SetRenderer(renderer)

    def RangeSelected(self, event):
        if event.Selecting():
            self.tl = event.GetTopLeftCoords()
            self.br = event.GetBottomRightCoords()

    #def OnRangeChange(self, event): #AlterSaveStatus
        ## this is activated when the user enters some data
        #self.Saved = False
        ## also record in the history file
        #col = self.m_grid.GetGridCursorCol()
        #row = self.m_grid.GetGridCursorRow()
        #value = self.m_grid.GetCellValue(row, col)
        #xmlevt = '<data row="'+str(row)+'" col="'+str(col)+'">'+str(value)+'</data>\n'

    def CutData(self, event):
        self.m_grid.Delete()

    def CopyData(self, event):
        self.m_grid.Copy()


    def PasteData(self, event):
        self.m_grid.OnPaste()

    def Undo(self, event):
        self.m_grid.Undo()

    def Redo(self, event):
        self.m_grid.Redo()

    def EditGrid(self, event, numrows):
        insert = self.AppendRows(numrows)

    def DeleteCurrentCol(self, event):
        currentcol = self.m_grid.GetGridCursorCol()
        self.m_grid.DeleteCols(currentcol, 1)
        self.m_grid.AdjustScrollbars()


    def DeleteCurrentRow(self, event):
        currentrow = self.m_grid.GetGridCursorRow()
        self.m_grid.DeleteRows(currentrow, 1)
        self.m_grid.AdjustScrollbars()

    def SelectAllCells(self, event):
        self.m_grid.SelectAll()

    # adds columns and rows to the grid
    def AddNCells(self, numcols, numrows):
        insert = self.m_grid.AppendCols(numcols)
        insert = self.m_grid.AppendRows(numrows)
        for i in range(self.m_grid.GetNumberCols() - numcols, self.m_grid.GetNumberCols(), 1):
            self.m_grid.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
            self.m_grid.SetColFormatFloat(i, 8, 4)
        self.m_grid.AdjustScrollbars()

    # function finds out how many cols contain data - all in a list
    #(ColsUsed) which has col #'s
    def GetUsedCols(self):
        ColsUsed = []
        colnums = []
        cols = self.m_grid.GetNumberCols()
        for i in range(cols):
            dat = self.m_grid.GetCellValue(0, i)
            if (dat!=''):
                ColsUsed.append(self.m_grid.GetColLabelValue(i))
                colnums.append(i)
        return ColsUsed, colnums

    def GetColsUsedList(self):
        colsusedlist = []
        for i in range(self.m_grid.GetNumberCols()):
            try:
                tmp = float(self.m_grid.GetCellValue(0,i))
                colsusedlist.append(i)
            except ValueError:
                colsusedlist.append(0)
        return colsusedlist

    def GetUsedRows(self):
        RowsUsed = []
        for i in range(self.m_grid.GetNumberCols()):
            if (self.m_grid.GetCellValue(0, i) != ''):
                for j in range(self.m_grid.GetNumberRows()):
                    if (self.m_grid.GetCellValue(j,i) == ''):
                        RowsUsed.append(j)
                        break
        return RowsUsed

    def SaveXlsAs(self, event):
        self.SaveXls(None, True)

    def SaveXls(self, *args):
        if len(args) == 1:
            saveAs= False
        else:
            saveAs= args[1]
        self.reportObj= ReportaExcel(cell_overwrite_ok = True)
        if self.Saved == False or saveAs: # path del grid
            # mostrar el dialogo para guardar el archivo
            dlg= wx.FileDialog(self, "Save Data File", "" , "",\
                               "excel (*.xls)|*.xls| \
                                    Any (*.*)| *.*", wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                self.path = dlg.GetPath()
            else:
                return
            self.reportObj.path = self.path
        else:
            self.reportObj.path = self.path
        cols, waste = self.GetUsedCols()
        if len(cols) == 0:
            pass
        else:
            # rows = self.GetUsedRows()
            cols= self.GetUsedCols()[1]
            totalResult = self.m_grid.getByColumns(maxRow = self.m_grid.maxrow )
            result= list()
            for posCol in range(cols[-1]+1):
                if posCol in cols:
                    result.append(totalResult[posCol])
                else:
                    result.append(list())
            self.reportObj.writeByCols(result, self.NumSheetReport)
        self.reportObj.save()
        self.Saved = True
        self.log.write("the fil %s was succesfully saved"%self.reportObj.path)

    def LoadXls(self, event):
        dlg = wx.FileDialog(self, "Load Data File", "","",
                            wildcard= "Excel File (*.xls)|*.xls",
                            style = wx.OPEN)
                #, wx.OPEN)
        icon = images.getIconIcon()
        dlg.SetIcon(icon)
        if dlg.ShowModal() != wx.ID_OK: # ShowModal
            dlg.Destroy()
            return

        filename = dlg.GetPath()
        dlg.Destroy()
        # se lee el libro
        wb = xlrd.open_workbook(filename)
        sheets = [wb.sheet_by_index(i) for i in range(wb.nsheets)]
        sheetNames = [sheet.name for sheet in sheets]
        if len(sheetNames) == 1:
            sheetSelected = sheets[0]
        else:
            # create a dialog to selecct the sheet to be loaded
            bt1= ('Choice',   (sheetNames,))
            bt2= ('StaticText', ('Selec a sheet to be loaded',))
            setting = {'Title': 'Select a sheet one'}
            dlg = dialog(self, struct=[[bt1,bt2],], settings= setting)
            if dlg.ShowModal() != wx.ID_OK:
                return
            (sheetNameSelected,)= dlg.GetValue()
            dlg.Destroy()
            if not (sheetNameSelected in sheetNames):
                return
            for sheet, sheetname in zip(sheets, sheetNames):
                if sheetname == sheetNameSelected:
                    sheetSelected = sheet
                    break
        # se lee el tamanio del sheet seleccionado
        #size = (sheetSelected.nrows, sheetSelected.ncols)
        # se hace el grid de tamanio 1 celda y se redimensiona luego
        self.m_grid.ClearGrid()
        #if size[0] > 1:
        #    self.m_grid.DeleteRows(1, size[0]-1)

        #if size[1] > 1:
        #    self.m_grid.DeleteCols(1, size[1]-1)

        size = (sheetSelected.nrows, sheetSelected.ncols)
        # se lee el tamanio de la pagina y se ajusta las dimensiones
        newSize = (sheetSelected.nrows, sheetSelected.ncols)
        if newSize[0]-size[0] > 0:
            self.m_grid.AppendCols(newSize[0]-size[0])

        if newSize[1]-size[1] > 0:
            self.m_grid.AppendRows(newSize[1]-size[1])

        # se escribe los datos en el grid
        for row in range(newSize[0]):
            for col in range(newSize[1]):
                newValue = sheetSelected.cell_value(row,col)
                if isinstance(newValue, (str,)):
                    self.m_grid.SetCellValue(row, col, newValue)
                elif isinstance(newValue, (int,float,bool)):
                    self.m_grid.SetCellValue(row, col, str(newValue))
                else:
                    try:
                        self.m_grid.SetCellValue(row, col, str(newValue))
                    except:
                        self.log.write("could not import the row,col (%i,%i)"%(row+1,col+1))


    def getData(self, x):
        for i in range(len(x)):
            try:
                row = int(x[i].attributes["row"].value)
                col = int(x[i].attributes["column"].value)
                datavalue = float(self.getText(x[i].childNodes))
                self.SetCellValue(row, col, str(datavalue))
            except ValueError:
                print "problem importing the xml"

    def getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    def CleanRowData(self, row):
        indata = []
        for i in range(self.GetNumberCols()):
            datapoint = self.GetCellValue(row, i)
            if (datapoint != ''):
                value = float(datapoint)
                if (value != missingvalue):
                    indata.append(value)
        return indata

    # Routine to return a "clean" list of data from one column
    def CleanData(self, col):
        indata = []
        self.missing = 0
        for i in range(self.m_grid.GetNumberRows()):
            datapoint = self.m_grid.GetCellValue(i, col).strip().replace(',','.')
            if (datapoint != u'') and (datapoint != u'.'):
                try:
                    value = float(datapoint)
                    if (value != missingvalue):
                        indata.append(value)
                    else:
                        self.missing = self.missing + 1
                except ValueError:
                    pass
        return indata

    def GetEntireDataSet(self, numcols):
        """Returns the data specified by a list 'numcols' in a Numeric
        array"""
        biglist = []
        for i in range(len(numcols)):
            smalllist = frame.grid.CleanData(numcols[i])
            biglist.append(smalllist)
        return numpy.array((biglist), numpy.float)

#---------------------------------------------------------------------------
# DescChoice-wx.CheckListBox with list of descriptive stats in it
class DescChoiceBox(wx.CheckListBox): # CheckListBox
    def __init__(self, parent, id):
        wx.CheckListBox.__init__( self, parent, -1,
                                  wx.DefaultPosition, wx.DefaultSize, DescList)

    def SelectAllDescriptives(self, event):
        for i in range(len(DescList)):
            self.Check(i, True)

    def SelectNoDescriptives(self, event):
        for i in range(len(DescList)):
            self.Check(i, False)

#---------------------------------------------------------------------------
# base class for getting number of columns/rows to add
class EditGridFrame(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Change Grid Size", \
                           size=(205, 100+wind))
        icon = images.getIconIcon()
        self.SetIcon(icon)
        l1 = wx.StaticText(self, -1, 'Add Columns',pos=(10,15))
        l2 = wx.StaticText(self, -1, 'Add Rows',pos=(10,55))
        self.numnewcols = wx.SpinCtrl(self, -1, "", wx.Point(110,10), wx.Size(80,25))
        self.numnewcols.SetRange(1, 5000)
        self.numnewcols.SetValue(0)
        self.numnewRows = wx.SpinCtrl(self, -1, "", wx.Point(110, 50), wx.Size(80,25))
        self.numnewRows.SetRange(1, 5000)
        self.numnewRows.SetValue(0)
        okaybutton = wx.Button(self, wx.ID_ANY, "Okay", wx.Point(10, 90),\
                               wx.Size(BWidth, BHeight))
        cancelbutton = wx.Button(self, wx.ID_ANY, "Cancel", wx.Point(110,90), \
                                 wx.Size(BWidth, BHeight))
        self.Bind(wx.EVT_BUTTON, self.OkayButtonPressed, id = okaybutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.CancelButtonPressed, id= cancelbutton.GetId())

    def OkayButtonPressed(self, event):
        colswanted = self.numnewcols.GetValue()
        rowswanted = self.numnewRows.GetValue()
        frame.grid.AddNCells(colswanted, rowswanted)
        self.Close(True)

    def CancelButtonPressed(self, event):
        self.Destroy()

#---------------------------------------------------------------------------
# grid preferences - set row & col sizes
class GridPrefs(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Cell Size", \
                           size=(205,100+wind))
        icon = images.getIconIcon()
        self.SetIcon(icon)
        self.colwidth = wx.SpinCtrl(self, -1, "", wx.Point(110,10), wx.Size(80,25))
        self.colwidth.SetRange(1,200)
        self.colwidth.SetValue(frame.grid.m_grid.GetDefaultColSize())
        self.rowheight= wx.SpinCtrl(self, -1, "", wx.Point(110,50), wx.Size(80,25))
        self.rowheight.SetRange(1,100)
        self.rowheight.SetValue(frame.grid.m_grid.GetDefaultRowSize())
        l1 = wx.StaticText(self, -1, 'Column Width:',pos=(10,15))
        l2 = wx.StaticText(self, -1, 'Row Height:',pos=(10,55))
        self.okaybutton = wx.Button(self, 321, "Okay", wx.Point(10, 90), \
                                    wx.Size(BWidth, BHeight))
        self.cancelbutton = wx.Button(self, 322, "Cancel", wx.Point(110,90),\
                                      wx.Size(BWidth, BHeight))
        self.Bind(wx.EVT_BUTTON, self.OkayButtonPressed, id = self.okaybutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCloseGridPrefs, id = self.cancelbutton.GetId())

    def OkayButtonPressed(self, event):
        frame.grid.m_grid.SetDefaultColSize(self.colwidth.GetValue(), True)
        frame.grid.m_grid.SetDefaultRowSize(self.rowheight.GetValue(), True)
        frame.grid.m_grid.ForceRefresh()
        self.Close(True)

    def OnCloseGridPrefs(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# Simply display the About box w/html frame in it
class AboutFrame(wx.Frame):
    def __init__(self, parent, id, tabnumber):
        wx.Frame.__init__(self, parent, id, "About SalStat", \
                          size=wx.Size(320, 240), pos=wx.DefaultPosition)
        #set icon for frame (needs x-platform separator!
        icon = images.getIconIcon()
        self.SetIcon(icon)
        GoIcon = images.getApplyBitmap()

        BackIcon = images.getLeftBitmap()
        ForeIcon = images.getRightBitmap()
        HomeIcon = images.getHomeBitmap()
        toolBar = self.CreateToolBar(wx.TB_HORIZONTAL | \
                                     wx.TB_3DBUTTONS)
        toolBar.AddSimpleTool(210, BackIcon, "Back","")
        toolBar.AddSimpleTool(211, ForeIcon, "Forward","")
        toolBar.AddSimpleTool(212, HomeIcon, "Home","")
        toolBar.SetToolBitmapSize((24,24))
        toolBar.Realize()
        self.SetToolBar(toolBar)
        self.tabs = wx.Notebook(self, -1)
        self.wizard = MyHtmlWindow(self.tabs, -1)
        self.topics = MyHtmlWindow(self.tabs, -1)
        self.scripting = MyHtmlWindow(self.tabs, -1)
        licence = MyHtmlWindow(self.tabs, -1)
        peeps = MyHtmlWindow(self.tabs, -1)
        self.tabs.AddPage(self.wizard, "Help Choosing a test!")
        self.wizard.LoadPage('help/wizard.html')
        self.tabs.AddPage(self.topics, "Topics")
        self.topics.LoadPage('help/index.html')
        self.tabs.AddPage(licence, "Licence")
        licence.LoadPage('help/COPYING')
        self.tabs.AddPage(peeps, "Peeps")
        peeps.LoadPage('help/about.html')
        self.tabs.SetSelection(tabnumber)
        self.Bind(wx.EVT_TOOL, self.GoBackPressed, id =  210)
        self.Bind(wx.EVT_TOOL, self.GoForwardPressed, id =  211)
        self.Bind(wx.EVT_TOOL, self.GoHomePressed, id =212)

    def GoBackPressed(self, event):
        pagenum = self.tabs.GetSelection()
        if (pagenum == 0):
            self.wizard.GoBack(event)
        if (pagenum == 1):
            self.topics.GoBack(event)

    def GoForwardPressed(self, event):
        pagenum = self.tabs.GetSelection()
        if (pagenum == 0):
            self.wizard.GoForward(event)
        if (pagenum == 1):
            self.topics.GoForward(event)

    def GoHomePressed(self, event):
        pagenum = self.tabs.GetSelection()
        if (pagenum == 0):
            self.wizard.LoadPage('wizard.html')
        if (pagenum == 1):
            self.topics.LoadPage('help/index.html')

    def OnCloseAbout(self, event):
        self.Close(True)

    def OnCloseWindow(self, event):
        self.Destroy()

#---------------------------------------------------------------------------
# user can change settings like variable names, decimal places, missing no.s
# using a SimpleGrid Need event handler - when new name entered, must be
#checked against others so no match each other

class VariablesFrame(wx.Dialog):
    def __init__(self,parent,id):
        wx.Dialog.__init__(self, parent,id,"SalStat - Variables", \
                           size=(500,185+wind))

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        okaybutton = wx.Button(self.m_panel1 , 2001, "Okay", wx.DefaultPosition, wx.DefaultSize, 0 )
        cancelbutton = wx.Button(self.m_panel1 , 2002, "Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )

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


        self.m_grid1 = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.vargrid = wx.grid.Grid(self,-1,) #
        self.vargrid.SetRowLabelSize(120)
        self.vargrid.SetDefaultRowSize(27, True)
        maxcols = frame.grid.m_grid.GetNumberCols()
        self.vargrid.CreateGrid(3,maxcols)
        for i in range(maxcols):
            oldlabel = frame.grid.m_grid.GetColLabelValue(i)
            self.vargrid.SetCellValue(0, i, oldlabel)
        self.vargrid.SetRowLabelValue(0,"Variable Name")
        self.vargrid.SetRowLabelValue(1,"Decimal Places")
        self.vargrid.SetRowLabelValue(2,"Missing Value")

        self.m_mgr.AddPane( self.vargrid, wx.aui.AuiPaneInfo() .Left() .CaptionVisible( False ).PaneBorder( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).DockFixed( False ).CentrePane() )

        self.m_mgr.Update()
        self.Centre( wx.BOTH )

        self.Bind(wx.EVT_BUTTON, self.OnOkayVariables, id= 2001)
        self.Bind(wx.EVT_BUTTON, self.OnCloseVariables, id =  2002)

    # this method needs to work out the other variables too
    def OnOkayVariables(self, event):
        for i in range(frame.grid.m_grid.GetNumberCols()-1):
            newlabel = self.vargrid.GetCellValue(0, i)
            if (newlabel != ''):
                frame.grid.m_grid.SetColLabelValue(i, newlabel)
            newsig = self.vargrid.GetCellValue(1, i)
            if (newsig != ''):
                try:
                    frame.grid.m_grid.SetColFormatFloat(i, -1, int(newsig))
                except ZeroDivisionError:
                    pass
        frame.grid.m_grid.ForceRefresh()
        self.Close(True)

    def OnCloseVariables(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# base html window class
class MyHtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id):
        wx.html.HtmlWindow.__init__(self, parent, id)
        ##wx.Image_AddHandler(wxJPEGHandler()) # just in case!
        self.WholeOutString = ''
        self.Saved = True

    """def OnLinkClicked(self, linkinfo):
        ref = string.split(linkinfo.GetHref(),',')
        means = []
        for i in range(1, len(ref), 2):
            if ref[i] == 'M':
                means.append(float(ref[i+1]))
            elif ref[i] == 'k':
                k = int(ref[i+1])
            elif ref[i] == 'n':
                n = int(ref[i+1])
            elif ref[i] == 'p':
                p = float(ref[i+1])
        self.Addhtml(str(means)+' '+str(k)+' '+str(n)+' '+str(p))
        if ref[0] == 'friedman':
            waste = salstat_stats.FriedmanComp(means, k, n, p)"""

    def Addhtml(self, htmlline):
        self.Saved = False
        self.AppendToPage(htmlline)
        self.WholeOutString = self.WholeOutString+htmlline + '\n'

    def write(self, TextIn):
        TextIn = '<br>'+TextIn
        self.Addhtml(TextIn)

    def LoadHtmlPage(self, event):
        dlg = wx.FileDialog(self, "Load Output File", "","","*.html|*.*", \
                            wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            outputfilename = dlg.GetPath()
            self.LoadPage(outputfilename)
            inits.update({'opendir': dlg.GetDirectory()})

    def SaveHtmlPage(self, event):
        dlg = wx.FileDialog(self, "Save Output","","","*.html|*>*",wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            outputfilename = dlg.GetPath()
            fout = open(outputfilename, "w")
            fout.write(self.WholeOutString)
            fout.close()
            inits.update({'savedir': dlg.GetDirectory()})
            self.Saved = True

    def PrintHtmlPage(self, event):
        dlg = wx.PrintDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            None #null

    def GoBack(self, event):
        if self.HistoryCanBack():
            self.HistoryBack()

    def GoForward(self, event):
        if self.HistoryCanForward():
            self.HistoryForward()

#---------------------------------------------------------------------------
# user selects which cols to analyse, and what stats to have
class DescriptivesFrame(wx.Dialog):
    def __init__( self, parent, id ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY,
                             title = "Descriptive Statistics",
                             pos = wx.DefaultPosition, size = wx.Size( 375,326 ),
                             style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        icon = images.getIconIcon()
        self.SetIcon(icon)
        ColumnList, self.colnums  = frame.grid.GetUsedCols()

        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        self.DescChoice = DescChoiceBox(self, 1107)
        self.m_checkList5 = self.DescChoice
        self.m_mgr.AddPane( self.m_checkList5, wx.aui.AuiPaneInfo() .Center() .
                            Caption( u"Select Descriptive Statistics" ).CloseButton( False ).
                            PaneBorder( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).BottomDockable( False ).TopDockable( False ) )

        self.ColChoice = wx.CheckListBox( self, 1102, wx.DefaultPosition, wx.DefaultSize, ColumnList, 0 )
        self.m_mgr.AddPane( self.ColChoice, wx.aui.AuiPaneInfo() .Center() .Caption( u"Select Column(s) to Analize" ).
                            CloseButton( False ).PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.Size( 161,93 ) ).DockFixed( False ).BottomDockable( False ).
                            TopDockable( False ).Row( 1 ).Layer( 0 ) )

        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel1, wx.aui.AuiPaneInfo() .Bottom() .CaptionVisible( False ).
                            CloseButton( False ).PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ).LeftDockable( False ).
                            RightDockable( False ).MinSize( wx.Size( -1,30 ) ) )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        okaybutton = wx.Button( self.m_panel1, 1103, u"Ok", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT  )
        bSizer2.Add( okaybutton, 0, wx.ALL, 5 )

        cancelbutton = wx.Button( self.m_panel1, 1104, u"Cancel", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT  )
        bSizer2.Add( cancelbutton, 0, wx.ALL, 5 )

        allbutton = wx.Button( self.m_panel1,105, u"Select All", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT  )
        bSizer2.Add( allbutton, 0, wx.ALL, 5 )

        nonebutton = wx.Button( self.m_panel1, 106, u"Select None", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT  )
        bSizer2.Add( nonebutton, 0, wx.ALL, 5 )

        self.m_panel1.SetSizer( bSizer2 )
        self.m_panel1.Layout()
        bSizer2.Fit( self.m_panel1 )

        self.m_mgr.Update()
        self.Centre( wx.BOTH )

        self.Bind(wx.EVT_BUTTON, self.OnOkayButton,          id = okaybutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCloseContDesc,       id = cancelbutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.DescChoice.SelectAllDescriptives, id = allbutton.GetId())
        self.Bind(wx.EVT_BUTTON,  self.DescChoice.SelectNoDescriptives, id = nonebutton.GetId())

    def OnOkayButton(self, event):
        descs = []
        for i in range(len(self.colnums)):
            if self.ColChoice.IsChecked(i):
                realColi = self.colnums[i]
                name = frame.grid.m_grid.GetColLabelValue(realColi)
                descs.append(statistics(
                    frame.grid.CleanData(realColi), name,
                    frame.grid.missing))
                #descs.append(statistics( \
                #    frame.grid.CleanData(realColi), name, \
                #    frame.grid.missing))
        ManyDescriptives(self, descs)
        self.Close(True)

    def OnCloseContDesc(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# instance of the tool window that contains the test buttons
# note this is experimental and may not be final
#---------------------------------------------------------------------------
class TransformFrame(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Transformations", \
                           size=(500,400+wind))
        #set icon for frame (needs x-platform separator!
        x = self.GetClientSize()
        winheight = x[1]
        icon = images.getIconIcon()
        self.SetIcon(icon)
        self.transform = ""
        self.transformName = ""
        self.ColumnList, self.colnums = frame.grid.GetUsedCols()
        self.cols = frame.grid.m_grid.GetNumberCols()
        l0 = wx.StaticText(self,-1,"Select Columns to Transform",pos=(10,10))
        self.ColChoice = wx.CheckListBox(self,1102, wx.Point(10,30), \
                                         wx.Size(230,(winheight * 0.8)), self.ColumnList)
        self.okaybutton = wx.Button(self, wx.ID_ANY, "Okay",wx.Point(10,winheight-35),\
                                    wx.Size(BWidth, BHeight))
        self.cancelbutton = wx.Button(self, wx.ID_ANY, "Cancel",wx.Point(100,winheight-35),\
                                      wx.Size(BWidth, BHeight))
        # common transformations:
        l1 = wx.StaticText(self, -1, "Common Transformations:", pos=(250,30))
        self.squareRootButton = wx.Button(self, wx.ID_ANY, "Square Root", wx.Point(250, 60), \
                                          wx.Size(BWidth, BHeight))
        self.logButton = wx.Button(self, wx.ID_ANY, "Logarithmic",wx.Point(250, 100), \
                                   wx.Size(BWidth, BHeight))
        self.reciprocalButton = wx.Button(self, wx.ID_ANY, "Reciprocal", wx.Point(250,140), \
                                          wx.Size(BWidth, BHeight))
        self.squareButton = wx.Button(self, wx.ID_ANY, "Square", wx.Point(250,180), \
                                      wx.Size(BWidth, BHeight))
        l2 = wx.StaticText(self, -1, "Function :", wx.Point(250, 315))
        self.transformEdit = wx.TextCtrl(self, 1114,pos=(250,335),size=(150,20))
        self.Bind(wx.EVT_BUTTON, self.OnOkayButton,        id = self.okaybutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCloseFrame,        id = self.cancelbutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.squareRootTransform, id = self.squareRootButton.GetId())
        self.Bind(wx.EVT_BUTTON, self.logTransform,        id = self.logButton.GetId())
        self.Bind(wx.EVT_BUTTON, self.reciprocalTransform, id = self.reciprocalButton.GetId())
        self.Bind(wx.EVT_BUTTON, self.squareTransform,     id = self.squareButton.GetId())

    def squareRootTransform(self, event):
        self.transform = "math.sqrt(x)"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Square Root"

    def logTransform(self, event):
        self.transform = "math.log(x)"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Logarithm"

    def reciprocalTransform(self, event):
        self.transform = "1 / x"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Reciprocal"

    def squareTransform(self, event):
        self.transform = "x * x"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Square"

    def OnOkayButton(self, event):
        # start transforming!
        # process: collect each selected column, then pass the contents through the self.transform function
        # then put the resulting column into a new column, and retitle it with the original variable
        # name plus the function.
        self.transform = self.transformEdit.GetValue()
        cols = range(self.cols)
        emptyCols = []
        for i in cols:
            if cols[i] not in self.colnums:
                emptyCols.append(cols[i])
        for i in range(len(self.colnums)):
            if self.ColChoice.IsChecked(i):
                newColi = self.colnums[i]
                oldcol = frame.grid.CleanData(newColi)
                newcol = [0]*len(oldcol)
                for j in range(len(oldcol)):
                    x = oldcol[j]
                    try:
                        newcol[j] = eval(self.transform)
                    except: # which exception would this be?
                        pass # need to do something here.
                PutData(emptyCols[i], newcol)
                # put in a nice new heading
                oldHead = frame.grid.m_grid.GetColLabelValue(self.colnums[i])
                if self.transformName == "":
                    self.transformName = ' ' + self.transform
                oldHead = oldHead + self.transformName
                frame.grid.m_grid.SetColLabelValue(emptyCols[i], oldHead)
                emptyCols.pop(emptyCols[i])
        self.Close(True)

    def OnCloseFrame(self, event):
        self.Close(True)

class formulaBar ( wx.Panel ):

    def __init__( self, parent , *args,**params):
        wx.Panel.__init__ ( self, parent, *args, **params)

        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_textCtrl1 = wx.TextCtrl( self, wx.ID_ANY,
                                        wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                        wx.TE_CHARWRAP|wx.TE_MULTILINE|wx.TE_RICH2|
                                        wx.TE_WORDWRAP|wx.NO_BORDER )

        self.m_textCtrl1.SetMinSize( wx.Size( 160,25 ) )

        bSizer1.Add( self.m_textCtrl1, 0, 0, 5 ) # wx.EXPAND

        #self.m_button1 = wx.Button( self, wx.ID_ANY, u">>",
    #                    wx.DefaultPosition, wx.DefaultSize,
    #                    wx.BU_EXACTFIT|wx.DOUBLE_BORDER )
        #bSizer1.Add( self.m_button1, 0, wx.EXPAND, 5 )

        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
# call instance of DataGrid
# This is main interface of application
class MainFrame(wx.Frame):
    def __init__(self, parent, appname ):
        self.path = None
        wx.Frame.__init__(self,parent,-1,"SalStat Statistics",
                          size=wx.Size(640,480 ), pos=wx.DefaultPosition)

        self.m_notebook1 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.logPanel = LogPanel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )

        self.defaultDialogSettings = {'Title': None,
                                      'icon': images.getIconIcon()}

        self.m_mgr = aui.AuiManager()# wx.aui
        self.m_mgr.SetManagedWindow( self )

        #set icon for frame (needs x-platform separator!
        icon = images.getIconIcon()
        self.SetIcon(icon)
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
        #-----------------------
        # Se crea el menubar
        #set up menus
        file_menu = wx.Menu()
        edit_menu = wx.Menu()
        prefs_menu = wx.Menu()
        describe_menu = wx.Menu()
        analyse_menu = wx.Menu()
        #analyse2_menu = wx.Menu()
        preparation_menu = wx.Menu()
        chart_menu = wx.Menu()
        help_menu = wx.Menu()
        #add contents of menu

        self.mn1= wx.MenuItem(file_menu, wx.ID_ANY, '&New Data')
        self.mn1.SetBitmap(NewIcon)
        file_menu.AppendItem(self.mn1)
        #file_menu.Append(ID_FILE_NEWOUTPUT, 'New &Output Sheet')
        self.mn2=file_menu.Append(wx.ID_ANY, '&Open...')
        self.mn2.SetBitmap(OpenIcon)
        self.mn3=file_menu.Append(wx.ID_ANY, '&Save')
        self.mn3.SetBitmap(SaveIcon)
        self.mn4=file_menu.Append(wx.ID_ANY, 'Save &As...')
        self.mn4.SetBitmap(SaveAsIcon)
        self.mn5=file_menu.AppendSeparator()
        self.mn6=file_menu.Append(wx.ID_ANY, '&Print...')
        self.mn6.SetBitmap(PrintIcon)
        file_menu.AppendSeparator()
        self.mn7=file_menu.Append(wx.ID_ANY, 'E&xit')
        self.mn7.SetBitmap(ExitIcon)
        self.mn8= wx.MenuItem(edit_menu, wx.ID_ANY,'Cu&t')
        self.mn8.SetBitmap(CutIcon)
        edit_menu.AppendItem(self.mn8)
        self.mn9=edit_menu.Append(wx.ID_ANY, '&Copy')
        self.mn9.SetBitmap(CopyIcon)
        self.mn10=edit_menu.Append(wx.ID_ANY, '&Paste')
        self.mn10.SetBitmap(PasteIcon)
        self.mn11=edit_menu.Append(wx.ID_ANY, 'Select &All')
        self.mn12=edit_menu.Append(wx.ID_ANY, '&Find and Replace...')
        self.mn12.SetBitmap(FindRIcon)
        edit_menu.AppendSeparator()
        self.mn13=edit_menu.Append(wx.ID_ANY, 'Delete Current Column')
        self.mn14=edit_menu.Append(wx.ID_ANY, 'Delete Current Row')
        self.mn15=prefs_menu.Append(wx.ID_ANY, 'Variables...')
        self.mn16=prefs_menu.Append(wx.ID_ANY, 'Add Columns and Rows...')
        self.mn17=prefs_menu.Append(wx.ID_ANY, 'Change Cell Size...')
        self.mn18=prefs_menu.Append(wx.ID_ANY, 'Change the Font...')

        # se crea el menu de datos estadisticos con base en las caracteristicas disponibles
        self.mn19=preparation_menu.Append(wx.ID_ANY, 'Descriptive Statistics')
        self.mn20=preparation_menu.Append(wx.ID_ANY, 'Transform Data')
        self.mn21=preparation_menu.Append(wx.ID_ANY, 'short data')
        self.menuStats= list()
        for (mainItem,subitems) in STATS.items():
            newmenu = wx.Menu()
            for item in subitems:
                menuItem = wx.MenuItem( newmenu, wx.ID_ANY, item, wx.EmptyString, wx.ITEM_NORMAL )
                # setting the callbak
                self.Bind(wx.EVT_MENU, getattr(self, item), id = menuItem.GetId())
                newmenu.AppendItem(menuItem )
            analyse_menu.AppendSubMenu(newmenu,mainItem)

        self.mn26= chart_menu.Append(wx.ID_ANY, 'Line Chart of All Means...')
        self.mn27= chart_menu.Append(wx.ID_ANY, 'Bar Chart of All Means...')
        self.mn273= chart_menu.Append(wx.NewId(), 'Lines')
        self.mn271= chart_menu.Append(wx.NewId(), 'Scatter')
        self.mn272= chart_menu.Append(wx.NewId(), 'Box&Wishker Plot')
        self.mn274= chart_menu.Append(wx.NewId(), 'Lineal Regress')
        self.mn275= chart_menu.Append(wx.ID_ANY, 'Ternary Plot')
        self.mn276= chart_menu.Append(wx.ID_ANY, 'Probability plot')

        self.mn28=help_menu.Append(wx.ID_ANY, '&What Test Should I Use...')
        self.mn29=help_menu.Append(wx.ID_ANY, '&Topics...')
        self.mn30=help_menu.Append(wx.ID_ANY, '&Licence...')
        self.mn31=help_menu.Append(wx.ID_ANY, '&About...')
        #set up menu bar
        menuBar = wx.MenuBar()
        menuBar.Append(file_menu, '&File')
        menuBar.Append(edit_menu, '&Edit')
        menuBar.Append(prefs_menu, '&Preferences')
        menuBar.Append(preparation_menu, 'P&reparation')
        menuBar.Append(analyse_menu, '&Statistics')
        menuBar.Append(chart_menu, '&Graph')
        menuBar.Append(help_menu, '&Help')
        self.SetMenuBar(menuBar)
        #------------------------
        #create small status bar
        self.CreateStatusBar()
        self.SetStatusText('SalStat Statistics')

        #----------------------
        # se crea una barra de herramientas
        
        tb1= aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                            agwStyle=  aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_HORZ_LAYOUT)

        self.bt1 = tb1.AddSimpleTool(10, "New",  NewIcon,"New")
        self.bt2 = tb1.AddSimpleTool(20, "Open", OpenIcon,"Open")
        self.bt3 = tb1.AddSimpleTool(30, "Save", SaveIcon,"Save")
        self.bt4 = tb1.AddSimpleTool(40, "Save As",SaveAsIcon,"Save As")
        self.bt5 = tb1.AddSimpleTool(50, "Print",PrintIcon,"Print")
        tb1.AddSeparator()
        self.bt11= tb1.AddSimpleTool(wx.ID_ANY,"Undo",UndoIcon,"Undo")
        self.bt12= tb1.AddSimpleTool(wx.ID_ANY,"Redo",RedoIcon,"Redo")
        tb1.AddSeparator()
        self.bt6 = tb1.AddSimpleTool(60, "Cut",  CutIcon, "Cut")
        self.bt7 = tb1.AddSimpleTool(70, "Copy", CopyIcon, "Copy")
        self.bt8 = tb1.AddSimpleTool(80, "Paste",PasteIcon, "Paste")
        tb1.AddSeparator()
        self.bt9 = tb1.AddSimpleTool(85, "Preferences",PrefsIcon, "Preferences")
        self.bt10= tb1.AddSimpleTool(90, "Help", HelpIcon, "Help")
        tb1.SetToolBitmapSize((24,24))
        tb1.Realize()

        #--------------------

        #still need to define event handlers
        #set up the datagrid

        self.grid = SimpleGrid(self, self.logPanel, size= (500,50))
        self.grid.Saved = False
        self.grid.m_grid.SetDefaultColSize(60, True)
        self.grid.m_grid.SetRowLabelSize(40)


        # adicion de panel para mostrar las respuestas
        self.answerPanel = NoteBookSheet(self)
        self.answerPanel2 = ScriptPanel(self, self.logPanel, self.grid.m_grid, self.answerPanel)

        #--------------------------------------------
        self.m_notebook1.AddPage( self.logPanel, u"Log", True )

        #--------------------------------
        self.scriptPanel = wx.py.shell.Shell(self.m_notebook1)
        self.scriptPanel.wrap(True)

        self.m_notebook1.AddPage( self.scriptPanel , u"Shell", False )
        #-------------------------------
        self.formulaBarPanel= formulaBar(self,wx.ID_ANY)

        self.m_mgr.AddPane( self.formulaBarPanel,
                            aui.AuiPaneInfo().ToolbarPane().Top().Row(1).
                            Position(1).
                            LeftDockable(False).RightDockable(False).
                            MinSize( wx.Size( -1,15 ) ).CloseButton( False ) )

        self.m_mgr.AddPane(self.grid,
                           aui.AuiPaneInfo().Centre().
                           CaptionVisible(True).Caption('Main Panel').
                           MaximizeButton(True).MinimizeButton(True).
                           CloseButton( False ).MinSize( wx.Size( 240,-1 )))

        self.m_mgr.AddPane(self.answerPanel,
                           aui.AuiPaneInfo().Centre().Right().
                           CaptionVisible(True).Caption(("Output Panel")).
                           MinimizeButton(True).Resizable(True).MaximizeButton(True).
                           CloseButton( False ).MinSize( wx.Size( 240,-1 )))

        self.m_mgr.AddPane( tb1, aui.AuiPaneInfo().
                            ToolbarPane().Top().Row(1).
                            LeftDockable( False ).RightDockable( False ).
                            CloseButton( False ) )

        self.m_mgr.AddPane(self.answerPanel2,
                           aui.AuiPaneInfo().Centre().Right().
                           CaptionVisible(True).Caption(("Script Panel")).
                           MinimizeButton().Resizable(True).MaximizeButton(True).
                           CloseButton( False ).MinSize( wx.Size( 240,-1 )))

        self.panelNtb = self.m_mgr.AddPane( self.m_notebook1,
                                            aui.AuiPaneInfo() .Bottom() .
                                            CloseButton( False ).MaximizeButton( True ).
                                            Caption(('Shell')).
                                            MinimizeButton().PinButton( False ).
                                            Dock().Resizable().FloatingSize( wx.DefaultSize ).
                                            CaptionVisible(True).
                                            DockFixed( False ).BestSize(wx.Size(-1,150)))
        self.BindEvents()
        self.m_mgr.Update()

    def BindEvents(self):
        # grid callback
        self.grid.m_grid.Bind( wx.grid.EVT_GRID_CMD_SELECT_CELL, self._cellSelectionChange )
        self.grid.m_grid.Bind( wx.grid.EVT_GRID_SELECT_CELL, self._cellSelectionChange )
        #-----------------
        # para el toolbar
        self.Bind(wx.EVT_MENU, self.GoClearData,        id= self.bt1.GetId())
        self.Bind(wx.EVT_MENU, self.grid.LoadXls,       id= self.bt2.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SaveXls,       id= self.bt3.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SaveXlsAs,     id= self.bt4.GetId())
        ##self.Bind(wx.EVT_MENU, self.grid.PrintPage, id = self.bt5.GetId())
        self.Bind(wx.EVT_MENU, self.grid.CutData,       id= self.bt6.GetId())
        self.Bind(wx.EVT_MENU, self.grid.CopyData,      id= self.bt7.GetId())
        self.Bind(wx.EVT_MENU, self.grid.PasteData,     id= self.bt8.GetId())
        self.Bind(wx.EVT_MENU, self.GoVariablesFrame,   id= self.bt9.GetId())
        self.Bind(wx.EVT_MENU, self.GoHelpAboutFrame,   id= self.bt10.GetId())
        self.Bind(wx.EVT_MENU, self.grid.Undo,          id= self.bt11.GetId())
        self.Bind(wx.EVT_MENU, self.grid.Redo,          id= self.bt12.GetId())
        #-----------------
        # Menu
        self.Bind(wx.EVT_MENU, self.GoClearData,        id= self.mn1.GetId())
        self.Bind(wx.EVT_MENU, self.grid.LoadXls,       id= self.mn2.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SaveXls,       id= self.mn3.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SaveXlsAs,     id= self.mn4.GetId())
        ##self.Bind(wx.EVT_MENU, seelf.grid.SaveXlsAs,  id= ID_FILE_PRINT)
        self.Bind(wx.EVT_MENU, self.EndApplication,     id= self.mn7.GetId())
        self.Bind(wx.EVT_MENU, self.grid.CutData,       id= self.mn8.GetId())
        self.Bind(wx.EVT_MENU, self.grid.CopyData,      id= self.mn9.GetId())
        self.Bind(wx.EVT_MENU, self.grid.PasteData,     id= self.mn10.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SelectAllCells,id= self.mn11.GetId())
        self.Bind(wx.EVT_MENU, self.GoFindDialog,       id= self.mn12.GetId())
        self.Bind(wx.EVT_MENU, self.grid.DeleteCurrentCol,id= self.mn13.GetId())
        self.Bind(wx.EVT_MENU, self.grid.DeleteCurrentRow,id= self.mn14.GetId())
        self.Bind(wx.EVT_MENU, self.GoVariablesFrame,   id= self.mn15.GetId())
        self.Bind(wx.EVT_MENU, self.GoEditGrid,         id= self.mn16.GetId())
        self.Bind(wx.EVT_MENU, self.GoGridPrefFrame,    id= self.mn17.GetId())
        self.Bind(wx.EVT_MENU, self.GoFontPrefsDialog,  id= self.mn18.GetId())
        self.Bind(wx.EVT_MENU, self.GoContinuousDescriptives,id= self.mn19.GetId())
        self.Bind(wx.EVT_MENU, self.GoTransformData,    id= self.mn20.GetId())
        self.Bind(wx.EVT_MENU, self.shortData,          id= self.mn21.GetId())

        self.Bind(wx.EVT_MENU, self.GoChartWindow,      id= self.mn26.GetId())
        self.Bind(wx.EVT_MENU, self.GoBarChartWindow,   id= self.mn27.GetId())
        self.Bind(wx.EVT_MENU, self.GoScatterPlot,      id= self.mn271.GetId())
        self.Bind(wx.EVT_MENU, self.GoBoxWishkerPlot,   id= self.mn272.GetId())
        self.Bind(wx.EVT_MENU, self.GoLinesPlot,        id= self.mn273.GetId())
        self.Bind(wx.EVT_MENU, self.GoLinRegressPlot,   id= self.mn274.GetId())
        self.Bind(wx.EVT_MENU, self.GoTernaryplot,      id= self.mn275.GetId())
        self.Bind(wx.EVT_MENU, self.GoProbabilityplot,  id= self.mn276.GetId())

        # controlling the expansion of the notebook
        self.m_notebook1.Bind( wx.EVT_LEFT_DCLICK, self._OnNtbDbClick )

        self.grid.m_grid.setPadreCallBack(self)
        if 0:
            self.Bind(wx.EVT_MENU, self.GoCheckOutliers,    id = self.mn26.GetID())
            self.Bind(wx.EVT_MENU, self.GoHelpAboutFrame,   id = self.mn27.GetID())
            self.Bind(wx.EVT_MENU, self.GoHelpWizardFrame,  id = self.mn28.GetID())
            self.Bind(wx.EVT_MENU, self.GoHelpTopicsFrame,  id = self.mn29.GetID())
            self.Bind(wx.EVT_MENU, self.GoHelpLicenceFrame, id = self.mn30.GetID())

    def _cellSelectionChange(self, event):
        # se lee el contenido de la celda seleccionada
        row = event.GetRow()
        col = event.GetCol()
        texto =self.grid.m_grid.GetCellValue(row, col)
        self.formulaBarPanel.m_textCtrl1.SetValue(texto)


    def _OnNtbDbClick(self,event):
        for pane in self.mm_mgr.AllPanes:
            if pane.name == 'Bottom Panel':
                break
        if not pane.IsMaximized():
            self.mm_mgr.MaximizePane(pane)
        else:
            pane.MinimizeButton(True)
        #self.m_mgr.Update()

    def GoClearData(self, evt):
        #shows a new data entry frame
        self.grid.m_grid.ClearGrid()

    def GoNewOutputSheet(self, evt):
        #shows a new output frame
        SheetWin = OutputSheet(frame, -1)
        SheetWin.Show(True)

    def GoFindDialog(self, event):
        # Shows the find & replace dialog
        # NOTE - this doesn't appear to work on the grid, so I might be missing something...
        data = wx.FindReplaceData()
        dlg = wx.FindReplaceDialog(self.grid, data, 'Find and Replace', \
                                   wx.FR_REPLACEDIALOG)
        dlg.data = data
        dlg.Show(True)

    def GoEditGrid(self, event):
        #shows dialog for editing the data grid
        win = EditGridFrame(frame, -1)
        win.Show(True)

    def GoVariablesFrame(self, evt):
        # shows Variables dialog
        win = VariablesFrame(frame, -1)
        win.Show(True)

    def GoGridPrefFrame(self, evt):
        # shows Grid Preferences form
        win = GridPrefs(frame, -1)
        win.Show(True)

    def GoFontPrefsDialog(self, evt):
        # shows Font dialog for the data grid (output window has its own)
        data = wx.FontData()
        dlg = wx.FontDialog(frame, data)
        icon = images.getIconIcon()
        self.SetIcon(icon)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            #data2 = data.GetChosenFont()
            self.grid.m_grid.SetDefaultCellFont(data.GetChosenFont())

    def GoContinuousDescriptives(self, evt):
        # shows the continuous descriptives dialog
        win = DescriptivesFrame(frame, -1)
        win.Show(True)

    def GoTransformData(self, event):
        win = TransformFrame(frame, -1)
        win.Show(True)

    def GoCheckOutliers(self, event):
        pass

    def GoChartWindow(self, event):
        waste, colnums = self.grid.GetUsedCols()
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
        data = [statistics(self.grid.CleanData(cols), 'noname',None) for cols in [colnums[m] for m in selectedcols]]
        data = [data[i].mean for i in range(len(data))]
        plt= plot(parent = self, typePlot= 'plotLine',
                  data2plot= ((range(len(data)),data,'Mean'),),
                  xlabel = 'variable',
                  ylabel= 'mean',
                  title= 'Line Chart of all means',
                  xtics= [waste[i] for i in selectedCols])
        plt.Show()
        
    def GoTernaryplot(self, event):
        waste, colnums = self.grid.GetUsedCols()
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
        elif len(selectedcols) != 3:
            self.logPanel.write('You have to select 3 columns a, b and c')
            return
        
        data = [self.grid.CleanData(cols) for cols in [colnums[m] for m in selectedcols]]
        tam = [len(dat) for dat in data]
        if (tam[0] != tam[1]) or (tam[0] != tam[2]):
            self.logPanel.write('the selected columns must have the same quantity of elements')
            return
        
        legend = u''
        data= [data[0], data[1], data[2], legend]
            
        plt= plot(parent=    self,
                  typePlot=  'plotTrian',
                  data2plot= data, 
                  title=     'Ternary Plot')
        plt.Show()

    def GoBarChartWindow(self, event):
        waste, colnums = self.grid.GetUsedCols()
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
        data = [statistics(self.grid.CleanData(cols),'noname',None) for cols in [colnums[m] for m in selectedcols]]
        data = [data[i].mean for i in range(len(data))]
        plt= plot(parent = self, typePlot= 'plotBar',
                  data2plot= ((data,'Mean'),),
                  xlabel= 'variable',
                  ylabel= 'value',
                  title= 'Bar Chart of all means')
        plt.Show()

    def GoHelpWizardFrame(self, event):
        # shows the "wizard" in the help box
        win = AboutFrame(frame, -1, 0)
        win.Show(True)

    def GoHelpTopicsFrame(self, event):
        # shows the help topics in the help box
        win = AboutFrame(frame, -1, 1)
        win.Show(True)

    def GoHelpLicenceFrame(self, evt):
        # shows the licence in the help box
        win = AboutFrame(frame, -1, 2)
        win.Show(True)

    def GoHelpAboutFrame(self, evt):
        # Shows the "About" thing in the help box
        win = AboutFrame(frame, -1, 3)
        win.Show(True)

    def GoScatterPlot(self,event):
        waste, colnums = self.grid.GetUsedCols()
        if colnums == []:
            self.SetStatusText('You need some data to draw a graph!')
            return
        selection = selectDialogData2plot(self,waste)
        if selection.ShowModal() != wx.ID_OK:
            selection.Destroy()
            return
        (xcol,ycol) = selection.getData()
        selection.Destroy()
        data = [self.grid.CleanData(col) for col in (colnums[xcol],colnums[ycol])]
        if len(data[0]) != len(data[1]):
            self.SetStatusText('x and y data mus have the same size!')
            return
        plt= plot(parent = self, typePlot= 'plotScatter',
                  data2plot= ((data[0],data[1],waste[xcol] +u' Vs '+ waste[ycol]),),
                  xlabel= waste[xcol],
                  ylabel= waste[ycol],
                  title= 'Scatter Plot')
        plt.Show()

    def GoBoxWishkerPlot(self,event):
        waste, colnums = self.grid.GetUsedCols()
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
        data = [self.grid.CleanData(cols) for cols in [colnums[m] for m in selectedcols]]
        plt= plot(parent = self, typePlot= 'boxPlot',
                  data2plot= data,
                  xlabel = 'variable',
                  ylabel = 'value',
                  title= 'Box & whiskler plot',
                  xtics=  [waste[i] for i in selectedcols] )

        plt.Show()

    def GoLinesPlot(self, event):
        waste, colnums = self.grid.GetUsedCols()
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
        data = [self.grid.CleanData(cols) for cols in [colnums[m] for m in selectedcols]]
        data = [(range(len(data[i])),data[i],waste[i]) for i in range(len(data))]

        plt= plot(parent = self, typePlot= 'plotLine',
                  data2plot= data,
                  xlabel = '',
                  ylabel = 'value',
                  title= 'Line plot')

        plt.Show()

    def GoLinRegressPlot(self, event):
        waste, colnums = self.grid.GetUsedCols()
        if colnums == []:
            self.SetStatusText('You need some data to draw a graph!')
            return
        selection = selectDialogData2plot(self,waste)
        if selection.ShowModal() != wx.ID_OK:
            selection.Destroy()
            return
        (xcol,ycol) = selection.getData()
        selection.Destroy()
        data = [self.grid.CleanData(cols) for cols in [colnums[i] for i in (xcol,ycol)]]
        if len(data[0]) != len(data[1]):
            self.SetStatusText('x and y data mus have the same size!')
            return
        plt= plot(parent = self, typePlot= 'plotLinRegress',
                  data2plot= (data[0],data[1],waste[xcol] +u' Vs '+ waste[ycol]),
                  xlabel = waste[xcol], ylabel = waste[ycol],
                  title= 'Lin Regress plot' )
        plt.Show()

    def GoProbabilityplot(self, event):
        ColumnList, colnums = self.grid.GetUsedCols()
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
        (selectedcols,) = selection.GetValue()
        selection.Destroy()
        if len(selectedcols) == 0:
            self.SetStatusText('You need to select some data to draw a graph!')
            return
        values = [ [pos for pos, value in enumerate( ColumnList )
                    if value == val
                    ][0]
                   for val in selectedcols
                   ]
        data = [self.grid.CleanData(cols) for cols in [colnums[m] for m in values]]
        plt= plot(parent = self, typePlot= 'probabilityPlot',
                  data2plot= data,
                  title=     'Probability Plot',
                  xlabel=    'Order Statistic Medians',
                  ylabel=    'Ordered Values')
        plt.Show()
        
    def EndApplication(self, evt):
        # close the application (need to check for new data since last save)
        # need to save the inits dictionary to .salstatrc
        if 0:
            dims = self.GetSizeTuple()
            inits.update({'gridsizex': dims[0]})
            inits.update({'gridsizey': dims[1]})
            dims = self.GetPositionTuple()
            inits.update({'gridposx': dims[0]})
            inits.update({'gridposy': dims[1]})
            dims = output.GetSizeTuple()
            inits.update({'outputsizex': dims[0]})
            inits.update({'outputsizey': dims[1]})
            dims = output.GetPositionTuple()
            inits.update({'outputposx': dims[0]})
            inits.update({'outputposy': dims[1]})
            initskeys = inits.keys()
            initsvalues = inits.values()
            initfilename = ini.initfile
            fout = file(initfilename,'w')
            for i in range(len(initskeys)):
                fout.write(str(initskeys[i])+' '+str(initsvalues[i])+'\n')
            fout.close()
        if self.grid.Saved == False:
            win = SaveDialog(self, -1)
            win.Show(True)
        else:
            frame.Destroy()
#------------------------------------------
# definicion de las funciones estadisticas
#------------------------------------------
    def _statsType1(self, functionName, useNumpy = True,
                    requiredcols= None,allColsOneCalc = False,
                    nameResults= None, dataSquare= False):
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()
        bt1= group('StaticText', ('Select the columns to analyse',) )
        bt2 = group('CheckListBox', (ColumnList,))
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
            self.logPanel.write("you don't select any items")
            return

        if len(colNameSelect) < None:
            self.logPanel.write("you have to select at least %i columns"%requiredcols)
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
                col = numpy.array(GetData(colnums[ pos ]))
                col.shape = (len(col),1)
                colums.append(col)
        else:
            colums = [ GetData(colnums[ pos ]) for pos in values]

        if dataSquare:
            # identifica que las columnas seleccionadas deben tener igual
            #  cantidad de elementos
            lendata= [len(col) for col in colums]
            if sum([1 for leni in lendata if leni == lendata[0]]) <> len(colums):
                return "the data must have the same size"

        if allColsOneCalc:
            result = getattr(stats, functionName)( *colums )
        else:
            # se hace los calculos para cada columna
            result = [getattr(stats, functionName)( col ) for col in colums]

        # se muestra los resultados
        if nameResults == None:
            output.addColData(colNameSelect, functionName)
        else:
            output.addColData(nameResults, functionName)
        if functionName in ['kurtosis','kurtosistest','skewtest',
                            'normaltest','mode']:
            opt = False
            try:
                len(result[0])
            except:
                opt = True

            if opt:
                output.addColData(result)
            else:
                for i in range(len(result[0])):
                    res1= [res[i] for res in result]
                    output.addColData(res1)

        else:
            output.addColData(result)

        self.logPanel.write(functionName + ' successfull')

    def _statsType2(self, functionName, texto = 'moment',spinData= (1,100,1),
                    factor = 1, useNumpy = True):
        ''''select plus spin crtl'''
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()
        bt1= group('StaticText', ('Columns to analyse',) )
        bt2= group('CheckListBox', (ColumnList,))
        bt3= group('SpinCtrl', spinData)
        bt4= group('StaticText', (texto,) )
        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt3, bt4])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (colNameSelect, moment) = values
        moment = moment * factor
        if len( colNameSelect ) == 0:
            self.logPanel.write("you don't select any items")
            return
        if not isinstance(colNameSelect, (list, tuple)):
            colNameSelect = [colNameSelect]
            moment = [moment]
            
        values = [ [pos for pos, value in enumerate( ColumnList )
                    if value == val
                    ][0]
                   for val in colNameSelect
                   ]
        # -------------------
        if useNumpy:
            colums  = list()
            for pos in values:
                col = numpy.array(GetData(colnums[ pos ]))
                col.shape = (len(col),1)
                colums.append(col)
        else:
            colums = [ GetData(colnums[ pos ]) for pos in values]
        # se hace los calculos para cada columna
        result = [getattr(stats, functionName)( col, moment ) for col in colums]
        # se muestra los resultados
        output.addColData(colNameSelect, functionName)
        output.addColData(result)
        self.logPanel.write(functionName + ' successfull')

    def _statsType3(self, functionName, texto1 = u'',
                    texto2 = u'', useNumpy = False, nameCols = None,
                    **params):
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   (texto1,) )
        bt2= group('Choice',       (ColumnList,))
        bt3= group('StaticText',   (texto2,) )

        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt2, bt3])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (xcolname, ycolname) = values
        if len( xcolname ) == 0 or len( ycolname ) == 0:
            self.logPanel.write("you don't select any items")
            return
        if not isinstance(xcolname, (list, tuple)):
            xcolname = [xcolname]
            ycolname = [ycolname]
        xvalue= [ [pos for pos, value in enumerate( ColumnList )
                   if value == val
                   ][0]
                  for val in xcolname
                  ][0]
        yvalue= [ [pos for pos, value in enumerate( ColumnList )
                   if value == val
                   ][0]
                  for val in ycolname
                  ][0]
        # -------------------
        if useNumpy:
            xcolumn = numpy.array(GetData(colnums[ xvalue ]))
            ycolumn = numpy.array(GetData(colnums[ yvalue ]))
            xcolumn.shape= (len(xcolumn), 1)
            ycolumn.shape= (len(ycolumn), 1)
        else:
            xcolumn = GetData(colnums[ xvalue ])
            ycolumn = GetData(colnums[ yvalue ])

        # se hace los calculos
        result = getattr(stats, functionName)( xcolumn, ycolumn, **params)
        # se muestra los resultados
        if nameCols != None:
            output.addColData(nameCols, functionName)
            output.addColData(result)
        else:
            output.addColData(result, functionName)
        self.logPanel.write(functionName + ' successfull')


    def shortData(self,event):
        functionName = "short"
        useNumpy = False
        requiredcols= None
        allColsOneCalc = False,
        dataSquare= False
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()
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
            self.logPanel.write("you don't select any items")
            return

        if len(colNameSelect) < None:
            self.logPanel.write("you have to select at least %i columns"%requiredcols)
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
        output.addColData(colNameSelect, functionName)
        output.addColData(colums[0])
        output.addColData(colums[1])
        self.logPanel.write(functionName + ' successfull')


    def geometricmean(self,event):
        self._statsType1("geometricmean")

    def harmonicmean(self,event):
        self._statsType1("harmonicmean")

    def mean(self,event):
        self._statsType1("mean")

    def median(self,event):
        self._statsType1("median")

    def medianscore(self,event):
        self._statsType1("medianscore")

    def mode(self,event):
        self._statsType1("mode")

    def moment(self,event):
        self._statsType2("scoreatpercentile", texto = 'moment',
                         spinData = (1,100,1))

    def variation(self,event):
        self._statsType1("variation")

    def skew(self,event):
        self._statsType1("skew")

    def kurtosis(self,event):
        self._statsType1("kurtosis")

    def skewtest(self,event):
        self._statsType1("skewtest", useNumpy = False)

    def kurtosistest(self,event):
        self._statsType1("kurtosistest", useNumpy = False)

    def normaltest(self,event):
        self._statsType1("normaltest", useNumpy = True)

    def itemfreq(self,event):
        functionName = "itemfreq"
        useNumpy = True
        requiredcols= None
        allColsOneCalc = False,
        dataSquare= False
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()
        bt1= group('StaticText', ('Select the columns to analyse',) )
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
            self.logPanel.write("you don't select any items")
            return

        if len(colNameSelect) < None:
            self.logPanel.write("you have to select at least %i columns"%requiredcols)
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
            colums = [ stats.shellsort(GetData(colnums[ pos ]))[0] for pos in values]

        if dataSquare:
            # identifica que las columnas seleccionadas deben tener igual
            #  cantidad de elementos
            lendata= [len(col) for col in colums]
            if sum([1 for leni in lendata if leni == lendata[0]]) <> len(colums):
                return "the data must have the same size"

        if allColsOneCalc:
            result = getattr(stats, functionName)( *colums )
        else:
            # se hace los calculos para cada columna
            result = [getattr(stats, functionName)( col ) for col in colums]

        # se muestra los resultados
        output.addColData(colNameSelect, functionName)

        for i in range(len(result[0])):
            res1= [res[i] for res in result]
            output.addColData(res1)

        self.logPanel.write(functionName + ' successfull')



    def scoreatpercentile(self,event):
        self._statsType2("scoreatpercentile", texto = ' %',
                         spinData = (0,100,0))

    def percentileofscore(self,event):
        #adiconar dos parametros pendientes
        self._statsType2("scoreatpercentile", texto = 'Score',)

    def histogram(self,event):
        #adiconar dos parametros pendientes
        self._statsType2("histogram", texto = 'number of bins',
                         spinData = (1,100,10))

    def cumfreq(self,event):
        #adiconar un parametro pendiente
        self._statsType2("cumfreq", texto = 'number of beans' )

    def relfreq(self,event):
        #adiconar un parametro pendiente
        self._statsType2("relfreq", texto = 'number of bins',
                         spinData = (1,100,10))

    #def obrientransform(self,event):
    #    self.logPanel.write('obrientransform')

    def samplevar(self,event):
        self._statsType1("samplevar")

    def samplestdev(self,event):
        self._statsType1("samplestdev")

    def signaltonoise(self,event):
        self._statsType2("signaltonoise", texto = 'dimension',
                         spinData = (0,100,0))

    def var(self,event):
        self._statsType1("var")

    def stdev(self,event):
        self._statsType1("stdev")

    def sterr(self,event):
        self._statsType1("sterr")

    def sem(self,event):
        self._statsType1("sem")

    def z(self,event):
        self._statsType2("z", texto = 'score',
                         spinData = (1,100, 1))

    def zs(self,event):
        self._statsType1("zs")

    def zmap(self,event):
        self.logPanel.write('zmap')

    def threshold(self,event):
        functionName= "threshold"
        group= lambda x,y: (x,y)
        setting= self.defaultDialogSettings
        setting['Title']= functionName
        ColumnList, colnums= frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('Columns to analyse',),)
        bt2= group('Choice',       (ColumnList,),)
        bt3= group('NumTextCtrl',  (),)
        bt4= group('StaticText',   ("threshmin",),)
        bt5= group('NumTextCtrl',  (), )
        bt6= group('StaticText',   ("threshmax",),)
        bt7= group('NumTextCtrl',  (),)
        bt8= group('StaticText',   ("newval",),)

        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt3, bt4])
        structure.append([bt5, bt6])
        structure.append([bt7, bt8])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (colNameSelect, threshmin, threshmax, newval) = values
        if len( colNameSelect ) == 0:
            self.logPanel.write("you don't select any items")
            return
        if threshmin == None or threshmax == None or newval == None:
            self.logPanel.write("you don't input all the required values")
            return
        values = [ [pos for pos, value in enumerate( ColumnList )
                    if value == val
                    ][0]
                   for val in colNameSelect
                   ]
        # -------------------
        useNumpy = True
        if useNumpy:
            colums  = list()
            for pos in values:
                col = numpy.array(GetData(colnums[ pos ]))
                col.shape = (len(col),1)
                colums.append(col)
        else:
            colums = [ GetData(colnums[ pos ]) for pos in values]

        # se hace los calculos para cada columna
        result = [getattr(stats, functionName)( col, threshmin, threshmax, newval ) for col in colums]
        # se muestra los resultados
        output.addColData(colNameSelect, functionName)
        output.addColData(result)
        self.logPanel.write(functionName + ' successfull')

    def trimboth(self,event):
        self._statsType2("trimboth", texto = '% proportiontocut',
                         spinData = (1,100, 1), factor = 0.01)

    def trim1(self,event):
        functionName = "trim1"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('Columns to analyse',) )
        bt2= group('CheckListBox', (ColumnList,))
        bt3= group('NumTextCtrl',  ())
        bt4= group('StaticText',   ("proportiontocut",) )
        bt5= group('Choice',       (("right","left"),) )
        bt6= group('StaticText',   ("proportiontocut",) )

        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt3, bt4])
        structure.append([bt5, bt6])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (colNameSelect, proportiontocut, tail) = values
        if len( colNameSelect ) == 0:
            self.logPanel.write("you don't select any items")
            return
        values = [ [pos for pos, value in enumerate( ColumnList )
                    if value == val
                    ][0]
                   for val in colNameSelect
                   ]

        # -------------------
        colums = [ GetData(colnums[ pos ]) for pos in values]
        # se hace los calculos para cada columna
        result = [getattr(stats, functionName)( col, proportiontocut, tail ) for col in colums]
        # se muestra los resultados
        output.addColData(colNameSelect, functionName)
        output.addColData(result)
        self.logPanel.write(functionName + ' successfull')


    #def covariance(self, event):
    #    self._statsType1("covariance")

    #def correlation(self, event):
    #    self.logPanel.write('correlation')

    def paired(self, event):
        self._statsType3(functionName = "paired",
                         texto1 = u"X Column to analyse",
                         texto2 = u"Y Column to analyse",
                         useNumpy = False, allData = True)

    def pearsonr(self, event):
        self._statsType3(functionName = "pearsonr",
                         texto1 = u"X Column to analyse",
                         texto2 = u"Y Column to analyse",
                         useNumpy = True,
                         nameCols= ("Pearson's r"," two-tailed p-value"))


    def spearmanr(self, event):
        self._statsType3(functionName = "spearmanr",
                         texto1 = u"X Column to analyse",
                         texto2 = u"Y Column to analyse",
                         useNumpy = True,
                         nameCols= ("Spearman's r","two-tailed p-value"))

    def pointbiserialr(self, event):
        self._statsType3(functionName = "pointbiserialr",
                         texto1 = u"X Column to analyse",
                         texto2 = u"Y Column to analyse",
                         useNumpy = True,
                         nameCols= ("Point-biserial r","two-tailed p-value"))

    def kendalltau(self, event):
        self._statsType3(functionName = "kendalltau",
                         texto1 = u"X Column to analyse",
                         texto2 = u"Y Column to analyse",
                         useNumpy = True,
                         nameCols = ("Kendall's tau"," two-tailed p-value"))

    def linregress(self, event):
        self._statsType3(functionName = "linregress",
                         texto1 = u"X Column to analyse",
                         texto2 = u"Y Column to analyse",
                         useNumpy = True,
                         nameCols= ("slope", "intercept", "r", "two-tailed prob",
                                    "sterr-of-the-estimate", "n"))

    def ttest_1samp(self, event):
        functionName = "ttest_1samp"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('Column to analyse',) )
        bt2= group('Choice',       (ColumnList,))
        bt3= group('NumTextCtrl',  ())
        bt4= group('StaticText',   ("popmean",) )

        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt3, bt4])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (colNameSelect, popmean) = values
        if len( colNameSelect ) == 0:
            self.logPanel.write("you don't select any items")
            return
        values = [ [pos for pos, value in enumerate( ColumnList )
                    if value == val
                    ][0]
                   for val in colNameSelect
                   ]

        # -------------------
        columns = [ GetData(colnums[ pos ]) for pos in values][0]
        # se hace los calculos para cada columna
        result = getattr(stats, functionName)( columns, popmean)
        # se muestra los resultados
        colNameSelect = ['t','prob']
        output.addColData(colNameSelect, functionName)
        output.addColData(result)
        self.logPanel.write(functionName + ' successfull')


    def ttest_ind(self, event):
        functionName = "ttest_ind"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('X Column to analyse',) )
        bt2= group('Choice',       (ColumnList,))
        bt3= group('StaticText',   ('Y Column to analyse',) )

        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt2, bt3])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (xcolNameSelect, ycolNameSelect) = values
        if len( xcolNameSelect ) == 0 or len( ycolNameSelect ) == 0:
            self.logPanel.write("you don't select any items")
            return
        xvalues = [ [pos for pos, value in enumerate( ColumnList )
                     if value == val
                     ][0]
                    for val in xcolNameSelect
                    ]
        yvalues = [ [pos for pos, value in enumerate( ColumnList )
                     if value == val
                     ][0]
                    for val in ycolNameSelect
                    ]

        # -------------------
        xcolumns = [ GetData(colnums[ pos ]) for pos in xvalues][0]
        ycolumns = [ GetData(colnums[ pos ]) for pos in yvalues][0]
        # se hace los calculos para cada columna
        result = getattr(stats, functionName)( xcolumns, ycolumns)
        # se muestra los resultados
        colNameSelect = ['t','prob']
        output.addColData(colNameSelect, functionName)
        output.addColData(result)
        self.logPanel.write(functionName + ' successfull')


    def ttest_rel(self, event):
        functionName = "ttest_rel"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('X Column to analyse',) )
        bt2= group('Choice',       (ColumnList,))
        bt3= group('StaticText',   ('Y Column to analyse',) )

        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt2, bt3])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (xcolNameSelect, ycolNameSelect) = values
        if len( xcolNameSelect ) == 0 or len( ycolNameSelect ) == 0:
            self.logPanel.write("you don't select any items")
            return
        xvalues = [ [pos for pos, value in enumerate( ColumnList )
                     if value == val
                     ][0]
                    for val in xcolNameSelect
                    ]
        yvalues = [ [pos for pos, value in enumerate( ColumnList )
                     if value == val
                     ][0]
                    for val in ycolNameSelect
                    ]

        # -------------------
        xcolumns = [ GetData(colnums[ pos ]) for pos in xvalues][0]
        ycolumns = [ GetData(colnums[ pos ]) for pos in yvalues][0]
        # se hace los calculos para cada columna
        result = getattr(stats, functionName)( xcolumns, ycolumns)
        # se muestra los resultados
        colNameSelect = ['t','prob']
        output.addColData(colNameSelect, functionName)
        output.addColData(result)
        self.logPanel.write(functionName + ' successfull')



    def chisquare(self, event):
        functionName = "ttest_rel"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('obs',) )
        bt2= group('Choice',       (ColumnList,))
        bt3= group('StaticText',   ('frecuences',) )

        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt2, bt3])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (xcolNameSelect, ycolNameSelect) = values
        if len( xcolNameSelect ) == 0 :
            self.logPanel.write("you don't select any items")
            return
        xvalues = [ [pos for pos, value in enumerate( ColumnList )
                     if value == val
                     ][0]
                    for val in xcolNameSelect
                    ]
        xcolumns = [ GetData(colnums[ pos ]) for pos in xvalues][0]

        if len( ycolNameSelect ) == 0:
            ycolumns = None
        else:
            yvalues = [ [pos for pos, value in enumerate( ColumnList )
                         if value == val
                         ][0]
                        for val in ycolNameSelect
                        ]
            ycolumns = [ GetData(colnums[ pos ]) for pos in yvalues][0]

        # -------------------
        # se hace los calculos para cada columna
        result = getattr(stats, functionName)( xcolumns, ycolumns)
        # se muestra los resultados
        colNameSelect = [ 'chisq', 'chisqprob(chisq, k-1)']
        output.addColData(colNameSelect, functionName)
        output.addColData(result)
        self.logPanel.write(functionName + ' successfull')



    def ks_2samp(self, event):
        functionName = "ks_2samp"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('X Column to analyse',) )
        bt2= group('Choice',       (ColumnList,))
        bt3= group('StaticText',   ('Y Column to analyse',) )

        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt2, bt3])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (xcolNameSelect, ycolNameSelect) = values
        if len( xcolNameSelect ) == 0 or len( ycolNameSelect ) == 0:
            self.logPanel.write("you don't select any items")
            return
        xvalues = [ [pos for pos, value in enumerate( ColumnList )
                     if value == val
                     ][0]
                    for val in xcolNameSelect
                    ]
        yvalues = [ [pos for pos, value in enumerate( ColumnList )
                     if value == val
                     ][0]
                    for val in ycolNameSelect
                    ]

        # -------------------
        xcolumns = [ GetData(colnums[ pos ]) for pos in xvalues][0]
        ycolumns = [ GetData(colnums[ pos ]) for pos in yvalues][0]
        # se hace los calculos para cada columna
        result = getattr(stats, functionName)( xcolumns, ycolumns)
        # se muestra los resultados
        colNameSelect = ['t','prob']
        output.addColData(colNameSelect, functionName)
        output.addColData(result)
        self.logPanel.write(functionName + ' successfull')

    def mannwhitneyu(self, event):
        functionName = "mannwhitneyu"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('X Column to analyse',) )
        bt2= group('Choice',       (ColumnList,))
        bt3= group('StaticText',   ('Y Column to analyse',) )

        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt2, bt3])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (xcolNameSelect, ycolNameSelect) = values
        if len( xcolNameSelect ) == 0 or len( ycolNameSelect ) == 0:
            self.logPanel.write("you don't select any items")
            return
        xvalues = [ [pos for pos, value in enumerate( ColumnList )
                     if value == val
                     ][0]
                    for val in xcolNameSelect
                    ]
        yvalues = [ [pos for pos, value in enumerate( ColumnList )
                     if value == val
                     ][0]
                    for val in ycolNameSelect
                    ]

        # -------------------
        xcolumns = [ GetData(colnums[ pos ]) for pos in xvalues][0]
        ycolumns = [ GetData(colnums[ pos ]) for pos in yvalues][0]
        # se hace los calculos para cada columna
        result = getattr(stats, functionName)( xcolumns, ycolumns)
        # se muestra los resultados
        colNameSelect = ['t','prob']
        output.addColData(colNameSelect, functionName)
        output.addColData(result)
        self.logPanel.write(functionName + ' successfull')

    def ranksums(self, event):
        functionName = "ranksums"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('X Column to analyse',) )
        bt2= group('Choice',       (ColumnList,))
        bt3= group('StaticText',   ('Y Column to analyse',) )

        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt2, bt3])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (xcolNameSelect, ycolNameSelect) = values
        if len( xcolNameSelect ) == 0 or len( ycolNameSelect ) == 0:
            self.logPanel.write("you don't select any items")
            return
        xvalues = [ [pos for pos, value in enumerate( ColumnList )
                     if value == val
                     ][0]
                    for val in xcolNameSelect
                    ]
        yvalues = [ [pos for pos, value in enumerate( ColumnList )
                     if value == val
                     ][0]
                    for val in ycolNameSelect
                    ]

        # -------------------
        xcolumns = [ GetData(colnums[ pos ]) for pos in xvalues][0]
        ycolumns = [ GetData(colnums[ pos ]) for pos in yvalues][0]
        # se hace los calculos para cada columna
        result = getattr(stats, functionName)( xcolumns, ycolumns)
        # se muestra los resultados
        colNameSelect = ['t','prob']
        output.addColData(colNameSelect, functionName)
        output.addColData(result)
        self.logPanel.write(functionName + ' successfull')

    def wilcoxont(self, event):
        functionName = "wilcoxont"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('X Column to analyse',) )
        bt2= group('Choice',       (ColumnList,))
        bt3= group('StaticText',   ('Y Column to analyse',) )

        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt2, bt3])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (xcolNameSelect, ycolNameSelect) = values
        if len( xcolNameSelect ) == 0 or len( ycolNameSelect ) == 0:
            self.logPanel.write("you don't select any items")
            return
        xvalues = [ [pos for pos, value in enumerate( ColumnList )
                     if value == val
                     ][0]
                    for val in xcolNameSelect
                    ]
        yvalues = [ [pos for pos, value in enumerate( ColumnList )
                     if value == val
                     ][0]
                    for val in ycolNameSelect
                    ]

        # -------------------
        xcolumns = [ GetData(colnums[ pos ]) for pos in xvalues][0]
        ycolumns = [ GetData(colnums[ pos ]) for pos in yvalues][0]
        # se hace los calculos para cada columna
        result = getattr(stats, functionName)( xcolumns, ycolumns)
        # se muestra los resultados
        colNameSelect = ['t','prob']
        output.addColData(colNameSelect, functionName)
        output.addColData(result)
        self.logPanel.write(functionName + ' successfull')

    def kruskalwallish(self, event):
        self._statsType1(functionName = "kruskalwallish",
                         useNumpy = True,
                         allColsOneCalc = True,
                         nameResults= ('H-statistic (corrected for ties)', 'p-value'))


    def friedmanchisquare(self, event):
        self._statsType1(functionName = "friedmanchisquare",
                         useNumpy = True,
                         allColsOneCalc = True,
                         nameResults= ('chi-square statistic', 'p-value'),
                         dataSquare= True)

    def chisqprob(self, event):
        self._statsType2(functionName= "chisqprob",
                         texto = 'dregrees of fredom',
                         spinData= (1,100,1),
                         factor = 1,
                         useNumpy = True)

    def erfcc(self, event):
        functionName = "erfcc"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('X value',) )
        bt2= group('NumTextCtrl',  ())

        structure = list()
        structure.append([bt2, bt1])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (xvalue,) = values
        if xvalue == None:
            self.logPanel.write("you don?t enter a valid value")
            return

        # se hace los calculos
        result = getattr(stats, functionName)( xvalue)
        # se muestra los resultados
        colNameSelect = ['x', 'erfc(x)']
        output.addColData(colNameSelect, functionName)
        output.addColData([xvalue ,result])
        self.logPanel.write(functionName + ' successfull')



    def zprob(self, event):
        functionName = "zprob"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('Z value',) )
        bt2= group('NumTextCtrl',  ())
        structure = list()
        structure.append([bt2, bt1])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (xvalue,) = values
        if xvalue == None:
            self.logPanel.write("you don?t enter a valid value")
            return

        # se hace los calculos
        result = getattr(stats, functionName)( xvalue)
        # se muestra los resultados
        colNameSelect = ['x', 'erfc(x)']
        output.addColData(colNameSelect, functionName)
        output.addColData([xvalue ,result])
        self.logPanel.write(functionName + ' successfull')


    #def ksprob(self, event):
    #    self.logPanel.write('ksprob')

    #def fprob(self, event):
    #    self.logPanel.write('fprob')

    def betacf(self, event):
        functionName = "betacf"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('a',) )
        bt2= group('NumTextCtrl',  ())
        bt3= group('StaticText',   ('b',) )
        bt4= group('StaticText',   ('% x',) )
        bt5= group('SpinCtrl',     (0,100,1) )
        factor = 0.01
        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt2, bt3])
        structure.append([bt5, bt4])

        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (a, b, x) = values
        x= x*factor
        if a == None or b == None:
            self.logPanel.write("you don?t enter a valid value")
            return

        # se hace los calculos
        result = getattr(stats, functionName)(a, b, x)
        # se muestra los resultados
        colNameSelect = ['a', 'b','x','betacf(a,b,x)']
        output.addColData(colNameSelect, functionName)
        output.addColData([a, b, x, result])
        self.logPanel.write(functionName + ' successfull')

    def gammln(self, event):
        functionName = "gammln"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('xx',) )
        bt2= group('NumTextCtrl',  ())
        structure = list()
        structure.append([bt2, bt1])
        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (xvalue,) = values
        if xvalue == None:
            self.logPanel.write("you don?t enter a valid value")
            return

        # se hace los calculos
        result = getattr(stats, functionName)( xvalue)
        # se muestra los resultados
        colNameSelect = ['xx', 'lgammln(xx)']
        output.addColData(colNameSelect, functionName)
        output.addColData([xvalue ,result])
        self.logPanel.write(functionName + ' successfull')

    def betai(self, event):
        functionName = "betai"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = frame.grid.GetUsedCols()

        bt1= group('StaticText',   ('a',) )
        bt2= group('NumTextCtrl',  ())
        bt3= group('StaticText',   ('b',) )
        bt4= group('StaticText',   ('% x',) )
        bt5= group('SpinCtrl',     (0,100,1) )
        factor = 0.01
        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt2, bt3])
        structure.append([bt5, bt4])

        dlg = dialog(settings = setting, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        (a, b, x) = values
        x= x*factor
        if a == None or b == None:
            self.logPanel.write("you don?t enter a valid value")
            return

        # se hace los calculos
        result = getattr(stats, functionName)(a, b, x)
        # se muestra los resultados
        colNameSelect = ['a', 'b','x','betai(a,b,x)']
        output.addColData(colNameSelect, functionName)
        output.addColData([a, b, x, result])
        self.logPanel.write(functionName + ' successfull')


    def F_oneway(self, event):
        self._statsType1("F_oneway", allColsOneCalc = True,
                         nameResults= ("F","p-value"))

    def F_value(self, event):
        self._statsType1("F_value", allColsOneCalc = True,
                         nameResults= ("F","p-value"))
#---------------------------------------------------------------------------
# Scripting API is defined here. So far, only basic (but usable!) stuff.
def GetData(column):
    """This function enables the user to extract the data from the data grid.
    The data are "clean" and ready for analysis."""
    return frame.grid.CleanData(column)
def GetDataName(column):
    """This function returns the name of the data variable - in other words,
    the column label from the grid."""
    return frame.grid.m_grid.GetColLabelValue(column)
def PutData(column, data):
    """This routine takes a list of data, and puts it into the datagrid
    starting at row 0. The grid is resized if the list is too large. This
    routine desparately needs to be updated to prevent errors"""
    n = len(data)
    if (n > frame.grid.m_grid.GetNumberRows()):
        frame.grid.m_grid.AddNCols(-1, (datawidth - gridwidth + 5))
    for i in range(n):
        frame.grid.m_grid.SetCellValue(i, column, str(data[i]))

#--------------------------------------------------------------------------
# main loop
if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None, app)
    frame.grid.SetFocus()
    Logg= frame.logPanel
    output = frame.answerPanel
    frame.ShowFullScreen(True,False)
    app.MainLoop()
# eof