'''
Created on 26/10/2012

@author: USUARIO
'''
import wx
import wx.grid
import wx.aui
import numpy
from salstat2_glob import *
from sqlalchemy import Table, MetaData, create_engine
from sqlalchemy.orm import mapper, sessionmaker, clear_mappers
from sqlalchemy.exc import StatementError
from easyDialog import Dialog, Busy
from gridEditors import VARCHAR
from gridEditors import DATE
from gridCellRenderers import floatRenderer
from collections import OrderedDict
SEARCHINDEX= 70
DECIMAL_POINT = '.'

from gridEditors import datePickerEditor
from GridCopyPaste import PyWXGridEditMixin, MyContextGrid
from GridCopyPaste import EVT_GRID_BEFORE_PASTE, EVT_GRID_PASTE
from gridLib.NewGrid import NewGrid
from slbTools.slbTools import isnumeric
from numpy import ndarray, ravel
from copy import deepcopy
from xlrd import xldate_as_tuple

# definig some custom events
NewTableEvt, EVT_SQLGRID_NEW_TABLE = wx.lib.newevent.NewCommandEvent()
evtIDNewTable = wx.NewEventType()

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

class GenericDBClass(object):
    """"""
    pass

class SqlTable( wx.grid.PyGridTableBase):
    import datetime
    _currTable=      None
    def __init__( self, engine= None, tableName= None, allow2edit= False, firstColEditable= True):
        self._firstColEditable= firstColEditable
        self.genericDBClass=  GenericDBClass
        self.allow2edit=      allow2edit
        self._colsinfo=       None
        #self._currTable=      None
        self._initializeParams()
        self._numCols=        0
        self._numRows=        None
        self._filter=         ''
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
        
        # forcing to update the columns info
        ##self._colsinfo= None
        self._numRows= self.numRows
        self._numCols= self.GetNumberCols()
        
    def setEngine(self, engine):
        self.engine= engine
    
    def _clearmapper(self):
        class GenericDB:# object 
            """"""
            pass
        self.genericDBClass=  GenericDB()
        clear_mappers()
        mapper(self.genericDBClass, self.table)

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
        self.currDataRowChanging=  OrderedDict()# a dict containing all modified rows until the next commit
        self._newDataRowChanging= OrderedDict()
        self._rows2append= 0
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
        if self._colsinfo == None:
            print _("Updating columns information")
            table= self.table
            desc=  OrderedDict()
            for colName in table.columns.keys():
                desc[colName]= table.columns.get(colName).type.__visit_name__
            self._colsinfo= deepcopy(desc)

        return self._colsinfo

    def loadDatabase( self, evt):
        wildcard = "All files (*.*)|*.*"
        dlg = wx.FileDialog(
            None, message=_("Choose a file"),#defaultDir=self.current_directory,
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
        txt1 = ('StaticText', (_('Available tables'),))
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
        editor= {'DATE':     datePickerEditor}
        render= {'DATE':     floatRenderer,
                 'STRING':   floatRenderer,
                 'VARCHAR':  floatRenderer}
        #  creating attr by columns
        self.oddAttr=  list()
        self.evenAttr= list()
        self.tirdAttr= list()
        
        for pos, colType in enumerate(self.getColsInfo().values()):
            # the rederer is a global property for the sheet
            self.oddAttr.append(  wx.grid.GridCellAttr())
            self.oddAttr[-1].SetBackgroundColour( wx.Colour( 68, 155, 241 ))
            self.evenAttr.append( wx.grid.GridCellAttr())
            self.evenAttr[-1].SetBackgroundColour( wx.Colour( 246, 176, 54))
            self.tirdAttr.append( wx.grid.GridCellAttr())
            self.tirdAttr[-1].SetBackgroundColour( wx.Colour( 250, 250, 250 ))
            try:
                edit= editor[colType.upper()]
                if pos == 0 and not self._firstColEditable:
                    self.oddAttr[-1].SetReadOnly(True)
                    self.evenAttr[-1].SetReadOnly(True)
                    self.tirdAttr[-1].SetReadOnly(True)
                else:
                    self.oddAttr[-1].SetEditor( edit())
                    self.evenAttr[-1].SetEditor( edit())
                    self.tirdAttr[-1].SetEditor( edit())
            except KeyError:
                pass
            try:
                renderer= render[colType.upper()] 
                self.oddAttr[-1].SetRenderer( renderer(4))
                self.evenAttr[-1].SetRenderer( renderer(4))
                self.tirdAttr[-1].SetRenderer( renderer(4))
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
                                                   self._numCols+difCol, # position
                                                   -difCol)   # number of columns
                try:
                    self.GetView().ProcessTableMessage(msg) # self.GetView()
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
                                                   self._numRows+difRow, # row
                                                   -difRow)   # number of rows
                try:
                    self.GetView().ProcessTableMessage(msg)# GetView().
                except AttributeError:
                    pass
                # updating the current number of rows
                self._numRows= self.GetNumberRows()


            # update the column rendering plugins
            #self._updateColAttrs(grid)

            # update the scrollbars and the displayed part of the grid
            #self.AdjustScrollbars()
        else:
            raise StandardError(_("%s doesn't exist")%tableName)

    def loadTable( self, evt=None):
        metadata=       MetaData( self.engine)
        self.table=     Table( self.currTable, metadata, autoload=True, autoload_with=self.engine)
        self.colLabels= self.table.columns.keys()
        self.colTypes=  self._getColTypes(self.table)
        clear_mappers() #http://docs.sqlalchemy.org/en/rel_0_6/orm/mapper_config.html#sqlalchemy.orm.clear_mappers
        mapper( self.genericDBClass, self.table)
        self.Session=   sessionmaker( bind = self.engine)
        # updating the columns info
        self.__colsInfo= []
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
        res=     session.query(self.genericDBClass)# applaying the filter
        try:
            res= res.filter(self._filter)
        except:
            raise StandardError("filter error")
        finally:
            numberRows= res.count()+1
            session.close()
            return numberRows

    def GetNumberCols( self):
        return len(self.table.columns)

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

        rowMin= max( [0, row-SEARCHINDEX])
        rowMax= min( [self.numRows-1, row+SEARCHINDEX])
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
        session=  self.Session()
        rows=     session.query( self.genericDBClass).filter( self._filter).offset( minRequiredDb).limit( maxRequiredDb-minRequiredDb+1).all()
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
        
        # create a Session
        if self.currsession== None:
            self.currsession = self.Session()
            self.currDataRowChanging= OrderedDict()
            self._newDataRowChanging= OrderedDict()
            self._rows2append= 0

        rowNumber= row # self.GetValue(row, 0)

        if self.__commit:
            if rowNumber < self.numRows-1: #u''
                if not (rowNumber.__str__() in self.currDataRowChanging):
                    res= self.currsession.query( self.genericDBClass) #GenericDBClass
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
                    self._numRows+=      1 # add one column
                    self._rows2append+= 1 # tell the grid the rows to append
                    newRegsitry=   self.genericDBClass()

                    setattr(newRegsitry, self.colLabels[col], self.__fromGridToDB(value, col))

                    if not (rowNumber in self._newDataRowChanging):
                        self._newDataRowChanging[rowNumber]= OrderedDict()

                    self._newDataRowChanging[rowNumber][self.colLabels[col]]= self.__fromGridToDB(value, col)
                    self.currsession.add(newRegsitry)
                    self.currsession.commit()
                    self.updateBuffer(row, forceRefresh= True)
                    self.currsession.close()
                    self.currsession=  None
                    self.currDataRowChanging= OrderedDict() # changing

                    if self._filter == u'':
                        # tell the grid we've added a row
                        msg = wx.grid.GridTableMessage(self,            # The table
                                       wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                                       1                                       # how many
                                        )
                        self.GetView().ProcessTableMessage(msg)
                        self._rows2append= 0
                    # updating the number of rows to solve the issue when paste values
                    return
            else:
                setattr(res, self.colLabels[col], self.__fromGridToDB(value, col)) ##required to be changed to allow non numerical values
                self.currsession.commit()
                self.currsession.close()
                self.currsession= None
                self.currDataRowChanging= OrderedDict()
                self._newDataRowChanging= OrderedDict()
                self.updateBuffer(row, forceRefresh= True)
                # is missing to update the grid
                self.GetView().Refresh()
        else:
            # updating multiple information at one time
            if rowNumber < self.numRows-1: #u''
                if not (rowNumber.__str__() in self.currDataRowChanging):
                    res= 1
                    if not (rowNumber in self._newDataRowChanging):
                        self._newDataRowChanging[rowNumber]= OrderedDict() # adding a new record
                        self._newDataRowChanging[rowNumber]['_id']= rowNumber+1
                else:
                    res= 1
            else:
                res= None

            if res == None:
                if row >= self.numRows-1:
                    # se adiciona un registro nuevo
                    self._numRows+=      1 # add one column
                    self._rows2append+= 1 # tell the grid the rows to append

                    #setattr(newRegsitry, self.colLabels[col], self.__fromGridToDB(value, col))
                    if not (rowNumber in self._newDataRowChanging):
                        self._newDataRowChanging[rowNumber]= OrderedDict()
                        self._newDataRowChanging[rowNumber]['_id']= rowNumber+1
                    self._newDataRowChanging[rowNumber][self.colLabels[col]]= self.__fromGridToDB(value, col)
                    return
            else:
                #setattr(res, self.colLabels[col], self.__fromGridToDB(value, col)) ##required to be changed to allow non numerical values
                if not (rowNumber in self._newDataRowChanging):
                    self._newDataRowChanging[rowNumber]= OrderedDict()
                    self._newDataRowChanging[rowNumber]['_id']= rowNumber+1
                self._newDataRowChanging[rowNumber][self.colLabels[col]]= self.__fromGridToDB(value, col)

    def __fromGridToDB(self, value, column):
        # identifying the column type
        coltype= self.colTypes[column].upper()
        # translating the string or unicode value to it's corresponding on database
        if coltype in ('STRING',):
            pass
        elif coltype in ('REAL','FLOAT'):
            value= float(value)
        elif coltype in ('INT'):
            value= int(value)
        elif coltype in ('DATE',):
            value= [int(val) for val in value.split('-')]
            value= self.datetime.date(value.pop(0), value.pop(0), value.pop(0))
        return value

    def commit(self):
        self.__commit= True
        if self.currsession == None:
            self.currsession = self.Session()

        # check if there are rows to commit
        if len(self._newDataRowChanging) > 0 and self._rows2append > 0:
            values2Insert= self._newDataRowChanging.values()[-self._rows2append:]
            conn= self.engine.connect()
            conn.execute( self.table.insert(), *values2Insert )
            conn.close()

        if len(self._newDataRowChanging) - self._rows2append !=0:
            values2update= self._newDataRowChanging.values()
            values2update= values2update[:(len(values2update)-self._rows2append)]
            keys= values2update[0].keys()
            keys= [key for key in keys if key != '_id']
            translate= lambda x: " "+x.__str__()+"=:"+ x.__str__()
            keys=      [translate(key) for key in keys]
            concat=    lambda x,y: x + "," + y
            newstr= reduce(concat, keys)
            conn= self.engine.connect()
            strSql= "UPDATE "+ self.table.__str__() +\
                " SET "  + newstr +\
                " WHERE _id=:_id"
            conn.execute(strSql ,   *values2update )
            conn.close()

        self._newDataRowChanging= OrderedDict()
        # commit the data

        self.currsession.commit()
        self.currsession.close()
        self.currsession= None
        self._emptyTheBuffer()
        # adding the needed rows
        msg = wx.grid.GridTableMessage(self,            # The table
                                       wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                                       self._rows2append                      # how many
                                       )
        self.GetView().ProcessTableMessage(msg)
        self._rows2append= 0

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
        
    def AppendCols(self, nColumns= 1, tablename= None):
        if tablename == None:
            tablename = self.currTable
        else:
            if not (tablename in self.table_names):
                raise StandardError("The selected tablename doesn't exist")
        
        from sqlalchemy import Column, String
        
        def genColname():
            init=      65
            max=       90
            data=      [init]
            currpos=   0
            concat=    lambda x,y: x+y
            while True:
                if currpos < 0:
                    data.append(init)
                    currpos= len(data)-1 # locating the current pos in the las position

                if data[currpos]> max:
                    data[currpos]= init
                    if currpos>0:
                        data[currpos-1]+=1
                    currpos-=1
                    continue
                else:
                    currpos= len(data)-1

                yield reduce(concat, [ chr(dat) for dat in data])
                data[currpos]+=1
                
        colname= genColname()
        newColNames= list()
        for i in range(nColumns):
            while True:
                newColName= colname.next() 
                if not(newColName in self.colLabels):
                    newColNames.append(newColName)
                    break # exiting the while

        ##cols= [ Column( colnamei, String, nullable= True) for colnamei in  newColNames ]
        for colnamei in newColNames:
            self.engine.execute("ALTER TABLE " + self.currTable + " ADD " + colnamei + " TEXT DEFAULT NULL")

        # updating the table information
        self.currTable= self.currTable[:]
                
    def DeleteCols(self, pos= 0, numCols= 1):
        pass
    
    def SetColLabelValue(self, pos, newColName):
        originalColumnName= ""
        if isinstance(pos, (int, float)):
            if pos < self.GetNumberCols() and pos > -1:
                pos= int(pos)
            else: 
                raise StandardError( _("The column number must be a natural value"))
            originalColumnName= pos[:]
        elif isinstance(pos, (str, unicode)):
            originalColumnName= pos[:]
        else:
            raise StandardError( _("Not allowed type for pos"))
        
        
        col=getattr( self.table.c, originalColumnName)
        col.alter(name= newColName)
        self.currTable= self.currTable[:]
            
    def DeleteRows(self, pos= 0, numRows= 1):
        rowNumber= pos
        if not isnumeric(rowNumber):
            raise StandardError( _("The row number must be a numeric variable"))

        if rowNumber < 0:
            raise StandardError( _("The row number to eliminate must be greater than zero"))
        #elif rowNumber > self.NumberRows:
        #    raise StandardError("The maximum number to delete is %i"%self.NumberRows)
        session= self.Session()
        # transform the rownumber to _idNumber
        idNumber= self.GetValue(rowNumber,0)
        try:
            res= session.query(self.genericDBClass).filter(self._filter).filter(self.genericDBClass._id == idNumber).one()
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

class SqlGrid( NewGrid):#wx.grid.Grid, object): # wx.grid.Grid
    DEFAULT_FONT_SIZE= 12
    DEFAULT_COLSIZE= (1,100)
    def __init__(self, parent, engine= None, tableName= None, allow2edit= False, firstColEditable= True):
        try:     _ = wx.GetApp()._
        except:  _ = lambda x: x
        self._= _
        self.__firstColEditable= firstColEditable
        self.nombre=   'selobu'
        self.engine=   engine
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
        
        self.table= SqlTable( self.engine, tableName, allow2edit, firstColEditable= self.__firstColEditable)
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
        self.Bind(wx.EVT_MOUSEWHEEL,                       self.__OnMouseWheel)
        
    def newTable(self, evt=  None, engine= None, tablename= None, path= None):
        if engine== None:
            engine = self.engine
        self.engine= engine
        if tablename == None:
            #<\ generating new table name
            def nameGenerator(startName):
                index= 1
                while True:
                    yield startName +index.__str__()
                    index+= 1
            newTablename= nameGenerator('newTable_')
            while True:
                tablename= newTablename.next()
                if not tablename in self.table.tableNames:
                    break
            # end generating new table name />
        tablename= self.__transformTovalidTablename(tablename)
        if tablename in self.table.tableNames:
            raise StandardError(_("The table name already exist"))
        
        if not isinstance( tablename, (str, unicode)):
            raise StandardError(_("The table name must be an string"))

        # creating a new table
        self.__createNewTable( tablename)
        # clear the filter
        self.clearSqlFilter()
        # displaying the current table
        self.table.currTable= tablename
        # procesing the event
        wx.GetApp().frame._dbExplorerPanel.GetEventHandler().ProcessEvent( NewTableEvt(evtIDNewTable))
        return tablename

    # alias for newTable
    def __transformTovalidTablename(self, oldName):
        validAsciiCharacters= list()
        tuples= (48,57+1), (65,90+1), (97,122+1)
        for tpl in tuples:
            validAsciiCharacters.extend([chr(i) for i in range(*tpl)])
        validAsciiCharacters.append('_')
        fnc= lambda x,y: x+y
        newCharacters = [c for c in oldName if c in validAsciiCharacters]
        newName = reduce(fnc,newCharacters)
        return newName

    def __createNewTable(self, tableName, size= DEFAULT_COLSIZE):
        from sqlalchemy import MetaData, Column, Table
        from sqlalchemy import Integer, String
        metadata = MetaData( bind=self.engine)
        # creating the main file
        new_table = (tableName, # brakets are used to manage nonstandar names line .kjdjf=.j
                     metadata,
                     Column('_id', Integer, primary_key= True, autoincrement= True),
                     )

        def genColname():
            init=      65
            max=       90
            data=      [init]
            currpos=   0
            concat=    lambda x,y: x+y
            while True:
                if currpos < 0:
                    data.append(init)
                    currpos= len(data)-1 # locating the current pos in the las position

                if data[currpos]> max:
                    data[currpos]= init
                    if currpos>0:
                        data[currpos-1]+=1
                    currpos-=1
                    continue
                else:
                    currpos= len(data)-1

                yield reduce(concat, [ chr(dat) for dat in data])
                data[currpos]+=1
                
        colname= genColname()

        for colNumer in range(size[1]):
            new_table+=(Column( colname.next(), String, nullable= True),)
        table= Table(*new_table)
        table.create(self.engine) 
        #metadata.create_all() fails
    
    def setEngine(self, engine):
        self.engine= engine
        
    def onBeforePaste(self, evt):
        self.table.setCommit(False)
        evt.Skip()

    @Busy
    def Onpaste(self, evt):
        self.BeginBatch()
        try:
            self.table.commit()
        finally:
            self.EndBatch()
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
    @property
    def colNames(self):
        return [self.GetColLabelValue(col) for col in range(self.GetNumberCols())]

    def SetColLabelValue(self, *args, **params):
        """SetColLabelValue(self, pos, newColName)"""
        return self.table.SetColLabelValue(*args, **params)
    
    def _getCol(self, colNumber, includeHeader= False):
        if isinstance(colNumber, (str, unicode)):
            # searching for a col with the name:
            if not(colNumber in self.colNames):
                raise TypeError(_('You can only use a numeric value, or the name of an existing column'))
            colName= colNumber
        elif isnumeric(colNumber):
            if colNumber >=0:
                colNumber+=1
            elif colNumber < 0:
                if abs(colNumber) > len(self.colNames):
                    raise StandardError(_("Index doesn't exist"))
                colNumber= len(self.colNames) - abs(colNumber)
            if colNumber > self.GetNumberCols():
                raise StandardError( _('The maximum column allowed is %i, but you selected %i')%(self.GetNumberCols()-1, colNumber))
            colName= self.colNames[colNumber]
        else:
            raise TypeError( _('You can only use a column name or a numeric value, or the name of an existing column'))
        # executing the sql
        session=     self.table.Session()
        rows=        session.query( getattr( self.table.genericDBClass, colName)).filter( self.table._filter).all()
        session.close()
        ## Try to change the values to numerical values
        newRows= rows[:]
        for pos, row in enumerate(rows):
            try:
                newRows[pos]= (float(row[0]),)
            except:
                newRows[pos]= row

        index= [0, 1][includeHeader]
        return newRows[index:]

    def _getRow( self, rowNumber):
        if not isnumeric(rowNumber):
            raise TypeError( _('You can only use a numeric value of an existent column'))
        # executing the sql
        session=   self.table.Session()
        row=       session.query( self.Parent.genericDBClass).filter( self.table._filter).offset( rowNumber).limit(1).all()[0]
        session.close()
        # getting the data
        lista= list()
        for colName in self.colNames[1:]: ## since 1 to prevent to getting the _id column
            lista.append( getattr(row, colName))
        return numpy.array(lista)

    def GetCol(self, col, hasHeader= False):
        ##numpy.array() ## removed for now
        return [col[0] for col in self._getCol( col, hasHeader)] # self._cleanData( self._getCol( col, hasHeader))

    def GetRow(self, row):
        return self._getRow( row) # self._cleanData( self._getRow( row))

    # to be updated

    def GetUsedCols(self):
        return [self.colNames[1:], range(1,len(self.colNames))]
    
    def PutRow(self, rowNumber, data):
        try:     _= wx.GetApp()._
        except:  _= lambda x: x
        try: 
            if isinstance(rowNumber, (str, unicode)):
                if not(rowNumber in self.rowNames):
                    raise TypeError(_('You can only use a numeric value, or the name of an existing row'))
                for pos, value in enumerate(self.rowNames):
                    if value == rowNumber:
                        rowNumber= pos
                        break

            if not isnumeric(rowNumber):
                raise TypeError(_('You can only use a numeric value, or the name of an existing row'))

            rowNumber= int(rowNumber)        
            if rowNumber < 0 or rowNumber > self.GetNumberRows():
                raise StandardError(_('The minimum accepted col is 0, and the maximum is %i')%self.GetNumberRows()-1)

            #self.clearRow(rowNumber)

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
                try:
                    self.SetCellValue(rowNumber, col, dat)
                except UnicodeDecodeError:
                    self.SetCellValue(rowNumber, col, dat.decode("utf-8", "replace"))
        except:
            raise
        finally:
            self.hasSaved= False
            self.hasChanged= True
                    
    def PutCol(self, colNumber, data):
        try:
            if isinstance( colNumber, (str, unicode)):
                if not(colNumber in self.colNames):
                    raise TypeError( _('You can only use a numeric value, or the name of an existing column'))
                for pos, value in enumerate(self.colNames):
                    if value == colNumber:
                        colNumber= pos-1
                        break

            if not isnumeric( colNumber):
                raise TypeError( _('You can only use a numeric value, or the name of an existing column'))

            if colNumber < 0:
                colNumber= len(self.colNames)-abs(colNumber)-1
                if colNumber < 0:
                    raise StandardError( _('Index out of range'))

            colNumber= int(colNumber)+1 # avoiding the first column '_id'
            if colNumber > self.GetNumberCols():
                raise StandardError(  _('The minimum accepted col is 0, and the maximum is %i')%self.GetNumberCols()-1)

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
                    pass
                    #try:
                    #    dat= str(float(dat.replace(dp,'.'))).replace('.',dp)
                    #except:
                    #    pass
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
        finally:
            self.hasSaved= False
            self.hasChanged= True

    def GetColNumeric(self, colNumber, includeHeader= False):
        if isinstance(colNumber, (str, unicode)):
            # searching for a col with the name:
            if not(colNumber in self.colNames):
                raise TypeError(_('You can only use a numeric value, or the name of an existing column'))
            colName= colNumber
        elif isnumeric(colNumber):
            if colNumber >=0:
                colNumber+=1
            elif colNumber < 0:
                if abs(colNumber) > len(self.colNames):
                    raise StandardError("None existent index")
                colNumber= len(self.colNames) - abs(colNumber)
            if colNumber > self.GetNumberRows():
                raise StandardError(_('The maximum column allowed is %i, but you selected %i')%(self.GetNumberCols()-1, colNumber))
            colName= self.colNames[colNumber]
        else:
            raise TypeError( _('You can only use a column name or a numeric value, or the name of an existing column'))
        # executing the sql
        session=     self.table.Session()
        rows=        session.query( getattr( self.table.genericDBClass, colName)).\
                      filter( self.table._filter).\
                      filter( getattr( self.table.genericDBClass, colName) != None ).\
                      all()
        session.close()
        ## Try to change the values to numerical values
        newRows= rows[:]
        for pos, row in enumerate(rows):
            try:
                newRows[pos]= (float(row[0]),)
            except:
                newRows[pos]= row
        index= [0, 1][includeHeader]
        rows= newRows[index:]
        newrows= [row[0] for row in rows if isnumeric(row[0])]
        return newrows

    def _LoadDbf(self, path, *arg, **params):
        from dbfpy import dbf
        db = dbf.Dbf(path)
        fieldNames= db.fieldNames
        fieldDefs= db.fieldDefs
        ##fieldDefs[colNumber].decodeValue(
        # if it's an empty database
        if len(fieldNames)== 0:
            return (True, path)
        self.table._setcommit(False)
        try:
            for rowNumber, rec in enumerate(db):
                rowdata= [rec[fieldName] for colNumber, fieldName in enumerate(fieldNames)]
                self.PutRow(rowNumber, rowdata)
        finally:
            self.table._setcommit(True)
        # setting the col label values
        #for colNumber, fieldName in enumerate(fieldNames):
        #    self.SetColLabelValue(colNumber, fieldName)
        #return (True, path)

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

        ## se hace el grid de tamanio 1 celda y se redimensiona luego
        ##self.ClearGrid()
        # reading the size of the needed sheet
        currentSize= (self.NumberRows, self.NumberCols)
        # se lee el tamanio de la pagina y se ajusta las dimensiones
        neededSize = (sheetSelected.nrows, sheetSelected.ncols)

        # number of columns
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
            pass
            #for col in range( neededSize[1]):
            #    pass
                ##self.SetColLabelValue(col, self.generateLabel( col))
        # the rows are omited
        if hasHeader and neededSize[0] < 2:
            return
        book_datemode = sheetSelected.book.datemode
        self.table._setcommit(False)
        for reportRow, row in enumerate(range( star, neededSize[0])):
            for col in range( 1,neededSize[1]+1): # the first row is the field _id
                newValue = sheetSelected.cell_value( row, col-1)
                print (row, col)
                if isinstance( newValue, (str, unicode)):
                    self.SetCellValue( reportRow, col, newValue)
                elif sheetSelected.cell_type( row, col-1) in ( 2, ): # number
                    self.SetCellValue( reportRow, col, str( newValue).replace('.', DECIMAL_POINT))
                elif sheetSelected.cell_type( row, col-1) in ( 3,): # date
                    year, month, day, hour, minute, second = xldate_as_tuple(newValue, book_datemode)
                    self.SetCellValue( reportRow, col, self.datetime.date(year, month, day).__str__())
                else: # avoiding the bug of the xlrd library
                    try:
                        self.SetCellValue (reportRow, col, str(newValue))
                    except:
                        print  _("Could not import the row,col (%i,%i)") % (row+1, col+1)
        self.table.commit()
    
    def GetNumberRows(self):
        return self.Table.numRows
    
    def GetNumberCols(self):
        return self.table.GetNumberCols()
    
    def AppendCols(self, *args, **params):
        return self.table.AppendCols(*args, **params)
    
    def addColData( self, colData, pageName= None, currCol = None):
        '''adiciona una columna con el contenido de un iterable'''
        if pageName == None:
            if len(self.tableNames) == 0:
                'adding a new table'
                page = self.newTable()
            else:
                page = self.currTable
                
        elif pageName in self.tableNames:
            # activating the selected tablename
            self.currTable= pageName
            page = self.currTable
        else:
            page = self.newTable( tablename= pageName)
            
        #######==================#########
        # se procede a verificar las dimensiones de la pagina actual
        size = (page.GetNumberRows(), page.GetNumberCols())
        
        if currCol == None: 
            # adding the required number of columns
            page.Table.AppendCols(1)
        
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
        #if size[0] >= len(colData):
        #    pass
        #else:
        #    diffColNumber= len(colData) - size[0]
        #    # adding the required rows
        #    page.AppendRows(diffColNumber)
        
        # populate with data
        try:
            DECIMAL_POINT= wx.GetApp().DECIMAL_POINT
        except AttributeError:
            pass
        self.table._setcommit(False)
        try:
            for colPos, colValue in enumerate(colData):
                if isinstance(colValue, (str,unicode)):
                    pass
                else:
                    colValue = str(colValue).replace('.', DECIMAL_POINT)
                page.SetCellValue(colPos, currCol, colValue)
        finally:
            self.table._setcommit(True)
            self.table.commit()
    def beginBatch(self):
        self.BeginBatch()
        self.table.setCommit(False)
    def endBatch(self):
        try:
            self.table.setCommit(True)
        finally:
            self.EndBatch()
    def addRowData( self, rowData, pageName= None, currRow = None):
        '''adds a row with it's row content
        addRowData( rowData, pageName, currRow)
        '''
        # currRow is used to indicate if the user needs to insert
        # the rowContent into a relative row
        if not isnumeric(currRow) and currRow != None:
            raise TypeError('currRow must be a numerical value')

        if pageName == None:
            if len( self.tableNames) == 0:
                # adding a new page into the notebook
                page = self.addPage()
            else:
                page = self.currTable
        elif pageName in self.tableNames:
            self.currTable= pageName[:]
            page = self.currTable
        else:
            page = self.newTable( tablename= pageName)

        # check the size of the current page
        size = (self.GetNumberRows(), self.GetNumberCols())
        # check if it needs to add more columns
        neededCols= size[1] - len( rowData)
        if neededCols <  0:
            neededCols= abs( neededCols)
            self.AppendCols(neededCols)

        # checking if the user input some currRow
        if currRow  == None:
            currRow = self.table.numRows
        elif currRow > self.table.numRows:
            raise StandardError( _('The maximumn allowed row to insert %i')%(self.table.numRows))
        elif currRow < 0:
            raise StandardError( _('The minimum allowed row to insert 0'))
        currRow = int(currRow)

        #if currRow == self.GetNumberRows():
        #    # append one row
        #    page.AppendRows(1)
        #else:
        #    # insert one row
        #    page.InsertRows( pos = currRow, numRows = 1)

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
        print currRow
        for colPos, rowValue in enumerate( rowData):
            if isinstance( rowValue, (str, unicode)):
                pass
            else:
                rowValue = str( rowValue).replace('.', DECIMAL_POINT)
            self.SetCellValue( currRow, colPos, rowValue)
            
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
        self.aplyFilterButtom = wx.Button( self, wx.ID_ANY, _(u"Apply Filter"), wx.DefaultPosition, wx.DefaultSize, 0 )
        
        self.m_mgr.AddPane( self.aplyFilterButtom, wx.aui.AuiPaneInfo() .Bottom() .
                            CaptionVisible( False ).CloseButton( False ).PaneBorder( False ).
                            Movable( False ).Dock().Fixed().
                            DockFixed( False ).Floatable( False ).Row( 0 ) )
        

        self.m_mgr.AddPane( self.m_listBox, wx.aui.AuiPaneInfo().Left().
                            CaptionVisible(True).Caption(_('Existent Tables')).
                            MaximizeButton(True).MinimizeButton(False).Resizable(True).
                            PaneBorder( False ).CloseButton( False ).MinSize( wx.Size( 120,-1 )))

        self.m_mgr.AddPane( self.m_grid, wx.aui.AuiPaneInfo().Centre().
                            CaptionVisible(True).Caption(_('Table contents')).
                            MaximizeButton(True).MinimizeButton(False).Resizable(True).
                            PaneBorder( False ).CloseButton( False ))
        
        self.m_mgr.AddPane( self.txtCtrl, wx.aui.AuiPaneInfo().Left().
                            CaptionVisible(True).Caption(_('Filter')).
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

        self.m_button8 = wx.Button( self, wx.ID_ANY, _(u"Show Dialog"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer10.Add( self.m_button8, 0, wx.ALL, 5 )

        self.SetSizer( bSizer10 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_button8.Bind( wx.EVT_BUTTON, self.showDialog )
        
    # Virtual event handlers, overide them in your derived class
    def showDialog( self, evt ):
        dbPath= '..\\mymusic01.db'
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