__name__ = u"Descriptive Statistics"
__all__=  ['AllDescriptives']

from statlib import stats as _stats
import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size

#---------------------------------------------------------------------------
# user selects which cols to analyse, and what stats to have
LISTDATA= ( (u'N',                       'N'),
            (u'Sum',                    'suma'),
            (u'Mean',                   'mean'),
            (u'missing',                'missing'),
            (u'Variance',               'variance'), # changing by the correct
            (u'Standard Deviation',     'stddev'),
            (u'Standard Error',         'stderr'),
            (u'Sum of Squares',         'sumsquares'),#  (u'Sum of Squared Devs',    'ssdevs'),
            (u'Coefficient of Variation', 'coeffvar'),
            (u'Minimum',                'minimum'),
            (u'First Quartile',         'firstquartilescore'),
            (u'Third Quartile',         'thirdquartilescore'),
            (u'Maximum',                'maximum'),
            (u'Range',                  'range'), #      (u'Number Missing',         'missing'),
            (u'Geometric Mean',         'geomean'),
            (u'Harmonic Mean',          'harmonicmean'),
            (u'Skewness',               'skewness'),
            (u'Kurtosis',               'kurtosis'),
            (u'Median',                 'median'), #     (u'Median Absolute Deviation', 'mad'),
            (u'Mode',                   'mode'),  # sampleVar is missing
            (u'Interquartile Range',    'interquartilerange',),#     (u'Number of Unique Levels', 'numberuniques')
            )

class AllDescriptives(_genericFunc):
    ''''''
    name=      u"Descriptive Statistics"
    statName=  u"allDescriptives"
    _scritpEquivalenString= ""
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=            self._( "Descriptive Statistics")
        self.statName=        u"allDescriptives"
        self.minRequiredCols= 1
        self.colNameSelect=   ''
        self.DescList= [dat[0] for dat in LISTDATA]
        self.selectedStatistics = None

    def _dialog(self, *arg, **params):
        from easyDialog.easyDialog import CheckListBox
        import wx
        self._updateColsInfo() # update self.columnames and self.colnums
        dlg= wx.Dialog( parent= self.app.frame,
                        id =    wx.ID_ANY,
                        title = self._("Descriptive Statistics"),
                        pos =   wx.DefaultPosition,
                        size =  wx.Size( 420,326 ),
                        style = wx.DEFAULT_DIALOG_STYLE )


        dlg.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        icon = self.app.icon
        dlg.SetIcon(icon)
        # ColumnList, self.colnums  = wx.GetApp().grid.GetUsedCols()

        dlg.m_mgr = wx.aui.AuiManager()
        dlg.m_mgr.SetManagedWindow( dlg )
        newDescList= [self._( DescListi) for DescListi in self.DescList]
        dlg.DescChoice = CheckListBox( dlg, wx.ID_ANY,  wx.DefaultPosition, wx.DefaultSize, newDescList, 0 )
        dlg.m_mgr.AddPane( dlg.DescChoice, wx.aui.AuiPaneInfo() .Center() .
                           Caption( wx.GetApp()._( u"Select Descriptive Statistics") ).CloseButton( False ).
                           PaneBorder( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).
                           DockFixed( False ).BottomDockable( False ).TopDockable( False ) )

        dlg.ColChoice = CheckListBox( dlg, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.columnNames, 0 )
        dlg.m_mgr.AddPane( dlg.ColChoice, wx.aui.AuiPaneInfo() .Center() .Caption( wx.GetApp()._(u"Select Column(s) to Analyse") ).
                           CloseButton( False ).PaneBorder( False ).Dock().Resizable().
                           FloatingSize( wx.Size( 161,93 ) ).DockFixed( False ).BottomDockable( False ).
                           TopDockable( False ).Row( 1 ).Layer( 0 ) )

        dlg.m_panel1 = wx.Panel( dlg, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        dlg.m_mgr.AddPane( dlg.m_panel1, wx.aui.AuiPaneInfo() .Bottom() .CaptionVisible( False ).
                           CloseButton( False ).PaneBorder( False ).Dock().Resizable().
                           FloatingSize( wx.DefaultSize ).DockFixed( False ).LeftDockable( False ).
                           RightDockable( False ).MinSize( wx.Size( -1,30 ) ) )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        okaybutton = wx.Button( dlg.m_panel1, wx.ID_OK, wx.GetApp()._(u"Ok"), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT  )
        bSizer2.Add( okaybutton, 0, wx.ALL, 5 )

        cancelbutton = wx.Button( dlg.m_panel1, wx.ID_CANCEL, wx.GetApp()._(u"Cancel"), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT  )
        bSizer2.Add( cancelbutton, 0, wx.ALL, 5 )

        dlg.m_panel1.SetSizer( bSizer2 )
        dlg.m_panel1.Layout()
        bSizer2.Fit( dlg.m_panel1 )

        dlg.m_mgr.Update()
        dlg.Centre( wx.BOTH )

        return dlg

    def _showGui_GetValues(self):
        from openStats import statistics
        dlg= self._dialog()
        numcolSelect= 0
        selectedColumns= list()
        if dlg.ShowModal() == _OK:
            # check the selected columns to analyse
            for i in range( len( self.columnNames)):
                if dlg.ColChoice.IsChecked( i):
                    numcolSelect+= 1
                    selectedColumns.append( self.columnNames[i])
            # check the selected statistical
            selectedStatistics= list()
            for i in range( len( LISTDATA)):
                if dlg.DescChoice.IsChecked( i):
                    selectedStatistics.append( LISTDATA[i][1])
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        if numcolSelect  == 0 or selectedStatistics == 0:
            self.Logg.write( self._( u"you don't select any items"))
            return

        if  numcolSelect < self.minRequiredCols:
            self.Logg.write( self._( u"you have to select at least %i columns")%self.minRequiredCols)
            return

        # self.descriptives( dlg, descs)
        self.colNameSelect= selectedColumns
        self.selectedStatistics = selectedStatistics
        return [selectedColumns, selectedStatistics] # number of selected statistics and the number of the 

    def _calc( self, columns,  statistics, *args, **params):
        return [self.evaluate( col, statistics, *args, ** params) for col in columns]

    def object( self):
        return #_stats.geometricmean

    def evaluate( self, *args, **params):
        return self.descriptives(*args, **params)

    def showGui( self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc( *values )
        self._report( result)

    def descriptives( self, column, descriptiveStatistics):
        from openStats import statistics
        realColi= column
        name=     column
        descs=   statistics( self.grid.GetCol( realColi), name)
        return [getattr( descs, itemNameSelected) for itemNameSelected in descriptiveStatistics]

    def _report(self, result):
        # add the page and the first column
        firstcol= [self._(u'Descriptives')]
        firstcol.extend( [self._(desc) for desc in self.selectedStatistics])
        self.outputGrid.addColData( firstcol, self._(u'Descriptive statistics'))

        for res, colname in zip(result, self.colNameSelect):
            newRes= [colname]
            newRes.extend(res)
            self.outputGrid.addColData( newRes)

        self.Logg.write(self.statName+ ' '+self._('successful'))