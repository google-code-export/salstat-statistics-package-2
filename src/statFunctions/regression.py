__name__ = u"Regression"
__all__=  ["ols", "wls", "gls"]# "glsar"

from statlib import stats as _stats
import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size
from slbTools import homogenize
import scikits.statsmodels.api as _sm
import sys
from sei_glob import __

class ols( _genericFunc):
    ''''''
    name=      __(u'Ordinary least squares (OLS)')
    statName=  'OLS'
    def __init__( self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      __(u'Ordinary least squares (OLS)')
        self.statName=  'OLS'
        self.txt1= __(u"Response/dependent variable")
        self.txt2= __(u"Exogenous data")
        #self.nameResults= [__(u"Pearson's r"), __(u" two-tailed p-value")]
        self.minRequiredCols= 2
        self.colNameSelect= ''
        self._scritpEquivalenString='sm.'+self.statName
        
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,}
        self._updateColsInfo() # update self.columnames and self.colnums
        
        txt1=  ['StaticText',   [__(u'Select the columns to analyse')]]
        btn1=  ['Choice',       [self.columnNames]]
        txt2=  ['StaticText',   [self.txt1] ]
        txt3=  ['StaticText',   [self.txt2] ]

        structure = list()
        structure.append([txt1])
        structure.append([btn1, txt2])
        structure.append([btn1, txt3])
        return self.dialog(settings = setting, struct= structure)
        
    def _showGui_GetValues( self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        (self.xcolNameSelect, self.ycolNameSelect)= values
        
        if self.xcolNameSelect == None or self.ycolNameSelect == None:
            print __(u"You haven't selected any items!")
            return
        
        xcolumn= self.grid.GetCol( self.xcolNameSelect)
        ycolumn= self.grid.GetCol( self.ycolNameSelect)
        (xcolumn, ycolumn)= homogenize(xcolumn, ycolumn)
        
        xcolumn = numpy.array(xcolumn)
        ycolumn = numpy.array(ycolumn)
        xcolumn=  numpy.ravel(xcolumn)
        ycolumn=  numpy.ravel(ycolumn)
        
        return (xcolumn, ycolumn)
        
    def _calc( self, *args, **params):
        return self.evaluate(*args, **params )
        
    def object( self):
        return _sm.OLS
    
    def evaluate( self, *args, **params):
        #x= _sm.add_constant(args[0])
        #y= _sm.add_constant(args[1])
        return _sm.OLS(*args, **params).fit()
    
    def showGui( self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report( self, result):
        if 0:
            self.outputGrid.addColData( self.nameResults, self.name)
            self.outputGrid.addColData( result)
            self.outputGrid.addRowData( [__(u'Input Data')],  currRow= 0)
            self.outputGrid.addRowData( [__(u'x column='),   self.xcolNameSelect, 'y column=', self.ycolNameSelect ], currRow= 1)
            self.outputGrid.addRowData( [__(u'Output Data')], currRow= 2)
        print result.summary().__str__().decode( sys.getfilesystemencoding())
        print self.statName+ ' '+__(u'successful')
        
class gls(ols):
    name=      __(u'Generalized least squares (GLS)')
    statName=  u'GLS'
    def __init__(self):
        ols.__init__(self)
        self.name=      __(u'Generalized least squares (GLS)')
        self.statName=  u'GLS'
        self.txt1=      __(u"Response/independent variable")
        self.txt2=      __(u"Regressors/dependent variables")
        self.txt3=      __(u"Sigma")
        self._scritpEquivalenString= "sm."+ self.statName
        self.minRequiredCols= 3
        self.colNameSelect= ''
    
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,}
        self._updateColsInfo() # update self.columnames and self.colnums
        
        txt1=  ['StaticText',   [__(u'Select the columns to analyse')]]
        btn1=  ['Choice',       [self.columnNames]]
        txt2=  ['StaticText',   [self.txt1] ]
        txt3=  ['StaticText',   [self.txt2] ]
        checkBox= ['CheckBox',  ('Calculate Sigma Value',)]
        checkList= ('CheckListBox', [self.columnNames])
        txt4=  ['StaticText',   [self.txt3] ]

        structure = list()
        structure.append([txt1])
        structure.append([btn1, txt2])
        structure.append([checkList, txt3])
        structure.append([checkBox, btn1, txt4])
        return self.dialog(settings = setting, struct= structure)
    
    def _showGui_GetValues( self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        (self.response, self.regresors, calculateSigma, self.sigma)= values
        
        if self.response == None or len(self.regresors) == 0:
            print __(u"You haven't selected any items!")
            return
        
        response= self.grid.GetCol( self.response)
        regresors= list()
        for reg in self.regresors:
            regresors.append( self.grid.GetCol( reg))
        
        if not calculateSigma:
            sigma=     self.grid.GetCol( self.sigma)
            results=   homogenize(response, sigma, *regresors)
            response=  results.pop(0)
            sigma =    results.pop(0)
            regresors= results[:]
        else:
            results=   homogenize(response, *regresors)
            response=  results.pop(0)
            regresors= results[:]
        
        response= numpy.array(response)
        response= numpy.ravel(response)
        
        regresors = numpy.array( regresors).transpose()
        
        if calculateSigma:
            ols_resid = _sm.OLS( response, regresors).fit().resid
            res_fit =   _sm.OLS( ols_resid[1:], ols_resid[:-1]).fit()
            rho =       res_fit.params
            from scipy.linalg import toeplitz
            order =     toeplitz( numpy.arange( response.size))
            sigma =     rho**order
            
        
        return (response,regresors, sigma)
    
    def object( self):
        return _sm.GLS
    
    def evaluate( self, *args, **params):
        return _sm.GLS(*args, **params).fit()

class wls(ols):
    name=      __('Weighted least squares (WLS)')
    statName=  'WLS'
    def __init__(self):
        ols.__init__(self)
        self.name=      __('Weighted least squares (WLS)')
        self.statName=  'WLS'
        #self.nameResults= [__(u"Point-biserial r"), __(u"two-tailed p-value")]
        self.txt1= __(u"Response variable")
        self.txt2= __(u"Exogenous data")
        self.txt3= __(u"Weights")
        self._scritpEquivalenString= 'sm.'+ self.statName
        self.minRequiredCols= 3
        self.colNameSelect= ''
    
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,}
        self._updateColsInfo() # update self.columnames and self.colnums
        
        txt1=  ['StaticText',   [__(u'Select the columns to analyse')]]
        btn1=  ['Choice',       [self.columnNames]]
        txt2=  ['StaticText',   [self.txt1] ]
        txt3=  ['StaticText',   [self.txt2] ]
        checkBox= ['CheckBox',  ('Consider weights\nequals to one',)]
        txt4=  ['StaticText',   [self.txt3] ]

        structure = list()
        structure.append([txt1])
        structure.append([btn1, txt2])
        structure.append([btn1, txt3])
        structure.append([checkBox, btn1, txt4])
        return self.dialog(settings = setting, struct= structure)
    
    def _showGui_GetValues( self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        (self.xcolNameSelect, self.ycolNameSelect, wIsOnes, self.weights)= values
        
        if self.xcolNameSelect == None or self.ycolNameSelect == None:
            print __(u"You haven't selected any items!")
            return
        
        xcolumn= self.grid.GetCol( self.xcolNameSelect)
        ycolumn= self.grid.GetCol( self.ycolNameSelect)
        if wIsOnes:
            weights= numpy.ones( (len(xcolumn), 1) )
        else:
            weights= self.grid.GetCol( self.weights)
        
        (xcolumn, ycolumn, weights)= homogenize(xcolumn, ycolumn, weights)
        
        xcolumn = numpy.array(xcolumn)
        ycolumn = numpy.array(ycolumn)
        weights = numpy.array(weights)
        xcolumn=  numpy.ravel(xcolumn)
        ycolumn=  numpy.ravel(ycolumn)
        weights = numpy.ravel(weights)
        
        return (xcolumn, ycolumn, weights)
    
    def object( self):
        return _sm.WLS
    
    def evaluate( self, *args, **params):
        return _sm.WLS(*args, **params).fit()


##---------------------
### not implemented yet
class glsar(ols):
    name=      __('Feasible generalized least squares')
    statName=  'glsar'
    def __init__(self):
        ols.__init__(self)
        self.name=      ('Feasible generalized least squares')
        self.statName=  'glsar'
        self._scritpEquivalenString= 'sm.'+ self.statName
        self.nameResults= [__(u"Kendall's tau"), __(u" two-tailed p-value")]
        self.minRequiredCols= 2
        self.colNameSelect= ''
        
    def object( self):
        return _stats.kendalltau
    
    def evaluate( self, *args, **params):
        return _stats.kendalltau(*args, **params)        
##---------------------