__name__ = u"Generate data"
__all__=  ['random','randomn','linespace','beta',
           'chisquare','exponential', 'integerSpace']

import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size

class random(_genericFunc):
    ''''''
    name=      u'random'
    statName=  'rand'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      'random data'
        self.statName=  'rand'
        self._scritpEquivalenString='numpy.random.'+self.statName
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
        self._scritpEquivalenString='numpy.random.'+self.statName
        self.lenData= None
        
    def object(self):
        return numpy.random.randn
    
    def evaluate(self, *args, **params):
        return numpy.random.randn(*args, **params)
       
class linespace(_genericFunc):
    ''''''
    name=      u'linear space'
    statName=  'linspace'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      u'linear space'
        self.statName=  'linspace'
        self._scritpEquivalenString='numpy.random.'+self.statName
        self.lenData= None
        
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(290,240)}
        self._updateColsInfo() # update self.columnames and self.colnums
        txt1= ['StaticText',  ['Lower Limit <include>']]
        txt2= ['StaticText',  ['Upper Limit <include>']]
        txt3= ['StaticText',  ['Number of elements to generate']]
        btn1= ['IntTextCtrl', []]
        btn2= ['NumTextCtrl', []]
        structure= list()
        structure.append( [ btn2, txt1])
        structure.append( [ btn2, txt2])
        structure.append( [ btn1, txt3])
        return self.dialog( settings = setting, struct = structure)
    
    def _showGui_GetValues( self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        if None in values:
            return
        
        return values
        
    def _calc(self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object(self):
        return numpy.linspace
    
    def evaluate(self, *args, **params):
        return numpy.linspace(*args, **params)
    
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
        self.Logg.write(self.statName+ ' successfull')
        
class beta(_genericFunc):
    ''''''
    name=      u'beta space'
    statName=  'beta'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      u'beta space'
        self.statName=  'beta'
        self._scritpEquivalenString='numpy.random.'+self.statName
        self.lenData= None
        
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(290,240)}
        self._updateColsInfo() # update self.columnames and self.colnums
        txt1= ['StaticText',  ['Lower Limit <include> > 0']]
        txt2= ['StaticText',  ['Upper Limit <include> > 0']]
        txt3= ['StaticText',  ['Number of elements to generate']]
        btn1= ['IntTextCtrl', []]
        btn2= ['NumTextCtrl', []]
        structure= list()
        structure.append( [ btn2, txt1])
        structure.append( [ btn2, txt2])
        structure.append( [ btn1, txt3])
        return self.dialog( settings = setting, struct = structure)
    
    def _showGui_GetValues( self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        if None in values:
            return
        
        if any( [val < 0 for val in values]):
            return
        
        return values
        
    def _calc(self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object(self):
        return numpy.random.beta
    
    def evaluate(self, *args, **params):
        return numpy.random.beta(*args, **params)
    
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
        self.Logg.write(self.statName+ ' successfull')

class chisquare(_genericFunc):
    ''''''
    name=      u'chi square'
    statName=  'chisquare'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      u'chi square'
        self.statName=  'chisquare'
        self._scritpEquivalenString='numpy.random.'+self.statName
        self.lenData= None
        
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(290,240)}
        self._updateColsInfo() # update self.columnames and self.colnums
        txt1= ['StaticText',  ['Degrees of freedom']]
        txt3= ['StaticText',  ['Number of elements to generate']]
        btn1= ['IntTextCtrl', []]
        structure= list()
        structure.append( [ btn1, txt1])
        structure.append( [ btn1, txt3])
        return self.dialog( settings = setting, struct = structure)
    
    def _showGui_GetValues( self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        if None in values:
            return
        
        if any( [val < 0 for val in values]):
            return
        
        return values
        
    def _calc(self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object(self):
        return numpy.random.chisquare
    
    def evaluate(self, *args, **params):
        return numpy.random.chisquare(*args, **params)
    
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
        self.Logg.write(self.statName+ ' successfull')
    
class exponential(_genericFunc):
    ''''''
    name=      u'exponential space'
    statName=  'exponential'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      u'exponential space'
        self.statName=  'exponential'
        self._scritpEquivalenString='numpy.random.'+self.statName
        self.lenData= None
        
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(290,240)}
        self._updateColsInfo() # update self.columnames and self.colnums
        txt1= ['StaticText',  ['scale']]
        txt3= ['StaticText',  ['Number of elements to generate']]
        btn2= ['NumTextCtrl', []]
        btn1= ['IntTextCtrl', []]
        structure= list()
        structure.append( [ btn2, txt1])
        structure.append( [ btn1, txt3])
        return self.dialog( settings = setting, struct = structure)
    
    def _showGui_GetValues( self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        if None in values:
            return
        
        if any( [val <= 0 for val in values]):
            return
        
        return values
        
    def _calc(self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object(self):
        return numpy.random.exponential
    
    def evaluate(self, *args, **params):
        return numpy.random.exponential(*args, **params)
    
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
        self.Logg.write(self.statName+ ' successfull')

class integerSpace(_genericFunc):
    ''''''
    name=      u'integer space'
    statName=  'randint'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      u'integer space'
        self.statName=  'randint'
        self._scritpEquivalenString='numpy.random.'+self.statName
        self.lenData= None
        
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(290,240)}
        self._updateColsInfo() # update self.columnames and self.colnums
        txt1= ['StaticText',  ['Lower Limit <include>']]
        txt2= ['StaticText',  ['Upper Limit <include>']]
        txt3= ['StaticText',  ['Number of elements to generate']]
        btn1= ['IntTextCtrl', []]
        structure= list()
        structure.append( [ btn1, txt1])
        structure.append( [ btn1, txt2])
        structure.append( [ btn1, txt3])
        return self.dialog( settings = setting, struct = structure)
    
    def _showGui_GetValues( self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        if None in values:
            return
        
        return values
        
    def _calc(self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object(self):
        return numpy.random.randint
    
    def evaluate(self, *args, **params):
        return numpy.random.randint(*args, **params)
    
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
        self.Logg.write(self.statName+ ' successfull')