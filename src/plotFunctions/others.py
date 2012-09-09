__name__ = u"Another plots"
__all__=  [u'linRegres']
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
from numpy import amin, amax, ndarray, array, arange
from pylab import axes
from statlib.stats import linregress

imag= imageEmbed()

PROPLEGEND= {'size':11}

class table( _neededLibraries):
    name=      u"table"
    plotName=  u"table"
    image=     imag.scatter()
    def __init__( self):
        _neededLibraries.__init__(self)
        self.name=      u"table"
        self.plotName=  u"table"
        
    def _dialog(self, *arg, **params):
        self._updateColsInfo()
        if self.columnNames == []:
            self.log.write("You need some data to draw a graph!")
            return
        txt1= ["StaticText",    ["Select data to plot"]]
        txt2= ["StaticText",    ["Select the name of the rows"]]
        btn1= ["CheckListBox",  [self.columnNames] ]
        btn2= ["Choice",        [self.columnNames]]
        structure= list()
        structure.append( [txt1,])
        structure.append( [btn1,])
        structure.append( [txt2,])
        structure.append( [btn2,])
        return self.dialog( struct= structure, settings = {"Title": self.name, "_size": wx.Size( 300,500)},)

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

        self.selectedColNames= values[0]
        if len(self.selectedColNames) == 0:
            return
        
        self.rowlabelsCol= values[1]
        if self.rowlabelsCol == None:
            self.log.write('the user have to select a name colum to the rows')
            return

        data, posvalid= homogenize(*[ self.grid.GetCol( colX) for colX in self.selectedColNames], returnPos= True )
        rowlabelsValue= self.grid.GetCol(self.rowlabelsCol)
        rowlabelsValue= [row for pos, row in enumerate(rowlabelsValue) if pos in posvalid]
        return [data,  rowlabelsValue]
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        data = args[0]
        rowLabels= args[1]
        colLabels= self.selectedColNames
        plt= pltobj( None, xlabel= "", ylabel= self.rowlabelsCol, title= "Table Plot" )

        plt.gca().hold(True)
        rows = len(data)
        colours= ['b']*rows
        
        ind = arange( len( colLabels)) + 0.3  # the x locations for the groups
        cellText = []
        width = 0.5     # the width of the bars
        yoff = array([ 0.0] * len( colLabels)) # the bottom values for stacked bar chart
        for row in xrange( rows):
            plt.gca().bar( ind, data[row], width, bottom=yoff, color= colours[row])
            yoff = yoff + data[row]
            cellText.append( ['%1.1f' % (x/1000.0) for x in yoff])
        
        # Add a table at the bottom of the axes
        axes( [0.2, 0.2, 0.7, 0.6])
        colours.reverse()
        cellText.reverse()
        the_table = plt.gca().table( cellText = cellText,
                                     rowLabels = rowLabels,
                                     rowColours = colours,
                                     colLabels = colLabels,
                                     loc = 'bottom')
        plt.gca().set_xticks([])              
        plt.gca().hold( False)
        plt.updateControls()
        plt.canvas.draw()
        axes([0.2, 0.2, 0.7, 0.7]) 
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

class linRegres( _neededLibraries):
    name=      u"linear regression"
    plotName=  u"linregres"
    image=     imag.linearRegres()
    def __init__( self):
        _neededLibraries.__init__(self)
        self.name=      u"linear regression"
        self.plotName=  u"linregres"
        
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
        return self.dialog( struct= structure, settings = {"Title": "Scatter Chart Data" , "_size": wx.Size(300, 400)},)

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
        listLegend= list()
        listPlot = list()
        for x, y, title in args:
            xlabel, ylabel = title.split(u" VS ")
            listPlot.append( pltobj( None, xlabel= xlabel, ylabel= ylabel, title= title ))
            plt= listPlot[-1]
            (x, y) = homogenize( x, y)
            line=  linregress(x,y)
            yfit= lambda x: x*line[0]+line[1]
            plot= plt.gca().plot(x,y,'b.',x,[yfit(x1) for x1 in x],'r')
            legend= plt.legend(plot,( title,'linRegressFit'), prop = PROPLEGEND)
            legend.draggable(state=True)
            arrow_args = dict(arrowstyle="->")
            bbox_args = dict(boxstyle="round", fc="w")
            text2anotate = "y="+str( round( line[0],4)) + \
                "x"
            if round( line[1],4) > 0:
                text2anotate += "+" + str( round( line[1],4))
            elif round(line[1],4) < 0:
                text2anotate += str( round( line[1],4))
            text2anotate += "\n r = " + str( round( line[2],6))
            an1= plt.gca().annotate( text2anotate, xy=(x[int( len( x)/2)],
                                                       yfit( x[int( len( x)/2)])),  xycoords='data',
                                                   ha="center", va="center",
                                                   bbox=bbox_args,
                                                   arrowprops=arrow_args)
            an1.draggable()
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