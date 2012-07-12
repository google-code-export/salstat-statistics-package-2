'''a module thath will be used as a container of different functions'''
version = "0.0.1"

from easyDialog import Dialog as _dialog
import wx
import numpy

class _genericFunc(object):
    def __init__(self):
        self.name = ""
        self.statName= ""
        self.setminRequiredCols= 0
        self.app=       wx.GetApp()
        self.inputGrid= self.app.inputGrid # to read the input data from the main grid
        self.dialog=    _dialog         # to create de dialod
        self.Logg=      self.app.Logg   # to report
        self.outputGrid= self.app.output # the usern can use the plot functions
        self.plot=      self.app.plot   # acces to the plot system
        
    def _updateColsInfo(self):
        gridCol=            self.inputGrid.GetUsedCols()
        self.columnNames=   gridCol[0]
        self.columnNumbers= gridCol[1]
        
    def _convertColName2Values(self, colNamesSelected, *args, **params):
        '''geting the selected columns of the InputGrid'''
        columns  = list()
        for colName in colNamesSelected:
            col= numpy.array( self.inputGrid.GetColNumeric( colName))
            col.shape = ( len(col),1)
            columns.append( col)
        
        return columns
    
    @property
    def name(self):
        return self.__name__
    @name.setter
    def name(self, name):
        if not isinstance(name, (str, unicode)):
            return
        self.__name__ = name
    @property
    def statName(self):
        return self.__statName__
    @statName.setter
    def statName(self, name):
        if not isinstance(name, (str,)):
            return
        self.__statName__ = name
    @property
    def minRequiredCols(self):
        return self._minRequiredCols
    @minRequiredCols.setter
    def minRequiredCols(self, value):
        if not isinstance(value, (int, float,numpy.ndarray )):
            return
        self._minRequiredCols= value
        
