'''
Created on 14/05/2012

@author: Sebastian Lopez Buritica
'''

from scipy import stats as stats2
from statlib import stats
import math
import numpy as np

def isnumeric(data):
    if isinstance(data, (int, float, long, np.ndarray)):
        return True
    return False

class statistics(object):
    def __init__(self, data, name= None, missing= None):
        if isnumeric(data) and not isinstance( data, (np.ndarray)):
            data= [data]
        self.data=     data
        # self.missing=  missing # deprecated
        self.Name=     name
        
        # initializing values
        listOfProperties= ['_N',          '_suma',               '_mean',               '_variance',
                           '_stderr',     '_stddev',             '_sumsquares',         '_minimum',
                           '_maximum',    '_firstquartilescore', '_thirdquartilescore', '_interquartilerange',
                           '_samplevar',  '_range',              '_geomean',            '_harmonicmean',
                           '_skewness',   '_kurtosis',           '_median',             '_isParMinorThanZero',
                           '_mode',       '_coeffvar',]
        
        for prop in listOfProperties:
            setattr(self, prop, None)
        self.missing= len(self.data)
        self.data= self._filterdata(data)
        self.missing= self.missing - len(self.data)
        self.data= self._filterNonNumerical(self.data)
        # deleting non numerical data
    def _filterNonNumerical(self,data):
        return [dat for dat in data if isnumeric(dat) ]
        
    def _filterdata(self, data):
        return [dat for dat in data if dat != None ]
        
    # optimizing speed:
    @property
    def N(self):
        if self._N == None:
            self._N = len(self.data)
        return self._N
    @property
    def suma(self):
        if self._suma == None:
            self._suma = sum(self.data)
        return self._suma
    @property
    def mean(self):
        if self._mean == None:
            self._mean= stats.mean(self.data)
        return self._mean
    @property
    def variance(self):
        if self._variance== None:
            if self.N == 1:
                self._variance = None
            else:
                self._variance= stats.var(self.data)
        return self._variance
    @property
    def stderr(self):
        if self._stderr== None:
            if self.N == 1:
                self._stderr = None
            else:
                self._stderr= stats.sterr(self.data)
        return self._stderr
    @property
    def stddev(self):
        if self._stddev== None:
            if self.N == 1:
                self._stddev = None
            else:
                self._stddev= stats.stdev(self.data)
        return self._stddev
    @property
    def sumsquares(self):
        if self._sumsquares == None:
            self._sumsquares= stats.ss(self.data)
        return self._sumsquares
    @property
    def minimum(self):
        if self._minimum == None:
            self._minimum=  min(self.data)
        return self._minimum
    @property
    def firstquartilescore(self):
        if self._firstquartilescore == None:
            self._firstquartilescore =  stats.firstquartilescore(self.data)
        return self._firstquartilescore
    @property
    def thirdquartilescore(self):
        if self._thirdquartilescore == None:
            self._thirdquartilescore =  stats.thirdquartilescore(self.data)
        return self._thirdquartilescore
    @property
    def interquartilerange(self):
        if self._interquartilerange == None:
            self._interquartilerange = self.thirdquartilescore - self.firstquartilescore
        return self._interquartilerange
    @property
    def maximum(self):
        if self._maximum == None:
            self._maximum =  max(self.data)
        return self._maximum
    @property
    def range(self):
        if self._range == None:
            self._range =  self.maximum - self.minimum
        return self._range
    @property
    def isParMinorThanZero(self):
        # to be used as a reference in the geometric mean calculations
        if self._isParMinorThanZero == None:
            if sum([ 1 for dat in self.data if dat < 0])%2 == 0:
                self._isParMinorThanZero = True
            else:
                self._isParMinorThanZero = False
        return self._isParMinorThanZero
    @property
    def geomean(self):
        if self._geomean == None:
            if self.isParMinorThanZero:
                self._geomean = stats.geometricmean(self.data)
            else:
                self._geomean = None
        return self._geomean
    @property
    def harmonicmean(self):
        if self._harmonicmean == None:
            try:
                self._harmonicmean = stats.harmonicmean(self.data)
            except ZeroDivisionError:
                self._harmonicmean = None
        return self._harmonicmean
    @property
    def skewness(self):
        if self._skewness == None:
            self._skewness = stats.skew(self.data)
        return self._skewness
    @property
    def kurtosis(self):
        if self._kurtosis== None:
            self._kurtosis =  stats.kurtosis(self.data)
        return self._kurtosis
    @property
    def median(self):
        if self._median == None:
            self._median= stats.median(self.data)
        return self._median
    @property
    def samplevar(self):
        if self._samplevar == None:
            self._samplevar = stats.samplevar(self.data)
        return self._samplevar
    @property
    def coeffvar(self):
        if self._coeffvar == None:
            if self.mean !=0 and self.stddev != None:
                self._coeffvar= self.stddev/float(self.mean)
            else:
                self._coeffvar = None
        return self._coeffvar
    @property
    def mode(self):
        if self._mode == None:
            self._mode = stats.mode(self.data)[1][0]
        return self._mode
        
def normProb( x, loc= 0, scale= 1):
    return stats2.norm(loc= loc, scale= scale).cdf(x)

def normProbInv( x, loc= 0, scale= 1):
    return stats2.norm(loc= loc, scale= scale).ppf(x)

def OneSampleTests(colData, tests, userMean):
    # detect the selected tests
    posible={'t-test':     False,
             'Sign Test':  False,
             'Chi square test for variance':False}
    
    for test in tests:
        if test in posible.keys():
            posible[test]= True
    
    # calculating descriptive statistics
    de= statistics(colData)
    result= list()
    # ttest= (t, 2 tailed prob)
    if posible['t-test']:
        ttest= stats.ttest_1samp( colData, userMean)
        result.append(ttest)
        
    def OneSampleSignTest(data1, usermean):
        """
        This method performs a single factor sign test. The data must be 
        supplied to this method along with a user hypothesised mean value.
        Usage: OneSampleSignTest(data1, usermean)
        Returns: nplus, nminus, z, prob.
        """
        nplus=0
        nminus=0
        for i in range(len(data1)):
            if (data1[i] < usermean):
                nplus+= 1
                
            if (data1[i] > usermean):
                nminus+= 1
                
        ntotal= nplus + nminus
        try:
            z= nplus- (ntotal/2)/ math.sqrt(ntotal/2)
        except ZeroDivisionError:
            z=     0
            prob= -1.0
        else:
            prob= stats.erfcc(abs(z) / 1.4142136)
        return (z, prob)
    #####
    def ChiSquareVariance(de, usermean):
        """
        This method performs a Chi Square test for the variance ratio.
        Usage: ChiSquareVariance(self, usermean)
        Returns: df, chisquare, prob
        """
        df = de.N - 1
        try:
            chisquare = (de.stderr / usermean) * df
        except ZeroDivisionError:
            chisquare = 0.0
        prob = stats.chisqprob( float(chisquare), df) 
        
        return (df, chisquare, prob)
    #####
    if posible['Sign Test']:
        oneSampleST= OneSampleSignTest( colData, userMean)
        result.append(oneSampleST)
        
    if posible['Chi square test for variance']:
        chisqtest= ChiSquareVariance( de, userMean)
        result.append(chisqtest)
    
    return result

def twoSampleTests(colData, tests, userMean):
    posible={'t-test':     False,
             'Sign Test':  False,
             'Chi square test for variance':False}
    
    for test in tests:
        if test in posible.keys():
            posible[test]= True
