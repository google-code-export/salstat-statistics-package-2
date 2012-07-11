'''One condition test'''
__name__ ='One condition test'
from statlib import stats as _stats
import numpy
# _genericFunc ist called from the __init__.py file
from statFunctions import _genericFunc
from wx import ID_OK as _OK
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
        
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name}
        self._updateColsInfo() # update self.columnames and self.colnums
        btn1= ['StaticText',   ['Select the columns to analyse']]
        btn2= ['CheckListBox', [self.columnNames]]
        btn3= ['StaticText',   ['Choose test(s)']]
        btn4= ['CheckListBox',  [['t-test', 'Sign Test', 'Chi square test for variance'],]]
        btn5= ['RadioBox',     ['Select hypothesis',   ['One tailed','Two tailed'],]]
        btn6= ['StaticText',   ['User hypothesised mean:']]
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
            self.logPanel.write("you have to select at least %i columns"%requiredcols)
            return
        
        columns=  [numpy.ravel(self._convertColName2Values( colName )) for colName in self.colNameSelect]
        self.tests= values[1]
        hypotesis= values[2]
        userMean=  values[3]
        return (columns, self.tests, hypotesis, userMean)
    
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
        
        result= self._calc(values[0], *values[1:])
        self._report(result)
        
    def _report( self, result):
        self.colNameSelect # names
        if len(result) == 0:
            return
        
        # se hace el reporte por variables
        self.outpuGrid.addColData(coldescription, self.name)
        
        d=    [0]
        d[0]= TBase.d1
        x2=   ManyDescriptives(self, d)

        # One sample t-test

        result= []
        result.append( 'One sample t-test')
        if self.TestChoice.IsChecked( 0):
            TBase.OneSampleTTest( umean)
            if (TBase.prob == -1.0):
                result.append( 'All elements are the same, test not possible')
            else:
                if self.m_radioBtn1.GetValue():  # (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append( 't(%d) = %5.3f'%(TBase.df, TBase.t))
                result.append( 'p (approx) = %1.6f'%(TBase.prob))
            result.append( '')
            
        result.append( 'One sample sign test') 
        if self.TestChoice.IsChecked( 1):
            TBase.OneSampleSignTest( x, umean)
            if (TBase.prob == -1.0):
                result.append( 'All data are the same - no analysis is possible')
            else:
                if self.m_radioBtn1.GetValue(): #(self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append( 'N = %5.0f'%(TBase.ntotal))
                result.append( 'z = %5.3f'%( TBase.z))
                result.append( 'p = %1.6f'%(TBase.prob))
            result.append( '')

        result.append( 'One sample chi square') 
        if self.TestChoice.IsChecked( 2):
            TBase.ChiSquareVariance( umean)
            if self.m_radioBtn1.GetValue():  #(self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            if (TBase.prob == None):
                TBase.prob = 1.0
            result.append( 'Chi square (%d) = %5.3f'%(TBase.df, TBase.chisquare))
            result.append( 'p = %1.6f'%( TBase.prob))
        # se organiza los datos seleccionados
        data= [[res] for res in result]
        self.outpuGrid.addColData(self.colNameSelect, self.name)
        self.outpuGrid.addColData(result)
        self.Logg.write(self.statName+ ' successfull')
        