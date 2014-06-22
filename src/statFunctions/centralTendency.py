__name__ = u"Central Tendency"
__all__=  ['geometricMean', 'harmonicmean', 'mean',
           'median', 'medianscore', 'mode']

from statlib import stats as _stats
import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size
from sei_glob import __

class geometricMean(_genericFunc):
    ''''''
    name=      __(u"geometric Mean")
    statName=  u"geometricmean"
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      __('geometric Mean')
        self.statName=  'geometricmean'
        self._scritpEquivalenString='stats.'+self.statName
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(220,300)}
        self._updateColsInfo() # update self.columnames and self.colnums
        bt1= ['StaticText',   [__(u'Select the columns to analyse')]]
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
            print __(u"you don't select any items")
            return
        
        if len( self.colNameSelect ) < self.minRequiredCols:
            print __(u"you have to select at least %i columns")%self.minRequiredCols
            return
        
        columns= self._convertColName2Values( self.colNameSelect )
        return columns
        
    def _calc(self, columns, *args, **params):
        return [self.evaluate( col ) for col in columns]
        
    def object(self):
        return _stats.geometricmean
    
    def evaluate(self, *args, **params):
        return _stats.geometricmean(*args, **params)
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(values)
        self._report(result)
        
    def _report(self, result):
        self.outputGrid.addColData(self.colNameSelect, self.name)
        self.outputGrid.addColData(result)
        print self.statName+ ' '+ __('successful')
        
class harmonicmean(geometricMean):
    name=      __(u"harmonic mean")
    statName=  'harmonicmean'
    
    def __init__(self):
        geometricMean.__init__(self)
        self.minRequiredCols= 1
        self.name=      __('harmonic mean')
        self.statName=  'harmonicmean'
        self._scritpEquivalenString='stats.'+self.statName
        
    def evaluate(self, *args, **params):
        return _stats.harmonicmean(*args, **params)
    
    def object(self):
        return _stats.harmonicmean
    
class mean(geometricMean):
    name= u"mean"
    statName= 'mean'
    
    def __init__(self):
        geometricMean.__init__(self)
        self.minRequiredCols= 1
        self.name= 'mean'
        self.statName= 'mean'
        self._scritpEquivalenString='stats.'+self.statName
    def evaluate(self, *args, **params):
        return _stats.mean(*args, **params)
    
    def object(self):
        return _stats.mean
    
class median(geometricMean):
    name=  __(u"median")
    statName= 'median'
    def __init__(self):
        geometricMean.__init__(self)
        self.minRequiredCols= 1
        self.name=  'median'
        self.statName= 'median'
        self._scritpEquivalenString='stats.'+self.statName
        
    def evaluate(self, *args, **params):
        return _stats.median(*args, **params)
    
    def object(self):
        return _stats.median
    
class medianscore(geometricMean):
    name=   __(u"medianscore")
    statName=  'medianscore'
    def __init__(self):
        geometricMean.__init__(self)
        self.minRequiredCols= 1
        self.name=   __('medianscore')
        self.statName=  'medianscore'
        self._scritpEquivalenString='stats.'+self.statName
    def evaluate(self, *args, **params):
        return _stats.medianscore(*args, **params)
    
    def object(self):
        return _stats.medianscore

class mode(geometricMean):
    name= u"mode"
    statName= 'mode'
    def __init__(self):
        geometricMean.__init__(self)
        self.minRequiredCols= 1
        self.name= 'mode'
        self.statName= 'mode'
        self._scritpEquivalenString='stats.'+self.statName
    def _calc(self, columns, *args, **params):
        return [self.evaluate( map(None, col) ) for col in columns]
          
    def evaluate(self, *args, **params):
        return _stats.mode(*args, **params)
    
    def _report(self, result):
        res1= [__(u'variable name')]
        res1.extend(self.colNameSelect)
        self.outputGrid.addColData(res1, self.name)
        res2= [__(u'value')]
        res2.extend([numpy.ravel(res[1]) for res in result])
        self.outputGrid.addColData(res2)
        res3= [__(u'frecuency')]
        res3.extend([numpy.ravel(res[0])[0] for res in result])
        self.outputGrid.addColData(res3)
        print self.statName + ' ' + __('successfull')