__name__ = u"Generate data"
__all__=  ['random','randomn','linespace','beta',
           'chisquare','exponential', 'integerSpace']

import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size
from easyDialog.easyDialog import Ctrl, Busy
from sei_glob import __

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
        dlg = self.dialog()
        dlg.Title = self.name
        dlg.size = Size(270,260)
        ##setting= {'Title': self.name,
        ##          '_size': Size(270,260)}

        self._updateColsInfo() # update self.columnames and self.colnums
        bt1 = Ctrl.StaticText('Select the number of elements to generate')# ['StaticText',   ['Select the number of elements to generate']]
        bt2 = Ctrl.IntTextCtrl()#'IntTextCtrl',  []]
        btn3 = Ctrl.StaticText(__('Destination variable'))
        btn4 = Ctrl.Choice(self.columnNames)
        structure = list()
        structure.append( [ bt1, bt2])
        structure.append( [ btn3, btn4])
        dlg.struct = structure
        return dlg
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
    @Busy(__('Calculating'))
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
        values, outputColumn= values[:-1], values[-1]
        result= self._calc(values[0])
        self._report(result, outputColumn)
    @Busy(__('Reporting'))
    def _report(self, result, outputColumn):
        # choose the first empty col
        self.grid.PutCol( outputColumn, result)
        ##self.grid.SetColLabelValue(outputColumn, self.statName)
        print self.statName+ ' '+_('successfull')
        
class randomn(random):
    ''''''
    name=      __(u'normal random')
    statName=  'randn'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      __('normal random')
        self.statName=  'randn'
        self._scritpEquivalenString='numpy.random.'+self.statName
        self.lenData= None
        
    def object(self):
        return numpy.random.randn
    
    def evaluate(self, *args, **params):
        return numpy.random.randn(*args, **params)
       
class linespace(_genericFunc):
    ''''''
    name=      __(u'linear space')
    statName=  __('linspace')
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      __(u'linear space')
        self.statName=  __('randint')
        self._scritpEquivalenString='numpy.random.'+self.statName
        self.lenData= None
        
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(290,240)}

        self._updateColsInfo() # update self.columnames and self.colnums
        txt1= Ctrl.StaticText(__('Lower Limit <included>'))
        txt2= Ctrl.StaticText(__('Upper Limit <included>'))
        txt3= Ctrl.StaticText(__('Number of elements to generate'))
        txt4= Ctrl.StaticText(__('Destination variable'))
        btn1= Ctrl.IntTextCtrl()
        btn2= Ctrl.NumTextCtrl()
        btn3= Ctrl.Choice(self.columnNames)
        structure= list()
        structure.append( [ btn2, txt1])
        structure.append( [ btn2, txt2])
        structure.append( [ btn1, txt3])
        structure.append( [ btn3, txt4])
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
        values, outputColumn= values[:-1], values[-1]
        result= self._calc(*values)
        self._report(result, outputColumn)
        
    def _report(self, result, outputColumn):
        colReport= outputColumn
        self.grid.PutCol( colReport, result)        
        #self.grid.SetColLabelValue(colReport, self.statName)
        print self.statName + ' successfull'
        
class beta(_genericFunc):
    ''''''
    name=      __(u'beta space')
    statName=  'beta'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      __(u'beta space')
        self.statName=  'beta'
        self._scritpEquivalenString='numpy.random.'+self.statName
        self.lenData= None
        
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(290,240)}
        self._updateColsInfo() # update self.columnames and self.colnums
        txt1 = Ctrl.StaticText( __('Lower Limit <include> > 0'))
        txt2 = Ctrl.StaticText( __('Upper Limit <include> > 0'))
        txt3 = Ctrl.StaticText( __('Number of elements to generate'))
        txt4 = Ctrl.StaticText( __("Destination variable "))
        btn1 = Ctrl.IntTextCtrl()
        btn2 = Ctrl.NumTextCtrl()
        btn3 = Ctrl.Choice( self.columnNames)
        structure= list()
        structure.append( [ btn2, txt1])
        structure.append( [ btn2, txt2])
        structure.append( [ btn1, txt3])
        structure.append( [ btn3, txt4])
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
        values, outputColumn= values[:-1], values[-1]
        if any( [val < 0 for val in values]):
            return
        
        return values, outputColumn
        
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
        values, outputColumn= values[:-1], values[-1]
        result= self._calc(*values[0])
        self._report(result, outputColumn)
        
    def _report(self, result, outputColumn):
        self.grid.PutCol( outputColumn, result)
        print self.statName+ ' '+ __('successfull')

class chisquare(_genericFunc):
    ''''''
    name=      __(u'chi square')
    statName=  'chisquare'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      __(u'chi square')
        self.statName=  'chisquare'
        self._scritpEquivalenString='numpy.random.'+self.statName
        self.lenData= None
        
    def _dialog( self, *arg, **params):
        dlg = self.dialog()
        dlg.title = self.name
        dlg.size = Size(290,240)
        self._updateColsInfo() # update self.columnNames and self.colnums
        txt1 = Ctrl.StaticText( __('Degrees of freedom'))
        txt3 = Ctrl.StaticText( __('Number of elements to generate'))
        txt4 = Ctrl.StaticText(__('Destination variable'))
        btn1 = Ctrl.IntTextCtrl()
        btn2 = Ctrl.Choice(self.columnNames)
        structure = list()
        structure.append( [btn1, txt1])
        structure.append( [btn1, txt3])
        structure.append( [btn2, txt4])
        dlg.struct= structure
        return dlg
    
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

        values,outputColumn= values[:-1], values[-1]
        if any( [val < 0 for val in values]):
            return
        
        return values, outputColumn
        
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
        values,outputColumn= values[:-1], values[-1]
        values= values[0]
        result= self._calc(*values)
        self._report(result, outputColumn)
        
    def _report(self, result, outputColumn):
        self.grid.PutCol( outputColumn, result)
        print self.statName+ ' ' +_('successfull')
    
class exponential(_genericFunc):
    ''''''
    name=      __(u'exponential space')
    statName=  'exponential'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=     __(u'exponential space')
        self.statName=  'exponential'
        self._scritpEquivalenString='numpy.random.'+self.statName
        self.lenData= None
        
    def _dialog( self, *arg, **params):
        dlg= self.dialog()
        dlg.Title= self.name
        dlg.size= Size(290,240)
        self._updateColsInfo() # update self.columnames and self.colnums
        txt1= Ctrl.StaticText( __('scale'))
        txt3= Ctrl.StaticText( __('Number of elements to generate'))
        txt4= Ctrl.StaticText( __('Destination variable'))
        btn2= Ctrl.NumTextCtrl()
        btn1= Ctrl.IntTextCtrl()
        btn3= Ctrl.Choice( self.columnNames)
        structure= list()
        structure.append( [ btn2, txt1])
        structure.append( [ btn1, txt3])
        structure.append( [ btn3, txt4])
        dlg.struct= structure
        return dlg
    
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
        values, outputColumn= values[:-1], values[-1]
        if any( [val <= 0 for val in values]):
            return
        
        return values, outputColumn

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
        values, outputColumn= values[:-1], values[-1]
        values= values[0]
        result= self._calc(*values)
        self._report(result, outputColumn)

    def _report(self, result, outputColumn):
        self.grid.PutCol( outputColumn, result)
        print self.statName + ' ' + __('successfull')

class integerSpace(_genericFunc):
    ''''''
    name=      __(u'integer space')
    statName=  'randint'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      __(u'integer space')
        self.statName=  'randint'
        self._scritpEquivalenString='numpy.random.'+self.statName
        self.lenData= None
        
    def _dialog( self, *arg, **params):
        dlg= self.dialog()
        dlg.Title= self.name
        dlg.size= Size(290,240)
        self._updateColsInfo() # update self.columnames and self.colnums
        txt1= Ctrl.StaticText( __('Lower Limit <include>'))
        txt2= Ctrl.StaticText( __('Upper Limit <include>'))
        txt3= Ctrl.StaticText( __('Number of elements to generate'))
        txt4= Ctrl.StaticText( __('Destination variable'))
        btn1= Ctrl.IntTextCtrl()
        btn2= Ctrl.Choice( self.columnNames)
        structure= list()
        structure.append( [ btn1, txt1])
        structure.append( [ btn1, txt2])
        structure.append( [ btn1, txt3])
        structure.append( [ btn2, txt4])
        dlg.struct= structure
        return dlg
    
    def _showGui_GetValues( self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        values, outputColumn= values[:-1], values[-1]
        if None in values:
            return
        return values,outputColumn
        
    def _calc(self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object(self):
        return numpy.random.randint
    
    def evaluate(self, *args, **params):
        return numpy.random.randint(*args, **params)
    
    def showGui(self, *args, **params):
        values = self._showGui_GetValues()
        if values == None:
            return None
        values, outputColumn = values[:-1], values[-1]
        values= values[0]
        result= self._calc(*values)
        self._report(result, outputColumn)
        
    def _report(self, result, outputColumn):
        self.grid.PutCol( outputColumn, result)
        print self.statName + ' ' + __('successfull')