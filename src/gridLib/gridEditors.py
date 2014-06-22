__all__ = ['DATE','HOUR','FLOAT',]

import string
import wx
import wx.grid as Grid
from easyDialog.easyDialog import IntTextCtrl, NumTextCtrl
import wx.lib.masked as masked
import datetime

#newControl  = masked.TextCtrl( self, -1, "",
                     #mask         = control[1],
                     #excludeChars = control[2],
                     #formatcodes  = control[3],
                     #includeChars = "",
                     #validRegex   = control[4],
                     #validRange   = control[5],
                     #choices      = control[6],
                     #choiceRequired = True,
                     #defaultValue = control[7],
                     #demo         = True,
                     #name         = control[0])

def numberFormatInterpreter(format):
    """Given the format """
class BIGINT(Grid.PyGridCellEditor):
    pass
class BINARY(Grid.PyGridCellEditor):
    pass
class BLOB(Grid.PyGridCellEditor):
    pass
class BOOLEAN(Grid.PyGridCellEditor):
    pass
class BOOLEANTYPE(Grid.PyGridCellEditor):
    pass
class CHAR(Grid.PyGridCellEditor):
    pass
class CLOB(Grid.PyGridCellEditor):
    pass

class TestComboTreeBox(wx.Panel, wx.Control):
    def __init__(self, parent):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition,
                            size = wx.DefaultSize, style = wx.TAB_TRAVERSAL )
        wx.Control.__init__(self, parent)

        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        from wx.lib.combotreebox import ComboTreeBox
        self.comboBox = ComboTreeBox(self, style= 0) ## |wx.CB_SORT) # wx.CB_READONLY

         # reading the contents of the app
        dictContabilidad= wx.GetApp().dictContabilidad

        padre= self.comboBox.Append( 'plan contable 2006')
        for key, value in dictContabilidad.items():
            self.comboBox.Append( key.__str__() + '-' + value, parent=  padre)

        bSizer1.Add( self.comboBox, 0, 0 , border=0)
        bSizer1.Fit(self.comboBox)
        self.SetSizer( bSizer1 )
        self.Layout()

##### needs to be checked
class CUENTA(Grid.PyGridCellEditor):
    """Requires app.dictContabilidad as a dict containing the """
    def __init__(self):
        Grid.PyGridCellEditor.__init__(self)

    def Create(self, parent, id, evtHandler):
        """
        Called to create the control, which must derive from wx.Control.
        *Must Override*
        """
        self._tc= TestComboTreeBox(parent)
        self.SetControl(self._tc)
        if evtHandler:
            self._tc.PushEventHandler(evtHandler)

    def SetSize(self, rect):
        """
        Called to position/size the edit control within the cell rectangle.
        If you don't fill the cell (the rect) then be sure to override
        PaintBackground and do something meaningful there.
        """
        self._tc.SetDimensions(rect.x, rect.y, rect.width+2, rect.height+2,
                               wx.SIZE_ALLOW_MINUS_ONE)
        self._tc.Fit()

    def Show(self, show, attr):
        """
        Show or hide the edit control.  You can use the attr (if not None)
        to set colours or fonts for the control.
        """
        super(CUENTA, self).Show(show, attr)

    def PaintBackground(self, rect, attr):
        """
        Draws the part of the cell not occupied by the edit control.  The
        base  class version just fills it with background colour from the
        attribute.  In this class the edit control fills the whole cell so
        don't do anything at all in order to reduce flicker.
        """
        return

    def BeginEdit(self, row, col, grid):
        """
        Fetch the value from the table and prepare the edit control
        to begin editing.  Set the focus to the edit control.
        *Must Override*
        """
        self.startValue = grid.GetTable().GetValue(row, col)
        self._tc.comboBox.SetValue(self.startValue)
        self._tc.SetFocus()

    def EndEdit(self, row, col, grid, oldVal):
        """
        End editing the cell.  This function must check if the current
        value of the editing control is valid and different from the
        original value (available as oldval in its string form.)  If
        it has not changed then simply return None, otherwise return
        the value in its string form.
        *Must Override*
        """
        changed = False
        val = self._tc.comboBox.GetValue()
        if val != self.startValue:
            changed = True
        return changed

    def ApplyEdit(self, row, col, grid):
        """
        This function should save the value of the control into the
        grid or grid table. It is called only after EndEdit() returns
        a non-None value.
        *Must Override*
        """
        val = self._tc.comboBox.GetValue()
        # check if it's a valid time value
        grid.GetTable().SetValue(row, col, val) # update the table
        self.startValue = val
        self._tc.comboBox.SetValue(val)

    def Reset(self):
        """
        Reset the value in the control back to its starting value.
        *Must Override*
        """
        self._tc.comboBox.SetValue(self.startValue)

    def IsAcceptedKey(self, evt):
        """
        Return True to allow the given key to start editing: the base class
        version only checks that the event has no modifiers.  F2 is special
        and will always start the editor.
        """

        ## We can ask the base class to do it
        #return super(MyCellEditor, self).IsAcceptedKey(evt)

        # or do it ourselves
        return (not (evt.ControlDown() or evt.AltDown()) and
                evt.GetKeyCode()  not in (wx.WXK_SHIFT, wx.WXK_DELETE, wx.WXK_NUMPAD_ENTER,wx.WXK_EXECUTE ))

    def StartingKey(self, evt):
        """
        If the editor is enabled by pressing keys on the grid, this will be
        called to let the editor do something about that first key if desired.
        """
        key = evt.GetKeyCode()
        ch = None
        if key in [ wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3,
                    wx.WXK_NUMPAD4, wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7,
                    wx.WXK_NUMPAD8, wx.WXK_NUMPAD9
                    ]:

            ch = ch = chr(ord('0') + key - wx.WXK_NUMPAD0)

        elif key < 256 and key >= 0 and chr(key) in string.printable:
            ch = chr(key)

        if ch is not None:
            # For this example, replace the text.  Normally we would append it.
            #self._tc.AppendText(ch)
            self._tc.comboBox.SetValue(ch)
            #self._tc.SetInsertionPointEnd()
        else:
            evt.Skip()

    def Clone( self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return CUENTA()

    def Destroy( self):
        """final cleanup"""
        super(CUENTA, self).Destroy()

class HOUR(Grid.PyGridCellEditor):
    """
    This is a sample GridCellEditor that shows you how to make your own custom
    grid editors.  All the methods that can be overridden are shown here.  The
    ones that must be overridden are marked with "*Must Override*" in the
    docstring.
    """
    def __init__(self):
        Grid.PyGridCellEditor.__init__(self)

    def Create(self, parent, id, evtHandler):
        """
        Called to create the control, which must derive from wx.Control.
        *Must Override*
        """

        self._tc = masked.TextCtrl(parent, -1, "",
                               mask = "##:##", # excludeChars = "",
                               # formatcodes = 'F^-',     # validRegex = "^\(\d{3}\) \d{3}-\d{4}",
                               # validRange = '',
                               # validRegex= '\d{2}:\d{2}',
                               #choiceRequired = True,
                               #demo = True,
                               #name = __("Hora")
                               )

        #self._tc.SetInsertionPoint(0)
        self.SetControl(self._tc)
        if evtHandler:
            self._tc.PushEventHandler(evtHandler)

    def SetSize(self, rect):
        """
        Called to position/size the edit control within the cell rectangle.
        If you don't fill the cell (the rect) then be sure to override
        PaintBackground and do something meaningful there.
        """
        self._tc.SetDimensions(rect.x, rect.y, rect.width+2, rect.height+2,
                               wx.SIZE_ALLOW_MINUS_ONE)

    def Show(self, show, attr):
        """
        Show or hide the edit control.  You can use the attr (if not None)
        to set colours or fonts for the control.
        """
        super(HOUR, self).Show(show, attr)

    def PaintBackground(self, rect, attr):
        """
        Draws the part of the cell not occupied by the edit control.  The
        base  class version just fills it with background colour from the
        attribute.  In this class the edit control fills the whole cell so
        don't do anything at all in order to reduce flicker.
        """
        return

    def BeginEdit(self, row, col, grid):
        """
        Fetch the value from the table and prepare the edit control
        to begin editing.  Set the focus to the edit control.
        *Must Override*
        """
        self.startValue = grid.GetTable().GetValue(row, col)
        if self.startValue == u'':
            current_time = datetime.datetime.now().time()
            hour = current_time.hour
            minute = current_time.minute
            if hour < 10:   hour = '0' + hour.__str__()
            else:           hour= hour.__str__()
            if minute < 10: minute = '0' + minute.__str__()
            else:           minute = minute.__str__()
            self._tc.SetValue( hour+':'+minute)
        else:
            self._tc.SetValue(self.startValue)
        self._tc.SetInsertionPointEnd()
        self._tc.SetFocus()
        # For this example, select the text
        self._tc.SetSelection(0, self._tc.GetLastPosition())

    def EndEdit(self, row, col, grid, oldVal):
        """
        End editing the cell.  This function must check if the current
        value of the editing control is valid and different from the
        original value (available as oldval in its string form.)  If
        it has not changed then simply return None, otherwise return
        the value in its string form.
        *Must Override*
        """
        val = self._tc.GetValue()
        if val != self.startValue:
            return val
        else:
            return None

    def ApplyEdit(self, row, col, grid):
        """
        This function should save the value of the control into the
        grid or grid table. It is called only after EndEdit() returns
        a non-None value.
        *Must Override*
        """
        val = self._tc.GetValue()
        # check if it's a valid time value
        if not self.isValidTime(val):
            val= u''
        grid.GetTable().SetValue(row, col, val) # update the table
        self.startValue = val
        self._tc.SetValue(val)

    def isValidTime(self, value):
        try:
            hours= int(value[:1])
            if hours > 24:
                return False
            minutes = int(value[-2:])
            if minutes > 60:
                return False
            return True
        except:
            return False

    def Reset(self):
        """
        Reset the value in the control back to its starting value.
        *Must Override*
        """
        self._tc.SetValue(self.startValue)
        self._tc.SetInsertionPointEnd()

    def IsAcceptedKey(self, evt):
        """
        Return True to allow the given key to start editing: the base class
        version only checks that the event has no modifiers.  F2 is special
        and will always start the editor.
        """

        ## We can ask the base class to do it
        #return super(MyCellEditor, self).IsAcceptedKey(evt)

        # or do it ourselves
        return (not (evt.ControlDown() or evt.AltDown()) and
                evt.GetKeyCode()  not in (wx.WXK_SHIFT, wx.WXK_DELETE, wx.WXK_NUMPAD_ENTER,wx.WXK_EXECUTE ))

    def StartingKey(self, evt):
        """
        If the editor is enabled by pressing keys on the grid, this will be
        called to let the editor do something about that first key if desired.
        """
        key = evt.GetKeyCode()
        ch = None
        if key in [ wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3,
                    wx.WXK_NUMPAD4, wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7,
                    wx.WXK_NUMPAD8, wx.WXK_NUMPAD9
                    ]:

            ch = ch = chr(ord('0') + key - wx.WXK_NUMPAD0)

        elif key < 256 and key >= 0 and chr(key) in string.printable:
            ch = chr(key)

        if ch is not None:
            # For this example, replace the text.  Normally we would append it.
            #self._tc.AppendText(ch)
            self._tc.SetValue(ch)
            self._tc.SetInsertionPointEnd()
        else:
            evt.Skip()

    def StartingClick(self):
        """
        If the editor is enabled by clicking on the cell, this method will be
        called to allow the editor to simulate the click on the control if
        needed.
        """
        return

    def Destroy(self):
        """final cleanup"""
        super(HOUR, self).Destroy()

    def Clone(self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return HOUR(self.log)
class DATE(Grid.PyGridCellEditor):
    """
    This GridCellEditor allows you to date pick from a calendar inside the
    cell of a grid.
    """
    def __init__(self):
        Grid.PyGridCellEditor.__init__(self)

    #def _OnKeypress(self, evt):
    #    key = evt.GetKeyCode()
    #    if key == ord(" ") and evt.ShiftDown():
    #        return
    #    if evt.CmdDown():
    #        evt.Skip()
    #        return
    #    if key == wx.WXK_EXECUTE: ##320	WXK_EXECUTE
    #        evt.Skip()
    #        self.Destroy()
    #    elif key == wx.WXK_NUMPAD_ENTER: ##370	WXK_NUMPAD_ENTER
    #        evt.Skip()
    #        self.Destroy()
    #    elif key:
    #        evt.Skip()


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
        ### check if the user press the enter key
        ##self._picker.Bind(wx.EVT_TEXT_ENTER, self._OnKeypress)

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
        super( DATE, self).Show( show, attr)

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
        if val.Format("%d-%m-%Y") != self.startValue:
            self.startValue = val.Format("%d-%m-%Y")
            grid.GetTable().SetValue(row, col, str(val.Format("%d-%m-%Y"))) # update the table
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
                evt.GetKeyCode() not in (wx.WXK_SHIFT, wx.WXK_DELETE, wx.WXK_NUMPAD_ENTER, wx.WXK_EXECUTE))

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

    #def StartingClick( self):
    #    """
    #    If the editor is enabled by clicking on the cell, this method will be
    #    called to allow the editor to simulate the click on the control if
    #    needed.
    #    """
    #    pass

    def Destroy( self):
        """final cleanup"""
        super(DATE, self).Destroy()

    def Clone( self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return DATE()
class DATETIME(Grid.PyGridCellEditor):
    pass
class DECIMAL(Grid.PyGridCellEditor):
    pass
class FLOAT(Grid.PyGridCellEditor):
    """formats founded in 406 registers
    ['99990.99', '999999999990.99', '9990.9999', '0.0000', '9999999990.099', '999999999999990.9999',
     '0', '99999999999990.9999', '99990.09', '9999999990.09999', '99999990.9999', '990', '999',
     '999999999990.09', '999999999999990', '99999999999999999999', '999000000000', '90.000',
     '990000', '90.999', '99999999999999999990', '99999', '00000000', '99990', '9999', '990.99',
     '999900', '#.0099', '99999990.9', '9990', '999999999999999999900', '90.99', '99999999999999999990.99999',
     '99999999999999999999990', None, '9999999990.99999', '9999999990.9999', '99999999999999999990.09',
     '99999999999999999990.9999999999', '90.09', '9999990.9999', '999990.99', '999990', '999999990.09',
     '9999999999999999999999990', '0.099', '90.99999999', '999990.999', '9999999999999999999999999999999999999999',
     '00', '0000000000', '999990.09', '9999999990.0999999999', '90.9999999', '0000', '99', '99999999990000',
     '99999999990', '90', '9990.000', '9999999990.9999999999', '999.99', '99999999999900', '#.#', '#.99',
     '999999999990.999999', '999999990', '9999999990.09', '99000', '0.9999', '9999999990.99', '999999990.99', '9',
     '000000000', '9990.99', '#', '000', '9999999990', '99999999990.0000', '990.009999',
     '99999999999999999990.0999999999', '99999999', '000000', '9999999900', '99999990', '90.009999', '990.09',
     '9999999999999990.9999', '999999999990']
      unique symbols =9,0,None,#,.,
      Interpret # like a number without restrictions.
      Interpret 0 as the minimun required acepted  numerical value positions.
      Interpert 9 as the maximum option acepted numerical  value.
      Interpret . as the decimal point.
      Interpret None as none restriction about the format equals to #
    """
    def __init__(self, *args, **params):
        Grid.PyGridCellEditor.__init__(self)
        self._InitKey = None
        self.__min= None
        self.__max = None
        self.__longitudmaxima = None
        self.__format = None
        for key, value in params.items():
            allowedKeys = ['min','max','format',
                           'longitudmaxima','longitudminima',
                           'obligatorio','formato']
            if key in allowedKeys:
                setattr( self, key, value)
    @property
    def min(self):
        return self.__min
    @min.setter
    def min(self, value):
        if value != None:
            self.__min = float(value)

    @property
    def max(self):
        return self.__max
    @max.setter
    def max(self, value):
        if value != None:
            self.__max = float(value)

    @property
    def formato(self):
        return self.__format
    @formato.setter
    def formato(self, value):
        if value != None:
            self.__format = value

    @property
    def longitudmaxima(self):
        return self.__longitudmaxima
    @longitudmaxima.setter
    def longitudmaxima(self, value):
        if value != None:
            self.__longitudmaxima = int(value)

    @property
    def longitudminima(self):
        return self.__longitudminima
    @longitudminima.setter
    def longitudminima(self, value):
        if value != None:
            self.__longitudminima = int(value)

    @property
    def obligatorio(self):
        return self.__obligatorio
    @obligatorio.setter
    def obligatorio(self, value):
        self.__obligatorio = value

    def _OnKeypress(self, evt):
        key = evt.GetKeyCode()
        if key == ord(" ") and evt.ShiftDown():
            return
        if evt.CmdDown():
            evt.Skip()
            return
        if key == wx.WXK_EXECUTE: ##320	WXK_EXECUTE
            evt.Skip()
            self.Destroy()
        elif key == wx.WXK_NUMPAD_ENTER: ##370	WXK_NUMPAD_ENTER
            evt.Skip()
            self.Destroy()
        elif key:
            evt.Skip()

    def Create(self, parent, id, evtHandler):
        """
        Called to create the control, which must derive from wx.Control.
        """
        self._picker = NumTextCtrl(parent, id, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.NO_BORDER,
                                   min= self.min, max=self.max,
                                   longitudmaxima= self.longitudmaxima ,
                                   formato = self.formato)
        self.startingValue = None
        self.SetControl(self._picker)
        self._picker.Bind(wx.EVT_KEY_DOWN, self._OnKeypress)
        if evtHandler:
            self._picker.PushEventHandler(evtHandler)
        # check if the user press the enter key

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
        super( FLOAT, self).Show( show, attr)

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
        # check if the value of the init key is a number
        if self._InitKey in [ wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3,
                        wx.WXK_NUMPAD4, wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7,
                        wx.WXK_NUMPAD8, wx.WXK_NUMPAD9
                        ]:
            ch = chr(ord('0') + self.__InitKey - wx.WXK_NUMPAD0)
            self.startValue= chr(ord('0') + self.__InitKey - wx.WXK_NUMPAD0)
        else:
            self.startValue = str(grid.GetTable().GetValue(row, col)).strip()

        if not self.startValue == '':
            # Split the string up and then insert it in there
            self._picker.SetValue(self.startValue)
            self.startingValue = self.startValue
        else:
            self.startingValue = None
            self._picker.SetValue(u'')
        self._picker.SetFocus()

    def EndEdit( self, row, col, grid, *args,**params):
        """
        Complete the editing of the current cell. Returns True if the value
        has changed.  If necessary, the control may be destroyed.
        *Must Override*
        """
        changed = False
        if not self._picker.hasValidFormat:
            return changed

        val = self._picker.GetValueAsStr()
        if val != self.startValue and val != None:
            grid.GetTable().SetValue(row, col, str(val)) # update the table
            changed = True
            # se hace activa la celda contigua COMO, evt.skip
        return changed

    def Reset( self):
        """
        Reset the value in the control back to its starting value.
        *Must Override*
        """
        if self.startingValue is not None:
            self._picker.SetValue(self.startingValue)

    def IsAcceptedKey( self, evt):
        """
        Return True to allow the given key to start editing: the base class
        version only checks that the event has no modifiers.  F2 is special
        and will always start the editor.
        """
        # or do it ourselves
        return (not (evt.ControlDown() or evt.AltDown()) and
                evt.GetKeyCode() not in (wx.WXK_SHIFT, wx.WXK_DELETE))

    def StartingKey( self, evt):
        """
        If the editor is enabled by pressing keys on the grid, this will be
        called to let the editor do something about that first key if desired.
        """
        self._InitKey = key = evt.GetKeyCode()
        if key > 256 : # cuando se presiona la tecla End chr(key) produce un error
            return
        ch = None
        if key in [ wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3,
                    wx.WXK_NUMPAD4, wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7,
                    wx.WXK_NUMPAD8, wx.WXK_NUMPAD9
                    ]:
            ch = chr(ord('0') + key - wx.WXK_NUMPAD0)
        elif key < 256 and key >= 0 and chr(key) in string.printable: # key &lt;= 256 and key &gt;= 0 and
            ch = chr(key)
        evt.Skip()

    def Destroy( self):
        """final cleanup"""
        super(FLOAT, self).Destroy()

    def Clone( self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return FLOAT()
class INT(Grid.PyGridCellEditor):
    def __init__(self):
        Grid.PyGridCellEditor.__init__(self)

    #def _OnKeypress(self, evt):
    #    key = evt.GetKeyCode()
    #    if key == ord(" ") and evt.ShiftDown():
    #        return
    #    if evt.CmdDown():
    #        evt.Skip()
    #        return
    #    if key == wx.WXK_EXECUTE: ##320	WXK_EXECUTE
    #        evt.Skip()
    #        self.Destroy()
    #    elif key == wx.WXK_NUMPAD_ENTER: ##370	WXK_NUMPAD_ENTER
    #        evt.Skip()
    #        self.Destroy()
    #    elif key:
    #        evt.Skip()


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
        ### check if the user press the enter key
        ##self._picker.Bind(wx.EVT_TEXT_ENTER, self._OnKeypress)

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
        super( INT, self).Show( show, attr)

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
        val = self._picker.GetAsNumber()
        return val


        #changed = False
        #val = self._picker.GetValue().GetDateOnly()
        #if val.Format("%d/%m/%Y") != self.startValue:
        #    self.startValue = val.Format("%d/%m/%Y")
        #    grid.GetTable().SetValue(row, col, str(val.Format("%d/%m/%Y"))) # update the table
        #    changed = True
        #    # se hace activa la celda contigua COMO, evt.skip
        #return changed

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
                evt.GetKeyCode() not in (wx.WXK_SHIFT, wx.WXK_DELETE))

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

    #def StartingClick( self):
    #    """
    #    If the editor is enabled by clicking on the cell, this method will be
    #    called to allow the editor to simulate the click on the control if
    #    needed.
    #    """
    #    pass

    def Destroy( self):
        """final cleanup"""
        super(INT, self).Destroy()

    def Clone( self):
        """
        Create a new object which is the copy of this one
        *Must Override*
        """
        return INT()
class INTEGER(Grid.PyGridCellEditor):
    pass
class NCHAR(Grid.PyGridCellEditor):
    pass
class NULLTYPE(Grid.PyGridCellEditor):
    pass
class NUMERIC(Grid.PyGridCellEditor):
    pass
class NVARCHAR(Grid.PyGridCellEditor):
    pass
class REAL(Grid.PyGridCellEditor):
    pass
class SMALLINT(Grid.PyGridCellEditor):
    pass
class STRINGTYPE(Grid.PyGridCellEditor):
    pass
class TEXT(Grid.PyGridCellEditor):
    pass
class TIME(Grid.PyGridCellEditor):
    pass
class TIMESTAMP(Grid.PyGridCellEditor):
    pass
class VARBINARY(Grid.PyGridCellEditor):
    pass
class VARCHAR(Grid.PyGridCellEditor):
    # taken from pyspread
    """Custom cell editor

    All the methods that can be overridden are present. The ones that 
    must be overridden are marked with "*Must Override*" in the docstring.

    """

    def __init__(self):
        wx.grid.PyGridCellEditor.__init__(self)

    def Create(self, parent, id, evtHandler):
        """Called to create the control, which must derive from wx.Control.

        *Must Override*

        """

        self.parent = parent
        self._tc = wx.TextCtrl(parent, id, "")#, grid=self.parent)
        self._tc.SetInsertionPoint(0)
        self.SetControl(self._tc)

        if evtHandler:
            self._tc.PushEventHandler(evtHandler)

    def Show(self, show, attr):
        """
        Show or hide the edit control.  You can use the attr (if not None)
        to set colours or fonts for the control.

        """

        super(VARCHAR, self).Show(show, attr)

    def BeginEdit(self, row, col, grid):
        """Fetch value from the table and prepare the edit control for editing.

        Set the focus to the edit control.
        *Must Override*

        """

        self.start_value = grid.GetTable().GetValue(row, col)
        try:
            self._tc.SetValue(self.start_value)
        except TypeError:
            pass
        self._tc.SetInsertionPointEnd()

        # wx.GTK fix that prevents the grid from moving around
        grid.Freeze()
        gridpos = grid.GetScrollPos(wx.HORIZONTAL), \
            grid.GetScrollPos(wx.VERTICAL)
        self._tc.SetFocus()
        new_gridpos = grid.GetScrollPos(wx.HORIZONTAL), \
            grid.GetScrollPos(wx.VERTICAL)
        if gridpos != new_gridpos:
            grid.Scroll(*gridpos)
        grid.Thaw()

        # Select the text
        self._tc.SetSelection(-1, -1)

    def EndEdit(self, row, col, grid, *args,**params):
        """Complete the editing of the current cell.

        Returns True if the value has changed.  
        If necessary, the control may be destroyed.
        *Must Override*

        """
        changed = False

        val = self._tc.GetValue()

        if val != self.start_value:
            changed = True

            # Update the table

            grid.GetTable().SetValue(row, col, val) 

        self.start_value = ''

        # self.parent.pysgrid.unredo.mark()

        return changed

    def Reset(self):
        """
        Reset the value in the control back to its starting value.

        *Must Override*

        """

        self._tc.SetValue(self.start_value)
        self._tc.SetInsertionPointEnd()

    def StartingKey(self, evt):
        """If the editor is enabled by pressing keys on the grid, this will be

        called to let the editor do something about that first key if desired.

        """

        key = evt.GetKeyCode()
        char = None
        if key in [ wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, 
                    wx.WXK_NUMPAD3, wx.WXK_NUMPAD4, wx.WXK_NUMPAD5, 
                    wx.WXK_NUMPAD6, wx.WXK_NUMPAD7, wx.WXK_NUMPAD8, 
                    wx.WXK_NUMPAD9 ]:
            char = chr(ord('0') + key - wx.WXK_NUMPAD0)

        elif key < 256 and key >= 0 and chr(key) in string.printable:
            char = chr(key)

        if char is not None:
            #self._tc.AppendText(char)
            self._tc.ChangeValue(char) # Replace
            self._tc.SetInsertionPointEnd()
        else:
            self._tc.SetSelection(-1, -1)
            evt.Skip()

    def StartingClick(self):
        """If the editor is enabled by clicking on the cell,
        this method will be called to allow the editor to 
        simulate the click on the control if needed.

        """

        pass

    def Clone(self):
        """Create a new object which is the copy of this one

        *Must Override*

        """

        return VARCHAR()#parent=self)
class datePickerEditor(Grid.PyGridCellEditor):
    """
    This GridCellEditor allows you to date pick from a calendar inside the
    cell of a grid.
    """
    def __init__(self):
        Grid.PyGridCellEditor.__init__(self)
        self.startValue= None # to solve a trouble generated when whatching an emptycell

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
        changed=  False
        val=      self._picker.GetValue().GetDateOnly()
        if val.Format("%Y-%m-%d") != self.startValue:
            self.startValue = val.Format("%Y-%m-%d")
            grid.GetTable().SetValue(row, col, str(val.Format("%Y-%m-%d"))) # update the table
            changed= True
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