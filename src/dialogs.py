import wx

class NumTextCtrl(wx.TextCtrl):
    '''a text ctrl that only acepts numbers'''
    def __init__(self, parent, *args, **params):
        wx.TextCtrl.__init__(self, parent, *args, **params)
        self.Bind(wx.EVT_TEXT, self._textChange)

    def _textChange(self,event):
        texto = self.GetValue()
        if len(texto) == 0:
            return
        allowed= [ str(x) for x in range(11)]
        allowed.extend(['.','-'])
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
                prevResult = float(prevResult)
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

    # Virtual event handlers, overide them in your derived class
    def All( self, event ):
        self.m_checkList2.Checked= range(len(self.m_checkList2.Items))
        customEvent = wx.PyCommandEvent(wx.EVT_CHECKLISTBOX.typeId, self.m_checkList2.GetId())
        self.GetEventHandler().ProcessEvent(customEvent)

    def none( self, event ):
        self.m_checkList2.Checked= ()
        customEvent = wx.PyCommandEvent(wx.EVT_CHECKLISTBOX.typeId, self.m_checkList2.GetId())
        self.GetEventHandler().ProcessEvent(customEvent)
        
    def Invert( self, event ):
        # identifing not checked
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


    # Virtual event handlers, overide them in your derived class
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
    