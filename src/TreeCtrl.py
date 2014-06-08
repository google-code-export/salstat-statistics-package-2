import wx
from wx.lib.mixins.treemixin import ExpansionState
import os
import cPickle
from salstat2_glob import *
from collections import OrderedDict

TreeBaseClass = wx.TreeCtrl
## from gridLib.gridsql import EVT_SQLGRID_NEW_TABLE
from threading import Thread
from copy import deepcopy

class myEVT_CUSTOM:
    def __init__(self, item, itemtext):
        self.__item= item
        self.__itemtext= itemtext
        return
    def Skip(self):
        return
    @property
    def item(self):
        return self.__item
    @property
    def itemtext(self):
        return self.__itemtext

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
    def __init__(self, parent):
        TreeBaseClass.__init__(self, parent, style= wx.TR_HAS_VARIABLE_ROW_HEIGHT|wx.TR_HAS_BUTTONS)
        self.parent = parent
        self.__icons= [wx.ArtProvider.GetBitmap(artName, wx.ART_MENU, (16,16)) for artName in
                       [wx.ART_FOLDER, wx.ART_FILE_OPEN, wx.ART_EXECUTABLE_FILE ]]
        self.__datatype= 'list'
        self.BuildTreeImageList()
        if self.USE_CUSTOMTREECTRL:
            self.SetSpacing(10)
            self.SetWindowStyle(self.GetWindowStyle() & ~wx.TR_LINES_AT_ROOT)
        self.SetInitialSize((100,80))
        self._callbacks= dict()

    def getIcons(self):
        return self.__icons

    def addIcon(self, icon):
        try:
            if icon in self.getIcons():
                return [pos for pos, iconi in enumerate(self.getIcons()) if icon == iconi][0]
            else:
                self.getIcons().append(icon)
                return len(self.getIcons())-1
        finally:
            self.BuildTreeImageList()

    def setdatatype(self, datatype):
        self.__datatype= datatype
        self.BuildTreeImageList()

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
        imgList = wx.ImageList(16, 16)
        for icon in self.getIcons():
            imgList.Add( icon) #.GetBitmap())
        self.AssignImageList(imgList)

    def GetItemIdentity(self, item):
        return self.GetPyData(item)

    def getItemCallbackParameters(self, item):
        treePath= self._getTreePath(item)
        data= self.parent.treelist
        try:
            treePath.pop(0)
            treePath.pop(0)
            for key in treePath:
                value= [pos for pos, dat in enumerate(data) if dat.text == key][0]
                data= data[value]
            return data.params
        except:
            return None

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
                raise StandardError( __('Unknown item'))
            currdict= currdict[curritem]
            curritem= treePath.pop(0)
        if not currdict.has_key( curritem):
            raise StandardError( __('Unknown item'))
        return currdict[curritem]['_callbac']

    def __recreateTreeBaseItem(self, data, parent= None, filter= None):
        if parent == None:
            #try:
            #    parent= self.GetRootItem()
            mainRoot= self.AddRoot(data.text)
            self.SetItemImage( mainRoot, 0)
            for item in data:
                self.__recreateTreeBaseItem( item, mainRoot, filter)
            self.Expand( mainRoot)
            return

        if isinstance(data, (str, unicode)):
            return

        if len(data) == 0: # if has no childs
            texto= data.text.replace('&','').split('\t')[0]
            iconIndex= data.iconIndex
            if iconIndex == None:
                iconIndex = 2
            if filter in (None,u''):
                item= self.AppendItem(parent, texto, iconIndex , callback= data.callback)
            else:
                try:
                    if filter.lower() in data.text.lower():
                        item= self.AppendItem(parent, texto, iconIndex, callback= data.callback)
                        self.ExpandAll()
                except UnicodeDecodeError:
                    pass
            return
        else:
            # creating the item container
            folder= self.AppendItem(parent, data.text, 0)
            # setting the imagen to open folder
            self.SetItemImage( folder, 0, which = wx.TreeItemIcon_Normal)
            self.SetItemImage( folder, 1, which = wx.TreeItemIcon_Expanded)
            for item in data:
                self.__recreateTreeBaseItem( item, folder, filter)

    def recreateTree(self, data, parent= None, filter= None):
        def filterData( newdata, filter ):
            for key,value in newdata.items( ):
                if len( value ) == 0:
                    if filter.lower( ) in value.text.lower( ):
                        continue
                    # deleting the item
                    del( newdata[key])
                else:
                    filterData( value, filter)
                    if len( value) == 0:
                        del( newdata[key])
                        
        def copyTreedata(Treedata, root= None):
            if root == None:
                root= baseItem()
                for param in ('text', 'image', 'callback'):
                    setattr(root, param, getattr(Treedata, param))
            for pos in range(len(Treedata)):
                data= Treedata[pos]
                item= baseItem()
                for param in ('text', 'image', 'callback'):
                    setattr(item, param, getattr(data, param))
                root.addchild(item)
                copyTreedata(data, item)
            return root
                
        if self.__datatype == 'baseItem':
            ###############################################
            ############################# ----to be fixed
            ############################################### 
            if filter not in(None,''):
                # copying the contents of data in newdata
                newdata = copyTreedata(data)
                # filtering the data
                filterData( newdata, filter )
                return self.__recreateTreeBaseItem( newdata, parent, filter )
            ###############################################
            ###############################################
            return self.__recreateTreeBaseItem( data, parent, filter )
        
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
        
        elif len(data) >= 4: # ==
            if not isinstance( data[2], (list,tuple)):
                texto= data[0].replace('&','').split('\t')[0]
                if filtro in (None,''):
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
        else:
            parent= listItems
            
        return parent
            
    def filterData(self, data, filtro):
        # filtering the data to display only the needed items
        #if filtro in (None,''):
        #    return data
        #
        # if not isinstance(filtro, (str, unicode)):
        #    return data
        #
        #res= self.testFilter(data, filtro= filtro)
        # removing empty submenus
        
        return self.recreateTree(data, filter= filtro) #recreateTree

class baseItem:
    """contain all option of the item"""
    def __init__(self, parent= None, text= None, image= None, callback= None, id= None, *args, **params):
        self.__setIntialValues()
        self.parent = parent
        self.text = text
        self.image= image
        self.callback = callback
        self.args = args
        self.params = params
        self.child = OrderedDict()

    def __setIntialValues(self):
        self.__parent= None
        self.__text=   None
        self.__image=  None
        self.__iconIndex= None # to be manipulated by the treeCtrl
        self.__callback=   None
        self.__args=   None
        self.__params= None

    def has_key(self, key):
        if key in self.child:
            return True
        return False

    def items(self):
        return self.child.items()

    def values(self):
        return self.child.values

    def keys(self):
        return self.child.keys()

    @property
    def image(self):
        return self.__image
    @image.setter
    def image(self, image):
        self.__image = image
    @property
    def parent(self):
        return self.__parent
    @parent.setter
    def parent(self, parent):
        self.__parent = parent
    @property
    def text(self):
        return self.__text
    @text.setter
    def text(self, text):
        self.__text = text
    # to be manipulated by the treeCtrl
    @property
    def iconIndex(self):
        return self.__iconIndex
    @iconIndex.setter
    def iconIndex(self, iconIndex):
        self.__iconIndex= iconIndex
    @property
    def callback(self):
        return self.__callback
    @callback.setter
    def callback(self, callback):
        self.__callback= callback
    @property
    def args(self):
        return self.__args
    @args.setter
    def args(self, args):
        self.__args= args
    @property
    def params(self):
        return self.__params
    @params.setter
    def params(self, params):
        self.__params= params
    def addchild( self, child):
        if not isinstance( child, baseItem):
            raise StandardError( "Invalid child")
        child.parent= self
        self.child[child.text] = child

    def __getitem__( self, itemName):
        if self.child.has_key( itemName):
            return self.child[itemName]
        elif isinstance(itemName, (int)):
            itemNumber= itemName
            if itemNumber > len(self.child):
                raise IndexError
            needKey= self.child.keys()[itemNumber]
            return self.child[needKey]
        else:
            raise IndexError("Invalid item")

    def __delitem__( self, itemName):
        if self.child.has_key( itemName):
            self.child.pop( itemName)
        else:
            raise IndexError("Invalid item")

    def __len__( self):
        return len( self.child)

class _BaseTree(ExpansionState, TreeBaseClass):
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
                raise StandardError( __('Unknown item'))
            currdict= currdict[curritem]
            curritem= treePath.pop(0)
        if not currdict.has_key( curritem):
            raise StandardError( __('Unknown item'))
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

        elif len(data) >= 4: # ==
            if not isinstance( data[2], (list,tuple)):
                texto= data[0].replace('&','').split('\t')[0]
                if filtro in (None,''):
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

class _tree(ExpansionState, TreeBaseClass):
    pass

class _emptyLog:
    # emulating an empty log panel
    def clearLog(self):
        pass
    def writeLine(self, *args, **params):
        pass
    
class TreePanel(wx.Panel):
    USE_CUSTOMTREECTRL= False
    def __init__( self, parent, *args, **params):
        try:   self.__rootName= params.pop('rootName')
        except KeyError:  self.__rootName=  _('Main')
        try:    wx.Panel.__init__( self, parent, wx.ID_ANY, *args, **params)
        except: wx.Panel.__init__( self, parent, wx.ID_ANY)
        self.__thread = None
        self.__treedatatype = 'list'
        self.curritem= None
        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        # initialize the tree data
        self._treelist= []
        self._callbacDict= dict()
        
        # Create a TreeCtrl
        self.ReadConfigurationFile()
        self.treeMap = {}
        self.searchItems = {}

        self.tree = _wxPythonDemoTree( self )
        bSizer1.Add( self.tree, 1, wx.ALL|wx.EXPAND, 5 )

        self.filter = wx.SearchCtrl( self, style= wx.TE_PROCESS_ENTER)# leftPanel
        self.filter.ShowCancelButton( True)
        self.filter.Bind( wx.EVT_TEXT, self.OnSearchMenu) #RecreateTree
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
        
        #self.tree.Bind( wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed)
        self.tree.Bind( wx.EVT_TREE_SEL_CHANGED,    self.OnSelChanged)
        self.tree.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.OnTreeItemActivated)
        #self.tree.Bind( wx.EVT_LEFT_DOWN,           self.OnTreeLeftDown)

    def getdataType(self):
        return self.__treedatatype

    def setdataType(self, dataType):
        self.__treedatatype= dataType
        self.tree.setdatatype(dataType)

    @property
    def treelist(self):
        return self._treelist
    @treelist.setter
    def treelist(self, data):
        if isinstance( data, (tuple, list)):
            self._treelist= data
        elif isinstance(data, (baseItem)):
            self.setdataType('baseItem')
            self._treelist= data
        else:
            raise StandardError(__('unsupported variable type'))
        # force to update the icons
        self.updateIcons()
        self.RecreateTree()

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

    def __RecreateBaseItem(self, evt= None):
        """to Recreate the tree when the data is baseItem kind"""
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

        if self.USE_CUSTOMTREECTRL or 'wxMSW' not in wx.PlatformInfo:
            treeFont.SetPointSize(treeFont.GetPointSize()+2)
        #treeFont.SetWeight(wx.BOLD)
        #catFont.SetWeight(wx.BOLD)
        #self.tree.SetItemFont(self.root[-1], treeFont)
        firstChild= None
        selectItem= None
        filter=     self.filter.GetValue()
        count=      0

        ##############################
        ## recursive creation of data
        res= self.tree.filterData( self.treelist, filtro= filter)
        self.tree.Thaw()
        self.searchItems = {}
        #self.tree.Expand( mainRoot)

    def updateIcons(self):
        # to update the icons of the base items
        # reading all the contained icons recursively
        def iconize( data):
            if data.image != None:
                iconIndex= self.tree.addIcon(data.image)
                data.iconIndex= iconIndex
            if len(data.child) == 0:
                return
            for child in data.child.values():
                iconize(child)
        iconize( self._treelist)

    def RecreateTree(self, evt= None): # child of the main frame
        # Catch the search type (name or content)
        # reading the icons
        if self.getdataType() == 'baseItem':
            return self.__RecreateBaseItem(evt)
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
        mainRoot= self.tree.AddRoot( self.__rootName)
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
        res= self.tree.filterData(self.treelist, filtro= filter)
        
        self.tree.Thaw()
        self.searchItems = {}
        self.tree.Expand( mainRoot)

    class recreatreTheTree(Thread):
        def run(self, *args, **params):
            pass

    def OnSearch(self, event=None): # child of the main frame
        #if self.__thread != None
        #self.__thread = _checkUpdates()
        #thread.setDaemon(True)
        #thread.start()
        self.RecreateTree()

    def OnSearchMenu(self, event):
        # Catch the search type (name or content)
        searchMenu = self.filter.GetMenu().GetMenuItems()
        fullSearch = searchMenu[1].IsChecked()
        if len(self.filter.GetValue()) < 2 and not (self.filter.GetValue() in (None,u'')):
            return
        if fullSearch:
            self.OnSearch()
        else:
            self.RecreateTree()

    def OnItemCollapsed(self, event):
        item = event.GetItem()
        # change the icon to close state
        event.Skip()

    def OnSelChanged(self, evt):
        self.curritem= evt.Item
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
                callback(evt= myEVT_CUSTOM(item, itemText))

##class TreePanelSQL(TreePanel):
    ##def __init__(self, *args, **params):
        ##TreePanel.__init__(self, *args, **params)
        ##self.curritem = None
        ##self.Bind(EVT_SQLGRID_NEW_TABLE, self._onNewTable)

    ##def _onNewTable(self, evt):
        ##tablename = wx.GetApp().frame.db.currTable
        ### updating the tree labels
        ##lastSelectedItem = self.curritem
        ### check if the last selected item is the root
        ##treePath = self.tree._getTreePath(lastSelectedItem)
        ##if len(treePath) <= 1:
            ### takes the first child
            ##root = self.tree.RootItem
            ##firstItem = self.tree.GetFirstChild(root)[0]
            ##firstItemLabel = self.tree.GetItemText(firstItem)
            ### appending an item to the first item
        ##elif len(treePath) == 2:
            ##firstItemLabel = treePath[-1]
            ##treedata = self.treelist
            ### appending an item to the first item
        ##elif len(treePath) == 3:
            ##firstItemLabel = treePath[1]
        ##treedata = self.treelist
        ##newData = list()
        ##for dat in treedata:
            ##if dat[0] == firstItemLabel:
                ##dat[1].append([tablename, wx.EmptyIcon, wx.GetApp().frame.db.OpenFromDbExplorer, wx.ID_NEW])
            ##newData.append(dat)
        ### updating the contents of the tree panel
        ##self.treelist = newData
        ##print __("Adding a new table")

    ##def OnTreeItemActivated(self, evt):
        ### reset the overview text if the tree item is clicked on again
        ###pt = evt.GetPosition();
        ###item, flags = self.tree.HitTest(pt)
        ##self.curritem = item = evt.GetItem()
        ##if hasattr(item,'callback'):
            ##pass
        ##try:
            ##itemText = self.tree.GetItemText( item)
        ##except: # try to catch the wx._core.PyAssertionError
            ##return
        ##finally:
            ##evt.Skip()
        ##callback= self.tree.GetItemCallback(item)
        ##if callback != None:
            ##try:
                ##setattr( evt, 'parentPathLabel',
                         ##self.tree.GetItemText(self.tree.GetItemParent(item)))
                ##setattr( evt, 'tableName', 
                         ##self.tree.GetItemText(item))
                ##callback(evt)
            ##except TypeError:
                ##callback(evt= myEVT_CUSTOM())