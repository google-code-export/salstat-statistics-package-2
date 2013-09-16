'''
Created on 14/05/2012

@author: USUARIO
'''

import wx
import wx.lib.agw.aui as aui
from imagenes import imageEmbed
# from statlib import stats
# from plotFrame import MpltFrame as plot
import traceback
# import wx.lib.multisash as sash

# styled text using wxPython's
# wx.StyledTextCtrl(parent, id, pos, size, style, name)
# set up for folding and Python code highlighting
# source: Dietrich  16NOV2008
# http://www.python-forum.org/pythonforum/viewtopic.php?f=2&t=10065#

import  wx
import  wx.stc  as  stc
import  keyword
from wx.py import sliceshell
import os
import sys

class MyFileDropTarget(wx.FileDropTarget):
    def __init__( self, wxPanel ):
        wx.FileDropTarget.__init__(self)
        self.window = wxPanel

    def OnDropFiles( self, x, y, filenames):
        print "\n%d file(s) dropped at %d,%d:" %( len( filenames), x, y)
        for file in filenames:
            print file

        # try to load the file
        if isinstance(filenames, (str, unicode)):
            filenames= [filenames]

        if len(filenames) == 0:
            print "You don't select any file"
            return

        # selecting just the first filename
        filename= filenames[0]
        # self.window.LoadXls(filename)
        scriptPanel=   self.window
        notebookSheet= scriptPanel.Parent.Parent ## the script panel

        notebookSheet.loadScript( evt=None,  path= filename)

if wx.Platform == '__WXMSW__':
    # for windows OS
    faces = {
        'times': 'Times New Roman',
        'mono' : 'Courier New',
        # try temporary switch to mono
        'helv' : 'Courier New',
        #'helv' : 'Arial',
        'other': 'Comic Sans MS',
        'size' : 10,
        'size2': 8,
    }
else:
    faces = {
        'times': 'Times',
        'mono' : 'Courier',
        'helv' : 'Helvetica',
        'other': 'Century Schoolbook',
        'size' : 12,
        'size2': 10,
    }

class MySTC( stc.StyledTextCtrl, object):
    """
    set up for folding and Python code highlighting
    """
    #doc= None
    def __init__(self, parent, ID= wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0):
        stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)

        # use Python code highlighting
        self.SetLexer(stc.STC_LEX_PYTHON)

        # defining the keys to be colored
        keylist=['cls','plot','grid','show','dialog','OK','report']
        keylist.extend(keyword.kwlist)
        keylist.extend(keyword.__builtins__.keys())
        keyWordlist = " ".join(keylist)
        self.SetKeyWords(0, keyWordlist )

        # setting the margin one to be numerical
        self.SetMarginWidth(1, 45)
        self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        # setting the margin zero to be None

        self.SetMargins(0, 0)

        #self.SetMaxLength(250)

        # set other options ...
        self.SetProperty("fold", "1")

        self.SetViewWhiteSpace(False)
        self.SetUseAntiAliasing(True)
        self.SetEdgeColumn(100)# number of the column posiiton to higligh the code
        self.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
        self.SetCaretForeground("black") # background of the cursor
        self.SetTabWidth(4)

        # setup a margin to hold the fold markers
        self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)

        # fold markers use square headers
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,
                          stc.STC_MARK_BOXMINUS, "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDER,
                          stc.STC_MARK_BOXPLUS, "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,
                          stc.STC_MARK_VLINE, "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,
                          stc.STC_MARK_LCORNER, "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,
                          stc.STC_MARK_BOXPLUSCONNECTED, "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID,
                          stc.STC_MARK_BOXMINUSCONNECTED, "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL,
                          stc.STC_MARK_TCORNER, "white", "#808080")

        # bind some events ...
        self.Bind(stc.EVT_STC_UPDATEUI, self.onUpdateUI)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.onMarginClick)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPressed)

        # make some general styles ...
        # global default styles for all languages
        # set default font
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                          "face:%(helv)s,size:%(size)d" % faces)
        # set default background color
        if wx.Platform == "__WXMAC__":
            self.StyleSetBackground(style=stc.STC_STYLE_DEFAULT,
                                    back="#ffffff") # White
        else:
            self.StyleSetBackground(style=stc.STC_STYLE_DEFAULT,
                                    back="#F5F5DC") # beige / light yellow

        # reset all to be like the default
        self.StyleClearAll()

        # more global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER,
                          "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR,
                          "face:%(other)s" % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,
                          "fore:#FFFFFF,back:#0000FF,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,
                          "fore:#000000,back:#FF0000,bold")


        # make the Python styles ...
        # default
        self.StyleSetSpec(stc.STC_P_DEFAULT,
                          "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        # comments
        self.StyleSetSpec(stc.STC_P_COMMENTLINE,
                          "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
        # number
        self.StyleSetSpec(stc.STC_P_NUMBER,
                          "fore:#007F7F,size:%(size)d" % faces)
        # string
        self.StyleSetSpec(stc.STC_P_STRING,
                          "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        # single quoted string
        self.StyleSetSpec(stc.STC_P_CHARACTER,
                          "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        # keyword
        self.StyleSetSpec(stc.STC_P_WORD,
                          "fore:#00007F,bold,size:%(size)d" % faces)
        # triple quotes
        self.StyleSetSpec(stc.STC_P_TRIPLE,
                          "fore:#7F0000,size:%(size)d" % faces)
        # triple double quotes
        self.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE,
                          "fore:#7F0000,size:%(size)d" % faces)
        # class name definition
        self.StyleSetSpec(stc.STC_P_CLASSNAME,
                          "fore:#0000FF,bold,underline,size:%(size)d" % faces)
        # function or method name definition
        self.StyleSetSpec(stc.STC_P_DEFNAME,
                          "fore:#007F7F,bold,size:%(size)d" % faces)
        # operators
        self.StyleSetSpec(stc.STC_P_OPERATOR,
                          "bold,size:%(size)d" % faces)
        # identifiers
        self.StyleSetSpec(stc.STC_P_IDENTIFIER,
                          "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        # comment-blocks
        self.StyleSetSpec(stc.STC_P_COMMENTBLOCK,
                          "fore:#7F7F7F,size:%(size)d" % faces)
        # end of line where string is not closed
        self.StyleSetSpec(stc.STC_P_STRINGEOL,
                          "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d"\
                          % faces)

        # register some images for use in the AutoComplete box
        self.RegisterImage(1,
                           wx.ArtProvider.GetBitmap(wx.ART_TIP, size=(16,16)))
        self.RegisterImage(2,
                           wx.ArtProvider.GetBitmap(wx.ART_NEW, size=(16,16)))
        self.RegisterImage(3,
                           wx.ArtProvider.GetBitmap(wx.ART_COPY, size=(16,16)))

        #if self.doc:
        #    self.SetDocPointer(self.doc)
        #else:
        #    self.SetText(u"")
        #    MySTC.doc= self.GetDocPointer()

    def onKeyPressed(self, event):
        if self.CallTipActive():
            self.CallTipCancel()
        key = event.GetKeyCode()
        if key == 32 and event.CmdDown():
            pos = self.GetCurrentPos()
            # tips
            if event.ShiftDown():
                self.CallTipSetBackground("yellow")
                self.CallTipShow(pos, 'Show tip stuff')
            # code completion (needs more work)
            else:
                kw = keyword.kwlist[:]
                # optionally add more ...
                kw.append("__init__?3")
                # Python sorts are case sensitive
                kw.sort()
                # so this needs to match
                self.AutoCompSetIgnoreCase(True)
                # registered images are specified with appended "?type"
                for i in range(len(kw)):
                    if kw[i] in keyword.kwlist:
                        kw[i] = kw[i] + "?1"
                self.AutoCompShow(0, " ".join(kw))
        else:
            event.Skip()

    def onUpdateUI(self, evt):
        """update the user interface"""
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()
        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)
        # check before
        if charBefore and chr(charBefore) in "[]{}()"\
           and styleBefore == stc.STC_P_OPERATOR:
            braceAtCaret = caretPos - 1
        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and chr(charAfter) in "[]{}()"\
               and styleAfter == stc.STC_P_OPERATOR:
                braceAtCaret = caretPos
        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)
        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)

    def onMarginClick(self, evt):
        # fold and unfold as needed
        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.foldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())
                if self.GetFoldLevel(lineClicked) &\
                   stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldexpanded(lineClicked, True)
                        self.expand(lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldexpanded(lineClicked):
                            self.SetFoldexpanded(lineClicked, False)
                            self.expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldexpanded(lineClicked, True)
                            self.expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)

    def foldAll(self):
        """folding folds, marker - to +"""
        lineCount = self.GetLineCount()
        expanding = True
        # find out if folding or unfolding
        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) &\
               stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldexpanded(lineNum)
                break;
        lineNum = 0
        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if level & stc.STC_FOLDLEVELHEADERFLAG and \
               (level & stc.STC_FOLDLEVELNUMBERMASK) ==\
               stc.STC_FOLDLEVELBASE:
                if expanding:
                    self.SetFoldexpanded(lineNum, True)
                    lineNum = self.expand(lineNum, True)
                    lineNum = lineNum - 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldexpanded(lineNum, False)
                    if lastChild > lineNum:
                        self.HideLines(lineNum+1, lastChild)
            lineNum = lineNum + 1

    def expand(self, line, doexpand, force=False, visLevels=0, level=-1):
        """expanding folds, marker + to -"""
        lastChild = self.GetLastChild(line, level)
        line = line + 1
        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doexpand:
                    self.ShowLines(line, line)
            if level == -1:
                level = self.GetFoldLevel(line)
            if level & stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldexpanded(line, True)
                    else:
                        self.SetFoldexpanded(line, False)
                    line = self.expand(line, doexpand, force, visLevels-1)
                else:
                    if doexpand and self.GetFoldexpanded(line):
                        line = self.expand(line, True, force, visLevels-1)
                    else:
                        line = self.expand(line, False, force, visLevels-1)
            else:
                line = line + 1;
        return line

class PyslicesEditor(sliceshell.SlicesShell, object):
    from wx.py.sliceshell import INPUT_MASK, OUTPUT_MASK, OUTPUT_BG
    def __init__(self, *args, **params):
        self.__marginWith= 45
        try:   self.__marginWith= params.pop('marginWidth')
        except KeyError: pass

        sliceshell.SlicesShell.__init__(self, *args, **params)
        self.SetMarginWidth(1, self.__marginWith)
        self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        dropTarget = MyFileDropTarget( self)
        self.SetDropTarget(dropTarget)

    def processLine(self):
        """Process the line of text at which the user hit Enter or Shift+RETURN."""
        # The user hit ENTER (Shift+RETURN) (Shift+ENTER) and we need to
        # decide what to do. They could be sitting on any line in the slices shell.
        thepos = self.GetCurrentPos()
        cur_line = self.GetCurrentLine()
        marker=self.MarkerGet(cur_line)
        if marker & self.INPUT_MASK:
            pass
        elif marker & self.OUTPUT_MASK:
            return
        else:
            pass #print 'BLANK LINE!!'

        startline,endline=self.GetIOSlice(cur_line)

        if startline==0:
            startpos=0
        else:
            startpos=self.PositionFromLine(startline)

        endpos=self.GetLineEndPosition(endline)
        # If they hit ENTER inside the current command, execute the command.
        if self.CanEdit():
            self.SetCurrentPos(endpos)
            self.interp.more = False
            command = self.GetTextRange(startpos, endpos)
            lines = command.split(os.linesep)
            lines = [line.rstrip() for line in lines]
            command = '\n'.join(lines)
            if self.reader.isreading:
                if not command:
                    # Match the behavior of the standard Python shell
                    # when the user hits return without entering a value.
                    command= '\n'
                self.reader.input= command
                self.write(os.linesep,'Input')
                self.MarkerSet(self.GetCurrentLine(),READLINE_BG)
                self.MarkerSet(self.GetCurrentLine(),INPUT_READLINE)
            else:
                self.runningSlice = (startline,endline)
                #########  self.push(command,useMultiCommand=True)
                #print 'command: ',command
                wx.FutureCall(1, self.EnsureCaretVisible)
                self.runningSlice=None

        # removed because ctrl+enter doesn,t work
        skip=self.BackspaceWMarkers(force=True)
        if skip:
            self.DeleteBack()

        if self.GetCurrentLine()==self.GetLineCount()-1:
            self.write(os.linesep,type='Input')
            cpos= self.GetCurrentLine()
            if self.MarkerGet(cpos-1) & self.OUTPUT_MASK:
                self.MarkerAdd(cpos-1, self.OUTPUT_BG)
            self.SplitSlice()
        else:
            cur_line= self.GetCurrentLine()
            new_pos=  self.GetLineEndPosition(cur_line+1)
            self.SetSelection(new_pos,new_pos)
            self.SetCurrentPos(new_pos)

        self.EmptyUndoBuffer()
        self.NeedsCheckForSave= True
        if self.hasSyntaxError:
            pos= self.GetLineEndPosition(self.syntaxErrorRealLine)
            self.SetCurrentPos(pos)
            self.SetSelection(pos,pos)

def numPage():
    i = 1
    while True:
        yield i
        i+= 1

class emptylog:
    # emulating an empty log panel
    def clearLog(self):
        pass
    def writeLine(self, *args, **params):
        pass


class ScriptPanel( wx.Panel):
    tb1= None
    def __init__( self, parent,*args, **params ):
        self.finddlg= None
        self.finddata = wx.FindReplaceData()
        self.finddata.SetFlags(wx.FR_DOWN)

        '''ScriptPanel parent, log, *args'''
        self.log=   args[0]
        self.__hideToolbar= False
        try:
            self.__hideToolbar= params.pop('hideToolbar')
        except KeyError:
            pass

        try:
            wx.Panel.__init__(self, parent, wx.ID_ANY, *args[1:])
        except:
            wx.Panel.__init__(self, parent, wx.ID_ANY)

        self.m_mgr = aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        self.m_notebook= wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                              wx.aui.AUI_NB_SCROLL_BUTTONS|wx.aui.AUI_NB_TAB_MOVE|
                                              wx.aui.AUI_NB_WINDOWLIST_BUTTON|wx.aui.AUI_NB_BOTTOM|
                                              wx.aui.AUI_NB_TAB_SPLIT|wx.aui.AUI_NB_CLOSE_BUTTON)

        self.m_mgr.AddPane( self.m_notebook, aui.AuiPaneInfo().CenterPane().Dock().
                            Resizable(True).FloatingSize( wx.DefaultSize ).
                            DockFixed( True ).Centre().
                            CloseButton(False ) )
        self.npage = numPage()
        self.currentPage = None
        self.pageNames= dict()

        if not self.__hideToolbar:
            self.m_mgr.AddPane( self.getToolbar(),
                                aui.AuiPaneInfo().Name("tb5").
                                Caption(_("Basic Operations")).
                                ToolbarPane().Top().GripperTop().
                                CloseButton( False))

        self.Bindded()
        self.addPage()
        self.Layout()
        self.m_mgr.Update()
        self.Center( )

    def _createToolbar( self):
        if self.tb1 != None:
            return

        prepend_items, append_items = [], []
        item = aui.AuiToolBarItem()

        item.SetKind(wx.ITEM_SEPARATOR)
        append_items.append(item)

        item = aui.AuiToolBarItem()
        item.SetKind(wx.ITEM_NORMAL)
        item.SetId(wx.ID_ANY)
        item.SetLabel(_("Customize..."))
        append_items.append(item)

        if wx.version < "2.9":
            tb1= aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                                style = aui.AUI_TB_OVERFLOW | aui.AUI_TB_VERTICAL)
        else:
            tb1= aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                                agwStyle = aui.AUI_TB_OVERFLOW | aui.AUI_TB_VERTICAL)

        imagenes = imageEmbed()
        tb1.SetToolBitmapSize(wx.Size(16, 16))
        self.bt1= tb1.AddSimpleTool(wx.ID_ANY, _(u"Run Script") , imagenes.runIcon, _(u"Run Script"), )
        tb1.AddSeparator()
        self.bt2= tb1.AddSimpleTool(wx.ID_ANY, _(u"New Script") , imagenes.documentNew, _(u"New Script") )
        self.bt4= tb1.AddSimpleTool(wx.ID_ANY, _(u"Load Script") , imagenes.folderOpen, _(u"Load Script") )
        tb1.AddSeparator()
        self.btSave= tb1.AddSimpleTool(wx.ID_ANY, _(u"Save Script") , imagenes.disk, _(u"Save Script") )
        self.bt3= tb1.AddSimpleTool(wx.ID_ANY, _(u"Save Script As") , imagenes.save2disk, _(u"Save Script as") )
        tb1.AddSeparator()
        self.bt8= tb1.AddSimpleTool(wx.ID_ANY, _(u"Undo"), imagenes.edit_undo, _(u"Undo") )
        self.bt9= tb1.AddSimpleTool(wx.ID_ANY, _(u"Redo"), imagenes.edit_redo, _(u"Redo") )
        tb1.AddSeparator()
        self.bt5= tb1.AddSimpleTool(wx.ID_ANY, _(u"Cut"), imagenes.edit_cut, _(u"Cut") )
        self.bt6= tb1.AddSimpleTool(wx.ID_ANY, _(u"Copy"), imagenes.edit_copy, _(u"Copy") )
        self.bt7= tb1.AddSimpleTool(wx.ID_ANY, _(u"Paste"), imagenes.edit_paste, _(u"Paste") )
        tb1.AddSeparator()
        self.bt10= tb1.AddSimpleTool(wx.ID_ANY, _(u"Find"), imagenes.find, _(u"Find") )
        tb1.SetCustomOverflowItems( prepend_items, append_items)
        tb1.SetToolDropDown(wx.ID_ANY, True)
        tb1.Realize()
        self.tb1= tb1

    def getToolbar(self):
        if self.tb1 == None:
            self._createToolbar() # create and set the tb1
        return self.tb1

    # implementing a wrap to the current notebook
    def __getattribute__( self, name):
        '''wraps the funtions to the grid
        emulating a grid control'''
        try:
            return object.__getattribute__( self, name)
        except AttributeError:
            if self.GetPageCount( ) != 0:
                if str( type( self.currentPage)) == "<class 'wx._core._wxPyDeadObject'>":
                    self.currentPage == None
                    return
                currPage= self.currentPage
                return currPage.__getattribute__( name)
            raise AttributeError

    def getPageNames( self):
        return self.pageNames.keys()

    def getHeader( self,pageName):
        if not (pageName in self.pageNames.keys()):
            raise StandardError('The page does not exist')
        page= self.pageNames[pageName]
        return page.getHeader()

    def OnNotebookPageChange( self,evt):
        self.currentPage= self.m_notebook.GetPage( evt.Selection)

    def GetPageCount( self):
        # 21/04/2011
        # retorna el numero de paginas que hay en el notebook
        return self.m_notebook.PageCount

    def addPage( self, data= dict()):
        defaultData = {'name': u''}
        for key, value in data.items():
            if defaultData.has_key(key):
                defaultData[key] = value
        # adiciona una pagina al notebook grid
        newName= defaultData['name'] +'_'+ str(self.npage.next())
        #multi = sash.MultiSash( self.m_notebook, -1, pos = (0,0), size= self.m_notebook.GetSize())
        # Use this method to set the default class that will be created when
        # a new sash is created. The class's constructor needs 1 parameter
        # which is the parent of the window
        #multi.SetDefaultChildClass(MySTC)

        self.pageNames[newName]= PyslicesEditor(self.m_notebook,
                                                introText=            '#'+wx.GetApp().AppName,
                                                showPySlicesTutorial= False,
                                                enableShellMode=      False,
                                                showInterpIntro=      False,
                                                )
        setattr(self.pageNames[newName],'currPagePath', None)

        self.currentPage=  self.pageNames[newName]
        ntb= self.pageNames[newName]
        self.m_notebook.AddPage(ntb, newName, False )
        # se hace activo la pagina adicionada
        self.m_notebook.SetSelection(self.m_notebook.GetPageCount()-1)
        #callback
        self.pageNames[newName].Bind(wx.EVT_KEY_DOWN ,  self.OnKeyDown)
        return ntb # ret;na el objeto ntb

    def OnshowFindDlg(self, evt):
        if self.finddlg != None:
            return
        ##self.nb.SetSelection(1)
        self.finddlg = wx.FindReplaceDialog(self, self.finddata, _("Find"),
                        wx.FR_NOMATCHCASE | wx.FR_NOWHOLEWORD)
        self.finddlg.Show(True)

    def OnFindNext(self, event):
        if self.finddata.GetFindString():
            self.OnFind(event)
        else:
            self.OnHelpFind(event)

    def OnFindClose(self, event):
        event.GetDialog().Destroy()
        self.finddlg = None

    def OnFind(self, evt):
        editor = self
        ##self.nb.SetSelection(1)
        end = editor.GetLastPosition()
        textstring = editor.GetRange(0, end).lower()
        findstring = self.finddata.GetFindString().lower()
        backward = not (self.finddata.GetFlags() & wx.FR_DOWN)
        if backward:
            start = editor.GetSelection()[0]
            loc = textstring.rfind(findstring, 0, start)
        else:
            start = editor.GetSelection()[1]
            loc = textstring.find(findstring, start)
        if loc == -1 and start != 0:
            # string not found, start at beginning
            if backward:
                start = end
                loc = textstring.rfind(findstring, 0, start)
            else:
                start = 0
                loc = textstring.find(findstring, start)
        if loc == -1:
            dlg = wx.MessageDialog(self, _('Find String Not Found'),
                          _('Find String Not Found in Demo File'),
                          wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        if self.finddlg:
            if loc == -1:
                self.finddlg.SetFocus()
                return
            else:
                self.finddlg.Destroy()
                self.finddlg = None
        editor.ShowPosition(loc)
        editor.SetSelection(loc, loc + len(findstring))

    def OnKeyDown(self, evt):
        key = evt.GetKeyCode()
        if key == wx.WXK_F3:
            self.OnFindNext( evt)
            evt.Skip()
            return

        #if key == ord(" ") and evt.ShiftDown():
        #    self.SelectCol( self.GetGridCursorCol())
        #    return

        if not evt.CmdDown():
            evt.Skip()
            return
        # it works only if you have press hold down the [Ctrl] key
        if   key == ord("F"): self.OnshowFindDlg(evt)
        #elif key == ord("V"): self.OnPaste()
        #elif key == ord("X"): self.OnCut()
        #elif key == ord("Z"): self.Undo()
        #elif key == ord("Y"): self.Redo() # elif key == ord(" "): self.SelectCol(self.GetGridCursorCol())
        elif key:  evt.Skip()

    def Bindded(self):
        if not self.__hideToolbar:
            self.Bind( wx.EVT_TOOL, self.runScript,      id = self.bt1.GetId())
            self.Bind( wx.EVT_TOOL, self.newScript,      id = self.bt2.GetId())
            self.Bind( wx.EVT_TOOL, self.SaveScriptAs,   id = self.bt3.GetId())
            self.Bind( wx.EVT_TOOL, self.SaveScript,     id = self.btSave.GetId())
            self.Bind( wx.EVT_TOOL, self.loadScript,     id = self.bt4.GetId())
            self.Bind( wx.EVT_TOOL, self.CutSelection,   id = self.bt5.GetId())
            self.Bind( wx.EVT_TOOL, self.CopySelection,  id = self.bt6.GetId())
            self.Bind( wx.EVT_TOOL, self.PasteSelection, id = self.bt7.GetId())
            self.Bind( wx.EVT_TOOL, self.undo,           id = self.bt8.GetId())
            self.Bind( wx.EVT_TOOL, self.redo,           id = self.bt9.GetId())
            self.Bind( wx.EVT_TOOL, self.OnshowFindDlg,  id = self.bt10.GetId())
        self.m_notebook.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnNotebookPageChange)
        self.m_notebook.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.delPage)
        # to the find dialog
        self.Bind( wx.EVT_FIND,       self.OnFind)
        self.Bind( wx.EVT_FIND_NEXT,  self.OnFindNext)
        self.Bind( wx.EVT_FIND_CLOSE, self.OnFindClose)

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
        try:
            mainscript= self.GetText()
            wx.GetApp().frame.shellPanel.interp.runcode( mainscript)
        except (Exception, TypeError) as e:
            traceback.print_exc( file = self.log)

    def delPage( self, evt, page= None):
        # si no se ingresa un numero de pagina se
        #     considera que se va a borrar la pagina actual
        # las paginas se numeran mediante numeros desde el cero
        if page == None:
            # se considera que la pagina a borrar es la pagina actual
            #self.m_notebook.GetCurrentPage().Destroy() # borra el contenido de la pagina
            if self.m_notebook.GetSelection() > -1:
                page = self.m_notebook.GetSelection()
            else:
                return

        pageNumber = int(page)

        if pageNumber < 0:
            return

        if pageNumber > self.GetPageCount():
            raise IndexError("Page doesn't exist")

        currPageObj= self.m_notebook.GetPage(pageNumber)
        # delete the erased page from the pages list
        pageName = None
        for pageName, pageObj in self.pageNames.items():
            if pageObj == currPageObj:
                break

        if pageName == None:
            return

        self.pageNames.pop( pageName)
        # it isn't required to delete a page because the aui manageer makes itself
        # so if you enable the following line the app will crash
        #self.m_notebook.DeletePage( pageNumber)

        # in case there is no pages then the system adds one
        if len( self.pageNames) == 0:
            self.addPage()
        evt.Skip()

    def _load(self, texto):
        self.addPage()
        self.Text= u''
        dataToWrite= wx.TextDataObject()
        if not texto.endswith('\n'):
            content= texto+'\n'
        else:
            content= texto
        # changing the string to the default system encoding
        content= content.decode(sys.getfilesystemencoding())
        content= content.encode('utf8', errors= 'ignore')
        appName= wx.GetApp().GetAppName() 
        if content.startswith('#'+appName+'\r'):
            content= content.replace('#'+appName+'\r','')
        data = wx.TextDataObject( content)
        # readin the data content of the clipboard
        newData= wx.TextDataObject()
        if wx.TheClipboard.IsOpened() or wx.TheClipboard.Open():
            try:
                wx.TheClipboard.GetData( newData)
            finally:
                wx.TheClipboard.Close()
        self._clip(data)
        self.Paste()
        # restoring the clipboard
        if wx.TheClipboard.IsOpened() or wx.TheClipboard.Open():
            try:
                wx.TheClipboard.SetData( newData)
            finally:
                wx.TheClipboard.Close()

    def loadScript(self, evt= None, *args, **params):
        """
        :param event:
        :return:
        """
        try:
            path= params.pop('path')
        except:
            path= None

        if path == None:
            _= wx.GetApp()._
            wildcard = 'TEXT files (*.txt;*.py)|*.txt;*.py|ALL files (*.*)|*.*'
            dlg = wx.FileDialog(self, _("Open Script File"), "", "", \
                                wildcard, wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                path= filename
                import os.path
                if not os.path.exists(filename):
                    if evt != None:
                        evt.Skip()
                    return
        fout = open( path, "rb")
        content= fout.read()
        fout.close()
        self._load( content)
        setattr(self.currentPage, 'currPagePath', path)
        #self.processLine()
        if evt != None:
            evt.Skip()

    def SaveScript(self, evt):
        print "save Script"
        try:
            self.currentPage.currPagePath
        except:
            self.currentPage.currPagePath == None

        if self.currentPage.currPagePath == None:
            filename= self.SaveScriptAs(evt)
            if filename != None:
                setattr(self.currentPage, 'currPagePath', filename)
        else:
            fout = open( self.currentPage.currPagePath, "wb")
            for line in self.GetText().split('\n'):
                fout.writelines(line.encode('utf8', errors= 'ignore'))
            fout.close()
            # changing the name of the notebook
            filename= os.path.split(self.currPagePath)[-1].split('.')[0]
            if len( filename) > 8:
                filename= filename[:8]+u'\u2026'
            self.SetText= filename
        evt.Skip()

    def SaveScriptAs(self, evt):
        _= wx.GetApp()._
        try:
            wildcard = _('TEXT files (*.txt)|*.txt|ALL files (*.*)|*.*')
            dlg = wx.FileDialog(self, _("Open Script File"), "","",\
                                wildcard, wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                fullPath = dlg.GetPath()
                if os.path.exists(fullPath):
                    dlg = wx.MessageDialog(self, _('Would you like to overwrite the existent file?'),
                                   _('Warning'),
                                   wx.YES_NO | wx.ICON_WARNING )
                    if dlg.ShowModal() != wx.ID_YES:
                        dlg.Destroy()
                        return None
                    else:
                        dlg.Destroy()
                fout = open(fullPath, "wb")
                for line in self.GetText().split('\n'):
                    fout.writelines(line)
                fout.close()
                # changing the name of the notebook
                filename= dlg.GetFilename()[:-4]
                if len( filename) > 8:
                    filename= filename[:8]+u'\u2026'
                self.SetText= filename
                dlg.Destroy()
                return fullPath
        finally:
            evt.Skip()

    def undo(self,evt):
        self.Undo()
        evt.Skip()

    def redo(self,evt):
        self.Redo()
        evt.Skip()

    def CutSelection(self, evt):
        self.Cut()
        evt.Skip()

    def CopySelection(self, evt):
        self.Copy()
        evt.Skip()

    def PasteSelection(self, evt):
        self.Paste()
        evt.Skip()

    def newScript(self, evt):
        self.addPage()
        evt.Skip()

    def Destroy(self):
        self.m_mgr.UnInit()
        super( ScriptPanel, self).Destroy()
