__all__ = ['datePickerEditor']

import string
import wx
import wx.grid as Grid

class datePickerEditor(Grid.PyGridCellEditor):
    """
    This GridCellEditor allows you to date pick from a calendar inside the
    cell of a grid.
    """
    def __init__(self):
        Grid.PyGridCellEditor.__init__(self)

    def Create(self, parent, id, evtHandler):
        """
        Called to create the control, which must derive from wx.Control.
        """
        self._picker = wx.DatePickerCtrl(parent, id, style=wx.DP_DROPDOWN
                                          | wx.DP_SHOWCENTURY)
        self.startingDate = None
        self.SetControl(self._picker)
        if evtHandler:
            self._picker.PushEventHandler(evtHandler)

    def SetSize(self, rect):
        """
        Called to position/size the edit control within the cell rectangle.
        If you don't fill the cell (the rect) then be sure to override
        PaintBackground and do something meaningful there.
        """
        self._picker.SetDimensions( rect.x, rect.y, rect.width+2, rect.height+2,
                               wx.SIZE_ALLOW_MINUS_ONE)

    def Show(self, show, attr):
        """
        Show or hide the edit control.  You can use the attr (if not None)
        to set colours or fonts for the control.
        """
        super( datePickerEditor, self).Show( show, attr)

    def PaintBackground( self, rect, attr):
        """
        Draws the part of the cell not occupied by the edit control.  The
        base  class version just fills it with background colour from the
        attribute.  In this class the edit control fills the whole cell so
        don't do anything at all in order to reduce flicker.
        """
        pass

    def BeginEdit( self, row, col, grid):
        """
        Fetch the value from the table and prepare the edit control
        to begin editing.  Set the focus to the edit control.
        *Must Override*
        """
        self.startValue = str(grid.GetTable().GetValue(row, col)).strip()
        if not self.startValue == '':
            # Split the string up and then insert it in there
            tmpDate = wx.DateTime()
            tmpDate.ParseDate(self.startValue)
            self._picker.SetValue(tmpDate)
            self.startingDate = tmpDate
        else:
            self.startingDate = None
        self._picker.SetFocus()

    def EndEdit( self, row, col, grid, *args,**params):
        """
        Complete the editing of the current cell. Returns True if the value
        has changed.  If necessary, the control may be destroyed.
        *Must Override*
        """
        changed = False
        val = self._picker.GetValue().GetDateOnly()
        if val.Format("%d/%m/%Y") != self.startValue:
            self.startValue = val.Format("%d/%m/%Y")
            grid.GetTable().SetValue(row, col, str(val.Format("%d/%m/%Y"))) # update the table
            changed = True
            # se hace activa la celda contigua COMO, evt.skip
        return changed

    def Reset( self):
        """
        Reset the value in the control back to its starting value.
        *Must Override*
        """
        if self.startingDate is not None:
            self._picker.SetValue(self.startingDate)

    def IsAcceptedKey( self, evt):
        """
        Return True to allow the given key to start editing: the base class
        version only checks that the event has no modifiers.  F2 is special
        and will always start the editor.
        """
        # or do it ourselves
        return (not (evt.ControlDown() or evt.AltDown()) and
                evt.GetKeyCode() != wx.WXK_SHIFT)

    def StartingKey( self, evt):
        """
        If the editor is enabled by pressing keys on the grid, this will be
        called to let the editor do something about that first key if desired.
        """
        key = evt.GetKeyCode()
        if key > 256 : # cuando se presiona la tecla End chr(key) produce un error
            return
        ch = None
        if key in [ wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3,
                    wx.WXK_NUMPAD4, wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7,
                    wx.WXK_NUMPAD8, wx.WXK_NUMPAD9
                    ]:
            ch = ch = chr(ord('0') + key - wx.WXK_NUMPAD0)
        elif key < 256 and key >= 0 and chr(key) in string.printable: # key &lt;= 256 and key &gt;= 0 and
            ch = chr(key)
        evt.Skip()

    def StartingClick( self):
        """
        If the editor is enabled by clicking on the cell, this method will be
        called to allow the editor to simulate the click on the control if
        needed.
        """
        pass

    def Destroy( self):
        """final cleanup"""
        super(datePickerEditor, self).Destroy()

    def Clone( self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return datePickerEditor()