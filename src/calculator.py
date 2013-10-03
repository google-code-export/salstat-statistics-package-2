# -*- coding: utf-8 -*- 
import wx
import wx.aui
import statFunctions
import re
from salstat2_glob import *

from script  import PyslicesEditor
from TreeCtrl import TreePanel

def _(data):
    return data

Target = 1000

class MyFrame1 ( wx.Frame ):
    def __init__( self, parent, id= wx.ID_ANY ):
        wx.Frame.__init__ ( self, parent,
                            id = id, title = _(u"Transformation Panel"),
                            pos = wx.DefaultPosition, 
                            size = wx.Size( 640,480 ),
                            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)
        try:
            self.Icon= wx.GetApp().icon24
        except AttributeError:
            pass
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )
        self.m_mgr.SetFlags(wx.aui.AUI_MGR_TRANSPARENT_DRAG)

        self.m_panel6 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel6, 
                            wx.aui.AuiPaneInfo() .Center() .CaptionVisible( False ).
                            CloseButton( False ).PaneBorder( False ).Movable( False ).
                            Dock().Resizable().FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).Floatable( False ) )
        
        bSizer2 = wx.BoxSizer( wx.VERTICAL )

        sbSizer4 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel6, Target, _(u"Target Variable")), wx.VERTICAL )

        m_comboBox1Choices = [ ""]
        self.variableDestino = wx.ComboBox( self.m_panel6, wx.ID_ANY, _(u"target variable"), wx.DefaultPosition, wx.DefaultSize, m_comboBox1Choices, 0 )
        sbSizer4.Add( self.variableDestino, 0, wx.ALL|wx.EXPAND, 5 )

        bSizer2.Add( sbSizer4, 0, wx.EXPAND, 5 )

        sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel6, wx.ID_ANY, _(u"Script") ), wx.VERTICAL )

        self.scriptPanel = PyslicesEditor(self.m_panel6,
                                          introText=            '#'+wx.GetApp().AppName,
                                          showPySlicesTutorial= False,
                                          enableShellMode=      False,
                                          showInterpIntro=      False,
                                          marginWidth=          0,) # hide the linenumbers column
        
        sbSizer6.Add( self.scriptPanel, 1, wx.ALL|wx.EXPAND, 5 )

        bSizer2.Add( sbSizer6, 2, wx.EXPAND, 5 )

        gSizer1 = wx.GridSizer( 0, 6, 0, 0 )
        self.pusButtonList= list()
        listitems= ["( )", "[ ]", "<",  '>',  "==",    " or ",
                    "7",   "8",   "9",  "+",  ">=",    " and ",
                    "4",   "5",   "6",  "-",  "!=",    " not ",
                    "1",   "2",   "3",  "*",  "<=",    "",
                    ".",   "0",   ",",  "/",    "",   "<EVAL>",
                    ]
        startID= wx.ID_ANY
        for item in listitems:
            self.pusButtonList.append( wx.Button( self.m_panel6, startID, item , wx.DefaultPosition, wx.DefaultSize, 0 ))
            gSizer1.Add( self.pusButtonList[-1], 0, wx.EXPAND, 5 )
            startID+=1

        bSizer2.Add( gSizer1, 2, wx.EXPAND, 5 )

        self.m_panel6.SetSizer( bSizer2 )
        self.m_panel6.Layout()
        bSizer2.Fit( self.m_panel6 )
        self.m_panel7 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel7, wx.aui.AuiPaneInfo() .Right() .CaptionVisible( False ).
                            CloseButton( False ).PaneBorder( False ).Movable( False ).
                            Dock().Resizable().FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).Floatable( False ).
                            MinSize( wx.Size( 140,-1 ) ).Layer( 10 ) )
        bSizer3 = wx.BoxSizer( wx.VERTICAL )
        sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel7, wx.ID_ANY, _(u"Available Columns") ), wx.VERTICAL )
        m_checkList1Choices = []
        self.availableColumnsList = wx.ListBox( self.m_panel7, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkList1Choices, 0 )
        sbSizer1.Add( self.availableColumnsList, 1, wx.EXPAND, 5 )
        bSizer3.Add( sbSizer1, 1, wx.EXPAND, 5 )
        self.m_panel7.SetSizer( bSizer3 )
        self.m_panel7.Layout()
        bSizer3.Fit( self.m_panel7 )
        self.treePnl = TreePanel( self)#, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )

        from statFunctions import *
        self.treePnl.treelist= self.__autoCreateTreeList(statFunctions)
        self.m_mgr.AddPane( self.treePnl, wx.aui.AuiPaneInfo() .Left().
                            Caption( _(u"Available Functions") ).CloseButton( False ).
                            PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ).
                            Floatable( False ).MinSize( wx.Size( 170, 240 ) ) )
        self.helpCtrl = wx.TextCtrl( self, wx.ID_ANY, 
                                        wx.EmptyString, wx.DefaultPosition,
                                        wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP )
        self.m_mgr.AddPane( self.helpCtrl, 
                            wx.aui.AuiPaneInfo() .Bottom() .CaptionVisible( False ).
                            CloseButton( False ).PaneBorder( False ).Movable( False ).
                            Dock().Resizable().FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).Floatable( False ).
                            MinSize( wx.Size( -1, 100 ) ))
        self.__BindEvents()
        self.m_mgr.Update()
        self.Centre( wx.BOTH )
        
    def __autoCreateTreeList(self, module):
        # automatically creates a menu related with a specified module
        # to be used by the treectrl
        groups=   module.__all__
        subgroup= list()
        for group in groups:
            attr= getattr( module, group)
            result= list()
            for item in attr.__all__:
                fnc= getattr( attr, item)
                fnc.callbackFnc= self.__insertText
                result.append( ( _( fnc.name), fnc.icon,
                                 fnc().callback,
                                 fnc.id))#fnc.statName[:]
            subgroup.append( ( _( attr.__name__), result))
        return subgroup
        
    def __BindEvents(self):
        self.availableColumnsList.Bind( wx.EVT_LISTBOX_DCLICK, self.__OnListColumnsDoubleClick )
        for element in self.pusButtonList[:-1]: # the eval button has a different function
            element.Bind( wx.EVT_BUTTON, self.__OnPushButton )
        self.pusButtonList[-1].Bind(wx.EVT_BUTTON, self._onEvalButton__)
        # related help callback
        self.treePnl.tree.Bind( wx.EVT_LEFT_DOWN,  self.__OnRelatedHelp)
        self.treePnl.tree.Bind( wx.EVT_TREE_SEL_CHANGED, self.__OnTreeSelChangedRelatedHelp)
        
    def __OnTreeSelChangedRelatedHelp(self,evt):
        item= evt.GetItem()
        self.__showHelp(item)
        evt.Skip()
        
    def __OnRelatedHelp(self, evt):
        pt= evt.GetPosition();
        item, flags = self.treePnl.tree.HitTest(pt)
        self.__showHelp(item)
        evt.Skip()
        
    def __showHelp(self,item):        
        obj= self.treePnl.tree.GetItemCallback(item)
        if obj == None:
            return
        obj= obj.im_self
        textHelp= obj.object().__doc__
        # writing the text help into the help control
        self.helpCtrl.Clear()
        if textHelp != None:
            self.helpCtrl.AppendText( textHelp)
            self.helpCtrl.SetInsertionPoint(0)
            self.helpCtrl.Update( )
        
    def _onEvalButton__(self, evt):
        evt.Skip()
        
    def setAvailableColumns(self, colNames):
        if not isinstance(colNames, (list, tuple)):
            raise TypeError(self._('colNames must be a list or a tuple'))
        self.availableColumnsList.Items= colNames
        self.variableDestino.Items= colNames
        
    def __OnPushButton(self, evt):
        obj= evt.EventObject
        self.__insertText(obj.GetLabel())
        evt.Skip()
        
    def __insertText(self, text):
        if not (text in ('',u'')) and self.scriptPanel.CanPaste():
            # making the text compatible with the stc
            cpos=self.scriptPanel.GetCurrentPos()
            self.scriptPanel.UpdateUndoHistoryBefore('insert', text, cpos,
                                            cpos+len(text), forceNewAction=True)
            self.scriptPanel.write( text,'Input')
            self.scriptPanel.UpdateUndoHistoryAfter()
            # Makes paste -> type -> undo consistent with other STC apps
            self.scriptPanel.ReplaceSelection('')
        
    def __OnListColumnsDoubleClick( self, evt):
        texto= evt.GetString()# item selected
        self.__insertText(" "+texto+" ")
        evt.Skip()
        
    #def __del__( self ):
    #    self.m_mgr.UnInit()
    def GetValue(self):
        # returns all necesary values of the frame
        destinyVar= self.variableDestino.GetValue()
        if destinyVar == u'':
            dlg = wx.MessageDialog(self, self._('Target variable is empty!'),
                        self._('Error'),
                        wx.OK | wx.ICON_ERROR
                        #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                        )
            dlg.ShowModal()
            dlg.Destroy()
            return
        # removing multiple condition expresions in order to 
        # partially protect the system
        scriptText= self.scriptPanel.GetText().split(';')
        scriptText= scriptText[0]
        
        scriptText= self.scriptPanel.GetText().split('\n')
        # deleting the coment lines
        if not (len( scriptText) > 1):
            dlg = wx.MessageDialog(self, self._('The expresion to evaluate is empty!'),
                        self._('Error'),
                        wx.OK | wx.ICON_ERROR
                        #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                        )
            dlg.ShowModal()
            dlg.Destroy()
            return

        patern= "[a-zA-Z_][a-zA-Z0-9\._]*"
        foundVarNames = re.findall(patern, scriptText[1])
        return (destinyVar, scriptText[1], foundVarNames) # the first line it's a comment
   
if __name__ == '__main__':
    from wx import App
    app= App(0)
    setattr(app,'_',_)
    setattr(app,'grid',_)
    setattr(app,'Logg',_)
    setattr(app,'output',_)
    setattr(app,'plot',_)
    MyFrame1(None).Show()
    app.MainLoop()
    