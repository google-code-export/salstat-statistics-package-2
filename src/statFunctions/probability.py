__name__ = u"Probability calcs"
__all__=  ['chisqprob', 'erfcc', 'zprob',
           'ksprob', 'fprob', 'gammln','betacf','betai']

from statlib import stats as _stats
import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size
from statFunctions.frequency import scoreatpercentile
from statFunctions.centralTendency import geometricMean

class chisqprob(scoreatpercentile):
    ''''''
    name=      'chisqprob'
    statName=  'chisqprob'
    def __init__(self):
        # getting all required methods
        scoreatpercentile.__init__(self)
        self.name=      'chisqprob'
        self.statName=  'chisqprob'
        self.nameStaticText= 'Degrees of freedom'
        self.minRequiredCols= 1
        self.spindata= [1,100,1]
        self.colNameSelect= ''
        self._percent= None

    def _dialog(self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(280,220)}
        self._updateColsInfo() # update self.columnames and self.colnums
        bt1=  ['StaticText',   ['Select the column to analyse']]
        bt2=  ['Choice',       [self.columnNames]]
        btn3= ['SpinCtrl',     [0,100,0]]
        btn4= ['StaticText',   [self.nameStaticText] ]
        structure = list()
        structure.append([bt1,])
        structure.append([bt2,])
        structure.append([btn3, btn4 ])
        return self.dialog(settings = setting, struct = structure)
        
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        (self.colNameSelect, self._percent) = values
        if self.colNameSelect  == None:
            self.Logg.write("You haven't selected any item!")
            return

        col= numpy.array( self.inputGrid.GetColNumeric( self.colNameSelect))
        col= numpy.ravel( col)
        
        return (col, self._percent)
        
    def _calc(self, columns, *args, **params):
        return self.evaluate(columns, *args, **params)
        
    def object(self):
        return _stats.chisqprob
    
    def evaluate(self, *args, **params):
        return _stats.chisqprob(*args, **params)

class erfcc(geometricMean):
    name=      'erfcc'
    statName=  'erfcc'
    def __init__(self):
        # getting all required methods
        geometricMean.__init__(self)
        self.name=      'erfcc'
        self.statName=  'erfcc'
        self.minRequiredCols= 1
        self.colNameSelect= ''
    
    def _dialog(self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(220,300)}
        self._updateColsInfo() # update self.columnames and self.colnums
        bt1= ['StaticText',   ['Select the column to analyse']]
        bt2= ['Choice',       [self.columnNames]]
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
        
        if self.colNameSelect == None:
            self.Logg.write("you don't select any items")
            return
        
        if len( self.colNameSelect ) < self.minRequiredCols:
            self.Logg.write("you have to select at least %i column(s)"%self.requiredcols)
            return
        
        col= self.inputGrid.GetColNumeric( self.colNameSelect)
        return col
        
    def object(self):
        return _stats.erfcc
    
    def evaluate(self, *args, **params):
        return _stats.erfcc(*args, **params)
    
class zprob(erfcc):
    name=      'zprob'
    statName=  'zprob'
    def __init__(self):
        # getting all required methods
        erfcc.__init__(self)
        self.name=      'zprob'
        self.statName=  'zprob'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def object(self):
        return _stats.zprob
    
    def evaluate(self, *args, **params):
        return _stats.zprob(*args, **params)
    
class ksprob(erfcc):
    name=      'ksprob'
    statName=  'ksprob'
    def __init__(self):
        # getting all required methods
        erfcc.__init__(self)
        self.name=      'ksprob'
        self.statName=  'ksprob'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def object(self):
        return _stats.ksprob
    
    def evaluate(self, *args, **params):
        return _stats.ksprob(*args, **params)

class fprob(erfcc):
    name=      'fprob'
    statName=  'fprob'
    def __init__(self):
        # getting all required methods
        erfcc.__init__(self)
        self.name=      'fprob'
        self.statName=  'fprob'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def object(self):
        return _stats.fprob
    
    def evaluate(self, *args, **params):
        return _stats.fprob(*args, **params)
    
class gammln(erfcc):
    name=      'gammln'
    statName=  'gammln'
    def __init__(self):
        # getting all required methods
        erfcc.__init__(self)
        self.name=      'gammln'
        self.statName=  'gammln'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def object(self):
        return _stats.gammln
    
    def evaluate(self, *args, **params):
        return _stats.gammln(*args, **params)
    
class betacf(_genericFunc):
    ''''''
    name=      'betacf'
    statName=  'betacf'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      'betacf'
        self.statName=  'betacf'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(250,300)}
        self._updateColsInfo() # update self.columnames and self.colnums
        txt1= ['StaticText',  ['x']]
        txt2= ['StaticText',  ['a']]
        txt3= ['StaticText',  ['b']]
        btn1= ['NumTextCtrl', []]
        btn2= ['Choice', [self.columnNames]]
        structure = list()
        structure.append([btn1, txt2])
        structure.append([btn1, txt3])
        structure.append([btn2, txt1])
        return self.dialog(settings = setting, struct = structure)
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        (self.a, self.b, self.colNameSelect)= values
        
        if self.colNameSelect == None:
            self.Logg.write("you don't select any items")
            return
        
        if len( self.colNameSelect ) < self.minRequiredCols:
            self.Logg.write("you have to select at least %i column(s)"%self.requiredcols)
            return
        
        if self.a== None or self.b == None:
            self.Logg.write('You must input some data to the a and b variables')
            return
        
        columns= self.inputGrid.GetColNumeric( self.colNameSelect )
        return (columns, self.a, self.b)
        
    def _calc(self, columns, *args, **params):
        return [self.evaluate( col, *args, **params) for col in columns]
        
    def object(self):
        return _stats.betacf
    
    def evaluate(self, *args, **params):
        return _stats.betacf(*args, **params)
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report(self, result):
        self.outputGrid.addColData(result, self.name)
        self.outputGrid.addRowData(['Input data'],           currRow= 0)
        self.outputGrid.addRowData(['a', self.a.__str__()],  currRow= 1)
        self.outputGrid.addRowData(['b', self.b.__str__()],  currRow= 2)
        self.outputGrid.addRowData(['x', self.colNameSelect.__str__()], currRow= 3)
        self.outputGrid.addRowData(['Output data'],          currRow= 4)
        
        self.Logg.write(self.statName+ ' successfull')

class betai(betacf):
    ''''''
    name=      'betai'
    statName=  'betai'
    def __init__(self):
        # getting all required methods
        betacf.__init__(self)
        self.name=      'betai'
        self.statName=  'betai'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def object(self):
        return _stats.betai
    
    def evaluate(self, *args, **params):
        return _stats.betai(*args, **params)

