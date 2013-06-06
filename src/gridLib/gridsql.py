'''
Created on 26/10/2012

@author: USUARIO
'''
import wx
import wx.grid
import wx.aui
import numpy
from sqlalchemy import Table, MetaData, create_engine
from sqlalchemy.orm import mapper, sessionmaker, clear_mappers
from sqlalchemy.exc import StatementError
from easyDialog import Dialog
from gridEditors import VARCHAR
from gridEditors import DATE
from collections import OrderedDict
SEARCHINDEX= 50

from gridEditors import datePickerEditor
from GridCopyPaste import PyWXGridEditMixin, MyContextGrid
from GridCopyPaste import EVT_GRID_BEFORE_PASTE, EVT_GRID_PASTE
from gridLib.NewGrid import NewGrid
from slbTools import isnumeric
from numpy import ndarray, ravel
from gridLib.gridCellRenderers import floatRenderer

class okCancelPanel(wx.Panel):
    def __init__(self, *args, **params):
        wx.Panel.__init__(self, *args, **params)
        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer1.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )

        self.okButton = wx.Button( self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.cancelButton = wx.Button( self, wx.ID_CANCEL, u"CANCEL", wx.DefaultPosition, wx.DefaultSize, 0 )

        bSizer1.Add( self.okButton, 0, wx.ALL, 5 )
        bSizer1.Add( self.cancelButton, 0, wx.ALL, 5 )

        self.SetSizer( bSizer1 )
        self.Layout()

def AttrType( leg):
    editor={
        'BIGINT':      1,
        'BINARY':      2,
        'BLOB':        3,
        'BOOLEAN':     4,
        'BOOLEANTYPE': 5,
        'CHAR':        6,
        'CLOB':        7,
        'DATE':        DATE,
        'DATETIME':    9,
        'DECIMAL':     1,
        'FLOAT':       2,
        'INT':         3,
        'INTEGER':     4,
        'NCHAR':       5,
        'NULLTYPE':    6,
        'NUMERIC':     7,
        'NVARCHAR':    8,
        'REAL':        9,
        'SMALLINT':    1,
        'STRINGTYPE':  7,
        'TEXT':        2,
        'TIME':        3,
        'TIMESTAMP':   4,
        'VARBINARY':   5,
        'VARCHAR':     6,}
    return editor[leg]

class GenericDBClass( object):
    """"""
    pass

class SqlTable( wx.grid.PyGridTableBase):
    from datetime import datetime
    def __init__( self, engine= None, tableName= None, allow2edit= False):
        self.allow2edit=     allow2edit
        self._currTable=     None
        self._initializeParams()
        self._numCols=        0
        self._numRows=        None
        self._filter=         ''
        self._colsInfo=       {}
        self.currsession=     None
        self.__commit=        True
        self.__closeSession=  True
        self.__updateBuffer=  True
        wx.grid.PyGridTableBase.__init__(self)
        
        if engine == None:
            self.loadDatabase( evt = None)
        else:
            self.engine= engine
            if tableName == None:
                if len(self.tableNames) > 0:
                    tableName= self.tableNames[0]
                else:
                    return
            # once the currtable changes, also the data is autonatically loaded
            self.currTable= tableName
            
        
        # getting the information of the column
        self._colsInfo= self.getColsInfo()
        
        self._numRows= self.numRows
        self._numCols= self.GetNumberCols()
    def AppendCols(self, numCols= 1):
        pass
    def _setcommit(self, commitStatte):
        if commitStatte== False:
            self.__commit= commitStatte
        else:
            self.__commit= True

    def _initializeParams(self, udpdateNumrows= False):
        # used to initialize the data if the user change the selected table
        self.bufer=          dict()
        self.oldRowSelected= None
        self.curRowData=     None
        self.currDataRowChanging=   dict()# a dict containing all modified rows until the next commit
        # Used when changing the table
        if udpdateNumrows:
            self._numRows= None
            self.numRows()

    def GetAttr(self, row, col, kind):
        if (row) % 3 == 0:
            attr= self.tirdAttr
        elif (row+1) % 3 == 0:
            attr= self.oddAttr
        else:
            attr= self.evenAttr
        attr= attr[col]
        attr.IncRef()
        return attr

    def getColsInfo( self, evt= None):
        # it's used to read the type of columns of the selected table
        # and interact with the
        # getting the current table
        table= self.table
        desc=  OrderedDict()
        for colName in table.columns.keys():
            desc[colName]= table.columns.get(colName).type.__visit_name__
        return desc

    def loadDatabase( self, evt):
        wildcard = "All files (*.*)|*.*"
        dlg = wx.FileDialog(
            None, message="Choose a file",#defaultDir=self.current_directory,
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
        )
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        db_path= dlg.GetPath()
        dlg.Destroy()
        self.engine= create_engine('sqlite:///%s' % db_path, echo=False)
        self.table_names = self.engine.table_names()
        # displays the current tablenames and let the user to choosen one
        txt1 = ('StaticText', ('Tablas disponibles',))
        btnChoice= ('Choice',(self.table_names,))
        structure= list()
        structure.append([txt1])
        structure.append([btnChoice])
        dlg= Dialog(parent= None, struct= structure)
        values= []
        if dlg.ShowModal() == wx.ID_OK:
            values= dlg.GetValue()
        dlg.Destroy()

        try:
            self.currTable= values[0]
        except IndexError:
            # try to load the first table
            self.currTable= self.table_names[0]

        self.loadTable(evt= None)
        
    def _updateRenderer(self):
        editor= {'DATE': datePickerEditor,
                 }
        render={'REAL': floatRenderer(4),
                'INTEGER': floatRenderer(0),
                 }
        #  creating attr by column
        self.oddAttr=  list()
        self.evenAttr= list()
        self.tirdAttr= list()
        
        for colType in self.getColsInfo().values():
            # the rederer is a global property for the sheet
            self.oddAttr.append(  wx.grid.GridCellAttr())
            self.oddAttr[-1].SetBackgroundColour( wx.Colour( 68, 155, 241 ))
            self.evenAttr.append( wx.grid.GridCellAttr())
            self.evenAttr[-1].SetBackgroundColour( wx.Colour( 246, 176, 54))
            self.tirdAttr.append( wx.grid.GridCellAttr())
            self.tirdAttr[-1].SetBackgroundColour( wx.Colour( 250, 250, 250 ))
            # RENDERER
            try:
                rend= render[colType]
                self.oddAttr[-1].SetRenderer( rend)
                self.evenAttr[-1].SetRenderer( rend)
                self.tirdAttr[-1].SetRenderer( rend)
            except KeyError:
                pass
            # EDITOR
            try:
                edit= editor[colType]
                self.oddAttr[-1].SetEditor( edit())
                self.evenAttr[-1].SetEditor( edit())
                self.tirdAttr[-1].SetEditor( edit())
            except KeyError:
                pass

    @property
    def tableNames(self):
        return self.engine.table_names()

    @property
    def currTable(self):
        return self._currTable

    @currTable.setter
    def currTable(self, tableName):
        if tableName in self.tableNames:
            self._currTable= tableName
            # emptying the buffer content
            self._initializeParams( )
            # updating the required fields
            self.loadTable(evt= None)
            #updating the renderer
            self._updateRenderer()
            notifications= {'delRow': wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,
                            'addRow': wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED,
                            'delCol': wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED,
                            'addCol': wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED,}

            difCol= self.GetNumberCols()-self._numCols
            if difCol != 0:
                if difCol > 0: # add cols
                    msg = wx.grid.GridTableMessage(self, notifications['addCol'],
                                                   difCol)   # how many
                else:     # deleting cols
                    msg = wx.grid.GridTableMessage(self, notifications['delCol'],
                                                   self._numCols, # position
                                                   -difCol)   # number of columns
                try:
                    self.GetView().ProcessTableMessage(msg)
                except AttributeError:
                    pass
                # uodating the current number of columns
                self._numCols= self.GetNumberCols()

            difRow= self.GetNumberRows()-[0, self._numRows][self._numRows!=None]
            if difRow != 0:
                if difRow > 0:
                    msg = wx.grid.GridTableMessage(self, notifications['addRow'],
                                                   difRow)   # how many
                else:
                    msg = wx.grid.GridTableMessage(self, notifications['delRow'],
                                                   self._numRows, # row
                                                   -difRow)   # number of rows
                try:
                    self.GetView().ProcessTableMessage(msg)
                except AttributeError:
                    pass
                # updating the current number of rows
                self._numRows= self.GetNumberRows()
                pass
            # update the column rendering plugins
            #self._updateColAttrs(grid)

            # update the scrollbars and the displayed part of the grid
            #self.AdjustScrollbars()
        else:
            raise StandardError("%s doesn't exist"%tableName)

    def loadTable( self, evt=None):
        metadata=       MetaData( self.engine)
        self.table=     Table( self.currTable, metadata, autoload=True, autoload_with=self.engine)
        self.colLabels= self.table.columns.keys()
        self.colTypes=  self._getColTypes(self.table)
        clear_mappers() #http://docs.sqlalchemy.org/en/rel_0_6/orm/mapper_config.html#sqlalchemy.orm.clear_mappers
        mapper( GenericDBClass, self.table)
        self.Session=   sessionmaker( bind = self.engine)
        # updating the columns info
        self._colsInfo= self.getColsInfo()
        #self._filter= ''# reset the filter

    def _getColTypes(self, table):
        # Getting the column types as string
        types= list()
        for col in [table.columns.get(colname) for colname in table.columns.keys()]:
            types.append( col.type.__str__())
        return types

    @property
    def numRows( self):
        if self._numRows== None:
            self._numRows= self.GetNumberRows()
        return self._numRows
    
    def _refresTable(self, evt= None):
        self.currTable= self.currTable[:]
        
    def checkTableName( self, tableName):
        if not tableName in self.engine.table_names():
            return False
        return True

    def GetNumberRows( self):
        session= self.Session()
        res=     session.query(GenericDBClass)# applaying the filter
        try:
            res= res.filter(self._filter)
        except:
            raise StandardError("filter error")
        finally:
            numberRows= res.count()+1
            session.close()
            return numberRows

    def GetNumberCols( self):
        return len(self._getColTypes(self.table))

    def IsEmptyCell( self, row, col):
        try:
            return not self.GetValue(row, col)
        except IndexError:
            return True

    def getBufer( self, row):
        # se consulta la informacion de la base de datos
        if self.oldRowSelected == None:
            self.updateBuffer( row) # the first id element is 1 not 0
            self.oldRowSelected= row

        self.oldRowSelected= row
        try:
            curRowData= self.bufer[row ]#
        except KeyError:
            if row >= self.numRows:
                return [None]*len( self.colLabels)
            self.updateBuffer( row)
            curRowData= self.bufer[row ]#+ self.initId
        return curRowData

    def updateBuffer( self, row, forceRefresh= False):
        # around the row selected
        if row > self.numRows:
            self.bufer[row]= [None]*len( self.colLabels)
            return

        rowMin=      max( [0, row-SEARCHINDEX])
        rowMax=      min( [self.numRows-1, row+SEARCHINDEX])
        # emptying the not needed keys in buffer
        neededRange= range( rowMin, rowMax)
        # the position in buffer is equal to the position in the grid
        for key in self.bufer.keys():
            if not( key in neededRange):
                self.bufer.pop( key)

        # populating the buffer again
        existingKeys=  self.bufer.keys()
        required=      list()
        for rowNumber in numpy.arange( rowMin, rowMax, dtype= int):
            if rowNumber in existingKeys:
                continue
            else:
                required.append( rowNumber)

        if forceRefresh:
            required.append( row)

        if row == self.numRows-1:
            self.bufer[row]= [None]*len( self.colLabels)

        if len(required) == 0:
            # nothing to update
            return

        # check the maximum and minimum required row positions
        minRequiredDb, maxRequiredDb= (min( required), max( required))
        session=     self.Session()
        rows=        session.query( GenericDBClass).filter(self._filter).offset( minRequiredDb).limit( maxRequiredDb-minRequiredDb+1).all()
        session.close()
        rowResults=  self._getRowValues( rows)
        for pos, rowContents in enumerate( rowResults):
            self.bufer[minRequiredDb+pos]= rowContents
        # in case the row is the last then adding None data as the last element

    def _getRowValues( self, rowContents):
        result= list()
        for row in rowContents:
            rowList= list()
            for attr in self.colLabels:
                # check if the row contain data
                try:
                    rowList.append( getattr( row, attr))
                except AttributeError:
                    rowList.append(None)
            result.append(rowList)

        return result#[[getattr( row, attr) for attr in self.colLabels] for row in rowContents]

    def GetValue(self, row, col):
        value= self.getBufer(row)[col]
        if value== None:
            return u""
        return "%s" % (value)
    def bufferValue(self, row, data):
        # it's used to contain the data to upload to the database
        pass
    
    def setCommit(self, state):
        if isinstance(state,(bool,)):
            self.__commit= state
        else:
            raise StandardError('The estate of the commit must be a boolean')                

    def SetValue( self, row, col, value):
        # when editing a column value the filter must be freezed
        if not self.allow2edit:
            return
        
        # identifying if it's a date object
        columnType= self._colsInfo.values()[col]
        if columnType == 'DATE':
            value= [int(val) for val in value.split('-')]
            value= self.datetime(value.pop(0), value.pop(0), value.pop(0))
        elif columnType == 'REAL':
            value= float(value)
        
        # create a Session
        if self.currsession== None:
            self.currsession = self.Session()
            self.currDataRowChanging= dict()
                
        # querying for a record in the Artist table
        rowNumber= row # self.GetValue(row, 0)
        if rowNumber < self.numRows-1: #u''
            if not rowNumber.__str__() in self.currDataRowChanging:
                res= self.currsession.query( GenericDBClass)
                try:
                    res= res.filter(self._filter)
                except:
                    raise StandardError('aplying filter error')
                finally:
                    res= res[ long( rowNumber)]
                self.currDataRowChanging[rowNumber.__str__()]= res
            else:
                res= self.currDataRowChanging[rowNumber.__str__()]
        else:
            res= None

        if res == None:
            if row >= self.numRows-1:
                # se adiciona un registro nuevo
                newRegsitry= GenericDBClass()
                setattr(newRegsitry, self.colLabels[col], value)
                self.currsession.add(newRegsitry)
                if self.__commit:
                    self.currsession.commit()
                    self.updateBuffer(row, forceRefresh= True)
                    self.currsession.close()
                    self.currsession=  None

                self._numRows+= 1 # add one column

                self.currDataRowChanging= dict()

                if self._filter == u'':
                    # tell the grid we've added a row
                    msg = wx.grid.GridTableMessage(self,            # The table
                                            wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                                            1                                       # how many
                                            )
                    self.GetView().ProcessTableMessage(msg)
                # updating the number of rows to solve the issue when paste values
                return
        else:
            setattr(res, self.colLabels[col], value) ##required to be changed to allow non numerical values
            if self.__commit:
                self.currsession.commit()
                self.currsession.close()
                self.currsession= None
                self.currDataRowChanging= dict()
                self.updateBuffer(row, forceRefresh= True)
                # is missing to update the grid
                self.GetView().Refresh()
                
    def commit(self):
        self.__commit= True
        if self.currsession == None:
            self.currsession = self.Session()

        self.currsession.commit()
        self.currsession.close()
        self.currsession= None
        self._emptyTheBuffer()
        self.GetView().Refresh()
        
    def _emptyTheBuffer(self):
        self.bufer= dict()
    def GetColLabelValue( self, col):
        return self.colLabels[col]

    def GetRowLabelValue( self, row):
        return row.__str__()
    
    def applySqlFilter(self, SQLString):
        self._filter= SQLString
        self._refresTable()
    # to be implemented
    def DeleteCols(self, pos= 0, numCols= 1):
        pass

    def DeleteRows(self, pos= 0, numRows= 1):
        rowNumber= pos
        if not isnumeric(rowNumber):
            raise StandardError("The row number must be a numeric variable")

        if rowNumber < 0:
            raise StandardError("The row number to eliminate must be greater than zero")
        #elif rowNumber > self.NumberRows:
        #    raise StandardError("The maximum number to delete is %i"%self.NumberRows)
        session= self.Session()
        # transform the rownumber to _idNumber
        idNumber= self.GetValue(rowNumber,0)
        try:
            res= session.query(GenericDBClass).filter(self._filter).filter(GenericDBClass._id == idNumber).one()
            session.delete(res)
            session.commit()
            msg = wx.grid.GridTableMessage(self,            # The table
                                        wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, # what we did to it
                                        pos, # position
                                        1                                       # number of rows
                                        )
            self.GetView().ProcessTableMessage(msg)
            self._numRows-= 1
            self._emptyTheBuffer()
        finally:
            session.close()

class SqlGrid( wx.grid.Grid, object): # wx.grid.Grid
    DEFAULT_FONT_SIZE= 12
    def __init__(self, parent, engine= None, tableName= None, allow2edit= False):
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
        wx.grid.Grid.__init__(self, parent)
        #wx.grid.Grid.__init__( self, parent)
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

        # functions to copy paste
        if len([clase for clase in wx.grid.Grid.__bases__ if issubclass( PyWXGridEditMixin, clase)]) == 0:
            wx.grid.Grid.__bases__ += ( PyWXGridEditMixin,)
        # contextual menu
        self.__init_mixin__()
        
        self.table= SqlTable( engine, tableName, allow2edit)
        self.SetTable( self.table, True)
        self._currTable= self.table.currTable

        if wx.Platform == '__WXMAC__':
            self.SetGridLineColour("#b7b7b7")
            self.SetLabelBackgroundColour("#d2d2d2")
            self.SetLabelTextColour("#444444")
        else:
            self.SetLabelBackgroundColour( wx.Colour( 254, 226, 188 ) )

        self.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        
        self.Bind( wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnGridRighClic)
        self.Bind( EVT_GRID_BEFORE_PASTE, self.onBeforePaste)
        self.Bind( EVT_GRID_PASTE, self.Onpaste)
        self.Bind( wx.EVT_MOUSEWHEEL,                       self.__OnMouseWheel)
        self.Bind( wx.grid.EVT_GRID_COL_SIZE, self.__OnColSizeChange)
        
    def onBeforePaste(self, evt):
        self.table.setCommit(False)
        print "on before paste"
        evt.Skip()
    def Onpaste(self, evt):
        self.table.commit()
        print "paste the data"
        evt.Skip()

    def OnGridRighClic(self,evt):
        self.PopupMenu(MyContextGrid(self), evt.GetPosition())
        evt.Skip()
        
    def OnKeyDown(self, evt):
        if evt.GetKeyCode() != wx.WXK_RETURN:
            evt.Skip()
            return

        if evt.ControlDown():   # the edit control needs this key
            evt.Skip()
            return

        self.DisableCellEditControl()
        success = self.MoveCursorRight(evt.ShiftDown())

        if not success:
            newRow = self.GetGridCursorRow() + 1

            if newRow < self.GetTable().GetNumberRows():
                self.SetGridCursor(newRow, 0)
                self.MakeCellVisible(newRow, 0)
            else:
                # this would be a good place to add a new row if your app
                # needs to do that
                pass

    @property
    def tableNames(self):
        return self.table.tableNames

    @property
    def currTable(self):
        return self.table.currTable
    @currTable.setter
    def currTable(self, table):
        self.table.currTable= table

    def UpdateValues(self):
        """Update all displayed values"""
        # This sends an event to the grid table to update all of the values
        msg = wx.grid.GridTableMessage(self.table,
                                       wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.ProcessTableMessage(msg)

    def applySqlFilter(self, sqltxt):
        self.table.applySqlFilter(sqltxt)
    def clearSqlFilter(self):
        self.table._filter= ""
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

    # aditional methods to be like newgrid
    #-----------------------------------------
    # zoom rows and cols labels-- missing all cell renderer
    def __zoom_rows(self):
        """Zooms grid rows"""
        self.SetDefaultRowSize( self.defaultRowSize*self.zoom, resizeExistingRows=True)
        self.SetRowLabelSize( self.defaultRowLabelSize * self.zoom)

    def __zoom_cols(self):
        """Zooms grid columns"""
        tabno = 1 #self.current_table
        for colno in xrange(1,self.GetNumberCols()):# preventing show the _id column
            self.SetColSize(colno, self.defaultColSize * self.zoom)
        self.SetColLabelSize(self.defaultColLabelSize * self.zoom)

    def __zoom_labels(self):
        """Zooms grid labels"""
        labelfont = self.GetLabelFont()
        labelfont.SetPointSize(max(1, int(self.DEFAULT_FONT_SIZE * self.zoom)))
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
    #-----------------------------------------
    def __OnColSizeChange(self, evt):
        self.SetColSize(0, 0)
        evt.Skip()

    @property
    def colNames(self):
        return [self.GetColLabelValue(col) for col in range(self.GetNumberCols())]

    def _getCol(self, colNumber, includeHeader= False):
        if isinstance(colNumber, (str, unicode)):
            # searching for a col with the name:
            if not(colNumber in self.colNames):
                raise TypeError('You can only use a numeric value, or the name of an existing column')
            colName= colNumber
        elif isnumeric(colNumber):
            if colNumber >=0:
                colNumber+=1
            elif colNumber < 0:
                if abs(colNumber) > len(self.colNames):
                    raise StandardError("None existent index")
                colNumber= len(self.colNames) - abs(colNumber)
            if colNumber > self.GetNumberRows():
                raise StandardError('The maximum column allowed is %i, but you selected %i'%(self.GetNumberCols()-1, colNumber))
            colName= self.colNames[colNumber]
        else:
            raise TypeError('You can only use a column name or a numeric value, or the name of an existing column')
        # executing the sql
        session=     self.table.Session()
        rows=        session.query( getattr( GenericDBClass, colName)).filter( self.table._filter).all()
        session.close()
        index= [0, 1][includeHeader]
        return rows[index:]

    def _getRow( self, rowNumber):
        if not isnumeric(rowNumber):
            raise TypeError('You can only use a numeric value of an existent column')
        # executing the sql
        session=   self.table.Session()
        row=       session.query( GenericDBClass).filter( self.table._filter).offset( rowNumber).limit(1).all()[0]
        session.close()
        # getting the data
        lista= list()
        for colName in self.colNames[1:]: ## since 1 to prevent to getting the _id column
            lista.append( getattr(row, colName))
        return numpy.array(lista)

    def GetCol(self, col, hasHeader= False):
        return numpy.array([col[0] for col in self._getCol( col, hasHeader)]) # self._cleanData( self._getCol( col, hasHeader))

    def GetRow(self, row):
        return self._getRow( row) # self._cleanData( self._getRow( row))
    # to be updated
    def GetUsedCols(self):
        return [self.colNames[1:], range(1,len(self.colNames))]

    def PutCol(self, colNumber, data):
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

            if colNumber < 0:
                colNumber= len(self.colNames)-abs(colNumber)
                if colNumber < 1:
                    raise StandardError('Index out of range')
            else:
                colNumber+=1 # avoiding the first column '_id'

            colNumber= int(colNumber)+1 ##
            if colNumber < 0 or colNumber > self.GetNumberCols():
                raise StandardError('The minimum accepted col is 0, and the maximum is %i'%self.GetNumberCols()-1)

            colName= self.colNames[colNumber]

            if isinstance( data,(str, unicode)):
                data= [data]

            if isinstance( data, (int, long, float)):
                data= [data]

            if isinstance( data, (ndarray),):
                data= ravel( data)


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
            # stop commit values
            self.table._setcommit(False)
            try:
                for row, dat in enumerate(newdat):
                    self.SetCellValue(row, colNumber, dat)
            finally:
                self.table._setcommit(True)
            self.table.commit()
        except:
            raise
        finally:
            self.hasSaved= False
            self.hasChanged= True
    def GetColNumeric(self, colNumber, includeHeader= False):
        if isinstance(colNumber, (str, unicode)):
            # searching for a col with the name:
            if not(colNumber in self.colNames):
                raise TypeError('You can only use a numeric value, or the name of an existing column')
            colName= colNumber
        elif isnumeric(colNumber):
            if colNumber >=0:
                colNumber+=1
            elif colNumber < 0:
                if abs(colNumber) > len(self.colNames):
                    raise StandardError("None existent index")
                colNumber= len(self.colNames) - abs(colNumber)
            if colNumber > self.GetNumberRows():
                raise StandardError('The maximum column allowed is %i, but you selected %i'%(self.GetNumberCols()-1, colNumber))
            colName= self.colNames[colNumber]
        else:
            raise TypeError('You can only use a column name or a numeric value, or the name of an existing column')
        # executing the sql
        session=  self.table.Session()
        rows=     session.query( getattr( GenericDBClass, colName)).\
                        filter( self.table._filter).\
                        filter( getattr(GenericDBClass, colName ) != None).\
                        all()
        rows= [row for row in [row[0] for row in rows] if isnumeric(row)]
        session.close()
        index= [0, 1][includeHeader]
        return rows[index:]

class selectDbTableDialog( wx.Dialog):
    def __init__(self, parent,engine,tableName= None, allow2edit= False):
        wx.Dialog.__init__(self, parent,
                           id=    wx.ID_ANY,
                           title= "Choose a table",
                           size=  (640,480))

        self.m_mgr=  wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )
        self.m_mgr.SetFlags(wx.aui.AUI_MGR_DEFAULT)
        self.m_grid= SqlGrid( self, engine, tableName, allow2edit)

        self.m_listBox2Choices= self.m_grid.tableNames
        if len(self.m_listBox2Choices) > 0:
            selected= 0

        self.selectedTableName= self.m_listBox2Choices[selected]
        self.m_listBox= wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.m_listBox2Choices, selected )

        self.okCancel=  okCancelPanel(self, wx.ID_ANY)
        
        self.txtCtrl=   wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
        self.aplyFilterButtom = wx.Button( self, wx.ID_ANY, u"Apply Filter", wx.DefaultPosition, wx.DefaultSize, 0 )
        
        self.m_mgr.AddPane( self.aplyFilterButtom, wx.aui.AuiPaneInfo() .Bottom() .
                            CaptionVisible( False ).CloseButton( False ).PaneBorder( False ).
                            Movable( False ).Dock().Fixed().
                            DockFixed( False ).Floatable( False ).Row( 0 ) )
		

        self.m_mgr.AddPane( self.m_listBox, wx.aui.AuiPaneInfo().Left().
                            CaptionVisible(True).Caption('Existent Tables').
                            MaximizeButton(True).MinimizeButton(False).Resizable(True).
                            PaneBorder( False ).CloseButton( False ).MinSize( wx.Size( 120,-1 )))

        self.m_mgr.AddPane( self.m_grid, wx.aui.AuiPaneInfo().Centre().
                            CaptionVisible(True).Caption('Table contents').
                            MaximizeButton(True).MinimizeButton(False).Resizable(True).
                            PaneBorder( False ).CloseButton( False ))
        
        self.m_mgr.AddPane( self.txtCtrl, wx.aui.AuiPaneInfo().Left().
                            CaptionVisible(True).Caption('Filter').
                            MaximizeButton(True).MinimizeButton(False).Resizable(True).
                            PaneBorder( False ).CloseButton( False ))

        self.m_mgr.AddPane( self.okCancel, wx.aui.AuiPaneInfo().Bottom().
                            CaptionVisible(False).CloseButton( False ).
                            BestSize( wx.Size(-1, 35))
                            )

        self.currTableNumber= [pos for pos, tab in enumerate(self.m_grid.tableNames) if tab == self.m_grid.currTable][0]
        self.m_mgr.Update()
        self.Center()
        self.m_listBox.Bind( wx.EVT_LISTBOX, self._onListBoxElementSelected )
        self.aplyFilterButtom.Bind( wx.EVT_BUTTON, self.applyFilter)
        #self.okCancel.okButton.Bind( wx.EVT_BUTTON, self.ok )
        #self.okCancel.cancelButton.Bind( wx.EVT_BUTTON, self.cancel )

    def _onListBoxElementSelected(self, evt, *args, **params):
        currSelectionNumber= evt.GetSelection()
        if currSelectionNumber >= 0:
            if currSelectionNumber != self.currTableNumber:
                self.selectedTableName= self.m_listBox2Choices[currSelectionNumber]
                # clear the filter
                self.m_grid.clearSqlFilter()
                self.currTableNumber= currSelectionNumber
                # changing the selection of the table in the grid
                self.m_grid.currTable= evt.GetString()
                ## talking to the grid to udate it
                ## self.GetView().Refresh() # .table.
            else:
                return
            
    def applyFilter(self, evt):
        print "filtering data"
        self.m_grid.applySqlFilter( self.txtCtrl.GetValue())
        evt.Skip()
    
    def GetValue(self):
        return (self.selectedTableName, self.m_grid.table._filter)

    def Destroy(self, *args, **params):
        self.m_mgr.UnInit()

class _example( wx.Frame ):
    def __init__( self, parent ):
        self.name= 'selobu'
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY,
                            title = wx.EmptyString, pos = wx.DefaultPosition,
                            size = wx.Size( 200, 200 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer10 = wx.BoxSizer( wx.VERTICAL )

        self.m_button8 = wx.Button( self, wx.ID_ANY, u"Show Dialog", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer10.Add( self.m_button8, 0, wx.ALL, 5 )

        self.SetSizer( bSizer10 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_button8.Bind( wx.EVT_BUTTON, self.showDialog )
        
    # Virtual event handlers, overide them in your derived class
    def showDialog( self, evt ):
        dbPath= 'e:\\proyecto gridsql\\mymusic01.db'
        #dbPath= ':temp:'
        engine= create_engine('sqlite:///%s'%dbPath, echo=False)
        dlg= selectDbTableDialog(self, engine,allow2edit= True)
        if dlg.ShowModal() == wx.ID_OK:
            values= dlg.GetValue()
            print values
        dlg.Destroy()

if __name__ == '__main__':
    app=   wx.App()
    frame= _example(None)
    frame.Show()
    app.MainLoop()