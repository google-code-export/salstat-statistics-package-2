'''
Created on 16/05/2012

@author: USUARIO
'''
'''Easily create a dialog'''
__all__= ['Dialog']

import wx
from numpy import ndarray
import os
import re

_WILDCARD= "Supported Files (*.txt;*.csv;*.xlsx;*.xls)|*.txt;*.csv;*xlsx;*.xls|"\
    "Excel 2010 File (*.xlsx)|*.xlsx|" \
    "Excel 2003 File (*.xls)|*.xls|" \
    "Txt file (*.txt)|*.txt|" \
    "Csv file (*.csv)|*.csv"

def getPath( *args, **params):
    try: wildCard= params.pop('wildcard')
    except: wildCard= _WILDCARD

    dlg = wx.FileDialog(None, _("Load Data File"), "","",
                        wildcard= wildCard,
                        style = wx.OPEN)
    ##icon = imageEmbed().logo16()
    ##dlg.SetIcon(icon)

    if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        return None

    fileName= dlg.GetFilename()
    fullPath= dlg.Path
    dlg.Destroy()
    junk, filterIndex = os.path.splitext(fileName)
    pattern= "\*(.[a-zA-Z0-9]*)"
    allowedExtensions= list(set( re.findall(pattern, wildCard)))
    allowedExtensions= list(set([res.lower() for res in allowedExtensions]))
    if filterIndex.lower() in allowedExtensions:
        return fullPath
    return None

def isnumeric(data):
    if isinstance(data, (int, float, long, ndarray)):
        return True
    return False

class DataBaseImport( wx.Panel ):
    """DataBaseImport(parent, dataDict= dict())"""
    def __init__( self, parent, id= wx.ID_ANY,  *args, **params ):
        wx.Panel.__init__ ( self, parent,
                            id = id,
                            pos = wx.DefaultPosition,
                            size =  wx.Size( 420, 240 ),
                            style = wx.TAB_TRAVERSAL )

        Sizer= wx.BoxSizer( wx.HORIZONTAL )
        #==========================
        # left Panel
        bSizerLEFT = wx.BoxSizer( wx.VERTICAL )
        sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Table Name" ), wx.VERTICAL )
        sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Field Names" ), wx.VERTICAL )

        self.dataDict = args[0]
        if not isinstance( self.dataDict, (dict,)):
            raise StandardError("dataDict must be a dictionary!")

        m_choice1Choices = self.dataDict.keys()
        self.m_choice1 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice1Choices, 0 )
        self.m_choice1.SetSelection( 0 )
        self.currTableName= m_choice1Choices[0]

        m_listBox1Choices = []
        self.listBox = CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox1Choices, wx.LB_ALWAYS_SB|wx.LB_HSCROLL|wx.LB_MULTIPLE )

        self.listBox.SetItems(self.dataDict[self.dataDict.keys()[0]])
        self.listBox.SetSelection(0)

        sbSizer1.Add( self.m_choice1, 0, wx.ALL|wx.EXPAND, 5 )
        sbSizer2.Add( self.listBox, 1, wx.ALL|wx.EXPAND, 5 )
        bSizerLEFT.Add( sbSizer1, 0, wx.EXPAND, 5 )
        bSizerLEFT.AddSpacer( ( 3, 3), 0, wx.EXPAND, 5 )
        bSizerLEFT.Add( sbSizer2, 1, wx.EXPAND, 5 )
        #======================
        # Right Panel
        bSizerRIGHT = wx.BoxSizer( wx.VERTICAL )
        RIGTH_sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Limit" ), wx.VERTICAL )
        RIGTH_sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Order by" ), wx.VERTICAL )

        limit = IntTextCtrl(self,)

        columnNames= ['Field','Order']
        pairs = makePairs(self, colNames=columnNames,
                          choicesByColumn=[self.dataDict[self.dataDict.keys()[0]], ['asc','desc']],
                          rowNumber=1)
        for colu in range(len(columnNames)):
            pairs.SetColSize( colu, 80 )

        RIGTH_sbSizer1.Add( limit, 1, wx.EXPAND, 5 )
        RIGTH_sbSizer2.Add( pairs, 1, wx.EXPAND, 5 )
        bSizerRIGHT.Add( RIGTH_sbSizer1, 0, wx.EXPAND, 5 )
        bSizerRIGHT.AddSpacer( ( 3, 3), 0, wx.EXPAND, 5 )
        bSizerRIGHT.Add( RIGTH_sbSizer2, 1, wx.EXPAND, 5 )
        #======================
        # JOIN ALL PANELS
        Sizer.Add( bSizerLEFT,  1, wx.EXPAND, 5 )
        Sizer.AddSpacer( ( 3, 3), 0, wx.EXPAND, 5 )
        Sizer.Add( bSizerRIGHT, 1, wx.EXPAND, 5 )
        self.SetSizer( Sizer )
        self.Layout()

        # Connect Events
        self.m_choice1.Bind( wx.EVT_CHOICE, self.OnChoice )

    # Virtual event handlers, overide them in your derived class
    def OnChoice( self, evt ):
        tablename= evt.GetString()
        self.currTableName= tablename
        self.listBox.m_checkList2.SetSelection(0)
        self.listBox.SetItems(self.dataDict[tablename])
        evt.Skip()

    def OnListBox( self, evt ):
        evt.Skip()

    def GetValue(self):
        if len(self.listBox.Checked) > 0:
            prevResult= [self.listBox.Items[pos] for pos in self.listBox.Checked]
        else:
            prevResult= []
        return ( self.currTableName ,prevResult)

class NumTextCtrl( wx.TextCtrl):
    '''a text ctrl that only accepts numbers'''
    def __init__( self, parent, *args, **params):
        wx.TextCtrl.__init__( self, parent, *args, **params)
        self.Bind( wx.EVT_TEXT, self._textChange)
        self.allowed = [ str( x) for x in range( 10)]
        self.allowed.extend([ wx.GetApp().DECIMAL_POINT, '-'])

    def _textChange(self, evt):
        texto = self.Value

        if len(texto) == 0:
            return

        newstr= [ x for x in texto if x in self.allowed]

        if len(newstr) == 0:
            newstr = u''
        else:
            func = lambda x,y: x+y
            newstr= reduce(func, newstr)
        # prevent infinite recursion
        if texto == newstr:
            return

        self.SetValue(newstr)
        evt.Skip()
    def GetAsNumber(self):
        prevResult = self.Value
        if len(prevResult) == 0:
            prevResult = None
        else:
            try:
                prevResult = float(prevResult.replace(wx.GetApp().DECIMAL_POINT, '.'))
            except:
                prevResult = None
        return prevResult

    def GetValue(self):
        return self.GetAsNumber()

class IntTextCtrl( NumTextCtrl):
    '''a text ctrl that only accepts numbers'''
    def __init__( self, parent, *args, **params):
        wx.TextCtrl.__init__( self, parent, *args, **params)
        self.Bind( wx.EVT_TEXT, self._textChange)
        self.allowed = [ str( x) for x in range( 10)]

    def _textChange( self, evt):
        texto = self.Value

        newstr= [ x for x in texto if x in self.allowed]

        if len( newstr) == 0:
            newstr = u''
        else:
            func = lambda x,y: x+y
            newstr= reduce( func, newstr)

        # prevent infinite recursion
        if texto == newstr:
            return

        self.SetValue( newstr)
        evt.Skip()

    def GetAsNumber( self):
        prevResult = self.Value
        if len( prevResult) == 0:
            prevResult = None
        else:
            try:
                prevResult = int( prevResult)
            except:
                prevResult = None

        return prevResult

class CheckListBox( wx.Panel, object ):
    def __init__( self, parent , *args, **params):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1, -1 ), style = wx.TAB_TRAVERSAL )

        try:     _= wx.GetApp()._
        except:  _= lambda x: x

        bSizer8 = wx.BoxSizer( wx.VERTICAL )

        bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_button1 = wx.Button( self, wx.ID_ANY, _(u"All"), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        bSizer9.Add( self.m_button1, 0, 0, 5 )

        self.m_button2 = wx.Button( self, wx.ID_ANY, _(u"None"), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        bSizer9.Add( self.m_button2, 0, 0, 5 )

        self.m_button3 = wx.Button( self, wx.ID_ANY, _(u"Invert"), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        bSizer9.Add( self.m_button3, 0, 0, 5 )

        bSizer8.Add( bSizer9, 0, wx.EXPAND, 5 )

        self.m_checkList2 = wx.CheckListBox( self, *args, **params )
        bSizer8.Add( self.m_checkList2, 1, wx.EXPAND, 5 )

        self.SetSizer( bSizer8 )
        self.Layout()

        # Connect Events
        self.m_button1.Bind( wx.EVT_BUTTON, self.All )
        self.m_button2.Bind( wx.EVT_BUTTON, self.none )
        self.m_button3.Bind( wx.EVT_BUTTON, self.Invert )

    def __getattribute__(self, name):
        #import types
        #types.MethodType(self, instance, instance.__class__)
        try:
            return object.__getattribute__(self, name)

        except AttributeError:
            wrapee = self.m_checkList2.__getattribute__( name)
            try:
                return getattr(wrapee, name)
            except AttributeError:
                return wrapee  # detect a property value

    # Virtual event handlers, override them in your derived class
    def All( self, event ):
        self.m_checkList2.Checked= range(len(self.m_checkList2.Items))
        customEvent = wx.PyCommandEvent(wx.EVT_CHECKLISTBOX.typeId, self.m_checkList2.GetId())
        self.GetEventHandler().ProcessEvent(customEvent)

    def none( self, event ):
        self.m_checkList2.Checked= ()
        customEvent = wx.PyCommandEvent(wx.EVT_CHECKLISTBOX.typeId, self.m_checkList2.GetId())
        self.GetEventHandler().ProcessEvent(customEvent)

    def Invert( self, event ):
        # identifying not checked
        checked= self.m_checkList2.Checked
        notchecked= [pos for pos in range(len((self.m_checkList2.Items)))
                     if not(pos in checked)]
        self.m_checkList2.Checked= ()
        self.m_checkList2.Checked= notchecked
        customEvent = wx.PyCommandEvent(wx.EVT_CHECKLISTBOX.typeId, self.m_checkList2.GetId())
        self.GetEventHandler().ProcessEvent(customEvent)

# creating a class to make pairs
#<p> INIT MAKE PAIRS
import  wx.grid as gridlib
class _CustomDataTable( gridlib.PyGridTableBase):
    def __init__( self, columnNames, choiceNames, rowNumber, choicesByColumn=[]):
        gridlib.PyGridTableBase.__init__( self)
        try:     _= wx.GetApp()._
        except:  _= lambda x: x

        if isinstance(choicesByColumn, (list,)):
            if len(choicesByColumn) > 0:
                if len(choicesByColumn) !=  len(columnNames):
                    raise StandardError("Invalid amount of choicesbyColumn")
                choiceNames= choicesByColumn
            else:
                if isinstance( choiceNames, (str, unicode)):
                    choiceNames= [choiceNames]*len( columnNames)
                elif isinstance(choiceNames, (list, tuple)):
                    choiceNames= [choiceNames]*len(columnNames)
                else:
                    raise StandardError("Invalid choices!")

        self.colLabels = columnNames
        group= lambda x,y: x+','+y
        choices= list()
        for choicesByColumni in choiceNames:
            if len( choicesByColumni) > 1:
                #colsResume= list()
                #for choice in choicesByColumni:
                #    try:
                #        if choice == None:
                #            # the selected form correspond to a text editor
                #            colsResume.append(None)
                #            continue
                #    except:
                #        pass
                colsResume= reduce( group,  choicesByColumni[1:],  choicesByColumni[0])

            elif len( choicesByColumni) == 1:
                colsResume= choicesByColumni
            else:
                raise StandardError( _(u'You input a bad type data as choiceNames variable'))
            choices.append(colsResume)

        gvalue= gridlib.GRID_VALUE_CHOICE 
        self.dataTypes= list()
        for colResume in choices:
            if colResume != None:
                self.dataTypes.append( gvalue + ":,"+ colResume)
            else:
                self.dataTypes.append('string')

        if rowNumber == 0:
            self.data= [[] for i in range(len(choices))]
        elif rowNumber > 0:
            self.data= [[u'' for i in range(len(choices))] for j in range(rowNumber)]
        else:
            raise StandardError("The number of columns must be greater or equal to zero!")
    #--------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberRows(self):
        return  len(self.data)+1

    def GetNumberCols(self):
        return len(self.data[0])

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return True

    # Get/Set values in the table.  The Python version of these
    # methods can handle any data-type, (as long as the Editor and
    # Renderer understands the type too,) not just strings as in the
    # C++ version.
    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        def innerSetValue(row, col, value):
            try:
                self.data[row][col] = value
            except IndexError:
                # add a new row
                self.data.append([''] * self.GetNumberCols())
                innerSetValue(row, col, value)

                # tell the grid we've added a row
                msg = gridlib.GridTableMessage(self,            # The table
                                               gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                                               1                                       # how many
                                               )

                self.GetView().ProcessTableMessage(msg)
        innerSetValue(row, col, value) 

    #--------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        #print col
        return self.colLabels[col]

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        return self.dataTypes[col]

    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, typeName):
        prev= self.dataTypes[col]
        if prev != 'string':
            prev= prev[col]
            colType = prev.split(':')[0]
        else:
            colTpe= 'string'
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)

class _CustTableGrid(gridlib.Grid):
    def __init__(self, parent, colNames=['ColName1','ColName2'], choices= ['opt1','opt2'], rowNumber= 2, choicesByColumn=[]):
        gridlib.Grid.__init__(self, parent, -1)
        table = _CustomDataTable(colNames, choices, rowNumber, choicesByColumn)
        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(table, True)
        # self.SetRowLabelSize(0)
        self.SetMargins(0,0)
        self.SetRowLabelSize( 40 )
        self.AutoSizeColumns(False)
        gridlib.EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)
    ## I do this because I don't like the default behaviour of not starting the
    ## cell editor on double clicks, but only a second click.
    def OnLeftDClick(self, evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

class makePairs(wx.Panel):
    def __init__(self, parent, id= wx.ID_ANY,
                 colNames=['col1','col2'],
                 choices=['opt1','opt2','opt3'],\
                 rowNumber=0,
                 choicesByColumn=[]):

        wx.Panel.__init__(self, parent, id, style=0)
        self.colNames = colNames
        self.choices = choices
        self.rowNumber = rowNumber
        self.choicesByColumn = choicesByColumn

        self.grid = _CustTableGrid(self, colNames, choices, rowNumber, choicesByColumn)
        self.bs = wx.BoxSizer(wx.VERTICAL)
        self.bs.Add(self.grid, 1, wx.GROW|wx.ALL, 5)
        #bs.Add(b)
        self.SetSizer(self.bs)

    def __getattribute__(self, name):
        '''wraps the functions to the grid
        emulating a grid control'''
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self.grid.__getattribute__(name)

    def GetValue(self ):
        # reading the data by rows and check consistency
        result= list()
        numCols= self.grid.GetNumberCols()
        for row in range(self.grid.GetNumberRows()):
            rowdata= [self.grid.GetCellValue(row,col) for col in range(numCols)]
            if numCols == sum([1 for value in rowdata if value != u'']):
                result.append(rowdata)
        return result

    def changeParamsChoices(self, colNames, choices, rowNumber, choicesByColumn):
        # delet the grid
        del(self.grid)
        # creating a new grid
        self.grid= _CustTableGrid(self, colNames, choices, rowNumber, choicesByColumn)
        self.bs.Add(self.grid, 1, wx.GROW|wx.ALL, 5)

#  END MAKE PAIRS /<p>

def translate(a):
    return a
def _siguiente():
    i = 0
    while 1:
        i+= 1
        yield str(i)


class FilePath( wx.Panel ):
    def __init__( self, parent, id , *args, **params):
        wx.Panel.__init__ ( self, parent, id,
                            pos = wx.DefaultPosition,
                            size = wx.Size( -1,-1 ),
                            style = wx.TAB_TRAVERSAL )

        try:     self.path= args[0]
        except:  self.path= None
        try:     self.wildCard= args[1]
        except:  self.wildCard= None

        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
        self.txtCtrl = wx.TextCtrl( self, wx.ID_ANY,
                                    wx.EmptyString, wx.DefaultPosition,
                                    wx.Size( 180,-1 ), 0 )
        bSizer1.Add( self.txtCtrl, 0, wx.ALL, 5 )
        if self.path:
            self.txtCtrl.SetValue( self.path)
        self.button = wx.Button( self, wx.ID_ANY, u'\u2026',
                                 wx.DefaultPosition, wx.DefaultSize,
                                 wx.BU_EXACTFIT )
        bSizer1.Add( self.button, 0, wx.ALL, 5 )
        self.SetSizer( bSizer1 )
        self.Layout()
        self.Bind(wx.EVT_BUTTON, self._onSelectFile, id= self.button.GetId())
        self.txtCtrl.Bind( wx.EVT_TEXT, self._textChange)

    def _textChange(self, evt):
        evt.Skip()
        self.path= self.txtCtrl.Value

    def _onSelectFile(self, evt):
        if self.wildCard == None:
            path= getPath()
        else:
            path= getPath(wildcard= self.wildCard)

        if not (path in (None,'',u'')):
            self.path= path
            self.txtCtrl.SetValue(path)
        evt.Skip()

    def GetValue(self ):
        return self.path

class Dialog ( wx.Dialog):
    ALLOWED= ['StaticText',   'TextCtrl',     'Choice',
              'CheckListBox', 'StaticLine',   'RadioBox',
              'SpinCtrl',     'ToggleButton', 'NumTextCtrl',
              'CheckBox',     'makePairs',    'IntTextCtrl',
              'FilePath']
    def __init__( self, parent = None , settings= dict(), struct = []):
        '''Dialog( parent, settings, struct)

        a function to easily create a wx dialog

        parameters
        settings = {'Title': String title of the wxdialog ,
                    'icon': wxbitmap,
                    '_size': wx.Size(xsize, ysize) the size of the dialog ,
                    '_pos':  wx.Position(-1, -1) the position of the frame,
                    '_style': wx.DIALOG__STYLE of the dialog ,}
        struct = list() information with the data

        allowed controls: 'StaticText',   'TextCtrl',     'Choice',
                          'CheckListBox', 'StaticLine',   'RadioBox',
                          'SpinCtrl',     'ToggleButton', 'NumTextCtrl',
                          'CheckBox',     'makePairs',    'IntTextCtrl',
        'FilePath'

        struct example:

        >> structure = list()

        >> bt1 = ('StaticText', ('hoja a Imprimir',))
        >> bt2 = ('Button', ('nuevo',))

        >> bt6=  ('TextCtrl', ('Parametro',))

        >> btnChoice = ('Choice',(['opt1','opcion2','opt3'],))

        >> btnListBox = ('CheckListBox',(['opt1','opcion2','opt3'],))

        >> listSeparator = ('StaticLine',('horz',))

        >> bt7 = ('RadioBox',('titulo',['opt1','opt2','opt3'],))
        >> bt8 = ('SpinCtrl', ( 0, 100, 5 )) # (min, max, start)
        >> bt9 = ('ToggleButton', ['toggle'])
        >> bt10= ('CheckBox', ['Accept'])
        >> bt11= ('makePairs', [['col1','col2','col3'],['opt2','opt5'], 8]) # colum names, options, number of rows

        >> structure.append( [bt6, bt2] )
        >> structure.append( [bt6, bt5] )
        >> structure.append( [btnChoice, bt9 ] )
        >> structure.append( [listSeparator])
        >> structure.append( [btnListBox , bt1])
        >> structure.append( [bt7, ])
        >> structure.append( [bt8, ])
        >> structure.append( [bt11, ])

        to see an example run the class as a main script
        '''

        self.ALLOWED= ['StaticText',   'TextCtrl',     'Choice',
                       'CheckListBox', 'StaticLine',   'RadioBox',
                       'SpinCtrl',     'ToggleButton', 'NumTextCtrl',
                       'CheckBox',     'makePairs',    'IntTextCtrl',
                       'FilePath',     'DataBaseImport']
        self.ctrlNum = _siguiente()
        self.sizerNum= _siguiente()

        params = {'Title':  wx.EmptyString,
                  'icon':   None,
                  'size':   wx.DefaultSize,
                  '_pos':   wx.DefaultPosition,
                  '_style': wx.wx.DEFAULT_DIALOG_STYLE}

        for key, value in params.items():
            try:
                params[key] = settings[key]
            except:
                pass

        wx.Dialog.__init__ ( self, parent, 
                             id=     wx.ID_ANY,
                             title=  params.pop('Title'),
                             pos=    params.pop('_pos'),
                             size=   params.pop('size'),
                             style=  params.pop('_style') )

        #< setting the icon
        icon= params.pop('icon')
        if icon == None:
            try:
                icon= wx.GetApp().icon
            except AttributeError:
                icon= wx.EmptyIcon()
        self.SetIcon(icon)
        # setting the icon/>
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        # getting the horizontal border size
        bSizer1.Fit( self )
        xBorderSize= self.Size[0]
        
        self.m_scrolledWindow1 = wx.ScrolledWindow( self, wx.ID_ANY,
                                                    wx.DefaultPosition, wx.DefaultSize,
                                                    wx.DOUBLE_BORDER|wx.HSCROLL|wx.VSCROLL )
        self.m_scrolledWindow1.SetScrollRate( 5, 5 )
        bSizer3 = wx.BoxSizer( wx.VERTICAL )
        self.sisers= list()
        self.ctrls= list()
        self._allow= self.ALLOWED
        self._allow2get= ['TextCtrl','Choice',
                          'CheckListBox','RadioBox',
                          'SpinCtrl','ToggleButton','NumTextCtrl',
                          'CheckBox', 'makePairs','IntTextCtrl', 
                          'FilePath', 'DataBaseImport']

        bSizer1.Add( self.m_scrolledWindow1, 1, wx.EXPAND, 5 )
        
        # ok cancel buttoms
        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize()
        
        depthSize=  wx.GetDisplayDepth()
        buttonOkCancelSize= (self.m_sdbSizer1Cancel.Size[0] + self.m_sdbSizer1OK.Size[0] + depthSize,
                             max(self.m_sdbSizer1Cancel.Size[1], self.m_sdbSizer1OK.Size[1]) + depthSize)

        bSizer1.Add( m_sdbSizer1, 0, wx.EXPAND|wx.ALL, 5 )# 
        self.SetSizer( bSizer1 )
        
        # getting the actual size of the dialog
        bSizer1.Fit( self )
        sizeDialog= self.Size

        # adding the custom controls into the scroll dialog
        self.adding(bSizer3, struct)
        self.m_scrolledWindow1.SetSizer( bSizer3 )
        self.m_scrolledWindow1.Layout()
        bSizer3.Fit( self.m_scrolledWindow1 )
        # getting the size of the scrolldialog
        sizeScroll= self.m_scrolledWindow1.Size
        
        # getting the required size
        requiredSize= (sizeScroll[0] + xBorderSize,
                       sizeDialog[1] + sizeScroll[1]+ 0)

        # getting the border size
        maxSize= wx.GetDisplaySize()
        allowSize= [min([requiredSize[0], maxSize[0]-10]),
                    min([requiredSize[1], maxSize[1]-10]),]
        minAllowed= [buttonOkCancelSize[0], buttonOkCancelSize[1]]
        allowSize= [max([minAllowed[0], allowSize[0]]), max([minAllowed[1], allowSize[1]])]
        
        # adpat the dialog if needed
        if allowSize[1] == maxSize[1]-10 and allowSize[0] <= maxSize[0]-20:
            allowSize[0]= allowSize[0]+10
        elif allowSize[0] == maxSize[0]-10 and allowSize[1] <= maxSize[1]-20:
            allowSize[1]= allowSize[1]+10

        self.SetSize(wx.Size(allowSize[0], allowSize[1]))
        self.Layout()
        self.Centre( wx.BOTH )
        
    def adding(self, parentSizer, struct ):
        diferents= ['CheckListBox','Choice',]
        for row in struct:
            namebox= 'boxSizer'+ self.ctrlNum.next()
            setattr(self, namebox, wx.FlexGridSizer( 0, len(row), 0, 0 ))
            currSizer= getattr(self, namebox)
            currSizer.SetFlexibleDirection( wx.BOTH )
            currSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
            characters= wx.ALIGN_CENTER_VERTICAL | wx.ALL
            for key, args in row:
                if hasattr(wx, key):
                    #nameCtrl= 'ctrl' + self.sizerNum.next()
                    if key in diferents:
                        data= [wx.DefaultPosition, wx.DefaultSize, ]
                        if len(args) > 1:
                            # se identifica la posicion por defecto del control
                            defaultControlSelection= args[1]
                            data.extend(list((args[0],)))
                        else:
                            defaultControlSelection= None
                            data.extend(list(args))
                        data.append(0)
                        args= data
                    elif key == 'StaticLine':
                        data= [wx.DefaultPosition, wx.DefaultSize, ]
                        if args[0] == 'horz':
                            data.append(wx.LI_HORIZONTAL|wx.DOUBLE_BORDER)
                        else:
                            data.append(wx.LI_VERTICAL|wx.DOUBLE_BORDER)
                        args = data
                        characters = wx.ALL | wx.EXPAND
                    elif key == 'RadioBox':
                        data= [args[0] , wx.DefaultPosition, wx.DefaultSize]
                        data.append(args[1])
                        args= data
                    elif key == 'SpinCtrl':
                        data= [ wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS]
                        data.extend((args))
                        args= data
                    elif key == 'CheckBox':
                        pass
                    if key == 'CheckListBox':
                        self.ctrls.append((key, CheckListBox(self.m_scrolledWindow1, wx.ID_ANY, *args)))
                    else:
                        self.ctrls.append((key, getattr(wx, key)(self.m_scrolledWindow1, wx.ID_ANY, *args)))
                    currCtrl= self.ctrls[-1][1]
                    # setting default values    
                    if self.ctrls[-1][0] == 'Choice':
                        # selecting the last added item
                        if defaultControlSelection != None: # if the user select a default option
                            currCtrl.Selection= defaultControlSelection
                        else : # if the user select a default option
                            currCtrl.Selection= 0

                    currSizer.Add(currCtrl, 0, characters , 5)

                elif key == 'NumTextCtrl':
                    self.ctrls.append((key, NumTextCtrl(self.m_scrolledWindow1, wx.ID_ANY, *args)))
                    currCtrl= self.ctrls[-1][1]
                    currSizer.Add(currCtrl, 0, characters , 5)

                elif key  == 'IntTextCtrl':
                    self.ctrls.append((key, IntTextCtrl(self.m_scrolledWindow1, wx.ID_ANY, *args)))
                    currCtrl= self.ctrls[-1][1]
                    currSizer.Add(currCtrl, 0, characters , 5)

                elif key == 'makePairs':
                    self.ctrls.append((key, makePairs(self.m_scrolledWindow1, wx.ID_ANY, *args)))
                    currCtrl= self.ctrls[-1][1]
                    currSizer.Add(currCtrl, 0, characters , 5)
                    currCtrl.Fit()
                    # limiting the maximun size of the ctrl
                    maxAllowedSize= (300, 350)
                    currCtrl.SetSize(wx.Size(min([currCtrl.GetSize()[0], maxAllowedSize[0]]),
                                             min([currCtrl.GetSize()[1], maxAllowedSize[1]])))

                elif key == 'FilePath':
                    self.ctrls.append((key, FilePath( self.m_scrolledWindow1, wx.ID_ANY, *args)))
                    currCtrl= self.ctrls[-1][1]
                    currSizer.Add(currCtrl, 0, characters , 5)

                elif key == 'DataBaseImport':
                    self.ctrls.append((key, DataBaseImport( self.m_scrolledWindow1, wx.ID_ANY, *args)))
                    currCtrl= self.ctrls[-1][1]
                    currSizer.Add(currCtrl, 0, characters , 5)
                else:
                    raise StandardError("unknow control %s : type .ALLOWED to view all available controls"%key)

                #elif key == 'in':  # not used
                #    self.adding(parentSizer, [args])

            parentSizer.Add( currSizer, 0, wx.EXPAND, 5 )
            parentSizer.Layout()


    def GetValue(self):
        try:
            self.DECIMAL_POINT = wx.GetApp().DECIMAL_POINT
        except AttributeError:
            self.DECIMAL_POINT = '.'

        resultado = list()
        for typectrl, ctrl in self.ctrls:
            if typectrl in self._allow2get:
                if typectrl  in ['TextCtrl','ToggleButton','SpinCtrl']:
                    prevResult = ctrl.Value

                elif typectrl == 'Choice':
                    if len(ctrl.GetItems()) == 0:
                        prevResult= None
                    if ctrl.GetSelection() >= 0:
                        prevResult =  ctrl.GetItems()[ctrl.GetSelection()]
                    else:
                        prevResult= None

                elif typectrl == 'CheckBox':
                    prevResult= ctrl.IsChecked()

                elif typectrl == 'CheckListBox':
                    if len(ctrl.Checked) > 0:
                        prevResult= [ctrl.Items[pos] for pos in ctrl.Checked]
                    else:
                        prevResult= []

                elif typectrl == 'RadioBox':
                    prevResult= ctrl.Selection

                elif typectrl == 'NumTextCtrl':
                    prevResult = ctrl.GetValue()
                    if prevResult == u'':
                        prevResult = None                        
                    elif isnumeric(prevResult):
                        if prevResult == int(prevResult):
                            prevResult == int(prevResult)
                    else:
                        prevResult=  None

                elif typectrl == 'makePairs':
                    prevResult = ctrl.GetValue()
                else:
                    prevResult = ctrl.GetValue()

                resultado.append(prevResult)
        return resultado

class _example( wx.Frame ):
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY,
                            title = wx.EmptyString, pos = wx.DefaultPosition,
                            size = wx.Size( 200, 200 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer10 = wx.BoxSizer( wx.VERTICAL )

        self.m_button8 = wx.Button( self, wx.ID_ANY, u"Show Dialog", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer10.Add( self.m_button8, 0, wx.ALL, 5 )

        self.SetSizer( bSizer10 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_button8.Bind( wx.EVT_BUTTON, self.showDialog )

    # Virtual event handlers, overide them in your derived class
    def showDialog( self, evt ):
        dic= {'Title': 'title'}
        bt1= ('Button',     ['print'])
        bt2= ('StaticText', ['hoja a Imprimir'])
        bt3= ('Button',     ['nuevo'])
        bt4= ('StaticText', ['sebas'])
        bt5= ('StaticText', ['Ingrese la presion'])
        bt6= ('TextCtrl',   ['Parametro'])
        btnChoice=     ('Choice',       [['opt1', 'opcion2', 'opt3']])
        btnListBox=    ('CheckListBox', [['opt1', 'opcion2', 'opt3']])
        listSeparator= ('StaticLine',   ['horz'])
        bt7= ('RadioBox',     ['title', ['opt1', 'opt2', 'opt3']])
        bt8= ('SpinCtrl',     [ 0, 100, 5 ]) # (min, max, start)
        bt9= ('ToggleButton', ['toggle'])
        bt10= ['makePairs',[['column '+str(i) for i in range(2)],['opt1','opt2'],5]]
        bt11= ['FilePath', []]

        structure= list()
        structure.append( [bt6, bt2] )
        structure.append( [bt6, bt5] )
        structure.append( [btnChoice, bt9 ] )
        structure.append( [listSeparator])
        structure.append( [btnListBox , bt1])
        structure.append( [bt7, ])
        structure.append( [bt8, ])
        structure.append( [bt10, ])
        structure.append( [bt11, ])

        dlg= Dialog(self, settings = dic, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values= dlg.GetValue()
            print values
        dlg.Destroy()

if __name__ == '__main__':
    app= wx.App()
    app.translate= translate
    frame= _example(None)
    app.DECIMALPOINT = '.'
    frame.Show()
    app.MainLoop()