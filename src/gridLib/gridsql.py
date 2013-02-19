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

SEARCHINDEX= 500
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
        'DATE':        8,
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
    def __init__( self, engine= None, tableName= None, allow2edit= False):
        self.allow2edit=  allow2edit
        self._currTable=  None
        self._initializeParams()
        self._numCols= 0
        self._numRows= 0
        # the rederer is a global property for the sheet
        self.odd= wx.grid.GridCellAttr()
        self.odd.SetBackgroundColour( wx.Colour( 220, 230, 250 ))
        self.odd.SetEditor(VARCHAR())
        self.even= wx.grid.GridCellAttr()
        self.even.SetEditor(VARCHAR())
        self.even.SetBackgroundColour( wx.Colour( 146, 190, 183 ))
        wx.grid.PyGridTableBase.__init__(self)

        if engine == None:
            self.loadDatabase( evt = None)
            # getting the information of the column
            self.getColsInfo()
        else:
            self.engine= engine
            if tableName == None:
                tableName= self.tableNames[0]
            # once the currtable changes, also the data is autonatically loaded
            self.currTable= tableName

        self._numRows= self.numRows
        self._numCols= self.GetNumberCols()

        self.initId=         int(self.getFirstId())

    def _initializeParams(self):
        # used to initialize the data if the user change the selected table
        self.bufer=          dict()
        self.oldRowSelected= None
        self.curRowData=     None

    def GetAttr(self, row, col, kind):
        attr = [ self.even, self.odd][row % 2]
        attr.IncRef()
        return attr

    def getColsInfo( self, evt= None):
        # it's used to read the type of columns of the selected table
        # and interact with the 
        pass

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
            # updating the required fields
            self._initializeParams()
            self.loadTable(evt= None)

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

            difRow= self.GetNumberRows()-self._numRows
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


            # update the column rendering plugins 
            #self._updateColAttrs(grid) 

            # update the scrollbars and the displayed part of the grid 
            #self.AdjustScrollbars() 
            #self.ForceRefresh()
        else:
            raise StandardError("%s doesn't exist"%tableName)	

    def loadTable( self, evt):
        metadata=       MetaData( self.engine)
        self.table=          Table( self.currTable, metadata, autoload=True, autoload_with=self.engine)
        self.colLabels= self.table.columns.keys()
        self.colTypes=  self._getColTypes(self.table)
        clear_mappers() #http://docs.sqlalchemy.org/en/rel_0_6/orm/mapper_config.html#sqlalchemy.orm.clear_mappers
        mapper( GenericDBClass, self.table)
        self.Session=   sessionmaker( bind = self.engine)

    def _getColTypes(self, table):
        # Getting the column types as string
        types= list()
        for col in [table.columns.get(colname) for colname in table.columns.keys()]:
            types.append( col.type.__str__())
        return types

    def getFirstId( self):
        session= self.Session()
        res= session.query(GenericDBClass).first().id
        session.close()
        return res

    @property
    def numRows( self):
        return self.GetNumberRows()

    def checkTableName( self, tableName):
        if not tableName in self.engine.table_names():
            return False
        return True

    def GetNumberRows( self):
        session = self.Session()
        res= session.query(GenericDBClass).count()+1
        session.close()
        return res

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

        rowMin=      max( [self.getFirstId()-1, row-SEARCHINDEX])
        rowMax=      min( [self.numRows-1, row+SEARCHINDEX])
        # emptying the non needed keys in buffer
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
        rows=        session.query( GenericDBClass).offset( minRequiredDb).limit( maxRequiredDb-minRequiredDb+1).all()
        session.close()
        rowResults=  self._getRowValues( rows)
        for pos, rowContents in enumerate( rowResults): 
            self.bufer[minRequiredDb+pos]= rowContents
        # in case the row is the last then adding none data as the last element

    def _getRowValues( self, rowContents):
        return   [[getattr( row, attr) for attr in self.colLabels] for row in rowContents]

    def GetValue(self, row, col):
        value= self.getBufer(row)[col]
        if value== None:
            return u""
        return "%s" % (value)

    def SetValue( self, row, col, value):
        if not self.allow2edit:
            return
        # create a Session
        session = self.Session() 
        # querying for a record in the Artist table
        rowNumber= self.GetValue(row, 0)
        if rowNumber != u'':
            res= session.query( GenericDBClass).get( long(rowNumber))
        else:
            res= None

        if res == None:
            if row >= self.numRows-1:
                # se adiciona un registro nuevo
                newRegsitry= GenericDBClass()
                setattr(newRegsitry, self.colLabels[col], value)
                session.add(newRegsitry)
                try:
                    session.commit()
                except StatementError:
                    return
                finally:
                    session.close()
                self.updateBuffer(row, forceRefresh= True)
                # tell the grid we've added a row
                msg = wx.grid.GridTableMessage(self,            # The table
                                               wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                                               1                                       # how many
                                               )

                self.GetView().ProcessTableMessage(msg)
                session.close()
                return
        else:      
            setattr(res, self.colLabels[col], value)
            session.commit()
            session.close()
            self.updateBuffer(row, forceRefresh= True)
            # is missing to update the grid
            self.GetView().Refresh()
        # refresh the grid

    def GetColLabelValue( self, col):
        return self.colLabels[col]

    def GetRowLabelValue( self, row):
        session= self.Session()
        try:
            rowLabel= getattr( session.query( GenericDBClass).get( row+self.initId), self.colLabels[0])
        except AttributeError:
            return u''
        finally:
            session.close()
        return rowLabel

class SqlGrid( wx.grid.Grid):
    def __init__(self, parent, engine= None, tableName= None, allow2edit= False):
        wx.grid.Grid.__init__( self, parent)
        self.table= SqlTable( engine, tableName, allow2edit)
        self.SetTable( self.table, True)
        self._currTable= self.table.currTable
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


class selectDbTableDialog( wx.Dialog):
    def __init__(self, parent,engine,tableName= None, allow2edit= False):
        wx.Dialog.__init__(self, parent,
                           id=    wx.ID_ANY,
                           title= "Choose a table",
                           size=  (640,480))
        
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )
        self.m_mgr.SetFlags(wx.aui.AUI_MGR_DEFAULT)
        self.m_grid=  SqlGrid( self, engine, tableName, allow2edit)
        
        self.m_listBox2Choices= self.m_grid.tableNames
        if len(self.m_listBox2Choices) > 0:
            selected= 0
        
        self.selectedTableName= self.m_listBox2Choices[selected]
        self.m_listBox = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.m_listBox2Choices, selected )
        
        self.okCancel= okCancelPanel(self, wx.ID_ANY)
        
        self.m_mgr.AddPane( self.m_listBox, wx.aui.AuiPaneInfo().Left().
                            CaptionVisible(True).Caption('Existent Tables').
                            MaximizeButton(True).MinimizeButton(False).Resizable(True).
                            PaneBorder( False ).CloseButton( False ).MinSize( wx.Size( 120,-1 )) )
        
        self.m_mgr.AddPane( self.m_grid, wx.aui.AuiPaneInfo().Centre().
                            CaptionVisible(True).Caption('Table contents').
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
        #self.okCancel.okButton.Bind( wx.EVT_BUTTON, self.ok )
        #self.okCancel.cancelButton.Bind( wx.EVT_BUTTON, self.cancel )
        
    def _onListBoxElementSelected(self, evt, *args, **params):
        currSelectionNumber= evt.GetSelection()
        if currSelectionNumber >= 0:
            if currSelectionNumber != self.currTableNumber:
                self.selectedTableName= self.m_listBox2Choices[currSelectionNumber]
                self.currTableNumber= currSelectionNumber
                # changing the selection of the table in the grid
                self.m_grid.currTable= evt.GetString()
                ## talking to the grid to udate it
                ## self.GetView().Refresh() # .table.
            else:
                return
            
    def GetValue(self):
        return (self.selectedTableName,)
    
    def Destroy(self, *args, **params):
        self.m_mgr.UnInit()

class _example( wx.Frame ):
    def __init__( self, parent ):
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
        dbPath= 'e:\\proyecto gridsql\\mymusic.db'
        engine= create_engine('sqlite:///%s'%dbPath, echo=True)
        dlg= selectDbTableDialog(self, engine)
        if dlg.ShowModal() == wx.ID_OK:
            values= dlg.GetValue()
            print values
        dlg.Destroy()

if __name__ == '__main__':
    app=   wx.App()
    frame= _example(None)
    frame.Show()
    app.MainLoop()