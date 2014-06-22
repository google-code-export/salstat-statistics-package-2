#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sebastian Lopez Buritica -- selobu at gmail dot com'
__all__= ['PivotFrame']

import wx
import wx.aui
from ObjectListView import ObjectListView, ColumnDefn, GroupListView, Filter
from collections import namedtuple
import cPickle
from calculator import MyFrame1 as TransformFrame

## The code of the class below was taken from
## http://wiki.wxpython.org/ListControls#Drag_and_Drop_with_lists
class ListDrop(wx.PyDropTarget):
    """ Drop target for simple lists. """
    def __init__(self, source):
        """ Arguments:
         - source: source listctrl.
        """
        wx.PyDropTarget.__init__(self)

        self.dv = source

        # specify the type of data we will accept
        self.data = wx.CustomDataObject("ListCtrlItems")
        self.SetDataObject(self.data)

    # Called when OnDrop returns True.  We need to get the data and
    # do something with it.
    def OnData(self, x, y, d):
        # copy the data from the drag source to our data object
        if self.GetData():
            # convert it back to a list and give it to the viewer
            ldata = self.data.GetData()
            l = cPickle.loads(ldata)
            self.dv._insert(x, y, l)

        # what is returned signals the source what to do
        # with the original data (move, copy, etc.)  In this
        # case we just return the suggested value given to us.
        return d

class DragListStriped(wx.ListCtrl):
    def __init__(self, parent, *arg, **params):
        self.parent= parent
        try:  self.fields= params.pop('fields')
        except KeyError:   self.fields = None

        try:  self.choices= params.pop('choices')
        except KeyError:   self.choices = []

        try: self.droopTarget= params.pop('droopTarget')
        except KeyError: self.droopTarget= None

        try: self.delDragFields = params.pop('delDragFields')
        except KeyError: self.delDragFields = True

        try: self.addDroopFields = params.pop('addDroopFields')
        except KeyError: self.addDroopFields = True

        try: self.colWidth = params.pop('colWidth')
        except KeyError: self.colWidth = 220

        wx.ListCtrl.__init__(self, parent, *arg, **params)

        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self._startDrag)

        dt = ListDrop(self)
        self.SetDropTarget(dt)

        ##self.Bind(wx.EVT_LIST_BEGIN_DRAG, self._onDrag)
        ##self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._onSelect)
        ##self.Bind(wx.EVT_LEFT_UP,self._onMouseUp)
        ##self.Bind(wx.EVT_LEFT_DOWN, self._onMouseDown)
        ##self.Bind(wx.EVT_LEAVE_WINDOW, self._onLeaveWindow)
        ##self.Bind(wx.EVT_ENTER_WINDOW, self._onEnterWindow)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._onItemActivated)
        ##self.Bind(wx.EVT_LIST_DELETE_ITEM, self._onDelete)

        #---------------
        # Variables
        #---------------
        self.IsInControl=True
        self.startIndex=-1
        self.dropIndex=-1
        self.IsDrag=False
        self.dragIndex=-1
        if self.fields != None:
            # update with the selected fields
            for col, fieldName in enumerate( self.fields):
                self.InsertColumn( col, fieldName, width= self.colWidth)

        if self.choices != []:
            try:
                numCols= len(self.choices[0])
                if numCols == len( self.fields):
                    for rowNumber, rowData in enumerate(self.choices):
                        self.InsertStringItem(rowNumber, rowData[0])
                        [self.SetStringItem(rowNumber, pos ,rowData[pos]) for pos in range(1,numCols)]
            except TypeError:
                pass
    def _onItemActivated(self, evt):
        evt.Skip()
    @property
    def fields(self):
        return self.__fields
    @fields.setter
    def fields(self, fields):
        self.__fields= fields

    def getItemInfo(self, idx):
        """Collect all relevant data of a listitem, and put it in a list"""
        l = []
        l.append(idx) # We need the original index, so it is easier to eventualy delete it
        l.append(self.GetItemData(idx)) # Itemdata
        l.append(self.GetItemText(idx)) # Text first column
        for i in range(1, self.GetColumnCount()): # Possible extra columns
            l.append(self.GetItem(idx, i).GetText())
        return l

    def _startDrag(self, e):
        """ Put together a data object for drag-and-drop _from_ this list. """
        l = []
        idx = -1
        while True: # find all the selected items and put them in a list
            idx = self.GetNextItem(idx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if idx == -1:
                break
            l.append(self.getItemInfo(idx))

        # Pickle the items list.
        itemdata = cPickle.dumps(l, 1)
        # create our own data format and use it in a
        # custom data object
        ldata = wx.CustomDataObject("ListCtrlItems")
        ldata.SetData(itemdata)
        # Now make a data object for the  item list.
        data = wx.DataObjectComposite()
        data.Add(ldata)

        # Create drop source and begin drag-and-drop.
        dropSource = wx.DropSource(self)
        dropSource.SetData(data)
        res = dropSource.DoDragDrop(flags=wx.Drag_DefaultMove)

        # If move, we want to remove the item from this list.
        if res == wx.DragMove and self.delDragFields:
            # It's possible we are dragging/dropping from this list to this list.  In which case, the
            # index we are removing may have changed...

            # Find correct position.
            l.reverse() # Delete all the items, starting with the last item
            for i in l:
                pos = self.FindItem(i[0], i[2])
                self.DeleteItem(pos)

    def _insert(self, x, y, seq):
        """ Insert text at given x, y coordinates --- used with drag-and-drop. """
        if not self.addDroopFields:
            return
        # Find insertion point.
        index, flags = self.HitTest((x, y))

        if index == wx.NOT_FOUND: # not clicked on an item
            if flags & (wx.LIST_HITTEST_NOWHERE|wx.LIST_HITTEST_ABOVE|wx.LIST_HITTEST_BELOW): # empty list or below last item
                index = self.GetItemCount() # append to end of list
            elif self.GetItemCount() > 0:
                if y <= self.GetItemRect(0).y: # clicked just above first item
                    index = 0 # append to top of list
                else:
                    index = self.GetItemCount() + 1 # append to end of list
        else: # clicked on an item
            # Get bounding rectangle for the item the user is dropping over.
            rect = self.GetItemRect(index)

            # If the user is dropping into the lower half of the rect, we want to insert _after_ this item.
            # Correct for the fact that there may be a heading involved
            if y > rect.y - self.GetItemRect(0).y + rect.height/2:
                index += 1

        for i in seq: # insert the item data
            idx = self.InsertStringItem(index, i[2])
            self.SetItemData(idx, i[1])
            for j in range(1, self.GetColumnCount()):
                try: # Target list can have more columns than source
                    self.SetStringItem(idx, j, i[2+j])
                except:
                    pass # ignore the extra columns
            index += 1
        self.parent.OnRefresh(evt= None)
class DragListStripedControlFields(DragListStriped):
    def __init__(self, *args, **params):
        self.alowedFields= params.pop('allowedFields')
        DragListStriped.__init__(self, *args, **params)

    # overwrite method to control de insert items
    def _insert(self, x, y, seq):
        """ Insert text at given x, y coordinates --- used with drag-and-drop. """
        if not self.addDroopFields:
            return
        # chek if the drag data is allowed
        if not (seq[-1][-1] in self.alowedFields):
            return
        # Find insertion point.
        index, flags = self.HitTest((x, y))

        if index == wx.NOT_FOUND: # not clicked on an item
            if flags & (wx.LIST_HITTEST_NOWHERE|wx.LIST_HITTEST_ABOVE|wx.LIST_HITTEST_BELOW): # empty list or below last item
                index = self.GetItemCount() # append to end of list
            elif self.GetItemCount() > 0:
                if y <= self.GetItemRect(0).y: # clicked just above first item
                    index = 0 # append to top of list
                else:
                    index = self.GetItemCount() + 1 # append to end of list
        else: # clicked on an item
            # Get bounding rectangle for the item the user is dropping over.
            rect = self.GetItemRect(index)

            # If the user is dropping into the lower half of the rect, we want to insert _after_ this item.
            # Correct for the fact that there may be a heading involved
            if y > rect.y - self.GetItemRect(0).y + rect.height/2:
                index += 1

        for i in seq: # insert the item data
            idx = self.InsertStringItem(index, i[2])
            self.SetItemData(idx, i[1])
            for j in range(1, self.GetColumnCount()):
                try: # Target list can have more columns than source
                    self.SetStringItem(idx, j, i[2+j])
                except:
                    pass # ignore the extra columns
            index += 1
        self.parent.OnRefresh(evt= None)

class DragListCustomFields(DragListStriped):
    def __init__(self, parent, *args, **params):
        self.parent= parent
        self.__env= None
        self.ydata= []
        # current source of data
        self.cs= parent.cs
        self.columnsChoices= params.pop('columnsChoices')
        DragListStriped.__init__(self, parent, *args, **params)

    # overwrite method to control de insert items
    @property
    def env(self):
        if self.__env == None:
            # making available useful object to the shell
            import shapefile
            import adodbapi
            import scikits.statsmodels.api as sm ##import statsmodels.api as sm
            from easyDialog import Ctrl
            from slbTools import homogenize 
            import dict2xml
            import numpy
            import scipy
            from statlib import stats
            import sys
            frame= wx.GetApp().frame
            env = {'grid':   frame.grid,
                   'col':    frame.grid.GetCol,
                   'numpy':  numpy,
                   'homogenize': homogenize,
                   'scipy':  scipy,
                   'stats':  stats,
                   #'getPath':self.getPath,
                   'sm':     sm, # statmodels
                   'sh':     shapefile,
                   'adodbapi': adodbapi,
                   'dict2xml': dict2xml,
                   #'db':     frame.db, # mdb manipulation
                   }
            # path of modules
            pathInit = sys.argv[0].decode( sys.getfilesystemencoding())
            ##pathModules = os.path.join( pathInit, 'Modules')
            ##sys.path.append( pathModules)
            # Add the path of modules
            self._env = env
        return self._env

    def _insert(self, x, y, seq):
        """ Insert text at given x, y coordinates --- used with drag-and-drop. """
        if not self.addDroopFields:
            return

        # Find insertion point.
        self.index, self.flags = self.HitTest((x, y))

        # show the transform Panel
        self.goCustomField(None, x, y, seq)

    def _endInsert(self, evt, *args, **params):
        try:
            responseCol, expresion, foundVarNames = self.__TransformFrame.GetValue()
        except:
            return
        x, y, seq = self.__TransformFrame.args
        fieldName, expresion, foundVarNames = self.__TransformFrame.GetValue()
        newdata= self.ydata
        newdata.extend(foundVarNames)
        self.ydata= list(set(newdata)) 
        self.__TransformFrame.Close()
        seq[-1][-1]= fieldName
        seq[-1].append(expresion)
        # Find insertion point.
        index, flags = self.index, self.flags
        if index == wx.NOT_FOUND: # not clicked on an item
            if flags & (wx.LIST_HITTEST_NOWHERE|wx.LIST_HITTEST_ABOVE|wx.LIST_HITTEST_BELOW): # empty list or below last item
                index = self.GetItemCount() # append to end of list
            elif self.GetItemCount() > 0:
                if y <= self.GetItemRect(0).y: # clicked just above first item
                    index = 0 # append to top of list
                else:
                    index = self.GetItemCount() + 1 # append to end of list
        else: # clicked on an item
            # Get bounding rectangle for the item the user is dropping over.
            rect = self.GetItemRect(index)

            # If the user is dropping into the lower half of the rect, we want to insert _after_ this item.
            # Correct for the fact that there may be a heading involved
            if y > rect.y - self.GetItemRect(0).y + rect.height/2:
                index += 1

        for i in seq: # insert the item data
            idx = self.InsertStringItem(index, i[2])
            self.SetItemData(idx, i[1])
            for j in range(1, self.GetColumnCount()):
                try: # Target list can have more columns than source
                    self.SetStringItem(idx, j, i[2+j])
                except:
                    pass # ignore the extra columns
            index += 1
        self.parent.OnRefresh(evt= None)

    def goCustomField(self, evt, *args, **params):
        self.__TransformFrame = TransformFrame( self.parent, -1, targetVariableAsTextBox= True)
        # dissabling the destination variable in the transformFrame
        setattr(self.__TransformFrame, 'args', args )
        self.__TransformFrame.setAvailableColumns( self.columnsChoices)
        # send objects to the shell
        self._sendObj2Shell(self.__TransformFrame.scriptPanel)
        # making the callback of the eval button
        self.__TransformFrame.pusButtonList[-1].Bind(wx.EVT_BUTTON, self._endInsert)
        self.__TransformFrame.Show(True)

    def _sendObj2Shell(self, shell):
        shell.interp.locals = self.env
        return self.env

class PivotFrame(wx.Frame):
    def __init__( self, parent, *args, **params):        
        """registros= reg
        fieldNames= fields"""
        self.grid = params.pop('grid')
        self.__env = None
        # current source of data
        self.cs= wx.GetApp().frame.formulaBarPanel.lastObject
        if self.cs == None:
            self.cs= wx.GetApp().grid

        self.columnNames = self.grid.colNames

        self.registros= []#params.pop('registros')
        self.fieldNames= []#params.pop('fieldNames')

        wx.Frame.__init__ ( self, parent,  size = wx.Size( 800,600 ), title = "Tabla Pivot", *args, **params) ## id = wx.ID_ANY,  pos = wx.DefaultPosition, , style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )
        self.m_mgr.SetFlags(wx.aui.AUI_MGR_DEFAULT)

        ###############
        ## central panel
        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel1, wx.aui.AuiPaneInfo().Left().CaptionVisible( False ).
                            CloseButton( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).CentrePane())

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.info = wx.InfoBar(self.m_panel1)   
        bSizer1.Add( self.info, 0, wx.ALL|wx.EXPAND, 5 )
        self.miOLV = ObjectListView( self.m_panel1, -1, style= wx.LC_REPORT|wx.SUNKEN_BORDER)
        bSizer1.Add( self.miOLV, 1, wx.ALL|wx.EXPAND, 5 )
        self.m_panel1.SetSizer( bSizer1 )
        self.m_panel1.Layout()
        bSizer1.Fit( self.m_panel1 )
        ###############

        m_listBox1Choices = [[coli] for coli in self.columnNames]
        self.m_listBox1 = DragListStriped(self, style= wx.LC_REPORT|wx.LC_SINGLE_SEL,
                                          fields= ['Campos'], choices= m_listBox1Choices,
                                          delDragFields= False, addDroopFields= False)
        self.m_mgr.AddPane( self.m_listBox1, wx.aui.AuiPaneInfo().Left().
                            CaptionVisible( False ).Caption( u"Filtros" ).
                            CloseButton( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ) )

        self.m_listBox3 = DragListStripedControlFields(self, style= wx.LC_REPORT|wx.LC_SINGLE_SEL,
                              fields= ['Columnas'], choices= [], allowedFields= self.columnNames)
        self.m_mgr.AddPane( self.m_listBox3, wx.aui.AuiPaneInfo().Left().
                            CaptionVisible( False ).Caption( u"Columnas" ).
                            CloseButton( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ) )

        self.m_listBox4 = DragListCustomFields(self, style= wx.LC_REPORT|wx.LC_SINGLE_SEL,
                                    fields= ['Alias','calculos'], choices= [],
                                    columnsChoices= [m[0] for m in m_listBox1Choices],
                                    colWidth= 120)
        self.m_mgr.AddPane( self.m_listBox4, wx.aui.AuiPaneInfo().Left().
                            CaptionVisible( False ).Caption( u"Valores" ).
                            CloseButton( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ) )
        
        self.filtersPanel = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,
                                         wx.DefaultPosition, wx.DefaultSize,
                                         wx.HSCROLL|wx.TE_LEFT|wx.TE_MULTILINE )
        self.m_mgr.AddPane( self.filtersPanel, wx.aui.AuiPaneInfo().Left().
                            CaptionVisible( False ).Caption( u"Filters" ).
                            CloseButton( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ) )

        self.m_auiToolBar3 = wx.aui.AuiToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_TB_HORZ_LAYOUT ) 
        self.Ok = wx.Button( self.m_auiToolBar3, wx.ID_ANY, u"Aceptar", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_auiToolBar3.AddControl( self.Ok )
        self.m_auiToolBar3.AddSeparator()

        self.Refresh = wx.Button( self.m_auiToolBar3, wx.ID_ANY, u"Refrescar", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_auiToolBar3.AddControl( self.Refresh )
        self.m_auiToolBar3.AddSeparator()

        self.Cancel = wx.Button( self.m_auiToolBar3, wx.ID_ANY, u"Cancelar", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_auiToolBar3.AddControl( self.Cancel )
        self.m_auiToolBar3.Realize()

        self.m_mgr.AddPane( self.m_auiToolBar3, wx.aui.AuiPaneInfo().Top().
                            CaptionVisible( False ).CloseButton( False ).
                            PaneBorder( False ).Dock().Fixed().DockFixed( False ).
                            Floatable( False ).Layer( 20 ).ToolbarPane() )

        self.Bind(wx.EVT_BUTTON, self.OnRefresh, self.Refresh)
        self.Bind(wx.EVT_BUTTON, self.onAceptar, self.Ok)
        self.Bind(wx.EVT_BUTTON, self.onCancel, self.Cancel)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnCalcDoubleClick, self.m_listBox4)

        self.InicOLV()
        self.m_mgr.Update()
        self.Centre( wx.BOTH )

    @property
    def env(self):
        if self.__env == None:
            # making available useful object to the shell
            import shapefile
            import adodbapi
            import scikits.statsmodels.api as sm ##import statsmodels.api as sm
            from easyDialog import Ctrl
            from slbTools import homogenize 
            import dict2xml
            import numpy
            import scipy
            from statlib import stats
            import sys
            frame= wx.GetApp().frame
            env = {'grid':   frame.grid,
                   'col':    frame.grid.GetCol,
                   'numpy':  numpy,
                   'homogenize': homogenize,
                   'scipy':  scipy,
                   'stats':  stats,
                   #'getPath':self.getPath,
                   'sm':     sm, # statmodels
                   'sh':     shapefile,
                   'adodbapi': adodbapi,
                   'dict2xml': dict2xml,
                   #'db':     frame.db, # mdb manipulation
                   }
            # path of modules
            pathInit = sys.argv[0].decode( sys.getfilesystemencoding())
            ##pathModules = os.path.join( pathInit, 'Modules')
            ##sys.path.append( pathModules)
            # Add the path of modules
            self._env = env
        return self._env

    def OnRefresh(self, evt):
        # getting the contents of the related lists
        values= self._getListValues()
        if len(values[0]) == 0:
            return
        if len(values[1]) == 0:
            message= __("Please select at least one field for the columns")
            self.showMessage(message)
            return
        if len(values[2]) == 0:
            message= __("Please select at least one field for the values")
            self.showMessage(message)
            return
        # making the calculation
        from slbTools import GroupData
        from collections import namedtuple
        from slbTools import concat
        import re
        grid= self.cs
        group= GroupData(env= self.env)
        group.xdata=   [grid.GetCol(name, True) for name in values[1]]
        # reading the calculated fields
        patern= "[a-zA-Z_][a-zA-Z0-9\._]*"
        posibleNames= list()

        for expresion in [val[1] for val in values[2]]:
            posibleNames.extend(re.findall(patern, expresion))            
        posibleNames= list(set(posibleNames))

        group.ydata= [grid.GetCol(name, True) for name in posibleNames if name in self.columnNames]
        group.yvaluesAlias=  [val[0].replace(' ','') for val in values[2]]
        group.yvalues= [val[1].replace(' ','') for val in values[2]]

        res= list()
        for pos, lis in enumerate( group.getAsRow()):
            if pos == 0:
                self.fieldNames= group.getAsRow()[0]
                n= namedtuple('registros',concat(self.fieldNames)[0].replace(';',','), verbose=False, rename= False)
                continue
            res.append(n(*lis))
        self.registros= res
        self.InicOLV()

    def onCancel(self, evt):
        self.Close()

    def onAceptar( self, evt):        
        output= wx.GetApp().output
        # getting the contents of the related lists
        values= self._getListValues()
        if len(values[0]) == 0:
            return
        if len(values[1]) == 0:
            message= __("Please select at least one field for the columns")
            self.showMessage(message)
            return
        if len(values[2]) == 0:
            message= __("Please select at least one field for the values")
            self.showMessage(message)
            return
        # making the calculation
        from slbTools import GroupData
        from collections import namedtuple
        from slbTools import concat
        import re
        grid= wx.GetApp().grid
        group= GroupData(env= self.env)
        group.xdata=   [grid.GetCol(name, True) for name in values[1]]
        # reading the calculated fields
        patern= "[a-zA-Z_][a-zA-Z0-9\._]*"
        posibleNames= list()

        for expresion in [val[1] for val in values[2]]:
            posibleNames.extend(re.findall(patern, expresion))            
        posibleNames= list(set(posibleNames))

        group.ydata= [grid.GetCol(name, True) for name in posibleNames if name in self.columnNames]
        group.yvaluesAlias=  [val[0].replace(' ','') for val in values[2]]
        group.yvalues= [val[1].replace(' ','') for val in values[2]]

        output.addPage()
        for lis in group.getAsRow():
            output.addRowData( lis)
        self.Close()
        return

    def _getListValues(self):
        choices1 = self.m_listBox1.choices
        choices2 = [self.m_listBox3.GetItem(itemNumber).GetText() for itemNumber in range(self.m_listBox3.ItemCount)]
        lb4= self.m_listBox4
        choices3 = [[lb4.GetItem(itemNumber,col).GetText() for col in range(lb4.ColumnCount)] for itemNumber in range(lb4.ItemCount)]
        return (choices1, choices2, choices3, lb4.ydata)

    def showMessage(self, message):
        self.info.ShowMessage(message, wx.ICON_WARNING)

    def OnDismiss(self, evt= None):
        self.info.Dismiss()
    def OnCalcDoubleClick(self, evt):
        """on double click the calculations column """
        lb4= self.m_listBox4
        if lb4.SelectedItemCount != 1:
            return

        for i in range(lb4.GetItemCount()):
            if lb4.IsSelected(i):
                break

        setattr(lb4,'curChangItem',i)
        data= [lb4.GetItem(i,col).GetText() for col in range(lb4.ColumnCount)]

        # parsing the data to the calculation frame
        self.__TransformFrame = TransformFrame( self, -1, targetVariableAsTextBox= True)
        # dissabling the destination variable in the transformFrame
        self.__TransformFrame.setAvailableColumns( self.columnNames)
        # send objects to the shell
        self._sendObj2Shell(self.__TransformFrame.scriptPanel)
        # changing the contents of some controls
        self.__TransformFrame.variableDestino.Value= data.pop(0)
        self.__TransformFrame._insertText( data.pop(0))
        # making the callback of the eval button
        self.__TransformFrame.pusButtonList[-1].Bind(wx.EVT_BUTTON, self.onLb4Insert)
        self.__TransformFrame.Show(True)

    def onLb4Insert(self,evt):
        cch= self.m_listBox4.curChangItem
        try:    fieldName, expresion, foundVarNames = self.__TransformFrame.GetValue()
        except: return
        self.__TransformFrame.Close()
        lb4= self.m_listBox4
        lb4.SetStringItem(cch, 0, fieldName)
        lb4.SetStringItem(cch, 1, expresion)
        #lb4.Update()

    def _sendObj2Shell(self, shell):
        shell.interp.locals = self.env    
    # Configuración de las columnas y asignación de datos    
    def InicOLV(self):
        # Configuración de columnas
        self.miOLV.SetColumns([ ColumnDefn(fieldName, 'Left', 100,  fieldName)  for fieldName in self.fieldNames])
        # Asignacion de los datos al OLV
        self.miOLV.SetObjects( self.registros)

if __name__ == "__main__":
    app = wx.App(0)
    n= namedtuple('registros', 'posicion1,posicion2,posicion3,categoria', verbose=False, rename=False)
    listado = PivotPanel(None, fieldNames= n._fields, 
                         registros= [n(1, 2, 3, 'informacion 1'),
                                     n(2, 3, 4, 'informacion 2'),
                                     n(4, 5, 1, 'informacion 3'),
                                     n(2, 4, 2, 'informacion 1'),
                                     n(1, 7, 3, 'informacion 2')])
    listado.Show()
    app.MainLoop()