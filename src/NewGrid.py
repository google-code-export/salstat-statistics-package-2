# -*- coding:utf-8 -*-
"""
Created on 09/12/2010

@author: usuario
"""
import wx
import wx.grid
import tempfile
import csv

from imagenes import imageEmbed
import os
import subprocess

class _MyContextGrid(wx.Menu):
    # Clase para hacer el menu contextual del grid
    def __init__(self,parent,*args,**params):
        wx.Menu.__init__(self)
        self.parent = parent
        cortar =    wx.MenuItem(self, wx.NewId(), '&Cortar\tCtrl+X')
        copiar =    wx.MenuItem(self, wx.NewId(), 'Copiar\tCtrl+C')
        pegar =     wx.MenuItem(self, wx.NewId(), '&Pegar\tCtrl+V')
        eliminar =  wx.MenuItem(self, wx.NewId(), '&Eliminar\tDel')
        deshacer =  wx.MenuItem(self, wx.NewId(), '&Deshacer\tCtrl+Z')
        rehacer =   wx.MenuItem(self, wx.NewId(), '&Rehacer\tCtrl+Y')
        exportarCsv= wx.MenuItem(self,wx.NewId(), '&Exportar\tCtrl+E')
        
        imagenes = imageEmbed()
        cortar.SetBitmap(imagenes.edit_cut())
        copiar.SetBitmap(imagenes.edit_copy())
        pegar.SetBitmap(imagenes.edit_paste())
        eliminar.SetBitmap(imagenes.cancel())
        deshacer.SetBitmap(imagenes.edit_undo())
        rehacer.SetBitmap(imagenes.edit_redo())
        exportarCsv.SetBitmap(imagenes.exporCsv())
        # edit_redo
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
        self.AppendItem(exportarCsv,)
        
        self.Bind(wx.EVT_MENU, self.OnCortar, id=cortar.GetId())
        self.Bind(wx.EVT_MENU, self.OnCopiar, id=copiar.GetId())
        self.Bind(wx.EVT_MENU, self.OnPegar, id=pegar.GetId())
        self.Bind(wx.EVT_MENU, self.OnEliminar, id=eliminar.GetId())
        self.Bind(wx.EVT_MENU, self.OnDeshacer, id=deshacer.GetId())
        self.Bind(wx.EVT_MENU, self.OnRehacer, id=rehacer.GetId())
        self.Bind(wx.EVT_MENU, self.OnExportarCsv, id=exportarCsv.GetId())
        
    def OnCortar(self, event):
        self.parent.OnCut()

    def OnCopiar(self, event):
        self.parent.Copy()
        
    def OnPegar(self, event):
        self.parent.OnPaste()

    def OnEliminar(self, event):
        self.parent.Delete()
        
    def OnRehacer(self, event):
        self.parent.Redo()

    def OnDeshacer(self, event):
        self.parent.Undo()
    
    def OnExportarCsv(self,event):
        self.parent.OnExportCsv()
 
###########################################################################
## Class NewGrid
###########################################################################
class NewGrid(wx.grid.Grid):
    def __init__(self,*args, **params):
        wx.grid.Grid.__init__(self, *args, **params)
        if len([clase for clase in wx.grid.Grid.__bases__ if issubclass(_PyWXGridEditMixin,clase)]) == 0:
            wx.grid.Grid.__bases__ += (_PyWXGridEditMixin,)
        # se activan las funciones para el menu contextual
        if len(args) > 0:
            self.__init_mixin__( args[0])
        elif 'parent' in params.keys():
            self.__init_mixin__( params['parent'])
        # se activa el menu contextual sobre el grid
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnGridRighClic )
        
    def OnGridRighClic(self,evt):
        self.PopupMenu(_MyContextGrid(self), evt.GetPosition())
        
    def setColNames(self,names):
        # escribe los nombres de las columnas en el grid
        if not(type(names) == type(list()) or type(names) == type(tuple())):
            raise TypeError('Solo se acepta una lista de iterable')
        [self.SetColLabelValue(colNumber, value) for colNumber, value in enumerate(names) ]
        
    def setRowNames(self,names):
        if not(type(names) == type(list()) or type(names) == type(tuple())):
            raise TypeError('Solo se acepta una lista de iterable')
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
    
    def getByColumns(self):
        # retorna el valor de la malla por columnas
        numRows = self.GetNumberRows()
        ncols= self.GetNumberCols()
        # se extrae los contenidos de cada fila
        return tuple([tuple([ self.GetCellValue(row,col) for row in range(numRows) ]) for col in range(ncols)])
    
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
    
class _PyWXGridEditMixin():
    """ A Copy/Paste and undo/redo mixin for wx.grid. Undo/redo is per-table, not yet global."""
    def __init_mixin__(self, parent=False):
        # el parent se utiliza para hacer un llamado a una funcion externa 
        # luego de modificar las celda en el caso que se deban aceptar ciertos 
        # valores en las celdas, especificamente cuando se quiera realizar una accion
        # sobre la funcion wx.grid.EVT_GRID_CELL_CHANGE
        """caller must invoke this method to enable keystrokes, or call these handlers if they are overridden."""
        wx.EVT_KEY_DOWN(self, self.OnMixinKeypress)
        wx.grid.EVT_GRID_CELL_CHANGE(self, self.Mixin_OnCellChange)
        wx.grid.EVT_GRID_EDITOR_SHOWN(self, self.Mixin_OnCellEditor)
        self._undoStack = []
        self._redoStack = []
        self._stackPtr = 0
        self.padre= parent
        
    def setPadreCallBack(self,padreObj):
        self.padre = padreObj

    def OnMixinKeypress(self, event):
        """Keystroke handler."""
        key = event.GetKeyCode() 
        if key == ord(" ") and event.ShiftDown and not event.ControlDown:
            self.SelectRow(self.GetGridCursorRow())
            return
        if not event.ControlDown: return
        if key == 67: self.Copy()
        elif key == 86: self.OnPaste()
        elif key == ord("X"): self.OnCut()
        elif key == wx.WXK_DELETE: self.Delete()
        elif key == ord("Z"): self.Undo()
        elif key == ord("Y"): self.Redo()
        elif key == ord(" "): self.SelectCol(self.GetGridCursorCol())
        elif key: event.Skip()
        
    def Mixin_callbackChangeCell(self, rango):
        # realiza el llamado a la funcion OnRangeChange del respectivo parent
        # asignado indicando el rango que se ha modificado
        # range= (celltop, cellLeft, NumRows,NumCols)
        # se rehubica la posicion del cursor para que sean mas ovios los cambios
        if self.padre != False:
            try:
                self.padre.OnRangeChange(rango)
                # self.GrandParent.OnRangeChange(rango)
            except:
                return
                # print "la funcion padre no implementa OnRangeChange"
            
    def Mixin_OnCellEditor(self, evt=None):
        """this method saves the value of cell before it's edited (when that value disappears)"""
        top, left, rows, cols = self.GetSelectionBox()[0]
        v = self.GetCellValue(top, left)
        self._editOldValue = v+"\n"

    def Mixin_OnCellChange(self, evt):
        """Undo/redo handler Use saved value from above for undo."""
        box = self.GetSelectionBox()[0]
        newValue = self.GetCellValue(*box[:2])
        self.AddUndo(undo=(self.Paste, (box, self._editOldValue)),
            redo=(self.Paste, (box, newValue)))
        self._editOldValue = None
        self.Mixin_callbackChangeCell(box)
    
    def GetSelectionBox(self):
        """Produce a set of selection boxes of the form (top, left, nrows, ncols)"""
        #For wxGrid, blocks, cells, rows and cols all have different selection notations.  
        #This captures them all into a single "box" tuple (top, left, rows, cols)
        gridRows = self.GetNumberRows()
        gridCols = self.GetNumberCols()
        tl, br = self.GetSelectionBlockTopLeft(), self.GetSelectionBlockBottomRight()
        # need to reorder based on what should get copy/pasted first
        boxes = []
        # collect top, left, rows, cols in boxes for each selection
        for blk in range(len(tl)):
            boxes.append((tl[blk][0], tl[blk][1], br[blk][0] - tl[blk][0]+1, br[blk][1]-tl[blk][1]+1))
        for row in self.GetSelectedRows():
            boxes.append((row, 0, 1, gridCols))
        for col in self.GetSelectedCols():
            boxes.append((0, col, gridRows, 1))
        # if not selecting rows, cols, or blocks, add the current cursor (this is not picked up in GetSelectedCells
        if len(boxes) ==0:
            boxes.append((self.GetGridCursorRow(), self.GetGridCursorCol(), 1, 1))
        for (top, left) in self.GetSelectedCells():
                boxes.append((top, left, 1, 1)) # single cells are 1x1 rowsxcols.
        return boxes

    def Copy(self):
        """Copy selected range into clipboard.  If more than one range is selected at a time, only the first is copied"""
        top, left, rows,cols = self.GetSelectionBox()[0]
        data = self.Box2String(top, left, rows, cols)
        # Create text data object for use by TheClipboard
        clipboard = wx.TextDataObject()
        clipboard.SetText(data)
        # Put the data in the clipboard
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(clipboard)
            wx.TheClipboard.Close()
        else:
            print "Can't open the clipboard"

    def Box2String(self, top, left, rows, cols):
        """Return values in a selected cell range as a string.  This is used to pass text to clipboard."""
        data = '' # collect strings in grid for clipboard
        # Tabs '\t' separate cols and '\n' separate rows
        for r in range(top, top+rows):
            # the str option return an errror when it's used to unicode in a compiled program
            rowAsString = [self.GetCellValue(r, c) for c in range(left, left+cols) if self.CellInGrid(r,c)]
            data += str.join("\t",rowAsString) + "\n"
        return data    

    def OnPaste(self):
        """Event handler to paste from clipboard into grid.  Data assumed to be separated by tab (columns) and "\n" (rows)."""
        clipboard = wx.TextDataObject()
        if wx.TheClipboard.Open():
            wx.TheClipboard.GetData(clipboard)
            wx.TheClipboard.Close()
        else:
            print "Can't open the clipboard"
        data = clipboard.GetText()
        table = [r.split('\t') for r in data.splitlines()] # convert to array
        #Determine the paste area given the size of the data in the clipboard (clipBox) and the current selection (selBox)
        top, left, selRows,selCols = self.GetSelectionBox()[0]
        if len(table) ==0 or type(table[0]) is not list: table = [table]
        pBox = self._DeterminePasteArea(top, left, len(table), len(table[0]), selRows, selCols)
        self.AddUndo(undo=(self.Paste, (pBox, self.Box2String(*pBox))),
            redo=(self.Paste, (pBox, data)))
        self.Paste(pBox, data)
        # se almacena el rango que se ha cambiado
        self.Mixin_callbackChangeCell(pBox)
        
    def _DeterminePasteArea(self, top, left, clipRows, clipCols, selRows, selCols):
        """paste area rules: if 1-d selection (either directon separately) and 2-d clipboard, use clipboard size, otherwise use selection size"""
        pRows = selRows ==1 and clipRows > 1 and clipRows or selRows
        pCols = selCols ==1 and clipCols > 1 and clipCols or selCols
        return top, left, pRows, pCols
        if clipRows ==1 and clipCols ==1: # constrain paste range by what's in clipboard
            pRows, pCols = clipRows, clipCols 
        else: # constrain paste range by current selection
            pRows, pCols = selRows, selCols
        return top, left, pRows, pCols # the actual area we'll paste into
        
    def Paste(self, box, dataString):
        top, left, rows, cols = box
        data = [r.split('\t') for r in dataString.splitlines()]
        if len(data) ==0 or type(data[0]) is not list: data = [data]
        # get sizes (rows, cols) of both clipboard and current selection
        dataRows, dataCols = len(data), len(data[0])
        try:
            for r in range(rows):
                row = top + r
                for c in range(cols):
                    col = left + c
                    if self.CellInGrid(row, col): self.SetCellValue(row, col, data[r %dataRows][c % dataCols])
            return
        except ZeroDivisionError: print "Division por cero: Num_col "  +str(dataRows)+ ", Num_Fil " + str(dataCols)
            

    def CellInGrid(self, r, c): # only paste data that actually falls on the table
        return r >=0 and c >=0 and r < self.GetNumberRows() and c < self.GetNumberCols()

    def OnCut(self):
        """Cut cells from grid into clipboard"""
        box = self.GetSelectionBox()[0]
        self.Copy()
        self.Delete() #this takes care of undo/redo
        
    def OnExportCsv(self):
        "exporta el contenido de la malla en formato csv"
        '''Se abre un archivo temporal y se procede a reportar'''
        archivo= tempfile.mkstemp(suffix='.csv') #Se crea el archivo temporal
        path = os.path.abspath(archivo[1])
        writer = csv.writer(open(path,'wb'), delimiter= ';',
                            quotechar= ' ', quoting= csv.QUOTE_MINIMAL)
        for line in self.getValue(): # self.getByRows()[1:]
            writer.writerow([s.encode('utf-8') for s in line])
        print path
        if os.name == 'mac':
            subprocess.call(('open', path))
        elif os.name == 'nt':
            os.startfile(path)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', path))
        
    def Delete(self):
        """Clear Cell contents"""
        boxes = self.GetSelectionBox()
        for box in boxes: #allow multiple selection areas to be deleted
            # first, save data in undo stack
            self.AddUndo(undo=(self.Paste, (box, self.Box2String(*box))),
                redo=(self.Paste, (box, "\n")))
            self.Paste(box, "\n")
            self.Mixin_callbackChangeCell(box)

    def AddUndo(self, undo, redo):
        """Add an undo/redo combination to the respective stack"""
        (meth, parms) = undo
        #print self._stackPtr, "set undo: ",parms, "redo=",redo[1]
        self._undoStack.append((meth, parms))
        (meth, parms) = redo
        self._redoStack.append((meth, parms))
        self._stackPtr+= 1
        # remove past undos beyond the current one.
        self._undoStack = self._undoStack[:self._stackPtr]
        self._redoStack = self._redoStack[:self._stackPtr]

    def Undo(self, evt = None):
        if self._stackPtr > 0:
            self._stackPtr -= 1
            (funct, params) = self._undoStack[self._stackPtr]
            #print "UNdoing:"+`self._stackPtr`+"=",`params[0]`
            funct(*params)
            # set cursor at loc asd selection if block
            top, left, rows, cols = params[0]
            self.SelectBlock(top, left, top+rows-1, left+cols-1)
            self.SetGridCursor(top,left)
            self.Mixin_callbackChangeCell(params[0])
            # padre= self.GetParent() 
            # padre.SetGridCursor(top, left) # se espera que el parent sea el grid

    def Redo(self, evt = None):
        if self._stackPtr < len(self._redoStack):
            (funct, params) = self._redoStack[self._stackPtr]
            #print "REdoing:"+`self._stackPtr`+"=",`params[0]`
            funct(*params)
            # set cursor at loc
            top, left, rows, cols = params[0]
            self.SetGridCursor(top, left)
            self.SelectBlock(top, left, top+rows-1, left+cols-1)
            self._stackPtr += 1
            self.Mixin_callbackChangeCell(params[0])
            # padre= self.GetParent() 
            # padre.SetGridCursor(top, left) # se espera que el parent sea el grid 
         
def test():
    # para verificar el correcto funcionamiento del grid
    pass
if __name__ == '__main__':    
        app = wx.PySimpleApp()
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