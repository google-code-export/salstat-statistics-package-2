'''
Created on 27/10/2010
# 08 de nov de 2010:
-> llamado a GrandParent para el momento en que se deba hacer una operacion con EVT_GRID_CELL_CHANGE
#    el metodo dentro del parent se debe llamar GrandParent.OnRangeChange(self,range)
#    range=(top, left, #rows, #cols)
-> adicion de cambio en la posicion del cursor cuando se realiza un cambio en el grid
@author: Administrator
'''
__all__= ['PyWXGridEditMixin']
import wx
import wx.grid
from sei_glob import *


import wx.lib.newevent
# creating the evt of paste a cell
PasteEvt, EVT_GRID_PASTE = wx.lib.newevent.NewCommandEvent()
UndoEvt, EVT_GRID_UNDO = wx.lib.newevent.NewCommandEvent()
RedoEvt, EVT_GRID_REDO = wx.lib.newevent.NewCommandEvent()

BeforePasteEvt, EVT_GRID_BEFORE_PASTE = wx.lib.newevent.NewCommandEvent()
evtIDpaste=       wx.NewEventType()
evtIDBeforePaste= wx.NewEventType()
evtIDUndo= wx.NewEventType()
evtIDRedo= wx.NewEventType()

"""
Mixin for wx.grid to implement cut/copy/paste and undo/redo.
Handlers are in the method Key below.  Other handlers (e.g., menu, toolbar) should call the functions in OnMixinKeypress.
"""
try:
    from imagenes import imageEmbed
    EXISTIMAGES = True
except ImportError:
    EXISTIMAGES = False
    
class MyContextGrid(wx.Menu):
    # Clase para hacer el menu contextual del grid
    def __init__(self,parent,*args,**params):
        wx.Menu.__init__(self)
        self.parent = parent
        cortar =     wx.MenuItem(self, wx.NewId(), __('&Cut\tCtrl+X'))
        copiar =     wx.MenuItem(self, wx.NewId(), __('C&opy\tCtrl+C'))
        pegar =      wx.MenuItem(self, wx.NewId(), __('&Paste\tCtrl+V'))
        eliminar =   wx.MenuItem(self, wx.NewId(), __('&Del\tDel'))
        deshacer =   wx.MenuItem(self, wx.NewId(), __('&Undo\tCtrl+Z'))
        rehacer =    wx.MenuItem(self, wx.NewId(), __('&Redo\tCtrl+Y'))
        delRow=      wx.MenuItem(self, wx.NewId(), __('Del Row'))
        delCol=      wx.MenuItem(self, wx.NewId(), __('Del Col'))
        ##exportarCsv= wx.MenuItem(self, wx.NewId(), '&Export\tCtrl+E')
        
        if EXISTIMAGES:
            imagenes = imageEmbed()
            cortar.SetBitmap(imagenes.edit_cut)
            copiar.SetBitmap(imagenes.edit_copy)
            pegar.SetBitmap(imagenes.edit_paste)
            eliminar.SetBitmap(imagenes.cancel)
            deshacer.SetBitmap(imagenes.edit_undo)
            rehacer.SetBitmap(imagenes.edit_redo)
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
        self.Bind(wx.EVT_MENU, self.OnDelRow,      id= delRow.GetId())
        self.Bind(wx.EVT_MENU, self.OnDelCol,      id= delCol.GetId())
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
        self.parent.GetEventHandler().ProcessEvent( RedoEvt(evtIDRedo))
        evt.Skip()

    def OnDeshacer(self, evt):
        self.parent.Undo()
        self.parent.GetEventHandler().ProcessEvent( UndoEvt(evtIDUndo))
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
            self.parent.DeleteRows(currentRow)
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

class PyWXGridEditMixin:
    """ A Copy/Paste and undo/redo mixin for wx.grid. Undo/redo is per-table, not yet global."""
    def __init__(self):
        """caller must invoke this method to enable keystrokes, or call these handlers if they are overridden."""
        wx.EVT_KEY_DOWN(self, self.OnMixinKeypress)
        wx.grid.EVT_GRID_CELL_CHANGE(self, self.Mixin_OnCellChange)
        wx.grid.EVT_GRID_EDITOR_SHOWN(self, self.Mixin_OnCellEditor)
        self._undoStack = []
        self._redoStack = []
        self._stackPtr = 0
        self.change = True
        self.isSave = False
    @property
    def change(self):
        return self.__hasChanged
    @change.setter
    def change(self, value):
        self.__hasChanged = value
        if value ==  True:
            self.isSave = False
    @property
    def isSave(self):
        return self.__hasSave
    @isSave.setter
    def isSave(self, value):
        self.__hasSave= value
        if value == True:
            self.change= False

    def OnMixinKeypress(self, event):
        """Keystroke handler."""
        key = event.GetKeyCode() 
        if key == ord(" ") and event.ShiftDown():
            #self.SelectRow(self.GetGridCursorRow())
            self.SelectCol(self.GetGridCursorCol())
            return
        
        if key == wx.WXK_DELETE:
            self.Delete()
        
        if not event.CmdDown():
            event.Skip()
            return
        
        if   key == ord("C"): self.Copy()
        elif key == ord("V"): self.OnPaste()
        elif key == ord("X"): self.OnCut()
        elif key == ord("Z"): self.Undo()
        elif key == ord("Y"): self.Redo() # elif key == ord(" "): self.SelectCol(self.GetGridCursorCol())
        event.Skip()
        
    def Mixin_OnCellEditor(self, evt=None):
        """this method saves the value of cell before it's edited (when that value disappears)"""
        top, left, rows, cols = self.GetSelectionBox()[0]
        v = self.GetCellValue(top, left)
        self._editOldValue = v+"\n"

    def Mixin_OnCellChange(self, evt):
        """Undo/redo handler Use saved value from above for undo."""
        box=      self.GetSelectionBox()[0]
        newValue= self.GetCellValue(*box[:2])
        self.AddUndo(undo=(self.__Paste, (box, self._editOldValue)),
            redo=(self.__Paste, (box, newValue)))
        self._editOldValue = None
        evt.Skip()
    
    def GetSelectionBox(self):
        """Produce a set of selection boxes of the form (top, left, nrows, ncols)"""
        #For wxGrid, blocks, cells, rows and cols all have different selection notations.  
        #This captures them all into a single "box" tuple (top, left, rows, cols)
        gridRows=  self.GetNumberRows()
        gridCols=  self.GetNumberCols()
        tl, br =   self.GetSelectionBlockTopLeft(), self.GetSelectionBlockBottomRight()
        # need to reorder based on what should get copy/pasted first
        boxes=     []
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

        data=       self.Box2String(top, left, rows, cols)
        # Create text data object for use by TheClipboard
        clipboard=  wx.TextDataObject()
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
                    cellValue= self.GetCellValue(r, c)
                    if not isinstance(cellValue, (str, unicode)):
                        cellValue= cellValue.__str__()
                    rowAsString.append(cellValue)                    
            # rowAsString = [str(self.GetCellValue(r, c)) for c in range(left, left+cols) if self.CellInGrid(r,c)]
            data += str.join("\t",rowAsString) + "\n"
        return data    

    def OnPaste(self, ):
        """Event handler to paste from clipboard into grid.
        Data assumed to be separated by tab (columns) and "\n" (rows)."""
        clipboard = wx.TextDataObject()
        if wx.TheClipboard.Open():
            wx.TheClipboard.GetData(clipboard)
            wx.TheClipboard.Close()
        else:
            print "Can't open the clipboard"
        data=  clipboard.GetText()
        table= [r.split('\t') for r in data.splitlines()] # convert to array

        #Determine the paste area given the size of the data in the clipboard (clipBox) and the current selection (selBox)
        top, left, selRows, selCols= self.GetSelectionBox()[0]
        if len(table) ==0 or type(table[0]) is not list:
            table = [table]
        pBox= self._DeterminePasteArea(top, left, len(table), len(table[0]), selRows, selCols)
        self.AddUndo(undo=(self.__Paste, (pBox, self.Box2String(*pBox))),
            redo=(self.__Paste, (pBox, data)))
        self.__Paste(pBox, data)
        self.change= True
        
    def _DeterminePasteArea(self, top, left, clipRows, clipCols, selRows, selCols):
        """paste area rules: if 1-d selection (either directon separately) and 2-d clipboard, use clipboard size, otherwise use selection size"""
        pRows = selRows ==1 and clipRows > 1 and clipRows or selRows
        pCols = selCols ==1 and clipCols > 1 and clipCols or selCols
        return top, left, pRows, pCols
        
        if clipRows == 1 and clipCols == 1: # constrain paste range by what's in clipboard
            pRows, pCols = clipRows, clipCols 
        else: # constrain paste range by current selection
            pRows, pCols = selRows, selCols
        return top, left, pRows, pCols # the actual area we'll paste into
        
    def __Paste(self, box, dataString):
        #####################################
        ### setting attributes to the evt ###
        bptevt= BeforePasteEvt(evtIDBeforePaste)
        ptevt= PasteEvt(evtIDpaste)
        setattr(bptevt, 'box', box)
        setattr( ptevt, 'box', box)
        #####################################

        self.GetEventHandler().ProcessEvent( bptevt)
        top, left, rows, cols = box
        data= [r.split('\t') for r in dataString.splitlines()]
        if len(data) == 0 or type(data[0]) is not list:
            data= [data]
        # get sizes (rows, cols) of both clipboard and current selection
        dataRows, dataCols= len(data), len(data[0])
        # adding row and cols if needed
        lastCol, lastRow= self.GetNumberCols()-1, self.GetNumberRows()-1
        cols2add, rows2add= (left+dataCols)- lastCol, (top+dataRows)- lastRow
        if cols2add > 0:
            self.AppendCols(cols2add)
        if rows2add > 0:
            self.AppendRows(rows2add)
        try:
            for r in range(rows):
                row= top + r
                for c in range(cols):
                    col= left + c
                    try:
                    #if self.CellInGrid(row, col): # fails when updating a database
                        self.SetCellValue(row, col, data[r %dataRows][c % dataCols])
                    except:
                        pass
        except ZeroDivisionError:
            print "Zero division: Num_col "  +str(dataRows)+ ", Num_Fil " + str(dataCols)

        ## post the event
        #wx.PostEvent(self.GrandParent, PasteEvt(evtID))
        self.GetEventHandler().ProcessEvent( ptevt)

    def CellInGrid(self, r, c): # only paste data that actually falls on the table
        return r >=0 and c >=0 and r < self.GetNumberRows() and c < self.GetNumberCols()

    def OnCut(self):
        """Cut cells from grid into clipboard"""
        box = self.GetSelectionBox()[0]
        self.Copy()
        self.Delete() #this takes care of undo/redo
        self.change= True

    def Delete(self):
        """Clear Cell contents"""
        boxes = self.GetSelectionBox()
        for box in boxes: #allow multiple selection areas to be deleted
            # first, save data in undo stack
            self.AddUndo(undo=(self.__Paste, (box, self.Box2String(*box))),
                redo=(self.__Paste, (box, "\n")))
            self.__Paste(box, "\n")
        self.change= True
        
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
            #padre= self.GetParent() 
            #padre.m_grid.SetGridCursor(top, left) # se espera que el parent sea el grid
            self.change= True
            
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
            #padre= self.GetParent() 
            #padre.m_grid.SetGridCursor(top, left) # se espera que el parent sea el grid
            self.change= True
            
    def emptyTheBuffer(self):
        self._undoStack= list()
        self._redoStack= list()
        
class SqlPyWXGridEditMixin(PyWXGridEditMixin):
    def __init_mixin__(self):
        """caller must invoke this method to enable keystrokes, or call these handlers if they are overridden."""
        wx.EVT_KEY_DOWN(self, self.OnMixinKeypress)
        wx.grid.EVT_GRID_CELL_CHANGE(self, self.Mixin_OnCellChange)
        wx.grid.EVT_GRID_EDITOR_SHOWN(self, self.Mixin_OnCellEditor)
        self._undoStack = []
        self._redoStack = []
        self._stackPtr = 0
        
    def OnMixinKeypress(self, event):
        """Keystroke handler."""
        key = event.GetKeyCode() 
        if key == ord(" ") and event.ShiftDown():
            #self.SelectRow(self.GetGridCursorRow())
            self.SelectCol(self.GetGridCursorCol())
            return
        
        if key == wx.WXK_DELETE:
            self.Delete()
        
        if not event.CmdDown():
            event.Skip()
            return
        
        if   key == ord("C"): self.Copy()
        elif key == ord("V"): self.OnPaste()
        elif key == ord("X"): self.OnCut()
        elif key == ord("Z"): self.Undo()
        elif key == ord("Y"): self.Redo() # elif key == ord(" "): self.SelectCol(self.GetGridCursorCol())
        elif key:  event.Skip()
        
    def Mixin_OnCellEditor(self, evt=None):
        """this method saves the value of cell before it's edited (when that value disappears)"""
        top, left, rows, cols = self.GetSelectionBox()[0]
        v = self.GetCellValue(top, left)
        self._editOldValue = v+"\n"

    def Mixin_OnCellChange(self, evt):
        """Undo/redo handler Use saved value from above for undo."""
        box=      self.GetSelectionBox()[0]
        newValue= self.GetCellValue(*box[:2])
        self.AddUndo(undo=(self.__Paste, (box, self._editOldValue)),
            redo=(self.__Paste, (box, newValue)))
        self._editOldValue = None
        evt.Skip()
    
    def GetSelectionBox(self):
        """Produce a set of selection boxes of the form (top, left, nrows, ncols)"""
        #For wxGrid, blocks, cells, rows and cols all have different selection notations.  
        #This captures them all into a single "box" tuple (top, left, rows, cols)
        gridRows=  self.GetNumberRows()
        gridCols=  self.GetNumberCols()
        tl, br =   self.GetSelectionBlockTopLeft(), self.GetSelectionBlockBottomRight()
        # need to reorder based on what should get copy/pasted first
        boxes=     []
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

        data=       self.Box2String(top, left, rows, cols)
        # Create text data object for use by TheClipboard
        clipboard=  wx.TextDataObject()
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
                    cellValue= self.GetCellValue(r, c)
                    if not isinstance(cellValue, (str, unicode)):
                        cellValue= cellValue.__str__()
                    rowAsString.append(cellValue)                    
            # rowAsString = [str(self.GetCellValue(r, c)) for c in range(left, left+cols) if self.CellInGrid(r,c)]
            data += str.join("\t",rowAsString) + "\n"
        return data    

    def OnPaste(self):
        """Event handler to paste from clipboard into grid.
        Data assumed to be separated by tab (columns) and "\n" (rows)."""
        clipboard = wx.TextDataObject()
        if wx.TheClipboard.Open():
            wx.TheClipboard.GetData(clipboard)
            wx.TheClipboard.Close()
        else:
            print "Can't open the clipboard"
        data=  clipboard.GetText()
        table= [r.split('\t') for r in data.splitlines()] # convert to array

        #Determine the paste area given the size of the data in the clipboard (clipBox) and the current selection (selBox)
        top, left, selRows, selCols= self.GetSelectionBox()[0]
        if len(table) ==0 or type(table[0]) is not list:
            table = [table]
        pBox= self._DeterminePasteArea(top, left, len(table), len(table[0]), selRows, selCols)
        self.AddUndo(undo=(self.__Paste, (pBox, self.Box2String(*pBox))),
            redo=(self.__Paste, (pBox, data)))
        self.__Paste(pBox, data)
        
    def _DeterminePasteArea(self, top, left, clipRows, clipCols, selRows, selCols):
        """paste area rules: if 1-d selection (either directon separately) and 2-d clipboard, use clipboard size, otherwise use selection size"""
        pRows = selRows ==1 and clipRows > 1 and clipRows or selRows
        pCols = selCols ==1 and clipCols > 1 and clipCols or selCols
        return top, left, pRows, pCols
        
        if clipRows == 1 and clipCols == 1: # constrain paste range by what's in clipboard
            pRows, pCols = clipRows, clipCols 
        else: # constrain paste range by current selection
            pRows, pCols = selRows, selCols
        return top, left, pRows, pCols # the actual area we'll paste into
        
    def __Paste(self, box, dataString):
        #####################################
        ### setting attributes to the evt ###
        bptevt= BeforePasteEvt(evtIDBeforePaste)
        ptevt= PasteEvt(evtIDpaste)
        setattr(bptevt, 'box', box)
        setattr( ptevt, 'box', box)
        #####################################

        self.GetEventHandler().ProcessEvent( bptevt)
        top, left, rows, cols = box
        data= [r.split('\t') for r in dataString.splitlines()]
        if len(data) == 0 or type(data[0]) is not list:
            data= [data]
        # get sizes (rows, cols) of both clipboard and current selection
        dataRows, dataCols= len(data), len(data[0])
        # adding row and cols if needed
        lastCol, lastRow= self.GetNumberCols()-1, self.GetNumberRows()-1
        cols2add, rows2add= (left+dataCols)- lastCol, (top+dataRows)- lastRow
        if cols2add > 0:
            self.AppendCols(cols2add)
        if rows2add > 0:
            self.AppendRows(rows2add)
        try:
            for r in range(rows):
                row= top + r
                for c in range(cols):
                    col= left + c
                    try:
                    #if self.CellInGrid(row, col): # fails when updating a database
                        self.SetCellValue(row, col, data[r %dataRows][c % dataCols])
                    except:
                        pass
        except ZeroDivisionError:
            print "Zero division: Num_col "  +str(dataRows)+ ", Num_Fil " + str(dataCols)
        finally:
            self.hasChanged= True
            self.hasSaved=   False
        
        ## post the event
        #wx.PostEvent(self.GrandParent, PasteEvt(evtID))
        self.GetEventHandler().ProcessEvent( ptevt)

    def CellInGrid(self, r, c): # only paste data that actually falls on the table
        return r >=0 and c >=0 and r < self.GetNumberRows() and c < self.GetNumberCols()

    def OnCut(self):
        """Cut cells from grid into clipboard"""
        box = self.GetSelectionBox()[0]
        self.Copy()
        self.Delete() #this takes care of undo/redo
        self.hasChanged= True
        self.hasSaved= False

    def Delete(self):
        """Clear Cell contents"""
        boxes = self.GetSelectionBox()
        for box in boxes: #allow multiple selection areas to be deleted
            # first, save data in undo stack
            self.AddUndo(undo=(self.__Paste, (box, self.Box2String(*box))),
                redo=(self.__Paste, (box, "\n")))
            self.__Paste(box, "\n")
        self.hasChanged= True
        self.hasSaved= False
        
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
            #padre= self.GetParent() 
            #padre.m_grid.SetGridCursor(top, left) # se espera que el parent sea el grid
            self.hasChanged= True
            self.hasSaved= False
            
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
            #padre= self.GetParent() 
            #padre.m_grid.SetGridCursor(top, left) # se espera que el parent sea el grid
            self.hasChanged= True
            self.hasSaved= False
            
    def emptyTheBuffer(self):
        self._undoStack= list()
        self._redoStack= list()
      
    def Paste(self, box, dataString):
        bptevt= BeforePasteEvt(evtIDBeforePaste)
        ptevt= PasteEvt(evtIDpaste)
        setattr(bptevt, 'box', box)
        setattr( ptevt, 'box', box)
        self.GetEventHandler().ProcessEvent( bptevt)
        top, left, rows, cols = box
        data= [r.split('\t') for r in dataString.splitlines()]
        if len(data) == 0 or type(data[0]) is not list:
            data= [data]
        # get sizes (rows, cols) of both clipboard and current selection
        dataRows, dataCols= len(data), len(data[0])
        # adding row and cols if needed
        lastCol, lastRow= self.GetNumberCols()-1, self.GetNumberRows()-1
        cols2add, rows2add= (left+dataCols)- lastCol-1, (top+dataRows)- lastRow
        if cols2add <0: cols2add= 0
        if rows2add > 0:
            self.AppendRows(rows2add)
        try:
            for r in range(rows):
                row= top + r
                for c in range(cols-cols2add):
                    col= left + c
                    try:
                    #if self.CellInGrid(row, col): # fails when updating a database
                        self.SetCellValue(row, col, data[r %dataRows][c % dataCols])
                    except:
                        pass
        except ZeroDivisionError:
            print "Zero division: Num_col "  +str(dataRows)+ ", Num_Fil " + str(dataCols)
        finally:
            self.hasChanged= True
            self.hasSaved=   False
        
        ## post the event
        #wx.PostEvent(self.GrandParent, PasteEvt(evtID))
        self.GetEventHandler().ProcessEvent( ptevt)

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
