'''
Created on 29/05/2012

@author: Sebastian Lopez Buritica <Colombia>
'''
from math import sqrt
class triplot:
    def __init__(self, data2plot):
        self.meshPoints = self._generateMeshPoints(10)
        # converting data to be reported
        data = data2plot['data']
        convertedData = list()
        for serie in data:
            x= list()
            y= list()
            for a,b,c in serie:
                (xi,yi)= triang2xy(a, b, c) 
                x.append(xi)
                y.append(yi)
            convertedData.append((x,y))
        self.xydata= convertedData
        
    def triang2xy(self,a,b,c, triangle = 'equilater'):
        '''a= 100%   (0, 0)
        b= 100%  (1, 0)
        c= 100%  (1/2, sqrt(3)/2'''
        if a < 0 or b < 0 or c < 0:
            raise StandardError('all input data must be positive')
        total = a+b+c
        return (2*b+c)/float(2*total), c*sqrt(3)/float(2*total)
        
    def _generateMeshPoints(self, divisions = 10):
        if divisions < 2:
            raise StandardError('el numero de divisiones debe ser mayor de 2')
        divisions = divisions/float(2)
        if divisions-int(divisions) > 0:
            divisions= int(divisions)+1
        lines= list()
        for a1 in range(0,divisions+1,1):
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

if __name__ == '__main__':
    points = generateMeshPoints()
    print points