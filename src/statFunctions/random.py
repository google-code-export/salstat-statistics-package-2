__name__ ='Random data'
__all__=  ['random','randomn']

import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size

class random(_genericFunc):
    ''''''
    name=      'random'
    statName=  'rand'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      'random data'
        self.statName=  'rand'
        self.lenData= None
        
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(270,260)}
        self._updateColsInfo() # update self.columnames and self.colnums
        bt1= ['StaticText',   ['Select the number of elements to generate']]
        bt2= ['IntTextCtrl',  []]
        structure= list()
        structure.append( [ bt1,])
        structure.append( [ bt2,])
        return self.dialog( settings = setting, struct = structure)
    
    def _showGui_GetValues( self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        if values[0] == None:
            return
        self.lenData= values[0]
        return values
        
    def _calc(self, columns, *args, **params):
        return self.evaluate(columns, *args, **params)
        
    def object(self):
        return numpy.random.rand
    
    def evaluate(self, *args, **params):
        return numpy.random.rand(*args, **params)
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report(self, result):
        self.outputGrid.addColData( result, self.name)
        self.outputGrid.addRowData( ['Input data'], currRow = 0)
        self.outputGrid.addRowData( ['Len Data', self.lenData],        currRow = 1)
        self.outputGrid.addRowData( ['Results'],    currRow = 2)
        
        self.Logg.write(self.statName+ ' successfull')
        
class randomn(random):
    ''''''
    name=      'normal random'
    statName=  'randn'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      'normal random'
        self.statName=  'randn'
        self.lenData= None
        
    def object(self):
        return numpy.random.randn
    
    def evaluate(self, *args, **params):
        return numpy.random.randn(*args, **params)
       