'''
Created on 27/10/2010
# 08 de nov de 2010:
-> llamado a GrandParent para el momentn en que se deba hacer una operacion con EVT_GRID_CELL_CHANGE
#    el metodo dentro del parent se debe llamar GrandParent.OnRangeChange(self,range)
#    range=(top, left, #rows, #cols)
-> adicion de cambio en la posicion del cursor cuando se realiza un cambio en el grid
@author: Administrator
'''

import wx
import wx.grid

"""
Mixin for wx.grid to implement cut/copy/paste and undo/redo.
Handlers are in the method Key below.  Other handlers (e.g., menu, toolbar) should call the functions in OnMixinKeypress.
"""
class PyWXGridEditMixin():
    """ A Copy/Paste and undo/redo mixin for wx.grid. Undo/redo is per-table, not yet global."""
    def __init_mixin__(self, padre=False):
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
        self.padre= padre
        
    def setPadreCallBack(self,padreObj):
        self.padre = padreObj
        
    def OnMixinKeypress(self, event):
        """Keystroke handler."""
        key = event.GetKeyCode() 
        if key == ord(" ") and event.ShiftDown():
            #self.SelectRow(self.GetGridCursorRow())
            self.SelectCol(self.GetGridCursorCol())
            return
        
        if key == wx.WXK_DELETE: self.Delete()
        
        if not event.ControlDown():
            event.Skip()
            return
        
        if key == 67:         self.Copy()
        elif key == 86:       self.OnPaste()
        elif key == ord("X"): self.OnCut()
        elif key == ord("Z"): self.Undo()
        elif key == ord("Y"): self.Redo() # elif key == ord(" "): self.SelectCol(self.GetGridCursorCol())
        elif key:  event.Skip()
        
    def Mixin_callbackChangeCell(self,rango):
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
            rowAsString = list()
            for c in range (left, left+cols):
                if self.CellInGrid(r,c):
                    try:
                        cellValue= str(self.GetCellValue(r, c))
                    except:
                        cellValue= self.GetCellValue(r, c)
                    rowAsString.append(cellValue)                    
                    
            # rowAsString = [str(self.GetCellValue(r, c)) for c in range(left, left+cols) if self.CellInGrid(r,c)]
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
            padre= self.GetParent() 
            #padre.m_grid.SetGridCursor(top, left) # se espera que el parent sea el grid

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
            padre= self.GetParent() 
            #padre.m_grid.SetGridCursor(top, left) # se espera que el parent sea el grid

if __name__ == '__main__':
        import sys
        app = wx.PySimpleApp()
        frame = wx.Frame(None, -1, size=(700,500), title = "wx.Grid example")

        grid = wx.grid.Grid(frame)
        grid.CreateGrid(20,6)

        # To add capability, mix it in, then set key handler, or add call to grid.Key() in your own handler
        wx.grid.Grid.__bases__ += (PyWXGridEditMixin,)
        grid.__init_mixin__()

        grid.SetDefaultColSize(70, 1)
        grid.EnableDragGridSize(False)
        
        grid.SetCellValue(0,0,"Col is")
        grid.SetCellValue(1,0,"Read Only")
        grid.SetCellValue(1,1,"hello")
        grid.SetCellValue(2,1,"23")
        grid.SetCellValue(4,3,"greren")
        grid.SetCellValue(5,3,"geeges")
        
        # make column 1 multiline, autowrap
        ##cattr = wx.grid.GridCellAttr()
        ##cattr.SetEditor(wx.grid.GridCellAutoWrapStringEditor())
        ##cattr.SetRenderer(wx.grid.GridCellAutoWrapStringRenderer())
        ##grid.SetColAttr(1, cattr)
        
        frame.Show(True)
        app.MainLoop()
