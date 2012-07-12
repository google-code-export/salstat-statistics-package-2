'''One condition test'''
__name__ ='One condition test'
from statlib import stats as _stats
import numpy
# _genericFunc ist called from the __init__.py file
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size
from openStats import OneSampleTests
        
class oneConditionTest(_genericFunc):
    def __init__( self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=     'One condition test'
        self.statName= 'oneConditionTest'
        self.minRequiredCols= 1
        self.colNameSelect= []
        self.tests= []
        self.hypotesis= 0
        
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,
                  '_size':  Size(280,430)}
        self._updateColsInfo() # update self.columnames and self.colnums
        btn1= ['StaticText',   ['Select the columns to analyse']]
        btn2= ['CheckListBox', [self.columnNames]]
        btn3= ['StaticText',   ['Choose test(s)']]
        btn4= ['CheckListBox',  [['t-test', 'Sign Test', 'Chi square test for variance'],]]
        btn5= ['RadioBox',     ['Select hypothesis',   ['One tailed','Two tailed'],]]
        btn6= ['StaticText',   ['User hypothesised mean']]
        btn7= ['NumTextCtrl',  []]
        structure= list()
        structure.append( [btn1,])
        structure.append( [btn2,])
        structure.append( [btn3,])
        structure.append( [btn4,])
        structure.append( [btn5,])
        structure.append( [btn7, btn6])
        return self.dialog( settings = setting, struct = structure)
    
    def _showGui_GetValues( self):
        dlg= self._dialog()
        if dlg.ShowModal() == _OK:
            values = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        self.colNameSelect= values[0]
        
        if len( self.colNameSelect ) == 0:
            self.logPanel.write("you don't select any items")
            return
        
        if len( self.colNameSelect ) < self.minRequiredCols:
            self.logPanel.write("you have to select at least %i column(s)"%self.requiredcols)
            return
        
        columns=  [numpy.ravel(self._convertColName2Values( [colName] )) for colName in self.colNameSelect]
        self.tests= values[1]
        self.hypotesis= values[2]
        userMean=  values[3]
        return (columns, self.tests, self.hypotesis, userMean)
    
    def _calc( self, columns, *args, **params):
        return self.evaluate( columns, *args, **params)
    
    def evaluate( self, *args, **params):
        # computations here
        columns=   args[0]
        tests=     args[1]
        hypotesis= args[2] #0== One Tailed, 1== two tailed
        umean=     args[3]
        if umean == None or len(columns) == 0 or len(tests) == 0:
            raise StandardError('The input parameters are incorrect')
        
        TBase= [OneSampleTests(col, tests, umean)  for col in columns]
        return TBase

    def showGui( self):
        values= self._showGui_GetValues()
        if values== None:
            return None
        
        result= self._calc( values[0], *values[1:])
        self._report( result)
        
    def _report( self, result):
        if len(result) == 0:
            return
        
        # se hace el reporte por variables
        coldescription= [u'test - variable']
        for nameTest in self.tests:
            coldescription.append( nameTest)
            if nameTest == u't-test':
                coldescription.extend( ['t', 'prob (approx)'])
                
            elif nameTest == u'Sign Test':
                coldescription.extend( ['z', 'prob'])
                
            elif nameTest == u'Chi square test for variance':
                coldescription.extend( ['df', 'chisquare', 'prob'])
                
        self.outputGrid.addColData( coldescription, self.name)
        
        for name, testResults in zip( self.colNameSelect, result):
            col2report= [name]
            for nameTest in self.tests:
                result= testResults.pop( 0)
                if nameTest == u't-test':
                    prob= result[1]
                    if prob == -1.0:
                        col2report.extend( ['All elements are the same', 'test not possible', ''])
                    else:
                        if self.hypotesis == 0:
                            prob= result[1]/2.0
                        col2report.append( '')
                        col2report.append( result[0]) 
                        col2report.append( prob)
                        
                elif nameTest == u'Sign Test':
                    prob= result[1]
                    if prob == -1.0:
                        col2report.extend([ 'All data are the same','no analysis is possible',''])
                    else:
                        if self.hypotesis == 0:
                            prob= prob/2.0
                        col2report.append( '')
                        col2report.append( result[0])
                        col2report.append( prob)
                        
                elif nameTest == u'Chi square test for variance':
                    prob= result[2]
                    if prob == None:
                        prob= 1.0
                        
                    if self.hypotesis == 0:
                        continue
                        # prob= prob / 2.0 # chisquare
                    
                    col2report.extend( ['',result[0], result[1], prob])
                    
            self.outputGrid.addColData( col2report)
            