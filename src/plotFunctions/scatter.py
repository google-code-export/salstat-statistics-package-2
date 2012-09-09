__name__ = u"scatter"
__all__=  [u'scatter', 'adaptative',
           'box_whisker', 'normalProb']
from plotFunctions import _neededLibraries, pltobj, GaussianFilter
from plotFunctions import DropShadowFilter, generateColors
from wx import ID_OK as _OK
import wx
from openStats import statistics
from imagenes import imageEmbed
from numpy import array
import matplotlib.transforms as mtransforms # used to generate the lines shadow
from slbTools import homogenize
# import to be used to probability plot
from scipy.stats import probplot
from numpy import amin, amax, ndarray, array

imag= imageEmbed()

PROPLEGEND= {'size':11}

class scatter( _neededLibraries):
    name=      u"scatter"
    plotName=  u"scatter"
    image=     imag.scatter()
    def __init__( self):
        _neededLibraries.__init__(self)
        self.name=      u"scatter"
        self.plotName=  u"scatter"
        
    def _dialog(self, *arg, **params):
        self.log.write("Scatter")
        self._updateColsInfo()
        if self.columnNames == []:
            self.log.write("You need some data to draw a graph!")
            return

        bt1= ["StaticText", ["Select pairs of data by rows"]]
        bt2= ["makePairs",  [["X data to plot", "Y data to plot"], [self.columnNames]*2, 20]]
        structure= list()
        structure.append([bt1,])
        structure.append([bt2,])
        return self.dialog( struct= structure, settings = {"Title": "Scatter Chart Data" , "_size": wx.Size(300,500)},)

    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg == None:
            return
        
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        self.pairs= values[0]
        if len(self.pairs) == 0:
            return

        data= [(self.grid.GetCol( colX), self.grid.GetCol( colY), colX +" VS " +colY) for (colX, colY) in self.pairs]

        return data
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        plt= pltobj( None, xlabel= "X data", ylabel= "Y data", title= "Scatter Plot" )
        plt.gca().hold(True)
        listLegend= list()
        listPlot = list()
        for x,y,title in args:
            # se homogeniza la informacion
            (x, y) = homogenize( x, y)
            listPlot.append( plt.gca().plot( x, y, '.'))
            listLegend.append( title)
        legend= plt.legend( listPlot, listLegend, prop = PROPLEGEND)
        legend.draggable( state= True)
        plt.gca().hold( False)
        plt.updateControls()
        plt.canvas.draw()
        return plt
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report(self, result):
        result.Show()
        self.log.write(self.plotName+ ' successfull')

class adaptative( _neededLibraries):
    name=      u"Adaptative"
    plotName=  u"Adaptative"
    image=     imag.adaptative()
    def __init__( self):
        _neededLibraries.__init__(self)
        self.name=      u"Adaptative"
        self.plotName=  u"Adaptative"
        
    def _dialog(self, *arg, **params):
        self._updateColsInfo()
        if self.columnNames == []:
            self.log.write("You need some data to draw a graph!")
            return
        txt1= ['StaticText',    [u"Select data to plot"]]
        btn1= ['CheckListBox',    [self.columnNames]]
        structure= list()
        structure.append( [txt1])
        structure.append( [btn1])
        setting= {'Title': 'Adaptative chart of selected columns',
                  '_size': wx.Size( 250,320)}
        
        return self.dialog(settings= setting, struct= structure)
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg == None:
            return
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        self.columnNames = values[0]
        
        if len( self.columnNames) == 0:
            self.log.write("You need to select some data to draw a graph!")
            return
        
        return [self.grid.GetColNumeric(col) for col in self.columnNames]
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        plt= pltobj( None, xlabel = "variable",  ylabel = "value",
                     title= "Adaptative plot")
        
        plt.gca().hold(True)
        for serieNumber, serieData in enumerate(args): 
            xmin= serieNumber-0.4
            xmax= serieNumber+0.4
            size= len(serieData)
            if size == 0: continue
            step= 0.8/float(size)
            xdata= [ -0.4 + serieNumber + i*step for i in range(size)]
            plt.gca().plot( xdata, serieData, marker= '.', linestyle= '_')
        plt.gca().set_xticks( range( len( args)))
        plt.gca().set_xticklabels( self.columnNames )
        plt.gca().hold( False)
        plt.updateControls()
        plt.canvas.draw()
        return plt
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report(self, result):
        result.Show()
        self.log.write(self.plotName+ ' successfull')

class box_whisker(_neededLibraries):
    name= u"Box & Whisker"
    plotName=  u"boxWhisker"
    image=     imag.boxWhisker()
    def __init__( self):
        _neededLibraries.__init__(self)
        self.name=      u"Box & Whisker"
        self.plotName=  u"boxWhisker"
        
    def _dialog(self, *arg, **params):
        self._updateColsInfo()
        if self.columnNames == []:
            self.log.write("You need some data to draw a graph!")
            return
        txt1= ['StaticText',    [u"Select data to plot"]]
        btn1= ['CheckListBox',    [self.columnNames]]
        structure= list()
        structure.append( [txt1])
        structure.append( [btn1])
        setting= {'Title': 'Adaptative chart of selected columns',
                  '_size': wx.Size( 250,320)}
        
        return self.dialog(settings= setting, struct= structure)
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg == None:
            return
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        self.columnNames = values[0]
        
        if len( self.columnNames) == 0:
            self.log.write("You need to select some data to draw a graph!")
            return
        
        return [self.grid.GetColNumeric(col) for col in self.columnNames]
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        plt= pltobj( None, xlabel = "variable",  ylabel = "value",
                     title= self.name)
        
        plt.gca().boxplot( args, notch=0, sym='+', vert=1, whis=1.5,
                           positions=None, widths=None, patch_artist=False)
        plt.gca().set_xticklabels( self.columnNames)
        plt.updateControls()
        plt.canvas.draw()
        return plt
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report(self, result):
        result.Show()
        self.log.write(self.plotName+ ' successfull')
        
class normalProb( _neededLibraries):
    name=      u"Normal probability"
    plotName=  u"normalProb"
    image=     imag.normalProb()
    def __init__( self):
        _neededLibraries.__init__(self)
        self.name=      u"Normal probability"
        self.plotName=  u"normalProb"
        
    def _dialog(self, *arg, **params):
        self._updateColsInfo()
        if self.columnNames == []:
            self.log.write("You need some data to draw a graph!")
            return
        txt1= ['StaticText',    [u"Select data to plot"]]
        btn1= ['CheckListBox',   [self.columnNames]]
        structure= list()
        structure.append( [txt1])
        structure.append( [btn1])
        setting= {'Title': 'Adaptative chart of selected columns',
                  '_size': wx.Size( 250,320)}
        
        return self.dialog(settings= setting, struct= structure)
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg == None:
            return
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        self.columnNames = values[0]
        
        if len( self.columnNames) == 0:
            self.log.write("You need to select some data to draw a graph!")
            return
        
        return [self.grid.GetColNumeric(col) for col in self.columnNames]
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        listPlot= list()
        for ydat, varName in zip(args, self.columnNames):
            title=   self.name + u"of " + varName
                  
            listPlot.append( pltobj( None,
                                     xlabel=  "Order Statistic Medians",
                                     ylabel=  "Ordered Values",
                                     title= title))
            plt= listPlot[-1]
            if not isinstance( ydat,(ndarray,)):
                ydat= array( ydat)
            res=   probplot(ydat,)
            (osm,osr)=  res[0]
            (slope, intercept, r)= res[1]
            ax= plt.gca()
            ax.plot(osm, osr, 'o', osm, slope*osm + intercept)
            xmin, xmax= amin(osm),amax(osm)
            ymin, ymax= amin(ydat),amax(ydat)
            posx, posy= xmin+0.70*(xmax-xmin), ymin+0.01*(ymax-ymin)
            ax.text(posx,posy, "r^2=%1.4f" % r)
            plt.updateControls()
            plt.canvas.draw()
        return listPlot
        
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report(self, result):
        for res in result:
            res.Show()
        self.log.write(self.plotName+ ' successfull')