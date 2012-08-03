__name__ ='Histogram plot'
__all__=  ['histogram'] #'cumulativeFrecuency','relativefrequency'

from statlib import stats as _stats
import numpy
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size, GetApp
from statFunctions.frequency import histogram as _histogram
from statFunctions.frequency import cumfreq, relfreq
import os

class histogram( _genericFunc):
    '''this function is used to plot a histogram
    chart of the selected column'''   
    name=     'Histogram'
    statName=  'histogram'
    def __init__(self):
        _genericFunc.__init__(self)
        self.name=     'Histogram'
        self.statName= 'histogram'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *args, **params):
        '''this function is used to plot a histogram chart of the selected column'''
        self.Logg.write('Histogram Chart')
        setting= {'Title': self.name,
                  '_size': Size(220,300)}
        self._updateColsInfo()
        if len(self.columnNames) == 0:
            self.Logg.write('You need some data to draw a graph!')
            return
        
        self.colours= ['random', 'blue', 'black',
                  'red', 'green', 'lightgreen', 'darkblue',
                  'yellow', 'hsv', 'white']
        # getting all the available figures
        path=  os.path.join( GetApp().installDir, 'nicePlot','images','histplot')
        self.figTypes= [fil[:-4] for fil in os.listdir(path) if fil.endswith('.png')]
        txt1= ['StaticText', ['Histogram type']]
        txt2= ['StaticText', ['Color']]
        txt3= ['StaticText', ['Select data to plot']]
        txt4= ['StaticText', ['number of bins']]
        btn1= ['Choice',     [self.figTypes]]
        btn2= ['Choice',     [self.colours]]
        btn3= ['Choice',     [self.columnNames]]
        btn4= ['SpinCtrl',   [2,80,3]]
        structure= list()
        structure.append([txt3])
        structure.append([btn3])
        structure.append([btn4, txt4])
        structure.append([btn1, txt1])
        structure.append([btn2, txt2])
        setting= {'Title':'Histogram chart of selected columns'}
        return self.dialog(settings= setting, struct= structure)
    
    def _calc(self, columns, *args, **params):
        return [self.evaluate(col, *args, **params) for col in columns]
        
    def object(self):
        return self
    
    def evaluate(self, *args, **params):
        # extracting data from the result
        colData= args[0]
        numBins= args[1]
        # evaluating the histogram function to obtain the data to plot
        return _histogram().evaluate(colData, numBins)  
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        res= self._calc(*values)
        self._report(res)
        
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg.ShowModal() != _OK:
            dlg.Destroy()
            return
        
        values=   dlg.GetValue()
        
        self.colNameSelect= values[0]
        numBins=           values[1]
        self.histType=     values[2]
        self.colour=       values[3]

        if self.histType == None:
            self.histType= self.figTypes[0]

        if self.colour == None:
            self.colour=  self.colours[0]
            
        if isinstance( self.colNameSelect, (str, unicode)):
            self.colNameSelect= [self.colNameSelect]

        if len( self.colNameSelect) == 0:
            self.SetStatusText( 'You need to select some data to draw a graph!')
            return
        
        # it only retrieves the numerical values
        columns= [self.inputGrid.GetColNumeric( col) 
                   for col in self.colNameSelect] 
        
        return (columns, numBins)
                
    def _report(self, result):
        plots = list()
        for res, varName in zip( result, self.colNameSelect):
            ydata= res[0]
            incr=  res[2]/2.0
            xdata= [x + incr for x in range( 1, len( res[0])+1)]
            plt= self.plot(parent=    None,
                      typePlot= 'plotNiceHistogram',
                      data2plot= (xdata,
                                  ydata,
                                  None, # legend
                                  self.colour,
                                  self.histType,),
                      xlabel=  'variable',
                      ylabel=  'value',
                      title=   'Histogram Chart of ' + varName)
            plots.append(plt)
            
        for plt in plots:
            plt.Show()
        self.Logg.write( self.name + ' successful')
        
class cumulativeFrecuency( cumfreq):
    name=     'Cumulative Frecuency'
    statName= 'cumulativeFrecuency'
    def __init__(self):
        cumfreq.__init__(self)
        self.name=     'Cumulative Frecuency'
        self.statName= 'cumulativeFrecuency'
    
#    def _report(self, result):
#        self.outputGrid.addColData(self.colNameSelect, self.name)
#        self.outputGrid.addColData(result)
#        
#        # inserting information about the input data
#        self.outputGrid.addRowData( ['Input Data'] , currRow= 0)
#        self.outputGrid.addRowData( [self.nameStaticText+'=',  self._percent], currRow= 1)
#        self.outputGrid.addRowData( ['Output Data'] , currRow= 2)
#        
#        self.Loggg.write( self.name + ' successful')
        
class relativefrequency( relfreq):
    name=     'Realtive Frecuency'
    statName= 'relativeFrecuency'
    def __init__(self):
        relfreq.__init__(self)
        self.name=     'Relative Frecuency'
        self.statName= 'relativeFrecuency'
    
#    def _report(self, result):
#        self.outputGrid.addColData(self.colNameSelect, self.name)
#        self.outputGrid.addColData(result)
#        
#        # inserting information about the input data
#        self.outputGrid.addRowData( ['Input Data'] , currRow= 0)
#        self.outputGrid.addRowData( [self.nameStaticText+'=',  self._percent], currRow= 1)
#        self.outputGrid.addRowData( ['Output Data'] , currRow= 2)
#        
#        self.Loggg.write( self.name + ' successful')
