__name__ = u"Inferential stats"
__all__=  ['ttest_1samp', 'ttest_ind','ttest_rel',
           'chisquare', 'ks_2samp', 'mannwhitneyu',
           'ranksums', 'wilcoxont','kruskalwallish',
           'friedmanchisquare']

from statlib import stats as _stats
import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size
from statFunctions.correlation import pearsonr
from statFunctions.centralTendency import geometricMean

class ttest_1samp(_genericFunc):
    ''''''
    name=      u't-test one sample'
    statName=  'ttest_1samp'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=      't-test one sample'
        self.statName=  'ttest_1samp'
        self._scritpEquivalenString='stats.'+self.statName
        self.minRequiredCols= 1
        self.colNameSelect= ''

    def _dialog(self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(250,250)}
        self._updateColsInfo() # update self.columnames and self.colnums
        bt1=  ['StaticText',   ['Select the columns to analyse']]
        bt2=  ['CheckListBox', [self.columnNames]]
        bt3= ['NumTextCtrl',  []]
        txt2= ['StaticText',    ['popmean']]
        structure = list()
        structure.append([bt1,])
        structure.append([bt2,])
        structure.append([bt3, txt2])

        return self.dialog(settings = setting, struct = structure)

    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        (self.colNameSelect, self.popmean)= values

        if len( self.colNameSelect ) == 0:
            self.logPanel.write("you don't select any items")
            return

        if len( self.colNameSelect ) < self.minRequiredCols:
            self.logPanel.write("you have to select at least %i column(s)"%self.requiredcols)
            return

        if self.popmean == None:
            self.logPanel.write("You must input some value into the popmean field")
            return

        columns= [ self.inputGrid.GetCol(col) for col in  self.colNameSelect]
        return (columns, self.popmean)

    def _calc(self, columns, *args, **params):
        return [self.evaluate( col, *args, **params ) for col in columns]

    def object(self):
        return _stats.ttest_1samp

    def evaluate(self, *args, **params):
        return _stats.ttest_1samp(*args, **params)

    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)

    def _report(self, result):
        for varSelected, res in zip(self.colNameSelect, result):
            #self.outputGrid.addColData( res)
            self.outputGrid.addRowData( ['Input Data'],     self.statName)
            self.outputGrid.addRowData( ['selected Col=',   varSelected],   currRow= 1)
            self.outputGrid.addRowData( ['popmean=',        self.popmean],  currRow= 2)
            self.outputGrid.addRowData( ['t',               res[0]])
            self.outputGrid.addRowData( ['two tailed prob', res[1]])
            ##self.outputGrid.addRowData( ['Output',        res],           currRow= 3)

class ttest_ind(pearsonr):
    ''''''
    name=      u't-test independent'
    statName=  'ttest_ind'
    def __init__(self):
        # getting all required methods
        pearsonr.__init__(self)
        self.name=      u't-test independent'
        self.statName=  'ttest_ind'
        self._scritpEquivalenString='stats.'+self.statName
        self.txt1= "X Column to analyse"
        self.txt2= "Y Column to analyse"
        self.nameResults= ['t', 'two tailed prob']
        self.minRequiredCols= 2
        self.colNameSelect= ''

    def object( self):
        return _stats.ttest_ind

    def evaluate( self, *args, **params):
        return _stats.ttest_ind(*args, **params)

class ttest_rel(pearsonr):
    ''''''
    name=      u't-test related'
    statName=  'ttest_rel'
    def __init__(self):
        # getting all required methods
        pearsonr.__init__(self)
        self.name=      u't-test related'
        self.statName=  'ttest_rel'
        self._scritpEquivalenString='stats.'+self.statName
        self.txt1= "X Column to analyse"
        self.txt2= "Y Column to analyse"
        self.nameResults= ['t', 'two tailed prob']
        self.minRequiredCols= 2
        self.colNameSelect= ''

    def object( self):
        return _stats.ttest_rel

    def evaluate( self, *args, **params):
        return _stats.ttest_rel(*args, **params)

class chisquare(pearsonr):
    ''''''
    name=      u'chi-square test'
    statName=  'chisquare'
    def __init__(self):
        # getting all required methods
        pearsonr.__init__(self)
        self.name=      u'chi-square test'
        self.statName=  'chisquare'
        self._scritpEquivalenString='stats.'+self.statName
        self.txt1= "X Column to analyse"
        self.txt2= "Y Column to analyse"
        self.nameResults= ['chisq', 'chisqprob(chisq, k-1)']
        self.minRequiredCols= 2
        self.colNameSelect= ''

    def object( self):
        return _stats.chisquare

    def evaluate( self, *args, **params):
        return _stats.chisquare(*args, **params)

class ks_2samp(pearsonr):
    ''''''
    name=      u'Kolmogorov-Smirnof two samples'
    statName=  'ks_2samp'
    def __init__(self):
        # getting all required methods
        pearsonr.__init__(self)
        self.name=      u'Kolmogorov-Smirnof two samples'
        self.statName=  'ks_2samp'
        self._scritpEquivalenString='stats.'+self.statName
        self.txt1= "X Column to analyse"
        self.txt2= "Y Column to analyse"
        self.nameResults= ['KS D-value', 'associated p-value']
        self.minRequiredCols= 2
        self.colNameSelect= ''

    def object( self):
        return _stats.ks_2samp

    def evaluate( self, *args, **params):
        return _stats.ks_2samp(*args, **params)

class mannwhitneyu(pearsonr):
    ''''''
    name=      u'Mann-Whitney U statistic'
    statName=  'mannwhitneyu'
    def __init__(self):
        # getting all required methods
        pearsonr.__init__(self)
        self.name=      u'Mann-Whitney U statistic'
        self.statName=  'mannwhitneyu'
        self._scritpEquivalenString='stats.'+self.statName
        self.txt1= "X Column to analyse"
        self.txt2= "Y Column to analyse"
        self.nameResults= ['u-statistic', 'one-tailed p-value']
        self.minRequiredCols= 2
        self.colNameSelect= ''

    def object( self):
        return _stats.mannwhitneyu

    def evaluate( self, *args, **params):
        return _stats.mannwhitneyu(*args, **params)

class ranksums(pearsonr):
    ''''''
    name=      u'rank sums statistic'
    statName=  'ranksums'
    def __init__(self):
        # getting all required methods
        pearsonr.__init__(self)
        self.name=      u'rank sums statistic'
        self.statName=  'ranksums'
        self._scritpEquivalenString='stats.'+self.statName
        self.txt1= "X Column to analyse"
        self.txt2= "Y Column to analyse"
        self.nameResults= ['z-statistic', 'two-tailed p-value']
        self.minRequiredCols= 2
        self.colNameSelect= ''

    def object( self):
        return _stats.ranksums

    def evaluate( self, *args, **params):
        return _stats.ranksums(*args, **params)

class wilcoxont(pearsonr):
    ''''''
    name=      u'Wilcoxon T-test related samples'
    statName=  'wilcoxont'
    def __init__(self):
        # getting all required methods
        pearsonr.__init__(self)
        self.name=      u'Wilcoxon T-test related samples'
        self.statName=  'wilcoxont'
        self._scritpEquivalenString='stats.'+self.statName
        self.txt1= "X Column to analyse"
        self.txt2= "Y Column to analyse"
        self.nameResults= ['t-statistic', 'two-tail probability estimate']
        self.minRequiredCols= 2
        self.colNameSelect= ''

    def object( self):
        return _stats.wilcoxont

    def evaluate( self, *args, **params):
        return _stats.wilcoxont(*args, **params)

class kruskalwallish(geometricMean):
    ''''''
    name=      u"Kruskal-Wallis H-test"
    statName=  'kruskalwallish'
    def __init__(self):
        # getting all required methods
        geometricMean.__init__(self)
        self.name=      u"Kruskal-Wallis H-test"
        self.statName=  'kruskalwallish'
        self._scritpEquivalenString='stats.'+self.statName
        self.minRequiredCols= 3
        self.colNameSelect= ''
        self.nameResults= ['H-statistic (corrected for ties)',
                                     'associated p-value']

    def _calc(self, columns, *args, **params):
        return self.evaluate(*columns)

    def object(self):
        return _stats.kruskalwallish

    def evaluate(self, *args, **params):
        return _stats.kruskalwallish(*args, **params)

    def _report(self, result):
        self.outputGrid.addColData(self.nameResults, self.name)
        self.outputGrid.addColData(result)

        self.outputGrid.addRowData(['selected columns',], currRow= 0)
        self.outputGrid.addRowData(self.colNameSelect,    currRow= 1)
        self.outputGrid.addRowData(['results'],           currRow= 2)


        self.Logg.write(self.statName+ ' successfull')

class friedmanchisquare(kruskalwallish):
    ''''''
    name=      u'Friedman Chi-Square test'
    statName=  'friedmanchisquare'
    def __init__(self):
        # getting all required methods
        kruskalwallish.__init__(self)
        self.name=      u'Friedman Chi-Square test'
        self.statName=  'friedmanchisquare'
        self._scritpEquivalenString='stats.'+self.statName
        self.minRequiredCols= 3
        self.colNameSelect= ''
        self.nameResults= ['chi-square statistic', 'associated p-value']

    def object(self):
        return _stats.friedmanchisquare

    def evaluate(self, *args, **params):
        return _stats.friedmanchisquare(*args, **params)

