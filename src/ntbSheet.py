# -*- coding: utf-8 -*-
'''
Created on 25/10/2010

@author: Sebastian Lopez
'''

import wx
from gridLib.gridsql import SqlGrid, GenericDBClass  # grid with context menu
from imagenes import imageEmbed
from gridLib.NewGrid import NewGrid
import wx.grid
from slbTools import isnumeric, isiterable
from gridLib import floatRenderer
import wx.aui
from numpy import ndarray, ravel, genfromtxt
from wx.grid  import GridCellAttr
#import traceback

DEFAULT_GRID_SIZE= (0,0)
DEFAULT_FONT_SIZE = 12
DECIMAL_POINT = '.' # default value

## defining the event of the range select change

def numPage():
    i = 1
    while True:
        yield i
        i+= 1

class MyFileDropTarget(wx.FileDropTarget):
    def __init__( self, wxPanel ):
        wx.FileDropTarget.__init__(self)
        self.window = wxPanel

    def OnDropFiles( self, x, y, filenames):
        print "\n%d file(s) dropped at %d,%d:" %( len( filenames), x, y)
        for file in filenames:
            print file

        # try to load the file
        if isinstance(filenames, (str, unicode)):
            filenames= [filenames]

        if len(filenames) == 0:
            print "You don't select any file"
            return

        # selecting just the first filename
        filename= filenames[0]
        # self.window.LoadXls(filename)
        self.window.LoadFile(evt= None, fullpath= filename)

class SqlSimpleGrid( wx.Panel, object):# wxGrid
    def __init__( self, parent, size= (800,20)):
        self.rowsizes= dict()
        self.colsizes= dict()
        self.NumSheetReport = 0
        self.path = None

        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, style = wx.TAB_TRAVERSAL )
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        #-------------------------
        #< don't change this line
        #
        ## setting the parameter to the table
        import tempfile
        from sqlalchemy import create_engine
        from sqlalchemy import MetaData, Column, Table
        from sqlalchemy import Integer, String, DateTime, REAL
        from sqlalchemy.pool import StaticPool

        dbFileObject= tempfile.TemporaryFile()
        dbPath= dbFileObject.name
        dbFileObject.close()
        print dbPath
        # creating a database with the conection
        engine= create_engine('sqlite:///%s'%dbPath, echo=False)
        metadata=MetaData(bind=engine)
        # creating the main file
        main_table= ('temp',
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
            main_table+=(Column( colname.next(), String, nullable= True),)
        table= Table(*main_table)
        metadata.create_all()
        self.m_grid = SqlGrid( self, engine= engine, tableName= 'temp', allow2edit= True ) #NewGrid(self ,size, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        # don't change this line/>
        #-------------------------
        self.sizer.Add( self.m_grid , 1, wx.EXPAND, 5 )
        self.SetSizer(self.sizer)
        self.Fit()

        # allowing drop files into the sheet
        dropTarget = MyFileDropTarget( self)
        self.m_grid.SetDropTarget(dropTarget)
        self.grid = self.m_grid # adding some compatibility

    def __getattribute__(self, name):
        '''wraps the functions to the grid
        emulating a grid control'''
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self.m_grid.__getattribute__(name)


class SimpleGrid( wx.Panel, object):# wxGrid
    def __init__( self, parent, size= (800,20)):
        self.rowsizes= dict()
        self.colsizes= dict()
        self.NumSheetReport = 0
        self.path = None

        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, style = wx.TAB_TRAVERSAL )
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        #< don't change this line
        self.m_grid = NewGrid(self ,size, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        # don't change this line/>
        self.sizer.Add( self.m_grid , 1, wx.EXPAND, 5 )
        self.SetSizer(self.sizer)
        self.Fit()

        # allowing drop files into the sheet
        dropTarget = MyFileDropTarget( self)
        self.m_grid.SetDropTarget(dropTarget)
        self.grid = self.m_grid # adding some compatibility

    def __getattribute__(self, name):
        '''wraps the functions to the grid
        emulating a grid control'''
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self.m_grid.__getattribute__(name)

class NoteBookSheet(wx.aui.AuiNotebook, object):
    def __init__( self, parent, *args, **params):
        wx.aui.AuiNotebook.__init__( self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                     wx.aui.AUI_NB_SCROLL_BUTTONS|wx.aui.AUI_NB_TAB_MOVE|
                                     wx.aui.AUI_NB_WINDOWLIST_BUTTON|wx.aui.AUI_NB_BOTTOM|
                                     wx.aui.AUI_NB_TAB_SPLIT|wx.aui.AUI_NB_CLOSE_BUTTON)
        from collections import OrderedDict # to be used under the notebook
        # se almacenan las paginas en un diccionario con llave el numero de pagina
        if params.has_key('fb'):
            self.fb= params.pop('fb')

        bSizer = wx.BoxSizer( wx.VERTICAL )
        self.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnNotebookPageChange)

        # se inicia el generador para el numero de pagina
        self.npage = numPage()
        self.currentPage=    None
        self._pageObjects=   OrderedDict() #dict()
        self.Layout()
        self.numberPage=  self._generador()

    def _generador(self):
        i= 1
        while True:
            yield i
            i+= 1

    # implementing a wrap to the current grid
    def __getattribute__( self, name):
        '''wraps the funtions to the grid
        emulating a grid control'''
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            if self.GetPageCount() != 0:
                if str(type(self.currentPage)) == "<class 'wx._core._wxPyDeadObject'>":
                    self.currentPage = None
                    self.currentPageNumber= None
                    return
                currGrid=  self.currentPage
                return currGrid.__getattribute__(name)
            raise AttributeError

    def __getitem__(self, item):
        if isinstance(item, (str, unicode)):
            if item in self.getPageNames():
                return self._pageObjects[item]

        elif isinstance(item, (int, float)):
            item= int(item)
            if item < 0:
                item = self.GetPageCount() + item
            if item < 0:
                raise StandardError("The selectecd page doesn't exist")
            return self._pageObjects[self._pageObjects.keys()[item]]

    def GetCol(self,*args, **params):
        if self.GetPageCount() != 0:
            if str(type(self.currentPage)) == "<class 'wx._core._wxPyDeadObject'>":
               self.currentPage = None
               self.currentPageNumber= None
        else:
            raise AttributeError
        pageObject=self.currentPage
        return  getattr( pageObject, 'GetCol')(*args, **params)

    def PutCol(self, *args, **params):
        if self.GetPageCount() != 0:
            if str(type(self.currentPage)) == "<class 'wx._core._wxPyDeadObject'>":
               self.currentPage = None
               self.currentPageNumber= None
        else:
            raise AttributeError
        pageObject=self.currentPage
        return  getattr( pageObject, 'PutCol')(*args, **params)

    def _gridSetRenderer(self, grid):
        return
        '''setting the renderer to the grid'''
        attr=   GridCellAttr()
        attr.IncRef() # correct delete column
        renderer = floatRenderer( 4)
        attr.SetRenderer( renderer)
        self.floatCellAttr= attr
        for colNumber in range( grid.NumberCols):
            grid.SetColAttr( colNumber, self.floatCellAttr)

        if wx.Platform == '__WXMAC__':
            grid.SetGridLineColour("#b7b7b7")
            grid.SetLabelBackgroundColour("#d2d2d2")
            grid.SetLabelTextColour("#444444")

    def getGridAllValueByCols( self,pageName):
        if not (pageName in self._pageObjects.keys()):
            raise StandardError('The page does not exist')
        page= self._pageObjects[pageName]
        return page.getByColumns()

    def __len__(self):
        return self.PageCount

    def getPageNames( self):
        return self._pageObjects.keys()

    def getHeader( self,pageName):
        if not (pageName in self._pageObjects.keys()):
            raise StandardError('The page does not exist')
        page= self._pageObjects[pageName]
        return page.getHeader()

    def OnNotebookPageChange( self,evt):
        self.currentPage= self.GetPage( evt.Selection)
        self.currentPageNumber= evt.Selection

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
        return self.PageCount
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
        elif pageName in self._pageObjects.keys():
            page = self._pageObjects[pageName]
        else:
            page = self.addPage( name= pageName)
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
        try:
            DECIMAL_POINT= wx.GetApp().DECIMAL_POINT
        except AttributeError:
            pass
        for colPos, colValue in enumerate(colData):
            if isinstance(colValue, (str,unicode)):
                pass
            else:
                colValue = str(colValue).replace('.', DECIMAL_POINT)
            page.SetCellValue(colPos, currCol, colValue)

    def addRowData( self, rowData, pageName= None, currRow = None):
        '''adds a row with it's row content
        addRowData( rowData, pageName, currRow)
        '''
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
        elif pageName in self._pageObjects.keys():
            page = self._pageObjects[pageName]
        else:
            page = self.addPage( name= pageName)

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


    def addOnePage(self, id= wx.ID_ANY, gridSize= DEFAULT_GRID_SIZE):
        #overwrite this method to create your own custom widget
        ## changing the grid to sqlgrid
        grid=  SimpleGrid( self, size= gridSize)

        grid.hasSaved= True
        grid.hasChanged= False
        grid.SetDefaultColSize( 60, True)
        grid.SetRowLabelSize( 40)
        grid.SetDefaultCellAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTER )
        # adjust the renderer
        self._gridSetRenderer(grid)
        # setting the callback to the range change
        grid.Bind( wx.grid.EVT_GRID_SELECT_CELL, self._cellSelectionChange)
        grid.Bind( wx.grid.EVT_GRID_RANGE_SELECT, self._gridRangeSelect)
        return grid

    def _gridRangeSelect(self, evt):
        grid= evt.GetEventObject()
        # displays the count and the sum of selected values
        selectedCells= grid.get_selection()
        # Count the selected cells
        # getting the cell values:
        selectedCellText= list()
        selectedNumerical= list()
        emptyText= 0
        try:
            DECIMAL_POINT= wx.GetApp().DECIMAL_POINT
        except AttributeError:
            pass
        for rowi, coli in selectedCells:
            currText= grid.GetCellValue( rowi, coli)
            if currText == u"":
                emptyText+= 1
            try:
                selectedNumerical.append( float( currText.replace( DECIMAL_POINT, ".")))
            except:
                pass
            selectedCellText.append( currText)
        try:
            statusBar= wx.GetApp().frame.StatusBar
            statusBar.SetStatusText( wx.GetApp()._(u"cells Selected: %.0f  count: %.0f  sum: %.4f ")%(len(selectedCells),len(selectedCells)-emptyText,sum(selectedNumerical)),1 )
        except AttributeError:
            pass
        evt.Skip()

    def _cellSelectionChange( self, evt):
        # se lee el contenido de la celda seleccionada
        row= evt.GetRow()
        col= evt.GetCol()
        texto= u""
        grid= evt.GetEventObject()
        try:
            texto= grid.GetCellValue( row, col)
        except wx._core.PyAssertionError:
            pass
        try:
            formulaBar= wx.GetApp().frame.formulaBarPanel
            formulaBar.value= texto
        except AttributeError:
            pass
        evt.Skip()

    def addPage( self, **params):
        defaultData = {'name': u'', 'gridSize': DEFAULT_GRID_SIZE}
        for key, value in params.items():
            if defaultData.has_key(key):
                defaultData[key] = value
        # adiciona una pagina al notebook grid
        newName= defaultData['name'] +'_'+ str(self.npage.next())
        self._pageObjects[newName]= self.addOnePage( gridSize = defaultData['gridSize'])
        self.currentPage=  self._pageObjects[newName]
        ntb= self._pageObjects[newName]
        self.AddPage(ntb, newName, False )
        # se hace activo la pagina adicionada
        self.SetSelection(self.GetPageCount()-1)
        return ntb # retorna el objeto ntb

    def delPage( self, evt= None, page= None):
        # si no se ingresa un numero de pagina se
        #     considera que se va a borrar la pagina actual
        # las paginas se numeran mediante numeros desde el cero
        if page == None:
            # se considera que la pagina a borrar es la pagina actual
            #self.GetCurrentPage().Destroy() # borra el contenido de la pagina
            if self.GetSelection() > -1:
                page = self.GetSelection()
            else:
                return
        pageNumber = int(page)
        if pageNumber < 0:
            return
        if pageNumber > self.GetPageCount():
            raise IndexError("Page doesn't exist")
        currPageObj= self.GetPage(pageNumber)
        # delete de erased page from the pages list
        pageName = None
        for pageName, pageObj in self._pageObjects.items():
            if pageObj == currPageObj:
                break
        if pageName == None:
            return
        self._pageObjects.pop( pageName)

    def changeLabel(self, page= None, newLabel= None):
        if self.GetPageCount() < 1:
            return

        if page== None:
            # check for the current sheet
            pageNumber= self.currentPageNumber

        if not isinstance(pageNumber, (int, long, float, ndarray)):
            return
        pageNumber= int(pageNumber)
        if newLabel== None:
            newlabel= self.numberPage.next().__str__()

        elif not isinstance(newLabel, (str, unicode)):
            return

        newLabel= newLabel.replace(' ', '')
        if newLabel== '':
            newlabel= self.numberPage.next().__str__()

        self.SetPageText(pageNumber, newLabel)

    def SaveXlsAs(self, evt):
        currGrid=  self.currentPage
        if currGrid == None:
            return
        (HasSaved, fileName)= currGrid.__getattribute__( 'SaveXlsAs')(evt)
        if not HasSaved:
            return
        self.changeLabel( newLabel= fileName)

class NoteBookSql(NoteBookSheet, object):
    def __init__(self, parent, *args, **params):
        wx.aui.AuiNotebook.__init__( self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                     wx.aui.AUI_NB_SCROLL_BUTTONS|wx.aui.AUI_NB_TAB_MOVE|
                                     wx.aui.AUI_NB_WINDOWLIST_BUTTON|wx.aui.AUI_NB_BOTTOM|
                                     wx.aui.AUI_NB_TAB_SPLIT|wx.aui.AUI_NB_CLOSE_BUTTON)
        from collections import OrderedDict # to be used under the notebook
        # se almacenan las paginas en un diccionario con llave el numero de pagina
        if params.has_key('fb'):
            self.fb= params.pop('fb')

        bSizer = wx.BoxSizer( wx.VERTICAL )
        self.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnNotebookPageChange)

        # se inicia el generador para el numero de pagina
        self.npage = numPage()
        self.currentPage=    None
        self._pageObjects=   OrderedDict() #dict()
        self.Layout()
        self.numberPage=  self._generador()
        # check if there is a sqltable to load
        #------------------
        # to be implemented
        if not params.has_key('sqlFullPath'):
            # creating a temp sqltable
            self.createTempSqlFile()
        else:
            self.loadSqlFile(params.pop('sqlFullPath'))
        #------------------
    def createTempSqlFile(self):
        pass
    def loadSqlFile(self, sqlFullPath):
        pass
    def addPage( self, **params):
        defaultData = {'name': u'', 'gridSize': (1,800)}
        for key, value in params.items():
            if defaultData.has_key(key):
                defaultData[key] = value
        # adiciona una pagina al notebook grid
        newName= defaultData['name'] +'_'+ str(self.npage.next())
        self._pageObjects[newName]= self.addOnePage( gridSize = defaultData['gridSize'])
        self.currentPage=  self._pageObjects[newName]
        ntb= self._pageObjects[newName]
        self.AddPage(ntb, newName, False )
        # se hace activo la pagina adicionada
        self.SetSelection(self.GetPageCount()-1)
        return ntb # retorna el objeto ntb
    def addOnePage(self, id= wx.ID_ANY, gridSize= DEFAULT_GRID_SIZE):
        #overwrite this method to create your own custom widget
        ## changing the grid to sqlgrid
        grid=  SqlSimpleGrid( self, size= gridSize)
        # hide the column _id
        grid.hasSaved= True
        grid.hasChanged= False
        grid.SetColMinimalAcceptableWidth(0)
        grid.SetDefaultColSize( 60, True)
        grid.SetColSize(0, 0)
        grid.SetRowLabelSize( 40)

        grid.SetDefaultCellAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTER )
        # adjust the renderer
        self._gridSetRenderer(grid)
        # setting the callback to the range change
        grid.Bind( wx.grid.EVT_GRID_SELECT_CELL, self._cellSelectionChange)
        grid.Bind( wx.grid.EVT_GRID_RANGE_SELECT, self._gridRangeSelect)
        return grid

class Test(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(480, 520))
        customPanel = NoteBookSheet(self,-1)
        # se adicionan 4 paginas al sheet
        for i in range(4):
            customPanel.addPage( gridSize=(40,20))
        #customPanel.delPage(2)
        self.Centre()
        self.Show(True)

if __name__ == '__main__':
    app = wx.App()
    Test(None, -1, 'Custom Grid Cell')
    app.MainLoop()
#eof