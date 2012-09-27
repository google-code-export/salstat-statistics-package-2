__name__ = u"Correlation"
__all__=  ['paired', 'pearsonr', 'covariance', 'spearmanr',
           'pointbiserialr', 'kendalltau', 'linregress',]

from statlib import stats as _stats
import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size
from slbTools import homogenize

class pearsonr( _genericFunc):
    ''''''
    name=      u'pearsonr'
    statName=  'pearsonr'
    def __init__( self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      'pearsonr'
        self.statName=  'pearsonr'
        self.txt1= self.translate(u"X Column to analyse")
        self.txt2= self.translate(u"Y Column to analyse")
        self.nameResults= [self.translate(u"Pearson's r"), self.translate(u" two-tailed p-value")]
        self.minRequiredCols= 2
        self.colNameSelect= ''
        
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(280,250)}
        self._updateColsInfo() # update self.columnames and self.colnums
        
        txt1=  ['StaticText',   [self.translate(u'Select the columns to analyse')]]
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
            self.logPanel.write(self.translate(u"You haven't selected any items!"))
            return
        
        xcolumn= self.inputGrid.GetCol( self.xcolNameSelect)
        ycolumn= self.inputGrid.GetCol( self.ycolNameSelect)
        (xcolumn, ycolumn)= homogenize(xcolumn, ycolumn)
        
        xcolumn = numpy.array(xcolumn)
        ycolumn = numpy.array(ycolumn)
        xcolumn=  numpy.ravel(xcolumn)
        ycolumn=  numpy.ravel(ycolumn)
        
        return (xcolumn, ycolumn)
        
    def _calc( self, *args, **params):
        return self.evaluate(*args, **params )
        
    def object( self):
        return _stats.pearsonr
    
    def evaluate( self, *args, **params):
        return _stats.pearsonr(*args, **params)
    
    def showGui( self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report( self, result):
        self.outputGrid.addColData( self.nameResults, self.name)
        self.outputGrid.addColData( result)
        self.outputGrid.addRowData( [self.translate(u'Input Data')],  currRow= 0)
        self.outputGrid.addRowData( [self.translate(u'x column='),   self.xcolNameSelect, 'y column=', self.ycolNameSelect ], currRow= 1)
        self.outputGrid.addRowData( [self.translate(u'Output Data')], currRow= 2)
                
        self.Logg.write( self.statName+ ' '+self.translate(u'successful'))
        
class spearmanr(pearsonr):
    name=      'spearmanr'
    statName=  'spearmanr'
    def __init__(self):
        pearsonr.__init__(self)
        self.name=      'spearmanr'
        self.statName=  'spearmanr'
        self.nameResults= [self.translate(u"Spearman's r"), self.translate(u"two-tailed p-value")]
        self.minRequiredCols= 2
        self.colNameSelect= ''
        
    def object( self):
        return _stats.spearmanr
    
    def evaluate( self, *args, **params):
        return _stats.spearmanr(*args, **params)
 
class pointbiserialr(pearsonr):
    name=      'pointbiserialr'
    statName=  'pointbiserialr'
    def __init__(self):
        pearsonr.__init__(self)
        self.name=      'pointbiserialr'
        self.statName=  'pointbiserialr'
        self.nameResults= [self.translate(u"Point-biserial r"), self.translate(u"two-tailed p-value")]
        self.minRequiredCols= 2
        self.colNameSelect= ''
        
    def object( self):
        return _stats.pointbiserialr
    
    def evaluate( self, *args, **params):
        return _stats.pointbiserialr(*args, **params)

class kendalltau(pearsonr):
    name=      'kendalltau'
    statName=  'kendalltau'
    def __init__(self):
        pearsonr.__init__(self)
        self.name=      'kendalltau'
        self.statName=  'kendalltau'
        self.nameResults= [self.translate(u"Kendall's tau"), self.translate(u" two-tailed p-value")]
        self.minRequiredCols= 2
        self.colNameSelect= ''
    def object( self):
        return _stats.kendalltau
    
    def evaluate( self, *args, **params):
        return _stats.kendalltau(*args, **params)
        
class linregress(pearsonr):
    name=      u'linregress'
    statName=  'linregress'
    def __init__(self):
        pearsonr.__init__(self)
        self.name=      'linregress'
        self.statName=  'linregress'
        self.nameResults= [self.translate(u"slope"),
                           self.translate(u"intercept"),
                           self.translate(u"r"),
                           self.translate(u"two-tailed prob"),
                           self.translate(u"stderr-of-the-estimate"),
                           self.translate(u"n")]
        self.minRequiredCols= 2
        self.colNameSelect= ''
        
    def object( self):
        return _stats.linregress
    
    def evaluate( self, *args, **params):
        return _stats.linregress(*args, **params)
    
class covariance(pearsonr):
    name=      u'covariance'
    statName=  'covariance'
    def __init__(self):
        pearsonr.__init__(self)
        self.name=      'covariance'
        self.statName=  'covariance'
        self.nameResults= [self.translate(u'covariance')]
        self.minRequiredCols= 2
        self.colNameSelect= ''
    def object( self):
        return _stats.covariance
    
    def evaluate( self, *args, **params):
        return _stats.covariance(*args, **params)

class paired(pearsonr):
    name=      u'paired'
    statName=  'paired'
    def __init__(self):
        pearsonr.__init__(self)
        self.name=      'paired'
        self.statName=  'paired'
        self.nameResults= ['']
        self.minRequiredCols= 2
        self.colNameSelect= ''
    def object( self):
        return _stats.paired
    
    def evaluate( self, *args, **params):
        return _stats.paired(*args, **params)
