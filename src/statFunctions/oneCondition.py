'''One condition test'''
__name__ ='One condition test'
from statlib import stats as _stats
import numpy
# _genericFunc ist called from the __init__.py file
from statFunctions import _genericFunc
from wx import ID_OK as _OK

        
class oneConditionTest(_genericFunc):
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=     'One condition test'
        self.statName= 'oneConditionTest'
        self.minRequiredCols= 1
        
    def _dialog(self, *arg, **params):
        setting= {'Title': self.name}
        self._updateColsInfo() # update self.columnames and self.colnums
        btn1= ['StaticText',   ['Select the columns to analyse']]
        btn2= ['CheckListBox', [self.columnNames]]
        btn3= ['RadioBox',     ['Select Hypothesis',['One tailed','Two tailed'],]]
        btn4= ['StaticText',   ['User Hypothesised Mean:']]
        btn5= ['textCtrl',     []]
        structure = list()
        structure.append( [bt1,])
        structure.append( [bt2,])
        structure.append( [bt3,])
        structure.append( [bt5,])
        structure.append( [bt4,])
        return self.dialog( settings = setting, struct = structure)
    
    def _showGui_GetValues(self):
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
        
        columns=   self._convertColName2Values( self.colNameSelect )
        hypotesis= values[1]
        userMean=  values[2]
        return (columns, hypotesis, userMean)
    def _calc(self, columns, *args, **params):
        return [self.evaluate( col, *args, **params) for col in columns]
    
    def evaluate(self, *args, **params):
        # computations here
        x1 = self.DescList2.GetSelection()
        if (x1 < 0): # add top limits of grid to this
            self.Close(True)
            return
        try:
            umean = float(self.UserMean.GetValue())
        except:
            data= {'name': 'One condition Tests','size':(1,1),'nameCol':'Error',
                   'data':[('Cannot do test \n No user hypothesised mean specified',),]}
            output.addPage(data)
            self.Close(True)
            return
        realColx1 = self.colnums[x1]
        name = frame.grid.m_grid.GetColLabelValue(realColx1)
        x = frame.grid.CleanData(realColx1)
        TBase = salstat_stats.OneSampleTests(frame.grid.CleanData(realColx1), name, \
                                             frame.grid.missing)
        d=[0]
        d[0] = TBase.d1
        x2=ManyDescriptives(self, d)
        # se verifica las opciones seleccionadas
        if len(self.TestChoice.GetChecked()) == 0:
            return
        # One sample t-test
        data={'name': 'One condition Tests',
              'size':(3,3),
              'nameCol': [],
              'data': []}
        result=[]
        result.append('One sample t-test')
        if self.TestChoice.IsChecked(0):    
            TBase.OneSampleTTest(umean)
            if (TBase.prob == -1.0):
                result.append('All elements are the same, test not possible')
            else:
                if self.m_radioBtn1.GetValue():  # (self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append('t(%d) = %5.3f'%(TBase.df, TBase.t))
                result.append('p (approx) = %1.6f'%(TBase.prob))
            result.append('')
            
        result.append('One sample sign test') 
        if self.TestChoice.IsChecked(1):
            TBase.OneSampleSignTest(x, umean)
            if (TBase.prob == -1.0):
                result.append('All data are the same - no analysis is possible')
            else:
                if self.m_radioBtn1.GetValue(): #(self.hypchoice.GetSelection() == 0):
                    TBase.prob = TBase.prob / 2
                result.append('N = %5.0f'%(TBase.ntotal))
                result.append('z = %5.3f'%( TBase.z))
                result.append('p = %1.6f'%(TBase.prob))
            result.append('')

        result.append('One sample chi square') 
        if self.TestChoice.IsChecked(2):
            TBase.ChiSquareVariance(umean)
            if self.m_radioBtn1.GetValue():  #(self.hypchoice.GetSelection() == 0):
                TBase.prob = TBase.prob / 2
            if (TBase.prob == None):
                TBase.prob = 1.0
            result.append('Chi square (%d) = %5.3f'%(TBase.df, TBase.chisquare))
            result.append('p = %1.6f'%( TBase.prob))
        # se organiza los datos seleccionados
        data['data']= [[res] for res in result]
        data['size']= (len(result),1)
        output.upData(data)
    
    def showGui(self):
        values= self._showGui_GetValues()
        if values== None:
            return None
        
        result= self._calc(values[0], *values[1:])
        self._report(result)
        
    def _report(self, result):
        self.outpuGrid.addColData(self.colNameSelect, self.name)
        self.outpuGrid.addColData(result)
        self.Logg.write(self.statName+ ' successfull')
    
        
        
