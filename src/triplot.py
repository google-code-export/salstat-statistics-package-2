'''
Created on 29/05/2012

@author: 2012 Sebastian Lopez Buritica <Colombia>
'''

from math import sqrt
from slbTools import homogenize, isnumeric
import wx

class triplot:
    def __init__(self, data2plot):
        self.meshLines = self._generateMeshPoints(10)
        # converting data to be reported
        data = data2plot
        convertedData = list()
        for avec, bvec, cvec,legend in data:
            x= list()
            y= list()
            # homogenizing the data
            (avec, bvec, cvec) = homogenize( avec, bvec, cvec)
            for a, b, c in zip( avec, bvec, cvec):
                (xi, yi)= triang2xy( a, b, c) 
                x.append( xi)
                y.append( yi)
            convertedData.append( (x, y, legend))
        self.xydata= convertedData
        self.ruler= self._generateRuler()
        self.dataLabel= self._generatePosLabel()
  
    def _generatePosLabel(self):
        result= dict()
        data=   list()
        val1= -0.023
        for xa in range(0,11,1):
            xa= xa/float(10)
            xb= 0
            xc= 1-xa
            xip, yip= triang2xy(xa, val1, xc) 
            data.append((xip, yip))
        result['AC']= data
        data= list()
        for xa in range(0,11,1):
            xa= xa/float(10)
            xb= 0
            xc= 1-xa
            xip, yip= triang2xy(val1, xc,  xa) 
            data.append((xip, yip))
        result['CB']= data
        data= list()
        for xa in range(0,11,1):
            xa= xa/float(10)
            xb= 0
            xc= 1-xa
            xip, yip= triang2xy(xc, xa,  val1) 
            data.append((xip, yip))
        result['AB']= data
        return result
        
    def _generateRuler(self):
        data= list()
        val1= -0.022
        val2= -0.015
        val3= -0.007
        # for AC side
        for xa in range(0,11,1):
            xa= xa/float(10)
            xb= 0
            xc= 1-xa
            xi, yi= triang2xy(xa, xb, xc)
            xip, yip= triang2xy(xa, val1, xc) 
            x= [xi, xip]
            y= [yi, yip]
            data.append((x, y))
        for xa in range(1,20,1):
            xa= xa/float(20)
            xb= 0
            xc= 1-xa
            xi, yi= triang2xy(xa, xb, xc)
            xip, yip= triang2xy(xa, val2, xc) 
            x= [xi, xip]
            y= [yi, yip]
            data.append((x, y))
        for xa in range(1,101,1):
            xa= xa/float(100)
            xb= 0
            xc= 1-xa
            xi, yi= triang2xy(xa, xb, xc)
            xip, yip= triang2xy(xa, val3, xc) 
            x= [xi, xip]
            y= [yi, yip]
            data.append((x, y))
        # for CB side
        for xa in range(0,11,1):
            xa= xa/float(10)
            xb= 0
            xc= 1-xa
            xi, yi= triang2xy(xb, xc,   xa)
            xip, yip= triang2xy(val1, xc,  xa) 
            x= [xi, xip]
            y= [yi, yip]
            data.append((x, y))
        for xa in range(1,20,1):
            xa= xa/float(20)
            xb= 0
            xc= 1-xa
            xi, yi= triang2xy(xb, xc,   xa)
            xip, yip= triang2xy( val2, xc,   xa) 
            x= [xi, xip]
            y= [yi, yip]
            data.append((x, y))
        for xa in range(1,101,1):
            xa= xa/float(100)
            xb= 0
            xc= 1-xa
            xi, yi= triang2xy(xb, xc,   xa)
            xip, yip= triang2xy( val3, xc,   xa) 
            x= [xi, xip]
            y= [yi, yip]
            data.append((x, y))
        # for AB side
        for xa in range(0,11,1):
            xa= xa/float(10)
            xb= 0
            xc= 1-xa
            xi, yi= triang2xy(xc,  xa,  xb)
            xip, yip= triang2xy(xc, xa,  val1) 
            x= [xi, xip]
            y= [yi, yip]
            data.append((x, y))
        for xa in range(1,20,1):
            xa= xa/float(20)
            xb= 0
            xc= 1-xa
            xi, yi= triang2xy(xc,  xa,  xb)
            xip, yip= triang2xy(xc,  xa, val2) 
            x= [xi, xip]
            y= [yi, yip]
            data.append((x, y))
        for xa in range(1,101,1):
            xa= xa/float(100)
            xb= 0
            xc= 1-xa
            xi, yi= triang2xy(xc,  xa,  xb)
            xip, yip= triang2xy(xc,  xa,  val3) 
            x= [xi, xip]
            y= [yi, yip]
            data.append((x, y))
        return data
    
    def _generateMeshPoints(self, divisions = 10):
        if divisions < 2:
            raise StandardError('el numero de divisiones debe ser mayor de 2')
        divisions = divisions/float(2)
        if divisions-int(divisions) > 0:
            divisions= int(divisions)+1
        lines= list()
        for a1 in range(0,int(divisions)+1,1):
            x= list()
            y= list()
            a1= a1/float(10)
            a1= [(a1, 0, 1-a1),
                 (0, a1, 1-a1),
                 (1-a1, a1, 0),
                 (1-a1, 0, a1),
                 (0, 1-a1, a1),
                 (a1, 1-a1, 0),
                 (a1, 0, 1-a1)]
            a1 = [triang2xy(*ai) for ai in a1]
            for xi,yi in a1:
                x.append(xi)
                y.append(yi)
            lines.append((x,y))
        return lines

def triang2xy( a, b, c, triangle = 'equilater'):
    '''a= 100%   (0, 0)
    b= 100%  (1, 0)
    c= 100%  (1/2, sqrt(3)/2'''
    #if a < 0 or b < 0 or c < 0:
    #    raise StandardError('all input data must be positive')
    # check if the data is numeric
    def _orga(a):
        if not isinstance(a, (str, unicode)):
            a= a.__str__()
            
    if sum([isnumeric(i) for i in [a, b, c]]) != 3:
        _orga(a)
        _orga(b)
        _orga(c)
        wx.GetApp().Logg.write('the point failed (%s,%s,%s)'%(a, b, c,), False)
        return
    
    total = a+b+c
    if total == 0:
        return 0,0
    return (2*b+c)/float(2*total), c*sqrt(3)/float(2*total)