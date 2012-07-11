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