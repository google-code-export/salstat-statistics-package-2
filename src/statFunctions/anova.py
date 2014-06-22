__name__ = u"Anova functions"
__all__=  ['oneway']

from statlib import stats as _stats
from openStats import stats2
import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size
from sei_glob import __

class oneway(_genericFunc):
    ''''''
    name=      __(u"one way anova")
    statName=  u"F_oneway"
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      __(u"one way anova")
        self.statName=  u"F_oneway"
        self.minRequiredCols= 2
        self.colNameSelect= ''
        self._scritpEquivalenString='stats.'+self.statName
        
    def _dialog(self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(250,260)}
        self._updateColsInfo() # update self.columnames and self.colnums
        bt1= ['StaticText',   [__(u'Select the columns to analyse')]]
        bt2= ['CheckListBox', [self.columnNames]]
        structure= list()
        structure.append( [bt1,])
        structure.append( [bt2,])
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
            print __(u"you don't select any items")
            return
        
        if len( self.colNameSelect ) < self.minRequiredCols:
            print __(u"you have to select at least %i columns")%self.minRequiredCols
            return
        
        columns= [self.grid.GetColNumeric( col) for col in self.colNameSelect]
        return columns
        
    def _calc(self, columns, *args, **params):
        return self.evaluate(columns, *args, **params)
        
    def object(self):
        return stats2.stats.f_oneway
    
    def evaluate(self, *args, **params):
        return stats2.stats.f_oneway(*args, **params)
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report(self, result):
        self.outputGrid.addColData( ["F","p-value"], self.name)
        self.outputGrid.addColData( result)
        self.outputGrid.addRowData( [__(u'Input data')],        currRow = 0)
        self.outputGrid.addRowData( [__(u'Selected columns'),], currRow = 1)
        self.outputGrid.addRowData( self.colNameSelect, currRow = 2)
        self.outputGrid.addRowData( [__(u'Asumptions')],        currRow = 3 )
        self.outputGrid.addRowData( [__(u'1-The samples are independent.')], currRow = 4 )
        self.outputGrid.addRowData( [__(u'2-Each sample is from a normally distributed population.')], currRow = 5)
        self.outputGrid.addRowData( [__(u''''3-The population standard deviations of the groups are all equal.
                                     This property is known as homoscedasticity.''')], currRow= 6)
        self.outputGrid.addRowData( [__(u'Results')],        currRow = 7)
        
        print self.statName + ' ' + __(u'successful')