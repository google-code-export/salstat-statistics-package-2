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
        self._scritpEquivalenString='stats.'+self.statName
        self.txt1= _(u"X Column to analyse")
        self.txt2= _(u"Y Column to analyse")
        self.nameResults= [_(u"Pearson's r"), _(u" two-tailed p-value")]
        self.minRequiredCols= 2
        self.colNameSelect= ''
        
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(280,250)}
        self._updateColsInfo() # update self.columnames and self.colnums
        
        txt1=  ['StaticText',   [_(u'Select the columns to analyse')]]
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
            self.logPanel.write(_(u"You haven't selected any items!"))
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
        self.outputGrid.addRowData( [_(u'Input Data')],  currRow= 0)
        self.outputGrid.addRowData( [_(u'x column='),   self.xcolNameSelect, 'y column=', self.ycolNameSelect ], currRow= 1)
        self.outputGrid.addRowData( [_(u'Output Data')], currRow= 2)
                
        self.Logg.write( self.statName+ ' '+_(u'successful'))
        
class spearmanr(pearsonr):
    name=      'spearmanr'
    statName=  'spearmanr'
    def __init__(self):
        pearsonr.__init__(self)
        self.name=      'spearmanr'
        self.statName=  'spearmanr'
        self._scritpEquivalenString='stats.'+self.statName
        self.nameResults= [_(u"Spearman's r"), _(u"two-tailed p-value")]
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
        self._scritpEquivalenString='stats.'+self.statName
        self.nameResults= [_(u"Point-biserial r"), _(u"two-tailed p-value")]
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
        self._scritpEquivalenString='stats.'+self.statName
        self.nameResults= [_(u"Kendall's tau"), _(u" two-tailed p-value")]
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
        self._scritpEquivalenString='stats.'+self.statName
        self.nameResults= [_(u"slope"),
                           _(u"intercept"),
                           _(u"r"),
                           _(u"two-tailed prob"),
                           _(u"stderr-of-the-estimate"),
                           _(u"n")]
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
        self._scritpEquivalenString='stats.'+self.statName
        self.nameResults= [_(u'covariance')]
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
        self._scritpEquivalenString='stats.'+self.statName
        self.nameResults= ['']
        self.minRequiredCols= 2
        self.colNameSelect= ''
    def object( self):
        return _stats.paired
    
    def evaluate( self, *args, **params):
        return _stats.paired(*args, **params)
