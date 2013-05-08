__name__ = u'Histogram plot'
__all__=  ['histogram', 'niceHistogram',
           'cumulativeFrecuency',] #,'relativefrequency'

from plotFunctions import _neededLibraries, pltobj
from wx import ID_OK as _OK
import wx
from openStats import statistics

from statFunctions import _genericFunc
from wx import Size, GetApp
from statFunctions.frequency import histogram as _histogram
from statFunctions.frequency import cumfreq, relfreq
import os
from numpy import array, ravel
import matplotlib.mlab as mlab
from nicePlot.graficaRibon import plothist 
from imagenes import imageEmbed
imag= imageEmbed()

class histogram( _neededLibraries):
    name=      u"Histogram"
    plotName=  u"Histogram"
    image =    imag.histogram
    def __init__( self):
        _neededLibraries.__init__(self)
        self.name=      u'Histogram'
        self.plotName=  u'Histogram'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *arg, **params):
        '''this function is used to plot a histogram chart of the selected column'''
        self.log.write(self.translate(u'Histogram Chart'))
        self._updateColsInfo()
        if len(self.columnNames) == 0:
            self.log.write(self.translate(u'You need some data to draw a graph!'))
            return
        
        self.colours= ['blue', 'black',
                  'red', 'green', 'lightgreen', 'darkblue',
                  'yellow', 'hsv', 'white']
        txt2= ['StaticText',   [self.translate(u'Colour')]]
        txt3= ['StaticText',   [self.translate(u'Select data to plot')]]
        txt4= ['StaticText',   [self.translate(u'number of bins')]]
        btn2= ['Choice',       [self.colours]]
        btn3= ['Choice',       [self.columnNames]] # trying to prevent out of memory error
        btn4= ['SpinCtrl',     [2,500,5]]
        btn5= ['ToggleButton', [self.translate(u'Show best Normal Curve')]]
        structure= list()
        structure.append([txt3])
        structure.append([btn3])
        structure.append([txt4])
        structure.append([btn4])
        structure.append([btn5])
        structure.append([btn2, txt2])
        setting= {'Title': self.translate(self.name),
                  '_size': Size(200,300)}
        
        return self.dialog(settings= setting, struct= structure)
    
    def _calc(self, columns, *args, **params):
        return [self.evaluate(col, *args, **params) for col in columns]
        
    def object(self):
        return self
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg == None:
            return
        
        if dlg.ShowModal() != _OK:
            dlg.Destroy()
            return
        
        values=   dlg.GetValue()
        
        self.colNameSelect= values[0]
        numBins=            values[1]
        showNormCurv=       values[2]
        self.colour=        values[3]

        if self.colour == None:
            self.colour=  self.colours[0]
            
        if self.colNameSelect == None:
            self.Logg.write(self.translate(u"you have to select at least %i columns")%self.minRequiredCols)
            return
        
        if isinstance( self.colNameSelect, (str, unicode)):
            self.colNameSelect= [self.colNameSelect]

        if len( self.colNameSelect) < self.minRequiredCols:
            self.SetStatusText( self.translate(u'You have to select at least %i columns to draw a graph!')%self.minRequiredCols)
            return
        
        # it only retrieves the numerical values
        columns= [self.grid.GetColNumeric( col) 
                   for col in self.colNameSelect][0]
        return (columns, numBins, showNormCurv, self.colour)
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        # extracting data from the result
        ydat=         args[0]
        nbins=        args[1]
        showNormCurv= args[2]
        color=        args[3]
        # evaluating the histogram function to obtain the data to plot
        data= _histogram().evaluate( array( ydat), nbins)
        
        plt= pltobj( None, xlabel= 'variable', ylabel= self.translate(u'value'), title= self.translate(u'Histogram Chart of ') + self.colNameSelect[0] )
        plt.gca().hold( True)
        
        ydat= ravel(array(ydat))
        n, bins, patches = plt.gca().hist( ydat, nbins, normed= sum(ydat),facecolor= color) #, alpha=0.75
        if showNormCurv:
            # add a 'best fit' line
            st= statistics( ydat)
            sigma= st.stddev
            mu= st.mean
            y = mlab.normpdf( bins, mu, sigma)
            l = plt.gca().plot( bins, y, 'r--', linewidth=1)
            lg= plt.legend([l, patches[0]], ['fit', 'hist'])
            lg.draggable(True)
        plt.gca().hold( False)
        plt.updateControls()
        plt.canvas.draw() #self.figpanel
        return plt
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report(self, result):
        result.Show()
        self.log.write(self.plotName+ ' ' +self.translate('successful'))

class niceHistogram( _neededLibraries):
    '''this function is used to plot a nice histogram
    chart of the selected column'''   
    name=      u'Nice Histogram'
    plotName=  'histogram'
    image=     imag.niceHistogram
    def __init__(self):
        _neededLibraries.__init__(self)
        self.name=     u'Nice Histogram'
        self.plotName= 'histogram'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *args, **params):
        '''this function is used to plot a histogram chart of the selected column'''
        self.log.write(self.translate(u'Histogram Chart'))
        setting= {'Title': self.name,
                  '_size': Size(220,300)}
        self._updateColsInfo()
        if len(self.columnNames) == 0:
            self.log.write(self.translate(u'You need some data to draw a graph!'))
            return
        
        self.colours= ['random', 'blue', 'black',
                  'red', 'green', 'lightgreen', 'darkblue',
                  'yellow', 'hsv', 'white']
        # getting all the available figures
        path=  os.path.join( GetApp().installDir, 'nicePlot','images','histplot')
        self.figTypes= [fil[:-4] for fil in os.listdir(path) if fil.endswith('.png')]
        txt1= ['StaticText',   [self.translate(u'Histogram type')]]
        txt2= ['StaticText',   [self.translate(u'Colour')]]
        txt3= ['StaticText',   [self.translate(u'Select data to plot')]]
        txt4= ['StaticText',   [self.translate(u'number of bins')]]
        btn1= ['Choice',       [self.figTypes]]
        btn2= ['Choice',       [self.colours]]
        btn3= ['Choice',       [self.columnNames]] # trying to prevent out of memory error
        btn4= ['SpinCtrl',     [2,80,3]]
        ##btn5= ['ToggleButton', ['Show best Normal Curve']]
        structure= list()
        structure.append([txt3])
        structure.append([btn3])
        structure.append([btn4, txt4])
        ##structure.append([btn5])
        structure.append([btn1, txt1])
        structure.append([btn2, txt2])
        setting= {'Title': self.translate(self.name)}
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
        result= [_histogram().evaluate( array(colData), numBins)]
        plots = list()
        for res, varName in zip( result, self.colNameSelect):
            ydata= res[0]
            incr=  res[2]/2.0
            xdata= [x + incr for x in range( 1, len( res[0])+1)]
            plt= pltobj( None, xlabel= 'variable', ylabel= self.translate(u'value'), 
                         title= self.translate(u'Histogram Chart of ') + self.colNameSelect[0] )
            plt.gca().hold( True)
            labels= []
            plt.gca().hold( True)
            plothist(ax=     plt.gca(),
                    xdata=   xdata,
                    ydata=   ydata,
                    labels=  None,
                    colors=  self.colour,
                    figName= self.histType)
            
            if 0:
                # add a 'best fit' line
                st= statistics(xdat)
                sigma= st.stddev
                mu= st.mean
                ydat= array(ydat)
                ydat= ravel(ydat)
                y = mlab.normpdf( ydat, mu, sigma)
                l = plt.gca().plot(ydat, y, 'r--', linewidth=1)
            
            plt.gca().hold( False)
            plt.updateControls()
            plt.canvas.draw()
            plots.append( plt)
            
        return plots[0]
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        res= self._calc(*values)
        self._report(res)
        
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg == None:
            return
        if dlg.ShowModal() != _OK:
            dlg.Destroy()
            return
        
        values=   dlg.GetValue()
        
        self.colNameSelect= values[0]
        numBins=            values[1]
        #self.showNormCurv=  values[2]
        self.histType=      values[2]
        self.colour=        values[3]

        if self.colNameSelect == None:
            self.log.write(self.translate(u"you have to select at least %i columns")%self.minRequiredCols)
            return
        
        if self.histType == None:
            self.histType= self.figTypes[0]

        if self.colour == None:
            self.colour=  self.colours[0]
            
        if isinstance( self.colNameSelect, (str, unicode)):
            self.colNameSelect= [self.colNameSelect]

        if len( self.colNameSelect) == 0:
            self.SetStatusText( self.translate(u'You need to select some data to draw a graph!'))
            return
        
        # it only retrieves the numerical values
        columns= [self.grid.GetColNumeric( col) 
                   for col in self.colNameSelect] 
        
        return (columns, numBins)
    
    def _report(self, result): 
        for plt in result:
            plt.Show()
        self.log.write( self.name + ' ' + self.translate('successful'))

       
class cumulativeFrecuency( cumfreq, _neededLibraries):
    name=     u'Cumulative Frecuency'
    plotName= 'cumulativeFrecuency'
    image=    imag.cumulativeFrecuency
    def __init__(self):
        cumfreq.__init__(self)
        _neededLibraries.__init__(self)
        self.name=     u'Cumulative Frecuency'
        self.plotName= 'cumulativeFrecuency'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        # extracting data from the result
        ydat=         args[0]
        nbins=        args[1]
        # evaluating the histogram function to obtain the data to plot
        ydat= cumfreq().evaluate(ydat, nbins)
        
        plt= pltobj( None, xlabel= 'variable', ylabel= self.translate(u'value'), 
                     title= self.translate(u'Histogram Chart of ') + self.colNameSelect[0] )
        plt.gca().hold( True)
        
        ydat= ravel( array( ydat))
        binsize= ydat[2] 
        xdat= array( range( len( ydat[0])))*binsize + ydat[1]
        
        plt.gca().bar( xdat, ydat[0], binsize) 
        plt.gca().hold( False)
        plt.updateControls()
        plt.canvas.draw() #self.figpanel
        return plt
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report(self, result):
        [res.Show() for res in result]
        self.log.write(self.plotName+ ' ' + self.translate('successful'))

        
class relativefrequency( relfreq, _neededLibraries):
    name=     u'Realtive Frecuency'
    statName= 'relativeFrecuency'
    def __init__(self):
        relfreq.__init__(self)
        _neededLibraries.__init__(self)
        self.name=     u'Relative Frecuency'
        self.plotName= 'relativeFrecuency'
        self.minRequiredCols= 1
        self.colNameSelect= ''
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        # extracting data from the result
        ydat=         args[0]
        nbins=        args[1]
        # evaluating the histogram function to obtain the data to plot
        ydat= relfreq().evaluate(ydat, nbins)
        
        plt= pltobj( None, xlabel= 'variable', ylabel= self.translate(u'value'), 
                     title= self.translate(u'Histogram Chart of ') + self.colNameSelect[0] )
        plt.gca().hold( True)
        
        dat= array(ydat)
        ydat= ravel(ydat)
        plt.gca().hold( True)
        n, bins, patches = plt.gca().hist( ydat, nbins, normed= sum(ydat)) 
        plt.gca().hold( False)
        plt.updateControls()
        plt.canvas.draw() #self.figpanel
        return plt
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report(self, result):
        [res.Show() for res in result]
        self.log.write(self.plotName+ ' ' + self.translate('successful'))