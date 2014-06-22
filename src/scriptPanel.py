import threading
import sys
import os
import wx
import wx.grid as gridlib
import inspect
import types
from wx.stc import EVT_STC_CHANGE
from wx.py.editwindow import EditWindow
from wx.py.filling import Filling, SIMPLETYPES, FillingTree, FillingText
from wx.py.shell import Shell
from wx.py.interpreter import Interpreter
from wx.py.crust import SessionListing
from wx.py import introspect
from wx.py import dispatcher
  
from pyext.curry import CurryAppend, ObjectFactory
from pyext.decorators import nested_property
from pyext.proxy import ScriptProxy, DynamicReference, GetMember, script_api
from pyext.moduleDescriptor import ModuleDescriptor
from pyext.docstring import DocString
from wxappext.assoc import StandardDocTemplate
from wxappext.stddocmgr import StandardDocManager, docview
from wxappext.stddoc import StandardDocument, SimpleFormatter
from wxappext.stdview import StandardView
from wxappext.xrcext import ConfiguredXMLHandler
from wxappext.stdevents import EVT_ITEM_SELECTION_CHANGED
from wxappext.stdselection import *
from wxappext.rtext import RichTextCtrlEx
from wx.richtext import RichTextAttr
  
class ScriptInterpreter(Interpreter):
    def __init__(self, locals=None, showInterpIntro=True, *args, **kwds):
        Interpreter.__init__(self, locals=locals, 
            showInterpIntro=showInterpIntro, *args, **kwds)
        if self.introText:
            self.introText = self.introText.split(os.linesep)[0]
  
    def _getAttributeNames(self, object, includeMagic, includeSingle,
        includeDouble):
        attributes = introspect.getAttributeNames(object, includeMagic,
            includeSingle, includeDouble)
        if isinstance(object, ScriptProxy):
            proxyMembers = object.Members
            if not (includeDouble and includeSingle):                
                private = set([m for m in object.Members if m.startswith('_')])
                veryPrivate = set([m for m in private if m.startswith('__')])
                private -= veryPrivate
                if not includeDouble:
                    proxyMembers -= veryPrivate
                if not includeSingle:
                    proxyMembers -= private
            attributes = sorted(list(proxyMembers.union(attributes)))
        return attributes
  
    def _getRoot(self, command, locals):
        root = introspect.getRoot(command, terminator='.')
        if locals is not None:
            object = eval(root, locals)
        else:
            object = eval(root)
        if isinstance(object, DynamicReference):
            object = object.getReferencedObject()
        return object
  
    def getAutoCompleteList(self, command='', *args, **kwds):
        """Return list of auto-completion options for a command.
  
        The list of options will be based on the locals namespace."""
        attributes = []
        stdin, stdout, stderr = sys.stdin, sys.stdout, sys.stderr
        sys.stdin, sys.stdout, sys.stderr = \
                   self.stdin, self.stdout, self.stderr
        try:
            object = self._getRoot(command, self.locals)
        except:
            pass
        else:
            attributes = self._getAttributeNames(object, 
                kwds['includeMagic'], kwds['includeSingle'],
                kwds['includeDouble'])
        sys.stdin, sys.stdout, sys.stderr = stdin, stdout, stderr
        return attributes
  
class ShellDocument(StandardDocument):
    def __init__(self, scriptInterfaceName='ShellDocument'):
        self._interpreter = None
        StandardDocument.__init__(self, scriptInterfaceName)
  
    def GetModel(self):
        return ''
  
class ShellView(StandardView):
    def __init__(self, includeMagic=True, includeSingle=True,
        includeDouble=True, scriptInterfaceName='ShellView'):
        self._shell = None
        self._shellSplitter = None
        self._filling = None       
        self._namespaceViewer = None
        self._autoCompleteOptions = {'magic': bool(includeMagic),
                                     'single': bool(includeSingle),
                                     'double': bool(includeDouble)}
        StandardView.__init__(self, scriptInterfaceName)
  
    def _CreateFinalize(self):
        self.AutoCompleteIncludeMagic = self._autoCompleteOptions['magic']
        self.AutoCompleteIncludeSingle = self._autoCompleteOptions['single']
        self.AutoCompleteIncludeDouble = self._autoCompleteOptions['double']
  
    def _GetComponentsFromFrame(self, frame):
        self._shell = frame.FindWindowByName('shell')
        self._shellSplitter = frame.FindWindowByName('shellSplitter')
        self._filling = frame.FindWindowByName('filling')
        self._namespaceViewer = frame.FindWindowByName('namespace')
  
    def _GetCustomXRCHandlers(self):
        # TODO: Make the option to use the default namespace (__main__.__dict__)
        # a configurable option
        scriptingService = wx.GetApp().Services.get('Scripting', None)
        if scriptingService:
            # TODO: Fix this hack (invoking a private method)
            namespace = scriptingService.Host._GetScriptGlobals()
        else:
            namespace = None
##        return [ShellXmlHandler(namespace=namespace), 
##                NamespaceXmlHandler(namespace=namespace),
##                ShellHistoryXmlHandler()]
        return [ShellXmlHandler(namespace=namespace), 
                NamespaceXmlHandler(namespace=namespace)]
  
    def _GetFrameXRC(self):
        """
        Return a tuple with the path and resource name that defines
        the frame.
        """
        return ("shell.xrc", "shellPanel")
  
    @nested_property
    def AutoCompleteIncludeDouble():
        def _fget(self):
            return self._shell.autoCompleteIncludeDouble
        def _fset(self, value):
            self._shell.autoCompleteIncludeDouble = value
        return locals()
  
    @nested_property
    def AutoCompleteIncludeMagic():
        def _fget(self):
            return self._shell.autoCompleteIncludeMagic
        def _fset(self, value):
            self._shell.autoCompleteIncludeMagic = value
        return locals()
  
    @nested_property
    def AutoCompleteIncludeSingle():
        def _fget(self):
            return self._shell.autoCompleteIncludeSingle
        def _fset(self, value):
            self._shell.autoCompleteIncludeSingle = value
        return locals()
  
EVT_MODULE_THREAD_NOTIFY_ID = wx.NewId()
ModuleThreadNotifyEventType = wx.NewEventType() 
EVT_MODULE_THREAD_NOTIFY = wx.PyEventBinder(ModuleThreadNotifyEventType) 
"""Notify module documents when the list of a module's attributes changes."""
  
class _ModuleThreadNotifyEvent(wx.PyEvent):
    """
    Represent details of the event sent when the list of top-level attributes
    the active ModuleDocument changes.
    """
  
    def __init__(self, document, moduleDirectory): 
        """
        Create a _ModuleThreadNotifyEvent instance.
  
        """
        wx.PyEvent.__init__(self, ModuleThreadNotifyEventType)
        self.SetEventType(EVT_MODULE_THREAD_NOTIFY_ID)
        self.moduleDirectory = moduleDirectory
        self.SetEventObject(document)
  
ModuleAttributesChangedEventType = wx.NewEventType() 
EVT_MODULE_ATTRIBUTES_CHANGED = wx.PyEventBinder(ModuleAttributesChangedEventType) 
"""Notify client objects when the list of a module's attributes changes."""
  
class ModuleAttributesChangedEvent(wx.PyCommandEvent):
    """
    Represent details of the event sent when the list of top-level attributes
    the active ModuleDocument changes.
    """
  
    def __init__(self, document, moduleDirectory): 
        """
        Create a ModuleAttributesChangedEvent instance.
  
        """
        wx.PyCommandEvent.__init__(self, ModuleAttributesChangedEventType)
        self.moduleDirectory = moduleDirectory
        self.SetEventObject(document)
  
ModuleSelectionChangedEventType = wx.NewEventType()
EVT_MODULE_SELECTION_CHANGED = wx.PyEventBinder(ModuleSelectionChangedEventType)
"""Notify client objects when the selection in a module edit window changes."""
  
class ModuleSelectionChangedEvent(wx.PyCommandEvent):
    """
    Represent details of the event sent when the selection in a module edit
    window changes.
    """
  
    def __init__(self, start, end, line, column):
        """
        Create a ModuleSelectionChangedEvent instance.
        """
        wx.PyCommandEvent.__init__(self, ModuleSelectionChangedEventType)
        self._start, self._end, self._line, self._column = (start, end, 
            line, column)
  
    @nested_property
    def Column():
        def _fget(self):
            return self._column
        return locals()
  
    @nested_property
    def EndPosition():
        def _fget(self):
            return self._end
        return locals()
  
    @nested_property
    def LineNumber():
        def _fget(self):
            return self._line
        return locals()
  
    @nested_property
    def StartPosition():
        def _fget(self):
            return self._start
        return locals()
  
  
class ModuleAttributesWorkerThread(threading.Thread):
    def __init__(self, document):
        threading.Thread.__init__(self)
        self._document = document
        self.start()
  
    def run(self):
        # TODO: if module has unsaved data, write it to a temp file
        moduleFilename = self._document.GetFilename()
        moduleDescriptor = ModuleDescriptor(moduleFilename)
        wx.PostEvent(self._document, _ModuleThreadNotifyEvent(self._document,
            moduleDescriptor))
  
class ModuleDocument(StandardDocument):
    def __init__(self, scriptInterfaceName='ModuleDocument'):
        StandardDocument.__init__(self, scriptInterfaceName)
        self._getTextFunc = None
        self._setTextFunc = None
        self._moduleDirectory = {}
        self._moduleDirectoryWorker = None
        self._BindEvents()
  
    def _BindEvents(self):
        self.Connect(-1, -1, EVT_MODULE_THREAD_NOTIFY_ID, 
            self._OnModuleDirectoryChanged)
  
    def _OnModuleDirectoryChanged(self, event):
        self._moduleDirectory = event.moduleDirectory
        self._moduleDirectoryWorker = None
        wx.EvtHandler.ProcessEvent(self, ModuleAttributesChangedEvent(self, 
            self._moduleDirectory))
  
    def _UpdateModuleDirectory(self):
        if not self._moduleDirectoryWorker:
            self._moduleDirectoryWorker = ModuleAttributesWorkerThread(self)
  
    @script_api(recordable=False)
    @nested_property
    def AttributeDirectory():
        """
        Return a L{ModuleDescriptor<pyext.moduleDescriptor.ModuleDescriptor>}
        object that describes the functions, classes and methods in the
        module.
        """
        def _fget(self):
            return self._moduleDirectory
        return locals()
  
    def GetFormatter(self):
        return SimpleFormatter()    
  
    def GetModel(self):
        return self._getTextFunc()
  
    def SetTextGetSetFunctions(self, getTextFunction, setTextFunction):
        """
        Set the function to invoke to retrieve the module's text from its
        editor control. This method is meant for the view to invoke.
        """
        self._getTextFunc = getTextFunction
        self._setTextFunc = setTextFunction
        if self._model:
            self.SetModel(self._model)
  
    def SetModel(self, model):
        """
        Set the model object that represents the serializable document
        data.
        """
        if self._setTextFunc:
            self._setTextFunc(model)
            self._UpdateModuleDirectory()
            # clear the value that we may have stored temporarily the
            # first time this method was invoked
            self._model = None
        else:
            # store the model temporarily, until the text functions are set
            self._model = model
  
class ModuleView(StandardView):
    def __init__(self, scriptInterfaceName='ModuleView'):
        StandardView.__init__(self, scriptInterfaceName)
        self._editWindow = None
        self._codeNavigator = None
        self._selection = None
  
    def _ActivateFinalize(self):
        self._editWindow.SetFocus()
  
    def _codeNavigator_ItemSelectionChanged(self, evt):
        self.GotoCode(evt.GetSelectedItemText())
  
    def _editWindowTextChanged(self, evt):
        self.GetDocument().Modify(True)
  
    def _ConnectDocumentToChildren(self):
        self._UpdateCodeNavigator()
  
    def _CreateFinalize(self):
        """
        Initialize view members after creation of the view and its children.
        """
        if self._editWindow:
            self.GetDocument().SetTextGetSetFunctions(self._editWindow.GetText, 
                self._editWindow.SetText)
            self._selection = ModuleSelection(self)
            self._selection.Bind(EVT_SELECTION_CHANGED, self._OnSelectionChanged)
  
            # TODO: Route these to the appropriate EditWindow methods
##            selection.Bind(cellselection.EVT_SELECTION_CAN_CLEAR, 
##                self._CellSelection_CanClear)
##            # same handler for copy and cut
##            selection.Bind(cellselection.EVT_SELECTION_CAN_COPY, 
##                self._CellSelection_CanCopy)
##            selection.Bind(cellselection.EVT_SELECTION_CAN_CUT, 
##                self._CellSelection_CanCopy)
##            selection.Bind(cellselection.EVT_SELECTION_CAN_PASTE, 
##                self._CellSelection_CanPaste)
            self._selection.Bind(EVT_SELECTION_CLEARED,
                lambda evt: self._editWindow.Clear())
            self._selection.Bind(EVT_SELECTION_COPIED, 
                lambda evt: self._editWindow.Copy())
            self._selection.Bind(EVT_SELECTION_CUT, 
                lambda evt: self._editWindow.Cut())
            self._selection.Bind(EVT_SELECTION_PASTED, 
                lambda evt: self._editWindow.Paste())
  
  
            self._editWindow.Bind(EVT_STC_CHANGE, self._editWindowTextChanged)
        self.GetDocument().Bind(EVT_MODULE_ATTRIBUTES_CHANGED, 
            self._OnModuleDirectoryChanged)
        if self._codeNavigator:
            self._codeNavigator.Bind(EVT_ITEM_SELECTION_CHANGED, 
                self._codeNavigator_ItemSelectionChanged)
  
    def _GetComponentsFromFrame(self, frame):
        self._editWindow = frame.FindWindowByName('editWindow')
        self._codeNavigator = frame.FindWindowByName('CodeNavigator')
  
##    def _GetCustomXRCHandlers(self):
##        return [EditWindowXmlHandler()]
  
    def _GetFrameXRC(self):
        """
        Return a tuple with the path and resource name that defines
        the frame.
        """
        return ("module.xrc", "modulePanel")
  
    def _GetSelection(self):
        return self._selection
  
    def _OnModuleDirectoryChanged(self, event):
        self._UpdateCodeNavigator()
        event.Skip()
  
    def _OnSelectionChanged(self, event):
        event.Skip()
  
    def _UpdateCodeNavigator(self):
        if self._codeNavigator:
            self._codeNavigator.SetValue(self.GetDocument().ScriptInterface)
  
    def BindEditWindowEvent(self, eventType, handler):
        if self._editWindow:
            self._editWindow.Bind(eventType, handler)
  
    @script_api(recordable=True)
    @nested_property
    def DisplayLineNumbers():
        """
        Return or set display of line numbers in the editor window.
        """
        def _fget(self):
            return self._editWindow.lineNumbers
        def _fset(self, value):
            self._editWindow.lineNumbers = value
            self._editWindow.setDisplayLineNumbers(value)
        return locals()
  
    @script_api(recordable=False)
    def GetCodeStartLine(self, identifier):
        """
        Return the 1-based starting line number of the code block specified by
        identifier. To specify a top-level code block such as function
        Foo, identifier should be either C{"(module).Foo"} or
        C{"Foo"}. To specify a method of a class, identifier should be
        C{"classname.methodname"}.
        """
        normalizedIdentifier = identifier.replace('(module).', '')
        if '.' in normalizedIdentifier:
            moduleAttribute, classAttribute = normalizedIdentifier.split('.')
        else:
            moduleAttribute, classAttribute = \
                (normalizedIdentifier and normalizedIdentifier or None, None)
        return self.GetDocument().AttributeDirectory.GetAttributeStartLine(moduleAttribute, 
            classAttribute)
  
    def GotoCode(self, identifier):
        """
        Go to the first line of the code block specified by
        identifier. To specify a top-level code block such as function
        Foo, identifier should be either C{"(module).Foo"} or
        C{"Foo"}. To specify a method of a class, identifier should be
        C{"classname.methodname"}.
        """
        start = self._editWindow.GetSelectionStart()
        currentLine = self._editWindow.LineFromPosition(start)
        line = self.GetCodeStartLine(identifier)
        if line:
            currentLine = line
            start = self.GotoLine(line)
        return (currentLine, start)
  
    def GotoLine(self, line):
        """
        Set the cursor to the beginning of the specified line and scroll
        the line into view, if necessary. Line numbers start at 1.
        """
        # Scintilla line numbers start at 0
        line -= 1
        self._editWindow.GotoLine(line)
        # Position the line at the top of the window
        topLineOffset = line - self._editWindow.GetFirstVisibleLine()
        if topLineOffset > 0:
            self._editWindow.LineScroll(0, topLineOffset)
        self._editWindow.SetFocus()
        return self._editWindow.GetSelectionStart()
  
    @script_api(recordable=True)
    @nested_property
    def WrapLines():
        """
        Return or set whether to wrap lines in the editor window.
        """
        def _fget(self):
            return self._editWindow.GetWrapMode()
        def _fset(self, value):
            self._editWindow.SetWrapMode(value)
        return locals()
  
class ModuleSelection(StandardSelection):
    """
    Represent the selected text in a module editor.
    """
  
    def __init__(self, view):
        """
        Initialize the ModuleSelection object.
  
        view: the ModuleView object whose text selection the 
        ModuleSelection object represents.
        """
  
        self._view = view
        self._selectedRange = []
        self._eventHandler = {}
        self._start = -1
        self._end = -1
        self._line = 0
        self._column = -1
        self._moduleAttribute = ''
        self._classAttribute = ''
        StandardSelection.__init__(self)
  
    def _BindEvents(self):
        self._view.BindEditWindowEvent(EVT_MODULE_SELECTION_CHANGED, 
            self._editWindow_SelectionChanged)            
        self._GetDocument().Bind(EVT_MODULE_ATTRIBUTES_CHANGED, 
            self._OnModuleDirectoryChanged)
  
    def _editWindow_SelectionChanged(self, event):
        self._column = event.Column
        start, end, line = (event.StartPosition, event.EndPosition, event.LineNumber + 1)
        if (self._start, self._end, self._line) != (start, end, line):
            self._start, self._end, self._line = (start, end, line)
            self._GetCurrentModuleAttributes()
            self._NotifyModuleSelectionChanged()
        event.Skip()
  
    def _GetCurrentModuleAttributes(self):
        directory = self.Document.AttributeDirectory
        myModuleName = self.Document.GetFilename()
        if directory:
            moduleAttribute, classAttribute = directory.GetAttributeAtLine(self.LineNumber)
            self._moduleAttribute = moduleAttribute and moduleAttribute or '(module)'
            self._classAttribute = classAttribute and classAttribute or ''
  
    def _GetDocument(self):
        return self._view.GetDocument()        
  
    def _GetView(self):
        return self._view
  
    def _NotifyModuleSelectionChanged(self):
        self._ProcessEvent(SelectionChangedEvent(self))
  
    def _OnModuleDirectoryChanged(self, event):
        self._GetCurrentModuleAttributes()
        event.Skip()
  
    @script_api(recordable=False)
    @nested_property
    def ClassAttribute():
        """
        Return the name of class method definition where the cursor is.
        """
        def _fget(self):
            return self._classAttribute
        return locals()
  
    @script_api(recordable=False)
    @nested_property
    def Column():
        """
        Return the 0-based column number of the start of the selection.
        """
        def _fget(self):
            return self._column
        return locals()
  
    @script_api(recordable=False)
    @nested_property
    def End():
        """
        Return the 0-based position of the end of the selection.
        """
        def _fget(self):
            return self._end
        return locals()
  
    @script_api(recordable=False)
    @nested_property
    def LineNumber():
        """
        Return the 1-based number of the current line.
        """
        def _fget(self):
            return self._line
        return locals()
  
    @script_api(recordable=False)
    @nested_property
    def ModuleAttribute():
        """
        Return the name of the class or function definition where the
        cursor is.
        """
        def _fget(self):
            return self._moduleAttribute
        return locals()
  
    @script_api(recordable=False)
    @nested_property
    def Position():
        """
        Return a tuple of the 0-based start and end positions of the selection.
        """
        def _fget(self):
            return (self._start, self._end)
        return locals()
  
    @script_api(recordable=False)
    @nested_property
    def Start():
        """
        Return the 0-based position of the start of the selection.
        """
        def _fget(self):
            return self._start
        return locals()
  
    @script_api(recordable=True)
    def GotoCode(self, identifier):
        """
        Go to the first line of the code block specified by
        identifier. To specify a top-level code block such as function
        Foo, identifier should be either C{"(module).Foo"} or
        C{"Foo"}. To specify a method of a class, identifier should be
        C{"classname.methodname"}.
  
        This method does not cause the EVT_SELECTION_CHANGED event to fire.
        """
        self.GotoLine(self._view.GetCodeStartLine(identifier))
  
    @script_api(recordable=True)
    def GotoLine(self, lineNumber):
        """
        Set the cursor to the beginning of the specified line and scroll
        the line into view, if necessary.
  
        This method does not cause the EVT_SELECTION_CHANGED event to fire.
  
        @param lineNumber: the line to go to, with line numbers starting at 1
        """
        self._line = lineNumber
        self._start, self._end = [self._view.GotoLine(lineNumber)] * 2
  
class ModuleEditWindow(EditWindow):
  
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.CLIP_CHILDREN | wx.SUNKEN_BORDER):
        EditWindow.__init__(self, parent, id=id, pos=pos, size=size, 
            style=style)
        self._selection = (-1, -1)
  
    def OnUpdateUI(self, event):
        super(ModuleEditWindow, self).OnUpdateUI(event)
        selection = self.GetSelection()
        if selection != self._selection:
            wx.EvtHandler.ProcessEvent(self, 
                ModuleSelectionChangedEvent(selection[0], selection[1],
                    self.LineFromPosition(selection[0]), 
                    self.GetColumn(selection[0])))
            self._selection = selection
  
class ObjectInfo(object):
    def __init__(self, obj, name, objParent=None):
        self.type = type(obj)
        self.name = name
        self.value = self._GetObjectValue(obj)
        self.isProperty = False
        self.documentedMember = self._GetDocumentedMember(obj,
            objParent, name)
        self.docString = self._GetDocstring(self.documentedMember)
        self.isMethod = False
        self.argumentNames = self._GetArgumentNames(obj)
  
    def _GetArgumentNames(self, obj):
        result = []
        if hasattr(obj, 'im_func'):
            func = getattr(obj, 'im_func', obj)
            self.isMethod = True
        else:
            func = obj
        # skip the self argument if it's a method
        firstArg = self.isMethod and 1 or 0
        if hasattr(func, '__argnames__'):
            # special case for functions decorated by 
            # pyext.decorators.simple_decorator
            argnames = func.__argnames__
            if len(argnames) > firstArg:
                result = argnames[firstArg:]
        else:
            funcCode = getattr(func, 'func_code', None)
            if funcCode:
                # skip the self argument if it's a method
                firstArg = self.isMethod and 1 or 0
                if funcCode.co_argcount > firstArg:
                    result = funcCode.co_varnames[firstArg:funcCode.co_argcount]
        return result
  
    def _GetDocumentedMember(self, obj, objParent, name):
        # if obj is returned by a property, get the
        # docstring of the property
        documentedMember = obj
        if objParent and isinstance(objParent, object):
            parentMember = GetMember(objParent, name.split('.')[-1])
            if parentMember:
                documentedMember = parentMember
                self.isProperty = True
        return documentedMember
  
    def _GetDocstring(self, obj):
        # Return a DocString object that represents the structured content
        # in the docstring associated with the specified object.
        docstring = None
        if type(obj) not in SIMPLETYPES:
            docstring = DocString(obj)
        return docstring
  
    def _GetObjectValue(self, obj):
        otype = type(obj)
        value = ''
        if otype is not types.MethodType:
            try:
                value = str(obj)
            except:
                value = ''
            if otype is types.StringType or otype is types.UnicodeType:
                value = repr(obj)
        return value
  
class DocStringViewer(RichTextCtrlEx):
    def __init__(self, *args, **kwargs):
        RichTextCtrlEx.__init__(self, *args, **kwargs)
        self._CreateStyles()
        self._objectInfo = None
  
    def _CreateStyles(self):
        # TODO: add a style sheet when wxPython supports it
        self.summaryStyle = RichTextAttr()
        self.summaryStyle.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        self.summaryStyle.SetParagraphSpacingAfter(20)
  
        self.syntaxStyle = RichTextAttr()
        self.syntaxStyle.SetFontWeight(wx.FONTWEIGHT_BOLD)
        self.syntaxStyle.SetParagraphSpacingAfter(20)
  
        self.normalChar = RichTextAttr()
        self.normalChar.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        self.normalChar.SetFontStyle(wx.FONTSTYLE_NORMAL)
  
        self.variableStyle = RichTextAttr()
        self.variableStyle.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        self.variableStyle.SetFontStyle(wx.FONTSTYLE_ITALIC)
  
        self.argDocStyle = RichTextAttr()
        self.argDocStyle.SetLeftIndent(20, 170)
        self.argDocStyle.SetTabs([200] + [200+(100 * x) for x in range(1, 5)])
  
    def _GetFormattedObjectInfo(self):
        def _SummaryParagraphs():
            summary = '%s\n' % (self._objectInfo.docString and \
                self._objectInfo.docString.Summary or '(Undocumented)', )
            yield self.Block(summary, self.summaryStyle)
  
        def _SyntaxElements():
            #inst
            if self._objectInfo.isMethod or self._objectInfo.isProperty:
                yield [('inst', self.variableStyle), '.']
            #short name
            yield self._objectInfo.name.split('.')[-1]
            #method elements
            if self._objectInfo.isMethod:
                # each arg name is in 'variable' style; the
                # commas separating them and the parentheses surrounding
                # them are in the paragraph's style
                argListBlocks = self.Block(', ').Join(((argName, 
                    self.variableStyle) for argName in \
                        self._objectInfo.argumentNames))
                yield(['(', argListBlocks, ') '])
            yield '\n'
  
        if self._objectInfo and self._objectInfo.docString:
            # Syntax paragraph
            yield ((block for block in _SyntaxElements()), self.syntaxStyle)
  
            # Summary paragraph(s)
            yield (block for block in _SummaryParagraphs())
  
            if self._objectInfo.isMethod:
                argumentDescriptions = self._objectInfo.docString.ArgumentDescriptions
                # Argument paragraphs
                # each arg name is in 'argument' style
                argBlocks = ([(arg, self.variableStyle), 
                    ':\t%s\n' % argumentDescriptions.get(arg, '?')] for arg \
                    in self._objectInfo.argumentNames)
                yield (argBlocks, self.argDocStyle)
  
    def _RenderObjectInfo(self):            
        self.Clear()
        self.EndAllStyles()
        if self._objectInfo and self._objectInfo.docString:    
            self.Block(self._GetFormattedObjectInfo()).WriteStyled()
  
  
    @nested_property
    def ObjectInfo():
        """
        Return or set the ObjectInfo object that represents the object
        to display.
        """
        def _fget(self):
            return self._objectInfo
        def _fset(self, value):
            self._objectInfo = value
            self._RenderObjectInfo()
        return locals()
  
class NamespaceText(wx.Panel):
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.CLIP_CHILDREN,
                 name='NamespaceText', static=False):
        """Create NamespaceText instance."""
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size,
            style=style, name=name)
        self._objectInfo = None
  
        self._rtc = self._CreateTextControl()
        self._grid = self._CreateGridControl()
        self._DoLayout()
  
        self._ApplySettings()
        self.Bind(wx.EVT_SIZE, self._OnSize)
        if not static:
            dispatcher.connect(receiver=self.push, signal='Interpreter.push')
            dispatcher.connect(receiver=self.display, signal='NamespaceTree.display')
  
    def _ApplySettings(self):
        self._rtc.SetEditable(False)
##        self.SetWrapMode(True)
##        self.SetMarginWidth(1, 0)
  
    def _CreateGridControl(self):
        grid = gridlib.Grid(self)
        grid.SetScrollLineX(1)
        grid.SetMargins(0, 0)
        grid.SetColLabelSize(0)
        grid.SetRowLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        grid.CreateGrid(3, 1)
        attr = grid.GetOrCreateCellAttr(0, 0)
        attr.SetReadOnly(True)
        grid.SetColAttr(0, attr)
        grid.SetLabelBackgroundColour(wx.WHITE)
        grid.SetRowLabelValue(0, 'Name')
        grid.SetRowLabelValue(1, 'Type')
        grid.SetRowLabelValue(2, 'Value')
        return grid
  
    def _OnSize(self, evt):
        # Resize the info column in the grid to fill available space
        width = evt.GetSize().GetWidth()
        defaultColSize = (width - self._grid.GetRowLabelSize()) - 4
        self._grid.SetDefaultColSize(defaultColSize, resizeExistingCols=True)
        evt.Skip()
  
    def _CreateTextControl(self):
        rtc = DocStringViewer(self)
        return rtc
  
    def _DoLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._grid, 1, wx.EXPAND)
        sizer.Add(self._rtc, 2, wx.EXPAND)
        self.SetSizer(sizer)
  
    def _SetGridContents(self, objectInfo=None):
        self._grid.ClearGrid()
        if objectInfo:
            self._grid.SetCellValue(0, 0, objectInfo.name)
            self._grid.SetCellValue(1, 0, str(objectInfo.type))
            self._grid.SetCellValue(2, 0, str(objectInfo.value))
            self._grid.AutoSizeRow(2, setAsMin=False)
  
    def display(self, objectInfo=None):
        """Receiver for NamespaceTree.display signal."""
        self.ObjectInfo = objectInfo
  
    @nested_property
    def ObjectInfo():
        def _fget(self):
            return self._objectInfo
        def _fset(self, value):
            self._objectInfo = value
##            self._RenderObjectInfo()
            self._rtc.ObjectInfo = value
            self._SetGridContents(self._objectInfo)        
        return locals()
  
    def push(self, command, more):
        """Receiver for Interpreter.push signal."""
        self.Refresh()
  
    def SetText(self, *args, **kwds):
        self._rtc.SetEditable(True)
        self._rtc.Clear()
        self._rtc.AppendText(*args, **kwds)
        self._rtc.SetEditable(False)
  
class NamespaceTree(FillingTree):
    """
    Display details about the namespace in a scripting environment.
    """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
        size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE,
        rootObject=None, rootLabel=None, rootIsNamespace=False,
        static=False):
        # If the Scripting service is enabled, allow it to determine
        # which objects and members to show in the namespace.
        # Set this filter before initializing the base class, because
        # the base class init method populates the tree.
        scriptingService = wx.GetApp().Services.get('Scripting', None)
        if scriptingService:
            self._memberFilterFunc = scriptingService.GetNamespaceFilter()
        else:
            self._memberFilterFunc = None
        FillingTree.__init__(self, parent, id=id, pos=pos, size=size, 
            style=style, rootObject=rootObject, rootLabel=rootLabel, 
            rootIsNamespace=rootIsNamespace, static=static)
  
    def _GetNamespaceObject(self, item):
        # Return the object associated with the item in the tree. If
        # the object is a DynamicReference, return the object that
        # it currently refers to.
        obj = self.GetPyData(item)
        if isinstance(obj, DynamicReference):
            try:
                obj = obj.getReferencedObject()
            except:
                obj = None
        return obj
  
    def _GetDocstring(self, obj):
        # Return a DocString object that represents the structured content
        # in the docstring associated with the specified object.
        docstring = None
        if type(obj) not in SIMPLETYPES:
            docstring = DocString(obj)
        return docstring
  
    def _GetObjectInfo(self, item, obj, objParent):
        # Return an ObjectInfo with details about the specified object.
        objectInfo = ObjectInfo(obj, self.getFullName(item), objParent)
        return objectInfo
  
    def _PopulateTree(self, item, obj):
        if self.IsExpanded(item):
            self.addChildren(item)
        if obj is not None:
            self.SetItemHasChildren(item, self.objHasChildren(obj))
  
    def display(self):
        item = self.item
        if not item:
            return
        obj = self._GetNamespaceObject(item)
        self._PopulateTree(item, obj)
  
        if wx.Platform == '__WXMSW__':
            if obj is None: # Windows bug fix.
                return
        itemParent = self.GetItemParent(item)
        objParent = itemParent and self._GetNamespaceObject(itemParent) or None
        objectInfo = self._GetObjectInfo(item, obj, objParent)
        dispatcher.send(signal='NamespaceTree.display', sender=self,
                        objectInfo=objectInfo)
  
    def objGetChildren(self, obj):
        if isinstance(obj, DynamicReference):
            # if the object is a dynamic reference, execute the dynamic
            # query to get the object (whatever it is at this moment)
            # and inspect that.
            try:
                obj = obj.getReferencedObject()
            except Exception, e:
                sys.stderr.write("%s in NamespaceTree.objGetChildren ignored\n" % str(e))
        children = dict(super(NamespaceTree, self).objGetChildren(obj))
        if self._memberFilterFunc:
            children = self._memberFilterFunc(obj, children)
        return children
  
  
class NamespaceViewer(wx.SplitterWindow):
    # We can't just subclass the py.Filling object, because its constructor
    # creates child windows directly, and we want to substitute our own
    # different window for the FillingText.
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
        size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE, name='NamespaceViewer',
        rootObject=None, rootLabel=None, rootIsNamespace=False,
        static=False):
        """Create a NamespaceViewer instance."""
  
        wx.SplitterWindow.__init__(self, parent, id, pos, size, style, name)
  
        self.tree = self._CreateFillingTree(rootObject, rootLabel, 
            rootIsNamespace, static)
        self.text = self._CreateFillingText(static=static)
  
        wx.FutureCall(1, self.SplitVertically, self.tree, self.text, 200)
  
        self.SetMinimumPaneSize(1)
  
        # Override the filling so that descriptions go to FillingText.
        self.tree.setText = self.text.SetText
  
        # Display the root item.
        self.tree.SelectItem(self.tree.root)
        self.tree.display()
  
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnChanged)                 
  
    def _CreateFillingText(self, static):
        return NamespaceText(parent=self, static=static)
  
    def _CreateFillingTree(self, rootObject, rootLabel, rootIsNamespace, static):
        return NamespaceTree(parent=self, rootObject=rootObject,
            rootLabel=rootLabel, rootIsNamespace=rootIsNamespace,
            static=static)        
  
    def OnChanged(self, event):
        #this is important: do not evaluate this event=> otherwise, splitterwindow behaves strange
        #event.Skip()
        pass
  
    def LoadSettings(self, config):
        pos = config.ReadInt('Sash/FillingPos', 200)
        wx.FutureCall(250, self.SetSashPosition, pos)
        zoom = config.ReadInt('View/Zoom/Filling', -99)
        if zoom != -99:
            self.text.SetZoom(zoom)
  
    def SaveSettings(self, config):
        config.WriteInt('Sash/FillingPos', self.GetSashPosition())
        config.WriteInt('View/Zoom/Filling', self.text.GetZoom())
  
class ShellXmlHandler(ConfiguredXMLHandler):
    """
    Create L{wx.py.shell.Shell} windows defined in Xrc resource files.
    """
  
    def __init__(self, namespace=None):
        """
        Create an ShellXmlHandler instance.
        """
        self._namespace = namespace
        ConfiguredXMLHandler.__init__(self, "Shell")
  
    def _CreateResourceInstance(self, instance, parent, id=-1, 
        pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name='Shell'):
        assert instance is None
        control = Shell(parent, id, pos=pos, size=size,
            style=style, locals=self._namespace, InterpClass=ScriptInterpreter)
        if name:
            control.SetName(name)
        return control
  
class NamespaceXmlHandler(ConfiguredXMLHandler):
    """
    Create L{wx.py.filling.Filling} windows defined in Xrc resource files.
    """
  
    def __init__(self, namespace=None):
        """
        Create an NamespaceXmlHandler instance.
        """
        self._namespace = namespace
        ConfiguredXMLHandler.__init__(self, "Namespace")
  
    def _CreateResourceInstance(self, instance, parent, id=-1, 
        pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name='Namespace'):
        assert instance is None
        rootObject, rootLabel, rootIsNamespace = self._namespace and (self._namespace, 
            wx.GetApp().GetAppName(), True) or (None, None, False)
        control = NamespaceViewer(parent, id, pos=pos, size=size,
            style=style, rootObject=rootObject, rootLabel=rootLabel,
            rootIsNamespace=rootIsNamespace)
        if name:
            control.SetName(name)
        return control
  
class PyModuleTemplateFactory(CurryAppend):
    """
    Create instances of StandardDocTemplate objects, using an interface
    that mimics the calling signature of the StandardDocTemplate constructor.
    The resulting StandardDocTemplate objects are configured for creating
    L{ModuleDocument} objects displayed in L{ModuleView} objects.
    The caller of a PyModuleTemplateFactory instance will supply
    the docManager, containerConfig and templateConfig arguments. The 
    instance will supply additional arguments that the StandardDocTemplate
    constructor requires.
    """
    def __init__(self, description='Custom Scripts', directory='scripts', 
        docTypeName='Script', viewTypeName='Code View', 
        icon=None, scriptInterfaceName=None):
        from wxappext.assoc import StandardDocTemplate
        CurryAppend.__init__(self, StandardDocTemplate, description, "*.py",
            directory, ".py", docTypeName, viewTypeName, 
            ModuleDocument, ModuleView, icon=icon,
            scriptInterfaceName=scriptInterfaceName)
  
class PyShellTemplateFactory(CurryAppend):
    """
    Create instances of StandardDocTemplate objects, using an interface
    that mimics the calling signature of the StandardDocTemplate constructor.
    The resulting StandardDocTemplate objects are configured for creating
    L{ShellDocument} objects displayed in L{ShellView} objects.
    The caller of a PyShellTemplateFactory instance will supply
    the docManager, containerConfig and templateConfig arguments. The 
    instance will supply additional arguments that the StandardDocTemplate
    constructor requires.
    """
    def __init__(self):
        from wxappext.assoc import StandardDocTemplate
        CurryAppend.__init__(self, StandardDocTemplate, 'InteractiveShell',
            '', '', '', 'ShellDocument', 'Shell', ShellDocument,
            ObjectFactory(ShellView, includeDouble=0, includeSingle=0),
            scriptInterfaceName='Shell', 
            flags=(docview.TEMPLATE_NO_CREATE ^ docview.TEMPLATE_VISIBLE) | \
                docview.TEMPLATE_INVISIBLE)
  
class WorkspaceTemplate(StandardDocTemplate):
    """
    Define the document and view configuration for a standard scripting
    environment. The environment uses a compound document that represents
    a script project, which can host multiple modules of various types.
    The environment's view contains a tree view of the project's modules,
    organized by type. The open modules display in a tabbed notebook. The
    view also displays a shell window and a namespace explorer.
    """
    def __init__(self, docManager, containerConfig, templateConfig,
        workspaceExtension, directory, icon, scriptTemplateFactories):
        """
        Create a new WorkspaceTemplate instance.
  
        @param docManager: the 
            L{StandardDocManager<stddocmgr.StandardDocManager>} object that
            manages document/view instances created from this template
        @param containerConfig: the 
            L{DocumentTemplateConfig<wxappext.config.sections.DocumentTemplateConfig>}
            object that represents the configuration for the container
            of the document/view instances created from this template
        @param templateConfig: the
            L{DocumentTemplateConfig<wxappext.config.sections.DocumentTemplateConfig>}
            object that represents the configuration for this template
        @param workspaceExtension: the file extension for the 
            file in which to save the settings of the scripting workspace
        @param directory: the directory in which to save the scripting
            workspace; if directory is C{None}, the default directory
            will be a 'dot' directory composed from the application's
            name, underneath the user's home folder
        @param icon: the L{Image<wx.Image>} to display as the workspace icon;
            if icon is C{None}, the template will attempt to use an icon
            named 'workspace.ico' in the application's resource directory,
            and will use a standard document icon if that attempt fails
        @param scriptTemplateFactories: a list of objects that
            can be used to create StandardDocTemplate objects
            from which to create special-purpose script modules (in addition
            to the built-in script module types that the WorkspaceTemplate
            creates by default)
        """
  
        from wxappext.stddocmgr import DocTypes
        from wxappext.config.docviewapp import TEMPLATE_NO_DLG            
        from wxappext.config import cfgsearch
        from wxappext.compoundfiles import CompoundDocument, CompoundView
        from wxappext.fs import FileSystem
  
        if directory is None:
            directory = '$HOME/.%s' % wx.GetApp().GetAppName()
        if icon is None:
            searcher = cfgsearch.ConfigFileSearch()
            try:
                icon = wx.Icon(searcher.FindFile('workspace.ico'), 
                    wx.BITMAP_TYPE_ICO)
            except:
                pass
  
        StandardDocTemplate.__init__(self, docManager, containerConfig,
            templateConfig, 'Workspace', "*%s" % workspaceExtension, 
            containerConfig.ExpandStandardPaths(directory), 
        workspaceExtension, 'Workspace', 'Workspace View', 
        ObjectFactory(CompoundDocument, 'Workspace',
            DocTypes('', 'Items', [PyModuleTemplateFactory(),
                PyShellTemplateFactory()] + scriptTemplateFactories),
            fileSystem=FileSystem(), defaultNew=[]),
        ObjectFactory(CompoundView, bottomPaneContentType='Shell',
            viewBottomPaneContent=True, 
            resourceNames={'notebook':'modules', 'xrc':'workspace.xrc',
                           'explorerMenu':'ScriptWorkspaceExplorer',
                           'subdocumentMenu':'ScriptingWorkspaceTabs'},
            scriptInterfaceName='WorkbookView'), 
        icon=icon, scriptInterfaceName='Workspace', flags=TEMPLATE_NO_DLG)
  
    def _GetAssociatedDocumentInfo(self, docManager, containerConfig, 
        templateConfig):
        # here's where we add the associated document info stuff
        # to the template, so that it knows how to associate a Shell
        # with the workspace
        result = super(WorkspaceTemplate, self)._GetAssociatedDocumentInfo(\
            docManager, containerConfig, templateConfig)
        from wxappext.assoc import AssociatedDocumentInfo
        workspaceInfo = AssociatedDocumentInfo('Shell', 
            PyShellTemplateFactory()(docManager, None, None), 
            '', '')
        result[workspaceInfo.Name] = workspaceInfo
        return result
  
  
class WorkspaceTemplateFactory(CurryAppend):
    """
    Create instances of WorkspaceTemplate objects, using an interface
    that mimics the calling signature of the StandardDocTemplate constructor.
    The caller of a WorkspaceTemplateFactory instance will supply
    the docManager, containerConfig and templateConfig arguments. The 
    instance will supply additional arguments that the WorkspaceTemplate
    constructor requires.
    """
    def __init__(self, workspaceExtension, directory=None, 
        icon=None, scriptTemplateFactories=[]):
        """
        Create a new WorkspaceTemplateFactory instance.
  
        @param workspaceExtension: the file extension for the 
            file in which to save the settings of the scripting workspace
        @param directory: if specified, the directory in which to save 
            the scripting workspace; see the L{WorkspaceTemplate}
            constructor for the default value
        @param icon: if specified, the L{Image<wx.Image>} to display
            as the workspace icon; see the L{WorkspaceTemplate}
            constructor for the default value
        @param scriptTemplateFactories: if specified, a list of objects that
            can be used to create StandardDocTemplate objects
            from which to create special-purpose script modules (in addition
            to the built-in script module types that the L{WorkspaceTemplate}
            creates by default)
        """
  
        CurryAppend.__init__(self, WorkspaceTemplate, workspaceExtension, 
            directory, icon, scriptTemplateFactories)