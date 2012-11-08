__name__ = u'Bar plot'
__all__=  ['barChart', 'HorizBarChart',
           'barChartAllMeans', 'barChartAllMeansNice',
           'stakedBar']

from openStats import statistics

import numpy
from plotFunctions import _neededLibraries, pltobj, generateColors
from wx import ID_OK as _OK
from nicePlot.graficaRibon import plotBar
import os
import sys
from imagenes import imageEmbed
from slbTools import homogenize

imag = imageEmbed()
            
class barChart( _neededLibraries):
    ''''''
    name=      u'Bar chart'
    plotName=  'barChart'
    image=     imag.bars()
    def __init__(self):
        # getting all required methods
        _neededLibraries.__init__( self)
        self.name=      u'Bar chart'
        self.plotName=  'barChart'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *arg, **params):
        '''this funtcion is used to plot the bar chart of all means'''
        self.log.write(self.translate(u"Bar Chart"))
        self._updateColsInfo()
        if len( self.columnNames) == 0:
            return

        self.colours= ["blue", "black",
                  "red", "green", "lightgreen", "darkblue",
                  "yellow", "white"]
        txt2= ["StaticText",   [self.translate(u"Colour")]]
        txt3= ["StaticText",   [self.translate(u"Select data to plot")]]
        btn2= ["Choice",       [self.colours]]
        btn3= ["CheckListBox", [self.columnNames]]
        btn4= ["CheckBox",     [self.translate(u"push the values up to the bars")] ]
        structure= list()
        structure.append( [txt3])
        structure.append( [btn3])
        structure.append( [btn2, txt2])
        structure.append( [btn4])
        setting= {"Title": self.translate(self.name)}
        return self.dialog(settings= setting, struct= structure)        
    
    def _calc( self, columns, *args, **params):
        return [self.evaluate( col, *args, **params) for col in columns]
        
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
        
        self.colNameSelect=  values[0]
        self.colour=         values[1]
        showBarValues=       values[2]

        if self.colour == None:
            self.colour=  self.colours[0]
            
        if self.colNameSelect == None:
            self.log.write(self.translate(u"you have to select at least %i column")%self.minRequiredCols)
            return
        
        if isinstance( self.colNameSelect, (str, unicode)):
            self.colNameSelect= [self.colNameSelect]

        if len( self.colNameSelect) < self.minRequiredCols:
            self.log.write( self.translate(u'You have to select at least %i columns to draw a graph!')%self.minRequiredCols)
            return
        
        # it only retrieves the numerical values
        columns= [self.grid.GetColNumeric(col) for col in self.colNameSelect]
        
        return ( columns, self.colour, showBarValues)
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        # extracting data from the result
        ydata=         args[0]
        color=         args[1]
        showBarValues= args[2]
        
        # evaluating the histogram function to obtain the data to plot        
        plots= list()
        for ydat in ydata:
            plots.append( pltobj( None, xlabel= 'variable', ylabel= self.translate(u'value'), title= self.translate( self.name)))
            plt= plots[-1]
            plt.gca().hold( True)
            xdat= numpy.arange(1, len( ydat)+1)
            res= plt.gca().bar( xdat, ydat, color= color, align='center')
            width= res[0]._width/2.0
            plt.gca().set_xlim( min( xdat)-0.5, max( xdat)+width*2+0.5)
            plt.gca().set_ylim( numpy.array( plt.gca().get_ylim())*numpy.array( [1, 1.05]))
            if showBarValues:
                ax= plt.gca()
                for label, xpos, ypos in zip( ydat, xdat, ydat):
                    if isinstance(label, (str,unicode)):
                        ax.annotate(label, ( xpos, ypos), va="bottom", ha="center")
                        
                    elif int(label) == float(label):
                        label = int(label)
                        ax.annotate(r"%d" % label, ( xpos, label), va="bottom", ha="center")
                        
                    elif type(label) == type(1.1):
                        ax.annotate(r"%f" % label, ( xpos, label), va="bottom", ha="center")
                        
                    elif str(type(label)) == "<type 'numpy.int32'>":
                        ax.annotate(r"%d" % label, ( xpos, label), va="bottom", ha="center")
            else:
                plt.gca().set_xticks( xdat + width)
                plt.gca().set_xticklabels( self.colNameSelect)
       
            plt.gca().hold( False)
            plt.updateControls()
            plt.canvas.draw()
        return plots
    
    def showGui( self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc( *values)
        self._report( result)
        
    def _report( self, result):
        [res.Show() for res in result]
        self.log.write( self.plotName+ ' '+self.translate(u'successful'))

class HorizBarChart(barChart):
    ''''''
    name=      u'Horizontal bar chart'
    plotName=  'barChart'
    image=     imag.HorizBarChart()
    def __init__(self):
        barChart.__init__(self)
        name=      u'Horizontal bar chart'
        plotName=  'barChart'
    def evaluate( self, *args, **params):
        # extracting data from the result
        ydata=         args[0]
        color=         args[1]
        showBarValues= args[2]
        
        # evaluating the histogram function to obtain the data to plot        
        plots = list()
        for xdat in ydata:
            plots.append( pltobj( None, xlabel= self.translate(u'value'), ylabel= 'variable', title= self.translate(self.name)))
            plt= plots[-1]
            plt.gca().hold( True)
            ydat= numpy.arange( 1, len( xdat)+1)
            res= plt.gca().barh( ydat, xdat, color= color, align='center')
            width= res[0]._width/2.0
            plt.gca().set_xlim( numpy.array( plt.gca().get_xlim())*numpy.array( [1, 1.1]))
            if showBarValues:
                ax= plt.gca()
                for label, xpos, ypos in zip( xdat, xdat, ydat):
                    xpos+= 0.05* plt.gca().get_xlim()[-1]
                    if isinstance( label, (str, unicode)):
                        ax.annotate(label, (xpos, ypos), va="bottom", ha="center")
                        
                    elif int( label) == float( label):
                        label = int(label)
                        ax.annotate(r"%d" % label, ( xpos, ypos), va="bottom", ha="center")
                        
                    elif type( label) == type( 1.1):
                        ax.annotate(r"%f" % label, ( xpos, ypos), va="bottom", ha="center")
                        
                    elif str( type( label)) == "<type 'numpy.int32'>":
                        ax.annotate( r"%d" % label, ( xpos, ypos), va="bottom", ha="center")
            else:
                plt.gca().set_yticks( ydat + width)
                plt.gca().set_yticklabels( self.colNameSelect)
       
            plt.gca().hold( False)
            plt.updateControls()
            plt.canvas.draw()
        
        return plots
    
class barChartAllMeans( _neededLibraries):
    ''''''
    name=      u'Bar chart of all means'
    plotName=  'barChartMeans'
    image=     imag.barChartAllMeans()
    def __init__(self):
        # getting all required methods
        _neededLibraries.__init__( self)
        self.name=      u'Bar chart of all means'
        self.plotName=  'barChartMeans'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *arg, **params):
        '''this funtcion is used to plot the bar chart of all means'''
        self.log.write(self.translate(u"Bar Chart of All Means"))
        self._updateColsInfo()
        if len( self.columnNames) == 0:
            return

        self.colours= ["blue", "black",
                  "red", "green", "lightgreen", "darkblue",
                  "yellow", "white"]
        txt2= ["StaticText",   [self.translate(u"Colour")]]
        txt3= ["StaticText",   [self.translate(u"Select data to plot")]]
        btn2= ["Choice",       [self.colours]]
        btn3= ["CheckListBox", [self.columnNames]]
        btn4= ["CheckBox",     [self.translate(u"push the values up to the bars")] ]
        structure= list()
        structure.append( [txt3])
        structure.append( [btn3])
        structure.append( [btn2, txt2])
        structure.append( [btn4])
        setting= {"Title": self.translate(self.name)}
        return self.dialog(settings= setting, struct= structure)        
    
    def _calc( self, columns, *args, **params):
        return [self.evaluate( col, *args, **params) for col in columns]
        
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
        
        self.colNameSelect=  values[0]
        self.colour=         values[1]
        showBarValues=       values[2]

        if self.colour == None:
            self.colour=  self.colours[0]
            
        if self.colNameSelect == None:
            self.log.write(self.translate(u"you have to select at least %i columns")%self.minRequiredCols)
            return
        
        if isinstance( self.colNameSelect, (str, unicode)):
            self.colNameSelect= [self.colNameSelect]

        if len( self.colNameSelect) < self.minRequiredCols:
            self.log.write( self.translate(u'You have to select at least %i columns to draw a graph!')%self.minRequiredCols)
            return
        
        # it only retrieves the numerical values
        columns= [statistics( self.grid.GetColNumeric(col),'noname',None).mean for col in self.colNameSelect]
        
        return ( columns, self.colour, showBarValues)
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        # extracting data from the result
        ydat=         args[0]
        color=        args[1]
        showBarValues= args[2]
        
        # evaluating the histogram function to obtain the data to plot        
        plt= pltobj( None, xlabel= 'variable', ylabel= 'value', title= self.translate(self.name))
        plt.gca().hold( True)
        xdat= numpy.arange(1, len(ydat)+1)
        res= plt.gca().bar( xdat, ydat, color= color)
        width= res[0]._width/2.0
        plt.gca().set_xlim( min(xdat)-0.5, max(xdat)+width*2+0.5)
        plt.gca().set_ylim( numpy.array( plt.gca().get_ylim())*numpy.array( [1, 1.05]))
        
        if showBarValues:
            ax= plt.gca()
            for label, xpos, ypos in zip( self.colNameSelect, xdat, ydat):
                xpos+= width
                if isinstance(label, (str,unicode)):
                    ax.annotate(label, (xpos, ypos), va="bottom", ha="center")
                    
                elif int(label) == float(label):
                    label = int(label)
                    ax.annotate(r"%d" % label, (xpos, label), va="bottom", ha="center")
                    
                elif type(label) == type(1.1):
                    ax.annotate(r"%f" % label, (xpos, label), va="bottom", ha="center")
                    
                elif str(type(label)) == "<type 'numpy.int32'>":
                    ax.annotate(r"%d" % label, (xpos, label), va="bottom", ha="center")
        else:
            plt.gca().set_xticks(xdat + width)
            plt.gca().set_xticklabels(self.colNameSelect)
   
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
        self.log.write(self.plotName+ ' '+self.translate(u'successful'))

class barChartAllMeansNice( _neededLibraries):
    ''''''
    name=      u'Nice Bar chart of all means'
    plotName=  'barChartMeans'
    image=     imag.barChartAllMeansNice()
    def __init__(self):
        # getting all required methods
        _neededLibraries.__init__( self)
        self.name=      u'Nice Bar chart of all means'
        self.plotName=  'barChartMeans'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *arg, **params):
        '''this funtcion is used to plot the bar chart of all means'''
        self.log.write(self.translate(u"Nice Bar Chart of All Means"))
        self._updateColsInfo()
        if len( self.columnNames) == 0:
            return
        
        self.colours= ["radom","blue", "black",
                  "red", "green", "lightgreen", "darkblue",
                  "yellow", "white", "hsv"]
        path1= sys.argv[0]
        path1= path1.decode( sys.getfilesystemencoding())
        
        path=     os.path.join( os.path.split( path1 )[0], "nicePlot", "images", "barplot")
        self.figTypes= [fil[:-4] for fil in os.listdir(path) if fil.endswith(".png")]
        txt1= ["StaticText",   [self.translate(u"Bar type")] ]
        txt2= ["StaticText",   [self.translate(u"Colour")] ]
        txt3= ["StaticText",   [self.translate(u"Select data to plot")] ]
        btn1= ["Choice",       [self.figTypes] ]
        btn2= ["Choice",       [self.colours] ]
        btn3= ["CheckListBox", [self.columnNames] ]
        btn4= ["CheckBox",     [self.translate(u"push the labels up to the bars")] ]
        structure= list()
        structure.append( [txt3])
        structure.append( [btn3])
        structure.append( [btn4])
        structure.append( [btn1, txt1])
        structure.append( [btn2, txt2])
        setting= {"Title": self.translate(self.name)}
        return self.dialog( settings = setting, struct = structure)        
    
    def _calc( self, columns, *args, **params):
        return [self.evaluate( col, *args, **params) for col in columns]
        
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
        
        self.colNameSelect=  values[0]
        showBarValues=       values[1]
        barType=             values[2]
        self.colour=         values[3]
        
        if self.colour == None:
            self.colour=  self.colours[0]
            
        if self.colNameSelect == None:
            self.log.write(self.translate("you have to select at least %i columns")%self.minRequiredCols)
            return
        
        if isinstance( self.colNameSelect, (str, unicode)):
            self.colNameSelect= [self.colNameSelect]

        if len( self.colNameSelect) < self.minRequiredCols:
            self.log.write( self.translate(u'You need to select at least %i columns to draw a graph!')%self.minRequiredCols)
            return
        
        # it only retrieves the numerical values
        columns= [statistics( self.grid.GetColNumeric(col),'noname',None).mean for col in self.colNameSelect]
        if barType == None:
            barType= self.figTypes[0]
        
        return ( columns, self.colour, barType, showBarValues)
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        # extracting data from the result
        ydat=          args[0]
        color=         args[1]
        barType=       args[2]
        showBarValues= args[3]
        
        # evaluating the histogram function to obtain the data to plot        
        plt= pltobj( None, xlabel= 'variable', ylabel= self.translate(u'value'), title= self.translate(self.name))
        plt.gca().hold( True)
        
        xdat= numpy.arange( 1, len( ydat)+1)
        if showBarValues:
            labelsBar= self.colNameSelect
        else:
            labelsBar= None
            
        plotBar(ax=      plt.gca(),
                xdata=   xdat,
                ydata=   ydat,
                labels=  labelsBar,
                colors=  color,
                figName= barType)

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
        self.log.write(self.plotName + ' ' + self.translate('successful'))

class stakedBar(_neededLibraries):
    ''''''
    name=      u'Staked bar chart'
    plotName=  'barStaked'
    image=     imag.staked()
    def __init__(self):
        # getting all required methods
        _neededLibraries.__init__( self)
        self.name=      u'Staked bar chart'
        self.plotName=  'barStaked'
        self.minRequiredCols= 1
        self.colNameSelect= ''
        
    def _dialog(self, *arg, **params):
        '''this funtcion is used to plot the bar chart of all means'''
        self.log.write(self.translate(u"Bar Chart"))
        self._updateColsInfo()
        if len( self.columnNames) == 0:
            return

        txt2= ["StaticText",   [self.translate(u"xtics Labels")]]
        txt3= ["StaticText",   [self.translate(u"Select data to plot")]]
        btn2= ["Choice",       [self.columnNames]]
        btn3= ["CheckListBox", [self.columnNames]]
        structure= list()
        structure.append( [txt3])
        structure.append( [btn3])
        structure.append( [txt2])
        structure.append( [btn2])
        setting= {"Title": self.translate(self.name)}
        return self.dialog(settings= setting, struct= structure)
    
    def _calc( self, columns, *args, **params):
        return [self.evaluate( col, *args, **params) for col in columns]
        
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
        self.colNameSelect=  values[0]
        if values[1] != None:
            self.xticlabel=  self.grid.GetCol( values[1])
            
        if self.colNameSelect == None:
            self.log.write(self.translate("you have to select at least %i columns")%self.minRequiredCols)
            return
        
        if isinstance( self.colNameSelect, (str, unicode)):
            self.colNameSelect= [self.colNameSelect]

        if len( self.colNameSelect) < self.minRequiredCols:
            self.log.write( self.translate(u'You have to select at least %i columns to draw a graph!')%self.minRequiredCols)
            return
        
        # it only retrieves the numerical values
        columns= [self.grid.GetColNumeric(col) for col in self.colNameSelect]
        
        return ( columns, self.xticlabel)# self.colour, showBarValues)
        
    def _calc( self, *args, **params):
        return self.evaluate( *args, **params)
        
    def object( self):
        return self.evaluate
    
    def evaluate( self, *args, **params):
        # extracting data from the result
        ydata, passPos =  homogenize( *args[0], returnPos= True)
        if args[0] != None:
            xticLabel=  numpy.array(args[1])[passPos]
        else:
            xticLabel= None
                    
        plt= pltobj( None, xlabel= 'variable', ylabel= self.translate(u'value'), title= self.translate(self.name))
        plt.gca().hold( True)
        bars= list()
        ydatInit= numpy.array( ydata[0])*0
        xdat= numpy.arange( 1, len( ydatInit)+1)
        colour= generateColors()
        for ydat in ydata:
            ydat= numpy.array( ydat)
            bars.append( plt.gca().bar( xdat, ydat, bottom = ydatInit, color= colour.next())) #align = 'center',
            ydatInit = ydatInit + ydat
        width= bars[-1][0]._width/2.0
        plt.gca().set_xlim( min( xdat)-0.5, max( xdat)+width*2+0.5)
        plt.gca().set_ylim( numpy.array( plt.gca().get_ylim())*numpy.array( [1, 1.05]))
        plt.gca().set_xticks( xdat + width)
        plt.gca().set_xticklabels( xticLabel)
        plt.gca().hold( False)
        legend= plt.legend( [bar[0] for bar in bars], self.colNameSelect )
        legend.draggable(True)
        plt.updateControls()
        plt.canvas.draw()
        return [ plt]
    
    def showGui( self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc( *values)
        self._report( result)
        
    def _report( self, result):
        [res.Show() for res in result]
        self.log.write( self.plotName+ ' ' + self.translate('successful'))
