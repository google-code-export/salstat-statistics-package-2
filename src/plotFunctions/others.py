__name__ = u"Another plots"
__all__=  [u'linRegres','ternaryScatter']
from plotFunctions import _neededLibraries, pltobj
from wx import ID_OK as _OK
import wx
from imagenes import imageEmbed
from slbTools import homogenize
# import to be used to probability plot
from numpy import array, arange
from pylab import axes
from statlib.stats import linregress
from triplot import triplot, triang2xy
import matplotlib.path as mpath
import matplotlib.patches as mpatches

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
            self.log.write(self.translate(u"You need some data to draw a graph!"))
            return
        txt1= ["StaticText",    [self.translate(u"Select data to plot")]]
        txt2= ["StaticText",    [self.translate(u"Select the name of the rows")]]
        btn1= ["CheckListBox",  [self.columnNames] ]
        btn2= ["Choice",        [self.columnNames]]
        structure= list()
        structure.append( [txt1,])
        structure.append( [btn1,])
        structure.append( [txt2,])
        structure.append( [btn2,])
        return self.dialog( struct= structure, settings = {"Title": self.translate(self.name),
                                                           "_size": wx.Size( 300,500)},)

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
            self.log.write(self.translate(u'the user have to select a name colum to the rows'))
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
        plt= pltobj( None, xlabel= "", ylabel= self.rowlabelsCol, title= self.translate(self.name) )

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
        self.log.write(self.plotName + ' ' + self.translate('successful'))

class linRegres( _neededLibraries):
    name=      u"linear regression"
    plotName=  u"linregres"
    image=     imag.linearRegres()
    def __init__( self):
        _neededLibraries.__init__(self)
        self.name=      u"linear regression"
        self.plotName=  u"linregres"
        
    def _dialog(self, *arg, **params):
        self.log.write(self.translate(self.name))
        self._updateColsInfo()
        if self.columnNames == []:
            self.log.write(self.translate(u"You need some data to draw a graph!"))
            return

        bt1= ["StaticText", [self.translate(u"Select pairs of data by rows")]]
        bt2= ["makePairs",  [[self.translate(u"X data to plot"), self.translate(u"Y data to plot")], [self.columnNames]*2, 20]]
        structure= list()
        structure.append([bt1,])
        structure.append([bt2,])
        return self.dialog( struct= structure, settings = {"Title": self.translate(u"Scatter Chart Data") ,
                                                           "_size": wx.Size(300, 400)},)

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
            legend= plt.legend(plot,( title,self.translate(u'linear Regression')), prop = PROPLEGEND)
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
        self.log.write(self.plotName+ ' '+self.translate(u'successful'))

class ternaryScatter( _neededLibraries):
    name=      u"Ternary scatter"
    plotName=  u"ternaryscatter"
    image=     imag.ternary()
    
    def __init__( self):
        _neededLibraries.__init__(self)
        self.name=      u"Ternary scatter"
        self.plotName=  u"ternaryscatter"
        
    def _dialog(self, *arg, **params):
        self._updateColsInfo()
        if len(self.columnNames) == 0:
            self.log.write( self.translate( u"You need some data to draw a graph!"))
            return
        
        txt1= ["StaticText", [self.translate(u"Left Corner Label")]]
        txt2= ["StaticText", [self.translate(u"Right Corner Label")]]
        txt3= ["StaticText", [self.translate(u"Upper Corner Label")]]
        btn1= ["TextCtrl",   [self.translate(u"A")]]
        btn2= ["TextCtrl",   [self.translate(u"B")]]
        btn3= ["TextCtrl",   [self.translate(u"C")]]
        btn4= ["StaticText", [self.translate(u"Select the pairs of data by rows")]]
        btn5= ["makePairs",  [[self.translate(u"A Left Corner"),self.translate(u"C Upper Corner"),
                               self.translate(u"B Right Corner")], [self.columnNames]*3, 30]]
        structure= list()
        structure.append( [btn1, txt1])
        structure.append( [btn2, txt2])
        structure.append( [btn3, txt3])
        structure.append( [btn4,])
        structure.append( [btn5,])
        settings = {"Tile": self.translate(u"Ternary plot dialog") ,
                    "_size": wx.Size(410, 400),}
        return self.dialog( settings= settings, struct= structure)

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
        
        Alabel= values[0]
        if Alabel == u'' or Alabel.replace(' ','') == u'':
            Alabel= u'A'

        Blabel= values[1]
        if Blabel == u'' or Blabel.replace(' ','') == u'':
            Blabel= u'B'

        Clabel= values[2]
        if Clabel == u'' or Clabel.replace(' ','') == u'':
            Clabel= u'C'

        pairs= values[3]
        if len(pairs) == 0:
            return

        data= [(self.grid.GetCol( colLeft),
                self.grid.GetCol( colUpper),
                self.grid.GetCol( colRight),
                colLeft+' - '+colUpper+' - '+colRight )
               for (colLeft, colUpper, colRight) in pairs]
        
        return (data, [Alabel, Blabel, Clabel] )
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        data2plot= args
        legends= data2plot[1]
        data2plot= data2plot[0]
        plotT = triplot(data2plot,)
        plt= pltobj( None, xlabel= "", ylabel= "", title= self.name )
        # plot the mesh
        ax= plt.gca()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim((-0.08, 1.08))
        ax.set_ylim((-0.08, 0.97))
        ax.set_axis_off()
        ax.hold(True)
        #<p> plot the grid
        a= plotT.meshLines[-1]
        plotT.meshLines[-1] = [a[0][:4],a[1][:4]]
        for pos,lineGrid in enumerate(plotT.meshLines):
            if pos == 0:
                ax.plot(lineGrid[0],lineGrid[1], 
                        color= wx.Colour(0, 0, 0, 0.5),
                        linestyle= '-',)
            else:
                ax.plot(lineGrid[0],lineGrid[1], 
                        color= wx.Colour(0, 0, 0, 0.5),
                        linestyle= '--',)
        #plot the grid /<p>

        #<p> generating a background patch
        # changing triangular coordinates to xy coordinates
        cord1= triang2xy(1,0,0)
        cord2= triang2xy(0,1,0)
        cord3= triang2xy(0,0,1)
        Path = mpath.Path
        pathdata = [(Path.MOVETO, cord1),
                    (Path.LINETO, cord2),
                    (Path.LINETO, cord3),
                    (Path.CLOSEPOLY, cord1),
                    ]
        codes, verts = zip(*pathdata)
        path = mpath.Path(verts, codes)
        patch = mpatches.PathPatch(path, facecolor='white', edgecolor='black', alpha=0.5)
        ax.add_patch(patch)
        #/<p>

        # <p> adding Corner labels
        cordLeft=  (-0.06, -0.03)
        cordRigth= ( 1.06, -0.03)
        cordUpper= ( 0.5, 0.94)
        stylename= 'round'
        fontsize= 13
        an1=ax.text( cordLeft[0], cordLeft[1], legends[0],
                     ha= "right",
                     va= 'top',
                     size= fontsize, #                 transform= ax.figure.transFigure,
                     bbox=dict( boxstyle=stylename, fc="w", ec="k")) #              bbox=dict(boxstyle=stylename, fc="w", ec="k")

        an2=ax.text( cordRigth[0], cordRigth[1],  legends[1],
                     ha= "left",
                     va= 'top',
                     size= fontsize,#                 transform= ax.figure.transFigure,
                     bbox=dict( boxstyle=stylename, fc="w", ec="k"))

        an3=ax.text( cordUpper[0], cordUpper[1],  legends[2],
                     ha= "center",
                     va= 'baseline',
                     size= fontsize, #                 transform= ax.figure.transFigure,
                     bbox=dict( boxstyle=stylename, fc="w", ec="k"))
        # adding coordinates  /<p>

        #<p> add a ruler
        for line in plotT.ruler:
            ax.plot(line[0],line[1], 
                    color= wx.Colour( 0, 0, 0, 0),
                    linestyle= '-',)
        # numbering the ruler
        for key, values in plotT.dataLabel.items():
            if key == 'AC':
                for ((x,y), value) in zip( values, range( 10,-1,-1)):
                    value = value/float( 10)
                    ax.text(x, y, str( value),
                            horizontalalignment= 'right',
                            verticalalignment=   'bottom',
                            fontsize=            10)
                        #transform=           ax.transAxes)
            if key == 'CB':
                for ((x,y), value) in zip( values, range( 10,-1,-1)):
                    value = value/float( 10)
                    ax.text(x, y, str(value),
                            horizontalalignment= 'left',
                            verticalalignment=   'bottom',
                            fontsize=            10)
            if key == 'AB':
                for ((x,y), value) in zip( values, range( 10,-1,-1)):
                    value = value/float(10)
                    ax.text(x, y, str(value),
                            horizontalalignment= 'center',
                            verticalalignment=   'top',
                            fontsize=            10)
        # add the ruler /<p>

        listPlot = list()
        for data in plotT.xydata:
            listPlot.append( ax.plot( data[0],data[1],
                                      linestyle= '_', marker='d'))

        listLegend= [dat[3] for dat in data2plot]
        legend= plt.legend( listPlot, listLegend, prop = PROPLEGEND)
        legend.draggable( state= True)
        ax.hold(False)
        plt.updateControls()
        plt.canvas.draw(0)
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