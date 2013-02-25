# -*- coding:utf-8 -*-
"""
Created on 09/12/2010

@author: usuario
"""
__all__ = ['NewGrid']
import wx
import wx.grid

def translate(a):
    return a
ECXISTIMAGES = True
try:
    from imagenes import imageEmbed
    EXISTIMAGES = True
except ImportError:
    EXISTIMAGES = False
    
from GridCopyPaste import PyWXGridEditMixin

def Translate(obj):
    return obj
class _MyContextGrid(wx.Menu):
    # Clase para hacer el menu contextual del grid
    def __init__(self,parent,*args,**params):
        wx.Menu.__init__(self)
        self.parent = parent
        try:
            translate= wx.GetApp().translate
        except AttributeError:
            translate = Translate
        cortar =     wx.MenuItem(self, wx.NewId(), translate('&Cut\tCtrl+X'))
        copiar =     wx.MenuItem(self, wx.NewId(), translate('C&opy\tCtrl+C'))
        pegar =      wx.MenuItem(self, wx.NewId(), translate('&Paste\tCtrl+V'))
        eliminar =   wx.MenuItem(self, wx.NewId(), translate('&Del\tDel'))
        deshacer =   wx.MenuItem(self, wx.NewId(), translate('&Undo\tCtrl+Z'))
        rehacer =    wx.MenuItem(self, wx.NewId(), translate('&Redo\tCtrl+Y'))
        delRow=      wx.MenuItem(self, wx.NewId(), translate('Del Row'))
        delCol=      wx.MenuItem(self, wx.NewId(), translate('Del Col'))
        ##exportarCsv= wx.MenuItem(self, wx.NewId(), '&Export\tCtrl+E')
        
        if EXISTIMAGES:
            imagenes = imageEmbed()
            cortar.SetBitmap(imagenes.edit_cut())
            copiar.SetBitmap(imagenes.edit_copy())
            pegar.SetBitmap(imagenes.edit_paste())
            eliminar.SetBitmap(imagenes.cancel())
            deshacer.SetBitmap(imagenes.edit_undo())
            rehacer.SetBitmap(imagenes.edit_redo())
        ##exportarCsv.SetBitmap(imagenes.exporCsv())

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
        self.AppendItem(delRow,)
        self.AppendItem(delCol,)
        ##self.AppendItem(exportarCsv,)
        
        self.Bind(wx.EVT_MENU, self.OnCortar,      id= cortar.GetId())
        self.Bind(wx.EVT_MENU, self.OnCopiar,      id= copiar.GetId())
        self.Bind(wx.EVT_MENU, self.OnPegar,       id= pegar.GetId())
        self.Bind(wx.EVT_MENU, self.OnEliminar,    id= eliminar.GetId())
        self.Bind(wx.EVT_MENU, self.OnDeshacer,    id= deshacer.GetId())
        self.Bind(wx.EVT_MENU, self.OnRehacer,     id= rehacer.GetId())
        self.Bind(wx.EVT_MENU, self.OnDelRow,     id= delRow.GetId())
        self.Bind(wx.EVT_MENU, self.OnDelCol,     id= delCol.GetId())
        ##self.Bind(wx.EVT_MENU, self.OnExportarCsv, id= exportarCsv.GetId())
        
    def OnCortar(self, evt):
        self.parent.OnCut()
        evt.Skip()

    def OnCopiar(self, evt):
        self.parent.Copy()
        evt.Skip()
        
    def OnPegar(self, evt):
        self.parent.OnPaste()
        evt.Skip()
        
    def OnEliminar(self, evt):
        self.parent.Delete()
        evt.Skip()
        
    def OnRehacer(self, evt):
        self.parent.Redo()
        evt.Skip()

    def OnDeshacer(self, evt):
        self.parent.Undo()
        evt.Skip()
    
    def OnExportarCsv(self,evt):
        self.parent.OnExportCsv()
        evt.Skip()
        
    def OnDelRow(self, evt):
        try:
            # searching for the parent in the simplegrid parent
            parent= self.parent.Parent
        except AttributeError:
            parent= None
            
        if hasattr(parent, 'DeleteCurrentRow'):
            parent.DeleteCurrentRow(evt)
        else:
            currentRow, left, rows,cols = self.parent.GetSelectionBox()[0]
            if rows < 1:
                return
            self.parent.DeleteRows(currentRow, 1)
            self.parent.AdjustScrollbars()
        
        self.parent.hasChanged= True
        self.parent.hasSaved=   False
        evt.Skip()
    
    def OnDelCol(self, evt):
        try:
            # searching for the parent in the simplegrid parent
            parent= self.parent.Parent
        except AttributeError:
            parent= None
            
        if hasattr(parent,  'DeleteCurrentCol'):
            parent.DeleteCurrentCol(evt)
        else:
            currentRow, currentCol, rows,cols = self.parent.GetSelectionBox()[0]
            if cols < 1:
                return
            self.parent.DeleteCols(currentCol, 1)
            self.parent.AdjustScrollbars()
        
        self.hasChanged= True
        self.hasSaved=   False
        evt.Skip()

    
###########################################################################
## Class NewGrid
###########################################################################
class NewGrid(wx.grid.Grid):
    def __init__(self,*args, **params):
        self.nombre = 'selobu'
        self.maxrow= 0
        self.maxcol= 0
        wx.grid.Grid.__init__(self, *args, **params)
        if len([clase for clase in wx.grid.Grid.__bases__ if issubclass( PyWXGridEditMixin, clase)]) == 0:
            wx.grid.Grid.__bases__ += ( PyWXGridEditMixin,)
        # se activan las funciones para el menu contextual
        if len(args) > 0:
            self.__init_mixin__( args[0])
        elif 'parent' in params.keys():
            self.__init_mixin__( params['parent'])
        # se activa el menu contextual sobre el grid
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnGridRighClic )
        
    def get_selection(self):
        """ Returns an index list of all cell that are selected in 
        the grid. All selection types are considered equal. If no 
        cells are selected, the current cell is returned.
        
        from: http://trac.wxwidgets.org/ticket/9473"""

        dimx, dimy = (self.NumberRows, self.NumberCols) #self.parent.grid.dimensions[:2]
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
        self.PopupMenu(_MyContextGrid(self), evt.GetPosition())
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
    
def test():
    # para verificar el funcionamiento correcto del grid
    pass

if __name__ == '__main__':    
        app = wx.PySimpleApp()
        app.translate= translate
        frame = wx.Frame(None, -1, size=(700,500), title = "wx.Grid example")
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
        cattr = wx.grid.GridCellAttr()
        cattr.SetEditor(wx.grid.GridCellAutoWrapStringEditor())
        #cattr.SetRenderer(wx.grid.GridCellAutoWrapStringRenderer())
        grid.SetColAttr(1, cattr)
        frame.Show(True)
        app.MainLoop()