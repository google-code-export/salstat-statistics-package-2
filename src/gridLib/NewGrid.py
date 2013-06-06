# -*- coding:utf-8 -*-
"""
Created on 09/12/2010

@author: usuario
"""
__all__ = ['NewGrid']
import wx
import wx.grid
from slbTools import ReportaExcel
import xlrd
from easyDialog import Dialog as dialog
from slbTools import isnumeric, isiterable
from numpy import ndarray, ravel
import os
import traceback

DEFAULT_GRID_SIZE= (0,0)
DEFAULT_FONT_SIZE = 12
DECIMAL_POINT = '.' 

from GridCopyPaste import PyWXGridEditMixin, MyContextGrid
from gridCellRenderers import floatRenderer

###########################################################################
## Class NewGrid
###########################################################################
class NewGrid(wx.grid.Grid, object):
    def __init__(self, parent, size, *args, **params):
        try:     _ = wx.GetApp()._
        except:  _ = lambda x: x
        self.nombre=   'selobu'
        self.maxrow=   0
        self.maxcol=   0
        self.zoom=     1.0
        self.moveTo=   None
        self.hasSaved= False
        self.wildcard= _("Suported Formats")+" (*.xls;*xlsx;*.txt;*csv)|*.xls;*xlsx;*.txt;*csv" + \
                       _("All Files")+" (*.*)|*.*|"
        #<p> used to check changes in the grid
        self.hasChanged = True
        self.usedCols= ([], [],)
        # </p>
        wx.grid.Grid.__init__(self, parent, *args, **params)
        # functions to copy paste
        if len([clase for clase in wx.grid.Grid.__bases__ if issubclass( PyWXGridEditMixin, clase)]) == 0:
            wx.grid.Grid.__bases__ += ( PyWXGridEditMixin,)
        # contextual menu
        self.__init_mixin__()
        
        # setting the renderer
        ##self.__initAttr()
        
        #if len(args) > 0:
        #    self.__init_mixin__( args[0])
        #elif 'parent' in params.keys():
        #    self.__init_mixin__( params['parent'])
        
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
        
        try:
            self.defaultRowSize=  self.GetRowSize(0)
        except:
            self.defaultRowSize=  19
        try:    
            self.defaultColSize=  self.GetColSize(0)
        except:
            self.defaultColSize=  80
        self.defaultRowLabelSize= self.GetRowLabelSize()
        self.defaultColLabelSize= self.GetColLabelSize()
        # Label Appearance
        if wx.Platform == '__WXMAC__':
            ##self.SetGridLineColour("#b7b7b7")
            self.SetGridLineColour( wx.BLACK)
            self.SetLabelBackgroundColour("#d2d2d2")
            self.SetLabelTextColour("#444444")
        else:
            self.SetLabelBackgroundColour( wx.Colour( 254, 226, 188 ) )
        # Cell Defaults
        self.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
        self.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        # se activa el menu contextual sobre el grid
        self.Bind(wx.grid.EVT_GRID_EDITOR_CREATED,         self.onCellEdit)
        self.Bind(wx.grid.EVT_GRID_CMD_LABEL_RIGHT_DCLICK, self.RangeSelected)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE,            self.onCellChanged)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK,       self.OnGridRighClic)
        self.Bind(wx.EVT_MOUSEWHEEL,                       self.__OnMouseWheel)

    def _selectDbTableDialog_initAttr(self):
        renderer = floatRenderer( 4)
        self.__oddAttr=  wx.grid.GridCellAttr()
        self.__oddAttr.SetBackgroundColour( wx.Colour( 220, 230, 250 ))
        self.__oddAttr.SetRenderer( renderer)
        self.__evenAttr= wx.grid.GridCellAttr()
        self.__evenAttr.SetBackgroundColour( wx.Colour( 146, 190, 183 ))
        self.__evenAttr.SetRenderer( renderer)
        
    def GetAttr(self, row, col, kind):
        attr=   [ self.__evenAttr, self.__oddAttr][row % 2]
        ##attr=  attr[col] # renderer by col is missing
        attr.IncRef()
        return attr
    
    def __zoom_rows(self):
        """Zooms grid rows"""
        for rowno in xrange(self.GetNumberRows()):
            self.SetRowSize(rowno, self.defaultRowSize*self.zoom)
        self.SetRowLabelSize( self.defaultRowLabelSize * self.zoom)

    def __zoom_cols(self):
        """Zooms grid columns"""
        tabno = 1 #self.current_table
        for colno in xrange(self.GetNumberCols()):
            self.SetColSize(colno, self.defaultColSize * self.zoom)
        self.SetColLabelSize(self.defaultColLabelSize * self.zoom)

    def __zoom_labels(self):
        """Zooms grid labels"""
        labelfont = self.GetLabelFont()
        labelfont.SetPointSize(max(1, int(DEFAULT_FONT_SIZE * self.zoom)))
        self.SetLabelFont(labelfont)

    def __OnMouseWheel(self, event):
        """Event handler for mouse wheel actions
        Invokes zoom when mouse when Ctrl is also pressed
        """
        if event.ControlDown():
            zoomstep = 0.05 * event.LinesPerAction
            if event.WheelRotation > 0:
                self.zoom += zoomstep
            else:
                if self.zoom > 0.6:
                    self.zoom -= zoomstep
            self.__zoom_rows()
            self.__zoom_cols()
            self.__zoom_labels()
            self.ForceRefresh()
        else:
            event.Skip()

    def setLog(self, log):
        self.log= log
    def onCellChanged(self, evt):
        self.hasChanged= True
        self.hasSaved=   False
        evt.Skip()

    def RangeSelected(self, evt):
        if evt.Selecting():
            self.tl = evt.GetTopLeftCoords()
            self.br = evt.GetBottomRightCoords()

    def CutData(self, evt):
        self.Copy()
        self.Delete()
        self.hasChanged= True
        self.hasSaved=   False
        evt.Skip()

    def CopyData(self, evt):
        self.Copy()

    def PasteData(self, evt):
        self.OnPaste()
        self.hasChanged= True
        self.hasSaved=   False
        evt.Skip()

    def DeleteCurrentCol(self, evt):
        currentRow, currentCol, rows,cols = self.GetSelectionBox()[0]
        if cols < 1:
            return
        # A wxpython bug was detected
        # the app crash when trying to delete a colum
        # with a custom attr
        # deleting all data
        if 1:
            self.clearCol(currentCol)
            self.SetColLabelValue(currentCol, self.generateLabel( currentCol))
        else:
            self.DeleteCols( pos = currentCol, numCols = 1)
        self.AdjustScrollbars( )
        self.hasChanged= True
        self.hasSaved=   False
        evt.Skip()

    def DeleteCurrentRow(self, evt):
        currentRow, currentCol, rows,cols = self.GetSelectionBox()[0]
        if rows < 1:
            return
        self.DeleteRows(currentRow, 1)
        self.AdjustScrollbars()
        self.hasChanged= True
        self.hasSaved=   False
        evt.Skip()

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
        self.hasChanged= True
        self.hasSaved=   False
        #evt.Skip()

    # function finds out how many cols contain data - all in a list
    #(ColsUsed) which has col #'s
    def GetUsedCols(self):
        # improving the performance
        if not self.hasChanged:
            return self.usedCols

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
        self.usedCols= (ColsUsed, colnums)
        self.hasChanged= False
        return self.usedCols

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
        return self.SaveXls(None, True)

    def SaveXls(self, *args):
        try:     _= wx.GetApp()._
        except:  _= lambda x: x
        if len(args) == 1:
            saveAs= False
        elif len(args) == 0:
            saveAs= True
        else:
            saveAs= args[1]
        self.reportObj= ReportaExcel(cell_overwrite_ok = True)
        if self.hasSaved == False or saveAs: # path del grid
            # mostrar el dialogo para guardar el archivo
            dlg= wx.FileDialog(self, _("Save Data File"), "" , "",\
                               "Excel (*.xls)|*.xls| \
                                    Any (*.*)| *.*", wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                self.path = dlg.GetPath()
                if not self.path.endswith('.xls'):
                    self.path= self.path+'.xls'       
            else:
                return (False, None)
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
            self.reportObj.writeByCols(result, sheet= 0) # report the data in the first sheet
        self.reportObj.save()
        self.hasSaved = True
        filename= os.path.split(self.path)[-1]
        if len( filename) > 8:
            filename = filename[:8]
        print "The file %s was successfully saved!" % self.reportObj.path
        return (True, filename)
    
    def load(self, path, *args, **params):
        # dispath load data depending on the file extension
        if path == None:
            return self._LoadFile(evt= None)
        
        extension= os.path.split(path)[1].split('.')[-1]
        
        available= {'csv':  self.LoadCsvTxt,
                    'txt':  self.LoadCsvTxt,
                    'xls':  self.LoadXls,
                    'xlsx': self.LoadXls,
                    'db':   self._LoadSqlite,
                    }
        try:
            return available[extension](path, *args, **params)
        except KeyError:
            raise
        
    def _LoadSqlite(self, path, *args, **params):
        # to load data from an sqlite database
        from sqlalchemy import create_engine
        if path == None:
            return ( False, )
        engine= create_engine( 'sqlite:///%s'%path, echo=False, )
        return ( self._loadDb( engine), path)
        
    def _loadDb(self, engine):
        from gridLib.gridsql import selectDbTableDialog, GenericDBClass
        dlg= selectDbTableDialog( self, engine, allow2edit= True)
        if dlg.ShowModal() == wx.ID_OK:
            values= dlg.GetValue()
        else:
            dlg.Destroy()
            return False
        # the dialog is destroyed after the results of the database
        value, filterTxt = values
        if value == None:
            dlg.Destroy()
            # The user didn't select any table
            return False
        # reading the data by columns and paste into the current sheet
        table=  dlg.m_grid.table
        sesion = table.Session()
        # add a page to write the result
        # self.addPage(name= 'noname', gridSize= (sesion.query(GenericDBClass).limit(20000).count(), len(table.colLabels)))
        for colNumber, colName in enumerate( table.colLabels):
            rowValues= list()
            for rowi in sesion.query( GenericDBClass).filter(filterTxt).limit(20000).all():
                rowValues.append( getattr( rowi, colName))
                # report the values
            # writing the data in a new sheet
            self.PutCol( colNumber, rowValues,)
        dlg.Destroy()
        return True
        
    def LoadFile(self, evt, **params):
        try:     _= wx.GetApp()._
        except:  _= lambda x: x
        wildcard=  _("Suported files")+" (*.txt;*.csv;*.xls;*.xlsx;*.db)|*.txt;*.csv;*.xls;*.xlsx;*db|" \
            "Excel Files (*xlsx;*xlsm;*.xls)|*.xlsx;*.xlsm;*.xls|"\
            "Txt file (*.txt)|*.txt|" \
            "Csv file (*.csv)|*.csv|" \
            "Sqlite Database (*.db)|*.db" \
            "Excel 2007 File (*xlsx)|*.xlsx|"\
            "Excel 2003 File (*.xls)|*.xls|" 
            
        dlg = wx.FileDialog(self, _("Load Data File"), "","",
                            wildcard= wildcard,
                            style = wx.OPEN)
        try:
            icon = imageEmbed().logo16()
            dlg.SetIcon(icon)
        except:
            pass

        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return (False, None)
        
        fullPath= dlg.Path
        # if the file is loaded then 
        if self.load(fullPath)[0]:
            self.hasChanged= True
            self.hasSaved= True
            # emptying the undo - redo buffer
            self.emptyTheBuffer()
            if evt != None:
                evt.Skip()
            return ( True, os.path.split(fullPath)[-1])
        else:
            return ( False, None)

    def LoadCsvTxt(self, fullPath):
        from numpy import genfromtxt
        try:     _= wx.GetApp()._
        except:  _= lambda x: x
        '''use the numpy library to load the data'''
        # comments='#', delimiter=None, skiprows=0, skip_header=0, skip_footer=0, converters=None, missing='', missing_values=None, filling_values=None, usecols=None, names=None, excludelist=None, deletechars=None, replace_space='_', autostrip=False, case_sensitive=True, defaultfmt='f%i', unpack=None, usemask=False, loose=True, invalid_raise=True
        btn1= ['FilePath',    [fullPath] ]
        txt1= ['StaticText',  [_('comments symbol')] ]
        btn2= ['TextCtrl',    [] ]
        txt2= ['StaticText',  [_('delimiter symbol')]]
        txt3= ['StaticText',  [_('Number of header lines to skip')]]
        btn3= ['IntTextCtrl', []]
        txt4= ['StaticText',  [_('Number of footer lines to skip')]]
        btn4= ['CheckBox',    [_('Has Header')]]

        structure= []
        structure.append([btn1 ])
        structure.append([btn2, txt1])
        structure.append([btn2, txt2])
        structure.append([btn3, txt3])
        structure.append([btn3, txt4])
        structure.append([btn4])

        setting = {'Title': _('Select a sheet')}

        dlg = dialog(self, struct= structure, settings= setting)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return False, None

        (f_name, comments, delimiter, header2skip, footer2skip, hasHeader)= dlg.GetValue()
        if delimiter== u'':
            delimiter= None

        if header2skip == None:
            header2skip= 0

        if footer2skip == None:
            footer2skip= 0

        if comments == u'':
            comments= '#'

        dlg.Destroy()
        # reading the data
        data = genfromtxt(f_name, comments= comments,
                          dtype= None,
                          delimiter=  delimiter,
                          skip_header= header2skip,
                          skip_footer= footer2skip)
        # putting the data inito the Data Entry Panel
        if hasHeader:
            initRow= 1
        else:
            initRow= 0

        #grid= wx.GetApp().inputGrid 
        if len(data.shape)== 1:
            # it's considered to be of one column
            data.shape= (data.shape[0],1)
        for col in range(data.shape[1]):
            self.PutCol( col, data[initRow:,col])

        # Renaming the column of the Data Entry Panel
        if hasHeader:
            headerData= [data[0, col] for col in range(data.shape[1]) ]
            for pos,x in enumerate(headerData):
                if not isinstance( x, (str, unicode)):
                    x.__str__()
                # writing the data
                self.SetColLabelValue(pos, x)

        self.hasChanged= True
        self.hasSaved=   True
        return (True, os.path.split(f_name)[-1])

    def LoadXls(self, fullPath):
        try:     _= wx.GetApp()._
        except:  _= lambda x: x
        print 'import xlrd'
        filename= fullPath
        filenamestr= filename.__str__()
        #print '# remember to write an  r   before the path'
        print 'filename= r' + "'" + filename.__str__() + "'"
        # se lee el libro
        wb= xlrd.open_workbook(filename)
        print 'wb = xlrd.open_workbook(filename)'
        sheets= [wb.sheet_by_index(i) for i in range(wb.nsheets)]
        print 'sheets= [wb.sheet_by_index(i) for i in range(wb.nsheets)]'
        sheetNames = [sheet.name for sheet in sheets]
        print 'sheetNames= ' + sheetNames.__str__()
        bt1= ('Choice',     [sheetNames])
        bt2= ('StaticText', [_('Select a sheet to be loaded')])
        bt3= ('CheckBox',   [_('Has header')])
        setting = {'Title': _('Select a sheet'),
                   '_size':  wx.Size(250,220)}

        dlg = dialog(self, struct=[[bt1,bt2],[bt3]], settings= setting)
        if dlg.ShowModal() != wx.ID_OK:
            return (False, None)

        (sheetNameSelected, hasHeader)= dlg.GetValue()
        if sheetNameSelected == None:
            return (False, None)

        if not isinstance(sheetNameSelected, (str, unicode)):
            sheetNameSelected = sheetNameSelected.__str__()

        print 'sheetNameSelected= ' + "'" + sheetNameSelected + "'"
        print 'hasHeader= ' + hasHeader.__str__()
        dlg.Destroy()

        if not ( sheetNameSelected in sheetNames):
            return (False, None)

        self._loadXls(sheetNameSelected= sheetNameSelected,
                      sheets= sheets,
                      sheetNames= sheetNames,
                      filename= filename,
                      hasHeader= hasHeader)
        print '''grid._loadXls(sheetNameSelected= sheetNameSelected,
                      sheets= sheets,
                      sheetNames= sheetNames,
                      filename= filename,
                      hasHeader= hasHeader)'''

        print 'Importing  : %s successful'%filename
        self.hasChanged= True
        self.hasSaved=   True
        return (True, sheetNameSelected)

    def _loadXls( self, *args,**params):
        try:     _= wx.GetApp()._
        except:  _= lambda x: x
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
        self.hasSaved= True
        # /<p>

        # se hace el grid de tamanio 1 celda y se redimensiona luego
        self.ClearGrid()
        # reading the size of the needed sheet
        currentSize= (self.NumberRows, self.NumberCols)
        # se lee el tamanio de la pagina y se ajusta las dimensiones
        neededSize = (sheetSelected.nrows, sheetSelected.ncols)
        if neededSize[0]-currentSize[0] > 0:
            self.AppendRows(neededSize[0]-currentSize[0])

        if neededSize[1]-currentSize[1] > 0:
            self.AppendCols(neededSize[1]-currentSize[1])

        # se escribe los datos en el grid
        try:
            DECIMAL_POINT= wx.GetApp().DECIMAL_POINT
        except AttributeError:
            pass
        star= 0
        if hasHeader:
            star= 1
            for col in range( neededSize[1]):
                header= sheetSelected.cell_value( 0, col)
                if header == u'' or header == None:
                    ## return the column to it's normal label value
                    self.SetColLabelValue( col, self.generateLabel( col))
                elif not isinstance( header,( str, unicode)):
                    self.SetColLabelValue( col, sheetSelected.cell_value( 0, col).__str__())
                else:
                    self.SetColLabelValue( col, sheetSelected.cell_value( 0, col))
        else:
            # return all header to default normal value
            for col in range( neededSize[1]):
                self.SetColLabelValue(col, self.generateLabel( col))

        if hasHeader and neededSize[0] < 2:
            return

        for reportRow, row in enumerate(range( star, neededSize[0])):
            for col in range( neededSize[1]):
                newValue = sheetSelected.cell_value( row, col)
                if isinstance( newValue, (str, unicode)):
                    self.SetCellValue( reportRow, col, newValue)
                elif sheetSelected.cell_type( row, col) in ( 2, 3):
                    self.SetCellValue( reportRow, col, str( newValue).replace('.', DECIMAL_POINT))
                else:
                    try:
                        self.SetCellValue (reportRow, col, str(newValue))
                    except:
                        print  _("Could not import the row,col (%i,%i)") % (row+1, col+1)

    def generateLabel( self, colNumber):
        colNumber+= 1
        analyse = True
        result= list()
        while analyse:
            res = colNumber/26.0
            if res == int(res):
                result.append(26)
                colNumber= colNumber/26-1
                analyse= res > 1
                continue

            fp= res-int(res) # float Part
            # deleting fix by rounding
            if fp !=0 :
                fp= int(round(fp*26.0,0))
            else:
                fp= 1

            result.append(fp)
            colNumber= colNumber/26
            analyse= res > 1

        res = '' 
        while len(result):
            res += chr(result.pop(-1) + 64) 
        return res

    def getData(self, x):
        try:     _= wx.GetApp()._
        except:  _= lambda x: x
        for i in range(len(x)):
            try:
                row = int(x[i].attributes["row"].value)
                col = int(x[i].attributes["column"].value)
                datavalue = float(self.getText(x[i].childNodes))
                self.SetCellValue(row, col, str(datavalue))
            except ValueError:
                print _("Problem importing the xml")

    def getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    def CleanRowData(self, row):
        indata = []
        missingvalue= wx.GetApp().missingvalue
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
        try:
            dp= wx.GetApp().DECIMAL_POINT
        except AttributeError:
            dp= DECIMAL_POINT
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
        try:
            dp = wx.GetApp().DECIMAL_POINT
        except AttributeError:
            dp= DECIMAL_POINT
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

    def PutRow(self, rowNumber, data):
        try:     _= wx.GetApp()._
        except:  _= lambda x: x
        try: 
            if isinstance(rowNumber, (str, unicode)):
                if not(rowNumber in self.rowNames):
                    raise TypeError(_('You can only use a numeric value, or the name of an existing column'))
                for pos, value in enumerate(self.rowNames):
                    if value == rowNumber:
                        rowNumber= pos
                        break

            if not isnumeric(rowNumber):
                raise TypeError(_('You can only use a numeric value, or the name of an existing column'))

            rowNumber= int(rowNumber)        
            if rowNumber < 0 or rowNumber > self.GetNumberRows():
                raise StandardError(_('The minimum accepted col is 0, and the maximum is %i')%self.GetNumberRows()-1)

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
            except AttributeError:
                dp= DECIMAL_POINT

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
            self.hasSaved= False
            self.hasChanged= True

    def GetRow(self, row):
        return self._cleanData( self._getRow( row))

    def GetEntireDataSet(self, numcols):
        """Returns the data specified by a list 'numcols' in a Numpy
        array"""
        import numpy.array
        biglist = []
        for i in range(len(numcols)):
            smalllist = wx.GetApp().frame.CleanData(numcols[i])
            biglist.append(smalllist)
        return numpy.array((biglist), numpy.float)

    def GetColNumeric(self, colNumber):
        try:     _= wx.GetApp()._
        except:  _= lambda x: x
        # return only the numeric values of a selected colNumber or col label
        # all else values are drop
        # add the ability to manage non numerical values
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

        values= self._cleanData( self._getCol( colNumber))
        return [val for val in values if not isinstance(val,(unicode, str)) and val != None ]
    def onCellEdit(self, event):
        '''
        When cell is edited, get a handle on the editor widget
        and bind it to EVT_KEY_DOWN
        '''        
        editor = event.GetControl()        
        editor.Bind(wx.EVT_KEY_DOWN, self.onEditorKey)
        event.Skip()

    #----------------------------------------------------------------------
    def onEditorKey(self, event):
        '''
        Handler for the wx's cell editor widget's keystrokes. Checks for specific
        keystrokes, such as arrow up or arrow down, and responds accordingly. Allows
        all other key strokes to pass through the handler.
        '''
        keycode = event.GetKeyCode() 
        if keycode == wx.WXK_UP:
            self.MoveCursorUp(False)
        elif keycode == wx.WXK_DOWN:
            self.MoveCursorDown(False)
        elif keycode == wx.WXK_LEFT:
            self.MoveCursorLeft(False)
        elif keycode == wx.WXK_RIGHT:
            self.MoveCursorRight(False)
        else:
            pass
        event.Skip()

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

        return [self.GetCellValue( rowNumber, col) for col in range( self.GetNumberCols())]
    
    def PutCol(self, *args, **params):
        return self.putCol(*args, **params)
    
    def putCol( self, colNumber, data):
        try:
            if isinstance( colNumber, (str, unicode)):
                if not(colNumber in self.colNames):
                    raise TypeError('You can only use a numeric value, or the name of an existing column')
                for pos, value in enumerate(self.colNames):
                    if value == colNumber:
                        colNumber= pos
                        break
    
            if not isnumeric( colNumber):
                raise TypeError('You can only use a numeric value, or the name of an existing column')
    
            colNumber= int(colNumber)        
            if colNumber < 0 or colNumber > self.GetNumberCols():
                raise StandardError('The minimum accepted col is 0, and the maximum is %i'%self.GetNumberCols()-1)
    
            self.clearCol( colNumber)
    
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
                dp= DECIMAL_POINT
    
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
        except:
            raise
        finally:
            self.hasSaved= False
            self.hasChanged= True

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
            
    def get_selection(self):
        """ Returns an index list of all cell that are selected in 
        the grid. All selection types are considered equal. If no 
        cells are selected, the current cell is returned.
        
        from: http://trac.wxwidgets.org/ticket/9473"""

        dimx, dimy = (self.NumberRows, self.NumberCols) #self.parent.dimensions[:2]
        selection = []
        selection += self.GetSelectedCells()
        selected_rows = self.GetSelectedRows()
        selected_cols = self.GetSelectedCols()
        selection += list((row, y) for row in selected_rows for y in xrange(dimy))
        selection += list((x, col) for col in selected_cols for x in xrange(dimx)) 
        for tl,br in zip(self.GetSelectionBlockTopLeft(), self.GetSelectionBlockBottomRight()):
            selection += [(x,y) for x in xrange(tl[0],br[0]+1) for y in xrange(tl[1], br[1]+1)]
            if selection == []: 
                selection = self.get_currentcell()
        selection = sorted(list(set(selection)))
        return selection
        
    def OnGridRighClic(self,evt):
        self.PopupMenu(MyContextGrid(self), evt.GetPosition())
        evt.Skip()
        
    def setColNames(self,names):
        # escribe los nombres de las columnas en el grid
        if not(type(names) == type(list()) or type(names) == type(tuple())):
            raise TypeError("It's allowed one list")
        [self.SetColLabelValue(colNumber, value) for colNumber, value in enumerate(names) ]
        
    def setRowNames(self,names):
        if not(type(names) == type(list()) or type(names) == type(tuple())):
            raise TypeError("It's allowed one iterable list")
        [self.SetRowLabelValue(rowNumber, value) for rowNumber, value in enumerate(names)]
        
    def updateGridbyRow(self,values):
        # reescribe los datos del grid con los nuevos datos ingresados por filas (rows)
        [self.SetCellValue(row,col,cellContent) for row, rowContent in enumerate(values) \
          for col, cellContent in enumerate(rowContent) ]
        
    def updateGridbyCol(self,values):
        [self.SetCellValue(row,col,cellContent) for col, colContent in enumerate(values) \
          for row, cellContent in enumerate(colContent)] 
               
    def getHeader(self):
        # retorna solo el encabezado de la malla actual
        return tuple([self.GetColLabelValue(index) for index in range(self.GetNumberCols())])
    
    def getByColumns(self, maxRow = None):
        # retorna el valor de la malla por columnas
        numRows = self.GetNumberRows()
        ncols= self.GetNumberCols()
        if maxRow != None:
            numRows= min([numRows, maxRow])
        # se extrae los contenidos de cada fila
        return tuple([tuple([ self.GetCellValue(row,col) for row in range(numRows) ])
                       for col in range(ncols)])

    def getByRows(self):
        '''retorna el contenido del grid mediante filas
        la primer fila corresponde al nombre de las filas'''
        contenidoGrid = [self.getRowNames()]
        numCols = self.GetNumberCols()
        numRows = self.GetNumberRows()
        contenidoGrid.extend(tuple([tuple([self.GetCellValue(row,col) for col in range(numCols)]) for row in range(numRows) ]))
        return tuple(contenidoGrid)
    
    def getRowNames(self):
        # retorna el nombre de las columnas del grid
        # retorna solo el encabezado de la malla actual
        return tuple([self.GetRowLabelValue(rowNumber) for rowNumber in range(self.GetNumberRows())])
    
    def getValue(self):
        # retorma los contenidos de la malla ordenados por filas y 
        # empezando por el encabezado
        # se extrae el nombre de la columnas
        numCols = self.GetNumberCols()
        contenidoGrid = [self.getHeader()]
        contenidoGrid.extend([tuple([self.GetCellValue(row,col) for col in range(numCols)]) for row in range(self.GetNumberRows())])
        return tuple(contenidoGrid)
    
    def getNumByCol(self,colNumber):
        # the colNumber exist?
        ncols= self.GetNumberCols() 
        nrows= self.GetNumberRows()
        if ncols < 1 or nrows < 1:
            return ()
        if colNumber > nrows:
            return ()
        selectCol= list(self.getByColumns()[colNumber])
        newlist= [selectCol[i] for i in range(len(selectCol)-1,-1,-1)]
        tamanio = len(selectCol)-1
        for pos,value in enumerate(newlist):
            if value == u'':
                realPos = tamanio-pos
                selectCol.pop(realPos)
            else:
                break
        if len(selectCol) == 0:
            return ()
        for pos, value in enumerate(selectCol):
            try:
                selectCol[pos]= float(value)
            except:
                selectCol[pos]= None
        return selectCol
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

def test():
    # para verificar el funcionamiento correcto del grid
    pass

if __name__ == '__main__':    
        app = wx.PySimpleApp()
        app.translate= lambda x:x
        frame = wx.Frame(None, -1, size=(700,500), title = "wx example")
        grid = NewGrid(frame)
        grid.CreateGrid(2000,60)
        grid.SetDefaultColSize(70, 1)
        grid.EnableDragGridSize(False)
        grid.SetCellValue(0,0,"Col is")
        grid.SetCellValue(1,0,"Read ")
        grid.SetCellValue(1,1,"hello")
        grid.SetCellValue(2,1,"23")
        grid.SetCellValue(4,3,"greren")
        grid.SetCellValue(5,3,"geeges")
        # make column 1 multiline, autowrap
        cattr = wxCellAttr()
        cattr.SetEditor(wxCellAutoWrapStringEditor())
        #cattr.SetRenderer(wxCellAutoWrapStringRenderer())
        grid.SetColAttr(1, cattr)
        frame.Show(True)
        app.MainLoop()