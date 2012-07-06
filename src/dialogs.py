# Copyrigth 2012 Sebastian Lopez Buritica 
# Colombia

import  wx

# creating a class to make pairs
#<p> INIT MAKE PAIRS
import  wx.grid as gridlib
class CustomDataTable( gridlib.PyGridTableBase):
    def __init__( self, columnNames, choiceNames, rowNumber):
        gridlib.PyGridTableBase.__init__( self)
        
        if isinstance( choiceNames, (str,)):
            choiceNames= [choiceNames]

        self.colLabels = columnNames
        group= lambda x,y: x+','+y
        
        if len( choiceNames)>1:
            colsResume= reduce( group,  choiceNames[1:],  choiceNames[0])
        elif len( choiceNames) == 1:
            colsResume= choiceNames[0]
        else:
            raise StandardError('You input bad type data as choiceNames variable')
        
        self.dataTypes = [gridlib.GRID_VALUE_CHOICE + ":,"+colsResume 
                          for i in range(len(columnNames))]
        self.data= [[u'' for i in range(len(columnNames))] for j in range(rowNumber)]

    #--------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberRows(self):
        return  len(self.data[0])+1

    def GetNumberCols(self):
        return len(self.data[0])

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return True

    # Get/Set values in the table.  The Python version of these
    # methods can handle any data-type, (as long as the Editor and
    # Renderer understands the type too,) not just strings as in the
    # C++ version.
    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        def innerSetValue(row, col, value):
            try:
                self.data[row][col] = value
            except IndexError:
                # add a new row
                self.data.append([''] * self.GetNumberCols())
                innerSetValue(row, col, value)

                # tell the grid we've added a row
                msg = gridlib.GridTableMessage(self,            # The table
                                               gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                                               1                                       # how many
                                               )

                self.GetView().ProcessTableMessage(msg)
        innerSetValue(row, col, value) 

    #--------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return self.colLabels[col]

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        return self.dataTypes[col]

    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, typeName):
        colType = self.dataTypes[col].split(':')[0]
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)
    
class CustTableGrid(gridlib.Grid):
    def __init__(self, parent, colNames, choices, rowNumber):
        gridlib.Grid.__init__(self, parent, -1)
        table = CustomDataTable(colNames, choices, rowNumber)
        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(table, True)
        self.SetRowLabelSize(0)
        self.SetMargins(0,0)
        self.AutoSizeColumns(False)

        gridlib.EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)


    ## I do this because I don't like the default behaviour of not starting the
    ## cell editor on double clicks, but only a second click.
    def OnLeftDClick(self, evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

class makePairs(wx.Panel):
    def __init__(self, parent, id, colNames, choices, rowNumber= 20):
        wx.Panel.__init__(self, parent, id, style=0)

        self.grid = CustTableGrid(self, colNames, choices, rowNumber)
        #b = wx.Button(self, -1, "Another Control...")
        #b.SetDefault()
        bs = wx.BoxSizer(wx.VERTICAL)
        bs.Add(self.grid, 1, wx.GROW|wx.ALL, 5)
        #bs.Add(b)
        self.SetSizer(bs)
        
    def GetValue(self ):
        # reading the data by rows and check consistency
        result= list()
        numCols= self.grid.GetNumberCols()
        for row in range(self.grid.GetNumberRows()):
            rowdata= [self.grid.GetCellValue(row,col) for col in range(numCols)]
            if numCols == sum([1 for value in rowdata if value != u'']):
                result.append(rowdata)
        return result

#  END MAKE PAIRS /<p>
class NumTextCtrl(wx.TextCtrl):
    '''a text ctrl that only accepts numbers'''
    def __init__(self, parent, *args, **params):
        wx.TextCtrl.__init__(self, parent, *args, **params)
        self.Bind(wx.EVT_TEXT, self._textChange)

    def _textChange(self,event):
        texto = self.GetValue()
        if len(texto) == 0:
            return
        allowed= [ str(x) for x in range(11)]
        allowed.extend([wx.GetApp().DECIMAL_POINT, '-'])
        newstr= [x for x in texto if x in allowed]
        if len(newstr) == 0:
            newstr = u''
        else:
            func = lambda x,y: x+y
            newstr= reduce(func, newstr)
        # prevent infinite recursion
        if texto == newstr:
            return
        self.SetValue(newstr)
        
    def GetAsNumber(self):
        prevResult = self.Value
        if len(prevResult) == 0:
            prevResult = None
        else:
            try:
                prevResult = float(prevResult.replace(wx.GetApp().DECIMAL_POINT, '.'))
            except:
                prevResult = None
        return prevResult
    
class CheckListBox( wx.Panel, object ):
    def __init__( self, parent , *args, **params):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1, -1 ), style = wx.TAB_TRAVERSAL )

        bSizer8 = wx.BoxSizer( wx.VERTICAL )

        bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_button1 = wx.Button( self, wx.ID_ANY, u"All", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        bSizer9.Add( self.m_button1, 0, 0, 5 )

        self.m_button2 = wx.Button( self, wx.ID_ANY, u"None", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        bSizer9.Add( self.m_button2, 0, 0, 5 )

        self.m_button3 = wx.Button( self, wx.ID_ANY, u"Invert", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        bSizer9.Add( self.m_button3, 0, 0, 5 )

        bSizer8.Add( bSizer9, 0, wx.EXPAND, 5 )

        self.m_checkList2 = wx.CheckListBox( self, *args, **params )
        bSizer8.Add( self.m_checkList2, 1, wx.EXPAND, 5 )

        self.SetSizer( bSizer8 )
        self.Layout()

        # Connect Events
        self.m_button1.Bind( wx.EVT_BUTTON, self.All )
        self.m_button2.Bind( wx.EVT_BUTTON, self.none )
        self.m_button3.Bind( wx.EVT_BUTTON, self.Invert )
        
    def __getattribute__(self, name):
        #import types
        #types.MethodType(self, instance, instance.__class__)
        try:
            return object.__getattribute__(self, name)
            
        except AttributeError:
            wrapee = self.m_checkList2.__getattribute__( name)
            try:
                return getattr(wrapee, name)
            except AttributeError:
                return wrapee  # detect a property value

    # Virtual event handlers, override them in your derived class
    def All( self, event ):
        self.m_checkList2.Checked= range(len(self.m_checkList2.Items))
        customEvent = wx.PyCommandEvent(wx.EVT_CHECKLISTBOX.typeId, self.m_checkList2.GetId())
        self.GetEventHandler().ProcessEvent(customEvent)

    def none( self, event ):
        self.m_checkList2.Checked= ()
        customEvent = wx.PyCommandEvent(wx.EVT_CHECKLISTBOX.typeId, self.m_checkList2.GetId())
        self.GetEventHandler().ProcessEvent(customEvent)
        
    def Invert( self, event ):
        # identifying not checked
        checked= self.m_checkList2.Checked
        notchecked= [pos for pos in range(len((self.m_checkList2.Items)))
                     if not(pos in checked)]
        self.m_checkList2.Checked= ()
        self.m_checkList2.Checked= notchecked
        customEvent = wx.PyCommandEvent(wx.EVT_CHECKLISTBOX.typeId, self.m_checkList2.GetId())
        self.GetEventHandler().ProcessEvent(customEvent)

class SixSigma( wx.Dialog ):
    def __init__( self, parent, colNames ):
        ''' colNames: a list of column Names'''
        if not isinstance(colNames, (list, tuple)):
            return list()
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Six Sigma Pack", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer3 = wx.BoxSizer( wx.VERTICAL )

        sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Select Columns to analyse" ), wx.VERTICAL )

        m_checkList2Choices = colNames
        self.m_checkList2 = CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,70 ), m_checkList2Choices, 0 )
        sbSizer2.Add( self.m_checkList2, 0, wx.ALL|wx.EXPAND, 5 )
        
        

        bSizer3.Add( sbSizer2, 0, wx.EXPAND, 5 )

        sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Limits" ), wx.VERTICAL )

        bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_textCtrl1 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer5.Add( self.m_textCtrl1, 0, wx.ALL, 5 )

        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Upper Control Limit", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        bSizer5.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sbSizer1.Add( bSizer5, 1, wx.EXPAND, 5 )

        bSizer6 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_textCtrl3 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer6.Add( self.m_textCtrl3, 0, wx.ALL, 5 )

        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Lower Control Limit", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        bSizer6.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sbSizer1.Add( bSizer6, 1, wx.EXPAND, 5 )

        bSizer7 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_textCtrl4 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer7.Add( self.m_textCtrl4, 0, wx.ALL, 5 )

        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"Target value", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        bSizer7.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sbSizer1.Add( bSizer7, 1, wx.EXPAND, 5 )


        bSizer3.Add( sbSizer1, 1, wx.EXPAND, 5 )

        sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )

        bSizer8 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_spinCtrl1 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), wx.SP_ARROW_KEYS, 1, 10, 6 )
        bSizer8.Add( self.m_spinCtrl1, 0, wx.ALL, 5 )

        self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"Use tolerance of  k  in  k*Sigma", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )
        bSizer8.Add( self.m_staticText6, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sbSizer3.Add( bSizer8, 0, wx.EXPAND, 5 )

        bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_spinCtrl2 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), wx.SP_ARROW_KEYS, 2, 15, 2)
        bSizer9.Add( self.m_spinCtrl2, 0, wx.ALL, 5 )

        self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, u"Subgroup Size", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )
        bSizer9.Add( self.m_staticText7, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sbSizer3.Add( bSizer9, 0, wx.EXPAND, 5 )


        bSizer3.Add( sbSizer3, 0, wx.EXPAND, 5 )

        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        m_sdbSizer2 = wx.StdDialogButtonSizer()
        self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
        self.m_sdbSizer2Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer2.AddButton( self.m_sdbSizer2Cancel )
        m_sdbSizer2.Realize();

        bSizer4.Add( m_sdbSizer2, 1, wx.EXPAND, 5 )


        bSizer3.Add( bSizer4, 0, wx.ALL|wx.EXPAND, 5 )

        self.SetSizer( bSizer3 )
        self.Layout()
        bSizer3.Fit( self )

        self.Centre( wx.BOTH )
        self._BindEvents()

    def _BindEvents(self):
        self.Bind(wx.EVT_CHECKLISTBOX, self.lstboxChange)

    def lstboxChange(self, event):
        if len(self.m_checkList2.Checked) < 2:
            self.m_spinCtrl2.Enabled= True
        else:
            self.m_spinCtrl2.Enabled= False

    def GetValue(self):
        result= list()
        if len(self.m_checkList2.Checked) == 0:
            result.append([])
        else:
            result.append([self.m_checkList2.Items[pos] for pos in self.m_checkList2.Checked])
        result.append(self.m_textCtrl1.GetAsNumber())
        result.append(self.m_textCtrl3.GetAsNumber())
        result.append(self.m_textCtrl4.GetAsNumber())
        result.append(self.m_spinCtrl1.Value)
        result.append(self.m_spinCtrl2.Value)
        return result

class _MyFrame1 ( wx.Frame ):
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY,
                            title = wx.EmptyString, pos = wx.DefaultPosition,
                            size = wx.Size( -1, -1 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer10 = wx.BoxSizer( wx.VERTICAL )

        self.m_button8 = wx.Button( self, wx.ID_ANY, u"Show Dialog", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer10.Add( self.m_button8, 0, wx.ALL, 5 )


        self.SetSizer( bSizer10 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_button8.Bind( wx.EVT_BUTTON, self.showDialog )


    # Virtual event handlers, override them in your derived class
    def showDialog( self, event ):

        dlg = SixSigma(self,[str(i) for i in range(20)])
        if dlg.ShowModal() == wx.ID_OK:
            print "ok"
        dlg.Destroy()


if __name__ == '__main__':
    app = wx.App()
    frame = _MyFrame1(None)
    frame.Show()
    app.MainLoop()
    