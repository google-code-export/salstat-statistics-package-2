__name__ = u"Lines and areas"
__all__=  [u'lines', u'linesOfMean','stem', 
           u'shadowLines', u'areaPlot',
           u'multipleAreaPlot']
from plotFunctions import _neededLibraries, pltobj, GaussianFilter
from plotFunctions import DropShadowFilter, generateColors
from wx import ID_OK as _OK
import wx
from openStats import statistics
from imagenes import imageEmbed
from numpy import array
import matplotlib.transforms as mtransforms # used to generate the lines shadow
from slbTools import homogenize
imag= imageEmbed()

class lines( _neededLibraries):
    name=      u"lines"
    plotName=  u"lines"
    image=     imag.lines()
    def __init__( self):
        _neededLibraries.__init__(self)
        self.name=      u"lines"
        self.plotName=  u"lines"

    def _dialog(self, *arg, **params):
        self._updateColsInfo()
        if self.columnNames == []:
            self.log.write(self.translate(u"You need some data to draw a graph!"))
            return
        
        return self.data2Plotdiaglog( None, self.columnNames, title= self.name)
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg == None:
            return
        if dlg.ShowModal() == _OK:
            selectedcols = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        self.log.write("selectedcols= " + selectedcols.__str__(), False)
        if len(selectedcols) == 0:
            self.log.write(self.translate(u"You need to select some data to draw a graph!"))
            return
        
        return selectedcols
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        # generate the chart
        selectedcols= args[0]
        data= [self.grid.GetColNumeric(colName) for colName in selectedcols ]
        data= [(range( len( data[i])), data[i], self.columnNames[i]) for i in range( len( data))]
        plt= pltobj(None, xlabel = "", ylabel = self.translate(u"value"), title= self.translate(self.name) )
        plt.gca().hold(True)
        listLegend= list()
        listPlot = list()
        for x,y,texto in data:
            listPlot.append( plt.gca().plot( x, y))
            listLegend.append(texto)
        legend= plt.legend( listPlot, listLegend) #self.figpanel
        legend.draggable( state = True)
        plt.gca().hold(False)
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
        self.log.write(self.plotName + ' ' + self.translate('successful'))
class stem( _neededLibraries):
    name=      u"stem"
    plotName=  u"stem"
    image=     imag.stem()
    def __init__( self):
        _neededLibraries.__init__(self)
        self.name=      u"stem"
        self.plotName=  u"stem"
        
    def _dialog(self, *arg, **params):
        self._updateColsInfo()
        if self.columnNames == []:
            self.log.write(self.translate(u"You need some data to draw a graph!"))
            return
        
        return self.data2Plotdiaglog( None, self.columnNames, title= self.name)
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg == None:
            return
        if dlg.ShowModal() == _OK:
            selectedcols = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        self.log.write("selectedcols= " + selectedcols.__str__(), False)
        if len(selectedcols) == 0:
            self.log.write(self.translate(u"You need to select some data to draw a graph!"))
            return
        
        return selectedcols
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        # generate the chart
        selectedcols= args[0]
        data= [self.grid.GetColNumeric(colName) for colName in selectedcols ]
        data= [(range( len( data[i])), data[i], self.columnNames[i]) for i in range( len( data))]
        plotList= list()
        for x,y,texto in data:
            plotList.append( pltobj(None, xlabel = "", ylabel = "value", title= self.name ))
            plt= plotList[-1]
            plt.gca().stem( x, y)
            plt.updateControls()
            plt.canvas.draw() #self.figpanel
            
        return plotList
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(*values)
        self._report(result)
        
    def _report(self, result):
        for res in result:
            res.Show()
        self.log.write(self.plotName+ ' ' + self.translate('successful'))
         
class linesOfMean( _neededLibraries):
    name=      u"lines of all means"
    plotName=  u"linesMean"
    image=     imag.linesOfMean()
    def __init__( self):
        _neededLibraries.__init__(self)
        self.name=      u"lines of all means"
        self.plotName=  u"linesMean"
                
    def _dialog(self, *arg, **params):
        self._updateColsInfo()
        if self.columnNames == []:
            self.log.write(self.translate(u"You need some data to draw a graph!"))
            return
        
        return self.data2Plotdiaglog( None, self.columnNames, title= self.name)
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg == None:
            return
        if dlg.ShowModal() == _OK:
            selectedcols = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        self.log.write("selectedcols= " + selectedcols.__str__(), False)
        if len(selectedcols) == 0:
            self.log.write(self.translate(u"You need to select some data to draw a graph!"))
            return
        
        return selectedcols
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        selectedcols= args[0]
        data = [statistics( self.grid.GetColNumeric( cols), "noname", None).mean for cols in selectedcols]
        plt= pltobj( None, xlabel = "", ylabel = self.translate(u"value"), title= self.translate(self.name))
        plt.gca().hold( True)
        listLegend= list()
        listPlot = list()
        listPlot.append( plt.gca().plot( range( len( data)), data) )
        listLegend.append( self.name)
        legend= plt.legend( listPlot, listLegend) #self.figpanel
        legend.draggable( state = True)
        plt.gca().hold( False)
        plt.updateControls()
        plt.canvas.draw() #self.figpanel
        return plt
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc( *values)
        self._report( result)
        
    def _report( self, result):
        result.Show()
        self.log.write( self.plotName + ' ' + self.translate(u'successful'))

class shadowLines(lines):
    name=      u"lines with shadow"
    plotName=  u"linesShadow"
    image=     imag.shadowLines()
    def __init__( self):
        lines.__init__(self)
        self.name=      u"lines with shadow"
        self.plotName=  u"linesShadow"
        
    def evaluate( self, *args, **params):
        # generate the chart
        selectedcols= args[0]
        data= [self.grid.GetColNumeric(colName) for colName in selectedcols ]
        data= [(range( len( data[i])), data[i], self.columnNames[i]) for i in range( len( data))]
        plt= pltobj(None, xlabel = "", ylabel = self.translate(u"value"), 
                    title= self.translate(self.name) )
        plt.gca().hold(True)
        listLegend= list()
        listPlot = list()
        for x,y,texto in data:
            listPlot.append( plt.gca().plot( x, y, mfc = "w", lw = 5, mew = 3, ms = 10,))
            listLegend.append( texto)
        gauss = DropShadowFilter( 4)
        
        for line in listPlot:
            # draw shadows with same lines with slight offset.
            line = line[0]
            xx = line.get_xdata()
            yy = line.get_ydata()
            shadow, = plt.gca().plot( xx, yy)
            shadow.update_from(line)
            # offset transform
            ot = mtransforms.offset_copy(line.get_transform(), plt.gca().figure,
                                         x=4.0, y=-6.0, units='points')
    
            shadow.set_transform(ot)
            # adjust zorder of the shadow lines so that it is drawn below the
            # original lines
            shadow.set_zorder(line.get_zorder()-0.5)
            shadow.set_agg_filter(gauss)
            shadow.set_rasterized(True) # to support mixed-mode renderers
        legend= plt.legend( listPlot, listLegend)
        legend.draggable( state = True)
        plt.gca().hold(False)
        plt.updateControls()
        plt.canvas.draw()
        return plt

class areaPlot( lines):
    name=      u"Area chart"
    plotName=  u"arePlot"
    image=     imag.areaPlot()
    def __init__( self):
        lines.__init__(self)
        self.name=      u"Area chart"
        self.plotName=  u"areaPlot"
        
    def _dialog(self, *arg, **params):
        self._updateColsInfo()
        if self.columnNames == []:
            self.log.write(self.translate(u"You need some data to draw a graph!"))
            return
        
        return self.data2Plotdiaglog( None, self.columnNames, title= self.name)
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg == None:
            return
        if dlg.ShowModal() == _OK:
            selectedcols = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        self.log.write("selectedcols= " + selectedcols.__str__(), False)
        if len(selectedcols) == 0:
            self.log.write(self.translate(u"You need to select some data to draw a graph!"))
            return
        
        return selectedcols
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        selectedcols= args[0]
        data= [ self.grid.GetColNumeric( colName) for colName in selectedcols ]
        data= [( range( len(data[i])), data[i], self.columnNames[i]) for i in range( len( data))]
        listPlot = list()
        for x, y, texto in data:
            listPlot.append( pltobj( None, xlabel = "", ylabel = "value", title= self.name ))
            plt= listPlot[-1]
            gca= plt.gca()
            x= [x[0]] + x[:] + [x[-1]]
            y= [0] + y[:] + [0]
            gca.fill( x, y)
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
        self.log.write(self.plotName+ ' ' + self.translate(u'successful'))
     
class multipleAreaPlot( lines):
    name=      u"Multiple area chart"
    plotName=  u"multiArePlot"
    image=     imag.multipleAreaPlot()
    def __init__( self):
        lines.__init__(self)
        self.name=      u"Multiple area chart"
        self.plotName=  u"areaPlot"
        
    def _dialog(self, *arg, **params):
        self._updateColsInfo()
        if self.columnNames == []:
            self.log.write(self.translate(u"You need some data to draw a graph!"))
            return
        
        return self.data2Plotdiaglog( None, self.columnNames, title= self.name)
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg == None:
            return
        if dlg.ShowModal() == _OK:
            self.colNameSelect = dlg.GetValue()[0]
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        self.log.write("selectedcols= " + self.colNameSelect.__str__(), False)
        if len( self.colNameSelect) == 0:
            self.log.write(self.translate(u"You need to select some data to draw a graph!"))
            return
        
        return homogenize(*[ self.grid.GetColNumeric( colName) for colName in self.colNameSelect ])
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        data= list( args)
        ydat= array( data.pop( 0))
        xdat= range( len( ydat))
        line= list()
        plt=  pltobj( None, xlabel = "", ylabel = self.translate(u"value"), 
                      title= self.translate(self.name) )
        gca= plt.gca()
        colour= generateColors()
        gca.fill_between( xdat, ydat*0, ydat, alpha=0.6, color= colour.next())
        line.append( ydat[0])
        if len(data) > 0:
            for ydat1 in data:
                ydat1= array( ydat1)
                gca.fill_between( xdat, ydat, ydat+ydat1, alpha=0.6, color= colour.next())
                ydat= ydat + ydat1
                line.append( ydat[0])
                
        legend= plt.legend( [lin for lin in line], self.colNameSelect)
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
        self.log.write(self.plotName + ' ' + self.translate('successful'))