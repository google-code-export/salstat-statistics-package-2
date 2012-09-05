# Copyrigth 2012 Sebastian Lopez Buritica 
# Colombia

import  wx
from imagenes import imageEmbed
from openStats import statistics # used in descriptives frame
import math # to be used in transform pane
import numpy
import scipy
from slbTools import isnumeric

if wx.Platform == '__WXMSW__':
    wind = 50
else:
    wind = 0

# creating a class to make pairs
#<p> INIT MAKE PAIRS
import  wx.grid as gridlib
class _CustomDataTable( gridlib.PyGridTableBase):
    def __init__( self, columnNames, choiceNames, rowNumber):
	gridlib.PyGridTableBase.__init__( self)

	if isinstance( choiceNames, (str, unicode)):
	    choiceNames= [choiceNames]*len( columnNames)

	self.colLabels = columnNames
	group= lambda x,y: x+','+y

	if len( choiceNames) >= 1:
	    colsResume= list()
	    for choice in choiceNames:
		try:
		    if choice == None:
			# the selected form correspond to a text editor
			colsResume.append(None)
			continue
		except:
		    pass
		colsResume.append( reduce( group,  choice[1:],  choice[0]))

	elif len( choiceNames) == 1:
	    colsResume= choiceNames[0]*len(columnNames)
	else:
	    raise StandardError( wx.GetApp().translate(u'You input bad type data as choiceNames variable'))

	gvalue= gridlib.GRID_VALUE_CHOICE 
	self.dataTypes= list()
	for colResume in colsResume:
	    if colResume != None:
		self.dataTypes.append( [gvalue + ":,"+colResume for i in range(len(columnNames))])
	    else:
		self.dataTypes.append('string')
	self.data= [[u'' for i in range(len(columnNames))] for j in range(rowNumber)]

    #--------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberRows(self):
	return  len(self.data)

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
	print col
	return self.colLabels[col]

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
	return self.dataTypes[col][col]

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
    def __init__(self, parent, colNames, choices, rowNumber):
	gridlib.Grid.__init__(self, parent, -1)
	table = _CustomDataTable(colNames, choices, rowNumber)
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
    def __init__(self, parent, id, colNames, choices, rowNumber= 20):
	wx.Panel.__init__(self, parent, id, style=0)

	self.grid = _CustTableGrid(self, colNames, choices, rowNumber)
	#b = wx.Button(self, -1, "Another Control...")
	#b.SetDefault()
	bs = wx.BoxSizer(wx.VERTICAL)
	bs.Add(self.grid, 1, wx.GROW|wx.ALL, 5)
	#bs.Add(b)
	self.SetSizer(bs)

    def GetValue(self ):
	# reading the data by rows and check consistency
	result= list()
	numCols= self.grid.GetNumberCols()
	for row in range(self.grid.GetNumberRows()):
	    rowdata= [self.grid.GetCellValue(row,col) for col in range(numCols)]
	    if numCols == sum([1 for value in rowdata if value != u'']):
		result.append(rowdata)
	return result

#  END MAKE PAIRS /<p>

#<p> INIT SELECT A TYPE OF CHART
class _panelSubPlot(wx.ScrolledWindow):
    def __init__(self, *args, **param):
	wx.ScrolledWindow.__init__(self, *args, **param)
	self.SetScrollRate( 5, 5 )
	self.sizer = wx.WrapSizer( )
	self.SetSizer( self.sizer )

    def createButtons( self, buttonsData):
	# buttonsData = [(label, image, callback, id), (...), ...]
	for label, image, callback, id in buttonsData:
	    self._createbutton( image, label, callback)
	self.Layout()
	self.Centre( wx.BOTH )

    def _createbutton( self, img, label, callback= None):
	if len(label) > 20:
	    label= label[:20] + '\n' + label[20:]

	newSizer=   wx.BoxSizer( wx.VERTICAL )
	button=     wx.BitmapButton( self, wx.ID_ANY, img,
	                             wx.DefaultPosition, wx.DefaultSize,
	                             wx.BU_AUTODRAW )
	newSizer.Add( button, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
	staticText= wx.StaticText( self, wx.ID_ANY, label,
	                           wx.DefaultPosition, wx.DefaultSize, 0 )
	staticText.Wrap( -1 )
	newSizer.Add( staticText, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
	self.sizer.Add( newSizer, 0, 0, 5 )
	button.Bind(wx.EVT_BUTTON, callback)

class createPlotSelectionPanel( wx.Panel):
    def __init__( self, *args, **params):
	wx.Panel.__init__( self, *args, **params)
	self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
	bSizer1 = wx.BoxSizer( wx.VERTICAL )
	self.notebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

	bSizer1.Add( self.notebook, 1, wx.EXPAND, 5 )
	self.SetSizer( bSizer1 )
	self.Layout()
	self.Centre( wx.BOTH )

    def createPanels(self, dataPanels):
	for dat in dataPanels:
	    panel = _panelSubPlot( self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize)
	    panel.createButtons( dat[-1])
	    self.notebook.AddPage( panel, dat[0], False )

	self.Layout()
	self.Centre( wx.BOTH )

#  END SELECT A TYPE OF CHART /<p>

class SaveDialog(wx.Dialog):
    def __init__(self, parent):  
	translate= wx.GetApp().translate
	wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = translate(u"Save data?"), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
	self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
	self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

	bSizer1 = wx.BoxSizer( wx.VERTICAL )

	self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, translate(u"You have unsaved data!"), wx.DefaultPosition, wx.DefaultSize, 0 )
	self.m_staticText1.Wrap( -1 )
	bSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

	self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, translate(u"Do you wish to save it?"), wx.DefaultPosition, wx.DefaultSize, 0 )
	self.m_staticText2.Wrap( -1 )
	bSizer1.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

	bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

	self.m_button1 = wx.Button( self, wx.ID_ANY, translate(u"Save"), wx.DefaultPosition, wx.DefaultSize, 0 )
	bSizer2.Add( self.m_button1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

	self.m_button2 = wx.Button( self, wx.ID_ANY, translate(u"Discard"), wx.DefaultPosition, wx.DefaultSize, 0 )
	bSizer2.Add( self.m_button2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

	self.m_button3 = wx.Button( self, wx.ID_ANY, translate(u"Cancel"), wx.DefaultPosition, wx.DefaultSize, 0 )
	bSizer2.Add( self.m_button3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

	bSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )

	self.SetSizer( bSizer1 )
	self.Layout()
	bSizer1.Fit( self )

	self.Centre( wx.BOTH )

	self.Bind(wx.EVT_BUTTON, self.SaveData,     id = self.m_button1.GetId())
	self.Bind(wx.EVT_BUTTON, self.DiscardData,  id = self.m_button2.GetId())
	self.Bind(wx.EVT_BUTTON, self.CancelDialog, id = self.m_button3.GetId())

    def SaveData(self, evt):
	wx.GetApp().frame.grid.Saved = True
	wx.GetApp().frame.grid.SaveXlsAs(self) # will it be ASCII or XML?
	# wx.GetApp().output.Close(True)
	self.Close(True)
	wx.GetApp().frame.Close(True)

    def DiscardData(self, evt):
	self.Close(True)
	wx.GetApp().frame.Close(True)


    def CancelDialog(self, evt):
	self.Close(True)

class VariablesFrame(wx.Dialog):
    def __init__(self,parent,id):
	wx.Dialog.__init__(self, parent,id,"SalStat - Variables", \
	                   size=(500,190+wind))
	translate= wx.GetApp().translate
	self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
	self.m_mgr = wx.aui.AuiManager()
	self.m_mgr.SetManagedWindow( self )

	self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )

	bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

	okaybutton = wx.Button(self.m_panel1 ,   2001, translate( "Okay"), wx.DefaultPosition, wx.DefaultSize, 0 )
	cancelbutton = wx.Button(self.m_panel1 , 2002, translate( "Cancel"), wx.DefaultPosition, wx.DefaultSize, 0 )

	bSizer2.Add( okaybutton, 0, wx.ALL, 5 )
	bSizer2.Add( cancelbutton , 0, wx.ALL, 5 )

	self.m_panel1.SetSizer( bSizer2 )
	self.m_panel1.Layout()
	bSizer2.Fit( self.m_panel1 )
	self.m_mgr.AddPane( self.m_panel1, wx.aui.AuiPaneInfo().Bottom().
	                    CaptionVisible( False ).CloseButton( False ).PaneBorder( False ).
	                    Dock().Resizable().FloatingSize( wx.Size( 170,54 ) ).
	                    DockFixed( False ).LeftDockable( False ).RightDockable( False ).
	                    MinSize( wx.Size( -1,30 ) ).Layer( 10 ) )

	self.vargrid = wx.grid.Grid( self,-1,) #
	self.vargrid.SetRowLabelSize( 120)
	self.vargrid.SetDefaultRowSize( 27, True)
	maxcols = wx.GetApp().frame.grid.GetNumberCols()
	self.vargrid.CreateGrid( 3,maxcols)
	for i in range( maxcols):
	    oldlabel = wx.GetApp().frame.grid.GetColLabelValue( i)
	    self.vargrid.SetDefaultCellAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
	    if wx.Platform == '__WXMAC__':
		self.vargrid.SetGridLineColour( "#b7b7b7")
		self.vargrid.SetLabelBackgroundColour( "#d2d2d2")
		self.vargrid.SetLabelTextColour( "#444444")
	    self.vargrid.SetCellValue( 0, i, oldlabel)
	self.vargrid.SetRowLabelValue( 0, translate( u"Variable Name"))
	self.vargrid.SetRowLabelValue( 1, translate( u"Decimal Places"))
	self.vargrid.SetRowLabelValue( 2, translate( u"Missing Value"))

	self.m_mgr.AddPane( self.vargrid, wx.aui.AuiPaneInfo() .Left() .CaptionVisible( False ).PaneBorder( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).DockFixed( False ).CentrePane() )

	self.m_mgr.Update()
	self.Centre( wx.BOTH )

	self.Bind(wx.EVT_BUTTON, self.OnOkayVariables, id= 2001)
	self.Bind(wx.EVT_BUTTON, self.OnCloseVariables, id =  2002)

    # this method needs to work out the other variables too
    def OnOkayVariables(self, evt):
	for i in range(wx.GetApp().frame.grid.GetNumberCols()-1):
	    newlabel = self.vargrid.GetCellValue(0, i)
	    if (newlabel != ''):
		wx.GetApp().frame.grid.SetColLabelValue(i, newlabel)
	    newsig = self.vargrid.GetCellValue(1, i)
	    if (newsig != ''):
		try:
		    wx.GetApp().frame.grid.SetColFormatFloat(i, -1, int(newsig))
		except ZeroDivisionError:
		    pass
	wx.GetApp().frame.grid.ForceRefresh()
	self.Close(True)

    def OnCloseVariables(self, evt):
	self.Close(True)

#---------------------------------------------------------------------------
# user selects which cols to analyse, and what stats to have
DescList= [u'N',
           u'Sum',
           u'Mean',
           u'missing',
           u'Variance',
           u'Standard Deviation',
           u'Standard Error',
           u'Sum of Squares',#'Sum of Squared Devs',
           u'Coefficient of Variation',
           u'Minimum',
           u'Maximum',
           u'Range',
           u'Number Missing',
           u'Geometric Mean',
           u'Harmonic Mean',
           u'Skewness',u'Kurtosis', 
           u'Median',        #'Median Absolute Deviation',
           u'Mode', ] #'Interquartile Range', 'Number of Unique Levels']

class ManyDescriptives:
    def __init__(self, source, ds):
	__x__= len(ds)
	if __x__ == 0:
	    return
	data= {'name': "Many Descriptives",
	       'size': (0,0),
	       'nameCol': list(),
	       'data': []}
	data['nameCol'].append('Statistic')
	data['nameCol'].extend([ds[i].Name for i in range(__x__)])
	listaDatos= ((u'N', 'N'),
	             (u'Sum', 'suma'),
	             (u'Mean', 'mean'),
	             (u'missing', 'missing'),
	             (u'Variance', 'variance'), # changing by the correct
	             (u'Standard Deviation', 'stddev'),
	             (u'Standard Error', 'stderr'),
	             (u'Sum of Squares', 'sumsquares'),
	             (u'Sum of Squared Devs', 'ssdevs'),
	             (u'Coefficient of Variation', 'coeffvar'),
	             (u'Minimum', 'minimum'),
	             (u'Maximum', 'maximum'),
	             (u'Range', 'range'),
	             (u'Number Missing', 'missing'),
	             (u'Geometric Mean', 'geomean'),
	             (u'Harmonic Mean', 'harmmean'),
	             (u'Skewness', 'skewness'),
	             (u'Kurtosis', 'kurtosis'),
	             (u'Median', 'median'),
	             (u'Median Absolute Deviation', 'mad'),
	             (u'Mode', 'mode'),#    'Interquartile Range', None,
	             (u'Number of Unique Levels', 'numberuniques')
	             )
	funcTrans= dict()
	for key,value in listaDatos:
	    funcTrans[wx.GetApp().translate(key)] = value

	items= source.DescChoice.GetItems()
	itemsSelected = source.DescChoice.GetChecked()
	if len( itemsSelected) == 0:
	    return
	firstcol= [wx.GetApp().translate(u'Descriptives')]
	firstcol.extend([items[pos] for pos in itemsSelected])
	wx.GetApp().output.addColData( firstcol, wx.GetApp().translate(u'Descriptive statistics'))
	itemNamesSelected= [ items[ itemnumber] for  itemnumber in itemsSelected ]
	for i, nameCol in zip(range(__x__), data['nameCol'][1:]):
	    statsi = ds[i]
	    result= [nameCol]
	    result.extend([getattr( statsi,funcTrans[ itemNameSelected]) for itemNameSelected in itemNamesSelected])
	    wx.GetApp().output.addColData( result)

class DescriptivesFrame(wx.Dialog):
    def __init__( self, parent, id ):
	wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY,
	                     title = wx.GetApp().translate("Descriptive Statistics"),
	                     pos = wx.DefaultPosition, size = wx.Size( 420,326 ),
	                     style = wx.DEFAULT_DIALOG_STYLE )

	self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
	icon = imageEmbed().logo16()
	self.SetIcon(icon)
	ColumnList, self.colnums  = wx.GetApp().frame.grid.GetUsedCols()

	self.m_mgr = wx.aui.AuiManager()
	self.m_mgr.SetManagedWindow( self )
	newDescList= [parent.translate(DescListi) for DescListi in DescList]
	self.DescChoice = CheckListBox(self, wx.ID_ANY,  wx.DefaultPosition, wx.DefaultSize, newDescList, 0 )
	self.m_mgr.AddPane( self.DescChoice, wx.aui.AuiPaneInfo() .Center() .
	                    Caption( wx.GetApp().translate(u"Select Descriptive Statistics") ).CloseButton( False ).
	                    PaneBorder( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).
	                    DockFixed( False ).BottomDockable( False ).TopDockable( False ) )

	self.ColChoice = CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, ColumnList, 0 )
	self.m_mgr.AddPane( self.ColChoice, wx.aui.AuiPaneInfo() .Center() .Caption( wx.GetApp().translate(u"Select Column(s) to Analyse") ).
	                    CloseButton( False ).PaneBorder( False ).Dock().Resizable().
	                    FloatingSize( wx.Size( 161,93 ) ).DockFixed( False ).BottomDockable( False ).
	                    TopDockable( False ).Row( 1 ).Layer( 0 ) )

	self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
	self.m_mgr.AddPane( self.m_panel1, wx.aui.AuiPaneInfo() .Bottom() .CaptionVisible( False ).
	                    CloseButton( False ).PaneBorder( False ).Dock().Resizable().
	                    FloatingSize( wx.DefaultSize ).DockFixed( False ).LeftDockable( False ).
	                    RightDockable( False ).MinSize( wx.Size( -1,30 ) ) )

	bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

	okaybutton = wx.Button( self.m_panel1, wx.ID_ANY, wx.GetApp().translate(u"Ok"), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT  )
	bSizer2.Add( okaybutton, 0, wx.ALL, 5 )

	cancelbutton = wx.Button( self.m_panel1, wx.ID_ANY, wx.GetApp().translate(u"Cancel"), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT  )
	bSizer2.Add( cancelbutton, 0, wx.ALL, 5 )

	self.m_panel1.SetSizer( bSizer2 )
	self.m_panel1.Layout()
	bSizer2.Fit( self.m_panel1 )

	self.m_mgr.Update()
	self.Centre( wx.BOTH )

	self.Bind(wx.EVT_BUTTON, self.OnOkayButton,          id = okaybutton.GetId())
	self.Bind(wx.EVT_BUTTON, self.OnCloseContDesc,       id = cancelbutton.GetId())

    def OnOkayButton(self, evt):
	descs = []
	for i in range(len(self.colnums)):
	    if self.ColChoice.IsChecked(i):
		realColi = self.colnums[i]
		name = wx.GetApp().frame.grid.GetColLabelValue(realColi)
		descs.append(statistics(
		    wx.GetApp().frame.grid.CleanData(realColi), name,
		    wx.GetApp().frame.grid.missing))
	ManyDescriptives(self, descs)
	self.Close(True)

    def OnCloseContDesc(self, evt):
	self.Close(True)

#---------------------------------------------------------------------------
# instance of the tool window that contains the test buttons
# note this is experimental and may not be final
#---------------------------------------------------------------------------
class TransformFrame(wx.Dialog):
    def __init__(self, parent, id= wx.ID_ANY):
	wx.Dialog.__init__( self, parent, id, parent.translate(u"Transformations"),
	                    size=(500,400+wind))
	#set icon for frame (needs x-platform separator!
	self.parent= parent
	x= self.GetClientSize()
	winheight= x[1]
	icon= imageEmbed().logo16()
	self.SetIcon(icon)
	self.transform= ""
	self.transformName= ""
	self.ColumnList, self.colnums= wx.GetApp().frame.grid.GetUsedCols()
	self.cols = wx.GetApp().frame.grid.NumberCols
	l0 = wx.StaticText( self, -1, parent.translate(u"Select Column(s) to Transform"), pos=(10,10))
	self.ColChoice = wx.CheckListBox( self,1102, wx.Point(10,30), \
	                                  wx.Size(230,(winheight * 0.8)), self.ColumnList)
	self.okaybutton = wx.Button( self, wx.ID_ANY, parent.translate(u"Okay"), wx.Point(10,winheight-35))
	self.cancelbutton = wx.Button( self, wx.ID_ANY, parent.translate(u"Cancel"),wx.Point(100,winheight-35))
	# common transformations:
	l1= wx.StaticText( self, -1, parent.translate(u"Common Transformations:"), pos=(250,30))
	self.squareRootButton= wx.Button( self, wx.ID_ANY, parent.translate(u"Square Root"), wx.Point(250, 60))
	self.logButton= wx.Button( self, wx.ID_ANY, parent.translate(u"Logarithmic"),wx.Point(250, 100))
	self.reciprocalButton= wx.Button( self, wx.ID_ANY, parent.translate(u"Reciprocal"), wx.Point(250,140))
	self.squareButton= wx.Button( self, wx.ID_ANY, parent.translate(u"Square"), wx.Point(250,180))
	l2 = wx.StaticText( self, -1, parent.translate(u"Function :"), wx.Point(250, 315))
	self.transformEdit= wx.TextCtrl( self, 1114,pos=(250,335),size=(150,20))
	self.Bind( wx.EVT_BUTTON, self.OnOkayButton,        id = self.okaybutton.GetId())
	self.Bind( wx.EVT_BUTTON, self.OnCloseFrame,        id = self.cancelbutton.GetId())
	self.Bind( wx.EVT_BUTTON, self.squareRootTransform, id = self.squareRootButton.GetId())
	self.Bind( wx.EVT_BUTTON, self.logTransform,        id = self.logButton.GetId())
	self.Bind( wx.EVT_BUTTON, self.reciprocalTransform, id = self.reciprocalButton.GetId())
	self.Bind( wx.EVT_BUTTON, self.squareTransform,     id = self.squareButton.GetId())

    def squareRootTransform(self, evt):
	self.transform = "math.sqrt(x)"
	self.transformEdit.SetValue(self.transform)
	self.transformName =  self.parent.translate(u" Square Root")

    def logTransform(self, evt):
	self.transform = "math.log(x)"
	self.transformEdit.SetValue(self.transform)
	self.transformName = parent.translate(u" Logarithm")

    def reciprocalTransform(self, evt):
	self.transform = "1 / x"
	self.transformEdit.SetValue(self.transform)
	self.transformName = parent.translate(u" Reciprocal")

    def squareTransform(self, evt):
	self.transform = "x * x"
	self.transformEdit.SetValue(self.transform)
	self.transformName = parent.translate(u" Square")

    def OnOkayButton(self, evt):
	# start transforming!
	# process: collect each selected column, then pass the contents through the self.transform function
	# then put the resulting column into a new column, and retitle it with the original variable
	# name plus the function.
	frame=  wx.GetApp().frame
	self.transform= self.transformEdit.GetValue()
	cols= range(frame.grid.NumberCols)
	emptyCols= []
	for i in cols:
	    if cols[i] not in self.colnums:
		emptyCols.append( cols[i])

	# count the number of needed columns 
	neededCols= sum( [1 for i in range(len(self.colnums)) if self.ColChoice.IsChecked(i)])
	cols2add=   len(self.colnums) + neededCols - frame.grid.NumberCols 
	if cols2add > 0:
	    # adding the needed cols
	    editorRederer= frame.floatCellAttr
	    frame.grid.AddNCells(cols2add, 0, attr= editorRederer)
	    emptyCols.extend( range(len(cols), frame.grid.NumberCols))
	    cols= frame.grid.NumberCols

	for i in range( len( self.colnums)):
	    if self.ColChoice.IsChecked( i):
		newColi= self.colnums[i]
		oldcol= frame.grid.GetCol( newColi)
		newcol= [0]*len( oldcol)
		# trying to made the evaluation by using numpy
		try:
		    arr= numpy.array(oldcol)
		    local= {'x': numpy.ravel(arr),'math': math,'scipy': scipy}
		    # posibly change by wx.GetApp().frame.scriptPanel.interp.runcode( mainscript)
		    newcol= eval( self.transform, {}, local)
		except:    
		    for j in range( len( oldcol)):
			x= oldcol[j]
			try:
			    newcol[j]= eval( self.transform)
			except: # which exception would this be?
			    newcol[j]= u''

		posNewCol= emptyCols.pop(0)
		frame.grid.PutCol( posNewCol, newcol)
		# put in a nice new heading
		oldHead= frame.grid.GetColLabelValue(self.colnums[i])
		if self.transformName == "":
		    self.transformName = ' ' + self.transform
		oldHead= oldHead + self.transformName
		frame.grid.SetColLabelValue(posNewCol, oldHead)

	self.Close(True)

    def OnCloseFrame(self, evt):
	self.Close(True)

class NumTextCtrl(wx.TextCtrl):
    '''a text ctrl that only accepts numbers'''
    def __init__( self, parent, *args, **params):
	wx.TextCtrl.__init__( self, parent, *args, **params)
	self.Bind( wx.EVT_TEXT, self._textChange)
	self.allowed = [ str( x) for x in range( 10)]
	self.allowed.extend([ wx.GetApp().DECIMAL_POINT, '-'])

    def _textChange(self, event):
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

    def _textChange( self, event):
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
	translate= wx.GetApp().translate
	bSizer8 = wx.BoxSizer( wx.VERTICAL )

	bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

	self.m_button1 = wx.Button( self, wx.ID_ANY, translate(u"All"), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
	bSizer9.Add( self.m_button1, 0, 0, 5 )

	self.m_button2 = wx.Button( self, wx.ID_ANY, translate(u"None"), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
	bSizer9.Add( self.m_button2, 0, 0, 5 )

	self.m_button3 = wx.Button( self, wx.ID_ANY, translate(u"Invert"), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
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

class SixSigma( wx.Dialog ):
    def __init__( self, parent, colNames ):
	''' colNames: a list of column Names'''
	if not isinstance(colNames, (list, tuple)):
	    return list()
	translate= wx.GetApp().translate
	wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = translate(u"Six Sigma Pack"), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

	self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

	bSizer3 = wx.BoxSizer( wx.VERTICAL )

	sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, translate(u"Select Column(s) to analyse") ), wx.VERTICAL )

	m_checkList2Choices = colNames
	self.m_checkList2 = CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,70 ), m_checkList2Choices, 0 )
	sbSizer2.Add( self.m_checkList2, 0, wx.ALL|wx.EXPAND, 5 )



	bSizer3.Add( sbSizer2, 0, wx.EXPAND, 5 )

	sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, translate(u"Limits") ), wx.VERTICAL )

	bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

	self.m_textCtrl1 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
	bSizer5.Add( self.m_textCtrl1, 0, wx.ALL, 5 )

	self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, translate(u"Upper Control Limit"), wx.DefaultPosition, wx.DefaultSize, 0 )
	self.m_staticText3.Wrap( -1 )
	bSizer5.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


	sbSizer1.Add( bSizer5, 1, wx.EXPAND, 5 )

	bSizer6 = wx.BoxSizer( wx.HORIZONTAL )

	self.m_textCtrl3 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
	bSizer6.Add( self.m_textCtrl3, 0, wx.ALL, 5 )

	self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, translate(u"Lower Control Limit"), wx.DefaultPosition, wx.DefaultSize, 0 )
	self.m_staticText4.Wrap( -1 )
	bSizer6.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


	sbSizer1.Add( bSizer6, 1, wx.EXPAND, 5 )

	bSizer7 = wx.BoxSizer( wx.HORIZONTAL )

	self.m_textCtrl4 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
	bSizer7.Add( self.m_textCtrl4, 0, wx.ALL, 5 )

	self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, translate(u"Target value"), wx.DefaultPosition, wx.DefaultSize, 0 )
	self.m_staticText5.Wrap( -1 )
	bSizer7.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


	sbSizer1.Add( bSizer7, 1, wx.EXPAND, 5 )


	bSizer3.Add( sbSizer1, 1, wx.EXPAND, 5 )

	sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )

	bSizer8 = wx.BoxSizer( wx.HORIZONTAL )

	self.m_spinCtrl1 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), wx.SP_ARROW_KEYS, 1, 10, 6 )
	bSizer8.Add( self.m_spinCtrl1, 0, wx.ALL, 5 )

	self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, translate(u"Use tolerance of  k  in  k*Sigma"), wx.DefaultPosition, wx.DefaultSize, 0 )
	self.m_staticText6.Wrap( -1 )
	bSizer8.Add( self.m_staticText6, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


	sbSizer3.Add( bSizer8, 0, wx.EXPAND, 5 )

	bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

	self.m_spinCtrl2 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), wx.SP_ARROW_KEYS, 2, 15, 2)
	bSizer9.Add( self.m_spinCtrl2, 0, wx.ALL, 5 )

	self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, translate(u"Subgroup Size"), wx.DefaultPosition, wx.DefaultSize, 0 )
	self.m_staticText7.Wrap( -1 )
	bSizer9.Add( self.m_staticText7, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


	sbSizer3.Add( bSizer9, 0, wx.EXPAND, 5 )


	bSizer3.Add( sbSizer3, 0, wx.EXPAND, 5 )

	bSizer4 = wx.BoxSizer( wx.VERTICAL )

	m_sdbSizer2 = wx.StdDialogButtonSizer()
	self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
	m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
	self.m_sdbSizer2Cancel = wx.Button( self, wx.ID_CANCEL )
	m_sdbSizer2.AddButton( self.m_sdbSizer2Cancel )
	m_sdbSizer2.Realize();

	bSizer4.Add( m_sdbSizer2, 1, wx.EXPAND, 5 )


	bSizer3.Add( bSizer4, 0, wx.ALL|wx.EXPAND, 5 )

	self.SetSizer( bSizer3 )
	self.Layout()
	bSizer3.Fit( self )

	self.Centre( wx.BOTH )
	self._BindEvents()

    def _BindEvents(self):
	self.Bind(wx.EVT_CHECKLISTBOX, self.lstboxChange)

    def lstboxChange(self, event):
	if len(self.m_checkList2.Checked) < 2:
	    self.m_spinCtrl2.Enabled= True
	else:
	    self.m_spinCtrl2.Enabled= False

    def GetValue(self):
	result= list()
	if len(self.m_checkList2.Checked) == 0:
	    result.append([])
	else:
	    result.append([self.m_checkList2.Items[pos] for pos in self.m_checkList2.Checked])
	result.append(self.m_textCtrl1.GetAsNumber())
	result.append(self.m_textCtrl3.GetAsNumber())
	result.append(self.m_textCtrl4.GetAsNumber())
	result.append(self.m_spinCtrl1.Value)
	result.append(self.m_spinCtrl2.Value)
	return result

class _MyFrame1 ( wx.Frame ):
    def __init__( self, parent ):
	wx.Frame.__init__ ( self, parent, id = wx.ID_ANY,
	                    title = wx.EmptyString, pos = wx.DefaultPosition,
	                    size = wx.Size( -1, -1 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

	self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

	bSizer10 = wx.BoxSizer( wx.VERTICAL )

	self.m_button8 = wx.Button( self, wx.ID_ANY, u"Show Dialog", wx.DefaultPosition, wx.DefaultSize, 0 )
	bSizer10.Add( self.m_button8, 0, wx.ALL, 5 )


	self.SetSizer( bSizer10 )
	self.Layout()

	self.Centre( wx.BOTH )

	# Connect Events
	self.m_button8.Bind( wx.EVT_BUTTON, self.showDialog )


    # Virtual event handlers, override them in your derived class
    def showDialog( self, event ):

	dlg = SixSigma(self,[str(i) for i in range(20)])
	if dlg.ShowModal() == wx.ID_OK:
	    print "ok"
	dlg.Destroy()


if __name__ == '__main__':
    app = wx.App()
    frame = _MyFrame1(None)
    frame.Show()
    app.MainLoop()