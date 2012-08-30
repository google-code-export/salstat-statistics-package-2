__name__ = u'Bar plot'
__all__=  ['barChartAllMeans']

from statlib import stats as _stats
import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size
from statFunctions.frequency import histogram

class barChartAllMeans(histogram):
    ''''''
    name=      u'bar chart of all means'
    statName=  'barChartMeans'
    def __init__(self):
        # getting all required methods
        histogram.__init__(self)
        self.name=      u'bar chart of all means'
        self.statName=  'barChartMeans'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *arg, **params):
        setting= {'Title': self.name,
                  '_size': Size(260,250)}
        self._updateColsInfo() # update self.columnames and self.colnums
        bt1= ['StaticText',   ['Columns to Analyse',] ]
        bt2= ['Choice',       self.columnNames]
        bt3= ['SpinCtrl',     [1,1000,1]]
        bt4= ['StaticText',   ['Number of Bins',] ]
        structure = list()
        structure.append([bt2, bt1])
        structure.append([bt3, bt4])
        return self.dialog(settings = setting, struct= structure)
    
    def _report(self, result):
        pass
        # implementing the plot system
        # self.outputGrid.addColData( name)
        # self.outputGrid.addColData( map(None,res[0]))
        # self.outputGrid.addColData( res[1])
        # self.outputGrid.addColData( res[2])
        # self.outputGrid.addColData( res[3])
