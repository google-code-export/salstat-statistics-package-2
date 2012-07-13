'''Some condition test'''
__name__ = 'Condition tests'
from statlib import stats as _stats
import numpy
# _genericFunc ist called from the __init__.py file
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size
from openStats import OneSampleTests
        
class oneConditionTest(_genericFunc):
    def __init__( self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=     'One condition test'
        self.statName= 'oneConditionTest'
        self.minRequiredCols= 1
        self.colNameSelect= []
        self.tests= []
        self.hypotesis= 0
        
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,
                  '_size':  Size(280,430)}
        self._updateColsInfo() # update self.columnames and self.colnums
        btn1= ['StaticText',   ['Select the columns to analyse']]
        btn2= ['CheckListBox', [self.columnNames]]
        btn3= ['StaticText',   ['Choose test(s)']]
        btn4= ['CheckListBox',  [['t-test', 'Sign Test', 'Chi square test for variance'],]]
        btn5= ['RadioBox',     ['Select hypothesis',   ['One tailed','Two tailed'],]]
        btn6= ['StaticText',   ['User hypothesised mean']]
        btn7= ['NumTextCtrl',  []]
        structure= list()
        structure.append( [btn1,])
        structure.append( [btn2,])
        structure.append( [btn3,])
        structure.append( [btn4,])
        structure.append( [btn5,])
        structure.append( [btn7, btn6])
        return self.dialog( settings = setting, struct = structure)
    
    def _showGui_GetValues( self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        self.colNameSelect= values[0]
        
        if len( self.colNameSelect ) == 0:
            self.logPanel.write("you don't select any items")
            return
        
        if len( self.colNameSelect ) < self.minRequiredCols:
            self.logPanel.write("you have to select at least %i column(s)"%self.requiredcols)
            return
        
        columns=  [numpy.ravel(self._convertColName2Values( [colName] )) for colName in self.colNameSelect]
        self.tests= values[1]
        self.hypotesis= values[2]
        userMean=  values[3]
        return (columns, self.tests, self.hypotesis, userMean)
    
    def _calc( self, columns, *args, **params):
        return self.evaluate( columns, *args, **params)
    
    def evaluate( self, *args, **params):
        # computations here
        columns=   args[0]
        tests=     args[1]
        hypotesis= args[2] #0== One Tailed, 1== two tailed
        umean=     args[3]
        if umean == None or len(columns) == 0 or len(tests) == 0:
            raise StandardError('The input parameters are incorrect')
        
        TBase= [OneSampleTests(col, tests, umean)  for col in columns]
        return TBase

    def showGui( self):
        values= self._showGui_GetValues()
        if values== None:
            return None
        
        result= self._calc( values[0], *values[1:])
        self._report( result)
        
    def _report( self, result):
        if len(result) == 0:
            return
        
        # se hace el reporte por variables
        coldescription= [u'test - variable']
        for nameTest in self.tests:
            coldescription.append( nameTest)
            if nameTest == u't-test':
                coldescription.extend( ['t', 'prob (approx)'])
                
            elif nameTest == u'Sign Test':
                coldescription.extend( ['z', 'prob'])
                
            elif nameTest == u'Chi square test for variance':
                coldescription.extend( ['df', 'chisquare', 'prob'])
                
        self.outputGrid.addColData( coldescription, self.name)
        
        for name, testResults in zip( self.colNameSelect, result):
            col2report= [name]
            for nameTest in self.tests:
                result= testResults.pop( 0)
                if nameTest == u't-test':
                    prob= result[1]
                    if prob == -1.0:
                        col2report.extend( ['All elements are the same', 'test not possible', ''])
                    else:
                        if self.hypotesis == 0:
                            prob= result[1]/2.0
                        col2report.append( '')
                        col2report.append( result[0]) 
                        col2report.append( prob)
                        
                elif nameTest == u'Sign Test':
                    prob= result[1]
                    if prob == -1.0:
                        col2report.extend([ 'All data are the same','no analysis is possible',''])
                    else:
                        if self.hypotesis == 0:
                            prob= prob/2.0
                        col2report.append( '')
                        col2report.append( result[0])
                        col2report.append( prob)
                        
                elif nameTest == u'Chi square test for variance':
                    prob= result[2]
                    if prob == None:
                        prob= 1.0
                        
                    if self.hypotesis == 0:
                        continue
                        # prob= prob / 2.0 # chisquare
                    
                    col2report.extend( ['',result[0], result[1], prob])
                    
            self.outputGrid.addColData( col2report)
    
class twoConditionTest(oneConditionTest):
    def __init__(self):
        oneConditionTest.__init__(self)
        self.name=     'Two condition test'
        self.statName= 'twoConditionTest'
        self.minRequiredCols= 2
        self.colNameSelect= []
        self.tests= []
        self.hypotesis= 0
        
    def evaluate( self, *args, **params):
        # computations here
        columns=   args[0]
        tests=     args[1]
        hypotesis= args[2] #0== One Tailed, 1== two tailed
        umean=     args[3]
        if umean == None or len(columns) == 0 or len(tests) == 0:
            raise StandardError('The input parameters are incorrect')
        
        TBase= [twoSampleTests(col, tests, umean) for col in columns]
        return TBase
    
    def _report( self, result):
        if len(result) == 0:
            return
        
        # se hace el reporte por variables
        coldescription= [u'test - variable']
        for nameTest in self.tests:
            coldescription.append( nameTest)
            if nameTest == u't-test':
                coldescription.extend( ['t', 'prob (approx)'])
                
            elif nameTest == u'Sign Test':
                coldescription.extend( ['z', 'prob'])
                
            elif nameTest == u'Chi square test for variance':
                coldescription.extend( ['df', 'chisquare', 'prob'])
                
        self.outputGrid.addColData( coldescription, self.name)
        
        for name, testResults in zip( self.colNameSelect, result):
            col2report= [name]
            for nameTest in self.tests:
                result= testResults.pop( 0)
                if nameTest == u't-test':
                    prob= result[1]
                    if prob == -1.0:
                        col2report.extend( ['All elements are the same', 'test not possible', ''])
                    else:
                        if self.hypotesis == 0:
                            prob= result[1]/2.0
                        col2report.append( '')
                        col2report.append( result[0]) 
                        col2report.append( prob)
                        
                elif nameTest == u'Sign Test':
                    prob= result[1]
                    if prob == -1.0:
                        col2report.extend([ 'All data are the same','no analysis is possible',''])
                    else:
                        if self.hypotesis == 0:
                            prob= prob/2.0
                        col2report.append( '')
                        col2report.append( result[0])
                        col2report.append( prob)
                        
                elif nameTest == u'Chi square test for variance':
                    prob= result[2]
                    if prob == None:
                        prob= 1.0
                        
                    if self.hypotesis == 0:
                        continue
                        # prob= prob / 2.0 # chisquare
                    
                    col2report.extend( ['',result[0], result[1], prob])
                    
            self.outputGrid.addColData( col2report)
            
#---------------------------------------------------------------------------
# dialog for single factor tests with 3+ conditions
class ThreeConditionTestFrame(wx.Dialog):
    def __init__(self, parent, id, ColumnList):
        wx.Dialog.__init__(self, parent, id, "Three Condition Tests", \
                           size = (500,400+wind))

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        icon = images.getIconIcon()
        self.SetIcon(icon)
        alltests = ['anova between subjects','anova within subjects',\
                    'Kruskall Wallis','Friedman test',\
                    'Cochranes Q']
        ColumnList, self.colnums = frame.grid.GetUsedCols()

        m_checkList5Choices = []
        self.DescChoice = DescChoiceBox(self, wx.ID_ANY)
        self.m_mgr.AddPane( self.DescChoice, wx.aui.AuiPaneInfo() .Center() .
                            Caption( u"Select Descriptive Statistics" ).
                            CloseButton( False ).PaneBorder( False ).Dock().
                            Resizable().FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).BottomDockable( False ).
                            TopDockable( False ).Row(0).Layer( 0 ) )

        m_checkList6Choices = alltests
        self.TestChoice = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkList6Choices, 0 )
        self.m_mgr.AddPane( self.TestChoice, wx.aui.AuiPaneInfo() .Center() .
                            Caption( u"Select the kind of Test" ).CloseButton( False ).
                            PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.Size( 161,93 ) ).DockFixed( False ).
                            BottomDockable( False ).TopDockable( False ).Row( 1 ).
                            Layer( 0 ) )

        self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SIMPLE_BORDER|wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel2, wx.aui.AuiPaneInfo() .Left() .
                            CaptionVisible( False ).CloseButton( False ).
                            PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ).
                            Row( 1 ).CentrePane() )

        bSizer21 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText1 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Select Columns to Analyse", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        bSizer21.Add( self.m_staticText1, 0, wx.LEFT, 5 )

        m_listBox1Choices = ColumnList
        self.ColChoice = wx.CheckListBox( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox1Choices, 0 )
        bSizer21.Add( self.ColChoice, 2, wx.EXPAND, 5 )
        for i in range(len(self.colnums)):
            self.ColChoice.Check(i, True)


        m_radioBox3Choices = HypList
        self.hypchoice = wx.RadioBox( self.m_panel2, wx.ID_ANY, u"Select Hypotesis", wx.DefaultPosition, wx.DefaultSize, m_radioBox3Choices, 1, wx.RA_SPECIFY_ROWS )
        self.hypchoice.SetSelection( 1 )
        bSizer21.Add( self.hypchoice, 1, wx.EXPAND, 5 )


        self.m_panel2.SetSizer( bSizer21 )
        self.m_panel2.Layout()
        bSizer21.Fit( self.m_panel2 )
        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel1, wx.aui.AuiPaneInfo() .Bottom() .CaptionVisible( False ).CloseButton( False ).PaneBorder( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).DockFixed( False ).LeftDockable( False ).RightDockable( False ).MinSize( wx.Size( -1,30 ) ) )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.okaybutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.okaybutton, 0, wx.ALL, 5 )

        self.cancelbutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.cancelbutton, 0, wx.ALL, 5 )

        self.allbutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Select All", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.allbutton, 0, wx.ALL, 5 )

        self.nonebutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Select None", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.nonebutton, 0, wx.ALL, 5 )


        self.m_panel1.SetSizer( bSizer2 )
        self.m_panel1.Layout()
        bSizer2.Fit( self.m_panel1 )

        self.m_mgr.Update()
        self.Centre( wx.BOTH )


        self.Bind(wx.EVT_BUTTON, self.OnOkayButton, id = self.okaybutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCloseThreeCond, id = self.cancelbutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.DescChoice.SelectAllDescriptives, id = self.allbutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.DescChoice.SelectNoDescriptives, id = self.nonebutton.GetId())

    def OnOkayButton(self, event):
        biglist = []
        ns = []
        sums = []
        means = []
        names = []
        miss = []
        k = 0
        for i in range(len(self.colnums)):
            if self.ColChoice.IsChecked(i):
                k = k + 1
                tmplist = frame.grid.CleanData(self.colnums[i])
                miss.append(frame.grid.missing)
                biglist.append(tmplist)
                names.append(frame.grid.m_grid.GetColLabelValue(i))
        k = len(biglist)
        d = []
        for i in range(k):
            x2=salstat_stats.FullDescriptives(biglist[i], names[i], miss[i])
            ns.append(x2.N)
            sums.append(x2.sum)
            means.append(x2.mean)
            d.append(x2)
        x2=ManyDescriptives(self, d)
        
        data={'name': 'Three + condition Tests',
              'size':(3,1),
              'data': []}
        result = []
        
        if (len(biglist) < 2):
            result.append('Not enough columns selected for \
                                    test!')
            data['size']=(1,1)
            output.upData(data)
            self.Close(True)
            return
        TBase = salstat_stats.ThreeSampleTests()
        #single factor between subjects anova
        if self.TestChoice.IsChecked(0):
            cols = []
            result.append('Single Factor anova - between \
                                    subjects')
            result.append('Warning! This test is based \
                                    on the following assumptions:')
            result.append('1) Each group has a normal \
                                    distribution of observations')
            result.append('2) The variances of each observation \
                                    are equal across groups (homogeneity of \
                                    variance)')
            result.append('3) The observations are statistically \
                                    independent')
            TBase.anovaBetween(d)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            result.append('FACTOR %5.3f  %5d  %5.3f %5.3f  %1.6f'%(TBase.SSbet,     \
                            TBase.dfbet, TBase.MSbet, TBase.F, TBase.prob))
            result.append('Error %5.3f %5d %5.3f'%(TBase.SSwit, TBase.dferr, \
                                                 TBase.MSerr))
            result.append('Total %5.3f %5d'%(TBase.SStot, TBase.dftot))
            result.append('')
            
        result.append('single factor within subjects anova')
        if self.TestChoice.IsChecked(1):
            result.append('Warning! This test is based \
                                    on the following assumptions:')
            result.append('1) Each group has a normal \
                                    distribution of observations')
            result.append('2) The variances of each observation \
                                    are equal across groups (homogeneity of \
                                    variance)')
            result.append('3) The observations are statistically \
                                    indpendent')
            result.append('4) The variances of each participant \
                                    are equal across groups (homogeneity of \
                                    covariance)')
            TBase.anovaWithin(biglist, ns, sums, means)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
                
            result.append('FACTOR %5.3f %5d %5.3f %5.3f %1.6f'%(TBase.SSbet,  \
                                TBase.dfbet, TBase.MSbet, TBase.F, TBase.prob))
            result.append('Within %5.3f %5d %5.3f '%(TBase.SSwit, TBase.dfwit,     \
                                            TBase.MSwit))
            result.append('Error %5.3f %5d %5.3f'%(TBase.SSres, TBase.dfres,   \
                                            TBase.MSres))
            result.append('Total %5.3f %5d '% (TBase.SStot, TBase.dftot))
            result.append('')

        result.append('kruskal wallis H Test')
        if self.TestChoice.IsChecked(2):
            TBase.KruskalWallisH(biglist)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            result.append('H(%d) = %5.3f, p = %1.6f'% \
                                (TBase.df, TBase.h, TBase.prob))

        result.append('Friedman Chi Square')
        if self.TestChoice.IsChecked(3):
            TBase.FriedmanChiSquare(biglist)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
                alpha = 0.10
            else:
                alpha = 0.05
            result.append('Chi(%d) = %5.3f, p = %1.6f'% \
                            (TBase.df, TBase.chisq, TBase.prob))
            # the next few lines are commented out & are experimental. They
            # help perform multiple comparisons for the Friedman test.
            #outstring = '<a href="friedman,'
            #for i in range(k):
            #    outstring = outstring+'M,'+str(TBase.sumranks[i])+','
            #outstring = outstring+'k,'+str(k)+','
            #outstring = outstring+'n,'+str(d[0].N)+','
            #outstring = outstring+'p,'+str(alpha)+'">Multiple Comparisons</a>'
            #output.htmlpage.Addhtml('<p>'+outstring+'</p>')

        result.append('Cochranes Q')
        if self.TestChoice.IsChecked(4):
            TBase.CochranesQ(biglist)
            if (self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            result.append('Q (%d) = %5.3f, p = %1.6f'% \
                                    (TBase.df, TBase.q, TBase.prob))
        data['size']= (len(result),1)
        data['data']= [[res] for res in result]
        output.upData(data)
        self.Close(True)

    def OnCloseThreeCond(self, event):
        self.Close(True)