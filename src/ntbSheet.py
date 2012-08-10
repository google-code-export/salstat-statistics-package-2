# -*- coding: utf-8 -*-
'''
Created on 25/10/2010

@author: Sebastian Lopez
'''

import wx
from NewGrid import NewGrid # grid with context menu
from imagenes import imageEmbed
import wx.grid
from slbTools import isnumeric, isiterable
from gridCellRenderers import floatRenderer
import wx.aui
from numpy import ndarray, ravel
from slbTools import ReportaExcel
import xlrd
from easyDialog import Dialog as dialog

try:
    from imagenes import imageEmbed
except:
    pass

def numPage():
    i = 1
    while True:
        yield i
        i+= 1

#---------------------------------------------------------------------------
# class for grid - used as datagrid.
class MyGridPanel( wx.Panel, object ):
    # can be used as a grid ctrl
    def __init__( self, parent , id= wx.ID_ANY, size= (5,5)):
        # bigParent: id del parent para llamar la funcion OnrangeChange
        wx.Panel.__init__ ( self, parent, id , pos = wx.DefaultPosition, style = wx.TAB_TRAVERSAL )
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        #< don't change this line
        self.m_grid = NewGrid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        # don't change this line/>
        # Grid
        self.CreateGrid( size[0], size[1] )
        self.EnableEditing( True )
        self.EnableGridLines( True )
        self.EnableDragGridSize( False )
        self.SetMargins( 0, 0 )
        self.floatCellAttr= None
        # Columns
        self.EnableDragColMove( False )
        self.EnableDragColSize( True )
        self.SetColLabelSize( 30 )
        self.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
        # Rows
        self.EnableDragRowSize( True )
        self.SetRowLabelSize( 80 )
        self.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
        # Label Appearance
        if wx.Platform == '__WXMAC__':
            self.SetGridLineColour("#b7b7b7")
            self.SetLabelBackgroundColour("#d2d2d2")
            self.SetLabelTextColour("#444444")
        else:
            self.SetLabelBackgroundColour( wx.Colour( 254, 226, 188 ) )
        # Cell Defaults
        self.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
        #< don't change this line
        self.sizer.Add( self.m_grid , 1, wx.ALL|wx.EXPAND, 5 )
        # don't change this line/>
        self.SetSizer(self.sizer)
        self.Fit()
         
    def __getattribute__(self, name):
        '''wraps the funtions to the grid
        emulating a grid control'''
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self.m_grid.__getattribute__(name)
        
    def _getCol(self, colNumber, includeHeader= False):
        if isinstance(colNumber, (str, unicode)):
            # searching for a col with the name:
            if not(colNumber in self.colNames):
                raise TypeError('You can only use a numeric value, or the name of an existing column')
            
            for pos, value in enumerate(self.colNames):
                if value == colNumber:
                    colNumber= pos
                    break
        
        if not isnumeric(colNumber):
            raise TypeError('You can only use a numeric value, or the name of an existing column')
        
        if colNumber > self.GetNumberRows():
            raise StandardError('The maximum column allowed is %i, but you selected %i'%(self.GetNumberRows()-1, colNumber))
        
        return self._getColNumber(colNumber, includeHeader)
    
    def _getColNumber(self, colNumber, includeHeader= False):
        if not isnumeric(colNumber):
            raise TypeError('Only allow numeric values for the column, but you input '+ str(type(colNumber)))
        
        colNumber= int(colNumber)
        if colNumber < 0 or colNumber > self.GetNumberCols():
            raise StandardError('The minimum accepted col is 0, and the maximum is %i'%self.GetNumberCols()-1)
        
        result = [self.GetCellValue(row, colNumber) for row in range(self.GetNumberRows())]
        if includeHeader:
            result.insert(0, self.GetColLabelValue(colNumber))
        return result
    
    
    def _getRow( self, rowNumber):
        if isinstance( rowNumber, (str, unicode)):
            # searching for a col with the name:
            if not(rowNumber in self.rowNames):
                raise TypeError('You can only use a numeric value, or the name of an existing row')
            for pos, value in enumerate(self.rowNames):
                if value == rowNumber:
                    rowNumber= pos
                    break
                
        if not isnumeric(rowNumber):
            raise TypeError('You can only use a numeric value, or the name of an existing row')
        
        if rowNumber > self.GetNumberRows():
            raise StandardError('The maximum row allowed is %i, but you selected %i'%(self.GetNumberRows()-1, rowNumber))
        
        return self._getRowNumber(rowNumber)
    
    
    def _getRowNumber(self, rowNumber):
        if not isnumeric( rowNumber):
            raise TypeError('Only allow numeric values for the row, but you input '+ type(rowNumber).__str__())
        
        rowNumber= int(rowNumber)
        if rowNumber < 0 or rowNumber > self.GetNumberRows():
            raise StandardError('The minimum accepted row is 0, and the maximum is %i'%self.GetNumberRows()-1)
        
        return [self.GetCellValue(rowNumber, col) for col in range(self.GetNumberCols())]
    
    def putCol(self, colNumber, data):
        if isinstance(colNumber, (str, unicode)):
            if not(colNumber in self.colNames):
                raise TypeError('You can only use a numeric value, or the name of an existing column')
            for pos, value in enumerate(self.colNames):
                if value == colNumber:
                    colNumber= pos
                    break
                
        if not isnumeric(colNumber):
            raise TypeError('You can only use a numeric value, or the name of an existing column')
        
        colNumber= int(colNumber)        
        if colNumber < 0 or colNumber > self.GetNumberCols():
            raise StandardError('The minimum accepted col is 0, and the maximum is %i'%self.GetNumberCols()-1)
        
        self.clearCol(colNumber)
        
        if isinstance( data,(str, unicode)):
            data= [data]
        
        if isinstance( data, (int, long, float)):
            data= [data]
        
        if isinstance( data, (ndarray),):
            data= ravel( data)
        
        rows2add= len( data) - self.GetNumberRows()
        if rows2add > 0:
            if len( data) > 1e6:
                data= data[:1e6]
                rows2add= len( data) - self.GetNumberRows()
            self.AppendRows( rows2add)
        
        try:
            dp= wx.GetApp().DECIMAL_POINT
        except:
            d= '.'
            
        newdat= list()
        for row, dat in enumerate( data):
            if isinstance( dat, (str, unicode)):
                try:
                    dat= str(float(dat.replace(dp,'.'))).replace('.',dp)
                except:
                    pass
            else:
                try:
                    dat= str(dat)
                except:
                    dat= None
                    
            newdat.append(dat)
            
        for row, dat in enumerate(newdat):
            self.SetCellValue(row, colNumber, dat)
            
        
            
    def clearCol( self, colNumber):
        if colNumber < 0 or colNumber > self.GetNumberCols():
            raise StandardError( 'The minimum accepted col is 0, and the maximum is %i'%self.GetNumberCols()-1)
        
        for row in range( self.GetNumberRows()):
            self.SetCellValue( row, colNumber, u'')
    
    def clearRow( self, rowNumber):
        if rowNumber < 0 or rowNumber > self.GetNumberRows():
            raise StandardError( 'The minimum accepted row is 0, and the maximum is %i'%self.GetNumberRols()-1)
        
        for col in range( self.GetNumberCols()):
            self.SetCellValue( rowNumber, col, u'')
    
    @property
    def rowNames( self):
        return [self.GetRowLabelValue(row) for row in range(self.GetNumberRows())]
    @rowNames.setter
    def rowNames( self, rowNames):
        if isinstance(rowNames, (str, unicode)):
            rolNames= [rowNames]
            
        if not isiterable(rowNames):
            raise TypeError('rowNames must be an iterable object')
        
        if len(rowNames) == 0:
            return
        
        for rownumber, rowname in enumerate(rowNames):
            self.SetRowLabelValue(rownumber, rowname)
    
    @property
    def colNames(self):
        return [self.GetColLabelValue(col) for col in range(self.GetNumberCols())]
    @colNames.setter
    def colNames(self, colNames):
        if isinstance(colNames, (str, unicode)):
            colNames= [colNames]
            
        if not isiterable(colNames):
            raise TypeError('colNames must be an iterable object')
        
        if len(colNames) == 0:
            return
        
        for colnumber, colname in enumerate(colNames):
            self.SetColLabelValue(colnumber, colname)

class SimpleGrid(MyGridPanel):# wxGrid
    def __init__(self, parent, log, size= (1000,100)):
        self.NumSheetReport = 0
        self.log = log
        self.path = None
        MyGridPanel.__init__(self, parent, -1, size)
        self.Saved = True
        self.moveTo = None
        if wx.Platform == "__WXMAC__":
            self.SetGridLineColour(wx.BLACK)
        self.setPadreCallBack(self)
        self.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.Bind(wx.grid.EVT_GRID_CMD_LABEL_RIGHT_DCLICK, self.RangeSelected)
        self.m_grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.onCellChanged)
        self.wildcard = "Any File (*.*)|*.*|" \
            "S2 Format (*.xls)|*.xls"
        
    def onCellChanged(self, evt):
        self.Saved = False

    def RangeSelected(self, evt):
        if evt.Selecting():
            self.tl = evt.GetTopLeftCoords()
            self.br = evt.GetBottomRightCoords()

    def CutData(self, evt):
        self.Delete()
        self.Saved= False

    def CopyData(self, evt):
        self.Copy()


    def PasteData(self, evt):
        self.OnPaste()
        self.Saved= False

    def DeleteCurrentCol(self, evt):
        currentcol = self.GetGridCursorCol()
        self.DeleteCols(currentcol, 1)
        self.AdjustScrollbars()
        self.Saved= False


    def DeleteCurrentRow(self, evt):
        currentrow = self.GetGridCursorRow()
        self.DeleteRows(currentrow, 1)
        self.AdjustScrollbars()
        self.Saved= False

    def SelectAllCells(self, evt):
        self.SelectAll()

    # adds columns and rows to the grid
    def AddNCells(self, numcols, numrows, attr= None):
        insert= self.AppendCols(numcols)
        insert= self.AppendRows(numrows)
        if attr != None:
            for colNumber in range(self.GetNumberCols() - numcols, self.GetNumberCols(), 1):
                #self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
                self.SetColAttr( colNumber, attr)
        self.AdjustScrollbars()
        self.Saved= False

    # function finds out how many cols contain data - all in a list
    #(ColsUsed) which has col #'s
    def GetUsedCols(self):
        ColsUsed = []
        colnums = []
        dat = ''
        tmp = 0
        for col in range(self.GetNumberCols()):
            for row in range(self.GetNumberRows()):
                dat = self.GetCellValue(row, col)
                if dat != '':
                    tmp += 1
                    break # it's just needed to search by the first element
                
            if tmp > 0:
                ColsUsed.append(self.GetColLabelValue(col))
                colnums.append(col)
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
        elif len(args) == 0:
            saveAs= True
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
                if not self.path.endswith('.xls'):
                    self.path= self.path+'.xls'       
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
        try:
            icon = imageEmbed().logo16()
            dlg.SetIcon(icon)
        except:
            pass
        if dlg.ShowModal() != wx.ID_OK: # ShowModal
            dlg.Destroy()
            return
        self.log.write('import xlrd', None)
        filename= dlg.GetPath()
        filenamestr= filename.__str__()
        self.log.write('# remember to write an  r   before the path', None)
        self.log.write('filename= ' + "'" + filename.__str__() + "'", None)
        dlg.Destroy()
        # se lee el libro
        wb= xlrd.open_workbook(filename)
        self.log.write('wb = xlrd.open_workbook(filename)', None)
        sheets= [wb.sheet_by_index(i) for i in range(wb.nsheets)]
        self.log.write('sheets= [wb.sheet_by_index(i) for i in range(wb.nsheets)]', None)
        sheetNames = [sheet.name for sheet in sheets]
        self.log.write('sheetNames= ' + sheetNames.__str__(), None)
        bt1= ('Choice',     [sheetNames])
        bt2= ('StaticText', ['Select a sheet to be loaded'])
        bt3= ('CheckBox',   ['Has header'])
        setting = {'Title': 'Select a sheet',
                   '_size':  wx.Size(200,200)}
        
        dlg = dialog(self, struct=[[bt1,bt2],[bt3]], settings= setting)
        if dlg.ShowModal() != wx.ID_OK:
            return
        (sheetNameSelected, hasHeader)= dlg.GetValue()
        if sheetNameSelected == None:
            return
        if not isinstance(sheetNameSelected, (str, unicode)):
            self.log.write('sheetNameSelected= ' + "'" + sheetNameSelected.__str__() + "'",None)
        else:
            self.log.write('sheetNameSelected= ' + "'" + sheetNameSelected + "'",None)
        self.log.write('hasHeader= ' + hasHeader.__str__(), None)
        dlg.Destroy()
        
        if not ( sheetNameSelected in sheetNames):
            return
        
        self._loadXls(sheetNameSelected= sheetNameSelected,
                      sheets= sheets,
                      sheetNames= sheetNames,
                      filename= filename,
                      hasHeader= hasHeader)
        self.log.write('''grid._loadXls(sheetNameSelected= sheetNameSelected,
                      sheets= sheets,
                      sheetNames= sheetNames,
                      filename= filename,
                      hasHeader= hasHeader)''', None)
        
        self.log.write('Importing  : %s successful'%filename)
        
    def _loadXls( self, *args,**params):
        sheets=         params.pop( 'sheets')
        sheetNames=     params.pop( 'sheetNames')
        sheetNameSelected= params.pop( 'sheetNameSelected')
        filename=       params.pop( 'filename')
        hasHeader=      params.pop( 'hasHeader')
        for sheet, sheetname in zip(sheets, sheetNames):
            if sheetname == sheetNameSelected:
                sheetSelected= sheet
                break
            
        #<p> updating the path related to the new open file
        self.path= filename
        self.Saved= True
        # /<p>
        
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
                if not isinstance(header,(str, unicode)):
                    self.SetColLabelValue(col, sheetSelected.cell_value(0, col).__str__())
        
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
    def CleanData(self, coldata):
        indata = []
        self.missing = 0
        dp= wx.GetApp().DECIMAL_POINT
        missingvalue= wx.GetApp().missingvalue 
        if dp == '.':
            for i in range(self.GetNumberRows()):
                datapoint = self.GetCellValue(i, coldata).strip()
                if (datapoint != u'' or datapoint.replace(' ','') != u'') and (datapoint != u'.'):
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
                datapoint = self.GetCellValue(i, coldata).strip().replace(dp, '.')
                if (datapoint != u'' or datapoint.replace(' ','') != u'') and (datapoint != u'.'):
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
            if dat == u'' or dat.replace(' ','') == u'': # to detect a cell of only space bar
                dat = None
            else:
                try:
                    dat= float(dat.replace(dp, '.'))
                except:
                    pass
                
            result.append(dat)
        return result
    
    def GetCol(self, col, hasHeader= False):
        return self._cleanData( self._getCol( col, hasHeader))
    
    def PutCol(self, colNumber, data):
        try:
            return self.putCol(colNumber, data)
        except:
            raise
        finally:
            self.Saved= False
            
    def PutRow(self, rowNumber, data):
        try: 
            if isinstance(rowNumber, (str, unicode)):
                if not(rowNumber in self.rowNames):
                    raise TypeError('You can only use a numeric value, or the name of an existing column')
                for pos, value in enumerate(self.rowNames):
                    if value == rowNumber:
                        rowNumber= pos
                        break
                    
            if not isnumeric(rowNumber):
                raise TypeError('You can only use a numeric value, or the name of an existing column')
            
            rowNumber= int(rowNumber)        
            if rowNumber < 0 or rowNumber > self.GetNumberRows():
                raise StandardError('The minimum accepted col is 0, and the maximum is %i'%self.GetNumberRows()-1)
            
            self.clearRow(rowNumber)
            
            if isinstance( data,(str, unicode)):
                data= [data]
            
            if isinstance( data, (int, long, float)):
                data= [data]
            
            if isinstance( data, (ndarray),):
                data= ravel( data)
            
            cols2add= len( data) - self.GetNumberCols()
            if cols2add > 0:
                if len( data) > 16384:
                    data= data[:16384]
                    cols2add= len( data) - self.GetNumberCols()
                self.AppendCols( cols2add) ############### TO TEST
            
            try:
                dp= wx.GetApp().DECIMAL_POINT
            except:
                d= '.'
                
            newdat= list()
            for row, dat in enumerate( data):
                if isinstance( dat, (str, unicode)):
                    try:
                        dat= str(float(dat.replace(dp,'.'))).replace('.',dp)
                    except:
                        pass
                else:
                    try:
                        dat= str(dat)
                    except:
                        dat= None
                        
                newdat.append(dat)
                
            for col, dat in enumerate(newdat):
                self.SetCellValue(rowNumber, col, dat)
        except:
            raise
        finally:
            self.Saved= False
        
    def GetRow(self, row):
        return self._cleanData( self._getRow( row))
    
    def GetEntireDataSet(self, numcols):
        """Returns the data specified by a list 'numcols' in a Numeric
        array"""
        biglist = []
        for i in range(len(numcols)):
            smalllist = wx.GetApp().frame.grid.CleanData(numcols[i])
            biglist.append(smalllist)
        return numpy.array((biglist), numpy.float)
    
    def GetColNumeric(self, colNumber):
        # return only the numeric values of a selected colNumber or col label
        # all else values are drop
        values= self._cleanData( self._getCol( colNumber))
        return [val for val in values if not isinstance(val,(unicode, str)) and val != None ]
                   
class NoteBookSheet(wx.Panel, object):
    def __init__( self, parent, *args, **params):
        # se almacenan las paginas en un diccionario con llave el numero de pagina
        if params.has_key('fb'):
            self.fb= params.pop('fb')

        wx.Panel.__init__ ( self, parent, *args, **params)
        bSizer = wx.BoxSizer( wx.VERTICAL )
        self.m_notebook = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_DEFAULT_STYLE )
        ## wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_BOTTOM )
        # self.m_notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,self.OnNotebookPageChange)
        bSizer.Add( self.m_notebook, 1, wx.EXPAND |wx.ALL, 5 )
        self.SetSizer( bSizer )
        # se inicia el generador para el numero de pagina
        self.npage = numPage()
        self.currentPage = None
        self.pageNames= dict()
        self.Layout()
        
    # implementing a wrap to the current grid
    def __getattribute__( self, name):
        '''wraps the funtions to the grid
        emulating a grid control'''
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            if self.GetPageCount() != 0:
                currGrid= self.m_notebook.GetSelection()
                return currGrid.__getattribute__(name)
            raise AttributeError

    def getGridAllValueByCols( self,pageName):
        if not (pageName in self.pageNames.keys()):
            raise StandardError('The page does not exist')
        page= self.pageNames[pageName]
        return page.getByColumns()

    def getPageNames( self):
        return self.pageNames.keys()

    def getHeader( self,pageName):
        if not (pageName in self.pageNames.keys()):
            raise StandardError('The page does not exist')
        page= self.pageNames[pageName]
        return page.getHeader()

    def OnNotebookPageChange( self,evt):
        self.currentPage= evt.Selection

    def addPage( self, data= dict()):
        defaultData = {'name': u'',
                       'size': (0,0),
                       'nameCol': list(),
                       'nameRow': list()}
        for key, value in data.items():
            if defaultData.has_key(key):
                defaultData[key] = value
        # adiciona una pagina al notebook grid
        newName= defaultData['name'] +'_'+ str(self.npage.next())
        self.pageNames[newName]= MyGridPanel(self.m_notebook,-1,size= defaultData['size'] )
        self.currentPage=  self.pageNames[newName]
        grid= self.pageNames[newName]
        self.m_notebook.AddPage(grid, newName, False )
        # se hace activo la pagina adicionada
        self.m_notebook.SetSelection(self.m_notebook.GetPageCount()-1)
        # se escriben los nombres de las columnas en el grid en caso de existir
        if 'nameCol' in defaultData.keys():
            for index, value in enumerate(defaultData['nameCol']):
                grid.SetColLabelValue(index,value) # str(value)
        if 'nameRow' in defaultData.keys():
            for index, value in enumerate(defaultData['nameRow']):
                grid.SetRowLabelValue(index,value)
        # para actualizar un toolbar del grid
        if hasattr(self,'fb'):
            self.pageNames[newName].Bind(wx.grid.EVT_GRID_CMD_SELECT_CELL,
                      self._cellSelectionChange,)

            self.pageNames[newName].Bind(wx.grid.EVT_GRID_SELECT_CELL,
                      self._cellSelectionChange,#      source= self.pageNames[newName],
                      )

        return grid # retorna el objeto MyGrid

    def _cellSelectionChange( self, event):
        if self.GetPageCount() == 0:
            return
        row=  int(event.Row)
        col=  int(event.Col)
        Id=   event.GetId()
        pageSelectNumber=  self.m_notebook.GetSelection()
        grid= self.m_notebook.GetPage(pageSelectNumber)
        try:
            texto= grid.GetCellValue(row, col)
            self.fb.m_textCtrl1.SetValue(texto)
        except:
            pass
        event.Skip()

    def __loadData__( self,selectedGrid,data, byRows = True):
        # gridId, nombre de la hoja en la que se adicionaran los datos
        # data: iterable con los datos puntuales a cargar ej:
        #       data= ((1,2,3,5),(7,8,9,4))
        #       corresponde a la matriz
        #
        #         1 ! 2 ! 3 ! 5
        #         7 ! 8 ! 9 ! 4
        # byRows : bool, indica si los datos se ingresan por filas o por columnas
        if byRows:
            for rowNumber,fil in enumerate(data):
                for colNumber,cellContent in enumerate(fil):
                    if cellContent != None:
                        if type(cellContent) == type(u''):
                            selectedGrid.SetCellValue(rowNumber,colNumber, cellContent) ##unicode(str(cellContent))
                        else:
                            selectedGrid.SetCellValue(rowNumber,colNumber, unicode(str(cellContent)))
        else:
            for colNumber, col in enumerate(data):
                for rowNumber, cellContent in enumerate(col):
                    if type(cellContent) == type(u''):
                        selectedGrid.SetCellValue(rowNumber, colNumber, cellContent)
                    else:
                        selectedGrid.SetCellValue(rowNumber, colNumber, unicode(str(cellContent))) ## unicode(str(cellContent))
        # implementar cargar los datos

    def GetPageCount( self):
        # 21/04/2011
        # retorna el numero de paginas que hay en el notebook
        return self.m_notebook.PageCount

    def delPage( self, page= None):
        # si no se ingresa un numero de pagina se
        #     considera que se va a borrar la pagina actual
        # las paginas se numeran mediante numeros desde el cero
        if page == None:
            # se considera que la pagina a borrar es la pagina actual
            #self.m_notebook.GetCurrentPage().Destroy() # borra el contenido de la pagina
            self.m_notebook.DeletePage(self.m_notebook.GetSelection())
            # se borra la pagina

            return
        page = int(page)
        if page <0:
            return
        if page > self.GetPageCount():
            raise IndexError("Page doesn't exist")
        parent = self.pages[page].GetParent()
        parent.DeletePage(page)

    def upData( self,  data):
        # It's used to upload data into a grid
        # where the grid it's an int number
        # that gives the page number into the NotebookSheet
        # data: dict information with ...
        #       name: string name of the page
        #       size: data size (#rows, #ncols)
        #       data: matrix data
        #       nameCol: objeto iterable con el nombre de las columnas
        #              Si no se escribe aparece por defecto a, b,.. la
        #              nomenclatura comun
        if type(data) != type(dict()):
            raise TypeError('Data must be a dictionary')
        if not('byRows' in data.keys()):
            byRows = True
        else:
            byRows = data['byRows']
        # se adiciona la pagina grid
        grid01= self.addPage(data)
        # se cargan los datos dentro del grid
        self.__loadData__( grid01, data['data'], byRows)
        #< setting the renderer
        try:
            attr= wx.grid.GridCellAttr()
            attr.SetRenderer( floatRenderer( 4))
            for colNumber in range( self.grid.NumberCols):
                grid01.SetColAttr( grid01.NumberCols-1, attr)
        except AttributeError:
            # the renderer was not find
            pass
        # setting the renderer />
        return grid01

    def addColData( self, colData, pageName= None):
        '''adiciona una columna con el contenido de un iterable'''
        if pageName == None:
            if len(self.getPageNames()) == 0:
                'se procede a adicionar una hoja nueva'
                page = self.addPage()
            else:
                page = self.currentPage
        elif pageName in self.pageNames.keys():
            page = self.pageNames[pageName]
        else:
            page = self.addPage({'name': pageName})
        # se procede a verificar las dimensiones de la pagina actual
        size = (page.GetNumberRows(), page.GetNumberCols())
        # adding one column
        page.AppendCols(1)
        #< setting the renderer
        try:
            attr= wx.grid.GridCellAttr()
            attr.SetRenderer( floatRenderer( 4))
            page.SetColAttr( page.NumberCols-1, attr)
        except AttributeError:
            # the renderer was not find
            pass
        # setting the renderer />
        currCol = size[1]
        if isinstance(colData,(str,)):
            colData = [colData]
        else:
            # se verifica si tiene mas de un elemento
            try:
                len(colData)
            except TypeError:
                colData = [colData]
                
        # compare de row numbres
        if size[0] >= len(colData):
            pass
        else:
            diffColNumber= len(colData) - size[0]
            # adding the required rows
            page.AppendRows(diffColNumber)
        # populate with data
        DECIMAL_POINT= wx.GetApp().DECIMAL_POINT
        for colPos, colValue in enumerate(colData):
            if isinstance(colValue, (str,unicode)):
                pass
            else:
                colValue = str(colValue).replace('.', DECIMAL_POINT)
            page.SetCellValue(colPos, currCol, colValue)
            
    def addRowData( self, rowData, pageName= None, currRow = None):
        '''adds a row with it's row content'''
        # currRow is used to indicate if the user needs to insert
        # the rowContent into a relative row
        if not isnumeric(currRow) and currRow != None:
            raise TypeError('currRow must be a numerical value')
            
        if pageName == None:
            if len( self.getPageNames()) == 0:
                # adding a new page into the notebook
                page = self.addPage()
            else:
                page = self.currentPage
        elif pageName in self.pageNames.keys():
            page = self.pageNames[pageName]
        else:
            page = self.addPage( {'name': pageName})
            
        # check the size of the current page
        size = (page.GetNumberRows(), page.GetNumberCols())
        # check if it needs to add more columns
        neededCols= size[1] - len( rowData)
        if neededCols <  0:
            neededCols= abs( neededCols)
            page.AppendCols(neededCols)
            #< setting the renderer
            try:
                attr= wx.grid.GridCellAttr()
                attr.SetRenderer( floatRenderer( 4))
                for colNum in range( page.NumberCols - neededCols - 1, page.NumberCols - 1 ):
                    page.SetColAttr( colNum, attr)
            except AttributeError:
                # the renderer was not found
                pass
            # setting the renderer />
            
        # checking if the user input some currRow
        if currRow  == None:
            currRow = page.NumberRows
        elif currRow > page.NumberRows:
            raise StandardError('the maximumn allowed row to insert is the row %i'%(page.NumberRows))
        elif currRow < 0:
            raise StandardError('the minimum allowed row to insert is the row 0')
        currRow = int(currRow)
        
        if currRow == page.NumberRows:
            # append one row
            page.AppendRows(1)
        else:
            # insert one row
            page.InsertRows( pos = currRow, numRows = 1)

        if isinstance( rowData, (str, unicode)):
            rowData = [rowData]
        else:
            # check if it has more than one element
            try:
                len( rowData)
            except TypeError:
                rowData = [rowData]
       
        # populate with data
        DECIMAL_POINT= wx.GetApp().DECIMAL_POINT
        for colPos, rowValue in enumerate( rowData):
            if isinstance( rowValue, (str, unicode)):
                pass
            else:
                rowValue = str( rowValue).replace('.', DECIMAL_POINT)
            page.SetCellValue( currRow, colPos, rowValue)

class Test(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(480, 520))
        customPanel = NoteBookSheet(self,-1)
        # se adicionan 4 paginas al sheet
        for i in range(4):
            customPanel.addPage(size=(15,10))
        #customPanel.delPage(2)
        self.Centre()
        self.Show(True)

if __name__ == '__main__':
    app = wx.App()
    Test(None, -1, 'Custom Grid Cell')
    app.MainLoop()
