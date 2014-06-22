# -*- coding: utf-8 -*-
#!/usr/bin/env python

import wx
from wx.html import HtmlHelpWindow
import sys
from os import path
from sei_glob import *

class Navegator ( wx.Dialog ):
    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = __(u"Help System"),
                            pos = wx.DefaultPosition, size = parent.GetClientSize(),
                            style = wx.DEFAULT_FRAME_STYLE)
        self.Icon= wx.GetApp().icon
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.html= HtmlHelpWindow(self, -1, 
                                helpStyle= wx.html.HF_DEFAULT_STYLE | wx.html.HF_EMBEDDED,
                                data= wx.GetApp().HELPDATA)
        bSizer1.Add( self.html, 1, wx.EXPAND )
        self.SetSizer( bSizer1 )
        self.Layout()
        self.Centre( wx.BOTH )
        

class TestFrame( wx.Frame ):
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY,
                            title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 640,480 ),
                            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        self.m_button1 = wx.Button( self, wx.ID_ANY, __(u"Show Help Window"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer1.Add( self.m_button1, 0, wx.ALL, 5 )
        self.SetSizer( bSizer1 )
        self.Layout()
        self.Centre( wx.BOTH )
        self.m_button1.Bind( wx.EVT_BUTTON, self.showHelp)
        self.Bind( wx.EVT_CLOSE, self.OnClose)

    def showHelp(self, evt):
        navegador = Navegator(self)
        navegador.Show()
        evt.Skip()

    def OnClose(self, evt):
        self.Destroy()
        evt.Skip()

if __name__ == '__main__':
    app= wx.App(0)
    from wx.html import HtmlHelpData
    import os
    path1= sys.argv[0]
    path1= path1.decode(sys.getfilesystemencoding())
    path= os.path.abspath(os.path.join(os.path.split(path1)[0], 'help'))
    fileName= os.path.join(path, "help.hhp")
    app.HELPDATA= HtmlHelpData()
    app.HELPDATA.AddBook(fileName)
    frame= TestFrame(None)
    frame.Show()
    app.MainLoop()