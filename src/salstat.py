#!/usr/bin/env python
A2 = [0,0, 1.886, 1.023, 0.729, 0.577, 0.483, 0.419, 0.373, 0.337, 0.308, 0.285, 0.266, 0.249, 0.235, 0.223]
A3 = [0,0, 2.659, 1.954, 1.628, 1.427, 1.287, 1.182, 1.099, 1.032, 0.975, 0.927, 0.886, 0.850, 0.817, 0.789]#, 0.680, 0.606]
D3 = [0,0, 0,     0,     0,     0,     0,     0.076, 0.136, 0.184, 0.223, 0.256, 0.283, 0.307, 0.328, 0.347]
D4 = [0,0, 3.268, 2.574, 2.282, 2.114, 2.004, 1.924, 1.864, 1.816, 1.777, 1.744, 1.717, 1.693, 1.672, 1.653]
# n   0 1      2      3      4      5      6      7      8      9     10     11     12     13     14     15       20     25
c4 = [0,0,0.7979,0.8862,0.9213,0.9400,0.9515,0.9594,0.9650,0.9693,0.9727,0.9754,0.9776,0.9794,0.9810,0.9823]#,0.9869,0.9896]
B3 = [0,0,     0,     0,     0,     0, 0.030, 0.118, 0.185, 0.239, 0.284, 0.322, 0.354, 0.382, 0.407, 0.428]#, 0.510, 0.565]
B4 = [0,0, 3.267, 2.568, 2.266, 2.089, 1.970, 1.882, 1.815, 1.761, 1.716, 1.678, 1.646, 1.619, 1.593, 1.572]#, 1.490, 1.435]
B5 = [0,0,     0,     0,     0,     0, 0.029, 0.113, 0.179, 0.232, 0.276, 0.313, 0.346, 0.374, 0.399, 0.421]#, 0.504, 0.559]
B6 = [0,0, 2.606, 2.276, 2.088, 1.964, 1.874, 1.806, 1.751, 1.707, 1.669, 1.637, 1.610, 1.585, 1.563, 1.544]#, 1.470, 1.420]

""" Copyright 2012 Sebastian Lopez Buritica

SalStat Statistics Package. Copyright 2002 Alan James Salmoni. Licensed
under the GNU General Public License (GPL 2). See the file COPYING for full
details of this license. """

import wx
import os

# automatically importing all the central tendency classes
from slbTools import isiterable

from statFunctions.centralTendency import geometricMean,\
     harmonicmean, mean, median, medianscore, mode
import wx.html
import wx.lib.agw.aui as aui

import wx.lib.wxpTag
import string, os, os.path, pickle

from imagenes import imageEmbed
import numpy, math
import wx.py
import xlrd
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
from ntbSheet import NoteBookSheet

from openStats import statistics, normProb, normProbInv

from slbTools import ReportaExcel, homogenize
from easyDialog import Dialog as dialog
from statlib import stats
from ntbSheet import MyGridPanel as MyGrid

from script import ScriptPanel
from imagenes import imageEmbed

from helpSystem import Navegator

from dialogs import CheckListBox, SixSigma
from gridCellRenderers import floatRenderer, AutoWrapStringRenderer

APPNAME= 'SalStat2'
DescList= ['N','Sum','Mean','missing',
           'Variance','Standard Deviation','Standard Error',
           'Sum of Squares',#'Sum of Squared Devs',
           'Coefficient of Variation','Minimum',
           'Maximum','Range','Number Missing',
           'Geometric Mean','Harmonic Mean',
           'Skewness','Kurtosis', 'Median',        #'Median Absolute Deviation',
           'Mode', ] #'Interquartile Range', 'Number of Unique Levels']

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
    def __init__(self, parent):  

        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Save data?", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"You have unsaved data!", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        bSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"Do you wish to save it?", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        bSizer1.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_button1 = wx.Button( self, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.m_button1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_button2 = wx.Button( self, wx.ID_ANY, u"Discard", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.m_button2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_button3 = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
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
        wx.GetApp().frame.grid.Saved = True
        wx.GetApp().frame.grid.SaveXlsAs(self) # will it be ASCII or XML?
        # wx.GetApp().output.Close(True)
        self.Close(True)
        wx.GetApp().frame.Close(True)

    def DiscardData(self, evt):
        self.Close(True)
        wx.GetApp().frame.Close(True)


    def CancelDialog(self, evt):
        self.Close(True)

#---------------------------------------------------------------------------
# class to wx.GetApp().output the results of several "descriptives" in one table
class ManyDescriptives:
    def __init__(self, source, ds):
        __x__= len(ds)
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
                    'Variance': 'variance', # changing by the correct
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
                    'Mode': 'mode',#    'Interquartile Range': None,
                    'Number of Unique Levels': 'numberuniques'}
        items= source.DescChoice.GetItems()
        itemsSelected = source.DescChoice.GetChecked()
        if len(itemsSelected ) == 0:
            return
        firstcol= ['Descriptives']
        firstcol.extend([items[pos] for pos in itemsSelected])
        wx.GetApp().output.addColData(firstcol, 'Descriptive statistics')
        itemNamesSelected= [ items[ itemnumber] for  itemnumber in itemsSelected ]
        for i, nameCol in zip(range(__x__), data['nameCol'][1:]):
            statsi = ds[i]
            result= [nameCol]
            result.extend([getattr(statsi,funcTrans[ itemNameSelected]) for itemNameSelected in itemNamesSelected])
            wx.GetApp().output.addColData(result)
        #for aliasParamName in itemsSelected:
            #realParamName = funcTrans[aliasParamName]
            #if realParamName == None:
                #continue
            #res= [aliasParamName]
            #if hasattr(ds[i],realParamName):
                #res.extend([getattr(ds[i],realParamName) for i in range(__x__)])
                #data['data'].append(res)
            #wx.GetApp().output.addColData(funcTrans.keys())
        #data['size']= (len(data['data']), len(data['nameCol']))

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

        self.setPadreCallBack(self)
        self.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        #for i in range(self.NumberCols):
        #    self.SetColFormatFloat(i, 8, 4)
        #self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.AlterSaveStatus)
        self.Bind(wx.grid.EVT_GRID_CMD_LABEL_RIGHT_DCLICK, self.RangeSelected)
        self.wildcard = "Any File (*.*)|*.*|" \
            "SalStat Format (*.xls)|*.xls"

    def RangeSelected(self, evt):
        if evt.Selecting():
            self.tl = evt.GetTopLeftCoords()
            self.br = evt.GetBottomRightCoords()
            
    #def OnRangeChange(self, evt): #AlterSaveStatus
        ## this is activated when the user enters some data
        #self.Saved = False
        ## also record in the history file
        #col = self.GetGridCursorCol()
        #row = self.GetGridCursorRow()
        #value = self.GetCellValue(row, col)

    def CutData(self, evt):
        self.Delete()

    def CopyData(self, evt):
        self.Copy()


    def PasteData(self, evt):
        self.OnPaste()

    #def Undo(self, evt):
        #self.Undo()

    #def Redo(self, evt):
        #self.Redo()

    def EditGrid(self, evt, numrows):
        insert = self.AppendRows(numrows)

    def DeleteCurrentCol(self, evt):
        currentcol = self.GetGridCursorCol()
        self.DeleteCols(currentcol, 1)
        self.AdjustScrollbars()


    def DeleteCurrentRow(self, evt):
        currentrow = self.GetGridCursorRow()
        self.DeleteRows(currentrow, 1)
        self.AdjustScrollbars()

    def SelectAllCells(self, evt):
        self.SelectAll()

    # adds columns and rows to the grid
    def AddNCells(self, numcols, numrows, attr= None):
        insert = self.AppendCols(numcols)
        insert = self.AppendRows(numrows)
        if attr != None:
            for colNumber in range(self.GetNumberCols() - numcols, self.GetNumberCols(), 1):
                #self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
                self.SetColAttr( colNumber, attr)
        self.AdjustScrollbars()

    # function finds out how many cols contain data - all in a list
    #(ColsUsed) which has col #'s
    def GetUsedCols(self):
        ColsUsed = []
        colnums = []
        dat = ''
        tmp = 0
        for i in range(self.GetNumberCols()):
            for j in range(self.GetNumberRows()):
                dat = self.GetCellValue(j, i)
                if dat != '':
                    tmp += 1
            if tmp > 0:
                ColsUsed.append(self.GetColLabelValue(i))
                colnums.append(i)
                tmp = 0
        return ColsUsed, colnums

    def GetColsUsedList(self):
        colsusedlist = []
        for i in range(self.GetNumberCols()):
            try:
                tmp = float(self.GetCellValue(0,i))
                colsusedlist.append(i)
            except ValueError:
                colsusedlist.append(0)
        return colsusedlist

    def GetUsedRows(self):
        RowsUsed = []
        for i in range(self.GetNumberCols()):
            if (self.GetCellValue(0, i) != ''):
                for j in range(self.GetNumberRows()):
                    if (self.GetCellValue(j,i) == ''):
                        RowsUsed.append(j)
                        break
        return RowsUsed

    def SaveXlsAs(self, evt):
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
                               "Excel (*.xls)|*.xls| \
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
            totalResult = self.getByColumns(maxRow = max(rows))
            result= list()
            # reporting the header
            allColNames= [self.GetColLabelValue(col) for col in range(self.NumberCols) ]
            for posCol in range(waste[-1]+1):
                header= [  ]
                if posCol in waste:
                    header.append(allColNames[posCol])
                    header.extend(totalResult[posCol])
                else:
                    pass
                result.append(header)
            self.reportObj.writeByCols(result, self.NumSheetReport)
        self.reportObj.save()
        self.Saved = True
        self.log.write("The file %s was successfully saved!" % self.reportObj.path)


    def LoadXls(self, evt):
        dlg = wx.FileDialog(self, "Load Data File", "","",
                            wildcard= "Excel File (*.xls)|*.xls",
                            style = wx.OPEN)
                #, wx.OPEN)
        icon = imagenes.logo16()
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
        bt1= ('Choice',     [sheetNames])
        bt2= ('StaticText', ['Select a sheet to be loaded'])
        bt3= ('CheckBox',   ['Has header'])
        setting = {'Title': 'Select a sheet one'}
        
        dlg = dialog(self, struct=[[bt1,bt2],[bt3]], settings= setting)
        if dlg.ShowModal() != wx.ID_OK:
            return
        (sheetNameSelected, hasHeader)= dlg.GetValue()
        sheetNameSelected= sheetNameSelected[0]
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
        self.ClearGrid()
        size = (self.NumberRows, self.NumberCols)
        # se lee el tamanio de la pagina y se ajusta las dimensiones
        newSize = (sheetSelected.nrows, sheetSelected.ncols)
        if newSize[0]-size[0] > 0:
            self.AppendRows(newSize[0]-size[0])

        if newSize[1]-size[1] > 0:
            self.AppendCols(newSize[1]-size[1])

        # se escribe los datos en el grid
        DECIMAL_POINT= wx.GetApp().DECIMAL_POINT
        star= 0
        if hasHeader:
            star= 1
            for col in range( newSize[1]):
                header= sheetSelected.cell_value(0, col)
                if header != u'':
                    self.SetColLabelValue(col, sheetSelected.cell_value(0, col))
        
        if hasHeader and newSize[0] < 2:
            return
        
        for reportRow, row in enumerate(range( star, newSize[0])):
            for col in range( newSize[1]):
                newValue = sheetSelected.cell_value( row, col)
                if isinstance( newValue, (str, unicode)):
                    self.SetCellValue( reportRow, col, newValue)
                elif sheetSelected.cell_type( row, col) in (2,3):
                    self.SetCellValue( reportRow, col, str( newValue).replace('.', DECIMAL_POINT))
                else:
                    try:
                        self.SetCellValue (reportRow, col, str(newValue))
                    except:
                        self.log.write( "Could not import the row,col (%i,%i)" % (row+1,col+1))

    def getData(self, x):
        for i in range(len(x)):
            try:
                row = int(x[i].attributes["row"].value)
                col = int(x[i].attributes["column"].value)
                datavalue = float(self.getText(x[i].childNodes))
                self.SetCellValue(row, col, str(datavalue))
            except ValueError:
                print "Problem importing the xml"

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
        dp= wx.GetApp().DECIMAL_POINT
        if dp == '.':
            for i in range(self.GetNumberRows()):
                datapoint = self.GetCellValue(i, col).strip()
                if (datapoint != u'') and (datapoint != u'.'):
                    try:
                        value = float(datapoint)
                        if (value != missingvalue):
                            indata.append(value)
                        else:
                            self.missing = self.missing + 1
                    except ValueError:
                        pass
        else:
            for i in range(self.GetNumberRows()):
                datapoint = self.GetCellValue(i, col).strip().replace(dp, '.')
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
    
    def _cleanData(self, data):
        if isinstance(data, (str, unicode)):
            data= [data]
            
        if not isiterable(data):
            raise TypeError('Only iterable data allowed!')
        
        for pos in range(len(data)-1, -1, -1):
            if data[pos] != u'':
                break
        
        data= data[:pos+1]
        # changing data into a numerical value
        dp = wx.GetApp().DECIMAL_POINT
        result= list()
        for dat in data:
            if dat == u'':
                dat = None
            else:
                try:
                    dat= float(dat.replace(dp, '.'))
                except:
                    pass
                
            result.append(dat)
        return result
    
    def GetCol(self, col):
        return self._cleanData( self._getCol( col))
    
    def PutCol(self, colNumber, data):
        return self.putCol(colNumber, data)
    
    def GetEntireDataSet(self, numcols):
        """Returns the data specified by a list 'numcols' in a Numeric
        array"""
        biglist = []
        for i in range(len(numcols)):
            smalllist = wx.GetApp().frame.grid.CleanData(numcols[i])
            biglist.append(smalllist)
        return numpy.array((biglist), numpy.float)

#---------------------------------------------------------------------------
# base class for getting number of columns/rows to add
class EditGridFrame(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Change Grid Size", \
                           size=(205, 100+wind))
        icon = imagenes.logo16()
        self.SetIcon(icon)
        l1 = wx.StaticText(self, -1, 'Add Columns',pos=(10,15))
        l2 = wx.StaticText(self, -1, 'Add Rows',pos=(10,55))
        self.numnewcols = wx.SpinCtrl(self, -1, "", wx.Point(110,10), wx.Size(80,25))
        self.numnewcols.SetRange(1, 5000)
        self.numnewcols.SetValue(0)
        self.numnewRows = wx.SpinCtrl(self, -1, "", wx.Point(110, 50), wx.Size(80,25))
        self.numnewRows.SetRange(1, 5000)
        self.numnewRows.SetValue(0)
        okaybutton = wx.Button(self, wx.ID_ANY, "Okay", wx.Point(10, 90))
        cancelbutton = wx.Button(self, wx.ID_ANY, "Cancel", wx.Point(110,90))
        self.Bind(wx.EVT_BUTTON, self.OkayButtonPressed, id = okaybutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.CancelButtonPressed, id= cancelbutton.GetId())

    def OkayButtonPressed(self, evt):
        colswanted = self.numnewcols.GetValue()
        rowswanted = self.numnewRows.GetValue()
        editorRederer= wx.GetApp().frame.floatCellAttr
        wx.GetApp().frame.grid.AddNCells(colswanted, rowswanted, attr= editorRederer)
        self.Close(True)

    def CancelButtonPressed(self, evt):
        self.Destroy()

#---------------------------------------------------------------------------
# grid preferences - set row & col sizes
class GridPrefs(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, "Cell Size", \
                           size=(205,100+wind))
        icon = imagenes.logo16()
        self.SetIcon(icon)
        self.colwidth = wx.SpinCtrl(self, -1, "", wx.Point(110,10), wx.Size(80,25))
        self.colwidth.SetRange(1,200)
        self.colwidth.SetValue(wx.GetApp().frame.grid.GetDefaultColSize())
        self.rowheight= wx.SpinCtrl(self, -1, "", wx.Point(110,50), wx.Size(80,25))
        self.rowheight.SetRange(1,100)
        self.rowheight.SetValue(wx.GetApp().frame.grid.GetDefaultRowSize())
        l1 = wx.StaticText(self, -1, 'Column Width:',pos=(10,15))
        l2 = wx.StaticText(self, -1, 'Row Height:',pos=(10,55))
        self.okaybutton = wx.Button(self, 321, "Okay", wx.Point(10, 90))
        self.cancelbutton = wx.Button(self, 322, "Cancel", wx.Point(110,90))
        self.Bind(wx.EVT_BUTTON, self.OkayButtonPressed, id = self.okaybutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCloseGridPrefs, id = self.cancelbutton.GetId())

    def OkayButtonPressed(self, evt):
        wx.GetApp().frame.grid.SetDefaultColSize(self.colwidth.GetValue(), True)
        wx.GetApp().frame.grid.SetDefaultRowSize(self.rowheight.GetValue(), True)
        wx.GetApp().frame.grid.ForceRefresh()
        self.Close(True)

    def OnCloseGridPrefs(self, evt):
        self.Close(True)

#---------------------------------------------------------------------------
# user can change settings like variable names, decimal places, missing no.s
# using a SimpleGrid Need evt handler - when new name entered, must be
#checked against others so no match each other

class VariablesFrame(wx.Dialog):
    def __init__(self,parent,id):
        wx.Dialog.__init__(self, parent,id,"SalStat - Variables", \
                           size=(500,190+wind))

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
        maxcols = wx.GetApp().frame.grid.GetNumberCols()
        self.vargrid.CreateGrid(3,maxcols)
        for i in range(maxcols):
            oldlabel = wx.GetApp().frame.grid.GetColLabelValue(i)
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
    def OnOkayVariables(self, evt):
        for i in range(wx.GetApp().frame.grid.GetNumberCols()-1):
            newlabel = self.vargrid.GetCellValue(0, i)
            if (newlabel != ''):
                wx.GetApp().frame.grid.SetColLabelValue(i, newlabel)
            newsig = self.vargrid.GetCellValue(1, i)
            if (newsig != ''):
                try:
                    wx.GetApp().frame.grid.SetColFormatFloat(i, -1, int(newsig))
                except ZeroDivisionError:
                    pass
        wx.GetApp().frame.grid.ForceRefresh()
        self.Close(True)

    def OnCloseVariables(self, evt):
        self.Close(True)

#---------------------------------------------------------------------------
# user selects which cols to analyse, and what stats to have
class DescriptivesFrame(wx.Dialog):
    def __init__( self, parent, id ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY,
                             title = "Descriptive Statistics",
                             pos = wx.DefaultPosition, size = wx.Size( 375,326 ),
                             style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        icon = imagenes.logo16()
        self.SetIcon(icon)
        ColumnList, self.colnums  = wx.GetApp().frame.grid.GetUsedCols()

        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        self.DescChoice = CheckListBox(self, wx.ID_ANY,  wx.DefaultPosition, wx.DefaultSize, DescList, 0 )
        self.m_mgr.AddPane( self.DescChoice, wx.aui.AuiPaneInfo() .Center() .
                            Caption( u"Select Descriptive Statistics" ).CloseButton( False ).
                            PaneBorder( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).BottomDockable( False ).TopDockable( False ) )

        self.ColChoice = CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, ColumnList, 0 )
        self.m_mgr.AddPane( self.ColChoice, wx.aui.AuiPaneInfo() .Center() .Caption( u"Select Column(s) to Analyse" ).
                            CloseButton( False ).PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.Size( 161,93 ) ).DockFixed( False ).BottomDockable( False ).
                            TopDockable( False ).Row( 1 ).Layer( 0 ) )

        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel1, wx.aui.AuiPaneInfo() .Bottom() .CaptionVisible( False ).
                            CloseButton( False ).PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ).LeftDockable( False ).
                            RightDockable( False ).MinSize( wx.Size( -1,30 ) ) )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        okaybutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Ok", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT  )
        bSizer2.Add( okaybutton, 0, wx.ALL, 5 )

        cancelbutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT  )
        bSizer2.Add( cancelbutton, 0, wx.ALL, 5 )

        self.m_panel1.SetSizer( bSizer2 )
        self.m_panel1.Layout()
        bSizer2.Fit( self.m_panel1 )

        self.m_mgr.Update()
        self.Centre( wx.BOTH )

        self.Bind(wx.EVT_BUTTON, self.OnOkayButton,          id = okaybutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCloseContDesc,       id = cancelbutton.GetId())
   
    def OnOkayButton(self, evt):
        descs = []
        for i in range(len(self.colnums)):
            if self.ColChoice.IsChecked(i):
                realColi = self.colnums[i]
                name = wx.GetApp().frame.grid.GetColLabelValue(realColi)
                descs.append(statistics(
                    wx.GetApp().frame.grid.CleanData(realColi), name,
                    wx.GetApp().frame.grid.missing))
        ManyDescriptives(self, descs)
        self.Close(True)

    def OnCloseContDesc(self, evt):
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
        icon = imagenes.logo16()
        self.SetIcon(icon)
        self.transform = ""
        self.transformName = ""
        self.ColumnList, self.colnums = wx.GetApp().frame.grid.GetUsedCols()
        self.cols = wx.GetApp().frame.grid.GetNumberCols()
        l0 = wx.StaticText(self,-1,"Select Column(s) to Transform",pos=(10,10))
        self.ColChoice = wx.CheckListBox(self,1102, wx.Point(10,30), \
                                         wx.Size(230,(winheight * 0.8)), self.ColumnList)
        self.okaybutton = wx.Button(self, wx.ID_ANY, "Okay",wx.Point(10,winheight-35))
        self.cancelbutton = wx.Button(self, wx.ID_ANY, "Cancel",wx.Point(100,winheight-35))
        # common transformations:
        l1 = wx.StaticText(self, -1, "Common Transformations:", pos=(250,30))
        self.squareRootButton = wx.Button(self, wx.ID_ANY, "Square Root", wx.Point(250, 60))
        self.logButton = wx.Button(self, wx.ID_ANY, "Logarithmic",wx.Point(250, 100))
        self.reciprocalButton = wx.Button(self, wx.ID_ANY, "Reciprocal", wx.Point(250,140))
        self.squareButton = wx.Button(self, wx.ID_ANY, "Square", wx.Point(250,180))
        l2 = wx.StaticText(self, -1, "Function :", wx.Point(250, 315))
        self.transformEdit = wx.TextCtrl(self, 1114,pos=(250,335),size=(150,20))
        self.Bind(wx.EVT_BUTTON, self.OnOkayButton,        id = self.okaybutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCloseFrame,        id = self.cancelbutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.squareRootTransform, id = self.squareRootButton.GetId())
        self.Bind(wx.EVT_BUTTON, self.logTransform,        id = self.logButton.GetId())
        self.Bind(wx.EVT_BUTTON, self.reciprocalTransform, id = self.reciprocalButton.GetId())
        self.Bind(wx.EVT_BUTTON, self.squareTransform,     id = self.squareButton.GetId())

    def squareRootTransform(self, evt):
        self.transform = "math.sqrt(x)"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Square Root"

    def logTransform(self, evt):
        self.transform = "math.log(x)"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Logarithm"

    def reciprocalTransform(self, evt):
        self.transform = "1 / x"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Reciprocal"

    def squareTransform(self, evt):
        self.transform = "x * x"
        self.transformEdit.SetValue(self.transform)
        self.transformName = " Square"

    def OnOkayButton(self, evt):
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
                oldcol = wx.GetApp().frame.grid.CleanData(newColi)
                newcol = [0]*len(oldcol)
                for j in range(len(oldcol)):
                    x = oldcol[j]
                    try:
                        newcol[j] = eval(self.transform)
                    except: # which exception would this be?
                        pass # need to do something here.
                PutData(emptyCols[i], newcol)
                # put in a nice new heading
                oldHead = wx.GetApp().frame.grid.GetColLabelValue(self.colnums[i])
                if self.transformName == "":
                    self.transformName = ' ' + self.transform
                oldHead = oldHead + self.transformName
                wx.GetApp().frame.grid.SetColLabelValue(emptyCols[i], oldHead)
                emptyCols.pop(emptyCols[i])
        self.Close(True)

    def OnCloseFrame(self, evt):
        self.Close(True)

class formulaBar ( wx.Panel ):

    def __init__( self, parent , *args,**params):
        wx.Panel.__init__ ( self, parent, *args, **params)

        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
        self.m_textCtrl1 = wx.TextCtrl( self, wx.ID_ANY,
                                        wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                        wx.TE_CHARWRAP|wx.TE_MULTILINE|wx.TE_RICH2|
                                        wx.TE_WORDWRAP|wx.NO_BORDER )

        self.m_textCtrl1.SetMinSize( wx.Size( 220,25 ) )
        bSizer1.Add( self.m_textCtrl1, 0, 0, 5 ) # wx.EXPAND

        #self.m_button1 = wx.Button( self, wx.ID_ANY, u">>",
    #                    wx.DefaultPosition, wx.DefaultSize,
    #                    wx.BU_EXACTFIT|wx.DOUBLE_BORDER )
        #bSizer1.Add( self.m_button1, 0, wx.EXPAND, 5 )
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
    exc.insert(0, "*** %s ***%s" % (now(), os.linesep))
    return "".join(exc)


class SalStat2App(wx.App):
    # the main app
    def OnInit(self):
        # getting the os type
        self.OSNAME = os.name
        self.VERSION= '2.1 alpha'
        wx.SetDefaultPyEncoding("utf-8")
        self.SetAppName(APPNAME)
        try:
            installDir = os.path.dirname(os.path.abspath(__file__))
        except:
            installDir = os.path.dirname(os.path.abspath(sys.argv[0]))

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
        #< help data
        from wx.html import HtmlHelpData
        path= os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], 'help'))
        fileName= os.path.join(path, "help.hhp")
        self.HELPDATA= HtmlHelpData()
        self.HELPDATA.AddBook(fileName)
        # help data />
        self.icon= imagenes.logo16()
        self.icon64= imagenes.logo64()
        self.frame = MainFrame(None, self)
        # let the main app known the input Grid
        self.inputGrid = self.frame.grid
        self.SetTopWindow(self.frame)
        self.frame.grid.SetFocus()
        self.Logg= self.frame.logPanel
        self.output = self.frame.answerPanel
        # referencing the plot system
        self.plot = plot
        self.frame.ShowFullScreen(True,False)
        return True

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
# call instance of DataGrid
# This is main interface of application
class MainFrame(wx.Frame):
    def __init__(self, parent, appname ):
        self.path= None
        wx.Frame.__init__(self,parent,-1,"SalStat Statistics",
                          size = wx.Size(640,480 ), pos = wx.DefaultPosition)

        self.m_mgr= aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        #set icon for frame (needs x-platform separator!
        self.Icon= appname.icon
        self.DECIMAL_POINT= appname.DECIMAL_POINT
        #----------------------
        # create toolbars
        tb1= self._createTb1()
        self.formulaBarPanel= formulaBar(self,wx.ID_ANY)
        #------------------------
        # create small status bar
        self.StatusBar= self.CreateStatusBar(3)
        self.StatusBar.SetStatusText('SalStat 2',0)
        self.StatusBar.SetStatusText('cells Selected:   '+'count:      '+'sum:    ',1 )
        self.StatusBar.SetStatusText('none',2)

        self.m_notebook1= wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.logPanel= LogPanel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )

        self.defaultDialogSettings = {'Title': None,
                                      'icon': imagenes.logo16()}

        #--------------------
        #< set up the datagrid
        self.grid= SimpleGrid(self, self.logPanel, size = (500,50))
        # let />
        self.grid.Saved= False
        self.grid.SetDefaultColSize( 60, True)
        self.grid.SetRowLabelSize( 40)
        self.grid.SetDefaultCellAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTER )
        ## adjust the renderer 
        attr=   wx.grid.GridCellAttr()
        editor= wx.grid.GridCellFloatEditor()
        attr.SetEditor(editor)
        renderer = floatRenderer( 4)
        attr.SetRenderer( renderer)
        self.floatCellAttr= attr
        for colNumber in range( self.grid.NumberCols):
            self.grid.SetColAttr( colNumber, self.floatCellAttr)
        #-----------------------
        # create menubar
        self._createMenu()

        # response panel
        self.answerPanel= NoteBookSheet(self, fb = self.formulaBarPanel)
        self.answerPanel2= ScriptPanel(self, self.logPanel, self.grid, self.answerPanel)
        #--------------------------------------------
        self.m_notebook1.AddPage( self.logPanel, u"Log", True )
        #--------------------------------
        #from IPython.lib.inputhook import InputHookManager
        #shell= InputHookManager()
        #shell.enable_wx(app = appname)
        self.scriptPanel= wx.py.shell.Shell(self.m_notebook1)
        self.scriptPanel.wrap(True)
        self.m_notebook1.AddPage( self.scriptPanel , u"Shell", False )

        #------------------------
        # organizing panels
        self.m_mgr.AddPane( self.formulaBarPanel,
                            aui.AuiPaneInfo().ToolbarPane().Top().Row(1).
                            Position(1).
                            LeftDockable(False).RightDockable(False).
                            MinSize( wx.Size( -1,15 ) ).CloseButton( False ) )

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
        self._BindEvents()
        self.m_mgr.Update()
        self.Center()

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
        return tb1

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
        #add contents of menu
        dat1= (
            ('&File',
             (('&New Data',   NewIcon,    self.GoClearData),
              ('&Open...',    OpenIcon,   self.grid.LoadXls),
              ('&Save',       SaveIcon,   self.grid.SaveXls),
              ('Save &As...', SaveAsIcon, self.grid.SaveXlsAs),
              ('&Print...',   PrintIcon,  None),
              ('E&xit',       ExitIcon,   self.EndApplication),
              )),
            ('&Edit',
             (('Cu&t',           CutIcon,         self.grid.CutData),
              ('&Copy',          CopyIcon,        self.grid.CopyData),
              ('&Paste',         PasteIcon,       self.grid.PasteData),
              ('Select &All',    None,            self.grid.SelectAllCells),
              ('&Find and Replace...',  FindRIcon,     self.GoFindDialog),
              ('Delete Current Column', None,  self.grid.DeleteCurrentCol),
              ('Delete Current Row',    None,  self.grid.DeleteCurrentRow),)),
            ('&Preferences',
             (('Variables...',             None,  self.GoVariablesFrame ),
              ('Add Columns and Rows...',  None,  self.GoEditGrid),
              ('Change Cell Size...',      None,  self.GoGridPrefFrame),
              ('Change the Font...',       None,  self.GoFontPrefsDialog),)),
            ('P&reparation',
             (('Descriptive Statistics',   None,  self.GoContinuousDescriptives),
              ('Transform Data',           None,  self.GoTransformData),
              ('short data',               None,  self.shortData),)),
            ('S&tatistics',
             (('Central Tendency',
               (('geometricmean', None, self.geometricmean),
                ('harmonicmean',  None, self.harmonicmean),
                ('mean',          None, self.mean),
                ('median',        None, self.median),
                ('medianscore',   None, self.medianscore),
                ('mode',          None, self.mode),)),
              ('Moments',
               (('moment',        None, self.moment),
                ('variation',     None, self.variation),
                ('skew',          None, self.skew),
                ('kurtosis',      None, self.kurtosis),
                ('skewtest',      None, self.skewtest),
                ('kurtosistest',  None, self.kurtosistest),
                ('normaltest',    None, self.normaltest),)),
              ('Frequency Stats',
               (('itemfreq',      None, self.itemfreq),
                ('scoreatpercentile',  None, self.scoreatpercentile),
                ('percentileofscore',  None, self.percentileofscore),
                ('histogram',     None, self.histogram),
                ('cumfreq',       None, self.cumfreq),
                ('relfreq',       None, self.relfreq)),),
              ('Variability',
               (( 'samplevar',    None, self.samplevar),
                ('samplestdev',   None, self.samplestdev), #'obrientransform'
                ('signaltonoise', None, self.signaltonoise),
                ('var',           None, self.var),
                ('stdev',         None, self.stdev),
                ('sterr',         None, self.sterr),
                ('sem',           None, self.sem),
                ('z',             None, self.z),
                ('zs',            None, self.zs)),), # 'zmap'
              ('Trimming Fcns',
               (('threshold',     None, self.threshold),)),#                 ('trimboth',      None, self.trimboth),                ('trim1',         None, self.trim1)),), #'round',
              ('Correlation Fcns',
               (( 'paired',       None, self.paired),
                ('pearsonr',      None, self.pearsonr),
                ('covariance',    None, self.covariance), # 'correlation'
                ('spearmanr',     None, self.spearmanr),
                ('pointbiserialr', None, self.pointbiserialr),
                ('kendalltau',    None, self.kendalltau),
                ('linregress',    None, self.linregress)),),
              ('Inferential Stats',
               (('ttest_1samp',  None, self.ttest_1samp),
                ('ttest_ind',    None, self.ttest_ind),
                ('ttest_rel',    None, self.ttest_rel),
                ('chisquare',    None, self.chisquare),
                ('ks_2samp',     None, self.ks_2samp),
                ('mannwhitneyu', None, self.mannwhitneyu),
                ('ranksums',     None, self.ranksums),
                ('wilcoxont',    None, self.wilcoxont),
                ('kruskalwallish', None, self.kruskalwallish),
                ('friedmanchisquare', None, self.friedmanchisquare)),),
              ('Probability Calcs',
               (('chisqprob',    None, self.chisqprob),
                ('erfcc',        None, self.erfcc),
                ('zprob',        None, self.zprob),   # 'ksprob'
                ('betacf',       None, self.betacf),
                ('gammln',       None, self.gammln),
                ('betai',        None, self.betai)),), # 'fprob'
              ('Anova Functions',
               (( 'F_oneway',    None, self.F_oneway),))),),
            ('Analyse',
             (('One Condition Test',      None, self.goOneConditionTest),
              ('Two Condition Test',      None, self.goTwoConditionTest),
              ('Three Condition Test',    None, self.goThreeConditionTest))),
            ('&Graph',
             (('Line Chart of All Means', None, self.GoChartWindow),
              ('Bar Chart of All Means',  None, self.GoBarChartWindow),
              ('Lines',                   None, self.GoLinesPlot),
              ('Scatter',                 None, self.GoScatterPlot),
              ('Box &Whisker',             None, self.GoBoxWhiskerPlot),
              ('Linear Regression',          None, self.GoLinRegressPlot),
              ('Ternary',                 None, self.GoTernaryplot),
              ('Probability',             None, self.GoProbabilityplot),
              ('Adaptive BMS',          None, self.GoAdaptativeBMS))),
            ('Ctrl Process',
             (('Six Sigma Pac',           sixsigma, self.GoSixPack),)),
            ('&Help',
             (('Help',       imag.about(), self.GoHelpSystem),
              ('&About...',  imag.icon16(), self.ShowAbout),)),
        )
        self.__createMenu(dat1, menuBar)
        self.SetMenuBar(menuBar)

    def __createMenu(self,data,parent):
        if len(data) == 3:
            if not isinstance(data[2], (list,tuple)):
                item= wx.MenuItem(parent, wx.ID_ANY, data[0])
                if data[1] != None:
                    item.SetBitmap(data[1])
                if data[2] != None:
                    self.Bind(wx.EVT_MENU, data[2], id= item.GetId())
                parent.AppendItem(item)
                return
        for item in data:
            if len(item) == 3:
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
        self.Bind(wx.EVT_MENU, self.grid.LoadXls,       id= self.bt2.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SaveXls,       id= self.bt3.GetId())
        self.Bind(wx.EVT_MENU, self.grid.SaveXlsAs,     id= self.bt4.GetId())
        ##self.Bind(wx.EVT_MENU, self.grid.PrintPage,    id = self.bt5.GetId())
        self.Bind(wx.EVT_MENU, self.grid.CutData,       id= self.bt6.GetId())
        self.Bind(wx.EVT_MENU, self.grid.CopyData,      id= self.bt7.GetId())
        self.Bind(wx.EVT_MENU, self.grid.PasteData,     id= self.bt8.GetId())
        self.Bind(wx.EVT_MENU, self.GoVariablesFrame,   id= self.bt9.GetId())
        self.Bind(wx.EVT_MENU, self.GoHelpSystem,       id= self.bt10.GetId())
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
        texto= self.grid.GetCellValue( row, col)
        self.formulaBarPanel.m_textCtrl1.SetValue( texto)
        evt.Skip()

    def _OnNtbDbClick(self,evt):
        for pane in self.mm_mgr.AllPanes:
            if pane.name == 'Bottom Panel':
                break
        if not pane.IsMaximized():
            self.mm_mgr.MaximizePane(pane)
        else:
            pane.MinimizeButton(True)
        
    def goOneConditionTest(self, evt):
        evt.Skip()
        
    def goTwoConditionTest(self, evt):
        evt.Skip()
        
    def goThreeConditionTest(self, evt):
        evt.Skip()
        
    def GoClearData(self, evt):
        #shows a new data entry frame
        self.grid.ClearGrid()

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
        win = EditGridFrame(wx.GetApp().frame, -1)
        win.Show(True)

    def GoVariablesFrame(self, evt):
        # shows Variables dialog
        win = VariablesFrame(wx.GetApp().frame, -1)
        win.Show(True)

    def GoGridPrefFrame(self, evt):
        # shows Grid Preferences form
        win = GridPrefs(wx.GetApp().frame, -1)
        win.Show(True)

    def GoFontPrefsDialog(self, evt):
        # shows Font dialog for the data grid (wx.GetApp().output window has its own)
        data = wx.FontData()
        dlg = wx.FontDialog(wx.GetApp().frame, data)
        icon = imagenes.logo16()
        self.SetIcon(icon)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            #data2 = data.GetChosenFont()
            self.grid.SetDefaultCellFont(data.GetChosenFont())

    def GoContinuousDescriptives(self, evt):
        # shows the continuous descriptives dialog
        win = DescriptivesFrame(wx.GetApp().frame, -1)
        win.Show(True)

    def GoTransformData(self, evt):
        win = TransformFrame(wx.GetApp().frame, -1)
        win.Show(True)

    def GoCheckOutliers(self, evt):
        pass

    def GoChartWindow(self, evt):
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
                  xtics= [waste[i] for i in selectedcols])
        plt.Show()

    def GoTernaryplot(self, evt):
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
            self.logPanel.write('You have to select 3 columns a, b, and c')
            return

        data = [self.grid.CleanData(cols) for cols in [colnums[m] for m in selectedcols]]
        tam = [len(dat) for dat in data]
        if (tam[0] != tam[1]) or (tam[0] != tam[2]):
            self.logPanel.write('The selected columns must have the same number of elements')
            return

        legend = u''
        data= [data[0], data[1], data[2], legend]

        plt= plot(parent=    self,
                  typePlot=  'plotTrian',
                  data2plot= data, 
                  title=     'Ternary Plot')
        plt.Show()

    def GoBarChartWindow(self, evt):
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

    def GoHelpSystem(self, evt):
        # shows the "wizard" in the help box
        win= Navegator(wx.GetApp().frame,)
        win.Show(True)

    def ShowAbout(self, evt):
        info= wx.AboutDialogInfo()
        info.Name= "S2 SalStat Statistics Package 2"
        info.Version= "V" + wx.GetApp().VERSION
        info.Copyright= "(C) 2012 Sebastian Lopez Buritica"
        info.Icon= wx.GetApp().icon64
        from wx.lib.wordwrap import wordwrap
        info.Description = wordwrap(
            "This is a newer version of the SalStat Statistics Package "
            "originally developed by Alan James Salmoni and Mark Livingstone. "
            "There have been minor bug corrections, and new improvements: "
            "You can cut, copy, and paste multiple cells,"
            "You can undo and redo some actions. "
            "The calculations are faster than the original version. "
            "The plot system can draw:"
            "Scatter charts, line chart of all means, bar chart of all means,"
            "Line charts of the data, box and whisker chart,"
            "Linear regression plot (show the equation and the correlation inside the chart),"
            "and much more!\n"
            "The input data can be saved to, and loaded from an xls format file.\n"
            "Salstat2 can be scripted by using Python.\n"
            "All the numerical results are send to a sheet in a different panel where you can cut, copy, paste, and edit them.",
            400, wx.ClientDC(self))
        info.WebSite = ("http://code.google.com/p/salstat-statistics-package-2/", "S2 home page")
        info.Developers = [ "Sebastian Lopez Buritica",
                            "Mark Livingstone",]

        info.License = wordwrap("GPL 2", 500, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)
        
    def GoScatterPlot(self,evt):
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
            self.SetStatusText('X and Y data must have the same number of elements!')
            return
        plt= plot(parent = self, typePlot= 'plotScatter',
                  data2plot= ((data[0],data[1],waste[xcol] +u' Vs '+ waste[ycol]),),
                  xlabel= waste[xcol],
                  ylabel= waste[ycol],
                  title= 'Scatter Plot')
        plt.Show()

    def GoBoxWhiskerPlot(self,evt):
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
                  title= 'Box & whisker plot',
                  xtics=  [waste[i] for i in selectedcols] )

        plt.Show()
    def GoAdaptativeBMS(self,evt):
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
        data= [self.grid.CleanData(cols) for cols in [colnums[m] for m in selectedcols]]
        plt= plot(parent = self,
                  typePlot = 'AdaptativeBMS',
                  data2plot = data,
                  xlabel = 'variable',
                  ylabel = 'value',
                  title= 'Adaptative BMS plot',
                  xtics=  [waste[i] for i in selectedcols])
        plt.Show()

    def GoLinesPlot(self, evt):
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

    def GoLinRegressPlot(self, evt):
        waste, colnums = self.grid.GetUsedCols()
        if colnums == []:
            self.SetStatusText('You need some data to draw a graph!')
            return
        selection = selectDialogData2plot(self,waste)
        if selection.ShowModal() != wx.ID_OK:
            selection.Destroy()
            return
        (xcol, ycol) = selection.getData()
        selection.Destroy()
        data = [self.grid.CleanData(cols) for cols in [colnums[i] for i in (xcol,ycol)]]
        # homogenize data
        data= homogenize(data[0],data[1])

        if len(data[0]) != len(data[1]):
            self.SetStatusText('X and Y data must have the same number of elements!')
            return
        plt= plot(parent = self, typePlot= 'plotLinRegress',
                  data2plot= (data[0],data[1],waste[xcol] +u' Vs '+ waste[ycol]),
                  xlabel = waste[xcol], ylabel = waste[ycol],
                  title= 'Linear Regression plot' )
        plt.Show()
        # lin regress removing most disperse data


    def GoProbabilityplot(self, evt):
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

    def GoSixPack(self, evt):
        '''six pack for continue data
        references:
        1) http://en.wikipedia.org/wiki/Process_capability_index
        2) http://en.wikipedia.org/wiki/Shewhart_individuals_control_chart
        3) http://www.statisticalprocesscontrol.info/glossary.html
        4) http://www.isixsigma.com/tools-templates/capability-indices-process-capability/process-capability-cp-cpk-and-process-performance-pp-ppk-what-difference/'''
        
        #####
        colValues = self.grid.GetCol('D')
        #####
        ColumnList, colnums = wx.GetApp().frame.grid.GetUsedCols()
        if len(ColumnList) == 0:
            return
        dlg= SixSigma(self, ColumnList)
        if dlg.ShowModal() == wx.ID_OK:
            (ColSelect, UCL, LCL, Target, k, groupSize) = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # -------------------
        # changing value strings to numbers
        if len(ColSelect) == 0:
            self.logPanel.write("You haven't selected a column!")
            return

        # taking the data
        values= [ [pos for pos, value in enumerate( ColumnList )
                   if value == val
                   ][0]
                  for val in ColSelect
                  ]
        columns= list()
        for pos in values:
            col = numpy.array(GetData(colnums[ pos ]))
            #col.shape = (len(col),1)
            columns.append(col)

        if len(ColSelect) == 1:
            result= self._sixpack(columns[0], UCL, LCL, Target, k, n= groupSize)
        else:
            # group homogenization in order to 
            # obtain comparable data
            columns= homogenize(*columns)
            # get the size of the group
            groupSize= len(ColumnList)
            # calculating the averages, ranges and standard deviations
            from scipy import stats
            rows= [[columns[pos][fil] for pos in range(len(columns))]
                   for fil in range(len(columns[0]))]
            del columns
            averages= [statistics(row).mean for row in rows]
            ranges= [max(row)-min(row) for row in rows]
            stddevs= [statistics(row).stddev for row in rows]

            Xga= statistics(averages).mean
            Ra= statistics(ranges).mean
            Sa= statistics(stddevs).mean

            # x-bar limits using Ra
            UCL_xbar= Xga + A2[groupSize]*Ra
            LCL_xbar= Xga - A2[groupSize]*Ra

            # R_ chart limits
            UCL_rchart= D4[groupSize]*Ra
            LCL_rchary= D3[groupSize]*Ra

            # S_chart limits
            UCL_schart= B4[groupSize]*Sa
            LCL_schart= B3[groupSize]*Sa

            columns= [numpy.array(averages)]

        for data in columns:
            result= self._sixpack(data, UCL, LCL, Target, k, n= groupSize)
            description= {'Desv.Est': 'Standard Deviation',
                          'Cp':  'Process Capability. A simple and straightforward indicator of process capability.',
                          'Pp':  'Process Performance. A simple and straightforward indicator of process performance. basically tries to verify if the sample that you have generated from the process is capable to meet Customer CTQs (requirements)',
                          'Cpk': 'Process Capability Index. Adjustment of Cp for the effect of non-centered distribution. measures how close a process is running to its specification limits, relative to the natural variability of the process',
                          'Ppk': 'Process Performance Index. Adjustment of Pp for the effect of non-centered distribution.',
                          'Cpm': 'Estimates process capability around a target, it is also known as the Taguchi capability index',
                          'ppm': 'In a quality control context, PPM stands for the number of parts per million (cf. percent) that lie outside the tolerance limits'}

            general= {'Desv.Est': round(result['stddev'],5),
                      'Pp':       round(result['Cp'],5),
                      'Ppk':      round(result['Cpk'],5),
                      'Cpm':      round(result['Cpm'],5),
                      'ppm':      int(result['ppm']),}
            LCU=    result['LCU']
            LCI=    result['LCL']
            # se muestra los resultados
            wx.GetApp().output.addColData('Input Data',pageName= 'SixSigma')
            wx.GetApp().output.addColData(('UCL','LCL','target','k','group size'))
            wx.GetApp().output.addColData((UCL, LCL, Target, k, groupSize))
            wx.GetApp().output.addColData('selcted columns',)
            wx.GetApp().output.addColData(ColSelect)
            keys= list()
            desc= list()
            values= list()
            for key,value in general.items():
                keys.append(key)
                desc.append(description[key])
                values.append(value)
            wx.GetApp().output.addColData(desc)
            wx.GetApp().output.addColData(keys)
            wx.GetApp().output.addColData(values)
            wx.GetApp().output.addColData(('xbar chart Limits'))
            wx.GetApp().output.addColData(('LCU','LCI'))
            wx.GetApp().output.addColData((LCU, LCI))
            #wx.GetApp().output.addColData('inside Potential')
            #wx.GetApp().output.addColData(inside.keys())
            #wx.GetApp().output.addColData(inside.values())
        # control process chart
        data2plot= {'UCL':     UCL,
                    'LCL':     LCL,
                    'target':  Target,
                    'data':    data,
                    }
        plt= plot(self,    'controlChart', data2plot,
                  title=   "Control Chart",
                  xlabel=   ColSelect[0],
                  ylabel=   ColSelect[0] + " Value")
        plt.Show()
        # normal probability chart
        pltNorm= plot(self, 'probabilityPlot', [data],
                      title=   "Normal probability plot",
                      )
        pltNorm.Show()
        # x-bar chart:
        xbar_data= (data[1:]+data[:-1])/2.0
        xbar_UCL=  Xga + A2[groupSize]*Ra
        xbar_LCL=  Xga - A2[groupSize]*Ra
        xbar_target= Xga
        data2plot= {'UCL':     xbar_UCL,
                    'LCL':     xbar_LCL,
                    'target':  xbar_target,
                    'data':    data,
                    }
        pltXbar= plot(self,    'controlChart', data2plot,
                      title=   "X-bar Chart",
                      xlabel=   ColSelect[0],
                      ylabel=   ColSelect[0] + " Value")
        pltXbar.Show()
        # r-chart:
        rchart_UCL= D4[groupSize]*Ra
        rchart_LCL= D3[groupSize]*Ra
        rchart_target= Ra
        # s-chart:
        schart_UCL= B4[groupSize]*Ra
        schart_LCL= B3[groupSize]*Ra
        schart_target= Sa

        self.logPanel.write('SixSigma' + ' successful')

    def _sixpack(self, data, UCL, LCL, Target, k= 6, n= 2 ):
        result= dict()
        stadis= statistics(data)
        stddev = stadis.stddev
        if stddev == 0:
            wx.GetApp().Logg.write('Six pack analysis fail because the stddev is zero')
            return

        if UCL == None:
            UCL= stadis.mean+ 0.5*k*stadis.stddev

        if LCL == None:
            LCL= stadis.mean- 0.5*k*stadis.stddev

        if Target == None:
            Target= stadis.mean

        if UCL <= LCL:
            wx.GetApp().Logg.write('Six pack analysis fail because LCL >= UCL  %f >= %f'%(LCL, UCL))
            return

        mean=     stadis.mean
        Cp=       (UCL-LCL)/float(k*stddev)
        Cpl=      2*(mean-LCL)/float(k*stddev)
        Cpu=      2*(UCL-mean)/float(k*stddev)
        Cpk=      min(Cpu, Cpl)
        va1=      (mean-Target)/float(stddev)
        val2=     math.sqrt(1+va1**2)
        val3=     Cp/float(val2)
        Cpm=      Cp/float(math.sqrt(1+((mean-Target)/float(stddev))**2))
        zUCL=     (UCL - mean)/float(stddev)
        zLCL=     (mean - LCL)/float(stddev)
        outOfUCL= sum([1 for x in data if x > UCL])
        outOfLCL= sum([1 for x in data if x < LCL])
        probUCL=  1 - normProb(zUCL)
        probLCL=  1 - normProb(zLCL)
        probTot=  probLCL + probUCL
        ppm=      int(probTot*1e6)
        sigmaLevel= normProbInv(1-probTot)+1.5

        # data for xbar chart
        mir= list()
        for x,y in zip(data[1:],data[:-1]):
            mir.append(abs(x-y))
        newData=       numpy.array(mir)
        rangeNewData=  max(newData)- min(newData)
        LCU=    stadis.mean+ A2[n]*rangeNewData
        LCL=    stadis.mean- A2[n]*rangeNewData

        for paramName, value in zip(['stddev', 'mean', 'Cp', 'Cpl', 'Cpu','Cpk',
                                     'zUCL', 'zLCL', 'probUCL', 'probLCL',
                                     'probTot', 'ppm', 'sigmaLevel', 'outOfUCL',
                                     'outOfLCL','Cpm','LCU','LCL',],
                                    [stddev, mean, Cp, Cpl, Cpu, Cpk, zUCL, zLCL,
                                     probUCL, probLCL, probTot, ppm, sigmaLevel,
                                     outOfUCL, outOfLCL, Cpm, LCU, LCL ]):
            result[paramName] = value
        return result


    def EndApplication(self, evt):
        if self.grid.Saved == False:
            win = SaveDialog(self)
            win.Show(True)
        else:
            wx.GetApp().frame.Destroy()
#------------------------------------------
# definicion de las funciones estadisticas
#------------------------------------------
    def _statsType1(self, functionName, grid, useNumpy = True,
                    requiredcols= None,allColsOneCalc = False,
                    nameResults= None, dataSquare= False, *args, **params):
        try:
            requiredcols= params.pop('requiredcols')
        except KeyError:
            requiredcols= None
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = grid.GetUsedCols()
        bt1= ['StaticText', ('Select the columns to analyse',) ]
        bt2= ['CheckListBox', (ColumnList,)]
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
            self.logPanel.write("You haven't selected any items!")
            return

        if len(colNameSelect) < requiredcols:
            self.logPanel.write("Uou have to select at least %i columns"%requiredcols)
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
                return "The data must have the same dimensions!"

        if allColsOneCalc:
            result = getattr(stats, functionName)( *colums )
        else:
            # se hace los calculos para cada columna
            result = [getattr(stats, functionName)( col ) for col in colums]

        # se muestra los resultados
        if nameResults == None:
            wx.GetApp().output.addColData(colNameSelect, functionName)
        else:
            wx.GetApp().output.addColData(nameResults, functionName)
        if functionName in ['kurtosis','kurtosistest','skewtest',
                            'normaltest','mode']:
            opt = False
            try:
                len(result[0])
            except:
                opt = True

            if opt:
                wx.GetApp().output.addColData(result)
            else:
                for i in range(len(result[0])):
                    res1= [res[i] for res in result]
                    wx.GetApp().output.addColData(res1)

        else:
            wx.GetApp().output.addColData(result)

        self.logPanel.write(functionName + ' successful')

    def _statsType2(self, functionName, texto = 'moment',spinData= (1,100,1),
                    factor = 1, useNumpy = True, nameResults= None):
        ''''select plus spin crtl'''
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()
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
            self.logPanel.write("You haven't selected any items!")
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
        wx.GetApp().output.addColData(colNameSelect, functionName)
        if nameResults != None:
            wx.GetApp().output.addColData(nameResults)
        wx.GetApp().output.addColData(numpy.ravel(result))
        self.logPanel.write(functionName + ' successful')

    def _statsType3(self, functionName, texto1 = u'',
                    texto2 = u'', **params):
        try:
            useNumpy= params.pop('useNumpy')
        except:
            useNumpy= False

        try:
            nameCols= params.pop('nameCols')
        except:
            nameCols= None

        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't selected any items!")
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
            wx.GetApp().output.addColData(nameCols, functionName)
            wx.GetApp().output.addColData(result)
        else:
            wx.GetApp().output.addColData(result, functionName)
        self.logPanel.write(functionName + ' successful')


    def shortData(self,evt):
        functionName = "short"
        useNumpy = False
        requiredcols= None
        allColsOneCalc = False,
        dataSquare= False
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
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
        self.logPanel.write(functionName + ' successful')


    def geometricmean(self,evt):
        geometricMean().showGui()

    def harmonicmean(self,evt):
        harmonicmean().showGui()
        #self._statsType1("harmonicmean", self.grid)

    def mean(self,evt):
        mean().showGui()

    def median(self,evt):
        median().showGui()

    def medianscore(self,evt):
        medianscore().showGui()

    def mode(self,evt):
        mode().showGui()

    def moment(self,evt):
        self._statsType2("scoreatpercentile", texto = 'moment',
                         spinData = (1,100,1))

    def variation(self,evt):
        self._statsType1("variation", self.grid)

    def skew(self,evt):
        self._statsType1("skew", self.grid)

    def kurtosis(self,evt):
        self._statsType1("kurtosis", self.grid)

    def skewtest(self,evt):
        self._statsType1("skewtest", self.grid, useNumpy = False)

    def kurtosistest(self,evt):
        self._statsType1("kurtosistest", self.grid, useNumpy = False)

    def normaltest(self,evt):
        self._statsType1("normaltest", self.grid, useNumpy = True)

    def itemfreq(self,evt):
        functionName = "itemfreq"
        useNumpy = True
        requiredcols= None
        allColsOneCalc = False,
        dataSquare= False
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()
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
            colums = [ stats.shellsort(GetData(colnums[ pos ]))[0] for pos in values]

        if dataSquare:
            # identifica que las columnas seleccionadas deben tener igual
            #  cantidad de elementos
            lendata= [len(col) for col in colums]
            if sum([1 for leni in lendata if leni == lendata[0]]) <> len(colums):
                return "The data must have the same dimensions"

        if allColsOneCalc:
            result = getattr(stats, functionName)( *colums )
        else:
            # se hace los calculos para cada columna
            result = [getattr(stats, functionName)( col ) for col in colums]

        # se muestra los resultados
        wx.GetApp().output.addColData(colNameSelect, functionName)

        for i in range(len(result[0])):
            res1= [res[i] for res in result]
            wx.GetApp().output.addColData(res1)

        self.logPanel.write(functionName + ' successful')



    def scoreatpercentile(self,evt):
        self._statsType2("scoreatpercentile", texto = ' %',
                         spinData = (0,100,0))

    def percentileofscore(self,evt):
        #adiconar dos parametros pendientes
        self._statsType2("scoreatpercentile", texto = 'Score',)

    def histogram(self,evt):
        #adiconar dos parametros pendientes
        self._statsType2("histogram", texto = 'number of bins',
                         spinData = (1,100,10))

    def cumfreq(self,evt):
        #adiconar un parametro pendiente
        self._statsType2("cumfreq", texto = 'number of beans' )

    def relfreq(self,evt):
        #adiconar un parametro pendiente
        self._statsType2("relfreq", texto = 'number of bins',
                         spinData = (1,100,10))

    #def obrientransform(self,evt):
    #    self.logPanel.write('obrientransform')

    def samplevar(self,evt):
        self._statsType1("samplevar", self.grid)

    def samplestdev(self,evt):
        self._statsType1("samplestdev", self.grid)

    def signaltonoise(self,evt):
        self._statsType2("signaltonoise", texto = 'dimension',
                         spinData = (0,100,0))

    def var(self,evt):
        self._statsType1("var", self.grid)

    def stdev(self,evt):
        self._statsType1("stdev", self.grid)

    def sterr(self,evt):
        self._statsType1("sterr", self.grid)

    def sem(self,evt):
        self._statsType1("sem", self.grid)

    def z(self,evt):
        self._statsType2("z", texto = 'score',
                         spinData = (1,100, 1))

    def zs(self,evt):
        self._statsType1("zs", self.grid)

    def zmap(self,evt):
        self.logPanel.write('zmap')

    def threshold(self,evt):
        functionName= "threshold"
        group= lambda x,y: (x,y)
        setting= self.defaultDialogSettings
        setting['Title']= functionName
        ColumnList, colnums= wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't selected any items!")
            return
        if threshmin == None or threshmax == None or newval == None:
            self.logPanel.write("You haven't entered all the required values!")
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
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData(numpy.ravel(result))
        self.logPanel.write(functionName + ' successful')

    def trimboth(self,evt):
        self._statsType2("trimboth", texto = '% proportiontocut',
                         spinData = (1,100, 1), factor = 0.01)

    def trim1(self,evt):
        functionName = "trim1"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't selected any items!")
            return
        values = [ [pos for pos, value in enumerate( ColumnList )
                    if value == val
                    ][0]
                   for val in colNameSelect
                   ]

        # -------------------
        colums = [ GetData(colnums[ pos ]) for pos in values]
        # se hace los calculos para cada columna
        result = [getattr(stats, functionName)( col, proportiontocut, tail[0] ) for col in colums]
        # se muestra los resultados
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData(numpy.ravel(result))
        self.logPanel.write(functionName + ' successful')


    def covariance(self, evt):
        self._statsType3(functionName = "covariance",
                         texto1 = u"X Column to analyse",
                         texto2 = u"Y Column to analyse",
                         useNumpy = True)

    #def correlation(self, evt):
    #    self.logPanel.write('correlation')

    def paired(self, evt):
        self._statsType3(functionName = "paired",
                         texto1 = u"X Column to analyse",
                         texto2 = u"Y Column to analyse",
                         useNumpy = True, allData = True)

    def pearsonr(self, evt):
        self._statsType3(functionName = "pearsonr",
                         texto1 = u"X Column to analyse",
                         texto2 = u"Y Column to analyse",
                         useNumpy = True,
                         nameCols= ("Pearson's r"," two-tailed p-value"))


    def spearmanr(self, evt):
        self._statsType3(functionName = "spearmanr",
                         texto1 = u"X Column to analyse",
                         texto2 = u"Y Column to analyse",
                         useNumpy = True,
                         nameCols= ("Spearman's r","two-tailed p-value"))

    def pointbiserialr(self, evt):
        self._statsType3(functionName = "pointbiserialr",
                         texto1 = u"X Column to analyse",
                         texto2 = u"Y Column to analyse",
                         useNumpy = True,
                         nameCols= ("Point-biserial r","two-tailed p-value"))

    def kendalltau(self, evt):
        self._statsType3(functionName = "kendalltau",
                         texto1 = u"X Column to analyse",
                         texto2 = u"Y Column to analyse",
                         useNumpy = True,
                         nameCols = ("Kendall's tau"," two-tailed p-value"))

    def linregress(self, evt):
        self._statsType3(functionName = "linregress",
                         texto1 = u"X Column to analyse",
                         texto2 = u"Y Column to analyse",
                         useNumpy = True,
                         nameCols= ("slope", "intercept", "r", "two-tailed prob",
                                    "sterr-of-the-estimate", "n"))

    def ttest_1samp(self, evt):
        functionName = "ttest_1samp"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't select any items!")
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
        colNameSelect = ['t','two tailed prob']
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData(result)
        self.logPanel.write(functionName + ' successful')


    def ttest_ind(self, evt):
        functionName = "ttest_ind"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't select any items!")
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
        colNameSelect = ['t','two tailed prob']
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData(result)
        self.logPanel.write(functionName + ' successful')


    def ttest_rel(self, evt):
        functionName = "ttest_rel"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't selected any items!")
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
        colNameSelect = ['t', 'two tailed prob']
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData(result)
        self.logPanel.write(functionName + ' successful')



    def chisquare(self, evt):
        functionName = "ttest_rel"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't selected any items!")
            return
        xvalues = [ [pos for pos, value in enumerate( ColumnList )
                     if value == val
                     ][0]
                    for val in xcolNameSelect
                    ]
        xcolumns = [ GetData(colnums[ pos ]) for pos in xvalues][0]
        if isinstance(ycolNameSelect, (str, unicode)):
            ycolNameSelect = [ycolNameSelect]
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
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData(result)
        self.logPanel.write(functionName + ' successful')

    def ks_2samp(self, evt):
        functionName = "ks_2samp"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't selected any items!")
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
        colNameSelect = ['KS D-value', 'associated p-value']
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData(result)
        self.logPanel.write(functionName + ' successful')

    def mannwhitneyu(self, evt):
        functionName = "mannwhitneyu"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't selected any items!")
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
        colNameSelect = ['u-statistic', 'one-tailed p-value']
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData(result)
        self.logPanel.write(functionName + ' successful')

    def ranksums(self, evt):
        functionName = "ranksums"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't selected any items!")
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
        colNameSelect = ['z-statistic', 'two-tailed p-value']
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData(result)
        self.logPanel.write(functionName + ' successful')

    def wilcoxont(self, evt):
        functionName = "wilcoxont"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't selected any items!")
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
        colNameSelect = ['t-statistic', 'two-tail probability estimate']
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData(result)
        self.logPanel.write(functionName + ' successful')

    def kruskalwallish(self, evt):
        self._statsType1("kruskalwallish",
                         self.grid,
                         useNumpy = True,
                         allColsOneCalc = True,
                         nameResults= ('H-statistic (corrected for ties)', 'p-value'))


    def friedmanchisquare(self, evt):
        self._statsType1("friedmanchisquare",
                         self.grid,
                         useNumpy = True,
                         allColsOneCalc = True,
                         nameResults= ('chi-square statistic', 'p-value'),
                         dataSquare= True)

    def chisqprob(self, evt):
        self._statsType2(functionName= "chisqprob",
                         texto = 'dregrees of fredom',
                         spinData= (1,100,1),
                         factor = 1,
                         useNumpy = True,
                         nameResults= ('one tailed probability'))
        
    def erfcc(self, evt):
        functionName = "erfcc"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't entered a valid value!")
            return

        # se hace los calculos
        result = getattr(stats, functionName)( xvalue)
        # se muestra los resultados
        colNameSelect = ['x', 'erfc(x)']
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData([xvalue ,result])
        self.logPanel.write(functionName + ' successful')

    def zprob(self, evt):
        functionName = "zprob"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't entered a valid value!")
            return

        # se hace los calculos
        result = getattr(stats, functionName)( xvalue)
        # se muestra los resultados
        colNameSelect = ['x', 'erfc(x)']
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData([xvalue ,result])
        self.logPanel.write(functionName + ' successful')

    #def ksprob(self, evt):
    #    self.logPanel.write('ksprob')

    #def fprob(self, evt):
    #    self.logPanel.write('fprob')

    def betacf(self, evt):
        functionName = "betacf"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't entered a valid value!")
            return

        # se hace los calculos
        result = getattr(stats, functionName)(a, b, x)
        # se muestra los resultados
        colNameSelect = ['a', 'b','x','betacf(a,b,x)']
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData([a, b, x, result])
        self.logPanel.write(functionName + ' successful')

    def gammln(self, evt):
        functionName = "gammln"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't entered a valid value!")
            return

        # se hace los calculos
        result = getattr(stats, functionName)( xvalue)
        # se muestra los resultados
        colNameSelect = ['xx', 'lgammln(xx)']
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData([xvalue ,result])
        self.logPanel.write(functionName + ' successful')

    def betai(self, evt):
        functionName = "betai"
        group = lambda x,y: (x,y)
        setting = self.defaultDialogSettings
        setting['Title'] = functionName
        ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

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
            self.logPanel.write("You haven't enter a valid value!")
            return

        # se hace los calculos
        result = getattr(stats, functionName)(a, b, x)
        # se muestra los resultados
        colNameSelect = ['a', 'b','x','betai(a,b,x)']
        wx.GetApp().output.addColData(colNameSelect, functionName)
        wx.GetApp().output.addColData([a, b, x, result])
        self.logPanel.write(functionName + ' successful')


    def F_oneway(self, evt):
        self._statsType1("F_oneway", self.grid, allColsOneCalc = True,
                         nameResults= ("F","p-value"))

    def F_value(self, evt):
        self._statsType1("F_value",self.grid, allColsOneCalc = True,
                         nameResults= ("F","p-value"))
#---------------------------------------------------------------------------
# Scripting API is defined here. So far, only basic (but usable!) stuff.
def GetData(column):
    """This function enables the user to extract the data from the data grid.
    The data are "clean" and ready for analysis."""
    return wx.GetApp().frame.grid.CleanData(column)
def GetDataName(column):
    """This function returns the name of the data variable - in other words,
    the column label from the grid."""
    return wx.GetApp().frame.grid.GetColLabelValue(column)
def PutData(column, data):
    """This routine takes a list of data, and puts it into the datagrid
    starting at row 0. The grid is resized if the list is too large. This
    routine desparately needs to be updated to prevt errors"""
    frame = wx.GetApp().frame
    n = len(data)
    if (n > frame.grid.GetNumberRows()):
        frame.grid.AddNCols(-1, (datawidth - gridwidth + 5))
    for i in range(n):
        frame.grid.SetCellValue(i, column, str(data[i]))

#--------------------------------------------------------------------------
# main loop
if __name__ == '__main__':
    app = SalStat2App(0)
    app.frame.Show()
    app.MainLoop()
# eof