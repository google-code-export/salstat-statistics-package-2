'''
Created on 14/05/2012

@author: USUARIO
'''
from statlib import stats
class statistics:
    def __init__(self, data, name, missing):
        self.missing= missing
        self.Name = name
        self.N = len(data)
        self.suma= sum(data)
        self.mean= stats.mean(data)
        self.variance = stats.var(data)
        self.stderr= stats.sterr(data)
        self.sumsquares = stats.ss(data)
        #self.short = stats.shellsort(data)
        self.minimum= min(data)
        self.maximum= max(data)
        self.range = self.maximum-self.minimum
        self.geomean= stats.geometricmean(data)
        try:
            self.harmmean = stats.harmonicmean(data)
        except ZeroDivisionError:
            self.harmmean = None
        self.skewness= stats.skew(data)
        self.kurtosis= stats.kurtosis(data)
        self.median= stats.median(data)
        self.stddev= stats.stdev(data)
        self.samplevar= stats.samplevar(data)
        self.variance= stats.var(data)
        if self.mean !=0:
            self.coeffvar= self.stddev/float(self.mean)
        else:
            self.coeffvar = None
        self.mode= stats.mode(data)[1][0]