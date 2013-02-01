import wx
from wx.lib.mixins.treemixin import ExpansionState
from imagenes import imageEmbed
import os
TreeBaseClass = wx.TreeCtrl

imagenes= imageEmbed()

_demoPngs = ["disk", "pageexcel", "printer", "cancel", "icono", "edit_copy",
             "edit_cut", "edit_paste", "edit_redo", "edit_undo", "x_office_spreadsheet",
             "save", "x_office_calendar", "view_refresh"]
USE_CUSTOMTREECTRL = False


_treeList = [
    # new stuff
    ('Recent Additions/Updates', [
        'PropertyGrid',
        'SystemSettings',
        'GridLabelRenderer',
        'InfoBar',
        'WrapSizer',
        'UIActionSimulator',
        'GraphicsGradient',
        'PDFViewer',
        'ItemsPicker',
        'CommandLinkButton',
        'DVC_DataViewModel',
        'DVC_IndexListModel',
        'DVC_ListCtrl',
        'DVC_TreeCtrl',
        'DVC_CustomRenderer',
        'PenAndBrushStyles',
        'HTML2_WebView',
        ]),

    # managed windows == things with a (optional) caption you can close
    ('Frames and Dialogs', [
        'AUI_DockingWindowMgr',
        'AUI_MDI',
        'Dialog',
        'Frame',
        'MDIWindows',
        'MiniFrame',
        'Wizard',
        ]),

    # the common dialogs
    ('Common Dialogs', [
        'AboutBox',
        'ColourDialog',
        'DirDialog',
        'FileDialog',
        'FindReplaceDialog',
        'FontDialog',
        'MessageDialog',
        'MultiChoiceDialog',
        'PageSetupDialog',
        'PrintDialog',
        'ProgressDialog',
        'SingleChoiceDialog',
        'TextEntryDialog',
        ]),

    # dialogs from libraries
    ('More Dialogs', [
        'ImageBrowser',
        'ScrolledMessageDialog',
        ]),
]

def GetDataDir():
    """
    Return the standard location on this platform for application data
    """
    sp = wx.StandardPaths.Get()
    return sp.GetUserDataDir()

def GetConfig():
    if not os.path.exists(GetDataDir()):
        os.makedirs(GetDataDir())

    config = wx.FileConfig(
        localFilename=os.path.join(GetDataDir(), "options"))
    return config

class _wxPythonDemoTree(ExpansionState, TreeBaseClass):
    def __init__(self, parent):
        TreeBaseClass.__init__(self, parent, style=wx.TR_DEFAULT_STYLE|
                               wx.TR_HAS_VARIABLE_ROW_HEIGHT)
        self.BuildTreeImageList()
        if USE_CUSTOMTREECTRL:
            self.SetSpacing(10)
            self.SetWindowStyle(self.GetWindowStyle() & ~wx.TR_LINES_AT_ROOT)

        self.SetInitialSize((100,80))


    def AppendItem(self, parent, text, image=-1, wnd=None):
        if USE_CUSTOMTREECTRL:
            item = TreeBaseClass.AppendItem(self, parent, text, image=image, wnd=wnd)
        else:
            item = TreeBaseClass.AppendItem(self, parent, text, image=image)
        return item

    def BuildTreeImageList(self):
        imgList = wx.ImageList(16, 16)
        for png in _demoPngs:
            imgList.Add(imagenes[png]) #.GetBitmap())

        # add the image for modified demos.
        imgList.Add(imagenes["config"])#.GetBitmap())

        self.AssignImageList(imgList)


    def GetItemIdentity(self, item):
        return self.GetPyData(item)



class TreePanel(wx.Panel):
    def __init__( self, parent, log, *args, **params):
        '''TreePanel parent, log, *args'''
        self.log=   log
        try:
            wx.Panel.__init__( self, parent, wx.ID_ANY, *args, **params)
        except:
            wx.Panel.__init__( self, parent, wx.ID_ANY)

        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        # initialize the tree data
        self._treelist= []
        self._callbacDict= dict()

        
        # Create a TreeCtrl
        self.ReadConfigurationFile()
        self.treeMap = {}
        self.searchItems = {}

        self.tree = _wxPythonDemoTree( self)#leftPanel
        bSizer1.Add( self.tree, 1, wx.ALL|wx.EXPAND, 5 )

        self.filter = wx.SearchCtrl( self, style= wx.TE_PROCESS_ENTER)# leftPanel

        self.filter.ShowCancelButton( True)
        self.filter.Bind( wx.EVT_TEXT, self.RecreateTree)
        self.filter.Bind( wx.EVT_SEARCHCTRL_CANCEL_BTN,
                          lambda e: self.filter.SetValue(''))
        self.filter.Bind( wx.EVT_TEXT_ENTER, self.OnSearch)
        bSizer1.Add( self.filter, 0, wx.ALL|wx.EXPAND, 5 )

        searchMenu = wx.Menu()
        item = searchMenu.AppendRadioItem( -1, "Sample Name")
        item = searchMenu.AppendRadioItem( -1, "Sample Content")
        self.Bind( wx.EVT_MENU, self.OnSearchMenu, item)
        #self.Bind( wx.EVT_MENU, self.OnSearchMenu, item)
        self.filter.SetMenu( searchMenu)

        self.RecreateTree()
        self.tree.SetExpansionState( self.expansionState)

        self.SetSizer( bSizer1 )
        self.Layout()
        
        #self.tree.Bind( wx.EVT_TREE_ITEM_EXPANDED,  self.OnItemExpanded)
        #self.tree.Bind( wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed)
        self.tree.Bind( wx.EVT_TREE_SEL_CHANGED,    self.OnSelChanged)
        #self.tree.Bind( wx.EVT_TREE_KEY_DOWN, self.OnSelChanged)
        self.tree.Bind( wx.EVT_LEFT_DOWN,           self.OnTreeLeftDown)

    @property
    def treelist(self):
        return self._treelist

    @treelist.setter
    def treelist(self, data):
        if isinstance( data, (tuple, list)):
            self._treelist= data
            # updating the callbacks:
            for key,values in data:
                for keyname, icon, callback, callbackOptional in values:
                    self._callbacDict[keyname] = callback
                 
            self.RecreateTree()
        else:
            raise StandardError('unsoported variable type')

    def ReadConfigurationFile(self):

        self.auiConfigurations = {}
        self.expansionState = [0, 1]

        config = GetConfig()
        val = config.Read('ExpansionState')
        if val:
            self.expansionState = eval(val)

        val = config.Read('AUIPerspectives')
        if val:
            self.auiConfigurations = eval(val)

        val = config.Read('AllowDownloads')
        if val:
            self.allowDocs = eval(val)

        val = config.Read('AllowAUIFloating')
        if val:
            self.allowAuiFloating = eval(val)

        return
        #MakeDocDirs()
        #pickledFile = GetDocFile()

        if not os.path.isfile(pickledFile):
            self.pickledData = {}
            return

        fid = open(pickledFile, "rb")
        try:
            self.pickledData = cPickle.load(fid)
        except:
            self.pickledData = {}

        fid.close()

    def RecreateTree(self, evt=None): # child of the main frame
        # Catch the search type (name or content)
        searchMenu = self.filter.GetMenu().GetMenuItems()
        fullSearch = searchMenu[1].IsChecked()
        if evt:
            if fullSearch:
                # Do not`scan all the demo files for every char
                # the user input, use wx.EVT_TEXT_ENTER instead
                return
        expansionState = self.tree.GetExpansionState()
        current = None
        item = self.tree.GetSelection()
        if item:
            prnt = self.tree.GetItemParent(item)
            if prnt:
                #try:
                    current = (self.tree.GetItemText(item),
                           self.tree.GetItemText(prnt))
                #except:
                #    pass
        self.tree.Freeze()
        self.tree.DeleteAllItems()
        self.root = self.tree.AddRoot("Statistical Functions")
        self.tree.SetItemImage(self.root, 0)
        self.tree.SetItemPyData(self.root, 0)
        treeFont = self.tree.GetFont()
        catFont = self.tree.GetFont()

        # The native treectrl on MSW has a bug where it doesn't draw
        # all of the text for an item if the font is larger than the
        # default.  It seems to be clipping the item's label as if it
        # was the size of the same label in the default font.
        if USE_CUSTOMTREECTRL or 'wxMSW' not in wx.PlatformInfo:
            treeFont.SetPointSize(treeFont.GetPointSize()+2)
        treeFont.SetWeight(wx.BOLD)
        catFont.SetWeight(wx.BOLD)
        self.tree.SetItemFont(self.root, treeFont)
        firstChild = None
        selectItem = None
        filter = self.filter.GetValue()
        count = 0

        # creation of list data
        for category, items in self.treelist:
            items= [item[0] for item in items]
            count += 1
            if filter:
                if fullSearch:
                    items = self.searchItems[category]
                else:
                    items = [item for item in items if filter.lower() in item.lower()] # item -> item[0]
            if items:
                child = self.tree.AppendItem(self.root, category, image=count)
                self.tree.SetItemFont(child, catFont)
                self.tree.SetItemPyData(child, count)
                if not firstChild: firstChild = child
                for childItem in items:
                    image = count
                    #if DoesModifiedExist(childItem):
                    #    image = len(_demoPngs)
                    theDemo = self.tree.AppendItem(child, childItem, image=image)
                    self.tree.SetItemPyData(theDemo, count)
                    self.treeMap[childItem] = theDemo
                    if current and (childItem, category) == current:
                        selectItem = theDemo

        #
        self.tree.Expand(self.root)
        if firstChild:
            self.tree.Expand(firstChild)
        if filter:
            self.tree.ExpandAll()
        elif expansionState:
            self.tree.SetExpansionState(expansionState)
        if selectItem:
            self.skipLoad = True
            self.tree.SelectItem(selectItem)
            self.skipLoad = False

        self.tree.Thaw()
        self.searchItems = {}

    def OnSearch(self, event=None): # child of the main frame
        value = self.filter.GetValue()
        if not value:
            self.RecreateTree()
            return

        wx.BeginBusyCursor()

        for category, items in self.treeList:
            self.searchItems[category] = []
            items= [item[0] for item in items]
            for childItem in items:
                if SearchDemo(childItem, value):
                    self.searchItems[category].append(childItem)

        wx.EndBusyCursor()
        self.RecreateTree()

    def OnSearchMenu(self, event):
        # Catch the search type (name or content)
        searchMenu = self.filter.GetMenu().GetMenuItems()
        fullSearch = searchMenu[1].IsChecked()

        if fullSearch:
            self.OnSearch()
        else:
            self.RecreateTree()
    def OnItemExpanded(self, event):
        item = event.GetItem()
        wx.LogMessage("OnItemExpanded: %s" % self.tree.GetItemText(item))
        event.Skip()

        #---------------------------------------------
    def OnItemCollapsed(self, event):
        item = event.GetItem()
        wx.LogMessage("OnItemCollapsed: %s" % self.tree.GetItemText(item))
        event.Skip()

    def OnSelChanged(self, evt):
        #if self.dying or not self.loaded or self.skipLoad:
        #  
        #self.StopDownload()
        item = evt.GetItem()
        itemText = self.tree.GetItemText( item)
        evt.Skip()
        self._loadDemo( itemText)

    def OnTreeLeftDown(self, event):
        # reset the overview text if the tree item is clicked on again
        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)
        try:
            itemText = self.tree.GetItemText( item)
        except: # try to catch the wx._core.PyAssertionError
            return
        finally:
            event.Skip()
        self._loadDemo( itemText)
        return
        if item == self.tree.GetSelection():
            self.SetOverview(self.tree.GetItemText(item)+" Overview", self.curOverview)
        event.Skip()
    
    def _loadDemo(self, demoName):
        try:
            self._callbacDict[demoName]()
        except KeyError:
            pass
