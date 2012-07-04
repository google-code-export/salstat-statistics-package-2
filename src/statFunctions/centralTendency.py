__name__ ='Central Tendency'
from statlib import stats as _stats
import numpy
# _genericFunc ist called from the __init__.py file
from statFunctions import _genericFunc
from wx import ID_OK as _OK

class geometricMean(_genericFunc):
    ''''''
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=     'geometric Mean'
        self.statName= 'geometricmean'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *arg, **params):
        setting= {'Title': self.name}
        self._updateColsInfo() # update self.columnames and self.colnums
        bt1= ['StaticText',   ['Select the columns to analyse']]
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
            self.logPanel.write("you don't select any items")
            return
        
        if len( self.colNameSelect ) < self.minRequiredCols:
            self.logPanel.write("you have to select at least %i columns"%requiredcols)
            return
        
        columns= self._convertColName2Values( self.colNameSelect )
        return columns
        
    def _calc(self, columns, *args, **params):
        return [self.evaluate( col ) for col in columns]
        
    def object(self):
        return _stats.geometricmean
    
    def evaluate(self, *args, **params):
        return _stats.geometricmean(*args, **params)
    
    def showGui(self):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(values)
        self._report(result)
        
    def _report(self, result):
        self.outpuGrid.addColData(self.colNameSelect, self.name)
        self.outpuGrid.addColData(result)
        self.Logg.write(self.statName+ ' successfull')
        
class harmonicmean(geometricMean):
    def __init__(self):
        geometricMean.__init__(self)
        self.name = 'harmonic mean'
        self.statName= 'harmonicmean'
        self.minRequiredCols= 1
    def evaluate(sef, *args, **params):
        return _stats.harmonicmean(*args, **params)
    def object(self):
        return _stats.harmonicmean
    
class mean(geometricMean):
    def __init__(self):
        geometricMean.__init__(self)
        self.name = 'mean'
        self.statName= 'mean'
        self.minRequiredCols= 1
    def evaluate(sef, *args, **params):
        return _stats.mean(*args, **params)
    def object(self):
        return _stats.mean
    
class median(geometricMean):
    def __init__(self):
        geometricMean.__init__(self)
        self.name = 'median'
        self.statName= 'median'
        self.minRequiredCols= 1
    def evaluate(sef, *args, **params):
        return _stats.median(*args, **params)
    def object(self):
        return _stats.median
    
class medianscore(geometricMean):
    def __init__(self):
        geometricMean.__init__(self)
        self.name = 'medianscore'
        self.statName= 'medianscore'
        self.minRequiredCols= 1
    def evaluate(sef, *args, **params):
        return _stats.medianscore(*args, **params)
    def object(self):
        return _stats.medianscore

class mode(geometricMean):
    def __init__(self):
        geometricMean.__init__(self)
        self.name = 'mode'
        self.statName= 'mode'
        self.minRequiredCols= 1
    def evaluate(sef, *args, **params):
        return _stats.mode(*args, **params)
    def _report(self, result):
        res1= ['var Name']
        res1.extend(self.colNameSelect)
        self.outpuGrid.addColData(res1, self.name)
        res2= ['value']
        res2.extend([res[1][0] for res in result])
        self.outpuGrid.addColData(res2)
        res3= ['frecuency']
        res3.extend([res[0][0] for res in result])
        self.outpuGrid.addColData(res3)
        self.Logg.write(self.statName+ ' successfull')