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
import wx.aui
from numpy import ndarray, ravel

def numPage():
    i = 1
    while True:
        yield i
        i+= 1

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
        
    def _getCol(self, colNumber):
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
        
        return self._getColNumber(colNumber)
     
    def _getColNumber(self, colNumber):
        if not isnumeric(colNumber):
            raise TypeError('Only allow numeric values for the column, but you input '+ str(type(colNumber)))
        
        colNumber= int(colNumber)
        if colNumber < 0 or colNumber > self.GetNumberCols():
            raise StandardError('The minimum accepted col is 0, and the maximum is %i'%self.GetNumberCols()-1)
        
        return [self.GetCellValue(row, colNumber) for row in range(self.GetNumberRows())]
    
    def putCol(self, colNumber, data):
        if isinstance(colNumber, (str,)):
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
            
        
            
    def clearCol(self, colNumber):
        if colNumber < 0 or colNumber > self.GetNumberCols():
            raise StandardError('The minimum accepted col is 0, and the maximum is %i'%self.GetNumberCols()-1)
        
        for row in range(self.GetNumberRows()):
            self.SetCellValue(row, colNumber, u'')
     
    @property
    def colNames(self):
        return [self.GetColLabelValue(col) for col in range(self.GetNumberCols())]
    @colNames.setter
    def colNames(self, colNames):
        if isinstance(colNames, (str,)):
            colNames= [colNames]
            
        if not isiterable(colName):
            raise TypeError('colNames must be an iterable object')
        
        if len(colNames) == 0:
            return
        
        for colnumber, colname in enumerate(colNames):
            self.SetColLabelValue(pos, colname)
            
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
    def __getattribute__(self, name):
        '''wraps the funtions to the grid
        emulating a grid control'''
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            if self.GetPageCount() != 0:
                currGrid= self.m_notebook.GetSelection()
                return currGrid.__getattribute__(name)
            raise AttributeError

    def getGridAllValueByCols(self,pageName):
        if not (pageName in self.pageNames.keys()):
            raise StandardError('The page does not exist')
        page= self.pageNames[pageName]
        return page.getByColumns()

    def getPageNames(self):
        return self.pageNames.keys()

    def getHeader(self,pageName):
        if not (pageName in self.pageNames.keys()):
            raise StandardError('The page does not exist')
        page= self.pageNames[pageName]
        return page.getHeader()

    def OnNotebookPageChange(self,evt):
        self.currentPage= evt.Selection

    def addPage(self, data= dict()):
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

    def _cellSelectionChange(self, event):
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

    def __loadData__(self,selectedGrid,data, byRows = True):
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

    def GetPageCount(self):
        # 21/04/2011
        # retorna el numero de paginas que hay en el notebook
        return self.m_notebook.PageCount

    def delPage(self, page= None):
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

    def upData(self,  data):
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
            floatCellRenderer= wx.GetApp().frame.floatCellRenderer
            attr.SetRenderer( floatCellRenderer)
            grid01.SetColAttr( grid01.NumberCols-1, attr)
        except AttributeError:
            # the renderer was not find
            pass
        # setting the renderer />
        return grid01

    def addColData(self, colData, pageName= None):
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
            floatCellRenderer= wx.GetApp().frame.floatCellRenderer
            attr.SetRenderer(floatCellRenderer)
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
            if isinstance(colValue,(str,unicode)):
                pass
            else:
                colValue = str(colValue).replace('.', DECIMAL_POINT)
            page.SetCellValue(colPos, currCol, colValue)

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
