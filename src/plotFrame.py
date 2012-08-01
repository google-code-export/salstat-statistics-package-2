'''
Created on 11/05/2012
New plot system

@author: Sebastian lopez Buritica <Colombia>
License: GPL3
'''
# wxPython module
import wx
import wx.aui
import wx.lib.agw.aui as aui
# Matplotlib Figure object
from matplotlib.figure import Figure
from matplotlib import font_manager
from matplotlib.widgets import Cursor
# Numpy functions for image creation
import numpy as np
from statlib.stats import linregress
import matplotlib.path as mpath
import matplotlib.patches as mpatches

# import the WxAgg FigureCanvas object, that binds Figure to
# WxAgg backend. In this case, this is a wxPanel
from matplotlib.backends.backend_wxagg import \
     FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.backends.backend_wx import StatusBarWx
from matplotlib.backend_bases import MouseEvent
from triplot import triplot, triang2xy

from slbTools import homogenize
from nicePlot.graficaRibon import plotBar # nice plot

PROPLEGEND= {'size':11}

class MpltFrame( wx.Frame, object ):
    def __init__( self, parent, typePlot = None, data2plot= None, *args, **params):
        '''
        MpltFrame( parent, typePlot, data2plot)

        typePlot:
        * plotLine
        * plotScatter
        * plotBar
        * plotBarH
        * plotPie
        * plotLinRegress
        * boxPlot
        * AdaptativeBMS
        * plotHistogram <pendiente>
        * plotPareto <pendiente>

        data2plot:
        ((serie1),(serie2),..,(serieEnd))

        serie depends on the typePlot as follows:
        * plotline
        ((x1data,y1data,legend1),(x2data,y2data,legend2))
        * plotScatter
        ((x1data,y1data,legend1),(x2data,y2data,legend2))
        * plotBar
        ((x1data,legend1),(x2data,legend2),...,(xndata,legendn))
        * plotPie
        ((x1,legend1),(x2,legend2),...,(xn,legendn))
        * plotHistogram
        ((x1,),(x2,),...,(xn,))
        * plotPareto
        ((x1,x2,...,xn))
        '''
        self.log= wx.GetApp().Logg  # to write the actions
        self.graphParams= {'xlabel': '',
                     'ylabel': '',
                     'title': '',
                     'xtics': []}

        for key in self.graphParams.keys():
            try:
                self.graphParams[key] = params.pop(key)
            except KeyError:
                continue
        
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 642,465 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        self.figpanel = MplCanvasFrame( self )
        self.m_mgr.AddPane( self.figpanel, aui.AuiPaneInfo() .Left().
                            CloseButton( False ).MaximizeButton( True ).MinimizeButton( ).
                            Caption('Graph').CaptionVisible(True).
                            Dock().Resizable().FloatingSize( wx.DefaultSize ).DockFixed( True ).
                            CloseButton(False).Centre() )

        self.m_notebook1 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

        self.m_mgr.AddPane( self.m_notebook1, aui.AuiPaneInfo() .Left() .
                            CloseButton( False ).MaximizeButton( True ).
                            MinimizeButton().Dock().Resizable().
                            Caption('Graph Properties').CaptionVisible(True).
                            FloatingSize( wx.DefaultSize ).DockFixed( True ).
                            CloseButton(False). BestSize(wx.Size(200,-1)))

        self.m_scrolledWindow1 = wx.ScrolledWindow( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
        self.m_scrolledWindow1.SetScrollRate( 5, 5 )
        bSizer2 = wx.BoxSizer( wx.VERTICAL )

        sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow1, wx.ID_ANY, u"Title" ), wx.HORIZONTAL )

        self.plt_textCtr1 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, self.graphParams['title'], wx.DefaultPosition, wx.Size( 135,-1 ), 0 )
        sbSizer3.Add( self.plt_textCtr1, 0, 0, 5 )

        self.m_button3 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        sbSizer3.Add( self.m_button3, 0, 0, 5 )


        bSizer2.Add( sbSizer3, 0, 0, 5 )

        sbSizer4 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow1, wx.ID_ANY, u"Xlabel" ), wx.HORIZONTAL )

        self.plt_textCtr2 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, self.graphParams['xlabel'], wx.DefaultPosition, wx.Size( 135,-1 ), 0 )
        sbSizer4.Add( self.plt_textCtr2, 0, 0, 5 )

        self.m_button4 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        sbSizer4.Add( self.m_button4, 0, 0, 5 )


        bSizer2.Add( sbSizer4, 0, 0, 5 )

        sbSizer5 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow1, wx.ID_ANY, u"Ylabel" ), wx.HORIZONTAL )

        self.plt_textCtr3 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, self.graphParams['ylabel'], wx.DefaultPosition, wx.Size( 135,-1 ), 0 )
        sbSizer5.Add( self.plt_textCtr3, 0, 0, 5 )

        self.m_button5 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        sbSizer5.Add( self.m_button5, 0, 0, 5 )


        bSizer2.Add( sbSizer5, 0, 0, 5 )

        gSizer1 = wx.GridSizer( 2, 2, 0, 0 )

        self.m_checkBox1 = wx.CheckBox( self.m_scrolledWindow1, wx.ID_ANY, u"Show Grid", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer1.Add( self.m_checkBox1, 0, wx.LEFT|wx.TOP, 5 )

        self.m_checkBox3 = wx.CheckBox( self.m_scrolledWindow1, wx.ID_ANY, u"View Cursor", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer1.Add( self.m_checkBox3, 0, wx.LEFT|wx.TOP, 5 )

        #self.m_checkBox2 = wx.CheckBox( self.m_scrolledWindow1, wx.ID_ANY, u"Legend", wx.DefaultPosition, wx.DefaultSize, 0 )
        #gSizer1.Add( self.m_checkBox2, 0, wx.ALL, 5 )

        bSizer2.Add( gSizer1, 0, 0, 5 )

        sbSizer10 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow1, wx.ID_ANY, u"Xaxis" ), wx.HORIZONTAL )

        self.m_staticText1 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"min", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        sbSizer10.Add( self.m_staticText1, 0, wx.ALL, 5 )

        self.plt_textCtr4 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        sbSizer10.Add( self.plt_textCtr4, 0, wx.ALL, 5 )

        self.m_staticText2 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"max", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        sbSizer10.Add( self.m_staticText2, 0, wx.ALL, 5 )

        self.plt_textCtr5 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        sbSizer10.Add( self.plt_textCtr5, 0, wx.ALL, 5 )


        bSizer2.Add( sbSizer10, 0, 0, 5 )

        sbSizer11 = wx.StaticBoxSizer( wx.StaticBox( self.m_scrolledWindow1, wx.ID_ANY, u"Yaxis" ), wx.HORIZONTAL )

        self.m_staticText3 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"min", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        sbSizer11.Add( self.m_staticText3, 0, wx.ALL, 5 )

        self.plt_textCtr6 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        sbSizer11.Add( self.plt_textCtr6, 0, wx.ALL, 5 )

        self.m_staticText4 = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, u"max", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        sbSizer11.Add( self.m_staticText4, 0, wx.ALL, 5 )

        self.plt_textCtr7 = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        sbSizer11.Add( self.plt_textCtr7, 0, wx.ALL, 5 )


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
        self.m_notebook1.AddPage( self.m_scrolledWindow1, u"Main Options", True )
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

        self.plt_textCtr8 = wx.TextCtrl( self.m_scrolledWindow3, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 130,-1 ), 0 )
        self.plt_textCtr8.Enable( False )

        sbSizer71.Add( self.plt_textCtr8, 0, wx.BOTTOM|wx.LEFT|wx.TOP, 5 )

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

        self.m_button12 = wx.Button( self.m_scrolledWindow3, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 60,-1 ), 0 )
        fgSizer2.Add( self.m_button12, 0, wx.ALL, 5 )

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

        self.m_button13 = wx.Button( self.m_scrolledWindow4, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
        fgSizer7.Add( self.m_button13, 0, wx.ALL, 5 )

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

        self.plt_textCtr11 = wx.TextCtrl( self.m_scrolledWindow4, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.plt_textCtr11.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer3.Add( self.plt_textCtr11, 0, wx.ALL, 5 )

        self.m_staticText17 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"Y axis pos 2", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText17.Wrap( -1 )
        fgSizer3.Add( self.m_staticText17, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        self.plt_textCtr12 = wx.TextCtrl( self.m_scrolledWindow4, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.plt_textCtr12.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer3.Add( self.plt_textCtr12, 0, wx.ALL, 5 )

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

        self.plt_textCtr13 = wx.TextCtrl( self.m_scrolledWindow4, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.plt_textCtr13.SetMinSize( wx.Size( 60,-1 ) )

        gSizer3.Add( self.plt_textCtr13, 0, wx.ALL, 5 )

        self.m_staticText20 = wx.StaticText( self.m_scrolledWindow4, wx.ID_ANY, u"X axis pos 1", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText20.Wrap( -1 )
        gSizer3.Add( self.m_staticText20, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5 )

        self.plt_textCtr14 = wx.TextCtrl( self.m_scrolledWindow4, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.plt_textCtr14.SetMinSize( wx.Size( 60,-1 ) )

        gSizer3.Add( self.plt_textCtr14, 0, wx.ALL, 5 )

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
        self.m_notebook1.AddPage( self.m_scrolledWindow4, u"patch", False )

        self.statusbar = self.CreateStatusBar( 2, wx.ST_SIZEGRIP, wx.ID_ANY )

        self.m_mgr.Update()
        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_ACTIVATE, self.OnActivate )
        self.plt_textCtr1.Bind( wx.EVT_TEXT, self._TitleChange )
        self.plt_textCtr2.Bind( wx.EVT_TEXT, self._xlabelChange )
        self.plt_textCtr3.Bind( wx.EVT_TEXT, self._ylabelChange )        
        
        self.m_button3.Bind( wx.EVT_BUTTON, self._titleFontProp )
        self.m_button4.Bind( wx.EVT_BUTTON, self._xlabelFontProp )        
        self.m_button5.Bind( wx.EVT_BUTTON, self._ylabelFontProp )
        self.m_checkBox1.Bind( wx.EVT_CHECKBOX, self._OnGrid )
        self.m_checkBox3.Bind( wx.EVT_CHECKBOX, self._OnViewCursor )
        ##self.m_checkBox2.Bind( wx.EVT_CHECKBOX, self._OnLegend )# leggend callback
        self.plt_textCtr4.Bind( wx.EVT_TEXT, self._xminValue )
        self.plt_textCtr5.Bind( wx.EVT_TEXT, self._xmaxValue )
        self.plt_textCtr6.Bind( wx.EVT_TEXT, self._yminValue )
        self.plt_textCtr7.Bind( wx.EVT_TEXT, self._ymaxValue )
        self.m_choice2.Bind( wx.EVT_CHOICE, self._OnXaxisScale )
        self.m_choice1.Bind( wx.EVT_CHOICE, self._OnYaxisScale )
        self.m_listBox1.Bind( wx.EVT_LISTBOX, self._OnListLinesChange )
        self.m_button87.Bind( wx.EVT_BUTTON, self._OnLineDel )
        self.m_button41.Bind( wx.EVT_BUTTON, self._OnRefreshLines )
        self.plt_textCtr8.Bind( wx.EVT_TEXT_ENTER, self._OnLineNameChange )
        self.m_choice7.Bind( wx.EVT_CHOICE, self._OnLineWidthChange )
        self.m_button12.Bind( wx.EVT_BUTTON, self._OnLineColourChange )
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
        self.m_button13.Bind( wx.EVT_BUTTON, self._OnPatchFaceColorChange )
        self.m_choice14.Bind( wx.EVT_CHOICE, self._OnPatchAlphaChange )
        self.m_button7.Bind( wx.EVT_BUTTON, self._OnAddHorzSpan )
        self.plt_textCtr11.Bind( wx.EVT_TEXT, self._Onm_textCtrl11Change )
        self.plt_textCtr12.Bind( wx.EVT_TEXT, self._Onm_textCtrl12Change )
        self.m_button8.Bind( wx.EVT_BUTTON, self._OnAddVerSpan )
        self.plt_textCtr13.Bind( wx.EVT_TEXT, self._Onm_textCtrl13Change )
        self.plt_textCtr14.Bind( wx.EVT_TEXT, self._Onm_textCtrl14Change )
        self.m_button11.Bind( wx.EVT_BUTTON, self._patchListboxUpdate )

        self.figpanel.canvas.mpl_connect('motion_notify_event', self._UpdateStatusBar)
        ###
        ###
        
        if typePlot == None:
            self._plotTest()
        else:
            # se ejecuta la opcion seleccionada
            if hasattr(self, typePlot):
                getattr(self, typePlot)( data2plot, *args, **params)
            else:
                self._plotTest()
        self._addLabels(self.graphParams)
        #
        # se actualiza el nombre de las escalas de las x
        if self.graphParams.has_key( 'xtics'):
            xtics = self.graphParams['xtics']
            if len(xtics) != 0:
                self.gca().set_xticklabels( self.graphParams['xtics'])
        if self.graphParams.has_key( 'ytics'):
            self.gca().set_yticklabels( self.graphParams['ytics'])
        # connect cursos with a selected axes
        # self._connectCursor(self.gca())
        # se actualiza las lineas del axes actual
        lineListNames= [line.get_label() for line in self.gca().get_lines()]
        self.m_listBox1.SetItems( lineListNames)
        #
        ###
        ###
        
        markerStyles= [ 'None', 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd']
        faceColors=   ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        lineStyles=   ['_', '-', '--', ':']
        lineSizes=    [str(x*0.5) for x in range(1,15,1)]
        markerSizes=  [str(x) for x in range(1,15,1)]
        alpha=        [str(x/float(10)) for x in range(1,11)]
        self.m_choice7.SetItems(lineSizes)
        self.m_choice4.SetItems(lineStyles)
        self.m_choice6.SetItems(markerStyles)
        self.m_choice8.SetItems(markerSizes)
        self._updateLineSelectionPane(self.m_listBox1)
        # se actualiza la informacion para la pestana de pach
        self.m_choice14.SetItems(alpha)
        self.m_choice81.SetItems(faceColors)
        self.m_choice12.SetItems(alpha)
        self.m_choice10.SetItems(faceColors)
        self.m_choice11.SetItems(alpha)
        self.m_choice14.SetSelection(0)
        self.m_choice81.SetSelection(0)
        self.m_choice12.SetSelection(0)
        self.m_choice10.SetSelection(0)
        self.m_choice11.SetSelection(0)
           
    def OnActivate(self, evt):
        # read the actual axes
        if hasattr(self, 'axes'):
            if len(self.axes) == 0:
                # clear the title, x and ylabel contents
                self._cleartitles()
            else:
                # update the title, x and ylabel contents
                self.plt_textCtr2.Value= self.gca().get_xlabel()
                # clear ylabel ctrl
                self.plt_textCtr3.Value= self.gca().get_ylabel()
                # clear title
                self.plt_textCtr1.Value= self.gca().get_title()
                # connect the cursor to current axes
                self._connectCursor(self.gca()) 
        
    def _clearTitles(self, evt):
        # clear xlabel ctrl
        self.plt_textCtr2.Value= u''
        # clear ylabel ctrl
        self.plt_textCtr3.Value= u''
        # clear title
        self.plt_textCtr1.Value= u''
        
    
    def _connectCursor(self, axes):
        # connect the cursor to the axes selected
        self.cursor= Cursor( axes, useblit = True, color = 'blue', linewidth = 1)
        self.cursor.horizOn= False
        self.cursor.vertOn=  False
        
        
    def __getattribute__(self, name):
        '''wraps the funtions to the grid
        emulating a plot frame control'''
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self.figpanel.__getattribute__(name)
        
    def _addLabels( self,labels):
        self.figpanel.gca().set_title(labels['title'])
        self.figpanel.gca().set_xlabel(labels['xlabel'])
        self.figpanel.gca().set_ylabel(labels['ylabel'])
        self.figpanel.canvas.draw()

    def _plotTest( self):
        x = np.arange(0, 6, .01)
        y = np.sin(x**2)*np.exp(-x)
        self.gca().plot(x, y)

    def plotLine( self,data2plot):
        self.gca().hold(True)
        listLegend= list()
        listPlot = list()
        for x,y,texto in data2plot:
            listPlot.append(self.gca().plot(x,y))
            listLegend.append(texto)
        legend= self.figpanel.legend(listPlot,listLegend)
        legend.draggable(state=True)
        self.gca().hold(False)
        self.figpanel.canvas.draw()

    def plotScatter( self,data2plot):
        self.gca().hold(True)
        listLegend= list()
        listPlot = list()
        for x,y,texto in data2plot:
            # se homogeniza la informacion
            (x, y) = homogenize( x, y)
            listPlot.append( self.gca().plot( x, y, '.'))
            listLegend.append( texto)
        legend= self.figpanel.legend( listPlot, listLegend, prop = PROPLEGEND)
        legend.draggable( state= True)
        self.gca().hold( False)
        self.figpanel.canvas.draw()

    def plotBar( self,data2plot):
        DeprecationWarning( 'Deprecated function')
        # warnings.warn( 'Deprecated function', DeprecationWarning)
        self.gca().hold(True)
        listLegend= list()
        listPlot = list()
        for y,texto in data2plot:
            listPlot.append(self.gca().bar(range(len(y)),y))
            listLegend.append(texto)
        legend= self.figpanel.legend(listPlot,listLegend, prop = PROPLEGEND)
        legend.draggable( state = True)
        self.gca().hold( False)
        self.figpanel.canvas.draw()
        
    def plotNiceBar( self, data2plot):
        xdat=  data2plot[0]
        ydat=  data2plot[1]
        label= data2plot[2]
        colour= data2plot[3]
        figNam= data2plot[4]
        self.gca().hold( True)
        #try:
        plotBar(ax=      self.gca(),
                xdata=   xdat,
                ydata=   ydat,
                labels=  None,
                colors=  colour,
                figName= figNam)
        #except:
        #    data2plot= (ydat,'Media')
        #plotBar(data2plot)
        self.gca().hold( False)
        self.figpanel.canvas.draw( )

    def plotBarH( self,data2plot):
        self.gca().hold(True)
        listLegend= list()
        listPlot = list()
        for y,texto in data2plot:
            listPlot.append(self.gca().barh(range(len(y)),y,align='center'))
            listLegend.append(texto)
        legend= self.figpanel.legend(listPlot,listLegend,  prop = PROPLEGEND)
        legend.draggable(state=True)
        self.gca().hold(False)
        self.figpanel.canvas.draw()

    def plotLinRegress( self,data2plot):
        x = data2plot[0]
        y = data2plot[1]
        line =  linregress(x,y)
        yfit = lambda x: x*line[0]+line[1]
        plt= self.gca().plot(x,y,'b.',x,[yfit(x1) for x1 in x],'r')
        legend= self.figpanel.legend(plt,(data2plot[-1],'linRegressFit'), prop = PROPLEGEND)
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
        an1= self.gca().annotate(text2anotate, xy=(x[int(len(x)/2)],
                                                  yfit(x[int(len(x)/2)])),  xycoords='data',
                                              ha="center", va="center",
                                              bbox=bbox_args,
                                              arrowprops=arrow_args)
        an1.draggable()
        self.figpanel.canvas.draw()

    def plotPie( self, data2plot):
        labels = data2plot[0]#'Frogs', 'Hogs', 'Dogs', 'Logs'
        fracs = data2plot[1]#[15,30,45, 10]
        explode= data2plot[2]#(0, 0.05, 0, 0)
        plt = self.figpanel.gca().pie( fracs, explode=explode,
                                         labels=labels,
                                         autopct='%1.1f%%',
                                         shadow=True)
        self.figpanel.canvas.draw()

    def boxPlot(self,data2plot):
        plt= self.gca().boxplot(data2plot, notch=0, sym='+', vert=1, whis=1.5,
                               positions=None, widths=None, patch_artist=False)
        self.figpanel.canvas.draw()

    def plotHistogram(self,data2plot):
        pass
    def plotTrian(self,data2plot):
        '''data2plot = ((a,b,c,'legend'))'''
        legends= data2plot[1]
        data2plot= data2plot[0]
        plotT = triplot(data2plot,)
        # plot the mesh
        ax= self.figpanel.gca()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim((-0.08, 1.08))
        ax.set_ylim((-0.08, 0.97))
        ax.set_axis_off()
        
        ax.hold(True)
        #<p> plot the grid
        a= plotT.meshLines[-1]
        plotT.meshLines[-1] = [a[0][:4],a[1][:4]]
        for pos,lineGrid in enumerate(plotT.meshLines):
            if pos == 0:
                ax.plot(lineGrid[0],lineGrid[1], 
                    color= wx.Colour(0, 0, 0, 0.5),
                    linestyle= '-',)
            else:
                ax.plot(lineGrid[0],lineGrid[1], 
                    color= wx.Colour(0, 0, 0, 0.5),
                    linestyle= '--',)
        #plot the grid /<p>
        
        #<p> generating a background patch
        # changing triangular coordinates to xy coordinates
        cord1= triang2xy(1,0,0)
        cord2= triang2xy(0,1,0)
        cord3= triang2xy(0,0,1)
        Path = mpath.Path
        pathdata = [(Path.MOVETO, cord1),
                    (Path.LINETO, cord2),
                    (Path.LINETO, cord3),
                    (Path.CLOSEPOLY, cord1),
                    ]
        codes, verts = zip(*pathdata)
        path = mpath.Path(verts, codes)
        patch = mpatches.PathPatch(path, facecolor='white', edgecolor='black', alpha=0.5)
        ax.add_patch(patch)
        #/<p>
        
        # <p> adding Corner labels
        cordLeft=  (-0.06, -0.03)
        cordRigth= ( 1.06, -0.03)
        cordUpper= ( 0.5, 0.94)
        stylename= 'round'
        fontsize= 13
        an1=ax.text( cordLeft[0], cordLeft[1], legends[0],
                 ha= "right",
                 va= 'top',
                 size= fontsize, #                 transform= ax.figure.transFigure,
                 bbox=dict(boxstyle=stylename, fc="w", ec="k")) #              bbox=dict(boxstyle=stylename, fc="w", ec="k")
        
        an2=ax.text( cordRigth[0], cordRigth[1],  legends[1],
                 ha= "left",
                 va= 'top',
                 size= fontsize,#                 transform= ax.figure.transFigure,
                 bbox=dict(boxstyle=stylename, fc="w", ec="k"))
        
        an3=ax.text( cordUpper[0], cordUpper[1],  legends[2],
                 ha= "center",
                 va= 'baseline',
                 size= fontsize, #                 transform= ax.figure.transFigure,
                 bbox=dict(boxstyle=stylename, fc="w", ec="k"))
        # adding coordinates  /<p>
        
        #<p> add a ruler
        for line in plotT.ruler:
            ax.plot(line[0],line[1], 
                    color= wx.Colour(0, 0, 0, 0),
                    linestyle= '-',)
        # numbering the ruler
        for key, values in plotT.dataLabel.items():
            if key == 'AC':
                for ((x,y), value) in zip(values, range(10,-1,-1)):
                    value = value/float(10)
                    ax.text(x, y, str(value),
                        horizontalalignment= 'right',
                        verticalalignment=   'bottom',
                        fontsize=            10)
                        #transform=           ax.transAxes)
            if key == 'CB':
                for ((x,y), value) in zip(values, range(10,-1,-1)):
                    value = value/float(10)
                    ax.text(x, y, str(value),
                        horizontalalignment= 'left',
                        verticalalignment=   'bottom',
                        fontsize=            10)
            if key == 'AB':
                for ((x,y), value) in zip(values, range(10,-1,-1)):
                    value = value/float(10)
                    ax.text(x, y, str(value),
                        horizontalalignment= 'center',
                        verticalalignment=   'top',
                        fontsize=            10)
        # add the ruler /<p>
        
        listPlot = list()
        for data in plotT.xydata:
            listPlot.append( ax.plot( data[0],data[1],
                                linestyle= '_', marker='d'))
            
        listLegend= [dat[3] for dat in data2plot]
        legend= self.figpanel.legend( listPlot, listLegend, prop = PROPLEGEND)
        legend.draggable( state= True)
        ax.hold(False)
        self.figpanel.canvas.draw(0)
        
    def AdaptativeBMS(self, data, xlabel='', ylabel='', title=''):
        self.figpanel.gca().hold(True)
        for serieNumber, serieData in enumerate(data): 
            xmin= serieNumber-0.4
            xmax= serieNumber+0.4
            size= len(serieData)
            if size == 0: continue
            step= 0.8/float(size)
            xdata= [ -0.4 + serieNumber + i*step for i in range(size)]
            self.gca().plot(xdata, serieData, marker= '.', linestyle= '_')
        self.gca().set_xticks(range(len(data)))
        self.figpanel.gca().set_title(title)
        self.figpanel.gca().set_xlabel(xlabel)
        self.figpanel.gca().set_ylabel(ylabel)
        self.figpanel.gca().hold(False)
        self.figpanel.canvas.draw()
        
    def _TitleChange( self, evt ):
        #self.log.write('# Changing Title', False)
        self.figpanel.gca().set_title(evt.GetString())
        self.figpanel.canvas.draw()
        
        #self.log.write('Title= ' + "'" + self.figpanel.gca().get_title().__str__()+ "'", False)
        #self.log.write('plt.gca().set_title(Title)', False)
                
    def probabilityPlot(self, data2plot):
        import scipy.stats as stats2
        from numpy import amin, amax
        if not isinstance(data2plot[0],(np.ndarray,)):
            data2plot[0]= np.array(data2plot[0])
        res=   stats2.probplot(data2plot[0],)
        (osm,osr)=  res[0]
        (slope, intercept, r)= res[1]
        ax= self.figpanel.gca()
        ax.plot(osm, osr, 'o', osm, slope*osm + intercept)
        xmin, xmax= amin(osm),amax(osm)
        ymin, ymax= amin(data2plot),amax(data2plot)
        posx, posy= xmin+0.70*(xmax-xmin), ymin+0.01*(ymax-ymin)
        ax.text(posx,posy, "r^2=%1.4f" % r)
        self.figpanel.canvas.draw()
        
    def controlChart(self, data2plot):
        UCL= data2plot['UCL']
        LCL= data2plot['LCL']
        target= data2plot['target']
        data= data2plot['data']
        posDataOutSide= list()
        # plot all data
        self.gca().plot(range(len(data)),data,marker= 'o')
        self.gca().hold(True)
        for pos, value in enumerate(data):
            if value > UCL or value < LCL:
                posDataOutSide.append((pos,value))
        # then plot the violating points
        self.gca().plot([dat[0] for dat in posDataOutSide],
                       [dat[1] for dat in posDataOutSide],
                       linestyle= '_', color='r', marker='d')
        # UCL, LCL  Lines
        self._OnAddRefHorzLine( evt= None, ypos= UCL, color= 'r')
        self._OnAddRefHorzLine( evt= None, ypos= LCL, color= 'r')
        # Target Line
        self._OnAddRefHorzLine( evt= None, ypos= target, color= 'k')
        self.gca().hold(False)
        self.figpanel.canvas.draw()

    def _xlabelChange( self, evt ):
        #self.log.write('# changing xlabel', False)
        self.figpanel.gca().set_xlabel(evt.GetString())
        self.figpanel.canvas.draw()
        #self.log.write('xlabel= ' + "'" +  self.figpanel.gca().get_xlabel().__str__()+ "'" , False)
        #self.log.write('plt.gca().set_xlabel(xlabel)', False)

    def _ylabelChange( self, evt ):
        #self.log.write('# changing ylabel', False)
        self.figpanel.gca().set_ylabel(evt.GetString())
        self.figpanel.canvas.draw()
        #self.log.write('ylabel= ' + "'" + self.figpanel.gca().get_ylabel().__str__()+ "'" , False)
        #self.log.write('plt.gca().set_xlabel(ylabel)', False)

    def _OnGrid( self, evt ):
        self.log.write('# changing grid state', False)
        value = evt.Checked()
        self.figpanel.gca().grid(value)
        self.figpanel.canvas.draw()
        self.log.write('plt.gca().grid('+value.__str__()+')', False)
 

    def _OnXaxisScale( self, evt ):
        self.log.write('# changing x axis scale', False)
        value = 'linear'
        if evt.Selection == 1:
            value = 'symlog'
        self.gca().set_xscale(value)
        self.figpanel.canvas.draw()
        self.log.write('plt.gca().set_xscale('+ "'" + value.__str__()+ "'" +')', False)


    def _OnYaxisScale( self, evt ):
        self.log.write('# changing y axis scale', False)
        value = 'linear'
        if evt.Selection == 1:
            value = 'symlog'
        self.gca().set_yscale(value)
        self.figpanel.canvas.draw()
        self.log.write('plt.gca().set_yscale('+ "'" + value.__str__()+ "'" +')', False)


    def _OnLegend( self, evt ):
        value = evt.Checked()
        try:
            legend= self.figpanel.gca().legend()
            legend.set_visible(value)
        except:
            pass

    def _xminValue( self, evt ):
        self.log.write('# changing x axis min value', False)
        axisValue= self.figpanel.gca().get_xbound()
        self.log.write('axisValue= plt.gca().get_xbound()', False)
        try:
            float(evt.GetString())
        except:
            return
        self.figpanel.gca().set_xbound((float(evt.GetString()),axisValue[1]))
        self.figpanel.canvas.draw()
        self.log.write('plt.gca().set_xbound((float('+evt.GetString().__str__()+'),axisValue[1]))', False)


    def _xmaxValue( self, evt ):
        self.log.write('# changing x axis max value', False)
        axisValue = self.figpanel.gca().get_xbound()
        self.log.write('axisValue= plt.gca().get_xbound()', False)
        try:
            float(evt.GetString())
        except:
            return
        self.figpanel.gca().set_xbound((axisValue[0],float(evt.GetString())))
        self.figpanel.canvas.draw()
        self.log.write('plt.gca().set_xbound((axisValue[0],float('+evt.GetString().__str__()+')))', False)

    def _yminValue( self, evt ):
        self.log.write('# changing y axis min value', False)
        axisValue = self.figpanel.gca().get_ybound()
        self.log.write('axisValue= plt.gca().get_ybound()', False)
        
        try:
            float(evt.GetString())
        except:
            return
        self.figpanel.gca().set_ybound((float(evt.GetString()),axisValue[1]))
        self.figpanel.canvas.draw()
        self.log.write('plt.gca().set_ybound((float('+evt.GetString().__str__()+'),axisValue[1]))', False)

        
    def _ymaxValue( self, evt ):
        self.log.write('# changing y axis max value', False)
        axisValue = self.figpanel.gca().get_ybound()
        self.log.write('axisValue= plt.gca().get_ybound()', False)
        try:
            float(evt.GetString())
        except:
            return
        self.figpanel.gca().set_ybound((axisValue[0],float(evt.GetString())))
        self.figpanel.canvas.draw()
        self.log.write('plt.gca().set_ybound((axisValue[0],float('+evt.GetString().__str__()+')))', False)

        
    def _titleFontProp( self, evt ):
        fontprop= fontDialog(self)
        currtitle = self.figpanel.gca().get_title()
        self.figpanel.gca().set_title(currtitle,fontprop)
        self.figpanel.canvas.draw()

    def _xlabelFontProp( self, evt ):
        fontprop= fontDialog(self)
        currtitle = self.figpanel.gca().get_xlabel()
        self.figpanel.gca().set_xlabel(currtitle,fontprop)
        self.figpanel.canvas.draw()

    def _ylabelFontProp( self, evt ):
        fontprop= fontDialog(self)
        currtitle = self.figpanel.gca().get_ylabel()
        self.figpanel.gca().set_ylabel(currtitle,fontprop)
        self.figpanel.canvas.draw()

    def _OnLineDel(self,event):
        if len(self.gca().get_lines())== 0:
            return
        selectedLine= self.figpanel.gca().get_lines()[self.m_listBox1.GetSelection()]
        selectedLine.remove()
        # se actualiza la linea seleccionada
        self._OnRefreshLines(None)
        self.figpanel.canvas.draw()

    def _OnViewCursor( self, evt ):
        # verify the cursor property created with
        # connectCursor
        if not hasattr(self,'cursor'):
            return
        value = evt.Checked()
        if not value:
            self.statusbar.SetStatusText(( ""), 1)
        
        self.cursor.horizOn = value
        self.cursor.vertOn = value
        self.figpanel.canvas.draw()

    def _UpdateStatusBar(self, evt):
        if evt.inaxes and self.m_checkBox3.GetValue():
            x, y = evt.xdata, evt.ydata
            self.statusbar.SetStatusText(( "x= " + str(x) +
                                           "  y=" +str(y) ),
                                         1)
    def _OnListLinesChange( self, evt ):
        self._updateLineSelectionPane(evt)

    def _updateLineSelectionPane(self,evt):
        if len(self.m_listBox1.GetItems()) == 0:
            self.plt_textCtr8.SetValue("")
            return
        if self.m_listBox1.GetSelection() == -1:
            self.plt_textCtr8.SetValue("")
            return
        selectedLine= self.gca().get_lines()[self.m_listBox1.GetSelection()]
        lineName = selectedLine.get_label()
        lineWidht= float(selectedLine.get_linewidth())
        lineColour= selectedLine.get_color()
        lineStyle = selectedLine.get_linestyle()
        markerStyle= selectedLine.get_marker()
        markerSize= float(selectedLine.get_markersize())
        visible = selectedLine.get_visible()
        # pass all data an update the notebookpane
        self.plt_textCtr8.SetValue(lineName)
        for pos,value in enumerate(self.m_choice7.GetItems()):
            if float(value) == lineWidht:
                self.m_choice7.SetSelection(pos)
                break
        #for pos,value in enumerate(self.m_choice3.GetItems()):
            #if value == lineColour:
                #self.m_choice3.SetSelection(pos)
                #break
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

    def _OnLineWidthChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        newWidth= float(evt.String)
        selectedLine= self.gca().get_lines()[self.m_listBox1.GetSelection()]
        selectedLine.set_linewidth(newWidth)
        self.figpanel.canvas.draw()

    def _OnRefreshLines( self, evt ):
        if len(self.gca().get_lines())== 0:
            self.m_listBox1.SetItems([])
            return
        lineListNames= [line.get_label() for line in self.gca().get_lines()]
        self.m_listBox1.SetItems(lineListNames)
        self.m_listBox1.SetSelection(0)
        self._updateLineSelectionPane(self.m_listBox1)

    def _OnLineNameChange( self, evt ):
        # pendeinte por implementar.. el evento wx.EVT_TEXT_TEXTENTER
        evt.Skip()

    def _OnLineColourChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            # If the user selected OK, then the dialog's wx.ColourData will
            # contain valid information. Fetch the data ...
            data = dlg.GetColourData()
        else:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.gca().get_lines()[actualLineNumber]
        colors = [getattr(data.Colour,param)/float(255) for param in ['red','green','blue','alpha']]
        lineSelected.set_color(colors)
        self.figpanel.canvas.draw()

    def _OnLineStyleChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.gca().get_lines()[actualLineNumber]
        newStyle = evt.GetString()
        lineSelected.set_linestyle(newStyle)
        self.figpanel.canvas.draw()

    def _OnLineMarkerStyleChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.gca().get_lines()[actualLineNumber]

        newMarkerStyle = evt.GetString()
        lineSelected.set_marker(newMarkerStyle)

        self.figpanel.canvas.draw()

    def _OnLineMarkerSizeChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.gca().get_lines()[actualLineNumber]

        newMarkerSize = float(evt.GetString())
        lineSelected.set_markersize(newMarkerSize)

        self.figpanel.canvas.draw()

    def _OnLineVisibleChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.gca().get_lines()[actualLineNumber]
        visible = evt.Checked()
        lineSelected.set_visible(visible)
        self.figpanel.canvas.draw()

    def _OnAddRefHorzLine( self, evt, **params ):
        self.log.write('# adding reference horizontal line', False)
        if params.has_key('ypos'):
            ypos = params.pop('ypos')
            self.gca().hold(True)
            #self.log.write('plt.gca().hold(True)', False)
            
            line= self.gca().axhline(ypos)
            self.log.write('line= pltgca().axhline('+ypos.__str__()+')', False)
            self.gca().hold(False)
            #self.log.write('plt.gca().hold(False)', False)
        else:
            try:
                ypos= float(self.HorLineTxtCtrl.GetValue())
                self.gca().hold(True)
                self.log.write('plt.gca().hold(True)', False)
                line= self.gca().axhline(ypos)
                self.log.write('plt.gca().axhline('+ypos.__str__()+')', False)
                self.gca().hold(False)
                self.log.write('plt.gca().hold(False)', False)
                self.HorLineTxtCtrl.SetValue('')
                self._OnRefreshLines(None)
            except:
                return
        if params.has_key('color'):
            line.set_color(params['color'])
            self.log.write('line.set_color('+"'"+params['color'].__str__()+"'"+')', False)
        self.figpanel.canvas.draw()
        #self.log.write('plt.draw()',False)
        
    def _OnAddRefVertLine( self, evt ):
        self.log.write('# adding reference vertical line', False)
        try:
            float(self.HorVerTxtCtrl.GetValue())
        except:
            return
        self.gca().hold(True)
        self.log.write('plt.gca().hold(True)', False)
        
        xpos= float(self.HorVerTxtCtrl.GetValue())
        self.gca().axvline(xpos)
        self.log.write('plt.gca().axvline('+xpos.__str__()+')', False)
        self.gca().hold(False)
        self.log.write('plt.gca().hold(False)', False)
        self.figpanel.canvas.draw()
        self.HorVerTxtCtrl.SetValue('')
        self._OnRefreshLines(None)
        self.figpanel.canvas.draw()
        #self.log.write('plt.draw()',False)

    def _OnTxtRefLineHorzChange( self, evt ):
        self._txtNumerOnly( self.HorLineTxtCtrl)

    def _OnTxtRefLineVerChange( self, evt ):
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
        self._txtNumerOnly( self.plt_textCtr11)

    def _Onm_textCtrl12Change( self,event):
        self._txtNumerOnly(self.plt_textCtr12)

    def _Onm_textCtrl13Change(self,event):
        self._txtNumerOnly( self.plt_textCtr13)

    def _Onm_textCtrl14Change(self, evt):
        self._txtNumerOnly( self.plt_textCtr14)

    def _OnPatchListboxChange(self,event):
        if len(self.patchListBox.GetItems()) == 0:
            self.textCtrlPatchName.SetValue(u"")
            return
        if self.patchListBox.GetSelection() == -1:
            self.textCtrlPatchName.SetValue(u"")
            return
        selectedPatch= self.patchListBox.GetItems()[self.patchListBox.GetSelection()]
        currPatch= None
        for patch in self.figpanel.gca().patches:
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
        #for pos,value in enumerate(self.m_choice13.GetItems()):
            #if value == faceColor:
                #self.m_choice13.SetSelection(pos)
                #break

    def _OnAddHorzSpan(self,event):
        self.log.write('# adding horizontal span', False)
        pos1 = self.plt_textCtr11.GetValue()
        pos2 = self.plt_textCtr12.GetValue()
        try:
            pos1= float(pos1)
            pos2= float(pos2)
        except:
            return
        self.log.write('pos1= ' + pos1.__str__(), False)
        self.log.write('pos2= ' + pos2.__str__(), False)
        
        faceColor= self.m_choice81.GetItems()[self.m_choice81.GetSelection()]
        self.log.write('faceColor= '+"'"+faceColor.__str__()+"'", False)
        
        Alpha= float(self.m_choice12.GetItems()[self.m_choice12.GetSelection()])
        self.log.write('Alpha= '+Alpha.__str__(), False)
        
        patch= self.figpanel.gca().axhspan(pos1,pos2, facecolor= faceColor, alpha= Alpha)
        self.log.write('patch= plt.gca().axhspan(pos1,pos2, facecolor= faceColor, alpha= Alpha)', False)
        patch.set_gid(wx.NewId())
        self._patchListboxUpdate()
        self.figpanel.canvas.draw()

    def _OnAddVerSpan(self,event):
        self.log.write('# adding vertical span', False)
        pos1 = self.plt_textCtr13.GetValue()
        pos2 = self.plt_textCtr14.GetValue()
        try:
            pos1= float(pos1)
            pos2= float(pos2)
        except:
            return
        self.log.write('pos1= ' + pos1.__str__(), False)
        self.log.write('pos2= ' + pos2.__str__(), False)
        
        faceColor= self.m_choice10.GetItems()[self.m_choice10.GetSelection()]
        self.log.write('faceColor= '+"'"+faceColor.__str__()+"'", False)
        
        Alpha= str(self.m_choice11.GetItems()[self.m_choice11.GetSelection()])
        self.log.write('Alpha= '+Alpha.__str__(), False)
        
        patch= self.figpanel.gca().axvspan(pos1,pos2,facecolor= faceColor, alpha= Alpha)
        self.log.write('patch= plt.gca().axvspan(pos1,pos2,facecolor= faceColor, alpha= Alpha)', False)
        patch.set_gid(wx.NewId())
        self._patchListboxUpdate()
        self.figpanel.canvas.draw()

    def _patchListboxUpdate(self,*args):
        # se lista todos los patch
        patches = self.figpanel.gca().patches
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
        for patch in self.figpanel.gca().patches:
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
        for patch in self.figpanel.gca().patches:
            if str(patch.get_gid()) == selectedPatch:
                currPatch= patch
                break
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            # If the user selected OK, then the dialog's wx.ColourData will
            # contain valid information. Fetch the data ...
            data = dlg.GetColourData()
        else:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.gca().get_lines()[actualLineNumber]
        colors = [getattr(data.Colour,param)/float(255) for param in ['red','green','blue','alpha']]
        currPatch.set_facecolor(colors)
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
        for patch in self.figpanel.gca().patches:
            if str(patch.get_gid()) == selectedPatch:
                currPatch= patch
                break
        alpha = float(self.m_choice14.GetItems()[self.m_choice14.GetSelection()])
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
        self.m_mgr = aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        self.figpanel= MplCanvasFrame( self )
        self.m_mgr.AddPane( self.figpanel, aui.AuiPaneInfo() .Left() .
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
    def __init__( self, parent, *args, **params):
        # initialize the superclass, the wx.Frame
        wx.Panel.__init__( self, parent, wx.ID_ANY)
        Figure.__init__( self,)
        self.canvas=  FigureCanvas( self, wx.ID_ANY, self)
        self.sizer=   wx.BoxSizer( wx.VERTICAL)
        # instantiate the Navigation Toolbar
        self.toolbar= NavigationToolbar2Wx( self.canvas)
        # needed to support Windows systems
        self.toolbar.Realize()
        # add it to the sizer
        self.sizer.Add( self.toolbar, 0, wx.LEFT | wx.EXPAND)
        # explicitly show the toolbar
        self.toolbar.Show()
        self.sizer.Add( self.canvas, 1,  wx.LEFT | wx.TOP | wx.EXPAND)

        self.SetSizer(self.sizer)
        self.Fit()

if __name__ == '__main__':
    from random import random
    # Create a wrapper wxWidgets application
    app = wx.App()
    # instantiate the Matplotlib wxFrame
    frame = MpltFrame( None, "boxPlot", [range(20),range(30),range(35),])
    # show it
    frame.Show( True)
    # start wxWidgets mainloop
    app.MainLoop()
