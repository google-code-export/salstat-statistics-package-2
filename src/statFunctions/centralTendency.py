__name__ ='Central Tendency'
from statlib import stats
import numpy
# _genericFunc ist called from the __init__.py file
from statFunctions import _genericFunc
import wx


class geometricMean(_genericFunc):
    ''''''
    __name__= 'geometric Mean'
    __statName__ = 'geometricmean'
    colNameSelect= ''
    minRequiredCols= 1
    
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        
    def _dialog(self, *arg, **params):
        setting= {'Title': self.__name__}
        self._updateColsInfo() # update self.columnames and self.colnums
        bt1= ['StaticText',   ['Select the columns to analyse']]
        bt2= ['CheckListBox', [self.columnNames]]
        structure = list()
        structure.append([bt1,])
        structure.append([bt2,])
        return self.dialog(settings = setting, struct = structure)
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg.ShowModal() == wx.ID_OK:
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
        
    def geometricMean(self):
        return stats.geometricmean
    
    def evaluate(self, *args, **params):
        return stats.geometricmean(*args, **params)
    
    def showGui(self):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(values)
        self._report(result)
        
    def _report(self, result):
        self.outpuGrid.addColData(self.colNameSelect, self.__name__)
        self.outpuGrid.addColData(result)
        self.Logg.write(self.__statName__+ ' successfull')
        
        
    