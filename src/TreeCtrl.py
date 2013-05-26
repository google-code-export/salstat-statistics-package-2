import wx
from wx.lib.mixins.treemixin import ExpansionState
import os
import cPickle

TreeBaseClass = wx.TreeCtrl


class myEVT_CUSTOM:
    def __init__(self):
        return
    def Skip(self):
        return

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
    USE_CUSTOMTREECTRL = False
    _demoPngs= [wx.ART_FOLDER, wx.ART_FOLDER_OPEN, wx.ART_EXECUTABLE_FILE ]
    def __init__(self, parent):
        TreeBaseClass.__init__(self, parent, style= wx.TR_HAS_VARIABLE_ROW_HEIGHT|wx.TR_HAS_BUTTONS)
        self.BuildTreeImageList()
        if self.USE_CUSTOMTREECTRL:
            self.SetSpacing(10)
            self.SetWindowStyle(self.GetWindowStyle() & ~wx.TR_LINES_AT_ROOT)
        self.SetInitialSize((100,80))
        self._callbacks= dict()

    def AppendItem( self, parent, text, image=-1, wnd=None, callback= None):
        if self.USE_CUSTOMTREECTRL:
            item= TreeBaseClass.AppendItem( self, parent, text, image=image, wnd=wnd)
        else:
            item= TreeBaseClass.AppendItem( self, parent, text, image=image)
        # getting the treePath of the item
        treePath = self._getTreePath(item)
        # getting the callback to the items
        self._setDictItemCallback( self._callbacks, treePath, callback)
        return item
    
    def _setDictItemCallback(self, dictionary, treePath, callback= None):
        curritem= treePath.pop(0)
        currdict= dictionary # using currdict as a reference to the dictionary object
        while len(treePath) > 0:
            if not currdict.has_key( curritem):
                currdict[curritem]= dict()
            currdict= currdict[curritem]
            curritem= treePath.pop(0)
        if not currdict.has_key(curritem):
            currdict[curritem]= dict()
        currdict[curritem]['_callbac']= callback
    
    def _getTreePath(self, item):
        # return the full path of the selected item
        root=      self.GetRootItem()
        pathList=  [item]
        done=      False
        while not done:
            try:
                item=  self.GetItemParent(item)
            except:
                return []
            pathList.insert(0, item)
            if item == root:
                done= True
        return [self.GetItemText( obj) for obj in  pathList]

    def BuildTreeImageList(self):
        def str2Bmp(artName):
            return wx.ArtProvider.GetBitmap(artName, wx.ART_MENU, (16,16))
        imgList = wx.ImageList(16, 16)
        for png in self._demoPngs:
            imgList.Add( str2Bmp(png)) #.GetBitmap())
        self.AssignImageList(imgList)

    def GetItemIdentity(self, item):
        return self.GetPyData(item)
    
    def GetItemCallback(self, item):
        # getting the path to the item
        treePath= self._getTreePath(item)
        # reading the callback of the item
        if len(treePath) == 0:
            return None
        curritem= treePath.pop(0)
        currdict= self._callbacks # using currdict as a reference to the dictionary object
        while len( treePath) > 0:
            if not currdict.has_key( curritem):
                raise StandardError( 'Unknown item')
            currdict= currdict[curritem]
            curritem= treePath.pop(0)
        if not currdict.has_key( curritem):
            raise StandardError( 'Unknown item')
        return currdict[curritem]['_callbac']
    def recreateTree(self, data, parent= None, filter= None):
        if parent == None:
            parent= self.GetRootItem()
            
        if isinstance(data, (str, unicode)):
            return
        
        if len(data) == 0:
            return
        
        if len(data) == 1:
            if data[0] == u"--":
                return None
            if isinstance(data, (tuple,)):
                if isinstance(data[0],(str, unicode)):
                    return None
            
        elif len(data) == 4:
            if not isinstance( data[2], (list,tuple)):
                texto= data[0].replace('&','').split('\t')[0]
                if filter in (None,u''):
                    item= self.AppendItem(parent, texto, 2 ,callback= data[2])# data[1]
                else:
                    if filter.lower() in data[0].lower():
                        item= self.AppendItem(parent, texto, 2, callback= data[2])# data[1]
                return
        
        for item in data:
            if len(item)== 0:
                continue
            if len( item) in [1,4] and not isinstance(item, (str, unicode)):
                self.recreateTree( item, parent, filter)
                continue
            if isinstance(item, (str, unicode)):
                continue
            texto= item[0].replace('&','').split('\t')[0]
            if filter in (None,u''):
                newitem= self.AppendItem(parent, texto, 0)
            else:
                newitem= self.AppendItem(parent, texto, 1)
            self.recreateTree( item[1], newitem, filter)
            if filter:
                self.ExpandAll()
    
    def testFilter(self, data, parent= None, filtro= None):
        if parent == None:
            parent= tuple()#self.GetRootItem()
            
        if isinstance(data, (str, unicode,)):
            return
        
        if len(data) == 1:
            if data[0] == u"--":
                return
            if isinstance(data, (tuple,)):
                if isinstance(data[0],(str, unicode)):
                    return
        
        elif len(data) == 4:
            if not isinstance( data[2], (list,tuple)):
                texto= data[0].replace('&','').split('\t')[0]
                if filtro == None:
                    return data
                else:
                    if filtro.lower() in data[0].lower():
                        return data
                return None
            
        if isinstance(parent, (str,unicode)):
            parent= (parent,)
        listItems= tuple()
        for item in data:
            if len( item) in [1,4]:
                res= self.testFilter( item, parent, filtro)
                if res != None:
                    listItems+=(res,)
                continue
            texto= item[0].replace('&','').split('\t')[0]
            newitem= texto
            res= self.testFilter( item[1], newitem, filtro)
            if len(res) > 0:
                listItems+= ( self.testFilter( item[1], newitem, filtro), )
            
        if len(parent)> 0:
            # in case there is not items to select
            if len(listItems) == 0:
                parent= tuple()
            else:
                parent+= (listItems,)
            #try:
                #if filtro != None and len(listItems)== 2:
                    #if isinstance(listItems[1], (tuple,)) and len( listItems[1])!=0:
                        #parent+= (listItems,)
                #else:
                    #parent+= (listItems,)
            #except IndexError:
                #parent+= (listItems,)
        else:
            parent= listItems
            
        return parent
            
    def filterData(self, data, filtro):
        # filtering the data to display only the needed items
        if filtro == None:
            return data
        
        if not isinstance(filtro, (str, unicode)):
            return data
        
        res= self.testFilter(data, filtro= filtro)
        # removing empty submenus
        
        return self.recreateTree(res, filter= filtro) #recreateTree

class _emptyLog:
    # emulating an empty log panel
    def clearLog(self):
        pass
    def writeLine(self, *args, **params):
        pass
    
class TreePanel(wx.Panel):
    USE_CUSTOMTREECTRL= False
    def __init__( self, parent, *args, **params):
        '''TreePanel parent, log, *args'''
        try:   self.log= params.pop('log')
        except KeyError:  self.log=  _emptyLog()
        try:    wx.Panel.__init__( self, parent, wx.ID_ANY, *args, **params)
        except: wx.Panel.__init__( self, parent, wx.ID_ANY)

        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        # initialize the tree data
        self._treelist= []
        self._callbacDict= dict()
        
        # Create a TreeCtrl
        self.ReadConfigurationFile()
        self.treeMap = {}
        self.searchItems = {}

        self.tree = _wxPythonDemoTree( self)
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
        
        self.tree.Bind( wx.EVT_TREE_ITEM_EXPANDED,  self.OnItemExpanded)
        #self.tree.Bind( wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed)
        #self.tree.Bind( wx.EVT_TREE_SEL_CHANGED,    self.OnSelChanged)
        self.tree.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.OnTreeItemActivated)
        #self.tree.Bind( wx.EVT_LEFT_DOWN,           self.OnTreeLeftDown)

    @property
    def treelist(self):
        return self._treelist

    @treelist.setter
    def treelist(self, data):
        if isinstance( data, (tuple, list)):
            self._treelist= data
            self.RecreateTree()
        else:
            raise StandardError('unsupported variable type')

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

    def RecreateTree(self, evt= None): # child of the main frame
        # Catch the search type (name or content)
        searchMenu= self.filter.GetMenu().GetMenuItems()
        fullSearch= searchMenu[1].IsChecked()
        if evt:
            if fullSearch:
                # Do not scan all the demo files for every char
                # the user input, use wx.EVT_TEXT_ENTER instead
                return
        expansionState= self.tree.GetExpansionState()
        current=        None
        item=           self.tree.GetSelection()
        if item:
            prnt=       self.tree.GetItemParent(item)
            if prnt:
                current= (self.tree.GetItemText(item),
                          self.tree.GetItemText(prnt))
        self.tree.Freeze()
        self.tree.DeleteAllItems()
        
        self.root= list()
        mainRoot= self.tree.AddRoot( "Main")
        self.root.append( mainRoot)
        self.tree.SetItemImage( self.root[-1], 0)
        self.tree.SetItemPyData( self.root[-1], 0)
        treeFont= self.tree.GetFont()
        catFont=  self.tree.GetFont()

        # The native treectrl on MSW has a bug where it doesn't draw
        # all of the text for an item if the font is larger than the
        # default.  It seems to be clipping the item's label as if it
        # was the size of the same label in the default font.
        if self.USE_CUSTOMTREECTRL or 'wxMSW' not in wx.PlatformInfo:
            treeFont.SetPointSize(treeFont.GetPointSize()+2)
        treeFont.SetWeight(wx.BOLD)
        catFont.SetWeight(wx.BOLD)
        self.tree.SetItemFont(self.root[-1], treeFont)
        firstChild= None
        selectItem= None
        filter=     self.filter.GetValue()
        count=      0
        
        ##############################
        ## recursive creation of data
        #self.tree.testFilter( self.treelist, filtro= filter)
        res= self.tree.filterData(self.treelist, filtro= filter)
        
        self.tree.Thaw()
        self.searchItems = {}
        self.tree.Expand( mainRoot)

    def OnSearch(self, event=None): # child of the main frame
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
        item= event.GetItem()
        # change the icon to open state
        event.Skip()
    def OnItemCollapsed(self, event):
        item = event.GetItem()
        # change the icon to close state
        event.Skip()

    def OnSelChanged(self, evt):
        #if self.dying or not self.loaded or self.skipLoad:
        #  
        #self.StopDownload()
        return

    def OnTreeItemActivated(self, evt):
        # reset the overview text if the tree item is clicked on again
        #pt = evt.GetPosition();
        #item, flags = self.tree.HitTest(pt)
        item= evt.GetItem()
        if hasattr(item,'callback'):
            pass
        try:
            itemText = self.tree.GetItemText( item)
        except: # try to catch the wx._core.PyAssertionError
            return
        finally:
            evt.Skip()
        callback= self.tree.GetItemCallback(item)
        if callback != None:
            try:
                callback()
            except TypeError:
                callback(evt= myEVT_CUSTOM())