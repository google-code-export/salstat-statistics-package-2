__name__ = u"Lines and areas"
__all__=  [u'lines', u'linesOfMean', 
           u'shadowLines', u'areaPlot']
from plotFunctions import _neededLibraries, pltobj, GaussianFilter, DropShadowFilter
from wx import ID_OK as _OK
import wx
from openStats import statistics
from imagenes import imageEmbed
import matplotlib.transforms as mtransforms # used to generate the lines shadow
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
            self.log.write("You need some data to draw a graph!")
            return
        
        return self.data2Plotdiaglog( None, self.columnNames)
    
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
            self.log.write("You need to select some data to draw a graph!")
            return
        
        return selectedcols
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        # generate the chart
        selectedcols= args
        data= [self.grid.GetColNumeric(colName) for colName in selectedcols ]
        data= [(range( len( data[i])), data[i], self.columnNames[i]) for i in range( len( data))]
        plt= pltobj(None, xlabel = "", ylabel = "value", title= "Line plot" )
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
        self.log.write(self.plotName+ ' successfull')
        
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
            self.log.write("You need some data to draw a graph!")
            return
        
        return self.data2Plotdiaglog( None, self.columnNames)
    
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
            self.log.write("You need to select some data to draw a graph!")
            return
        
        return selectedcols
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        selectedcols= args
        data = [statistics( self.grid.GetColNumeric( cols), "noname", None).mean for cols in selectedcols]
        plt= pltobj( None, xlabel = "", ylabel = "value", title= "Line plot" )
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
        self.log.write( self.plotName+ ' successfull')        

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
        selectedcols= args
        data= [self.grid.GetColNumeric(colName) for colName in selectedcols ]
        data= [(range( len( data[i])), data[i], self.columnNames[i]) for i in range( len( data))]
        plt= pltobj(None, xlabel = "", ylabel = "value", title= "Line plot" )
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
    name=      u"Area plot"
    plotName=  u"arePlot"
    image=     imag.areaPlot()
    def __init__( self):
        lines.__init__(self)
        self.name=      u"Area plot"
        self.plotName=  u"areaPlot"
        
    def _dialog(self, *arg, **params):
        self._updateColsInfo()
        if self.columnNames == []:
            self.log.write("You need some data to draw a graph!")
            return
        
        return self.data2Plotdiaglog( None, self.columnNames)
    
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
            self.log.write("You need to select some data to draw a graph!")
            return
        
        return selectedcols
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        selectedcols= args
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
        self.log.write(self.plotName+ ' successfull')
     
#class plotScatter( _genericFrame):
        #self.gca().hold(True)
        #listLegend= list()
        #listPlot = list()
        #for x,y,texto in data2plot:
            ## se homogeniza la informacion
            #(x, y) = homogenize( x, y)
            #listPlot.append( self.gca().plot( x, y, '.'))
            #listLegend.append( texto)
        #legend= self.figpanel.legend( listPlot, listLegend, prop = PROPLEGEND)
        #legend.draggable( state= True)
        #self.gca().hold( False)
        #self.figpanel.canvas.draw()

    #def plotBar( self,data2plot):
        #DeprecationWarning( 'Deprecated function')
        ## warnings.warn( 'Deprecated function', DeprecationWarning)
        #self.gca().hold(True)
        #listLegend= list()
        #listPlot = list()
        #for y,texto in data2plot:
            #listPlot.append(self.gca().bar(range(len(y)),y))
            #listLegend.append(texto)
        #legend= self.figpanel.legend(listPlot,listLegend, prop = PROPLEGEND)
        #legend.draggable( state = True)
        #self.gca().hold( False)
        #self.figpanel.canvas.draw()

    #def plotNiceBar( self, data2plot):
        #xdat=  data2plot[0]
        #ydat=  data2plot[1]
        #label= data2plot[2]
        #colour= data2plot[3]
        #figNam= data2plot[4]
        #labelsBar= data2plot[5]
        #self.gca().hold( True)
        #plotBar(ax=      self.gca(),
                #xdata=   xdat,
                #ydata=   ydat,
                #labels=  labelsBar,
                #colors=  colour,
                #figName= figNam)
        #self.gca().hold( False)
        #self.figpanel.canvas.draw( )

    #def plotBarH( self,data2plot):
        #self.gca().hold(True)
        #listLegend= list()
        #listPlot=   list()
        #for y,texto in data2plot:
            #listPlot.append(self.gca().barh(range(len(y)),y,align='center'))
            #listLegend.append(texto)
        #legend= self.figpanel.legend(listPlot,listLegend,  prop = PROPLEGEND)
        #legend.draggable(state=True)
        #self.gca().hold(False)
        #self.figpanel.canvas.draw()

    #def plotLinRegress( self,data2plot):
        #x = data2plot[0]
        #y = data2plot[1]
        #line =  linregress(x,y)
        #yfit = lambda x: x*line[0]+line[1]
        #plt= self.gca().plot(x,y,'b.',x,[yfit(x1) for x1 in x],'r')
        #legend= self.figpanel.legend(plt,(data2plot[-1],'linRegressFit'), prop = PROPLEGEND)
        #legend.draggable(state=True)
        #arrow_args = dict(arrowstyle="->")
        #bbox_args = dict(boxstyle="round", fc="w")
        #text2anotate = "y="+str(round(line[0],4)) + \
            #"x"
        #if round(line[1],4) > 0:
            #text2anotate += "+" + str(round(line[1],4))
        #elif round(line[1],4) < 0:
            #text2anotate += str(round(line[1],4))
        #text2anotate += "\n r = " + str(round(line[2],6))
        #an1= self.gca().annotate(text2anotate, xy=(x[int(len(x)/2)],
                                                   #yfit(x[int(len(x)/2)])),  xycoords='data',
                                               #ha="center", va="center",
                                               #bbox=bbox_args,
                                               #arrowprops=arrow_args)
        #an1.draggable()
        #self.figpanel.canvas.draw()

    #def plotPie( self, data2plot):
        #labels = data2plot[0]#'Frogs', 'Hogs', 'Dogs', 'Logs'
        #fracs = data2plot[1]#[15,30,45, 10]
        #explode= data2plot[2]#(0, 0.05, 0, 0)
        #plt = self.figpanel.gca().pie( fracs, explode=explode,
                                       #labels=labels,
                                       #autopct='%1.1f%%',
                                       #shadow=True)
        #self.figpanel.canvas.draw()

    #def boxPlot(self,data2plot):
        #plt= self.gca().boxplot(data2plot, notch=0, sym='+', vert=1, whis=1.5,
                                #positions=None, widths=None, patch_artist=False)
        #self.figpanel.canvas.draw()

    #def plotNiceHistogram(self, data2plot):
        #(xdat, ydat, labels, color, figName, showNormCurv) = data2plot
        #labels= []
        #self.gca().hold( True)
        #plothist(ax=     self.gca(),
                #xdata=   xdat,
                #ydata=   ydat,
                #labels=  None,
                #colors=  color,
                #figName= figName)
        #if showNormCurv:
            ## add a 'best fit' line
            #st= statistics(xdat)
            #sigma= st.stddev
            #mu= st.mean
            #ydat= array(ydat)
            #ydat= ravel(ydat)
            #y = mlab.normpdf( ydat, mu, sigma)
            #l = self.gca().plot(ydat, y, 'r--', linewidth=1)
            
        #self.gca().hold( False)
        #self.figpanel.canvas.draw( )

    #def plotHistogram(self, data2plot):
        #(ydat, nbins, color, showNormCurv) = data2plot
        #dat= array(ydat)
        #ydat= ravel(ydat)
        #self.gca().hold( True)
        #n, bins, patches = self.gca().hist( ydat, nbins, normed= sum(ydat),facecolor= color) #, alpha=0.75
        #if showNormCurv:
            ## add a 'best fit' line
            #st= statistics( ydat)
            #sigma= st.stddev
            #mu= st.mean
            #y = mlab.normpdf( bins, mu, sigma)
            #l = self.gca().plot( bins, y, 'r--', linewidth=1)
        #self.gca().hold( False)
        #self.figpanel.canvas.draw( )

    #def plotTrian(self,data2plot):
        #'''data2plot = ((a,b,c,'legend'))'''
        #legends= data2plot[1]
        #data2plot= data2plot[0]
        #plotT = triplot(data2plot,)
        ## plot the mesh
        #ax= self.figpanel.gca()
        #ax.set_xticks([])
        #ax.set_yticks([])
        #ax.set_xlim((-0.08, 1.08))
        #ax.set_ylim((-0.08, 0.97))
        #ax.set_axis_off()

        #ax.hold(True)
        ##<p> plot the grid
        #a= plotT.meshLines[-1]
        #plotT.meshLines[-1] = [a[0][:4],a[1][:4]]
        #for pos,lineGrid in enumerate(plotT.meshLines):
            #if pos == 0:
                #ax.plot(lineGrid[0],lineGrid[1], 
                        #color= wx.Colour(0, 0, 0, 0.5),
                        #linestyle= '-',)
            #else:
                #ax.plot(lineGrid[0],lineGrid[1], 
                        #color= wx.Colour(0, 0, 0, 0.5),
                        #linestyle= '--',)
        ##plot the grid /<p>

        ##<p> generating a background patch
        ## changing triangular coordinates to xy coordinates
        #cord1= triang2xy(1,0,0)
        #cord2= triang2xy(0,1,0)
        #cord3= triang2xy(0,0,1)
        #Path = mpath.Path
        #pathdata = [(Path.MOVETO, cord1),
                    #(Path.LINETO, cord2),
                    #(Path.LINETO, cord3),
                    #(Path.CLOSEPOLY, cord1),
                    #]
        #codes, verts = zip(*pathdata)
        #path = mpath.Path(verts, codes)
        #patch = mpatches.PathPatch(path, facecolor='white', edgecolor='black', alpha=0.5)
        #ax.add_patch(patch)
        ##/<p>

        ## <p> adding Corner labels
        #cordLeft=  (-0.06, -0.03)
        #cordRigth= ( 1.06, -0.03)
        #cordUpper= ( 0.5, 0.94)
        #stylename= 'round'
        #fontsize= 13
        #an1=ax.text( cordLeft[0], cordLeft[1], legends[0],
                     #ha= "right",
                     #va= 'top',
                     #size= fontsize, #                 transform= ax.figure.transFigure,
                     #bbox=dict(boxstyle=stylename, fc="w", ec="k")) #              bbox=dict(boxstyle=stylename, fc="w", ec="k")

        #an2=ax.text( cordRigth[0], cordRigth[1],  legends[1],
                     #ha= "left",
                     #va= 'top',
                     #size= fontsize,#                 transform= ax.figure.transFigure,
                     #bbox=dict(boxstyle=stylename, fc="w", ec="k"))

        #an3=ax.text( cordUpper[0], cordUpper[1],  legends[2],
                     #ha= "center",
                     #va= 'baseline',
                     #size= fontsize, #                 transform= ax.figure.transFigure,
                     #bbox=dict(boxstyle=stylename, fc="w", ec="k"))
        ## adding coordinates  /<p>

        ##<p> add a ruler
        #for line in plotT.ruler:
            #ax.plot(line[0],line[1], 
                    #color= wx.Colour(0, 0, 0, 0),
                    #linestyle= '-',)
        ## numbering the ruler
        #for key, values in plotT.dataLabel.items():
            #if key == 'AC':
                #for ((x,y), value) in zip(values, range(10,-1,-1)):
                    #value = value/float(10)
                    #ax.text(x, y, str(value),
                            #horizontalalignment= 'right',
                            #verticalalignment=   'bottom',
                            #fontsize=            10)
                        ##transform=           ax.transAxes)
            #if key == 'CB':
                #for ((x,y), value) in zip(values, range(10,-1,-1)):
                    #value = value/float(10)
                    #ax.text(x, y, str(value),
                            #horizontalalignment= 'left',
                            #verticalalignment=   'bottom',
                            #fontsize=            10)
            #if key == 'AB':
                #for ((x,y), value) in zip(values, range(10,-1,-1)):
                    #value = value/float(10)
                    #ax.text(x, y, str(value),
                            #horizontalalignment= 'center',
                            #verticalalignment=   'top',
                            #fontsize=            10)
        ## add the ruler /<p>

        #listPlot = list()
        #for data in plotT.xydata:
            #listPlot.append( ax.plot( data[0],data[1],
                                      #linestyle= '_', marker='d'))

        #listLegend= [dat[3] for dat in data2plot]
        #legend= self.figpanel.legend( listPlot, listLegend, prop = PROPLEGEND)
        #legend.draggable( state= True)
        #ax.hold(False)
        #self.figpanel.canvas.draw(0)

    #def AdaptativeBMS(self, data, xlabel='', ylabel='', title=''):
        #self.figpanel.gca().hold(True)
        #for serieNumber, serieData in enumerate(data): 
            #xmin= serieNumber-0.4
            #xmax= serieNumber+0.4
            #size= len(serieData)
            #if size == 0: continue
            #step= 0.8/float(size)
            #xdata= [ -0.4 + serieNumber + i*step for i in range(size)]
            #self.gca().plot(xdata, serieData, marker= '.', linestyle= '_')
        #self.gca().set_xticks(range(len(data)))
        #self.figpanel.gca().set_title(title)
        #self.figpanel.gca().set_xlabel(xlabel)
        #self.figpanel.gca().set_ylabel(ylabel)
        #self.figpanel.gca().hold(False)
        #self.figpanel.canvas.draw()
        
    #def probabilityPlot(self, data2plot):
        #import scipy.stats as stats2
        #from numpy import amin, amax
        #if not isinstance(data2plot[0],(np.ndarray,)):
            #data2plot[0]= np.array(data2plot[0])
        #res=   stats2.probplot(data2plot[0],)
        #(osm,osr)=  res[0]
        #(slope, intercept, r)= res[1]
        #ax= self.figpanel.gca()
        #ax.plot(osm, osr, 'o', osm, slope*osm + intercept)
        #xmin, xmax= amin(osm),amax(osm)
        #ymin, ymax= amin(data2plot),amax(data2plot)
        #posx, posy= xmin+0.70*(xmax-xmin), ymin+0.01*(ymax-ymin)
        #ax.text(posx,posy, "r^2=%1.4f" % r)
        #self.figpanel.canvas.draw()

    #def controlChart(self, data2plot):
        #UCL= data2plot['UCL']
        #LCL= data2plot['LCL']
        #target= data2plot['target']
        #data= data2plot['data']
        #posDataOutSide= list()
        ## plot all data
        #self.gca().plot(range(len(data)),data,marker= 'o')
        #self.gca().hold(True)
        #for pos, value in enumerate(data):
            #if value > UCL or value < LCL:
                #posDataOutSide.append((pos,value))
        ## then plot the violating points
        #self.gca().plot([dat[0] for dat in posDataOutSide],
                        #[dat[1] for dat in posDataOutSide],
                        #linestyle= '_', color='r', marker='d')
        ## UCL, LCL  Lines
        #self._OnAddRefHorzLine( evt= None, ypos= UCL, color= 'r')
        #self._OnAddRefHorzLine( evt= None, ypos= LCL, color= 'r')
        ## Target Line
        #self._OnAddRefHorzLine( evt= None, ypos= target, color= 'k')
        #self.gca().hold(False)
        #self.figpanel.canvas.draw()

    
    