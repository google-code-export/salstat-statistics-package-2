'''
Created on 25/10/2010

@author: Sebastian Lopez
'''

# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Sep  8 2010)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.grid
from GridCopyPaste import PyWXGridEditMixin # habilita las opciones de copiar
                                    # pegar- Undo y redo al Grid
from imagenes import imageEmbed

###########################################################################
## Class MyPanel1
###########################################################################
class MyContextGrid(wx.Menu):
    # Clase para hacer el menu contextual del grid
    def __init__(self,parent):
        wx.Menu.__init__(self)
        self.parent = parent

        cortar = wx.MenuItem(self, wx.NewId(), '&Cortar\tCtrl+X')
        copiar = wx.MenuItem(self, wx.NewId(), 'Copiar\tCtrl+C')
        pegar = wx.MenuItem(self, wx.NewId(), '&Pegar\tCtrl+V')
        eliminar = wx.MenuItem(self, wx.NewId(), '&Eliminar\tDel')
        deshacer = wx.MenuItem(self, wx.NewId(), '&Deshacer\tCtrl+Z')
        rehacer = wx.MenuItem(self, wx.NewId(), '&Rehacer\tCtrl+Y')
        
        imagenes = imageEmbed()
        cortar.SetBitmap(imagenes.edit_cut())
        copiar.SetBitmap(imagenes.edit_copy())
        pegar.SetBitmap(imagenes.edit_paste())
        eliminar.SetBitmap(imagenes.cancel())
        deshacer.SetBitmap(imagenes.edit_undo())
        rehacer.SetBitmap(imagenes.edit_redo()) # edit_redo
        
        self.AppendSeparator()
        self.AppendItem(cortar)
        self.AppendItem(copiar,)
        self.AppendItem(pegar,)
        self.AppendSeparator()
        self.AppendItem(eliminar,)
        self.AppendSeparator()
        self.AppendItem(deshacer,)
        self.AppendItem(rehacer,)
        self.AppendSeparator()
        
        self.Bind(wx.EVT_MENU, self.OnCortar, id=cortar.GetId())
        self.Bind(wx.EVT_MENU, self.OnCopiar, id=copiar.GetId())
        self.Bind(wx.EVT_MENU, self.OnPegar, id=pegar.GetId())
        self.Bind(wx.EVT_MENU, self.OnEliminar, id=eliminar.GetId())
        self.Bind(wx.EVT_MENU, self.OnDeshacer, id=deshacer.GetId())
        self.Bind(wx.EVT_MENU, self.OnRehacer, id=rehacer.GetId())
        
    def OnCortar(self, event):
        self.parent.m_grid.OnCut()

    def OnCopiar(self, event):
        self.parent.m_grid.Copy()
        
    def OnPegar(self, event):
        self.parent.m_grid.OnPaste()

    def OnEliminar(self, event):
        self.parent.m_grid.Delete()
        
    def OnRehacer(self, event):
        self.parent.m_grid.Redo()

    def OnDeshacer(self, event):
        self.parent.m_grid.Undo()

class MyGrid ( wx.Panel ):
    
    def __init__( self, parent, id= wx.ID_ANY, size=(15000,200)):
        wx.Panel.__init__ ( self, parent, id , pos = wx.DefaultPosition, style = wx.TAB_TRAVERSAL )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        cambia= False
        for clase in wx.grid.Grid.__bases__:
            if issubclass(PyWXGridEditMixin,clase):
                cambia = True
                break
        if not cambia:
            wx.grid.Grid.__bases__ += (PyWXGridEditMixin,)
            
        self.m_grid = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        
        # To add capability, mix it in, then set key handler, or add call to grid.Key() in your own handler
        self.m_grid.__init_mixin__()
       
        # Grid
        self.m_grid.CreateGrid( size[0], size[1] )
        self.m_grid.EnableEditing( True )
        self.m_grid.EnableGridLines( True )
        self.m_grid.EnableDragGridSize( False )
        self.m_grid.SetMargins( 0, 0 )
        
        
        # Columns
        self.m_grid.EnableDragColMove( False )
        self.m_grid.EnableDragColSize( True )
        self.m_grid.SetColLabelSize( 30 )
        self.m_grid.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
        
        # Rows
        self.m_grid.EnableDragRowSize( True )
        self.m_grid.SetRowLabelSize( 80 )
        self.m_grid.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
        
        # Label Appearance
        self.m_grid.SetLabelBackgroundColour( wx.Colour( 254, 226, 188 ) )  
        
        # Cell Defaults
        self.m_grid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
        bSizer1.Add( self.m_grid, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.SetSizer( bSizer1 )
        self.Layout()
        
        # se activa el menu contextual sobre el grid
        self.m_grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnGridRighClic )
                
    def setColNames(self,names):
        # escribe los nombres de las columnas en el grid
        if not(type(names) == type(list()) or type(names) == type(tuple())):
            raise TypeError('Solo se acepta una lista de iterable')
        for colNumber, value in enumerate(names):
            self.m_grid.SetColLabelValue(colNumber, value)
    def setRowNames(self,names):
        if not(type(names) == type(list()) or type(names) == type(tuple())):
            raise TypeError('Solo se acepta una lista de iterable')
        for rowNumber, value in enumerate(names):
            self.m_grid.SetRowLabelValue(rowNumber, value)
    def updateGridbyRow(self,values):
        # reescribe los datos del grid con los nuevos datos ingresados por filas (rows)
        for row, rowContent in enumerate(values):
            for col, cellContent in enumerate(rowContent):
                self.m_grid.SetCellValue(row,col,cellContent)
    def updateGridbyCol(self,values):
        for col, colContent in enumerate(values):
            for row, cellContent in enumerate(colContent):
                self.m_grid.SetCellValue(row,col,cellContent)
                
    def OnGridRighClic(self,evt):
        self.PopupMenu(MyContextGrid(self), evt.GetPosition())
        
    def getHeader(self):
        # retorna solo el encabezado de la malla actual
        nombreColumnas= ()
        for index in range(self.m_grid.GetNumberCols()):
            nombreColumnas += (self.m_grid.GetColLabelValue(index),)
        return nombreColumnas
    
    def getByColumns(self):
        # retorna el valor de la malla por columnas, empezando con el nombre
        # de las columnas
        grid = self.m_grid
        contenidoGrid = ()
        numRows = grid.GetNumberRows()
        # se extrae los contenidos de cada fila
        for col in range(grid.GetNumberCols()):
            rowContent = ()
            # rowVacia= True
            for row in range(numRows):
                rowContent+= (grid.GetCellValue(row,col),)
            contenidoGrid +=  (rowContent,)
        return contenidoGrid
    
    def getByRows(self):
        grid = self.m_grid
        contenidoGrid = ()
        contenidoGrid += (self.getRowNames(),)
        numCols = grid.GetNumberCols()
        numRows = grid.GetNumberRows()
        # se extrae los contenidos de cada fila
        for col in range(numCols):
            colContent = ()
            # rowVacia= True
            for row in range(numRows):
                colContent+= (grid.GetCellValue(row,col),)
            contenidoGrid +=  (colContent,)
        return contenidoGrid
    
    def getRowNames(self):
        # retorna el nombre de las columnas del grid
        # retorna solo el encabezado de la malla actual
        nameRows= ()
        for rowNumber in range(self.m_grid.GetNumberRows()):
            nameRows += (self.m_grid.GetRowLabelValue(rowNumber),)
        return nameRows
    
    def getValue(self):
        # retorma los contenidos de la malla ordenados por filas y 
        # empezando por el encabezado
        # se extrae el nombre de la columnas
        grid = self.m_grid
        #nombreColumnas= self.getHeader()
        numCols = grid.GetNumberCols()
        contenidoGrid = (self.getHeader(),)
        # se extrae los contenidos de cada fila
        for row in range(grid.GetNumberRows()):
            filContent = ()
            # filaVacia= True
            for col  in range(numCols):
                # valorCelda = grid.GetCellValue(row,col)
                #### se hace la conversion de unicode a tipo python
                ### valorCelda = self.retornaVlrCelda(valorCelda,valueName) # valueName: nombre de la columna
                ###if valorCelda == None:
                ###    # en caso de existir un valor por defecto se excribe
                ###    if valueName in default.keys():
                ###        valorCelda = default[valueName]
                ###    else:
                ###        # No existe un valor por defecto
                ###        valorCelda = None
                ###else:
                ##    filaVacia= False
                filContent+= (grid.GetCellValue(row,col),)
            contenidoGrid +=  (filContent,)
        return contenidoGrid
        
    def __del__( self ):
        pass
        
class NoteBookSheet(wx.Panel):
    def __init__( self, parent, id= wx.ID_ANY):
    
        # se almacenan las paginas en un diccionario con llave el numero de pagina
    
        wx.Panel.__init__ ( self, parent, id , pos = wx.DefaultPosition, style = wx.TAB_TRAVERSAL )
    
        bSizer = wx.BoxSizer( wx.VERTICAL )
        self.m_notebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_BOTTOM )
        # self.m_notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,self.OnNotebookPageChange)
        
        bSizer.Add( self.m_notebook, 1, wx.EXPAND |wx.ALL, 5 )
        
        self.SetSizer( bSizer )
        self.Layout()
        
    def getGridAllValueByCols(self,pageName):
        # retorna el contenido de una pagina del notebooksheet
        if pageName in self.getPageNames():
            for index,value in enumerate(self.getPageNames()):
                if value == pageName:
                    numberpage = index
                    break
            obj = self.m_notebook.GetPage(numberpage)
            return obj.getByColumns()
        else:
            raise StandardError('La pagina no existe')   
    
    def getPageNames(self):
        # retorna los nombre de las paginas adicionadas, como una lista
        numpages= self.m_notebook.GetPageCount()
        if numpages > 0:
            pages = ()
            for page in range(numpages):
                pages+= (self.m_notebook.GetPageText(page),)
            return pages
        else:
            return ()
        
    def getHeader(self,pageName):
        if pageName in self.getPageNames():
            for index,value in enumerate(self.getPageNames()):
                if value == pageName:
                    numberpage = index
                    break
            obj = self.m_notebook.GetPage(numberpage).getHeader()
            return obj
        else:
            raise StandardError('La pagina no existe')             
        
    def OnNotebookPageChange(self,evt):
        self.currentPage= evt.Selection
        
        
    def addPage(self,data= {'name': u"un Nombre", 'size':(50,4),'nameCol':('col1','col2','col3','col4')}):
        # adiciona una pagina al notebook grid
        grid= MyGrid(self.m_notebook,-1,size= data['size'] )
        self.m_notebook.AddPage(grid,data['name'] +'_'+ str(self.m_notebook.GetPageCount()), False )
        # se hace activo la pagina adicionada
        self.m_notebook.ChangeSelection(self.m_notebook.GetPageCount()-1)
        # se escriben los nombres de las columnas en el grid en caso de existir
        if 'nameCol' in data.keys():
            for index, value in enumerate(data['nameCol']):
                grid.m_grid.SetColLabelValue(index,value) # str(value)
        if 'nameRow' in data.keys():
            for index, value in enumerate(data['nameRow']):
                grid.m_grid.SetRowLabelValue(index,value)
                
        return grid # retorna el objeto MyGrid
    
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
        #       name: name of the page
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
        self.__loadData__(grid01.m_grid,data['data'],byRows)
        return grid01
        
    def __del__( self ):
        pass
    
class Test(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(480, 520)) 
        
        customPanel = NoteBookSheet(self,-1)
        # se adicionan 4 paginas al sheet
        for i in range(4):
            customPanel.addPage()
        customPanel.delPage(2)
        self.Centre()
        self.Show(True)
        
if __name__ == '__main__':
    app = wx.App()
    Test(None, -1, 'Custom Grid Cell')
    app.MainLoop()
    
    
    



