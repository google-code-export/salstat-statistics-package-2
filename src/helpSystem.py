# -*- coding: utf-8 -*-
#!/usr/bin/env python
import wx
from wx.html import HtmlHelpData, HtmlHelpWindow
import sys
from os import path

class Navegator ( wx.Frame ):
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Help System",
                            pos = wx.DefaultPosition, size = wx.Size(640,480),
                            style = wx.DEFAULT_FRAME_STYLE)
        self.path= path.abspath(path.join(path.split(sys.argv[0])[0], 'help'))
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        fileName= path.join(self.path, "help.hhp")
        ## help system ######
        if path.isfile(fileName):
            self.helpData= HtmlHelpData()
            self.helpData.AddBook(fileName)
            self.html= HtmlHelpWindow(self, -1, size= self.GetClientSize(),
                                      helpStyle= wx.html.HF_DEFAULT_STYLE | wx.html.HF_EMBEDDED,
                                      data= self.helpData) ## the trouble could be here
        else:
            self.html = wx.html.HtmlHelpWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_SCROLLBAR_AUTO)
        bSizer1.Add( self.html, 1, wx.EXPAND )
        ## help system end ##
        self.SetSizer( bSizer1 )
        self.Fit()
        self.Layout()
        self.Centre( wx.BOTH )
        self.Bind( wx.EVT_CLOSE, self.OnClose)
        
    def OnClose(self,event):
        self.Destroy()
        event.Skip()

class TestFrame( wx.Frame ):
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 640,480 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        self.m_button1 = wx.Button( self, wx.ID_ANY, u"Show Help Window", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer1.Add( self.m_button1, 0, wx.ALL, 5 )
        self.SetSizer( bSizer1 )
        self.Layout()
        self.Centre( wx.BOTH )
        self.m_button1.Bind( wx.EVT_BUTTON, self.showHelp)
        self.Bind( wx.EVT_CLOSE, self.OnClose)

    def showHelp(self, event):
        navegador = Navegator(self)
        navegador.Show()
        event.Skip()

    def OnClose(self, event):
        self.Destroy()
        event.Skip()

if __name__ == '__main__':
    app= wx.App(0)
    frame= TestFrame(None)
    frame.Show()
    app.MainLoop()