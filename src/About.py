__author__ = 'Sebastian Lopez Buritica selobu@gmail.com'
import wx
from imagenes import imageEmbed
import os
import sys
from sei_glob import *

class AboutDlg ( wx.Dialog ):
    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 457,480 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        imagenes = imageEmbed()
        self.m_bitmap2 = wx.StaticBitmap( self, wx.ID_ANY, imagenes.barner, wx.DefaultPosition, wx.Size( -1,100 ), 0 )
        bSizer1.Add( self.m_bitmap2, 0, wx.ALL, 5 )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )


        bSizer2.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )

        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"SALSTAT2", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        self.m_staticText1.SetFont( wx.Font( 18, 72, 90, 90, False, wx.EmptyString ) )

        bSizer2.Add( self.m_staticText1, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"V %s"%VERSION, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        self.m_staticText3.SetFont( wx.Font( 18, 72, 90, 90, False, wx.EmptyString ) )

        bSizer2.Add( self.m_staticText3, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        bSizer2.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        bSizer1.Add( bSizer2, 0, wx.EXPAND, 5 )
        bSizer10 = wx.BoxSizer( wx.HORIZONTAL )
        bSizer10.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        bSizer10.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        bSizer1.Add( bSizer10, 0, wx.EXPAND, 5 )
        bSizer3 = wx.BoxSizer( wx.VERTICAL )
        self.m_notebook1 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_panel1 = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        self.m_htmlWin1 = wx.html.HtmlWindow( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_SCROLLBAR_AUTO )
        bSizer4.Add( self.m_htmlWin1, 1, wx.ALL|wx.EXPAND, 5 )
        self.m_htmlWin1.SetPage(self.licence)


        self.m_panel1.SetSizer( bSizer4 )
        self.m_panel1.Layout()
        bSizer4.Fit( self.m_panel1 )
        self.m_notebook1.AddPage( self.m_panel1, __(u"License"), True )
        self.m_panel2 = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer5 = wx.BoxSizer( wx.VERTICAL )

        self.m_htmlWin2 = wx.html.HtmlWindow( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_SCROLLBAR_AUTO )
        bSizer5.Add( self.m_htmlWin2, 1, wx.ALL|wx.EXPAND, 5 )

        path2= os.path.abspath( os.path.join( wx.GetApp().installDir, "help", "acerca de.html"))
        self.m_htmlWin2.LoadPage( path2)

        self.m_panel2.SetSizer( bSizer5 )
        self.m_panel2.Layout()
        bSizer5.Fit( self.m_panel2 )
        self.m_notebook1.AddPage( self.m_panel2, __(u"About"), False )
        self.m_panel3 = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer6 = wx.BoxSizer( wx.VERTICAL )

        self.m_htmlWin3 = wx.html.HtmlWindow( self.m_panel3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_SCROLLBAR_AUTO )
        bSizer6.Add( self.m_htmlWin3, 1, wx.ALL|wx.EXPAND, 5 )
        path3= os.path.abspath( os.path.join( wx.GetApp().installDir, "help", "desarrollador.html"))
        self.m_htmlWin3.LoadPage( path3)

        self.m_panel3.SetSizer( bSizer6 )
        self.m_panel3.Layout()
        bSizer6.Fit( self.m_panel3 )
        self.m_notebook1.AddPage( self.m_panel3, __(u"Developed by"), False )
        self.m_panel4 = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer7 = wx.BoxSizer( wx.VERTICAL )

        self.m_htmlWin4 = wx.html.HtmlWindow( self.m_panel4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_SCROLLBAR_AUTO )
        bSizer7.Add( self.m_htmlWin4, 1, wx.ALL|wx.EXPAND, 5 )


        self.m_panel4.SetSizer( bSizer7 )
        self.m_panel4.Layout()
        bSizer7.Fit( self.m_panel4 )
        self.m_notebook1.AddPage( self.m_panel4, __(u"History"), False )

        bSizer3.Add( self.m_notebook1, 1, wx.EXPAND |wx.ALL, 5 )


        bSizer1.Add( bSizer3, 1, wx.EXPAND, 5 )

        self.m_hyperlink1 = wx.HyperlinkCtrl( self, wx.ID_ANY, __(u"Salstat2 Website"), u"https://code.google.com/p/salstat-statistics-package-2/", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
        bSizer1.Add( self.m_hyperlink1, 0, wx.ALL, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )
    @property
    def licence(self):
        return u"""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
        <head>
        <meta content="text/html; charset=ISO-8859-1"
        http-equiv="content-type">
        <title></title>
        </head>
        <body>
        <pre
        style="margin: 0px 0px 1em; padding: 0px; font-family: monospace; line-height: 1.3em; color: rgb(0, 0, 0);font-style: normal; font-variant: normal; font-weight: normal; letter-spacing: normal; text-align: left; text-indent: 0px; text-transform: none; word-spacing: 0px; background-color: rgb(255, 255, 255);"> Salstat2 Statistical package<br> Copyright (C) 2014 Sebastian Lopez- Salstat2 Team<br><br> This program is free software: you can redistribute it and/or modify<br> it under the terms of the GNU General Public License as published by<br> the Free Software Foundation, either version 3 of the License, or<br> (at your option) any later version.<br><br> This program is distributed in the hope that it will be useful,<br> but WITHOUT ANY WARRANTY; without even the implied warranty of<br> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the<br> GNU General Public License for more details.<br><br> You should have received a copy of the GNU General Public License<br> along with this program. If not, see &lt;http://www.gnu.org/licenses/&gt;.</pre>
        </body>
        </html>"""