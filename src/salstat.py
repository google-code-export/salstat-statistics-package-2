#!/usr/bin/env python

""" Copyright Sebastian Lopez Buritica 2012

SalStat Statistics Package. Copyright 2002 Alan James Salmoni. Licensed
under the GNU General Public License (GPL). See the file COPYING for full
details of this license. """

import wx
import os

from ntbSheet import MyGridPanel as MyGrid

from script import ScriptPanel
from imagenes import imageEmbed
import wx.html
import wx.aui
import wx.lib.agw.aui as aui
####from PanelScript import PanelPython

import wx.lib.wxpTag
# import system modules
import string, os, os.path, pickle
# import SalStat specific modules
import salstat_stats,images
import numpy, math
import wx.py
from xml.dom import minidom
# system of graphics
from plotFrame import MpltFrame as plot
from multiPlotDialog import data2Plotdiaglog, selectDialogData2plot, scatterDialog
from ntbSheet import NoteBookSheet

from openStats import statistics
import traceback
from slbTools import ReportaExcel

#---------------------------------------------------------------------------
# set up id's for menu events - all on menu, some also available elsewhere
ID_FILE_NEW = wx.ID_ANY
ID_FILE_NEWOUTPUT = wx.ID_ANY
ID_FILE_OPEN = wx.ID_ANY
ID_FILE_SAVE = wx.ID_ANY
ID_FILE_SAVEAS = wx.ID_ANY
ID_FILE_PRINT = wx.ID_ANY
ID_FILE_EXIT = wx.ID_ANY
ID_EDIT_CUT = wx.ID_ANY
ID_EDIT_COPY = wx.ID_ANY
ID_EDIT_PASTE = wx.ID_ANY
ID_EDIT_SELECTALL = wx.ID_ANY
ID_EDIT_FIND = wx.ID_ANY
ID_EDIT_DELETECOL = wx.ID_ANY
ID_EDIT_DELETEROW = wx.ID_ANY
ID_PREF_VARIABLES = wx.ID_ANY
ID_PREF_GRID = wx.ID_ANY
ID_PREF_CELLS = wx.ID_ANY
ID_PREF_FONTS = wx.ID_ANY
ID_PREPARATION_DESCRIPTIVES = wx.ID_ANY
ID_PREPARATION_TRANSFORM = wx.ID_ANY
ID_PREPARATION_OUTLIERS = wx.ID_ANY
ID_PREPARATION_NORMALITY = wx.ID_ANY
ID_TRANSFORM_SQUAREROOT = wx.ID_ANY
ID_TRANSFORM_SQUARE = wx.ID_ANY
ID_TRANSFORM_INVERSE = wx.ID_ANY
ID_TRANSFORM_OTHER = wx.ID_ANY
ID_ANALYSE_1COND = wx.ID_ANY
ID_ANALYSE_2COND = wx.ID_ANY
ID_ANALYSE_3COND = wx.ID_ANY
ID_ANALYSE_CORRELATION = wx.ID_ANY
ID_ANALYSE_2FACT = wx.ID_ANY
ID_ANALYSE_SCRIPT = wx.ID_ANY
ID_ANALYSE2_1COND = wx.ID_ANY
ID_ANALYSE2_2COND = wx.ID_ANY
ID_ANALYSE2_3COND = wx.ID_ANY
ID_ANALYSE2_1_TTEST = wx.ID_ANY
ID_ANALYSE2_1_SIGN = wx.ID_ANY
ID_CHART = wx.ID_ANY
ID_CHART_DRAW = wx.ID_ANY
ID_BARCHART_DRAW = wx.ID_ANY
ID_HELP_WIZARD = wx.ID_ANY
ID_HELP_TOPICS = wx.ID_ANY
ID_HELP_SCRIPTING = wx.ID_ANY
ID_HELP_LICENCE = wx.ID_ANY
ID_HELP_ABOUT = wx.ID_ANY
ID_OFILE_NEW = wx.ID_ANY
ID_OFILE_OPEN = wx.ID_ANY
ID_OFILE_SAVE = wx.ID_ANY
ID_OFILE_SAVEAS = wx.ID_ANY
ID_OFILE_PRINT = wx.ID_ANY
ID_OFILE_CLOSE = wx.ID_ANY
ID_OEDIT_CUT = wx.ID_ANY
ID_OEDIT_COPY = wx.ID_ANY
ID_OEDIT_PASTE = wx.ID_ANY
ID_OEDIT_SELECTALL = wx.ID_ANY
ID_OPREF_FONT = wx.ID_ANY
ID_FILE_GSAVEAS = wx.ID_ANY
ID_FILE_GPRINTSETUP = wx.ID_ANY
ID_FILE_GPRINTPREVIEW = wx.ID_ANY
ID_FILE_GPRINT = wx.ID_ANY
ID_FILE_GCLOSE = wx.ID_ANY
ID_TITLE_GYAXIS = wx.ID_ANY
ID_TITLE_GXAXIS = wx.ID_ANY
ID_TITLE_GTITLE = wx.ID_ANY
ID_TITLE_LEGEND = wx.ID_ANY
ID_TITLE_GRID = wx.ID_ANY

DescList=['N','Sum','Mean','missing',
          'Variance','Standard Deviation','Standard Error',
          'Sum of Squares',#'Sum of Squared Devs', 
          'Coefficient of Variation','Minimum',   
          'Maximum','Range','Number Missing',     
          'Geometric Mean','Harmonic Mean',       
          'Skewness','Kurtosis', 'Median',        #'Median Absolute Deviation',
          'Mode', 'Interquartile Range'] #, 'Number of Unique Levels']

HypList = ['One tailed','Two tailed']
inits={}    # dictionary to hold the config values
ColsUsed = []
RowsUsed = []
missingvalue = -99.999
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
        saveButton = wx.Button(self, 331, "Save...", size=(BWidth, BHeight))
        discardButton = wx.Button(self, 332, "Discard", size=(BWidth, BHeight))
        CancelButton = wx.Button(self, 333, "Cancel", size=(BWidth, BHeight))
        hbox.Add(saveButton, 0, wx.ALL, 5)
        hbox.Add(discardButton, 0, wx.ALL, 5)
        hbox.Add(CancelButton, 0, wx.ALL, 5)
        vbox.Add(hbox,1)
        self.SetAutoLayout(True)
        self.SetSizer(vbox)
        self.Layout()
        self.Bind(wx.EVT_BUTTON, self.SaveData, id = 331)
        self.Bind(wx.EVT_BUTTON, self.DiscardData, id = 332)
        self.Bind(wx.EVT_BUTTON, self.CancelDialog, id = 333)

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
# creates an init file in the home directory of the user
class GetInits:
    """This class deals with a users init file. The coords and sizes of the
    various widgets are kept here, and are stored throughout the program
    as a dictionary for easy access. When the program starts, the home
    directory is checked for the init files existence. If absent, it is
    created with a series of default values. If it is present, the values are
    read into the dictionary in a slightly roundabout way! I am sure that
    there is a more "Python" way of doing this, but this way works for now"""
    def __init__(self):
        self.initfile = os.path.join(INITDIR, '.salstatrc')
        if os.path.isfile(self.initfile):
            self.ReadInitFile(self.initfile)
        else:
            self.CreateInitFile(self.initfile)

    def ReadInitFile(self, initfilename):
        inits.clear()
        fin = file(initfilename, 'r')
        for i in range(28):
            a = fin.readline()
            a = string.split(a)
            tmpdict = {a[0]:a[1]}
            inits.update(tmpdict)

    def CreateInitFile(self, initfilename):
        inits = {
            'gridsizex': '600',
            'gridsizey': '420',
            'gridposx': '50',
            'gridposy': '20',
            'gridcellsx': '20',
            'gridcellsy': '80',
            'outputsizex': '500',
            'outputsizey': '400',
            'outputposx': '20',
            'outputposy': '50',
            'scriptsizex': '600',
            'scriptsizey': '400',
            'scriptposx': '35',
            'scriptposy': '35',
            'chartsizex': '600',
            'chartsizey': '400',
            'chartposx': '50',
            'chartposy': '50',
            'helpsizex': '600',
            'helpsizey': '400',
            'helpposx': '40',
            'helpposy': '40',
            'lastfile1': "...",
            'lastfile2': "...",
            'lastfile3': "...",
            'lastfile4': "...",
            'opendir': DOCDIR,
            'savedir': DOCDIR
        }
        initskeys = inits.keys()
        initsvalues = inits.values()
        fout = file(initfilename,'w')
        for i in range(len(initskeys)):
            fout.write(str(initskeys[i])+' '+str(initsvalues[i])+'\n')
        fout.close()
        self.ReadInitFile(initfilename) # damn hack!

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
    def __init__(self, parent, log, size= (500,50)):
        self.NumSheetReport = 0
        self.log = log
        self.path = None
        MyGrid.__init__(self, parent, -1, size)
        self.Saved = True
        self.moveTo = None
        ##self.m_grid.SetGridLineColour(wx.Color(0,0,0))
        #self.m_grid.CreateGrid(int(inits.get("gridcellsy")), \
        #                            int(inits.get("gridcellsx")))

        self.m_grid.setPadreCallBack(self)
        self.m_grid.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        for i in range(20):
            self.m_grid.SetColFormatFloat(i, 8, 4)
        # self.m_grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.AlterSaveStatus)
        self.m_grid.Bind(wx.grid.EVT_GRID_CMD_LABEL_RIGHT_DCLICK, self.RangeSelected)
        self.m_grid.wildcard = "Any File (*.*)|*.*|" \
            "ASCII data format (*.dat)|*.dat|" \
            "SalStat Format (*.xml)|*.xml"
        # se ajusta el render
        attr = wx.grid.GridCellAttr()
        editor = wx.grid.GridCellFloatEditor()
        attr.SetEditor(editor)
        renderer = wx.grid.GridCellFloatRenderer(0, 5)
        attr.SetRenderer(renderer)

    def RangeSelected(self, event):
        if event.Selecting():
            self.tl = event.GetTopLeftCoords()
            self.br = event.GetBottomRightCoords()

    def OnRangeChange(self, event): #AlterSaveStatus
        # this is activated when the user enters some data
        self.Saved = False
        # also record in the history file
        col = self.m_grid.GetGridCursorCol()
        row = self.m_grid.GetGridCursorRow()
        value = self.m_grid.GetCellValue(row, col)
        xmlevt = '<data row="'+str(row)+'" col="'+str(col)+'">'+str(value)+'</data>\n'

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
        xmlevt = '<deleteRow>'+str(currentrow)+'</deleteRow>\n'
       

    def SelectAllCells(self, event):
        self.m_grid.SelectAll()

    # adds columns and rows to the grid
    def AddNCells(self, numcols, numrows):
        insert = self.m_grid.AppendCols(numcols)
        insert = self.m_grid.AppendRows(numrows)
        for i in range(self.m_grid.GetNumberCols() - numcols):
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
            rows = self.GetUsedRows()
            cols= self.GetUsedCols()[1]
            self.reportObj.writeByCols(self.m_grid.getByColumns(), self.NumSheetReport)
        self.reportObj.save()
        self.Saved = True
        self.log.write("the fil %s was succesfully saved"%self.reportObj.path)
    def LoadDataASCII(self, event):
        dlg = wx.FileDialog(self, "Load Data File", "","",
                            wildcard= "SalStat Native (*.xml)|*.xml",
                            style = wx.OPEN)
                #, wx.OPEN)
        icon = images.getIconIcon()
        dlg.SetIcon(icon)
        if dlg.ShowModal() == wx.ID_OK: # ShowModal
            filename = dlg.GetPath()
            if filename[-3:] == 'xml':
                self.LoadNativeXML(filename)
            else:
                inits.update({'opendir': dlg.GetDirectory()})
                self.ClearGrid()
                # exception handler here!
                try:
                    fin = open(filename, "r")
                except IOError:
                    pass # what to do if they filename isn't visible? Messagebox?
                gridline = 0
                self.Freeze()
                for i in fin.readlines():
                    words = string.split(i)
                    if len(words) > self.GetNumberCols():
                        NumberCols = len(words) - self.GetNumberCols() + 10
                        self.AddNCells(NumberCols, 0)
                    for j in range(len(words)):
                        self.SetCellValue(gridline, j, words[j])
                    gridline = gridline + 1
                    if (gridline == self.GetNumberRows()):
                        self.AddNCells(0,10)
                fin.close()
                self.Thaw()
            self.ForceRefresh()

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

    def LoadNativeXML(self, filename):
        # also get rid of the old history
        if os.path.isfile(filename) == 0:
            pass
        else:
            # now start the XML processing
            self.ClearGrid()
            self.Freeze()
            xmldoc = minidom.parse(filename)
            datatags = xmldoc.getElementsByTagName('data')
            self.getData(datatags)
            deleteRowTags = xmldoc.getElementsByTagName('deleteRow')
            for i in range(len(deleteRowTags)):
                rownum = int(self.getText(deleteRowTags[i].childNodes))
                self.DeleteRows(rownum, 1)
            deleteColTags = xmldoc.getElementsByTagName('deleteColumn')
            for i in range(len(deleteColTags)):
                colnum = int(self.getText(deleteColTags[i].childNodes))
                self.DeleteCols(colnum, 1)
            appendRowTags = xmldoc.getElementsByTagName('appendRow')
            for i in range(len(appendRowTags)):
                rownum = int(self.getText(appendRowTags[i].childNodes))
                self.AppendRows()
            appendColTags = xmldoc.getElementsByTagName('appendColumn')
            for i in range(len(appendColTags)):
                colnum = int(self.getText(appendRowTags[i].childNodes))
                self.AppendCols()
            deleteColTags = xmldoc.getElementsByTagName('deleteColumn')
            for i in range(len(deleteColTags)):
                colnum = int(self.getText(deleteColTags[i].childNodes))
                self.DeleteCurrentCol(colnum)
            deleteRowTags = xmldoc.getElementsByTagName('deleteRow')
            for i in range(len(deleteRowTags)):
                rownum = int(self.getText(deleteRowTags[i].childNodes))
                self.DeleteCurrentRow(rownum)
            # there is a problem here - the html tags embedded between the <results> tags
            # are parsed as XML, but I want the whole lot available as a string.
            output.htmlpage.SetPage('<P><B>SalStat Statistics</B></P>')
            output.htmlpage.WholeOutString = ''
            resultsTags = xmldoc.getElementsByTagName('results')
            for i in range(len(resultsTags)):
                outputText = self.getText(resultsTags[i].childNodes)
                print "out" + outputText # debugging!
                output.htmlpage.Addhtml(outputText)
            #describeTags = xmldoc.getElementsByTagName('describe')
            #for i in range(len(describeTags)):
            self.Thaw()

    def LoadDataASCII2(self, event):
        # redundant routine
        default = inits.get('opendir')
        dlg = wx.FileDialog(self, "Load Data File", default,"",\
                            "ASCII Text (*.dat)|*.dat",wx.OPEN)
                #numpy Array (*.npy)|*.npy|", wx.OPEN)
        icon = images.getIconIcon()
        dlg.SetIcon(icon)
        if dlg.ShowModal() == wx.ID_OK:
            inits.update({'opendir': dlg.GetDirectory()})
            filename = dlg.GetPath()
            self.ClearGrid()
            # exception handler here!
            fin = open(filename, "r")
            #if filename[-3:] == 'dat':
            if 1:
                # text data file
                # size the datafile first
                dataheight = 0
                line = fin.readline()
                words = string.split(line)
                datawidth = len(words)
                while 1:
                    try:
                        line = fin.readline()
                    except:
                        pass
                    if (line == ''):
                        break
                    dataheight = dataheight + 1
                gridwidth = self.GetNumberCols()
                gridheight = self.GetNumberRows()
                if (datawidth > gridwidth):
                    self.AddNCols(-1, (datawidth - gridwidth + 5))
                if (dataheight > gridheight):
                    self.AddNRows(-1, (dataheight -  gridheight + 5))
                fin.close
                fin = open(filename, "r")
                currentrow = 0
                for i in range(dataheight):
                    line = fin.readline()
                    if (line == ''):
                        break
                    line = string.replace(line, ',', ' ')
                    words = string.split(line)
                    for i in range(len(words)):
                        self.SetCellValue(currentrow, i, words[i])
                    currentrow = currentrow + 1
            elif filename[-3:] == 'npy':
                p = pickle.Unpickler(fin)
                dataset = p.load()
                # put dataset into grid
            fin.close()
            self.ForceRefresh()

    def LoadNumericData(self, event):
        default = inits.get('opendir')
        dlg = wx.FileDialog(self, "Load Data File", default,"","*.\
                                    dat|*.*", wx.OPEN)
        icon = images.getIconIcon()
        dlg.SetIcon(icon)
        if dlg.ShowModal() == wx.ID_OK:
            inits.update({'opendir': dlg.GetDirectory()})
            filename = dlg.GetPath()
            self.ClearGrid()
            # exception handler here!
            fin = open(filename, "r")
            p = pickle.Unpickler(fin)
            dataset = p.load()
            fin.close()
            # put dataset into grid

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
        okaybutton = wx.Button(self, 421, "Okay", wx.Point(10, 90),\
                               wx.Size(BWidth, BHeight))
        cancelbutton = wx.Button(self, 422, "Cancel", wx.Point(110,90), \
                                 wx.Size(BWidth, BHeight))
        self.Bind(wx.EVT_BUTTON, self.OkayButtonPressed, id = 421)
        self.Bind(wx.EVT_BUTTON, self.CancelButtonPressed, id= 422)

    def OkayButtonPressed(self, event):
        colswanted = self.numnewcols.GetValue()
        rowswanted = self.numnewRows.GetValue()
        frame.grid.AddNCells(colswanted, rowswanted)
        self.Close(True)

    def CancelButtonPressed(self, event):
        self.Close(True)

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
# output window w/html class for output. Also has status bar and menu.Opens
# in new frame
class OutputSheet(wx.Frame):
    def __init__(self, parent, id):
        posx = int(inits.get('outputposx'))
        posy = int(inits.get('outputposy'))
        wx.Frame.__init__(self, parent, -1, "SalStat Statistics - Output", \
                          size=wx.DefaultSize )#pos=(posx, posy))
        #set icon for frame (needs x-platform separator!
        icon = images.getIconIcon()
        self.SetIcon(icon)
        file_menu = wx.Menu()
        edit_menu = wx.Menu()
        pref_menu = wx.Menu()
        help_menu = wx.Menu()
        self.bt1 = file_menu.Append(ID_FILE_NEW, '&New')
        self.bt2 = file_menu.Append(ID_OFILE_OPEN, '&Open...')
        self.bt3 = file_menu.Append(ID_OFILE_SAVE, '&Save')
        self.bt4 = file_menu.Append(ID_OFILE_SAVEAS, 'Save &As...')
        self.bt5 = file_menu.Append(ID_OFILE_PRINT, '&Print...')
        self.bt6 = file_menu.Append(ID_OFILE_CLOSE, '&Close')
        self.bt7 = edit_menu.Append(ID_OEDIT_CUT, 'Cu&t')
        self.bt8 = edit_menu.Append(ID_OEDIT_COPY, '&Copy')
        self.bt9 = edit_menu.Append(ID_OEDIT_PASTE, '&Paste')
        self.bt10 = edit_menu.Append(ID_OEDIT_SELECTALL, 'Select &All')
        self.bt11 = help_menu.Append(ID_HELP_WIZARD, '&What Test Should I Use...')
        self.bt12 = help_menu.Append(ID_HELP_TOPICS, '&Topics...')
        self.bt13 = help_menu.Append(ID_HELP_LICENCE, '&Licence...')
        self.bt14 = help_menu.Append(ID_HELP_ABOUT, '&About...')
        omenuBar = wx.MenuBar()
        omenuBar.Append(file_menu, '&File')
        omenuBar.Append(edit_menu, '&Edit')
        omenuBar.Append(pref_menu, '&Pref')
        omenuBar.Append(help_menu, '&Help')
        self.SetMenuBar(omenuBar)
        #wxInitAllImageHandlers()
        NewIcon = images.getNewBitmap()
        OpenIcon = images.getOpenBitmap()
        SaveAsIcon = images.getSaveAsBitmap()
        PrintIcon = images.getPrintBitmap()
        HelpIcon = images.getHelpBitmap()
        toolBar = self.CreateToolBar(wx.TB_HORZ_LAYOUT| \
                                     wx.TB_3DBUTTONS)
        self.bt15 = toolBar.AddSimpleTool(wx.ID_ANY, NewIcon,"New","New Data Sheet in \
                                    separate window")
        self.bt16 = toolBar.AddSimpleTool(wx.ID_ANY, OpenIcon,"Open","Open Data from a File")
        self.bt17 = toolBar.AddSimpleTool(wx.ID_ANY, SaveAsIcon,"Save As","Save Data under \
                                    a new filename")
        self.bt18 = toolBar.AddSimpleTool(wx.ID_ANY, PrintIcon,"Print","Print Out Results")
        self.bt19 = toolBar.AddSimpleTool(wx.ID_ANY, HelpIcon, "Help", "Get some help!")
        toolBar.SetToolBitmapSize((24,24))
        # more toolbuttons are needed: New Output, Save, Print, Cut, \
        # Variables, and Wizard creates the toolbar
        toolBar.Realize()
        self.SetToolBar(toolBar)
        self.CreateStatusBar()
        self.SetStatusText('SalStat Statistics')
        self.htmlpage = MyHtmlWindow(self, -1)
        self.htmlpage.Addhtml('<P><B>SalStat Statistics</B></P>')
        self.printer = wx.html
        self.Bind(wx.EVT_MENU, self.htmlpage.SaveHtmlPage, id = ID_FILE_SAVEAS)

        self.Bind(wx.EVT_MENU, self.ClearAll, id = self.bt1.GetId() )
        self.Bind(wx.EVT_MENU, self.PrintOutput, id = self.bt5.GetId())
        self.Bind(wx.EVT_MENU,  self.htmlpage.LoadHtmlPage, id = self.bt2.GetId())
        self.Bind(wx.EVT_MENU, frame.GoHelpAboutFrame, id = self.bt14.GetId())
        self.Bind(wx.EVT_MENU, frame.GoHelpWizardFrame, id =  self.bt11.GetId())
        self.Bind(wx.EVT_MENU, frame.GoHelpTopicsFrame, id = self.bt12.GetId())
        self.Bind(wx.EVT_MENU, frame.GoHelpLicenceFrame, id  = self.bt13.GetId())

        self.Bind(wx.EVT_MENU, self.ClearAll,  id = self.bt15.GetId())
        self.Bind(wx.EVT_MENU, self.htmlpage.LoadHtmlPage, id = self.bt16.GetId())
        self.Bind(wx.EVT_MENU, self.htmlpage.SaveHtmlPage, id = self.bt17.GetId())
        self.Bind(wx.EVT_MENU, self.PrintOutput, id = self.bt18.GetId())
        self.Bind(wx.EVT_MENU,  frame.GoHelpTopicsFrame, id= self.bt19.GetId())
        self.Bind(wx.EVT_CLOSE, self.DoNothing, self)

    def PrintOutput(self, event):
        data = wx.PrintDialogData()
        data.EnablePrintToFile(True)
        data.EnablePageNumbers(True)
        data.EnableSelection(True)
        dlg = wx.PrintDialog(output, data)
        if dlg.ShowModal() == wx.ID_OK:
            #print out html
            self.printer.PrintText(self.htmlpage.WholeOutString)
        dlg.Destroy()

    def DoNothing(self, event):
        pass

    def ClearAll(self, event):
        # check output has been saved
        self.htmlpage.SetPage('<P><B>SalStat Statistics</B></P>')
        self.htmlpage.WholeOutString = ''

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
                #descs.append(salstat_stats.FullDescriptives( \
                #    frame.grid.CleanData(realColi), name, \
                #    frame.grid.missing))
        ManyDescriptives(self, descs)
        self.Close(True)

    def OnCloseContDesc(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# Same as DescriptivesContinuousFrame, but for nominal descriptives
class OneConditionTestFrame(wx.Dialog):
    def __init__( self, parent, id, ColumnList ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = "One Condition Tests",
                             pos = wx.DefaultPosition, size = wx.Size( 500,400+wind ),
                             style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        icon = images.getIconIcon()
        self.SetIcon(icon)
        ColumnList, self.colnums = frame.grid.GetUsedCols()

        m_checkList5Choices = DescList
        # self.ColBox = wx.Choice(self, 101,(10,30), (110,20), choices = ColumnList)
        self.DescChoice = DescChoiceBox( self, wx.ID_ANY )

        self.m_mgr.AddPane( self.DescChoice, wx.aui.AuiPaneInfo().Center().
                            Caption(u"Select Descriptive Statistics").CaptionVisible(True).
                            CloseButton(False).
                            PaneBorder(False).Dock().Resizable().FloatingSize(wx.DefaultSize).
                            DockFixed(False).BottomDockable(False).TopDockable(False).
                            Row(0).Layer(0))

        Tests = ['t-test','Sign test','Chi square test for variance']
        m_checkList6Choices = Tests
        self.TestChoice= wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition,
                                          wx.DefaultSize, m_checkList6Choices, 0 )
        self.m_mgr.AddPane( self.TestChoice, wx.aui.AuiPaneInfo() .Center() .
                            Caption( u"Select the kind of Test" ).CloseButton( False ).
                            PaneBorder( False ).Dock().Resizable().FloatingSize( wx.Size( 161,93 ) ).
                            DockFixed( False ).BottomDockable( False ).TopDockable( False ).
                            Row( 1 ).Layer( 0 ) )

        self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel2, wx.aui.AuiPaneInfo().Left().CaptionVisible( False ).
                            CloseButton( False ).PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ).Row( 1 ).CentrePane() )

        bSizer21 = wx.BoxSizer( wx.VERTICAL )

        sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel2, wx.ID_ANY, u"Columna para analizar" ), wx.VERTICAL )

        m_comboBox1Choices = ColumnList
        self.DescList2 = wx.ComboBox( self.m_panel2, wx.ID_ANY, m_comboBox1Choices[0],
                                      wx.DefaultPosition, wx.DefaultSize, m_comboBox1Choices, 0 )
        if len(ColumnList) > 0 :
            self.DescList2.SetSelection(0)

        sbSizer1.Add( self.DescList2, 0, wx.ALL|wx.EXPAND, 5 )

        bSizer21.Add( sbSizer1, 1, wx.EXPAND, 5 )

        sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel2, wx.ID_ANY, u"Seleccione Hypotesis" ), wx.HORIZONTAL )
        self.m_radioBtn1 = wx.RadioButton( self.m_panel2, wx.ID_ANY, u"One Tailed", wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer2.Add( self.m_radioBtn1, 0, wx.ALL, 5 )

        self.m_radioBtn2 = wx.RadioButton( self.m_panel2, wx.ID_ANY, u"Two Tailed", wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer2.Add( self.m_radioBtn2, 0, wx.ALL, 5 )
        bSizer21.Add( sbSizer2, 1, wx.EXPAND, 5 )
        sbSizer4 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel2, wx.ID_ANY, u"User hypotesis test" ), wx.VERTICAL )

        self.UserMean = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer4.Add( self.UserMean, 0, wx.ALL|wx.EXPAND, 5 )
        bSizer21.Add( sbSizer4, 1, wx.EXPAND, 5 )
        self.m_panel2.SetSizer( bSizer21 )
        self.m_panel2.Layout()
        bSizer21.Fit( self.m_panel2 )
        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )

        self.m_mgr.AddPane( self.m_panel1, wx.aui.AuiPaneInfo() .Bottom() .CaptionVisible( False ).
                            CloseButton( False ).PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ).LeftDockable( False ).
                            RightDockable( False ).MinSize( wx.Size( -1,30 ) ) )
        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.okaybutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.okaybutton.Enable(False)
        bSizer2.Add( self.okaybutton, 0, wx.ALL, 5 )

        self.cancelbutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.cancelbutton, 0, wx.ALL, 5 )

        self.allbutton= wx.Button( self.m_panel1, wx.ID_ANY, u"Select All", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.allbutton, 0, wx.ALL, 5 )

        self.nonebutton  = wx.Button( self.m_panel1, wx.ID_ANY, u"Select None", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.nonebutton, 0, wx.ALL, 5 )


        self.m_panel1.SetSizer( bSizer2 )
        self.m_panel1.Layout()
        bSizer2.Fit( self.m_panel1 )

        self.m_radioBtn1.SetValue(True)
        self.m_mgr.Update()
        self.Centre( wx.BOTH )

        self.Bind(wx.EVT_BUTTON, self.OnOkayButton, id = self.okaybutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCloseOneCond, id = self.cancelbutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.DescChoice.SelectAllDescriptives, id = self.allbutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.DescChoice.SelectNoDescriptives, id = self.nonebutton.GetId())
        self.UserMean.Bind( wx.EVT_TEXT, self.usermeanControl )

    def usermeanControl( self, event ):
        allowValues= [u'0',u'1',u'2',u'3',u'4',u'5',u'6',u'7',u'8',u'9',u'.']
        resultado = [val for val in self.UserMean.GetValue() if val in allowValues]
        newres = u""
        for val in resultado:
            newres+= val
        if self.UserMean.GetValue() != newres:
            self.UserMean.SetValue(newres)
        if len(newres) > 0 :
            # se habilita el control ok para calcular
            self.okaybutton.Enable(True)
        else:
            self.okaybutton.Enable(False)
        event.Skip()

    def EnteredText(self, event):
        self.okaybutton.Enable(True)

    def OnOkayButton(self, event):
        x1 = self.DescList2.GetSelection()
        if (x1 < 0): # add top limits of grid to this
            self.Close(True)
            return
        try:
            umean = float(self.UserMean.GetValue())
        except:
            data= {'name': 'One condition Tests','size':(1,1),'nameCol':'Error',
                   'data':[('Cannot do test \n No user hypothesised mean specified',),]}
            output.addPage(data)
            self.Close(True)
            return
        realColx1 = self.colnums[x1]
        name = frame.grid.m_grid.GetColLabelValue(realColx1)
        x = frame.grid.CleanData(realColx1)
        TBase = salstat_stats.OneSampleTests(frame.grid.CleanData(realColx1), name, \
                                             frame.grid.missing)
        d=[0]
        d[0] = TBase.d1
        x2=ManyDescriptives(self, d)
        # se verifica las opciones seleccionadas
        if len(self.TestChoice.GetChecked()) == 0:
            return
        # One sample t-test
        data={'name': 'One condition Tests',
              'size':(3,3),
              'nameCol': [],
              'data': []}
        result=[]
        result.append('One sample t-test')
        if self.TestChoice.IsChecked(0):    
            TBase.OneSampleTTest(umean)
            if (TBase.prob == -1.0):
                result.append('All elements are the same, test not possible')
            else:
                if self.m_radioBtn1.GetValue():  # (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append('t(%d) = %5.3f'%(TBase.df, TBase.t))
                result.append('p (approx) = %1.6f'%(TBase.prob))
            result.append('')

        result.append('One sample sign test') 
        if self.TestChoice.IsChecked(1):
            TBase.OneSampleSignTest(x, umean)
            if (TBase.prob == -1.0):
                result.append('All data are the same - no analysis is possible')
            else:
                if self.m_radioBtn1.GetValue(): #(self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append('N = %5.0f'%(TBase.ntotal))
                result.append('z = %5.3f'%( TBase.z))
                result.append('p = %1.6f'%(TBase.prob))
            result.append('')

        result.append('One sample chi square')
        
        if self.TestChoice.IsChecked(2):
            TBase.ChiSquareVariance(umean)
            if TBase.prob != None:
                if self.m_radioBtn1.GetValue():  #(self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append('Chi square (%d) = %5.3f'%(TBase.df, TBase.chisquare))
                result.append('p = %1.6f'%( TBase.prob))
            else:
                result.append('Cannot compute the probability')
        # se organiza los datos seleccionados
        data['data']= [[res] for res in result]
        data['size']= (len(result),1)
        output.upData(data)
        self.Close(True)

    def OnCloseOneCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
#dialog for 2 sample tests
class TwoConditionTestFrame(wx.Dialog):
    def __init__(self, parent, id, ColumnList):
        wx.Dialog.__init__(self, parent, id, "Two Condition Tests", \
                           size=(500,400+wind))
        icon = images.getIconIcon()
        self.SetIcon(icon)

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        ColumnList, self.colnums = frame.grid.GetUsedCols()

        colsselected =  frame.grid.GetColsUsedList()

        self.DescChoice = DescChoiceBox( self, wx.ID_ANY )
        self.m_mgr.AddPane( self.DescChoice, wx.aui.AuiPaneInfo() .Center() .
                            Caption( u"Select Descriptive Statistics" ).CloseButton( False ).
                            PaneBorder( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).BottomDockable( False ).TopDockable( False ).
                            Row(0).Layer(0) )

        # list of tests in alphabetical order
        Tests = ['chi square','F test','Kolmogorov-Smirnov', \
                 'Linear Regression', 'Mann-Whitney U', \
                 'Paired Sign', 't-test paired','t-test unpaired', \
                 'Wald-Wolfowitz Runs', 'Wilcoxon Rank Sums', \
                 'Wilcoxon Signed Ranks'] # nb, paired permutation test missing
        m_checkList6Choices = Tests
        self.paratests = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkList6Choices, 0 )
        self.m_mgr.AddPane( self.paratests , wx.aui.AuiPaneInfo() .Center() .
                            Caption( u"Select Test(s) to Perform:" ).CloseButton( False ).
                            PaneBorder( False ).Dock().Resizable().FloatingSize( wx.Size( 161,93 ) ).
                            DockFixed( False ).BottomDockable( False ).TopDockable( False ).
                            Row( 1 ).Layer( 0 ) )

        self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel2, wx.aui.AuiPaneInfo() .Left() .CaptionVisible( False ).
                            CloseButton( False ).PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ).Row( 1 ).
                            CentrePane() )

        bSizer21 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText1 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Select Columns", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        bSizer21.Add( self.m_staticText1, 0, wx.LEFT, 5 )

        m_choice1Choices = ColumnList
        self.ColBox1 = wx.Choice( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice1Choices, 0 )
        bSizer21.Add( self.ColBox1, 0, wx.ALL|wx.EXPAND, 5 )

        m_choice2Choices = ColumnList
        self.ColBox2 = wx.Choice( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice2Choices, 0 )
        bSizer21.Add( self.ColBox2, 0, wx.ALL|wx.EXPAND, 5 )

        x1 = 0
        x2 = 1
        self.ColBox1.SetSelection(x1)
        self.ColBox2.SetSelection(x2)
        realColx1 = x1
        realColx2 = x2
        x1len = len(frame.grid.CleanData(realColx1))
        x2len = len(frame.grid.CleanData(realColx2))
        if (x1len != x2len):
            self.equallists = False
        else:
            self.equallists = True

        sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel2, wx.ID_ANY, u"Seleccione Hypotesis" ), wx.HORIZONTAL )

        self.m_radioBtn1 = wx.RadioButton( self.m_panel2, wx.ID_ANY, u"One Tailed", wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer2.Add( self.m_radioBtn1, 0, wx.ALL, 5 )

        self.m_radioBtn2 = wx.RadioButton( self.m_panel2, wx.ID_ANY, u"Two Tailed", wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer2.Add( self.m_radioBtn2, 0, wx.ALL, 5 )
        self.m_radioBtn1.SetValue(True)

        bSizer21.Add( sbSizer2, 1, wx.EXPAND, 5 )

        sbSizer4 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel2, wx.ID_ANY, u"User hypotesis test" ), wx.VERTICAL )

        self.UserMean = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer4.Add( self.UserMean, 0, wx.EXPAND, 5 )


        bSizer21.Add( sbSizer4, 1, wx.EXPAND, 5 )


        self.m_panel2.SetSizer( bSizer21 )
        self.m_panel2.Layout()
        bSizer21.Fit( self.m_panel2 )
        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel1, wx.aui.AuiPaneInfo() .Bottom() .CaptionVisible( False ).
                            CloseButton( False ).PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ).LeftDockable( False ).
                            RightDockable( False ).MinSize( wx.Size( -1,30 ) ) )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.okaybutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.okaybutton, 0, wx.ALL, 5 )
        self.okaybutton.Enable(False)

        cancelbutton  = wx.Button( self.m_panel1, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( cancelbutton , 0, wx.ALL, 5 )

        self.allbutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Select All", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.allbutton, 0, wx.ALL, 5 )

        self.nonebutton= wx.Button( self.m_panel1, wx.ID_ANY, u"Select None", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.nonebutton, 0, wx.ALL, 5 )


        self.m_panel1.SetSizer( bSizer2 )
        self.m_panel1.Layout()
        bSizer2.Fit( self.m_panel1 )

        self.m_mgr.Update()
        self.Centre( wx.BOTH )

        # using self.equallists, if True, enable all items in the checklist \
        # box, otherwise set the within subs and correlations to be
        # disabled as they cannot be used with unequal list lengths!
        # Also disble the f-test unless something is entered into the
        # user hyp variance box
        self.Bind(wx.EVT_BUTTON, self.OnOkayButton, id = self.okaybutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCloseTwoCond, id = cancelbutton .GetId())
        self.Bind(wx.EVT_BUTTON, self.DescChoice.SelectAllDescriptives, id = self.allbutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.DescChoice.SelectNoDescriptives, id = self.nonebutton.GetId())
        self.UserMean.Bind( wx.EVT_TEXT, self.usermeanControl )
        self.Bind(wx.EVT_CHOICE, self.ChangeCol1, id = self.ColBox1.GetId())
        self.Bind(wx.EVT_CHOICE, self.ChangeCol1, id = self.ColBox2.GetId())

    def usermeanControl( self, event ):
        allowValues= [u'0',u'1',u'2',u'3',u'4',u'5',u'6',u'7',u'8',u'9',u'.']
        resultado = [val for val in self.UserMean.GetValue() if val in allowValues]
        newres = u""
        for val in resultado:
            newres+= val
        if self.UserMean.GetValue() != newres:
            self.UserMean.SetValue(newres)
        if len(newres) > 0 :
            # se habilita el control ok para calcular
            self.okaybutton.Enable(True)
        else:
            self.okaybutton.Enable(False)
        event.Skip()

    def ChangeCol1(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        colx1 = self.ColBox1.GetSelection()
        colx2 = self.ColBox2.GetSelection()
        realColx1 = self.colnums[colx1]
        realColx2 = self.colnums[colx2]
        x1 = len(frame.grid.CleanData(realColx1))
        x2 = len(frame.grid.CleanData(realColx2))
        if (x1 != x2):
            # disable some tests in the listbox
            self.paratests.Check(0,False)
        else:
            pass
            # enable all tests in the listbox

    def ChangeCol2(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        colx1 = self.ColBox1.GetSelection()
        colx2 = self.ColBox2.GetSelection()
        realColx1 = self.colnums[colx1]
        realColx2 = self.colnums[colx2]
        x1 = len(frame.grid.CleanData(realColx1))
        x2 = len(frame.grid.CleanData(realColx2))
        if (x1 != x2):
            pass
        else:
            pass

    def OnOkayButton(self, event):
        x1 = self.ColBox1.GetSelection()
        y1 = self.ColBox2.GetSelection()
        realColx1 = self.colnums[x1]
        realColy1 = self.colnums[y1]
        name1 = frame.grid.m_grid.GetColLabelValue(realColx1)
        name2 = frame.grid.m_grid.GetColLabelValue(realColy1)
        if (x1 < 0) or (y1 < 0):
            self.Close(True)
            return
        x = frame.grid.CleanData(realColx1)
        xmiss = frame.grid.missing
        y = frame.grid.CleanData(realColy1)
        ymiss = frame.grid.missing
        TBase = salstat_stats.TwoSampleTests(x, y, name1, name2,xmiss,ymiss)
        d = [0,0]
        d[0] = TBase.d1
        d[1] = TBase.d2
        x2 = ManyDescriptives(self, d)
        # chi square test
        data={'name': 'Two condition Tests',
              'size':(3,1),
              'data': []}
        result = []
        # data['nameCol'].append('One sample t-test')
        result.append('Chi square')
        if self.paratests.IsChecked(0):
            TBase.ChiSquare(x, y)
            if (TBase.prob == -1.0):
                result.append('Cannot do chi square - unequal data sizes')
                result.append('')
            else:
                if TBase.prob == None:
                    result.append("can't be computed")
                else:
                    result.append('chi (%d) = %5.3f'%(TBase.df, TBase.chisq,))
                    result.append('p = %1.6f'%(TBase.prob,))
                result.append('')

        # F-test for variance ratio's
        result.append('F test for variance ratio (independent samples)')
        if self.paratests.IsChecked(1):
            try:
                umean = float(self.UserMean.GetValue())
            except:
                result.append('Cannot do test - no user hypothesised mean specified')
            else:
                TBase.FTest(umean)
                if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append('f(%d, %d) = %5.3f'%( TBase.df1, TBase.df2, TBase.f))
                result.append('p = %1.6f'%( TBase.prob))
                result.append('')

        result.append('Kolmogorov-Smirnov test (unpaired)')
        if self.paratests.IsChecked(2):
            TBase.KolmogorovSmirnov()
            if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            result.append('D = %5.3f'%(TBase.d))
            result.append('p = %1.6f'%(TBase.prob))

        result.append('Linear Regression')
        if self.paratests.IsChecked(3):
            TBase.LinearRegression(x,y)
            #s, i, r, prob, st = salstat_stats.LinearRegression(x, y)
            if (TBase.prob == -1.0):
                result.append('Cannot do linear regression - unequal data sizes')
            else:
                if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append('Slope = %5.3f, Intercept = %5.3f,\
                                    r = %5.3f, Estimated Standard Error = \
                                    %5.3f' %(TBase.slope, TBase.intercept, \
                                             TBase.r, TBase.sterrest))
                result.append('<br>t (%d) = %5.3f, p = %1.6f' \
                              %(TBase.df, TBase.t, TBase.prob ))
                result.append('')

        result.append('Mann-Whitney U test (unpaired samples)')
        if self.paratests.IsChecked(4):
            TBase.MannWhitneyU(x, y)
            if (TBase.prob == -1.0):
                result.append('Cannot do Mann-Whitney U test - all numbers are identical')
            else:
                if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append('z = %5.3f, small U = %5.3f, \
                                    big U = %5.3f, p = %1.6f'%(TBase.z, \
                                                               TBase.smallu, TBase.bigu, TBase.prob))
                result.append('')

        # Paired permutation test
        """if self.paratests.IsChecked(5):
            output.htmlpage.Addhtml('<P><B>Paired Permutation test</B></P>')
            TBase.PairedPermutation(x, y)
            if (TBase.prob == -1.0):
                output.htmlpage.Addhtml('<BR>Cannot do test - not paired \
                                    samples')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                output.htmlpage.Addhtml('<BR>Utail = %5.0f, nperm = %5.3f, \
                        crit = %5.3f, p = %1.6f'%(TBase.utail, TBase.nperm, \
                        TBase.crit, TBase.prob))"""

        result.append('2 sample sign test')
        if self.paratests.IsChecked(5):
            TBase.TwoSampleSignTest(x, y)
            if (TBase.prob == -1.0):
                result.append('Cannot do test - not paired \
                                    samples')
            else:
                if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append('N = %5.0f, z = %5.3f, p = %1.6f'\
                              %(TBase.ntotal, TBase.z, TBase.prob))
                result.append('')

        result.append('t-test paired')
        if self.paratests.IsChecked(6):    
            TBase.TTestPaired(x, y)
            if (TBase.prob == -1.0):
                result.append('Cannot do paired t test - \
                                    unequal data sizes')
            else:
                if self.m_radioBtn1.GetValue():#self.hypchoice.GetSelection() == 0:
                    TBase.prob = TBase.prob / 2
                result.append('t(%d) = %5.3f, p = %1.6f'% \
                              (TBase.df, TBase.t, TBase.prob))
                result.append('')

        result.append('t-test unpaired')
        if self.paratests.IsChecked(7):
            TBase.TTestUnpaired()
            if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            result.append('t(%d) = %5.3f, p =  %1.6f'% \
                          (TBase.df, TBase.t, TBase.prob))
            result.append('')

        # Wald-Wolfowitz runs test (no yet coded)
        if self.paratests.IsChecked(8):
            pass

        result.append('Wilcoxon Rank Sums test (unpairedsamples)')
        if self.paratests.IsChecked(9):
            result.append('Rank Sums test (unpaired samples)')
            TBase.RankSums(x, y)
            if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            result.append('t = %5.3f, p = %1.6f'%(TBase.z, \
                                                  TBase.prob))
            result.append('')

        result.append('Wilcoxon t (paired samples)')# 
        if self.paratests.IsChecked(10):
            TBase.SignedRanks(x, y)
            if (TBase.prob == -1.0):
                result.append('Cannot do Wilcoxon t test - \
                                    unequal data sizes')
            else:
                if TBase.prob == None:
                    result.append("can't be computed")
                else:
                    if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                        TBase.prob = TBase.prob / 2
                    result.append('z = %5.3f, t = %5.3f, p = %1.6f'%
                                  (TBase.z, TBase.wt, TBase.prob))
                result.append('')
        data['size'] = (len(result),1)
        data['data'] = [[res] for res in result]
        output.upData(data)
        self.Close(True)

    def OnCloseTwoCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# dialog for single factor tests with 3+ conditions
class ThreeConditionTestFrame(wx.Dialog):
    def __init__(self, parent, id, ColumnList):
        wx.Dialog.__init__(self, parent, id, "Three Condition Tests", \
                           size = (500,400+wind))

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        icon = images.getIconIcon()
        self.SetIcon(icon)
        alltests = ['anova between subjects','anova within subjects',\
                    'Kruskall Wallis','Friedman test',\
                    'Cochranes Q']
        ColumnList, self.colnums = frame.grid.GetUsedCols()

        m_checkList5Choices = []
        self.DescChoice = DescChoiceBox(self, wx.ID_ANY)
        self.m_mgr.AddPane( self.DescChoice, wx.aui.AuiPaneInfo() .Center() .
                            Caption( u"Select Descriptive Statistics" ).
                            CloseButton( False ).PaneBorder( False ).Dock().
                            Resizable().FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).BottomDockable( False ).
                            TopDockable( False ).Row(0).Layer( 0 ) )

        m_checkList6Choices = alltests
        self.TestChoice = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkList6Choices, 0 )
        self.m_mgr.AddPane( self.TestChoice, wx.aui.AuiPaneInfo() .Center() .
                            Caption( u"Select the kind of Test" ).CloseButton( False ).
                            PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.Size( 161,93 ) ).DockFixed( False ).
                            BottomDockable( False ).TopDockable( False ).Row( 1 ).
                            Layer( 0 ) )

        self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SIMPLE_BORDER|wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel2, wx.aui.AuiPaneInfo() .Left() .
                            CaptionVisible( False ).CloseButton( False ).
                            PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ).
                            Row( 1 ).CentrePane() )

        bSizer21 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText1 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Select Columns to Analyse", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        bSizer21.Add( self.m_staticText1, 0, wx.LEFT, 5 )

        m_listBox1Choices = ColumnList
        self.ColChoice = wx.CheckListBox( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox1Choices, 0 )
        bSizer21.Add( self.ColChoice, 2, wx.EXPAND, 5 )
        for i in range(len(self.colnums)):
            self.ColChoice.Check(i, True)


        m_radioBox3Choices = HypList
        self.hypchoice = wx.RadioBox( self.m_panel2, wx.ID_ANY, u"Select Hypotesis", wx.DefaultPosition, wx.DefaultSize, m_radioBox3Choices, 1, wx.RA_SPECIFY_ROWS )
        self.hypchoice.SetSelection( 1 )
        bSizer21.Add( self.hypchoice, 1, wx.EXPAND, 5 )


        self.m_panel2.SetSizer( bSizer21 )
        self.m_panel2.Layout()
        bSizer21.Fit( self.m_panel2 )
        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel1, wx.aui.AuiPaneInfo() .Bottom() .CaptionVisible( False ).CloseButton( False ).PaneBorder( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).DockFixed( False ).LeftDockable( False ).RightDockable( False ).MinSize( wx.Size( -1,30 ) ) )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.okaybutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.okaybutton, 0, wx.ALL, 5 )

        self.cancelbutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.cancelbutton, 0, wx.ALL, 5 )

        self.allbutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Select All", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.allbutton, 0, wx.ALL, 5 )

        self.nonebutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Select None", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.nonebutton, 0, wx.ALL, 5 )


        self.m_panel1.SetSizer( bSizer2 )
        self.m_panel1.Layout()
        bSizer2.Fit( self.m_panel1 )

        self.m_mgr.Update()
        self.Centre( wx.BOTH )


        self.Bind(wx.EVT_BUTTON, self.OnOkayButton, id = self.okaybutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCloseThreeCond, id = self.cancelbutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.DescChoice.SelectAllDescriptives, id = self.allbutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.DescChoice.SelectNoDescriptives, id = self.nonebutton.GetId())

    def OnOkayButton(self, event):
        biglist = []
        ns = []
        sums = []
        means = []
        names = []
        miss = []
        k = 0
        for i in range(len(self.colnums)):
            if self.ColChoice.IsChecked(i):
                k = k + 1
                tmplist = frame.grid.CleanData(self.colnums[i])
                miss.append(frame.grid.missing)
                biglist.append(tmplist)
                names.append(frame.grid.m_grid.GetColLabelValue(i))
        k = len(biglist)
        d = []
        for i in range(k):
            x2=salstat_stats.FullDescriptives(biglist[i], names[i], miss[i])
            ns.append(x2.N)
            sums.append(x2.sum)
            means.append(x2.mean)
            d.append(x2)
        x2=ManyDescriptives(self, d)

        data={'name': 'Three + condition Tests',
              'size':(3,1),
              'data': []}
        result = []

        if (len(biglist) < 2):
            result.append('Not enough columns selected for \
                                    test!')
            data['size']=(1,1)
            output.upData(data)
            self.Close(True)
            return
        TBase = salstat_stats.ThreeSampleTests()
        #single factor between subjects anova
        if self.TestChoice.IsChecked(0):
            cols = []
            result.append('Single Factor anova - between \
                                    subjects')
            result.append('Warning! This test is based \
                                    on the following assumptions:')
            result.append('1) Each group has a normal \
                                    distribution of observations')
            result.append('2) The variances of each observation \
                                    are equal across groups (homogeneity of \
                                    variance)')
            result.append('3) The observations are statistically \
                                    independent')
            TBase.anovaBetween(d)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            result.append('FACTOR %5.3f  %5d  %5.3f %5.3f  %1.6f'%(TBase.SSbet,     \
                                                                   TBase.dfbet, TBase.MSbet, TBase.F, TBase.prob))
            result.append('Error %5.3f %5d %5.3f'%(TBase.SSwit, TBase.dferr, \
                                                   TBase.MSerr))
            result.append('Total %5.3f %5d'%(TBase.SStot, TBase.dftot))
            result.append('')

        result.append('single factor within subjects anova')
        if self.TestChoice.IsChecked(1):
            result.append('Warning! This test is based \
                                    on the following assumptions:')
            result.append('1) Each group has a normal \
                                    distribution of observations')
            result.append('2) The variances of each observation \
                                    are equal across groups (homogeneity of \
                                    variance)')
            result.append('3) The observations are statistically \
                                    indpendent')
            result.append('4) The variances of each participant \
                                    are equal across groups (homogeneity of \
                                    covariance)')
            TBase.anovaWithin(biglist, ns, sums, means)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2

            result.append('FACTOR %5.3f %5d %5.3f %5.3f %1.6f'%(TBase.SSbet,  \
                                                                TBase.dfbet, TBase.MSbet, TBase.F, TBase.prob))
            result.append('Within %5.3f %5d %5.3f '%(TBase.SSwit, TBase.dfwit,     \
                                                     TBase.MSwit))
            result.append('Error %5.3f %5d %5.3f'%(TBase.SSres, TBase.dfres,   \
                                                   TBase.MSres))
            result.append('Total %5.3f %5d '% (TBase.SStot, TBase.dftot))
            result.append('')

        result.append('kruskal wallis H Test')
        if self.TestChoice.IsChecked(2):
            TBase.KruskalWallisH(biglist)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            result.append('H(%d) = %5.3f, p = %1.6f'% \
                          (TBase.df, TBase.h, TBase.prob))

        result.append('Friedman Chi Square')
        if self.TestChoice.IsChecked(3):
            TBase.FriedmanChiSquare(biglist)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
                alpha = 0.10
            else:
                alpha = 0.05
            result.append('Chi(%d) = %5.3f, p = %1.6f'% \
                          (TBase.df, TBase.chisq, TBase.prob))
            # the next few lines are commented out & are experimental. They
            # help perform multiple comparisons for the Friedman test.
            #outstring = '<a href="friedman,'
            #for i in range(k):
            #    outstring = outstring+'M,'+str(TBase.sumranks[i])+','
            #outstring = outstring+'k,'+str(k)+','
            #outstring = outstring+'n,'+str(d[0].N)+','
            #outstring = outstring+'p,'+str(alpha)+'">Multiple Comparisons</a>'
            #output.htmlpage.Addhtml('<p>'+outstring+'</p>')

        result.append('Cochranes Q')
        if self.TestChoice.IsChecked(4):
            TBase.CochranesQ(biglist)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            result.append('Q (%d) = %5.3f, p = %1.6f'% \
                          (TBase.df, TBase.q, TBase.prob))
        data['size']= (len(result),1)
        data['data']= [[res] for res in result]
        output.upData(data)
        self.Close(True)

    def OnCloseThreeCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
class CorrelationTestFrame(wx.Dialog):
    def __init__(self, parent, id, ColumnList):
        winheight = 500 + wind
        wx.Dialog.__init__(self, parent, id, "Correlations", \
                           size=(500,400+wind))

        icon = images.getIconIcon()
        self.SetIcon(icon)

        ColumnList, self.colnums = frame.grid.GetUsedCols()
        colsselected =  frame.grid.GetColsUsedList()

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        self.DescChoice = DescChoiceBox(self, 215)
        self.m_mgr.AddPane( self.DescChoice, wx.aui.AuiPaneInfo() .Center() .
                            Caption( u"Select Descriptive Statistics" ).
                            CloseButton( False ).PaneBorder( False ).Dock().
                            Resizable().FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).BottomDockable( False ).
                            TopDockable( False ).Row( 0 ).Layer( 0 ) )
        # list of tests in alphabetical order
        Tests = ['Kendalls tau','Pearsons correlation','Point Biserial r', \
                 'Spearmans rho']
        m_checkList6Choices = Tests
        self.paratests = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkList6Choices, 0 )
        self.m_mgr.AddPane( self.paratests, wx.aui.AuiPaneInfo() .Center() .
                            Caption(u"Select Test(s) to Perform:" ).
                            CloseButton( False ).PaneBorder( False ).Dock().
                            Resizable().FloatingSize( wx.Size( 161,93 ) ).
                            DockFixed( False ).BottomDockable( False ).
                            TopDockable( False ).Row( 1 ).Layer( 0 ) )

        self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SIMPLE_BORDER|wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel2, wx.aui.AuiPaneInfo() .Left() .
                            CaptionVisible( False ).CloseButton( False ).
                            PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ).Row( 1 ).
                            CentrePane() )

        bSizer21 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText1 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Select Columns", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        bSizer21.Add( self.m_staticText1, 0, wx.LEFT, 5 )

        m_choice1Choices = ColumnList
        self.ColBox1 = wx.Choice( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice1Choices, 0 )
        bSizer21.Add( self.ColBox1, 0, wx.ALL|wx.EXPAND, 5 )

        m_choice2Choices = ColumnList
        self.ColBox2 = wx.Choice( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice2Choices, 0 )
        bSizer21.Add( self.ColBox2, 0, wx.ALL|wx.EXPAND, 5 )

        x1 = 0
        x2 = 1
        self.ColBox1.SetSelection(x1)
        self.ColBox2.SetSelection(x2)
        realColx1 = self.colnums[x1]
        realColx2 = self.colnums[x2]
        x1len = len(frame.grid.CleanData(realColx1))
        x2len = len(frame.grid.CleanData(realColx2))
        if (x1len != x2len):
            self.equallists = False
        else:
            self.equallists = True

        m_radioBox3Choices = HypList
        self.hypchoice = wx.RadioBox( self.m_panel2, wx.ID_ANY, u"Select Hypotesis", wx.DefaultPosition, wx.DefaultSize, m_radioBox3Choices, 1, wx.RA_SPECIFY_COLS )
        self.hypchoice.SetSelection( 1 )
        bSizer21.Add( self.hypchoice, 0, wx.ALL|wx.EXPAND, 5 )


        self.m_panel2.SetSizer( bSizer21 )
        self.m_panel2.Layout()
        bSizer21.Fit( self.m_panel2 )
        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel1, wx.aui.AuiPaneInfo() .Bottom() .CaptionVisible( False ).CloseButton( False ).PaneBorder( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).DockFixed( False ).LeftDockable( False ).RightDockable( False ).MinSize( wx.Size( -1,30 ) ) )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.okaybutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.okaybutton, 0, wx.ALL, 5 )

        self.cancelbutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.cancelbutton, 0, wx.ALL, 5 )

        self.allbutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Select All", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.allbutton, 0, wx.ALL, 5 )

        self.nonebutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Select None", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.nonebutton, 0, wx.ALL, 5 )


        self.m_panel1.SetSizer( bSizer2 )
        self.m_panel1.Layout()
        bSizer2.Fit( self.m_panel1 )

        self.m_mgr.Update()
        self.Centre( wx.BOTH )        

        self.Bind(wx.EVT_BUTTON, self.OnOkayButton, id = self.okaybutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCloseTwoCond, id = self.cancelbutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.DescChoice.SelectAllDescriptives, id = self.allbutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.DescChoice.SelectNoDescriptives, id = self.nonebutton.GetId())
        self.Bind(wx.EVT_COMBOBOX, self.ChangeCol1, id = self.ColBox1.GetId())
        self.Bind(wx.EVT_COMBOBOX, self.ChangeCol1, id = self.ColBox2.GetId())

    def ChangeCol1(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        realColx1 = self.colnums[self.ColBox1.GetSelection()]
        realColx2 = self.colnums[self.ColBox2.GetSelection()] 
        x1 = len(frame.grid.CleanData(realColx1))
        x2 = len(frame.grid.CleanData(realColx2))
        if (x1 != x2):
            print "unequal"
            # disable some tests in the listbox
        else:
            print "equal"
            # enable all tests in the listbox

    def ChangeCol2(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        realColx1 = self.colnums[self.ColBox1.GetSelection()]
        realColx2 = self.colnums[self.ColBox2.GetSelection()] 
        x1 = len(frame.grid.CleanData(realColx1))
        x2 = len(frame.grid.CleanData(realColx2))
        if (x1 != x2):
            print "unequal"
        else:
            print "equal"

    def OnOkayButton(self, event):
        x1 = self.ColBox1.GetSelection()
        y1 = self.ColBox2.GetSelection()
        realColx1 = self.colnums[self.ColBox1.GetSelection()]
        realColy1 = self.colnums[self.ColBox2.GetSelection()] 
        x1 = len(frame.grid.CleanData(realColx1))
        y1 = len(frame.grid.CleanData(realColy1))
        name1 = frame.grid.m_grid.GetColLabelValue(realColx1)
        name2 = frame.grid.m_grid.GetColLabelValue(realColy1)
        if (x1 < 0) or (y1 < 0):
            self.Close(True)
            return
        x = frame.grid.CleanData(realColx1)
        xmiss = frame.grid.missing
        y = frame.grid.CleanData(realColy1)
        ymiss = frame.grid.missing
        TBase = salstat_stats.TwoSampleTests(x, y, name1, name2,xmiss,ymiss)
        d = [0,0]
        d[0] = TBase.d1
        d[1] = TBase.d2
        x2 = ManyDescriptives(self, d)

        data={'name': 'Three + condition Tests',
              'size':(3,1),
              'data': []}
        result = []
        result.append('Kendalls tau correlation')
        if self.paratests.IsChecked(0):
            TBase.KendallsTau(x, y)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            result.append('tau = %5.3f, z = %5.3f, p = %1.6f'% \
                          (TBase.tau, TBase.z, TBase.prob))

            result.append('')

        result.append('Pearsons r correlation')
        if self.paratests.IsChecked(1):
            TBase.PearsonsCorrelation(x, y)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            result.append('r (%d) = %5.3f, t = %5.3f, p = %1.6f'% \
                          (TBase.df, TBase.r, TBase.t, TBase.prob))
            result.append('')

        # Point Biserial r
        if self.paratests.IsChecked(2):
            pass

        result.append('Spearmans rho correlation')
        if self.paratests.IsChecked(3):
            TBase.SpearmansCorrelation(x, y)
            if (TBase.prob == -1.0):
                result.append('Cannot do Spearmans correlation \
                                    - unequal data sizes')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append('rho(%d) = %5.3f, p = %1.6f'% \
                              (TBase.df, TBase.rho, TBase.prob))
            result.append('')
        data['data']= [[res] for res in result]
        data['size']= (len(result),1)
        output.upData(data)
        self.Close(True)

    def OnCloseTwoCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
class MFanovaFrame(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Multi-factorial anova", \
                           size=(500,400+wind))
        #set icon for frame (needs x-platform separator!
        x = self.GetClientSize()
        winheight = x[1]
        icon = images.getIconIcon()
        self.SetIcon(icon)
        ColumnList, self.colnums = frame.grid.GetUsedCols()
        l0 = wx.StaticText(self,-1,"Select Columns to Analyse",pos=(10,10))
        l1 = wx.StaticText(self, -1, "Select IV:", pos=(10,60))
        l2 = wx.StaticText(self, -1, "Select DV", pos=(10,170))
        l4 = wx.StaticText(self,-1,"Select Descriptive Statistics",pos=(250,10))
        self.IVbox = wx.CheckListBox(self, 413,wx.Point(10,30),\
                                     wx.Size(230,130),ColumnList)
        self.DVbox = wx.CheckListBox(self, 414,wx.Point(10,190), \
                                     wx.Size(230,120),ColumnList)
        self.hypchoice=wx.RadioBox(self, 205,"Select Hypothesis",\
                                   wx.Point(10,320),wx.DefaultSize,HypList)
        self.hypchoice.SetSelection(1)
        #self.DescChoice = DescChoiceBox(self, 215)
        # I might leave the descriptives out and implement a feedback box
        # that tells the user about the analysis (eg, how many factors, #
        # levels per factor, # interactions etc which might be useful. It
        # would be updated whenever the user changes a selection.
        okaybutton = wx.Button(self,216,"Okay",wx.Point(10,winheight-35), \
                               wx.Size(BWidth, BHeight))
        cancelbutton = wx.Button(self,217,"Cancel",wx.Point(100,winheight-35), \
                                 wx.Size(BWidth, BHeight))
        allbutton = wx.Button(self, 218,"Select All",wx.Point(250,winheight-70),\
                              wx.Size(BWidth, BHeight))
        nonebutton = wx.Button(self, 220, "Select None", wx.Point(360, \
                                                                  winheight-70),wx.Size(BWidth, BHeight))
        self.DescChoice = DescChoiceBox(self, 104)
        self.Bind(wx.EVT_BUTTON,okaybutton, 216, self.OnOkayButton)
        self.Bind(wx.EVT_BUTTON,cancelbutton, 217, self.OnCloseTwoCond)
        self.Bind(wx.EVT_BUTTON,allbutton, 218, self.DescChoice.SelectAllDescriptives)
        self.Bind(wx.EVT_BUTTON,nonebutton, 220, self.DescChoice.SelectNoDescriptives)
        # Need to check that a col ticked in one box is not ticked in the other
        #EVT_CHECKLISTBOX(self.IVbox, 413, self.CheckforIXbox)
        #EVT_CHECKLISTBOX(self.DVbox,414,self.CheckforDVbox)

    def OnOkayButton(self, event):
        self.Close(True)

    def OnCloseTwoCond(self, event):
        self.Close(True)

#---------------------------------------------------------------------------
# instance of the tool window that contains the test buttons
# note this is experimental and may not be final
class TestFrame(wx.MiniFrame):
    def __init__(self, parent, title):
        self.parent = parent
        wx.MiniFrame.__init__(self, parent, -1, 'Tests', size=(120,400), pos=(5,5))
        descButton = wx.Button(self, 151,'Descriptives (F1)',wx.Point(0,0),wx.Size(115,40))
        sign1Button=wx.Button(self,153,'sign test 1 sample',wx.Point(0,40),wx.Size(115,40))
        ttestpairedButton=wx.Button(self,154,'t-test paired <F2>',wx.Point(0,80),wx.Size(115,40))
        ttestunpairedButton = wx.Button(self, 155, 't-test unpaired <F3>',wx.Point(0,120),wx.Size(115,40))
        chisquareButton = wx.Button(self,156,'Chi square <F4>',wx.Point(0,160),wx.Size(155,40))
        mannwhitneyButton=wx.Button(self,157,'Mann-Whitney U',wx.Point(0,200),wx.Size(115,40))
        kolmogorovButton=wx.Button(self,158,'Kolmogorov-Smirnov',wx.Point(0,240),wx.Size(115,40))
        anovaButton=wx.Button(self,159,'anova between',wx.Point(0,280),wx.Size(115,40))
        anovaWButton=wx.Button(self,160,'anova within',wx.Point(0,320),wx.Size(115,40))
        # and so on...
        # only put keyboard shortcuts for the most required ones. DONT allow the user to change this
        EVT_CLOSE(self, self.DoNothing)
        self.Bind(wx.EVT_BUTTON,descButton, 151, self.GetDescriptives)

    def DoNothing(self, event):
        pass

    def GetDescriptives(self, event):
        print self.parent.grid.m_grid.GetSelectedCols()

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
        pass # start transforming!
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

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
# call instance of DataGrid
# This is main interface of application
class DataFrame(wx.Frame):
    def __init__(self, parent, appname ):
        
        #dimx = int(inits.get('gridsizex'))
        #dimy = int(inits.get('gridsizey'))
        self.path = None
        wx.Frame.__init__(self,parent,-1,"SalStat Statistics", 
                          size=wx.Size(640,480 ), pos=wx.DefaultPosition)
        
        self.m_notebook1 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.logPanel = LogPanel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        
        
        
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

        self.mn1= wx.MenuItem(file_menu,ID_FILE_NEW,'&New Data')
        self.mn1.SetBitmap(NewIcon)
        file_menu.AppendItem(self.mn1)
        #file_menu.Append(ID_FILE_NEWOUTPUT, 'New &Output Sheet')
        self.mn2=file_menu.Append(ID_FILE_OPEN, '&Open...')
        self.mn2.SetBitmap(OpenIcon)
        self.mn3=file_menu.Append(ID_FILE_SAVE, '&Save')
        self.mn3.SetBitmap(SaveIcon)
        self.mn4=file_menu.Append(ID_FILE_SAVEAS, 'Save &As...')
        self.mn4.SetBitmap(SaveAsIcon)
        self.mn5=file_menu.AppendSeparator()
        self.mn6=file_menu.Append(ID_FILE_PRINT, '&Print...')
        self.mn6.SetBitmap(PrintIcon)
        file_menu.AppendSeparator()
        self.mn7=file_menu.Append(ID_FILE_EXIT, 'E&xit')
        self.mn7.SetBitmap(ExitIcon)
        self.mn8= wx.MenuItem(edit_menu,ID_EDIT_CUT,'Cu&t')
        self.mn8.SetBitmap(CutIcon)
        edit_menu.AppendItem(self.mn8)
        self.mn9=edit_menu.Append(ID_EDIT_COPY, '&Copy')
        self.mn9.SetBitmap(CopyIcon)
        self.mn10=edit_menu.Append(ID_EDIT_PASTE, '&Paste')
        self.mn10.SetBitmap(PasteIcon)
        self.mn11=edit_menu.Append(ID_EDIT_SELECTALL, 'Select &All')
        self.mn12=edit_menu.Append(ID_EDIT_FIND, '&Find and Replace...')
        self.mn12.SetBitmap(FindRIcon)
        edit_menu.AppendSeparator()
        self.mn13=edit_menu.Append(ID_EDIT_DELETECOL, 'Delete Current Column')
        self.mn14=edit_menu.Append(ID_EDIT_DELETEROW, 'Delete Current Row')
        self.mn15=prefs_menu.Append(ID_PREF_VARIABLES, 'Variables...')
        self.mn16=prefs_menu.Append(ID_PREF_GRID, 'Add Columns and Rows...')
        self.mn17=prefs_menu.Append(ID_PREF_CELLS, 'Change Cell Size...')
        self.mn18=prefs_menu.Append(ID_PREF_FONTS, 'Change the Font...')
        self.mn19=preparation_menu.Append(ID_PREPARATION_DESCRIPTIVES, 'Descriptive Statistics...')
        self.mn20=preparation_menu.Append(ID_PREPARATION_TRANSFORM, 'Transform Data...')
        #preparation_menu.Append(ID_PREPARATION_OUTLIERS, 'Check for Outliers...')
        #preparation_menu.Append(ID_PREPARATION_NORMALITY, 'Check for Normal Distribution...')
        self.mn21=analyse_menu.Append(ID_ANALYSE_1COND, '&1 Condition Tests...')
        self.mn22=analyse_menu.Append(ID_ANALYSE_2COND, '&2 Condition Tests...')
        self.mn23=analyse_menu.Append(ID_ANALYSE_3COND, '&3+ Condition Tests...')
        self.mn24=analyse_menu.Append(ID_ANALYSE_CORRELATION,'&Correlations...')
        #analyse_menu.Append(ID_ANALYSE_2FACT, '2+ &Factor Tests...')
        
        self.mn26=chart_menu.Append(ID_CHART_DRAW, 'Line Chart of All Means...')
        self.mn27=chart_menu.Append(ID_BARCHART_DRAW, 'Bar Chart of All Means...')
        self.mn273= chart_menu.Append(wx.NewId(), 'Lines')
        self.mn271= chart_menu.Append(wx.NewId(), 'Scatter')
        self.mn272= chart_menu.Append(wx.NewId(), 'Box&Wishker Plot')
        self.mn274= chart_menu.Append(wx.NewId(), 'Lineal Regress')

        self.mn28=help_menu.Append(ID_HELP_WIZARD, '&What Test Should I Use...')
        self.mn29=help_menu.Append(ID_HELP_TOPICS, '&Topics...')
        self.mn30=help_menu.Append(ID_HELP_LICENCE, '&Licence...')
        self.mn31=help_menu.Append(ID_HELP_ABOUT, '&About...')
        #set up menu bar
        menuBar = wx.MenuBar()
        menuBar.Append(file_menu, '&File')
        menuBar.Append(edit_menu, '&Edit')
        menuBar.Append(prefs_menu, '&Preferences')
        menuBar.Append(preparation_menu, 'P&reparation')
        menuBar.Append(analyse_menu, '&Analyse')
        menuBar.Append(chart_menu, '&Graph')
        menuBar.Append(help_menu, '&Help')
        self.SetMenuBar(menuBar)
        #------------------------
        #create small status bar
        self.CreateStatusBar()
        self.SetStatusText('SalStat Statistics')

        #----------------------
        # se crea una barra de herramientas

        #create toolbar (nothing to add yet!)
        tb1= aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                            agwStyle=  aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        ##tb1.SetDimensions(wx.Size(16,16))
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
        # more toolbuttons are needed: New Output, Save, Print, Cut, \
        # Variables, and Wizard creates the toolbar
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
                
        self.m_mgr.AddPane( tb1, aui.AuiPaneInfo().Top().Dock().
                            Resizable(False).FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).Layer(1).ToolbarPane().
                            LeftDockable( False ).RightDockable(False).
                            CloseButton(False ) )
        
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
        #-----------------
        # para el toolbar
        self.Bind(wx.EVT_MENU, self.GoClearData,        id = self.bt1.GetId())
        self.Bind(wx.EVT_MENU, self.grid.LoadDataASCII, id = self.bt2.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SaveXls,  id = self.bt3.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SaveXlsAs,id= self.bt4.GetId())
        ##self.Bind(wx.EVT_MENU, self.grid.PrintPage, id = self.bt5.GetId())
        self.Bind(wx.EVT_MENU, self.grid.CutData,       id = self.bt6.GetId())
        self.Bind(wx.EVT_MENU, self.grid.CopyData,      id = self.bt7.GetId())
        self.Bind(wx.EVT_MENU, self.grid.PasteData,     id = self.bt8.GetId())
        self.Bind(wx.EVT_MENU, self.GoVariablesFrame,   id = self.bt9.GetId())
        self.Bind(wx.EVT_MENU, self.GoHelpAboutFrame,   id = self.bt10.GetId())
        self.Bind(wx.EVT_MENU, self.grid.Undo,   id = self.bt11.GetId())
        self.Bind(wx.EVT_MENU, self.grid.Redo,   id = self.bt12.GetId())
        #-----------------
        # Menu
        self.Bind(wx.EVT_MENU, self.GoClearData,        id = self.mn1.GetId())
        self.Bind(wx.EVT_MENU, self.grid.LoadDataASCII, id = self.mn2.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SaveXls, id = self.mn3.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SaveXlsAs,id = self.mn4.GetId())
        ##self.Bind(wx.EVT_MENU, seelf.grid.SaveXlsAs,id = ID_FILE_PRINT)
        self.Bind(wx.EVT_MENU, self.EndApplication,     id = self.mn7.GetId())
        self.Bind(wx.EVT_MENU, self.grid.CutData,       id = self.mn8.GetId())
        self.Bind(wx.EVT_MENU, self.grid.CopyData,      id = self.mn9.GetId())
        self.Bind(wx.EVT_MENU, self.grid.PasteData,     id = self.mn10.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SelectAllCells,id = self.mn11.GetId())
        self.Bind(wx.EVT_MENU, self.GoFindDialog,       id = self.mn12.GetId())
        self.Bind(wx.EVT_MENU, self.grid.DeleteCurrentCol,id = self.mn13.GetId())
        self.Bind(wx.EVT_MENU, self.grid.DeleteCurrentRow,id = self.mn14.GetId())
        self.Bind(wx.EVT_MENU, self.GoVariablesFrame,   id = self.mn15.GetId())
        self.Bind(wx.EVT_MENU, self.GoEditGrid,         id = self.mn16.GetId())
        self.Bind(wx.EVT_MENU, self.GoGridPrefFrame,    id = self.mn17.GetId())
        self.Bind(wx.EVT_MENU, self.GoFontPrefsDialog,  id = self.mn18.GetId())
        self.Bind(wx.EVT_MENU, self.GoContinuousDescriptives,id = self.mn19.GetId())
        self.Bind(wx.EVT_MENU, self.GoTransformData,    id = self.mn20.GetId())
        self.Bind(wx.EVT_MENU, self.GoOneConditionTest, id = self.mn21.GetId())
        self.Bind(wx.EVT_MENU, self.GoTwoConditionTest, id = self.mn22.GetId())
        self.Bind(wx.EVT_MENU, self.GetThreeConditionTest,id = self.mn23.GetId())
        self.Bind(wx.EVT_MENU, self.GetCorrelationsTest,id = self.mn24.GetId())

        self.Bind(wx.EVT_MENU, self.GoChartWindow,      id = self.mn26.GetId())
        self.Bind(wx.EVT_MENU, self.GoBarChartWindow,   id = self.mn27.GetId())
        self.Bind(wx.EVT_MENU, self.GoScatterPlot,   id = self.mn271.GetId())
        self.Bind(wx.EVT_MENU, self.GoBoxWishkerPlot,   id = self.mn272.GetId())
        self.Bind(wx.EVT_MENU, self.GoLinesPlot,   id = self.mn273.GetId())
        self.Bind(wx.EVT_MENU, self.GoLinRegressPlot,   id = self.mn274.GetId())
        
        # controlling the expansion of the notebook
        self.m_notebook1.Bind( wx.EVT_LEFT_DCLICK, self._OnNtbDbClick )

        self.grid.m_grid.setPadreCallBack(self) 
        if 0:
            self.Bind(wx.EVT_MENU, self.GoCheckOutliers,    id = ID_PREPARATION_OUTLIERS)
            #self.Bind(wx.EVT_MENU, ID_ANALYSE_2FACT, self.GoMFanovaFrame)
            self.Bind(wx.EVT_MENU, self.GoHelpAboutFrame,   id = ID_HELP_ABOUT)
            self.Bind(wx.EVT_MENU, self.GoHelpWizardFrame,  id = ID_HELP_WIZARD)
            self.Bind(wx.EVT_MENU, self.GoHelpTopicsFrame,  id = ID_HELP_TOPICS)
            self.Bind(wx.EVT_MENU, self.GoHelpLicenceFrame, id = ID_HELP_LICENCE)
            self.Bind(wx.EVT_MENU, self.EndApplication,     id = ID_FILE_EXIT)


            self.Bind(wx.EVT_MENU, self.GoClearData, id=10) ### VERIFICAR
            # self.Bind(wx.EVT_MENU, ID_FILE_NEWOUTPUT, self.GoNewOutputSheet)
            # unsure if I want this - maybe restrict user to just one?
            self.Bind(wx.EVT_MENU, self.grid.SaveXls, id =  30)
            self.Bind(wx.EVT_MENU, self.grid.SaveAsSaveXlsAs40)
            #self.Bind(wx.EVT_MENU, ID_FILE_OPEN, self.grid.LoadNumericData)
            self.Bind(wx.EVT_MENU, self.grid.LoadDataASCII, id = 20)
            #EVT_TOOL(self, 20, self.grid.LoadNumericData)
            self.Bind(wx.EVT_MENU, self.grid.CutData, id= 60)
            self.Bind(wx.EVT_MENU, self.grid.CopyData, id = 70)
            self.Bind(wx.EVT_MENU, self.grid.PasteData, id = 80)


            self.Bind(wx.EVT_CLOSE, self.EndApplication, self)
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

    def GoOneConditionTest(self, event):
        # shows One Condition Test dialog
        ColumnList, waste = self.grid.GetUsedCols()
        if (len(ColumnList) > 0):
            win = OneConditionTestFrame(frame, -1, ColumnList)
            win.Show(True)
        else:
            self.SetStatusText('You need to enter 1 data column for this!')

    def GoTwoConditionTest(self,event):
        # show Two Conditions Test dialog
        ColumnList, waste = self.grid.GetUsedCols()
        if (len(ColumnList) > 1):
            win = TwoConditionTestFrame(frame, -1, ColumnList)
            win.Show(True)
        else:
            self.SetStatusText('You need 2 data columns for that!')

    def GetThreeConditionTest(self, event):
        # shows three conditions or more test dialog
        ColumnList, waste = self.grid.GetUsedCols()
        if (len(ColumnList) > 1):
            win = ThreeConditionTestFrame(frame, -1, ColumnList)
            win.Show(True)
        else:
            self.SetStatusText('You need some data for that!')

    def GetCorrelationsTest(self, event):
        # Shows the correlations dialog
        ColumnList, waste = self.grid.GetUsedCols()
        if (len(ColumnList) > 1):
            win = CorrelationTestFrame(frame, -1, ColumnList)
            win.Show(True)
        else:
            self.SetStatusText('You need 2 data columns for that!')

    def GoMFanovaFrame(self, event):
        win = MFanovaFrame(frame, -1)
        win.Show(True)



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
        data = [salstat_stats.FullDescriptives(self.grid.CleanData(cols)) for cols in [colnums[m] for m in selectedcols]]
        data = [data[i].mean for i in range(len(data))]
        plt= plot(parent = self, typePlot= 'plotLine',
                  data2plot= ((range(len(data)),data,'Mean'),))
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
        data = [salstat_stats.FullDescriptives(self.grid.CleanData(cols)) for cols in [colnums[m] for m in selectedcols]]
        data = [data[i].mean for i in range(len(data))]
        plt= plot(parent = self, typePlot= 'plotBar',
                  data2plot= ((data,'Mean'),))
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
                  data2plot= ((data[0],data[1],waste[xcol] +u' Vs '+ waste[ycol]),))
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
                  data2plot= data)
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
                  data2plot= data)
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
                  data2plot= (data[0],data[1],waste[xcol] +u' Vs '+ waste[ycol]) )
        plt.Show()

    def EndApplication(self, evt):
        # close the application (need to check for new data since last save)
        # need to save the inits dictionary to .salstatrc
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

def Display(text):
    """writes the text onto the html page. Handles lists and numerics"""
    text = str(text)
    output.htmlpage.write(string.join(text, ""))

def Describe(datain):
    """Provides OO descriptive statistics. Called by >>>x = Describe(a)
    and then a.N for the N, a.sumafor the sum etc"""
    if (type(datain) == int):
        datain = frame.grid.CleanData(col2)
    return salstat_stats.FullDescriptives(datain)


def PutData(column, data):
    """This routine takes a list of data, and puts it into the datagrid
    starting at row 0. The grid is resized if the list is too large. This
    routine desparately needs to be updated to prevent errors"""
    n = len(data)
    if (n > frame.grid.m_grid.GetNumberRows()):
        frame.grid.m_grid.AddNCols(-1, (datawidth - gridwidth + 5))
    for i in range(n):
        frame.grid.m_grid.SetCellValue(i, column, str(data[i]))

#---------------------------------------------------------------------------
# API statistical analysis functions
#One sample tests:
def DoOneSampleTTest(col1, usermean, tail = 2):
    """This routine performs a 1 sample t-test using the given data and
    a specified user mean."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for column 1\n'
    TBase = salstat_stats.OneSampleTests(col1, umean)
    TBase.OneSampleTTest(usermean)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.df, TBase.prob
    else:
        raise #return Error

def DoOneSampleSignTest(col1, usermean, tail = 2):
    """This routine performs a 1 sample sign-test using the given data and
    a specified user mean."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for column 1\n'
    TBase = salstat_stats.OneSampleTests(col1, umean)
    TBase.OneSampleSignTest(usermean)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.nplus, TBase.nminus, TBase.z, TBase.prob
    else:
        raise #return Error

def DoChiSquareVariance(col1, usermean, tail = 2):
    """This routine performs a chi square for variance ratio test using
    the given data and a specified user mean."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for column 1\n'
    TBase = salstat_stats.OneSampleTests(col1, umean)
    TBase.ChiSquareVariance(usermean)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.chisquare, TBase.df, TBase.prob
    else:
        raise #return Error

#Two sample tests:
def DoPairedTTest(col1, col2, tail = 2):
    """This routine performs a paired t-test using the data contained in
    col1 and col2 on the grid, with the passed alpha value which defaults
    to 0.05 (5%). If col1 and col2 are lists, then the data contained in the
    lists are used instead. There is a modicum of bounds checking on the
    passed variables to ensure that they are the right types (and bounds)"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for column 1\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col2)
    elif (type(col2) != list):
        error = error +'Invalid information for column 2\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.TTestPaired(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.df, TBase.prob
    else:
        raise # return Error

def DoUnpairedTTest(col1, col2, tail = 2):
    """This function performs an unpaired t-test on the data passed. If the
    passed parameters are a list, then that is used as the data, otherwise
    if the parameters are an integer, then that integers columns data are
    retrieved."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.TTestUnpaired()
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.df, TBase.prob
    else:
        return error

def DoPearsonsCorrelation(col1, col2, tail = 2):
    """This function performs a Pearsons correlation upon 2 data sets."""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.PearsonsCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.r, TBase.df, TBase.prob
    else:
        return error

def DoFTest(col1, col2, uservar, tail = 2):
    """This performs an F-test for variance ratios upon 2 data sets. Passed
    in addition to the datasets is the user variance"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.TwoSampleSignTextCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.t, TBase.r, TBase.df, TBase.prob
    else:
        return error

def DoSignTest(col1, col2, tail = 2):
    """This function performs a 2-sample sign test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.TwoSampleSignTextCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.z, TBase.prob
    else:
        return error

def DoKendallsCorrelation(col1, col2, tail = 2):
    """This function performs a Kendalls tau correlation"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.KendalssTau(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.tau, TBase.z, TBase.prob
    else:
        return error

def DoKSTest(col1, col2, tail = 2):
    """This function performs a Komogorov-Smirnov test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.KolmogorovSmirnov(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.d, TBase.prob
    else:
        return error

def DoSpearmansCorrelation(col1, col2, tail = 2):
    """This function performs a Spearmans correlation on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.SpearmansCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.rho, TBase.t, TBase.df, TBase.prob
    else:
        return error

def DoRankSums(col1, col2, tail = 2):
    """This function performs a Wilcoxon rank sums test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    selobu = salstat_stats.TwoSampleTests(col1,col2)
    TBase = selobu.RankSums(col1, col2) # salstat_stats.RankSums(col1, col2)
    TBase.TwoSampleSignTextCorrelation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.z, TBase.prob
    else:
        return error

def DoSignedRanks(col1, col2, tail = 2):
    """This function performs a Wilcoxon signed ranks test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.SignedRanks(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.z, TBase.wt, TBase.prob
    else:
        return error

def DoMannWhitneyTest(col1, col2, tail = 2):
    """This function performs a Mann-Whitney U test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.MannWhitneyU(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.bigu, TBase.smallu, TBase.z, TBase.prob
    else:
        return error

def DoLinearRegression(col1, col2, tail = 2):
    """This function performs a 2-sample sign test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.LinearRegression(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.df, TBase.r, TBase.slope, TBase.intercept, \
               TBase.sterrest, TBase.prob
    else:
        return error

def DoPairedPermutation(col1, col2, tail = 2):
    """This function performs a 2-sample sign test on 2 data sets"""
    error = ""
    if (type(col1) == int):
        col1 = frame.grid.CleanData(col1)
    elif (type(col1) != list):
        error = error + 'Invalid information for first dataset\n'
    if (type(col2) == int):
        col2 = frame.grid.CleanData(col1)
    elif (type(col2) != list):
        error = error + 'Invalid information for second dataset\n'
    TBase = salstat_stats.TwoSampleTests(col1, col2)
    TBase.PairedPermutation(col1, col2)
    if (tail == 1):
        TBase.prob = TBase.prob / 2
    if (tail != 1) and (tail != 2):
        error = error + "Invalid information for the tail"
    if (error == ""):
        return TBase.nperm, TBase.prob
    else:
        return error

# Three+ sample tests:

# Probability values
def GetChiProb(chisq, df):
    """This function takes the chi square value and the df and returns the
    p-value"""
    return salstat_stats.chisqprob(chisq, df)

def GetInverseChiProb(prob, df):
    """This function returns a chi value that matches the probability and
    df passed"""
    return salstat_stats.inversechi(prob, df)

def GetZProb(z):
    """This function returns the probability of z"""
    return salstat_stats.zprob(z)

def GetKSProb(ks):
    """This function returns the probability of a Kolmogorov-Smirnov test
    being significant"""
    return salstat_stats.ksprob(ks)

def GetTProb(t, df):
    """Gets the p-value for the passed t statistic and df"""
    return salstat_stats.betai(0.5*self.df,0.5,float(self.df)/(self.df+ \
                                                               self.t*self.t))

def GetFProb(f, df1, df2):
    """This returns the p-value of the F-ratio and the 2 df's passed"""
    return salstat_stats.fprob(df1, df2, f)

def GetInverseFProb(prob, df1, df2):
    """Returns the f-ratio of the given p-value and df's"""
    return salstat_stats.inversef(prob, df1, df2)


#---------------------------------------------------------------------------
# main loop
if __name__ == '__main__':
    import sys
    # find init file and read otherwise create it
    # ini = GetInits()
    app = wx.App()
    frame = DataFrame(None, app)
    frame.grid.SetFocus()
    Logg= frame.logPanel
    output = frame.answerPanel # OutputSheet(frame, -1)
    frame.ShowFullScreen(True,False)
    # output.Show(True)
    app.MainLoop()

#---------------------------------------------------------------------------