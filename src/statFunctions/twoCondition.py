#---------------------------------------------------------------------------
#dialog for 2 sample tests
class TwoConditionTestFrame(wx.Dialog):
    def __init__(self, parent, id, ColumnList):
        wx.Dialog.__init__(self, parent, id, "Two Condition Tests", \
                           size=(500,400+wind))
        icon = images.getIconIcon()
        self.SetIcon(icon)

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        ColumnList, self.colnums = frame.grid.GetUsedCols()

        colsselected =  frame.grid.GetColsUsedList()

        self.DescChoice = DescChoiceBox( self, wx.ID_ANY )
        self.m_mgr.AddPane( self.DescChoice, wx.aui.AuiPaneInfo() .Center() .
                            Caption( u"Select Descriptive Statistics" ).CloseButton( False ).
                            PaneBorder( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).BottomDockable( False ).TopDockable( False ).
                            Row(0).Layer(0) )

        # list of tests in alphabetical order
        Tests = ['chi square','F test','Kolmogorov-Smirnov', \
                 'Linear Regression', 'Mann-Whitney U', \
                 'Paired Sign', 't-test paired','t-test unpaired', \
                 'Wald-Wolfowitz Runs', 'Wilcoxon Rank Sums', \
                 'Wilcoxon Signed Ranks'] # nb, paired permutation test missing
        m_checkList6Choices = Tests
        self.paratests = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkList6Choices, 0 )
        self.m_mgr.AddPane( self.paratests , wx.aui.AuiPaneInfo() .Center() .
                            Caption( u"Select Test(s) to Perform:" ).CloseButton( False ).
                            PaneBorder( False ).Dock().Resizable().FloatingSize( wx.Size( 161,93 ) ).
                            DockFixed( False ).BottomDockable( False ).TopDockable( False ).
                            Row( 1 ).Layer( 0 ) )

        self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel2, wx.aui.AuiPaneInfo() .Left() .CaptionVisible( False ).
                            CloseButton( False ).PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ).Row( 1 ).
                            CentrePane() )

        bSizer21 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText1 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Select Columns", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        bSizer21.Add( self.m_staticText1, 0, wx.LEFT, 5 )

        m_choice1Choices = ColumnList
        self.ColBox1 = wx.Choice( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice1Choices, 0 )
        bSizer21.Add( self.ColBox1, 0, wx.ALL|wx.EXPAND, 5 )

        m_choice2Choices = ColumnList
        self.ColBox2 = wx.Choice( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice2Choices, 0 )
        bSizer21.Add( self.ColBox2, 0, wx.ALL|wx.EXPAND, 5 )

        x1 = 0
        x2 = 1
        self.ColBox1.SetSelection(x1)
        self.ColBox2.SetSelection(x2)
        realColx1 = x1
        realColx2 = x2
        x1len = len(frame.grid.CleanData(realColx1))
        x2len = len(frame.grid.CleanData(realColx2))
        if (x1len != x2len):
            self.equallists = False
        else:
            self.equallists = True

        sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel2, wx.ID_ANY, u"Seleccione Hypotesis" ), wx.HORIZONTAL )

        self.m_radioBtn1 = wx.RadioButton( self.m_panel2, wx.ID_ANY, u"One Tailed", wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer2.Add( self.m_radioBtn1, 0, wx.ALL, 5 )

        self.m_radioBtn2 = wx.RadioButton( self.m_panel2, wx.ID_ANY, u"Two Tailed", wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer2.Add( self.m_radioBtn2, 0, wx.ALL, 5 )
        self.m_radioBtn1.SetValue(True)

        bSizer21.Add( sbSizer2, 1, wx.EXPAND, 5 )

        sbSizer4 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel2, wx.ID_ANY, u"User hypotesis test" ), wx.VERTICAL )

        self.UserMean = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer4.Add( self.UserMean, 0, wx.EXPAND, 5 )


        bSizer21.Add( sbSizer4, 1, wx.EXPAND, 5 )


        self.m_panel2.SetSizer( bSizer21 )
        self.m_panel2.Layout()
        bSizer21.Fit( self.m_panel2 )
        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_mgr.AddPane( self.m_panel1, wx.aui.AuiPaneInfo() .Bottom() .CaptionVisible( False ).
                            CloseButton( False ).PaneBorder( False ).Dock().Resizable().
                            FloatingSize( wx.DefaultSize ).DockFixed( False ).LeftDockable( False ).
                            RightDockable( False ).MinSize( wx.Size( -1,30 ) ) )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.okaybutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.okaybutton, 0, wx.ALL, 5 )
        self.okaybutton.Enable(False)

        cancelbutton  = wx.Button( self.m_panel1, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( cancelbutton , 0, wx.ALL, 5 )

        self.allbutton = wx.Button( self.m_panel1, wx.ID_ANY, u"Select All", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.allbutton, 0, wx.ALL, 5 )

        self.nonebutton= wx.Button( self.m_panel1, wx.ID_ANY, u"Select None", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.nonebutton, 0, wx.ALL, 5 )


        self.m_panel1.SetSizer( bSizer2 )
        self.m_panel1.Layout()
        bSizer2.Fit( self.m_panel1 )

        self.m_mgr.Update()
        self.Centre( wx.BOTH )

        # using self.equallists, if True, enable all items in the checklist \
        # box, otherwise set the within subs and correlations to be
        # disabled as they cannot be used with unequal list lengths!
        # Also disble the f-test unless something is entered into the
        # user hyp variance box
        self.Bind(wx.EVT_BUTTON, self.OnOkayButton, id = self.okaybutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCloseTwoCond, id = cancelbutton .GetId())
        self.Bind(wx.EVT_BUTTON, self.DescChoice.SelectAllDescriptives, id = self.allbutton.GetId())
        self.Bind(wx.EVT_BUTTON, self.DescChoice.SelectNoDescriptives, id = self.nonebutton.GetId())
        self.UserMean.Bind( wx.EVT_TEXT, self.usermeanControl )
        self.Bind(wx.EVT_CHOICE, self.ChangeCol1, id = self.ColBox1.GetId())
        self.Bind(wx.EVT_CHOICE, self.ChangeCol1, id = self.ColBox2.GetId())

    def usermeanControl( self, event ):
        allowValues= [u'0',u'1',u'2',u'3',u'4',u'5',u'6',u'7',u'8',u'9',u'.']
        resultado = [val for val in self.UserMean.GetValue() if val in allowValues]
        newres = u""
        for val in resultado:
            newres+= val
        if self.UserMean.GetValue() != newres:
            self.UserMean.SetValue(newres)
        if len(newres) > 0 :
            # se habilita el control ok para calcular
            self.okaybutton.Enable(True)
        else:
            self.okaybutton.Enable(False)
        event.Skip()

    def ChangeCol1(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        colx1 = self.ColBox1.GetSelection()
        colx2 = self.ColBox2.GetSelection()
        realColx1 = self.colnums[colx1]
        realColx2 = self.colnums[colx2]
        x1 = len(frame.grid.CleanData(realColx1))
        x2 = len(frame.grid.CleanData(realColx2))
        if (x1 != x2):
            # disable some tests in the listbox
            self.paratests.Check(0,False)
        else:
            pass
            # enable all tests in the listbox

    def ChangeCol2(self, event):
        # check that len of 2 cols is equal, if not disable choices of test
        colx1 = self.ColBox1.GetSelection()
        colx2 = self.ColBox2.GetSelection()
        realColx1 = self.colnums[colx1]
        realColx2 = self.colnums[colx2]
        x1 = len(frame.grid.CleanData(realColx1))
        x2 = len(frame.grid.CleanData(realColx2))
        if (x1 != x2):
            pass
        else:
            pass

    def OnOkayButton(self, event):
        x1 = self.ColBox1.GetSelection()
        y1 = self.ColBox2.GetSelection()
        realColx1 = self.colnums[x1]
        realColy1 = self.colnums[y1]
        name1 = frame.grid.m_grid.GetColLabelValue(realColx1)
        name2 = frame.grid.m_grid.GetColLabelValue(realColy1)
        if (x1 < 0) or (y1 < 0):
            self.Close(True)
            return
        x = frame.grid.CleanData(realColx1)
        xmiss = frame.grid.missing
        y = frame.grid.CleanData(realColy1)
        ymiss = frame.grid.missing
        TBase = salstat_stats.TwoSampleTests(x, y, name1, name2,xmiss,ymiss)
        d = [0,0]
        d[0] = TBase.d1
        d[1] = TBase.d2
        x2 = ManyDescriptives(self, d)
        # chi square test
        data={'name': 'Two condition Tests',
              'size':(3,1),
              'data': []}
        result = []
        # data['nameCol'].append('One sample t-test')
        result.append('Chi square')
        if self.paratests.IsChecked(0):
            TBase.ChiSquare(x, y)
            if (TBase.prob == -1.0):
                result.append('Cannot do chi square - unequal data sizes')
                result.append('')
            else:
                if TBase.prob == None:
                    result.append("can't be computed")
                else:
                    result.append('chi (%d) = %5.3f'%(TBase.df, TBase.chisq,))
                    result.append('p = %1.6f'%(TBase.prob,))
                result.append('')

        # F-test for variance ratio's
        result.append('F test for variance ratio (independent samples)')
        if self.paratests.IsChecked(1):
            try:
                umean = float(self.UserMean.GetValue())
            except:
                result.append('Cannot do test - no user hypothesised mean specified')
            else:
                TBase.FTest(umean)
                if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append('f(%d, %d) = %5.3f'%( TBase.df1, TBase.df2, TBase.f))
                result.append('p = %1.6f'%( TBase.prob))
                result.append('')
        
        result.append('Kolmogorov-Smirnov test (unpaired)')
        if self.paratests.IsChecked(2):
            TBase.KolmogorovSmirnov()
            if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            result.append('D = %5.3f'%(TBase.d))
            result.append('p = %1.6f'%(TBase.prob))

        result.append('Linear Regression')
        if self.paratests.IsChecked(3):
            TBase.LinearRegression(x,y)
            #s, i, r, prob, st = salstat_stats.LinearRegression(x, y)
            if (TBase.prob == -1.0):
                result.append('Cannot do linear regression - unequal data sizes')
            else:
                if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append('Slope = %5.3f, Intercept = %5.3f,\
                                    r = %5.3f, Estimated Standard Error = \
                                    %5.3f' %(TBase.slope, TBase.intercept, \
                                             TBase.r, TBase.sterrest))
                result.append('<br>t (%d) = %5.3f, p = %1.6f' \
                                        %(TBase.df, TBase.t, TBase.prob ))
                result.append('')
                
        result.append('Mann-Whitney U test (unpaired samples)')
        if self.paratests.IsChecked(4):
            TBase.MannWhitneyU(x, y)
            if (TBase.prob == -1.0):
                result.append('Cannot do Mann-Whitney U test - all numbers are identical')
            else:
                if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append('z = %5.3f, small U = %5.3f, \
                                    big U = %5.3f, p = %1.6f'%(TBase.z, \
                                          TBase.smallu, TBase.bigu, TBase.prob))
                result.append('')

        # Paired permutation test
        """if self.paratests.IsChecked(5):
            output.htmlpage.Addhtml('<P><B>Paired Permutation test</B></P>')
            TBase.PairedPermutation(x, y)
            if (TBase.prob == -1.0):
                output.htmlpage.Addhtml('<BR>Cannot do test - not paired \
                                    samples')
            else:
                if (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                output.htmlpage.Addhtml('<BR>Utail = %5.0f, nperm = %5.3f, \
                        crit = %5.3f, p = %1.6f'%(TBase.utail, TBase.nperm, \
                        TBase.crit, TBase.prob))"""

        result.append('2 sample sign test')
        if self.paratests.IsChecked(5):
            TBase.TwoSampleSignTest(x, y)
            if (TBase.prob == -1.0):
                result.append('Cannot do test - not paired \
                                    samples')
            else:
                if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append('N = %5.0f, z = %5.3f, p = %1.6f'\
                              %(TBase.ntotal, TBase.z, TBase.prob))
                result.append('')

        result.append('t-test paired')
        if self.paratests.IsChecked(6):    
            TBase.TTestPaired(x, y)
            if (TBase.prob == -1.0):
                result.append('Cannot do paired t test - \
                                    unequal data sizes')
            else:
                if self.m_radioBtn1.GetValue():#self.hypchoice.GetSelection() == 0:
                    TBase.prob = TBase.prob / 2
                result.append('t(%d) = %5.3f, p = %1.6f'% \
                              (TBase.df, TBase.t, TBase.prob))
                result.append('')

        result.append('t-test unpaired')
        if self.paratests.IsChecked(7):
            TBase.TTestUnpaired()
            if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            result.append('t(%d) = %5.3f, p =  %1.6f'% \
                          (TBase.df, TBase.t, TBase.prob))
            result.append('')

        # Wald-Wolfowitz runs test (no yet coded)
        if self.paratests.IsChecked(8):
            pass

        result.append('Wilcoxon Rank Sums test (unpairedsamples)')
        if self.paratests.IsChecked(9):
            result.append('Rank Sums test (unpaired samples)')
            TBase.RankSums(x, y)
            if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            result.append('t = %5.3f, p = %1.6f'%(TBase.z, \
                                                  TBase.prob))
            result.append('')

        result.append('Wilcoxon t (paired samples)')# 
        if self.paratests.IsChecked(10):
            TBase.SignedRanks(x, y)
            if (TBase.prob == -1.0):
                result.append('Cannot do Wilcoxon t test - \
                                    unequal data sizes')
            else:
                if TBase.prob == None:
                    result.append("can't be computed")
                else:
                    if self.m_radioBtn1.GetValue():#(self.hypchoice.GetSelection() == 0):
                        TBase.prob = TBase.prob / 2
                    result.append('z = %5.3f, t = %5.3f, p = %1.6f'%
                                  (TBase.z, TBase.wt, TBase.prob))
                result.append('')
        data['size'] = (len(result),1)
        data['data'] = [[res] for res in result]
        output.upData(data)
        self.Close(True)

    def OnCloseTwoCond(self, event):
        self.Close(True)

