__name__= u"Process Control"
__all__=  ['sixPack',]

A2 = [0,0, 1.886, 1.023, 0.729, 0.577, 0.483, 0.419, 0.373, 0.337, 0.308, 0.285, 0.266, 0.249, 0.235, 0.223]
A3 = [0,0, 2.659, 1.954, 1.628, 1.427, 1.287, 1.182, 1.099, 1.032, 0.975, 0.927, 0.886, 0.850, 0.817, 0.789]#, 0.680, 0.606]
D3 = [0,0, 0,     0,     0,     0,     0,     0.076, 0.136, 0.184, 0.223, 0.256, 0.283, 0.307, 0.328, 0.347]
D4 = [0,0, 3.268, 2.574, 2.282, 2.114, 2.004, 1.924, 1.864, 1.816, 1.777, 1.744, 1.717, 1.693, 1.672, 1.653]
# n   0 1      2      3      4      5      6      7      8      9     10     11     12     13     14     15       20     25
c4 = [0,0,0.7979,0.8862,0.9213,0.9400,0.9515,0.9594,0.9650,0.9693,0.9727,0.9754,0.9776,0.9794,0.9810,0.9823]#,0.9869,0.9896]
B3 = [0,0,     0,     0,     0,     0, 0.030, 0.118, 0.185, 0.239, 0.284, 0.322, 0.354, 0.382, 0.407, 0.428]#, 0.510, 0.565]
B4 = [0,0, 3.267, 2.568, 2.266, 2.089, 1.970, 1.882, 1.815, 1.761, 1.716, 1.678, 1.646, 1.619, 1.593, 1.572]#, 1.490, 1.435]
B5 = [0,0,     0,     0,     0,     0, 0.029, 0.113, 0.179, 0.232, 0.276, 0.313, 0.346, 0.374, 0.399, 0.421]#, 0.504, 0.559]
B6 = [0,0, 2.606, 2.276, 2.088, 1.964, 1.874, 1.806, 1.751, 1.707, 1.669, 1.637, 1.610, 1.585, 1.563, 1.544]#, 1.470, 1.420]


'''six pack for continue data
references:
1) http://en.wikipedia.org/wiki/Process_capability_index
2) http://en.wikipedia.org/wiki/Shewhart_individuals_control_chart
3) http://www.statisticalprocesscontrol.info/glossary.html
4) http://www.isixsigma.com/tools-templates/capability-indices-process-capability/process-capability-cp-cpk-and-process-performance-pp-ppk-what-difference/'''

from statlib import stats as _stats
from openStats import statistics
from statFunctions import _genericFunc
from wx import Size
from wx import ID_OK as _OK
import numpy
from imagenes import imageEmbed
from dialogs import  SixSigma
from slbTools import homogenize
import math
from openStats import normProb, normProbInv
 
class sixPack(_genericFunc):
    icon= imageEmbed().sixsigma16()
    name=      u"Six Sigma Pack"
    statName=  'sixpack'
    def __init__(self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=     'Six Sigma Pack'
        self.statName= 'sixpack'
        self.minRequiredCols= 1
        self.colNameSelect= ''
    
    def _dialog(self, *arg, **params):
        self._updateColsInfo() # update self.columnames and self.colnums
        return SixSigma(None, self.columnNames)
    
    def _showGui_GetValues(self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            (self.ColSelect, self.UCL, self.LCL, self.Target, self.k, self.groupSize) = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # changing value strings to numbers
        if len(self.ColSelect) == 0:
            self.logPanel.write(self.translate(u"You haven't selected a column!"))
            return
    
        # taking the data
        values=  self._convertColName2Values(self.ColSelect)
        self.columns= list()
        for val in values:
            col = numpy.array( val)
            col= numpy.ravel( col)
            self.columns.append( col)
        
        return (self.columns, self.UCL, self.LCL, self.Target, self.k, self.groupSize)
    
    def _calc(self, columns, *args, **params):
        return self.evaluate(columns, *args, **params)
        
    def object(self):
        return self._sixpack
    
    def evaluate(self, *args, **params):
        (columns, UCL, LCL, Target, k, groupSize)= args[0]
        if len(columns) == 1:
            result= self._sixpack(columns[0], UCL, LCL, Target, k, n= groupSize)
            Xga= statistics(columns[0]).mean
        else:
            # group homogenization in order to
            # obtain comparable data
            columns= homogenize(*columns)
            # get the size of the group
            groupSize= len(columns)
            # calculating the averages, ranges and standard deviations
            from scipy import stats
            rows= [[columns[pos][fil] for pos in range(len(columns))]
                   for fil in range(len(columns[0]))]
            del columns
            averages= [statistics(row).mean for row in rows]
            ranges= [max(row)-min(row) for row in rows]
            stddevs= [statistics(row).stddev for row in rows]
    
            Xga= statistics(averages).mean
            Ra= statistics(ranges).mean
            Sa= statistics(stddevs).mean
    
            # x-bar limits using Ra
            UCL_xbar= Xga + A2[groupSize]*Ra
            LCL_xbar= Xga - A2[groupSize]*Ra
    
            # R_ chart limits
            UCL_rchart= D4[groupSize]*Ra
            LCL_rchary= D3[groupSize]*Ra
    
            # S_chart limits
            UCL_schart= B4[groupSize]*Sa
            LCL_schart= B3[groupSize]*Sa
    
            self.columns= [numpy.array(averages)]
    
            result= self._sixpack(self.columns, UCL, LCL, Target, k, n= groupSize)
        return result
    
    def showGui(self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        result= self._calc(values)
        self._report(result)
        
    def _report(self, result):
        description= {'Desv.Est': self.translate(u'Standard Deviation'),
                      'Cp':  self.translate(u'Process Capability. A simple and straightforward indicator of process capability.'),
                      'Pp':  self.translate(u'Process Performance. A simple and straightforward indicator of process performance. basically tries to verify if the sample that you have generated from the process is capable to meet Customer CTQs (requirements)'),
                      'Cpk': self.translate(u'Process Capability Index. Adjustment of Cp for the effect of non-centered distribution. measures how close a process is running to its specification limits, relative to the natural variability of the process'),
                      'Ppk': self.translate(u'Process Performance Index. Adjustment of Pp for the effect of non-centered distribution.'),
                      'Cpm': self.translate(u'Estimates process capability around a target, it is also known as the Taguchi capability index'),
                      'ppm': self.translate(u'In a quality control context, PPM stands for the number of parts per million (cf. percent) that lie outside the tolerance limits')}
        

        general= {'Desv.Est': round( result['stddev'], 5),
                  'Pp':       round( result['Cp'],  5),
                  'Ppk':      round( result['Cpk'], 5),
                  'Cpm':      round( result['Cpm'], 5),
                  'ppm':      int( result['ppm']),}
        LCU=    result['LCU']
        LCL=    result['LCL']
        # se muestra los resultados
        self.outputGrid.addColData( [self.translate(u'Input Data')], pageName= self.translate(u'SixSigma'))
        self.outputGrid.addColData( [self.translate(u'UCL'), self.translate(u'LCL'),
                                     self.translate(u'target'), self.translate(u'k'), self.translate(u'group size')])
        self.outputGrid.addColData( [self.UCL, self.LCL, self.Target, self.k, self.groupSize])
        self.outputGrid.addColData( [self.translate(u'selected columns')],)
        self.outputGrid.addColData( self.ColSelect)
        keys= list()
        desc= list()
        values= list()
        for key,value in general.items():
            keys.append( key)
            desc.append( description[key])
            values.append( value)
        self.outputGrid.addColData( desc)
        self.outputGrid.addColData( keys)
        self.outputGrid.addColData( values)
        self.outputGrid.addColData( [self.translate('xbar chart Limits')])
        self.outputGrid.addColData( (self.translate(u'LCU'),self.translate(u'LCL')))
        self.outputGrid.addColData( (LCU, LCL))
        
        # control process chart
        data = self.columns[0]
        if 0:
            data2plot= {'UCL':     self.UCL,
                    'LCL':     self.LCL,
                    'target':  self.Target,
                    'data':    data,
                    }
            plt= self.plot(None, 'controlChart', data2plot,
                  title=   "Control Chart",
                  xlabel=   self.ColSelect[0],
                  ylabel=   self.ColSelect[0] + " Value")
            plt.Show()
            # normal probability chart
            pltNorm= self.plot(None, 'probabilityPlot', [data],
                      title=   "Normal probability plot",
                      )
            pltNorm.Show()
        # x-bar chart:
        xbar_data= (data[1:]+data[:-1])/2.0
        try:
            xbar_UCL=  Xga + A2[groupSize]*Ra
        except NameError:
            return
        xbar_LCL=  Xga - A2[groupSize]*Ra
        xbar_target= Xga
        data2plot= {'UCL':     xbar_UCL,
                    'LCL':     xbar_LCL,
                    'target':  xbar_target,
                    'data':    data,
                    }
        pltXbar= self.plot(None,    'controlChart', data2plot,
                      title=   "X-bar Chart",
                      xlabel=   self.ColSelect[0],
                      ylabel=   self.ColSelect[0] + " Value")
        pltXbar.Show()
        # r-chart:
        rchart_UCL= D4[groupSize]*Ra
        rchart_LCL= D3[groupSize]*Ra
        rchart_target= Ra
        # s-chart:
        schart_UCL= B4[groupSize]*Ra
        schart_LCL= B3[groupSize]*Ra
        schart_target= Sa
    
        self.Logg.write(self.translate(u'SixSigma') + ' '+self.translate('successful'))
        
        self.outputGrid.addColData(self.colNameSelect, self.name)
        self.outputGrid.addColData(result)
        self.Logg.write(self.translate(self.statName)+ ' '+self.translate('successful'))
        
        
    def _sixpack(self, data, UCL, LCL, Target, k= 6, n= 2 ):
        result= dict()
        stadis= statistics(data)
        stddev = stadis.stddev
        if stddev == 0:
            self.Logg.write(self.translate(u'Six pack analysis fail because the stddev is zero)'))
            return
    
        if UCL == None:
            UCL= stadis.mean+ 0.5*k*stadis.stddev
    
        if LCL == None:
            LCL= stadis.mean- 0.5*k*stadis.stddev
    
        if Target == None:
            Target= stadis.mean
    
        if UCL <= LCL:
            self.Logg.write(self.translate(u'Six pack analysis fail because LCL >= UCL  %f >= %f')%(LCL, UCL))
            return
    
        mean=     stadis.mean
        Cp=       (UCL-LCL)/float(k*stddev)
        Cpl=      2*(mean-LCL)/float(k*stddev)
        Cpu=      2*(UCL-mean)/float(k*stddev)
        Cpk=      min(Cpu, Cpl)
        va1=      (mean-Target)/float(stddev)
        val2=     math.sqrt(1+va1**2)
        val3=     Cp/float(val2)
        Cpm=      Cp/float(math.sqrt(1+((mean-Target)/float(stddev))**2))
        zUCL=     (UCL - mean)/float(stddev)
        zLCL=     (mean - LCL)/float(stddev)
        outOfUCL= sum([1 for x in data if x > UCL])
        outOfLCL= sum([1 for x in data if x < LCL])
        probUCL=  1 - normProb(zUCL)
        probLCL=  1 - normProb(zLCL)
        probTot=  probLCL + probUCL
        ppm=      int(probTot*1e6)
        sigmaLevel= normProbInv(1-probTot)+1.5
    
        # data for xbar chart
        mir= list()
        for x,y in zip(data[1:],data[:-1]):
            mir.append(abs(x-y))
        newData=       numpy.array(mir)
        rangeNewData=  max(newData)- min(newData)
        LCU=    stadis.mean+ A2[n]*rangeNewData
        LCL=    stadis.mean- A2[n]*rangeNewData
    
        for paramName, value in zip(['stddev', 'mean', 'Cp', 'Cpl', 'Cpu','Cpk',
                                     'zUCL', 'zLCL', 'probUCL', 'probLCL',
                                     'probTot', 'ppm', 'sigmaLevel', 'outOfUCL',
                                     'outOfLCL','Cpm','LCU','LCL',],
                                    [stddev, mean, Cp, Cpl, Cpu, Cpk, zUCL, zLCL,
                                     probUCL, probLCL, probTot, ppm, sigmaLevel,
                                     outOfUCL, outOfLCL, Cpm, LCU, LCL ]):
            result[paramName] = value
        return result