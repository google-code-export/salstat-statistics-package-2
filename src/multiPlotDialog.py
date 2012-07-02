'''
Created on 11/05/2012

@author: USUARIO
'''
# -*- coding: utf-8 -*- 

import wx
from easyDialog import CheckListBox

class data2Plotdiaglog( wx.Dialog ):
    def __init__( self, parent, lisOfColumns ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 253,184 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer6 = wx.BoxSizer( wx.VERTICAL )

        sbSizer16 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Select data to plot" ), wx.VERTICAL )

        m_checkList1Choices = []
        self.m_checkList1 = CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkList1Choices,  wx.LB_MULTIPLE  )
        sbSizer16.Add( self.m_checkList1, 1, wx.ALL|wx.EXPAND, 5 )

        bSizer6.Add( sbSizer16, 1, wx.EXPAND, 5 )

        m_sdbSizer2 = wx.StdDialogButtonSizer()
        self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
        self.m_sdbSizer2Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer2.AddButton( self.m_sdbSizer2Cancel )
        m_sdbSizer2.Realize();
        bSizer6.Add( m_sdbSizer2, 0, wx.EXPAND, 5 )
        self.SetSizer( bSizer6 )
        self.Layout()

        self.Centre( wx.BOTH )

        self.m_checkList1.SetItems(lisOfColumns)

    def getData(self):
        return self.m_checkList1.GetChecked()

class selectDialogData2plot(wx.Dialog):    
    def __init__( self, parent, lisOfColumns ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 198,136 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer5 = wx.BoxSizer( wx.VERTICAL )

        sbSizer15 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Select data to plot" ), wx.VERTICAL )

        fgSizer8 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer8.SetFlexibleDirection( wx.BOTH )
        fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText28 = wx.StaticText( self, wx.ID_ANY, u"X data", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText28.Wrap( -1 )
        fgSizer8.Add( self.m_staticText28, 0, wx.ALL, 5 )

        m_choice14Choices = []
        self.m_choice14 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice14Choices, 0 )
        self.m_choice14.SetSelection( 0 )
        fgSizer8.Add( self.m_choice14, 0, wx.ALL, 5 )

        self.m_staticText29 = wx.StaticText( self, wx.ID_ANY, u"Y data", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText29.Wrap( -1 )
        fgSizer8.Add( self.m_staticText29, 0, wx.ALL, 5 )

        m_choice15Choices = []
        self.m_choice15 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice15Choices, 0 )
        self.m_choice15.SetSelection( 0 )
        fgSizer8.Add( self.m_choice15, 0, wx.ALL, 5 )


        sbSizer15.Add( fgSizer8, 1, wx.EXPAND, 5 )


        bSizer5.Add( sbSizer15, 1, wx.EXPAND, 5 )

        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize();

        bSizer5.Add( m_sdbSizer1, 0, wx.EXPAND, 5 )


        self.SetSizer( bSizer5 )
        self.Layout()

        self.Centre( wx.BOTH )
        self.m_choice14.SetItems(lisOfColumns)
        self.m_choice15.SetItems(lisOfColumns)
        self.m_choice14.SetSelection(0)
        self.m_choice15.SetSelection(0)

    def getData(self):
        return (self.m_choice14.GetSelection(),self.m_choice15.GetSelection(),)

class scatterDialog( wx.Dialog ):
    def __init__( self, parent, aviableVariables ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer3 = wx.BoxSizer( wx.VERTICAL )

        bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

        m_checkList1Choices = []
        self.m_checkList1 = CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkList1Choices, 0 )
        bSizer4.Add( self.m_checkList1, 0, wx.ALL, 5 )

        fgSizer2 = wx.FlexGridSizer( 2, 1, 0, 0 )
        fgSizer2.SetFlexibleDirection( wx.BOTH )
        fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_button1 = wx.Button( self, wx.ID_ANY, u"Set X data", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer2.Add( self.m_button1, 0, wx.ALL, 5 )

        self.m_button2 = wx.Button( self, wx.ID_ANY, u"Set Y data", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer2.Add( self.m_button2, 0, wx.ALL, 5 )


        bSizer4.Add( fgSizer2, 1, wx.EXPAND, 5 )


        bSizer3.Add( bSizer4, 0, wx.EXPAND, 5 )

        sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Selected data" ), wx.VERTICAL )

        bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Series Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        bSizer5.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_textCtrl2 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer5.Add( self.m_textCtrl2, 1, wx.ALL, 5 )

        self.m_button5 = wx.Button( self, wx.ID_ANY, u"add", wx.DefaultPosition, wx.Size( 30,-1 ), 0 )
        bSizer5.Add( self.m_button5, 0, wx.ALL, 5 )


        sbSizer2.Add( bSizer5, 0, wx.EXPAND, 5 )

        bSizer6 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"X data", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )
        bSizer6.Add( self.m_staticText6, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_textCtrl3 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl3.Enable( False )

        bSizer6.Add( self.m_textCtrl3, 1, wx.ALL, 5 )


        sbSizer2.Add( bSizer6, 0, wx.EXPAND, 5 )

        bSizer7 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, u"Y data", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )
        bSizer7.Add( self.m_staticText7, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_textCtrl4 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl4.Enable( False )

        bSizer7.Add( self.m_textCtrl4, 1, wx.ALL, 5 )


        sbSizer2.Add( bSizer7, 0, wx.EXPAND, 5 )


        bSizer3.Add( sbSizer2, 0, wx.EXPAND, 5 )

        sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Current List to plot" ), wx.HORIZONTAL )

        m_listBox1Choices = []
        self.m_listBox1 = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,70 ), m_listBox1Choices, 0 )
        sbSizer3.Add( self.m_listBox1, 1, wx.ALL|wx.EXPAND, 5 )

        self.m_button4 = wx.Button( self, wx.ID_ANY, u"del", wx.DefaultPosition, wx.Size( 30,-1 ), 0 )
        sbSizer3.Add( self.m_button4, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


        bSizer3.Add( sbSizer3, 1, wx.EXPAND, 5 )

        m_sdbSizer3 = wx.StdDialogButtonSizer()
        self.m_sdbSizer3OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer3.AddButton( self.m_sdbSizer3OK )
        self.m_sdbSizer3Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer3.AddButton( self.m_sdbSizer3Cancel )
        m_sdbSizer3.Realize();

        bSizer3.Add( m_sdbSizer3, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( bSizer3 )
        self.Layout()
        bSizer3.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_button1.Bind( wx.EVT_BUTTON, self._OnSetXData )
        self.m_button2.Bind( wx.EVT_BUTTON, self._OnSetYData )
        self.m_button5.Bind( wx.EVT_BUTTON, self._OnAddSerie )
        self.m_button4.Bind( wx.EVT_BUTTON, self._OnRemoveSerie )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def _OnSetXData( self, event ):
        event.Skip()

    def _OnSetYData( self, event ):
        event.Skip()

    def _OnAddSerie( self, event ):
        event.Skip()

    def _OnRemoveSerie( self, event ):
        event.Skip()