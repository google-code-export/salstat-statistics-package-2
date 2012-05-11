'''
Created on 11/05/2012
New plot system

@author: Sebastian lopez Buritica
License: GPL
'''
# wxPython module
import wx
import wx.aui
# Matplotlib Figure object
from matplotlib.figure import Figure
from matplotlib import font_manager
from matplotlib.widgets import Cursor
# Numpy functions for image creation
import numpy as np
from statlib.stats import linregress

# import the WxAgg FigureCanvas object, that binds Figure to
# WxAgg backend. In this case, this is a wxPanel
from matplotlib.backends.backend_wxagg import \
     FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.backends.backend_wx import StatusBarWx
from matplotlib.backend_bases import MouseEvent


class MpltFrame( wx.Frame ):
    def __init__( self, parent,typePlot = None, data2plot= None):
        '''
        MpltFrame( parent, typePlot, data2plot)

        typePlot:
        * plotLine
        * plotScatter
        * plotBar
        * plotBarH
        * plotPie
        * boxPlot
        * plotHistogram <pendiente>
        * plotPareto <pendiente>

        data2plot:
        ((serie1),(serie2),..,(serieEnd))

        serie depends on the typePlot as follows:
        * plotline
        ((x1data,y1data,legend1),(x2data,y2data,legend2))
        * plotScatter
        ((x1data,y1data,legend1),(x2data,y2data,legend2))
        * plotBbar
        ((x1data,legend1),(x2data,legend2),...,(xndata,legendn))
        * plotPie
        ((x1,legend1),(x2,legend2),...,(xn,legendn))
        * plotHistogram
        ((x1,),(x2,),...,(xn,))
        * plotPareto
        ((x1,x2,...,xn))
        '''
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 642,465 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        self.figpanel = MplCanvasFrame( self )
        self.m_mgr.AddPane( self.figpanel, wx.aui.AuiPaneInfo() .Left().
                            CloseButton( False ).MaximizeButton( True ).MinimizeButton( True ).
                            Dock().Resizable().FloatingSize( wx.DefaultSize ).DockFixed( False ).
                            Row( 2 ).Right().Center() )

        self.m_notebook1 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

        self.m_mgr.AddPane( self.m_notebook1, wx.aui.AuiPaneInfo() .Left() .
                            CloseButton( False ).MaximizeButton( True ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ).Left().
                            BestSize(wx.Size(300,-1)))

        self.m_scrolledWindow1 = wx.ScrolledWindow( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
        self.m_scrolledWindow1.SetScrollRate( 5, 5 )
        bSizer2 = wx.BoxSizer( wx.VERTICAL )

        sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow1, wx.ID_ANY, u"Title" ), wx.HORIZONTAL )

        self.m_textCtrl1 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, u"Title", wx.DefaultPosition, wx.Size( 135,-1 ), 0 )
        sbSizer3.Add( self.m_textCtrl1, 0, 0, 5 )

        self.m_button3 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        sbSizer3.Add( self.m_button3, 0, 0, 5 )


        bSizer2.Add( sbSizer3, 0, 0, 5 )

        sbSizer4 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow1, wx.ID_ANY, u"Xlabel" ), wx.HORIZONTAL )

        self.m_textCtrl2 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, u"xlabel", wx.DefaultPosition, wx.Size( 135,-1 ), 0 )
        sbSizer4.Add( self.m_textCtrl2, 0, 0, 5 )

        self.m_button4 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        sbSizer4.Add( self.m_button4, 0, 0, 5 )


        bSizer2.Add( sbSizer4, 0, 0, 5 )

        sbSizer5 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow1, wx.ID_ANY, u"Ylabel" ), wx.HORIZONTAL )

        self.m_textCtrl3 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, u"ylabel", wx.DefaultPosition, wx.Size( 135,-1 ), 0 )
        sbSizer5.Add( self.m_textCtrl3, 0, 0, 5 )

        self.m_button5 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        sbSizer5.Add( self.m_button5, 0, 0, 5 )


        bSizer2.Add( sbSizer5, 0, 0, 5 )

        gSizer1 = wx.GridSizer( 2, 2, 0, 0 )

        self.m_checkBox1 = wx.CheckBox( self.m_scrolledWindow1, wx.ID_ANY, u"Show Grid", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer1.Add( self.m_checkBox1, 0, wx.LEFT|wx.TOP, 5 )

        self.m_checkBox3 = wx.CheckBox( self.m_scrolledWindow1, wx.ID_ANY, u"View Cursor", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer1.Add( self.m_checkBox3, 0, wx.LEFT|wx.TOP, 5 )

        self.m_checkBox2 = wx.CheckBox( self.m_scrolledWindow1, wx.ID_ANY, u"Legend", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer1.Add( self.m_checkBox2, 0, wx.ALL, 5 )


        bSizer2.Add( gSizer1, 0, 0, 5 )

        sbSizer10 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow1, wx.ID_ANY, u"Xaxis" ), wx.HORIZONTAL )

        self.m_staticText1 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"min", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        sbSizer10.Add( self.m_staticText1, 0, wx.ALL, 5 )

        self.m_textCtrl4 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        sbSizer10.Add( self.m_textCtrl4, 0, wx.ALL, 5 )

        self.m_staticText2 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"max", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        sbSizer10.Add( self.m_staticText2, 0, wx.ALL, 5 )

        self.m_textCtrl5 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        sbSizer10.Add( self.m_textCtrl5, 0, wx.ALL, 5 )


        bSizer2.Add( sbSizer10, 0, 0, 5 )

        sbSizer11 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow1, wx.ID_ANY, u"Yaxis" ), wx.HORIZONTAL )

        self.m_staticText3 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"min", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        sbSizer11.Add( self.m_staticText3, 0, wx.ALL, 5 )

        self.m_textCtrl6 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        sbSizer11.Add( self.m_textCtrl6, 0, wx.ALL, 5 )

        self.m_staticText4 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"max", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        sbSizer11.Add( self.m_staticText4, 0, wx.ALL, 5 )

        self.m_textCtrl7 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        sbSizer11.Add( self.m_textCtrl7, 0, wx.ALL, 5 )


        bSizer2.Add( sbSizer11, 0, 0, 5 )

        sbSizer7 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow1, wx.ID_ANY, u"axis scale" ), wx.VERTICAL )

        gSizer2 = wx.GridSizer( 0, 2, 0, 0 )

        self.m_staticText5 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"X axis", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        gSizer2.Add( self.m_staticText5, 0, wx.ALL, 5 )

        self.m_staticText6 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"Y axis", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )
        gSizer2.Add( self.m_staticText6, 0, wx.ALL, 5 )

        m_choice2Choices = [ u"lin", u"log" ]
        self.m_choice2 = wx.Choice( self.m_scrolledWindow1, wx.ID_ANY, wx.DefaultPosition, wx.Size( 69,-1 ), m_choice2Choices, 0 )
        self.m_choice2.SetSelection( 0 )
        gSizer2.Add( self.m_choice2, 0, wx.LEFT|wx.RIGHT, 5 )

        m_choice1Choices = [ u"lin", u"log" ]
        self.m_choice1 = wx.Choice( self.m_scrolledWindow1, wx.ID_ANY, wx.DefaultPosition, wx.Size( 69,-1 ), m_choice1Choices, 0 )
        self.m_choice1.SetSelection( 0 )
        gSizer2.Add( self.m_choice1, 0, wx.LEFT|wx.RIGHT, 5 )


        sbSizer7.Add( gSizer2, 0, 0, 5 )


        bSizer2.Add( sbSizer7, 0, 0, 5 )


        self.m_scrolledWindow1.SetSizer( bSizer2 )
        self.m_scrolledWindow1.Layout()
        bSizer2.Fit( self.m_scrolledWindow1 )
        self.m_notebook1.AddPage( self.m_scrolledWindow1, u"Main Options", False )
        self.m_scrolledWindow3 = wx.ScrolledWindow( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
        self.m_scrolledWindow3.SetScrollRate( 5, 5 )
        bSizer21 = wx.BoxSizer( wx.VERTICAL )

        sbSizer8 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow3, wx.ID_ANY, u"Choose a line" ), wx.VERTICAL )

        m_listBox1Choices = []
        self.m_listBox1 = wx.ListBox( self.m_scrolledWindow3, wx.ID_ANY, wx.DefaultPosition, wx.Size( 130,80 ), m_listBox1Choices, 0 )
        sbSizer8.Add( self.m_listBox1, 0, wx.ALL, 5 )

        bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_button87 = wx.Button( self.m_scrolledWindow3, wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button87.SetMinSize( wx.Size( 20,-1 ) )

        bSizer5.Add( self.m_button87, 0, wx.LEFT|wx.RIGHT, 5 )

        self.m_button41 = wx.Button( self.m_scrolledWindow3, wx.ID_ANY, u"Refresh lines", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer5.Add( self.m_button41, 0, wx.ALIGN_RIGHT|wx.LEFT, 5 )


        sbSizer8.Add( bSizer5, 1, wx.EXPAND, 5 )


        bSizer21.Add( sbSizer8, 0, 0, 5 )

        sbSizer71 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow3, wx.ID_ANY, u"Some Properties" ), wx.VERTICAL )

        self.m_staticText11 = wx.StaticText( self.m_scrolledWindow3, wx.ID_ANY, u"Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText11.Wrap( -1 )
        sbSizer71.Add( self.m_staticText11, 0, wx.LEFT, 5 )

        self.m_textCtrl8 = wx.TextCtrl( self.m_scrolledWindow3, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 130,-1 ), 0 )
        self.m_textCtrl8.Enable( False )

        sbSizer71.Add( self.m_textCtrl8, 0, wx.BOTTOM|wx.LEFT|wx.TOP, 5 )

        fgSizer2 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer2.SetFlexibleDirection( wx.BOTH )
        fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        m_choice7Choices = []
        self.m_choice7 = wx.Choice( self.m_scrolledWindow3, wx.ID_ANY, wx.DefaultPosition, wx.Size( 60,-1 ), m_choice7Choices, 0 )
        self.m_choice7.SetSelection( 0 )
        fgSizer2.Add( self.m_choice7, 0, wx.ALL, 5 )

        self.m_staticText12 = wx.StaticText( self.m_scrolledWindow3, wx.ID_ANY, u"Line Width", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText12.Wrap( -1 )
        fgSizer2.Add( self.m_staticText12, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        m_choice3Choices = []
        self.m_choice3 = wx.Choice( self.m_scrolledWindow3, wx.ID_ANY, wx.DefaultPosition, wx.Size( 60,-1 ), m_choice3Choices, 0 )
        self.m_choice3.SetSelection( 0 )
        fgSizer2.Add( self.m_choice3, 0, wx.ALL, 5 )

        self.m_staticText7 = wx.StaticText( self.m_scrolledWindow3, wx.ID_ANY, u"Line Colour", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )
        fgSizer2.Add( self.m_staticText7, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        m_choice4Choices = []
        self.m_choice4 = wx.Choice( self.m_scrolledWindow3, wx.ID_ANY, wx.DefaultPosition, wx.Size( 60,-1 ), m_choice4Choices, 0 )
        self.m_choice4.SetSelection( 0 )
        fgSizer2.Add( self.m_choice4, 0, wx.ALL, 5 )

        self.m_staticText8 = wx.StaticText( self.m_scrolledWindow3, wx.ID_ANY, u"Line Style", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText8.Wrap( -1 )
        fgSizer2.Add( self.m_staticText8, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        m_choice6Choices = []
        self.m_choice6 = wx.Choice( self.m_scrolledWindow3, wx.ID_ANY, wx.DefaultPosition, wx.Size( 60,-1 ), m_choice6Choices, 0 )
        self.m_choice6.SetSelection( 0 )
        fgSizer2.Add( self.m_choice6, 0, wx.ALL, 5 )

        self.m_staticText10 = wx.StaticText( self.m_scrolledWindow3, wx.ID_ANY, u"Marker Style", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText10.Wrap( -1 )
        fgSizer2.Add( self.m_staticText10, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        m_choice8Choices = []
        self.m_choice8 = wx.Choice( self.m_scrolledWindow3, wx.ID_ANY, wx.DefaultPosition, wx.Size( 60,-1 ), m_choice8Choices, 0 )
        self.m_choice8.SetSelection( 0 )
        fgSizer2.Add( self.m_choice8, 0, wx.ALL, 5 )

        self.m_staticText13 = wx.StaticText( self.m_scrolledWindow3, wx.ID_ANY, u"Marker Size", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText13.Wrap( -1 )
        fgSizer2.Add( self.m_staticText13, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sbSizer71.Add( fgSizer2, 1, wx.EXPAND, 5 )

        self.m_checkBox4 = wx.CheckBox( self.m_scrolledWindow3, wx.ID_ANY, u" Visible", wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer71.Add( self.m_checkBox4, 0, wx.ALL, 5 )


        bSizer21.Add( sbSizer71, 0, 0, 5 )

        sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow3, wx.ID_ANY, u"Add ReferenceLine" ), wx.VERTICAL )

        fgSizer1 = wx.FlexGridSizer( 0, 3, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.HorLineTxtCtrl = wx.TextCtrl( self.m_scrolledWindow3, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), 0 )
        fgSizer1.Add( self.HorLineTxtCtrl, 0, wx.ALL, 5 )

        self.m_button51 = wx.Button( self.m_scrolledWindow3, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        fgSizer1.Add( self.m_button51, 0, wx.TOP, 5 )

        self.m_staticText131 = wx.StaticText( self.m_scrolledWindow3, wx.ID_ANY, u"Horizontal", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText131.Wrap( -1 )
        fgSizer1.Add( self.m_staticText131, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.HorVerTxtCtrl = wx.TextCtrl( self.m_scrolledWindow3, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), 0 )
        fgSizer1.Add( self.HorVerTxtCtrl, 0, wx.ALL, 5 )

        self.m_button511 = wx.Button( self.m_scrolledWindow3, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        fgSizer1.Add( self.m_button511, 0, wx.TOP, 5 )

        self.m_staticText14 = wx.StaticText( self.m_scrolledWindow3, wx.ID_ANY, u"Vertical", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText14.Wrap( -1 )
        fgSizer1.Add( self.m_staticText14, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sbSizer9.Add( fgSizer1, 1, wx.EXPAND, 5 )


        bSizer21.Add( sbSizer9, 0, 0, 5 )


        self.m_scrolledWindow3.SetSizer( bSizer21 )
        self.m_scrolledWindow3.Layout()
        bSizer21.Fit( self.m_scrolledWindow3 )
        self.m_notebook1.AddPage( self.m_scrolledWindow3, u"Lines", False )
        self.m_scrolledWindow4 = wx.ScrolledWindow( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
        self.m_scrolledWindow4.SetScrollRate( 5, 5 )
        bSizer3 = wx.BoxSizer( wx.VERTICAL )

        sbSizer15 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow4, wx.ID_ANY, u"Choose a patchs" ), wx.VERTICAL )

        patchListBoxChoices = []
        self.patchListBox = wx.ListBox( self.m_scrolledWindow4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, patchListBoxChoices, 0 )
        self.patchListBox.SetMinSize( wx.Size( 140,60 ) )

        sbSizer15.Add( self.patchListBox, 0, wx.ALL, 5 )

        fgSizer6 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer6.SetFlexibleDirection( wx.BOTH )
        fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_button9 = wx.Button( self.m_scrolledWindow4, wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, wx.BU_BOTTOM )
        self.m_button9.SetMinSize( wx.Size( 20,-1 ) )

        fgSizer6.Add( self.m_button9, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        self.m_button11 = wx.Button( self.m_scrolledWindow4, wx.ID_ANY, u"Refresh Patchs", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer6.Add( self.m_button11, 0, wx.LEFT, 5 )


        sbSizer15.Add( fgSizer6, 1, wx.EXPAND, 5 )


        bSizer3.Add( sbSizer15, 0, 0, 5 )

        sbSizer16 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow4, wx.ID_ANY, u"Some Properties" ), wx.VERTICAL )

        self.m_staticText28 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"Patch Name", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText28.Wrap( -1 )
        sbSizer16.Add( self.m_staticText28, 0, wx.ALL, 5 )

        self.textCtrlPatchName = wx.TextCtrl( self.m_scrolledWindow4, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.textCtrlPatchName.Enable( False )

        sbSizer16.Add( self.textCtrlPatchName, 0, wx.ALL, 5 )

        fgSizer7 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer7.SetFlexibleDirection( wx.BOTH )
        fgSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        m_choice13Choices = []
        self.m_choice13 = wx.Choice( self.m_scrolledWindow4, wx.ID_ANY, wx.DefaultPosition, wx.Size( 70,-1 ), m_choice13Choices, 0 )
        self.m_choice13.SetSelection( 0 )
        fgSizer7.Add( self.m_choice13, 0, wx.ALL, 5 )

        self.m_staticText29 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"Face Colour", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText29.Wrap( -1 )
        fgSizer7.Add( self.m_staticText29, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        m_choice14Choices = []
        self.m_choice14 = wx.Choice( self.m_scrolledWindow4, wx.ID_ANY, wx.DefaultPosition, wx.Size( 70,-1 ), m_choice14Choices, 0 )
        self.m_choice14.SetSelection( 0 )
        fgSizer7.Add( self.m_choice14, 0, wx.ALL, 5 )

        self.m_staticText30 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"Alpha", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText30.Wrap( -1 )
        fgSizer7.Add( self.m_staticText30, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sbSizer16.Add( fgSizer7, 1, wx.EXPAND, 5 )


        bSizer3.Add( sbSizer16, 0, 0, 5 )

        sbSizer12 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow4, wx.ID_ANY, u"add Span" ), wx.VERTICAL )

        sbSizer13 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow4, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )

        fgSizer4 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer4.SetFlexibleDirection( wx.BOTH )
        fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText15 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"Horzontal", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText15.Wrap( -1 )
        fgSizer4.Add( self.m_staticText15, 0, wx.ALL, 5 )

        self.m_button7 = wx.Button( self.m_scrolledWindow4, wx.ID_ANY, u"+", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button7.SetMinSize( wx.Size( 20,-1 ) )

        fgSizer4.Add( self.m_button7, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, 5 )


        sbSizer13.Add( fgSizer4, 0, 0, 5 )

        fgSizer3 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer3.SetFlexibleDirection( wx.BOTH )
        fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_textCtrl11 = wx.TextCtrl( self.m_scrolledWindow4, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl11.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer3.Add( self.m_textCtrl11, 0, wx.ALL, 5 )

        self.m_staticText17 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"Y axis pos 2", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText17.Wrap( -1 )
        fgSizer3.Add( self.m_staticText17, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        self.m_textCtrl12 = wx.TextCtrl( self.m_scrolledWindow4, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl12.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer3.Add( self.m_textCtrl12, 0, wx.ALL, 5 )

        self.m_staticText16 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"Y axis pos 2", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText16.Wrap( -1 )
        fgSizer3.Add( self.m_staticText16, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_choice81Choices = []
        self.m_choice81 = wx.Choice( self.m_scrolledWindow4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice81Choices, 0 )
        self.m_choice81.SetSelection( 0 )
        self.m_choice81.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer3.Add( self.m_choice81, 0, wx.ALL, 5 )

        self.m_staticText22 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"Face Colour", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText22.Wrap( -1 )
        fgSizer3.Add( self.m_staticText22, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_choice12Choices = []
        self.m_choice12 = wx.Choice( self.m_scrolledWindow4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice12Choices, 0 )
        self.m_choice12.SetSelection( 0 )
        self.m_choice12.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer3.Add( self.m_choice12, 0, wx.ALL, 5 )

        self.m_staticText26 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"Alpha", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText26.Wrap( -1 )
        fgSizer3.Add( self.m_staticText26, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )


        sbSizer13.Add( fgSizer3, 0, 0, 5 )


        sbSizer12.Add( sbSizer13, 0, 0, 5 )

        sbSizer14 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow4, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )

        fgSizer5 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer5.SetFlexibleDirection( wx.BOTH )
        fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText19 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"Vertical", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText19.Wrap( -1 )
        fgSizer5.Add( self.m_staticText19, 0, wx.ALL, 5 )

        self.m_button8 = wx.Button( self.m_scrolledWindow4, wx.ID_ANY, u"+", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button8.SetMinSize( wx.Size( 20,-1 ) )

        fgSizer5.Add( self.m_button8, 0, wx.ALIGN_CENTER_VERTICAL, 5 )


        sbSizer14.Add( fgSizer5, 0, 0, 5 )

        gSizer3 = wx.GridSizer( 0, 2, 0, 0 )

        self.m_textCtrl13 = wx.TextCtrl( self.m_scrolledWindow4, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl13.SetMinSize( wx.Size( 60,-1 ) )

        gSizer3.Add( self.m_textCtrl13, 0, wx.ALL, 5 )

        self.m_staticText20 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"X axis pos 1", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText20.Wrap( -1 )
        gSizer3.Add( self.m_staticText20, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5 )

        self.m_textCtrl14 = wx.TextCtrl( self.m_scrolledWindow4, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl14.SetMinSize( wx.Size( 60,-1 ) )

        gSizer3.Add( self.m_textCtrl14, 0, wx.ALL, 5 )

        self.m_staticText21 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"X axis pos 2", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText21.Wrap( -1 )
        gSizer3.Add( self.m_staticText21, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5 )

        m_choice10Choices = []
        self.m_choice10 = wx.Choice( self.m_scrolledWindow4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice10Choices, 0 )
        self.m_choice10.SetSelection( 0 )
        self.m_choice10.SetMinSize( wx.Size( 60,-1 ) )

        gSizer3.Add( self.m_choice10, 0, wx.ALL, 5 )

        self.m_staticText24 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"Face Colour", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText24.Wrap( -1 )
        gSizer3.Add( self.m_staticText24, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5 )

        m_choice11Choices = []
        self.m_choice11 = wx.Choice( self.m_scrolledWindow4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice11Choices, 0 )
        self.m_choice11.SetSelection( 0 )
        self.m_choice11.SetMinSize( wx.Size( 60,-1 ) )

        gSizer3.Add( self.m_choice11, 0, wx.ALL, 5 )

        self.m_staticText25 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"Alpha", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText25.Wrap( -1 )
        gSizer3.Add( self.m_staticText25, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5 )


        sbSizer14.Add( gSizer3, 0, 0, 5 )


        sbSizer12.Add( sbSizer14, 0, 0, 5 )


        bSizer3.Add( sbSizer12, 0, 0, 5 )


        self.m_scrolledWindow4.SetSizer( bSizer3 )
        self.m_scrolledWindow4.Layout()
        bSizer3.Fit( self.m_scrolledWindow4 )
        self.m_notebook1.AddPage( self.m_scrolledWindow4, u"patch", True )

        self.statusbar = self.CreateStatusBar( 2, wx.ST_SIZEGRIP, wx.ID_ANY )

        self.m_mgr.Update()
        self.Centre( wx.BOTH )

        # Connect Events
        self.m_textCtrl1.Bind( wx.EVT_TEXT, self._TitleChange )
        self.m_button3.Bind( wx.EVT_BUTTON, self._titleFontProp )
        self.m_textCtrl2.Bind( wx.EVT_TEXT, self._xlabelChange )
        self.m_button4.Bind( wx.EVT_BUTTON, self._xlabelFontProp )
        self.m_textCtrl3.Bind( wx.EVT_TEXT, self._ylabelChange )
        self.m_button5.Bind( wx.EVT_BUTTON, self._ylabelFontProp )
        self.m_checkBox1.Bind( wx.EVT_CHECKBOX, self._OnGrid )
        self.m_checkBox3.Bind( wx.EVT_CHECKBOX, self._OnViewCursor )
        self.m_checkBox2.Bind( wx.EVT_CHECKBOX, self._OnLegend )
        self.m_textCtrl4.Bind( wx.EVT_TEXT, self._xminValue )
        self.m_textCtrl5.Bind( wx.EVT_TEXT, self._xmaxValue )
        self.m_textCtrl6.Bind( wx.EVT_TEXT, self._yminValue )
        self.m_textCtrl7.Bind( wx.EVT_TEXT, self._ymaxValue )
        self.m_choice2.Bind( wx.EVT_CHOICE, self._OnXaxisScale )
        self.m_choice1.Bind( wx.EVT_CHOICE, self._OnYaxisScale )
        self.m_listBox1.Bind( wx.EVT_LISTBOX, self._OnListLinesChange )
        self.m_button87.Bind( wx.EVT_BUTTON, self._OnLineDel )
        self.m_button41.Bind( wx.EVT_BUTTON, self._OnRefreshLines )
        self.m_textCtrl8.Bind( wx.EVT_TEXT_ENTER, self._OnLineNameChange )
        self.m_choice7.Bind( wx.EVT_CHOICE, self._OnLineWidthChange )
        self.m_choice3.Bind( wx.EVT_CHOICE, self._OnLineColourChange )
        self.m_choice4.Bind( wx.EVT_CHOICE, self._OnLineStyleChange )
        self.m_choice6.Bind( wx.EVT_CHOICE, self._OnLineMarkerStyleChange )
        self.m_choice8.Bind( wx.EVT_CHOICE, self._OnLineMarkerSizeChange )
        self.m_checkBox4.Bind( wx.EVT_CHECKBOX, self._OnLineVisibleChange )
        self.HorLineTxtCtrl.Bind( wx.EVT_TEXT, self._OnTxtRefLineHorzChange )
        self.m_button51.Bind( wx.EVT_BUTTON, self._OnAddRefHorzLine )
        self.HorVerTxtCtrl.Bind( wx.EVT_TEXT, self._OnTxtRefLineVerChange )
        self.m_button511.Bind( wx.EVT_BUTTON, self._OnAddRefVertLine )
        self.patchListBox.Bind( wx.EVT_LISTBOX, self._OnPatchListboxChange )
        self.m_button9.Bind( wx.EVT_BUTTON, self._OnDelPatch )
        self.m_choice13.Bind( wx.EVT_CHOICE, self._OnPatchFaceColorChange )
        self.m_choice14.Bind( wx.EVT_CHOICE, self._OnPatchAlphaChange )
        self.m_button7.Bind( wx.EVT_BUTTON, self._OnAddHorzSpan )
        self.m_textCtrl11.Bind( wx.EVT_TEXT, self._Onm_textCtrl11Change )
        self.m_textCtrl12.Bind( wx.EVT_TEXT, self._Onm_textCtrl12Change )
        self.m_button8.Bind( wx.EVT_BUTTON, self._OnAddVerSpan )
        self.m_textCtrl13.Bind( wx.EVT_TEXT, self._Onm_textCtrl13Change )
        self.m_textCtrl14.Bind( wx.EVT_TEXT, self._Onm_textCtrl14Change )
        self.m_button11.Bind( wx.EVT_BUTTON, self._patchListboxUpdate )

        self.figpanel.canvas.mpl_connect('motion_notify_event', self._UpdateStatusBar)
        self.axes = self.figpanel.add_subplot(111)

        # Virtual event handlers, overide them in your derived class

        if typePlot == None:
            self._plotTest()
        else:
            # se ejecuta la opcion seleccionada
            if hasattr(self,typePlot):
                getattr(self,typePlot)(data2plot)
            else:
                self._plotTest()

        self.axes.set_title("Primer grafica", )
        self.axes.set_xlabel("Xlabel", )
        self.axes.set_ylabel("Ylabel", )
        self.cursor = Cursor(self.axes, useblit=True, color='blue', linewidth=1)
        self.cursor.horizOn = False
        self.cursor.vertOn = False

        # se actualiza el numero de opciones disponibles
        lineListNames= [line.get_label() for line in self.axes.get_lines()]
        self.m_listBox1.SetItems(lineListNames)
        markerStyles= [ 'None','o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd']
        faceColors= ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        lineStyles= ['_', '-', '--', ':']
        lineSizes = [str(x*0.5) for x in range(1,15,1)]
        markerSizes = [str(x) for x in range(1,15,1)]
        alpha = [str(x/float(10)) for x in range(1,11)]
        self.m_choice7.SetItems(lineSizes)
        self.m_choice3.SetItems(faceColors)
        self.m_choice4.SetItems(lineStyles)
        self.m_choice6.SetItems(markerStyles)
        self.m_choice8.SetItems(markerSizes)
        self._updateLineSelectionPane(self.m_listBox1)
        # se actualiza la informacion para la pestana de pach
        self.m_choice13.SetItems(faceColors)
        self.m_choice14.SetItems(alpha)
        self.m_choice81.SetItems(faceColors)
        self.m_choice12.SetItems(alpha)
        self.m_choice10.SetItems(faceColors)
        self.m_choice11.SetItems(alpha)

        self.m_choice13.SetSelection(0)
        self.m_choice14.SetSelection(0)
        self.m_choice81.SetSelection(0)
        self.m_choice12.SetSelection(0)
        self.m_choice10.SetSelection(0)
        self.m_choice11.SetSelection(0)

    def _Binded(self):
        pass
    def _plotTest(self):
        x = np.arange(0, 6, .01)
        y = np.sin(x**2)*np.exp(-x)
        self.axes.plot(x, y)

    def plotLine(self,data2plot):
        self.axes.hold(True)
        listLegend= list()
        listPlot = list()
        for x,y,texto in data2plot:
            listPlot.append(self.axes.plot(x,y))
            listLegend.append(texto)
        legend= self.figpanel.legend(listPlot,listLegend)
        legend.draggable(state=True)
        self.axes.hold(False)
        self.figpanel.canvas.draw()

    def plotScatter(self,data2plot):
        self.axes.hold(True)
        listLegend= list()
        listPlot = list()
        for x,y,texto in data2plot:
            listPlot.append(self.axes.plot(x,y,'.'))
            listLegend.append(texto)
        legend= self.figpanel.legend(listPlot,listLegend)
        legend.draggable(state=True)
        self.axes.hold(False)
        self.figpanel.canvas.draw()

    def plotBar(self,data2plot):
        self.axes.hold(True)
        listLegend= list()
        listPlot = list()
        for y,texto in data2plot:
            listPlot.append(self.axes.bar(range(len(y)),y))
            listLegend.append(texto)
        legend= self.figpanel.legend(listPlot,listLegend)
        legend.draggable(state=True)
        self.axes.hold(False)
        self.figpanel.canvas.draw()

    def plotBarH(self,data2plot):
        self.axes.hold(True)
        listLegend= list()
        listPlot = list()
        for y,texto in data2plot:
            listPlot.append(self.axes.barh(range(len(y)),y,align='center'))
            listLegend.append(texto)
        legend= self.figpanel.legend(listPlot,listLegend)
        legend.draggable(state=True)
        self.axes.hold(False)
        self.figpanel.canvas.draw()

    def plotLinRegress(self,data2plot):
        x = data2plot[0]
        y = data2plot[1]
        line =  linregress(x,y)
        yfit = lambda x: x*line[0]+line[1]
        plt= self.axes.plot(x,y,'b.',x,[yfit(x1) for x1 in x],'r')
        legend= self.figpanel.legend(plt,(data2plot[-1],'linRegressFit'))
        legend.draggable(state=True)
        arrow_args = dict(arrowstyle="->")
        bbox_args = dict(boxstyle="round", fc="w")
        text2anotate = "y="+str(round(line[0],4)) + \
            "x" 
        if round(line[1],4) > 0:
            text2anotate += "+" + str(round(line[1],4)) 
        elif round(line[1],4) < 0:
            text2anotate += str(round(line[1],4)) 
        text2anotate += "\n r = " + str(round(line[2],6))
        an1= self.axes.annotate(text2anotate, xy=(x[int(len(x)/2)],
                                                  yfit(x[int(len(x)/2)])),  xycoords='data',
                                              ha="center", va="center",
                                              bbox=bbox_args,
                                              arrowprops=arrow_args)
        an1.draggable()
        self.figpanel.canvas.draw()

    def plotPie(self,data2plot):
        labels = data2plot[0]#'Frogs', 'Hogs', 'Dogs', 'Logs'
        fracs = data2plot[1]#[15,30,45, 10]
        explode= data2plot[2]#(0, 0.05, 0, 0)
        plt = self.figpanel.axes[0].pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True)
        self.figpanel.canvas.draw()

    def boxPlot(self,data2plot):
        plt= self.axes.boxplot(data2plot, notch=0, sym='+', vert=1, whis=1.5,
                               positions=None, widths=None, patch_artist=False)

    def plotHistigram(self,data2plot):
        pass

    def _TitleChange( self, event ):
        self.figpanel.axes[0].set_title(event.GetString())
        self.figpanel.canvas.draw()

    def _xlabelChange( self, event ):
        self.figpanel.axes[0].set_xlabel(event.GetString())
        self.figpanel.canvas.draw()

    def _ylabelChange( self, event ):
        self.figpanel.axes[0].set_ylabel(event.GetString())
        self.figpanel.canvas.draw()

    def _OnGrid( self, event ):
        value = event.Checked()
        self.figpanel.axes[0].grid(value)
        self.figpanel.canvas.draw()

    def _OnXaxisScale( self, event ):
        value = 'linear'
        if event.Selection == 1:
            value = 'symlog'
        self.axes.set_xscale(value)
        self.figpanel.canvas.draw()

    def _OnYaxisScale( self, event ):
        value = 'linear'
        if event.Selection == 1:
            value = 'symlog'
        self.axes.set_yscale(value)
        self.figpanel.canvas.draw()

    def _OnLegend( self, event ):
        value = event.Checked()
        try:
            legend= self.figpanel.axes[0].legend()
            legend.set_visible(value)
        except:
            pass

    def _xminValue( self, event ):
        axisValue = self.figpanel.axes[0].get_xbound()
        try:
            float(event.GetString())
        except:
            return
        self.figpanel.axes[0].set_xbound((float(event.GetString()),axisValue[1]))
        self.figpanel.canvas.draw()

    def _xmaxValue( self, event ):
        axisValue = self.figpanel.axes[0].get_xbound()
        try:
            float(event.GetString())
        except:
            return
        self.figpanel.axes[0].set_xbound((axisValue[0],float(event.GetString())))
        self.figpanel.canvas.draw()

    def _yminValue( self, event ):
        axisValue = self.figpanel.axes[0].get_ybound()
        try:
            float(event.GetString())
        except:
            return
        self.figpanel.axes[0].set_ybound((float(event.GetString()),axisValue[1]))
        self.figpanel.canvas.draw()

    def _ymaxValue( self, event ):
        axisValue = self.figpanel.axes[0].get_ybound()
        try:
            float(event.GetString())
        except:
            return
        self.figpanel.axes[0].set_ybound((axisValue[0],float(event.GetString())))
        self.figpanel.canvas.draw()
    def _titleFontProp( self, event ):
        fontprop= fontDialog(self)
        currtitle = self.figpanel.axes[0].get_title()
        self.figpanel.axes[0].set_title(currtitle,fontprop)
        self.figpanel.canvas.draw()

    def _xlabelFontProp( self, event ):
        fontprop= fontDialog(self)
        currtitle = self.figpanel.axes[0].get_xlabel()
        self.figpanel.axes[0].set_xlabel(currtitle,fontprop)
        self.figpanel.canvas.draw()

    def _ylabelFontProp( self, event ):
        fontprop= fontDialog(self)
        currtitle = self.figpanel.axes[0].get_ylabel()
        self.figpanel.axes[0].set_ylabel(currtitle,fontprop)
        self.figpanel.canvas.draw()

    def _OnLineDel(self,event):
        if len(self.axes.get_lines())== 0:
            return
        selectedLine= self.figpanel.axes[0].get_lines()[self.m_listBox1.GetSelection()]
        selectedLine.remove()
        # se actualiza la linea seleccionada
        self._OnRefreshLines(None)
        self.figpanel.canvas.draw()

    def _OnViewCursor( self, event ):
        value = event.Checked()
        if not value:
            self.statusbar.SetStatusText(( ""), 1)
            #self.cursor.useblit = False
        self.cursor.horizOn = value
        self.cursor.vertOn = value
        self.figpanel.canvas.draw()

    def _UpdateStatusBar(self, event):
        if event.inaxes and self.m_checkBox3.GetValue():
            x, y = event.xdata, event.ydata
            self.statusbar.SetStatusText(( "x= " + str(x) +
                                           "  y=" +str(y) ),
                                         1)
    def _OnListLinesChange( self, event ):
        self._updateLineSelectionPane(event)

    def _updateLineSelectionPane(self,event):
        if len(self.m_listBox1.GetItems()) == 0:
            self.m_textCtrl8.SetValue("")
            return
        if self.m_listBox1.GetSelection() == 0:
            self.m_textCtrl8.SetValue("")
            return
        selectedLine= self.axes.get_lines()[self.m_listBox1.GetSelection()]
        lineName = selectedLine.get_label()
        lineWidht= float(selectedLine.get_linewidth())
        lineColour= selectedLine.get_color()
        lineStyle = selectedLine.get_linestyle()
        markerStyle= selectedLine.get_marker()
        markerSize= float(selectedLine.get_markersize())
        visible = selectedLine.get_visible()
        # pass all data an update the notebookpane
        self.m_textCtrl8.SetValue(lineName)
        for pos,value in enumerate(self.m_choice7.GetItems()):
            if float(value) == lineWidht:
                self.m_choice7.SetSelection(pos)
                break
        for pos,value in enumerate(self.m_choice3.GetItems()):
            if value == lineColour:
                self.m_choice3.SetSelection(pos)
                break
        for pos,value in enumerate(self.m_choice4.GetItems()):
            if value == lineStyle:
                self.m_choice4.SetSelection(pos)
                break
        for pos,value in enumerate(self.m_choice6.GetItems()):
            if value == markerStyle:
                self.m_choice6.SetSelection(pos)
                break
        for pos,value in enumerate(self.m_choice8.GetItems()):
            if float(value) == markerSize:
                self.m_choice8.SetSelection(pos)
                break
        self.m_checkBox4.SetValue(visible)

    def _OnLineWidthChange( self, event ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        newWidth= float(event.String)
        selectedLine= self.axes.get_lines()[self.m_listBox1.GetSelection()]
        selectedLine.set_linewidth(newWidth)
        self.figpanel.canvas.draw()

    def _OnRefreshLines( self, event ):
        if len(self.axes.get_lines())== 0:
            self.m_listBox1.SetItems([])
            return
        lineListNames= [line.get_label() for line in self.axes.get_lines()]
        self.m_listBox1.SetItems(lineListNames)
        self.m_listBox1.SetSelection(0)
        self._updateLineSelectionPane(self.m_listBox1)

    def _OnLineNameChange( self, event ):
        # pendeinte por implementar.. el evento wx.EVT_TEXT_TEXTENTER
        event.Skip()

    def _OnLineColourChange( self, event ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.axes.get_lines()[actualLineNumber]
        newcolour = event.GetString()
        lineSelected.set_color(newcolour)
        self.figpanel.canvas.draw()

    def _OnLineStyleChange( self, event ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.axes.get_lines()[actualLineNumber]
        newStyle = event.GetString()
        lineSelected.set_linestyle(newStyle)
        self.figpanel.canvas.draw()

    def _OnLineMarkerStyleChange( self, event ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.axes.get_lines()[actualLineNumber]

        newMarkerStyle = event.GetString()
        lineSelected.set_marker(newMarkerStyle)

        self.figpanel.canvas.draw()

    def _OnLineMarkerSizeChange( self, event ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.axes.get_lines()[actualLineNumber]

        newMarkerSize = float(event.GetString())
        lineSelected.set_markersize(newMarkerSize)

        self.figpanel.canvas.draw()

    def _OnLineVisibleChange( self, event ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.axes.get_lines()[actualLineNumber]
        visible = event.Checked()
        lineSelected.set_visible(visible)
        self.figpanel.canvas.draw()

    def _OnAddRefHorzLine( self, event ):
        try:
            float(self.HorLineTxtCtrl.GetValue())
        except:
            return
        self.axes.hold(True)
        ypos  = float(self.HorLineTxtCtrl.GetValue())
        self.axes.axhline(ypos)
        self.axes.hold(False)
        self.figpanel.canvas.draw()
        self.HorLineTxtCtrl.SetValue('')
        self._OnRefreshLines(None)

    def _OnAddRefVertLine( self, event ):
        try:
            float(self.HorVerTxtCtrl.GetValue())
        except:
            return
        self.axes.hold(True)
        xpos  = float(self.HorVerTxtCtrl.GetValue())
        self.axes.axvline(xpos)
        self.axes.hold(False)
        self.figpanel.canvas.draw()
        self.HorVerTxtCtrl.SetValue('')
        self._OnRefreshLines(None)

    def _OnTxtRefLineHorzChange( self, event ):
        self._txtNumerOnly( self.HorLineTxtCtrl)

    def _OnTxtRefLineVerChange( self, event ):
        self._txtNumerOnly( self.HorVerTxtCtrl)

    def _txtNumerOnly(self,refObj):
        texto = refObj.GetValue()
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
        refObj.SetValue(newstr)


    def _Onm_textCtrl11Change( self,event):
        self._txtNumerOnly( self.m_textCtrl11)

    def _Onm_textCtrl12Change( self,event):
        self._txtNumerOnly(self.m_textCtrl12)

    def _Onm_textCtrl13Change(self,event):
        self._txtNumerOnly( self.m_textCtrl13)

    def _Onm_textCtrl14Change(self, event):
        self._txtNumerOnly( self.m_textCtrl14)

    def _OnPatchListboxChange(self,event):
        if len(self.patchListBox.GetItems()) == 0:
            self.textCtrlPatchName.SetValue(u"")
            return
        if self.patchListBox.GetSelection() == -1:
            self.textCtrlPatchName.SetValue(u"")
            return
        selectedPatch= self.patchListBox.GetItems()[self.patchListBox.GetSelection()]
        currPatch= None
        for patch in self.figpanel.axes[0].patches:
            if str(patch.get_gid()) == selectedPatch:
                currPatch= patch
                break
        if currPatch == None:
            # se actualiza el patch actual
            self._patchListboxUpdate()
            return
        Alpha = str(currPatch.get_alpha())
        faceColor = currPatch.get_facecolor()
        name = str(currPatch.get_gid())
        self.textCtrlPatchName.SetValue(name)
        for pos,value in enumerate(self.m_choice14.GetItems()):
            if value == Alpha:
                self.m_choice14.SetSelection(pos)
                break
        for pos,value in enumerate(self.m_choice13.GetItems()):
            if value == faceColor:
                self.m_choice13.SetSelection(pos)
                break

    def _OnAddHorzSpan(self,event):
        pos1 = self.m_textCtrl11.GetValue()
        pos2 = self.m_textCtrl12.GetValue()
        try:
            pos1= float(pos1)
            pos2= float(pos2)
        except:
            return
        faceColor= self.m_choice81.GetItems()[self.m_choice81.GetSelection()]
        Alpha= float(self.m_choice12.GetItems()[self.m_choice12.GetSelection()])
        patch= self.figpanel.axes[0].axhspan(pos1,pos2, facecolor= faceColor, alpha= Alpha)
        patch.set_gid(wx.NewId())
        self._patchListboxUpdate()
        self.figpanel.canvas.draw()

    def _OnAddVerSpan(self,event):
        pos1 = self.m_textCtrl13.GetValue()
        pos2 = self.m_textCtrl14.GetValue()
        try:
            pos1= float(pos1)
            pos2= float(pos2)
        except:
            return
        faceColor= self.m_choice10.GetItems()[self.m_choice10.GetSelection()]
        Alpha= str(self.m_choice11.GetItems()[self.m_choice11.GetSelection()])
        patch = self.figpanel.axes[0].axvspan(pos1,pos2,facecolor= faceColor, alpha= Alpha)
        patch.set_gid(wx.NewId())
        self._patchListboxUpdate()
        self.figpanel.canvas.draw()

    def _patchListboxUpdate(self,*args):
        # se lista todos los patch
        patches = self.figpanel.axes[0].patches
        if len(patches) == 0:
            self.patchListBox.SetItems([])
        # se agrega un id para los patches que no lo tengan
        for patch in patches:
            if patch.get_gid() == None:
                patch.set_gid(wx.NewId())
        # se crea un listado con los nombres de los patches
        patches= [str(patch.get_gid()) for patch in patches]
        # se acutaliza el listado
        self.patchListBox.SetItems(patches)
        # se actualiza el frame
        if len(patches) > 0:
            self.patchListBox.SetSelection(0)
        self._OnPatchListboxChange(None)

    def _OnDelPatch(self,event):
        items = self.patchListBox.GetItems()
        if len(items) == 0:
            return
        selected = self.patchListBox.GetSelection()
        if selected == -1:
            return
        selectedPatch = items[selected]
        for patch in self.figpanel.axes[0].patches:
            if str(patch.get_gid()) == selectedPatch:
                patch.remove()
                break
        if len(items) > 0:
            self.patchListBox.SetSelection(0)
        self._patchListboxUpdate()
        self.figpanel.canvas.draw()
    def _OnPatchFaceColorChange(self,event):
        items= self.patchListBox.GetItems()
        if len(items) == 0:
            return
        selected = self.patchListBox.GetSelection()
        if  selected == -1:
            return
        selectedPatch= self.patchListBox.GetItems()[self.patchListBox.GetSelection()]
        currPatch= None
        for patch in self.figpanel.axes[0].patches:
            if str(patch.get_gid()) == selectedPatch:
                currPatch= patch
                break
        facecolor = self.m_choice13.GetItems()[self.m_choice13.GetSelection()]
        currPatch.set_facecolor(facecolor)
        self.figpanel.canvas.draw()

    def _OnPatchAlphaChange(self,event):
        items= self.patchListBox.GetItems()
        if len(items) == 0:
            return
        selected = self.patchListBox.GetSelection()
        if  selected == -1:
            return
        selectedPatch= self.patchListBox.GetItems()[self.patchListBox.GetSelection()]
        currPatch= None
        for patch in self.figpanel.axes[0].patches:
            if str(patch.get_gid()) == selectedPatch:
                currPatch= patch
                break
        alpha = self.m_choice14.GetItems()[self.m_choice14.GetSelection()]
        currPatch.set_alpha(alpha)
        self.figpanel.canvas.draw()


def fontDialog(parent):
    curClr = wx.Colour(0,0,0,0)#r,g,b,ALPHA
    fuente = wx.Font(wx.FONTSIZE_MEDIUM,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL)
    data = wx.FontData()
    data.EnableEffects(True)
    data.SetColour(curClr)         # set colour
    data.SetInitialFont(fuente)

    dlg = wx.FontDialog(parent, data)    
    if dlg.ShowModal() == wx.ID_OK:
        data = dlg.GetFontData()
        font = data.GetChosenFont()

        colour = data.GetColour()
        return {"name":   font.GetFaceName(),
                "size":   font.GetPointSize(),#  "stretch":font.stretch,
                "style":  "normal", #font.GetStyle(), #    "variant":font.variant,
                "weight": font.GetWeight(),#     "colour":  data.GetColour(),
                }

class fontmanager:
    def __init__(self):
        self.fontlist = font_manager.createFontList(font_manager.findSystemFonts())
        self._font2dict()

    def _font2dict(self):
        self.fontdict = dict()
        k = 0
        for font in self.fontlist:
            font1 = dict()
            try:
                for nombre,valor in [("fname",font.fname),
                                     ("name",font.name),
                                     ("size",font.size),
                                     ("stretch",font.stretch),
                                     ("style",font.style),
                                     ("variant",font.variant),
                                     ("weight", font.weight)]:
                    if nombre == "size":
                        if valor == 'scalable':
                            valor = 10
                    font1[nombre] = valor
            except AttributeError:
                k+= 1
                continue
            self.fontdict[k] = font1
            k+= 1



class test ( wx.Frame ):
    def __init__( self, parent):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY,
                            title='Matplotlib in Wx', pos = wx.DefaultPosition,
                            size = wx.DefaultSize,
                            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        self.figpanel= MplCanvasFrame( self )
        self.m_mgr.AddPane( self.figpanel, wx.aui.AuiPaneInfo() .Left() .
                            Caption("matplotlib embeded").
                            MaximizeButton( False ).MinimizeButton( False ).
                            PinButton( False ).PaneBorder( False ).Dock().
                            Resizable().FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).CentrePane().Row(0).Layer(0) )
        self.axes = self.figpanel.add_subplot(111)
        x = np.arange(0, 6, .01)
        y = np.sin(x**2)*np.exp(-x)
        self.axes.plot(x, y)
        self.axes.set_title("Primer grafica")
        self.axes.set_xlabel("Xlabel")
        self.axes.set_ylabel("Ylabel")

        self.m_mgr.Update()
        self.Centre(wx.BOTH)

class MplCanvasFrame(wx.Panel,Figure):
    """Class to represent a Matplotlib Figure as a wxPanel with Figure properties"""
    def __init__(self,parent, *args, **params):
        # initialize the superclass, the wx.Frame
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        Figure.__init__(self,)
        self.canvas = FigureCanvas(self, wx.ID_ANY, self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        # instantiate the Navigation Toolbar
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        # needed to support Windows systems
        self.toolbar.Realize()
        # add it to the sizer
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        # explicitly show the toolbar
        self.toolbar.Show()
        self.sizer.Add(self.canvas, 1,  wx.LEFT | wx.TOP | wx.EXPAND)

        #self.sizer.Add(self.statusbar, 1,  wx.EXPAND) # wx.LEFT | wx.TOP |

        self.SetSizer(self.sizer)
        self.Fit()

if __name__ == '__main__':
    from random import random
    # Create a wrapper wxWidgets application
    app = wx.App()
    # instantiate the Matplotlib wxFrame
    frame = MpltFrame(None,"boxPlot",[range(20),range(30),range(35),])
    # show it
    frame.Show(True)
    # start wxWidgets mainloop
    app.MainLoop()
