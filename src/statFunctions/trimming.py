__name__= u"Trimming Fcns"
__all__=  ['threshold',]

from statlib import stats as _stats
from statFunctions import _genericFunc
from wx import Size
from wx import ID_OK as _OK
import numpy

class threshold(_genericFunc):
    ''''''
    name=      'threshold'
    statName=  'threshold'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      'threshold'
        self.statName=  'threshold'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(250,400)}
        self._updateColsInfo() # update self.columnames and self.colnums
        txt1= ['StaticText',   ['Select the column']]
        btn2= ['Choice', [self.columnNames]]
        txt2= ['StaticText',   ['thresh  min']]
        txt3= ['StaticText',   ['thresh  max']]
        txt4= ['StaticText',   ['newval']]
        btn3= ['NumTextCtrl',  []]
        btn4= ['NumTextCtrl',  []]
        btn5= ['NumTextCtrl',  []]
        structure = list()
        structure.append([txt1,])
        structure.append([btn2,])
        structure.append([btn3, txt2,])
        structure.append([btn4, txt3,])
        structure.append([btn5, txt4,])
        
        return self.dialog(settings = setting, struct = structure)
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        (self.colNameSelect, self.threshmin, self.threshmax, self.newval)= values
        
        if len( self.colNameSelect ) == 0:
            self.logPanel.write("You don't select any items")
            return
        
        if len( self.colNameSelect ) < self.minRequiredCols:
            self.logPanel.write("You have to select at least %i column(s)"%self.requiredcols)
            return
        
        if None in (self.threshmin, self.threshmax, self.newval):
            self.logPanel.write('You have to input some threshold values')
            return
        
        columns= numpy.array(self._convertColName2Values( self.colNameSelect ))
        return (columns, self.threshmin, self.threshmax, self.newval)
               
    def object(self):
        return _stats.threshold
    
    def evaluate(self, *args, **params):
        return _stats.threshold(*args, **params)
            
    def _report(self, result):
        self.outputGrid.addColData(self.colNameSelect, self.name)
        self.outputGrid.addColData(numpy.ravel(result))
        self.outputGrid.addRowData(['threshmin', self.threshmin,], currRow= 0)
        self.outputGrid.addRowData(['threshmax', self.threshmax,], currRow= 1)
        self.outputGrid.addRowData(['newval',    self.newval,],    currRow= 2)
        self.outputGrid.addRowData(['varible',   'result'],        currRow= 3)
        self.Logg.write(self.statName+ ' successfull')
        