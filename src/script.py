'''
Created on 14/05/2012

@author: USUARIO
'''
import wx
import wx.lib.agw.aui as aui
from imagenes import imageEmbed

class ScriptPanel(wx.Panel):
    def __init__(self, parent,*args):
        '''ScriptPanel parent, log, *args'''
        self.log = args[0]
        try:
            wx.Panel.__init__(self, parent, wx.ID_ANY, *args[1:])
        except:
            wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )


        self.answerPanel2 = wx.py.crust.editwindow.EditWindow(self)
        self.answerPanel2.setDisplayLineNumbers(True)
        self.answerPanel2.SetIndent(4)               # Proscribed indent size for wx
        self.answerPanel2.SetIndentationGuides(True) # Show indent guides
        self.answerPanel2.SetBackSpaceUnIndents(True)# Backspace unindents rather than delete 1 space
        self.answerPanel2.SetTabIndents(True)        # Tab key indents
        self.answerPanel2.SetTabWidth(4)             # Proscribed tab size for wx
        self.answerPanel2.SetUseTabs(False)

        self.m_mgr.AddPane( self.answerPanel2, wx.aui.AuiPaneInfo().CenterPane().Dock().
                            Resizable(True).FloatingSize( wx.DefaultSize ).
                            DockFixed( True ).Centre().
                            CloseButton(False ) )

        tb1= aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                            agwStyle=  aui.AUI_TB_OVERFLOW | aui.AUI_TB_HORZ_LAYOUT)
        tb1.SetToolBitmapSize(wx.Size(16, 16))
        imagenes = imageEmbed()
        self.bt1= tb1.AddSimpleTool(wx.ID_ANY, u"Run Script" , imagenes.runIcon(), u"Run Script" )
        tb1.AddSeparator()
        self.bt2= tb1.AddSimpleTool(wx.ID_ANY, u"New Script" , imagenes.documentNew(), u"New Script" )
        self.bt3= tb1.AddSimpleTool(wx.ID_ANY, u"Save data" , imagenes.save2disk(), u"Save data" )
        self.bt4= tb1.AddSimpleTool(wx.ID_ANY, u"Load data" , imagenes.folderOpen(), u"Load data" )
        tb1.AddSeparator()
        self.bt5= tb1.AddSimpleTool(wx.ID_ANY, u"Cut" , imagenes.edit_cut(), u"Cut" )
        self.bt6= tb1.AddSimpleTool(wx.ID_ANY, u"Copy" , imagenes.edit_copy(), u"Copy" )
        self.bt7= tb1.AddSimpleTool(wx.ID_ANY, u"Paste" , imagenes.edit_paste(), u"Paste" )
        tb1.AddSeparator()
        self.bt8= tb1.AddSimpleTool(wx.ID_ANY, u"Undo", imagenes.edit_undo(), u"Undo")
        self.bt9= tb1.AddSimpleTool(wx.ID_ANY, u"Redo" , imagenes.edit_redo(), u"Redo" )
        tb1.Realize()

        self.m_mgr.AddPane( tb1, wx.aui.AuiPaneInfo().Top().Dock().
                            ToolbarPane().Resizable(False).FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).Layer(1).Gripper(True).
                            LeftDockable( False ).RightDockable(False).
                            CloseButton(False ) )
        self.Bindded()
        self.Layout()
        self.m_mgr.Update()
        self.Centre( wx.BOTH )


    def Bindded(self):
        self.Bind(wx.EVT_TOOL, self.runScript, id = self.bt1.GetId() )
        self.Bind(wx.EVT_TOOL, self.newScript, id = self.bt2.GetId())
        self.Bind(wx.EVT_TOOL, self.SaveScriptAs, id = self.bt3.GetId())
        self.Bind(wx.EVT_TOOL, self.loadScript, id = self.bt4.GetId())
        self.Bind(wx.EVT_TOOL, self.CutSelection, id = self.bt5.GetId())
        self.Bind(wx.EVT_TOOL, self.CopySelection, id = self.bt6.GetId())
        self.Bind(wx.EVT_TOOL, self.PasteSelection, id = self.bt7.GetId())
        self.Bind(wx.EVT_TOOL, self.undo, id = self.bt8.GetId())
        self.Bind(wx.EVT_TOOL, self.redo, id = self.bt9.GetId())

    def clearLog(self,):
        self.log.clearLog()

    def show(self,*variables):
        '''show the results in the log panel'''
        for var in variables:
            try:
                if isinstance(var,(str,unicode,)):
                    self.log.writeLine( var)
                else:
                    self.log.writeLine( str(var))
            except Exception as error:
                self.log.writeLine(error.message)

    def runScript(self, event):
        env= {'show': self.show,
              'cls': self.clearLog}
        buildins = {}
        buildins["locals"]   = None
        buildins["__name__"] = None
        buildins["__file__"] = None
        # buildins["__builtins__"] = None
        try:
            mainscript = self.answerPanel2.GetText()
            #mainscript = mainscript.replace() 
            exec(mainscript,buildins,env)
        except Exception as error:
            self.log.writeLine(error.message)

    def loadScript(self, event):
        wildcard = 'TEXT files (*.txt)|*.txt|ALL files (*.*)|*.*'
        dlg = wx.FileDialog(self, "Open Script File", "","",\
                            wildcard, wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.answerPanel2.SetText('')
            fout = open(filename, "rb")
            for line in fout.readlines():
                self.answerPanel2.AddText(line)
            fout.close()

    def SaveScriptAs(self, event):
        wildcard = 'TEXT files (*.txt)|*.txt|ALL files (*.*)|*.*'
        dlg = wx.FileDialog(self, "Open Script File", "","",\
                            wildcard, wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            fout = open(filename, "wb")
            for line in self.answerPanel2.GetValue().split('\n'):
                fout.writelines(line)
            fout.close()

    def undo(self,event):
        self.answerPanel2.Undo()

    def redo(self,event):
        self.answerPanel2.Redo()

    def CutSelection(self, event):
        self.answerPanel2.Cut()

    def CopySelection(self, event):
        self.answerPanel2.Copy()

    def PasteSelection(self, event):
        self.answerPanel2.Paste()

    def newScript(self, event):
        self.answerPanel2.SetText("")