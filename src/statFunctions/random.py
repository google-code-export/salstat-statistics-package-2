__name__ = u"Random data"
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
        cols= range(self.inputGrid.NumberCols)
        emptyCols= []
        self._updateColsInfo() # update the used columns
        for i in cols:
            if cols[i] not in self.columnNumbers:
                emptyCols.append( cols[i])
        
        # count the number of needed columns 
        neededCols= 1
        cols2add=   len(self.columnNumbers) + neededCols - self.inputGrid.NumberCols
        if cols2add > 0:
            # adding the needed cols
            editorRederer= frame.floatCellAttr
            self.inputGrid.AddNCells(cols2add, 0, attr= editorRederer)
            emptyCols.extend( range(len(cols), self.inputGrid.NumberCols))
            cols= self.inputGrid.NumberCols
            
        # choose the first empty col
        colReport= emptyCols[0]
        self.inputGrid.PutCol( colReport, result)        
        self.inputGrid.SetColLabelValue(colReport, self.statName)     
                
        #self.outputGrid.addColData( result, self.name)
        #self.outputGrid.addRowData( ['Input data'], currRow = 0)
        #self.outputGrid.addRowData( ['Len Data', self.lenData],        currRow = 1)
        #self.outputGrid.addRowData( ['Results'],    currRow = 2)
        
        self.Logg.write(self.statName+ ' successfull')
        
class randomn(random):
    ''''''
    name=      u'normal random'
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
       