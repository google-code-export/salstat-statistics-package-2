__name__ = u"variability"
__all__=  ['samplevar', 'samplestdev','signaltonoise',
           'var', 'stdev', 'sterr', 'sem', 'zs', 'z' ]

from statlib import stats as _stats
from statFunctions import _genericFunc
from statFunctions.centralTendency import geometricMean
from statFunctions.frequency import scoreatpercentile
from wx import Size
from wx import ID_OK as _OK

class samplevar(geometricMean):
    ''''''
    name=      'samplevar'
    statName=  'samplevar'
    def __init__(self):
        # getting all required methods
        geometricMean.__init__(self)
        self.name=      'samplevar'
        self.statName=  'samplevar'
        self.minRequiredCols= 1
        self.colNameSelect= ''
            
    def object(self):
        return _stats.samplevar
    
    def evaluate(self, *args, **params):
        return _stats.samplevar(*args, **params)

class samplestdev(geometricMean):
    ''''''
    name=      'samplestdev'
    statName=  'samplestdev'
    def __init__(self):
        # getting all required methods
        geometricMean.__init__(self)
        self.name=      'samplestdev'
        self.statName=  'samplestdev'
        self.minRequiredCols= 1
        self.colNameSelect= ''
            
    def object(self):
        return _stats.samplestdev
    
    def evaluate(self, *args, **params):
        return _stats.samplestdev(*args, **params)

class var(geometricMean):
    ''''''
    name=      'var'
    statName=  'var'
    def __init__(self):
        # getting all required methods
        geometricMean.__init__(self)
        self.name=      'var'
        self.statName=  'var'
        self.minRequiredCols= 1
        self.colNameSelect= ''
            
    def object(self):
        return _stats.var
    
    def evaluate(self, *args, **params):
        return _stats.var(*args, **params)

class stdev(geometricMean):
    ''''''
    name=      'stdev'
    statName=  'stdev'
    def __init__(self):
        # getting all required methods
        geometricMean.__init__(self)
        self.name=      'stdev'
        self.statName=  'stdev'
        self.minRequiredCols= 1
        self.colNameSelect= ''
            
    def object(self):
        return _stats.stdev
    
    def evaluate(self, *args, **params):
        return _stats.stdev(*args, **params)

class sterr(geometricMean):
    ''''''
    name=      'sterr'
    statName=  'sterr'
    def __init__(self):
        # getting all required methods
        geometricMean.__init__(self)
        self.name=      'sterr'
        self.statName=  'sterr'
        self.minRequiredCols= 1
        self.colNameSelect= ''
            
    def object(self):
        return _stats.sterr
    
    def evaluate(self, *args, **params):
        return _stats.sterr(*args, **params)

class sem(geometricMean):
    ''''''
    name=      'sem'
    statName=  'sem'
    def __init__(self):
        # getting all required methods
        geometricMean.__init__(self)
        self.name=      'sem'
        self.statName=  'sem'
        self.minRequiredCols= 1
        self.colNameSelect= ''
            
    def object(self):
        return _stats.sem
    
    def evaluate(self, *args, **params):
        return _stats.sem(*args, **params)

class zs(geometricMean):
    ''''''
    name=      'zs'
    statName=  'zs'
    def __init__(self):
        # getting all required methods
        geometricMean.__init__(self)
        self.name=      'zs'
        self.statName=  'zs'
        self.minRequiredCols= 1
        self.colNameSelect= ''
            
    def object(self):
        return _stats.zs
    
    def evaluate(self, *args, **params):
        return _stats.zs(*args, **params)

class signaltonoise(geometricMean):
    name=      'signal to noise (mean/stdev)'
    statName=  'signaltonoise'
    def __init__(self):
        # getting all required methods
        geometricMean.__init__(self)
        self.name=      'signal to noise (mean/stdev)'
        self.statName=  'signaltonoise'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        self.percent=   None  # self.percent == self.histbins
        
    def object(self):
        return _stats.signaltonoise
    
    def evaluate(self, *args, **params):
        return _stats.signaltonoise(*args, **params)
    
    def _report(self, result):
        result= [res[0] for res in result]
        self.outputGrid.addColData(self.colNameSelect, self.name)
        self.outputGrid.addColData(result)
        self.Logg.write(self.statName+ ' successfull')

class z(scoreatpercentile):
    name=      'z'
    statName=  'z'
    def __init__(self):
        # getting all required methods
        scoreatpercentile.__init__(self)
        self.name=      'z'
        self.statName=  'z'
        self.nameStaticText= 'score'
        self.spindata= [1, 100, 1]
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def object(self):
        return _stats.z
    
    def evaluate(self, *args, **params):
        return _stats.z(*args, **params)
            