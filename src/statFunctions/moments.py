__name__ = u"Moments"
__all__=  ['moment', 'variation', 
           'skew', 'skewtest',
           'kurtosis', 'kurtosistest',
           'normaltest']

from statlib import stats as _stats
import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size
from sei_glob import __

class moment(_genericFunc):
    ''''''
    name=      __(u'moment')
    statName=  'moment'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      __('moment')
        self.statName=  'moment'
        self.__scritpEquivalenString='stats.'+self.statName
        self.minRequiredCols= 1
        self.colNameSelect= ''
        self.moment= None
        
    def _dialog(self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(260,250)}
        self._updateColsInfo() # update self.columnames and self.colnums
        bt1= ['StaticText',   [__('Columns to analyse'),] ]
        bt2= ['CheckListBox', [self.columnNames]]
        bt3= ['SpinCtrl',     [1,100,1]]
        bt4= ['StaticText',   [__('moment'),] ]
        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt3, bt4])
        return self.dialog(settings = setting, struct= structure)
        
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # changing value strings to numbers
        (self.colNameSelect, self.moment) = values
        if len( self.colNameSelect ) == 0:
            print __("You haven't selected any items!")
            return
        
        if not isinstance(self.colNameSelect, (list, tuple)):
            self.colNameSelect = [self.colNameSelect]
            self.moment = [self.moment]

        columns= list()
        for selectedCol in self.colNameSelect:
            col= numpy.array( self.grid.GetColNumeric( selectedCol))
            col= numpy.ravel( col)
            columns.append( col)
        return (columns, self.moment)
    
    def _calc(self, columns, *args, **params):
        return [self.evaluate( col, *args, **params ) for col in columns]
        
    def object(self):
        return _stats.moment
    
    def evaluate(self, *args, **params):
        return _stats.moment(*args, **params)
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(values[0], values[1])
        self._report(result)
        
    def _report(self, result):
        self.outputGrid.addColData(self.colNameSelect, self.name)
        self.outputGrid.addColData(result)
        
        # inserting information about the input data
        self.outputGrid.addRowData(['Input Data'] , currRow= 0)
        self.outputGrid.addRowData([self.name+'=',  self.moment], currRow= 1)
        self.outputGrid.addRowData(['Output Data'] , currRow= 2)
        
        print self.name + ' '+_('successful')


class variation(_genericFunc):
    ''''''
    name=      __('variation')
    statName=  'variation'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      __('variation')
        self.statName=  'variation'
        self.__scritpEquivalenString='stats.'+self.statName
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(220,300)}
        self._updateColsInfo() # update self.columnames and self.colnums
        bt1= ['StaticText',   [__('Select the columns to analyse')]]
        bt2= ['CheckListBox', [self.columnNames]]
        structure = list()
        structure.append([bt1,])
        structure.append([bt2,])
        return self.dialog(settings = setting, struct = structure)
    
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
            print __("you don't select any items")
            return
        
        if len( self.colNameSelect ) < self.minRequiredCols:
            print __("you have to select at least %i column(s)")%self.requiredcols
            return
        
        columns= self._convertColName2Values( self.colNameSelect )
        return columns
        
    def _calc(self, columns, *args, **params):
        return [self.evaluate( col ) for col in columns]
        
    def object(self):
        return _stats.variation
    
    def evaluate(self, *args, **params):
        return _stats.variation(*args, **params)
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(values)
        self._report(result)
        
    def _report(self, result):
        self.outputGrid.addColData(self.colNameSelect, self.name)
        self.outputGrid.addColData(result)
        print self.statName+ ' '+_('successfull')

class skew(variation):
    ''''''
    name=      __(u'skew')
    statName=  'skew'
    def __init__(self):
        # getting all required methods
        variation.__init__(self)
        self.name=      __('skew')
        self.statName=  'skew'
        self.__scritpEquivalenString='stats.'+self.statName
        self.minRequiredCols= 1
        self.colNameSelect= ''
    
    def object(self):
        return _stats.skew
    
    def evaluate(self, *args, **params):
        return _stats.skew(*args, **params)
    
class kurtosis(variation):
    ''''''
    name=      __(u'kurtosis')
    statName=  'kurtosis'
    def __init__(self):
        # getting all required methods
        variation.__init__(self)
        self.name=      __('kurtosis')
        self.statName=  'kurtosis'
        self.__scritpEquivalenString='stats.'+self.statName
        self.minRequiredCols= 1
        self.colNameSelect= ''
    
    def object(self):
        return _stats.kurtosis
    
    def evaluate(self, *args, **params):
        return _stats.kurtosis(*args, **params)

class skewtest(variation):
    ''''''
    name=      __(u'skew test')
    statName=  'skewtest'
    def __init__(self):
        # getting all required methods
        variation.__init__(self)
        self.name=      __('skewtest')
        self.statName=  'skewtest'
        self.__scritpEquivalenString='stats.'+self.statName
        self.minRequiredCols= 1
        self.colNameSelect= ''
    
    def object(self):
        return _stats.skewtest
    
    def evaluate(self, *args, **params):
        return _stats.skewtest(*args, **params)
    
    def _report(self, result):
        self.outputGrid.addColData( self.colNameSelect, self.name)
        newResult= [list(), list()]
        for res in result:
            newResult[0].append( res[0])
            newResult[1].append( res[1])
        self.outputGrid.addColData( newResult[0]),
        self.outputGrid.addColData( newResult[1])
        self.outputGrid.addRowData( ['variable', 'z-score','2-tail z-probability'], currRow= 0)
        print  self.statName+ ' '+_('successfull')

class kurtosistest(skewtest):
    ''''''
    name=      __(u'kurtosis test')
    statName=  'kurtosistest'
    def __init__(self):
        # getting all required methods
        skewtest.__init__(self)
        self.name=      __(u'kurtosis test')
        self.statName=  'kurtosistest'
        self.__scritpEquivalenString='stats.'+self.statName
        self.minRequiredCols= 1
        self.colNameSelect= ''
    
    def object(self):
        return _stats.kurtosistest
    
    def evaluate(self, *args, **params):
        return _stats.kurtosistest(*args, **params)
    
class normaltest(kurtosistest):
    ''''''
    name=      __(u'normal test')
    statName=  'normaltest'
    def __init__(self):
        # getting all required methods
        variation.__init__(self)
        self.name=      __(u'normal test')
        self.statName=  'normaltest'
        self.__scritpEquivalenString='stats.'+self.statName
        self.minRequiredCols= 1
        self.colNameSelect= ''
    
    def object(self):
        return _stats.normaltest
    
    def evaluate(self, *args, **params):
        return _stats.normaltest(*args, **params)