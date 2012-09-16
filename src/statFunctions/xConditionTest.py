'''Some condition test'''

__name__ = u"Condition tests"
__all__ = ['oneConditionTest','twoConditionTest','threeConditionTest']

import numpy
# _genericFunc ist called from the __init__.py file
from statFunctions import _genericFunc
from wx import ID_OK as _OK
from wx import Size
from statlib import stats as _stats
from openStats import OneSampleTests, twoSampleTests
from slbTools import homogenize
from statFunctions.inferential import chisquare, ks_2samp, mannwhitneyu
from statFunctions.inferential import ranksums,ttest_ind,ttest_rel,wilcoxont
from statFunctions.inferential import  kruskalwallish, friedmanchisquare
from statFunctions.anova import oneway
from statFunctions.correlation import linregress
        
class oneConditionTest(_genericFunc):
    name= u"One condition test"
    statName= 'oneConditionTest'
    def __init__( self):
        # getting all required methods
        _genericFunc.__init__(self)
        self.name=     'One condition test'
        self.statName= 'oneConditionTest'
        self.minRequiredCols= 1
        self.aviableTest= ['t-test', 'Sign Test',
                           'Chi square test for variance']
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
        btn4= ['CheckListBox',  [self.aviableTest,]]
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
            self.Logg.write("you don't select any items")
            return
        
        if len( self.colNameSelect ) < self.minRequiredCols:
            self.Logg.write("you have to select at least %i column(s)"%self.requiredcols)
            return
        
        columns=  [numpy.ravel(self._convertColName2Values( [colName] )) for colName in self.colNameSelect]
        self.tests= values[1]
        self.hypotesis= values[2]
        self.userMean=  values[3]
        return (columns, self.tests, self.hypotesis, self.userMean)
    
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

    def showGui( self, *args, **params):
        values= self._showGui_GetValues()
        if values== None:
            return None
        
        result= self._calc( *values)
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
        self.outputGrid.addRowData( ['user mean=' ,  self.userMean ], currRow= 0)
    
class twoConditionTest(oneConditionTest):
    name= u'Two condition test'
    statName= 'twoConditionTest'
    def __init__( self):
        oneConditionTest.__init__(self)
        self.name=     'Two condition test'
        self.statName= 'twoConditionTest'
        self.minRequiredCols= 2
        self.aviableTest= ['chisquare', 'ks_2samp', 'linear regression',
                           'Mann Whitneyu', 'ttest related', 'ttest independent',
                           'Rank Sums', 'Wilcoxon t-test <signed ranks>']
        self.colNameSelect= []
        self.tests= []
        self.hypotesis= None
    
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,
                  '_size':  Size(280,430)}
        self._updateColsInfo() # update self.columnames and self.colnums
        btn1= ['StaticText',   ['Select the columns to analyse']]
        btn2= ['CheckListBox', [self.columnNames]]
        btn3= ['StaticText',   ['Choose test(s)']]
        btn4= ['CheckListBox',  [self.aviableTest,]]
        #btn5= ['RadioBox',     ['Select hypothesis',   ['One tailed','Two tailed'],]]
        #btn6= ['StaticText',   ['User hypothesised mean']]
        #btn7= ['NumTextCtrl',  []]
        structure= list()
        structure.append( [btn1,])
        structure.append( [btn2,])
        structure.append( [btn3,])
        structure.append( [btn4,])
        #structure.append( [btn5,])
        #structure.append( [btn7, btn6])
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
            self.Logg.write("you don't select any items")
            return
        
        if len( self.colNameSelect ) != 2:
            self.Logg.write("you have to select only two column(s)")
            return
        
        columns=  [numpy.ravel(self._convertColName2Values( [colName] )) for colName in self.colNameSelect]
        # se homogeniza las columnas
        columns= homogenize(*columns)
        self.tests=     values[1]
        #self.hypotesis= values[2]
        #self.userMean=  values[3]
        return ( columns, self.tests) #, self.hypotesis, self.userMean)

    def evaluate( self, *args, **params):
        # computations here
        columns=   args[0]
        tests=     args[1]
        # hypotesis= args[2] #0 == One Tailed, 1 == two tailed
        # umean=     args[3]
        if len(columns) == 0 or len(tests) == 0:
            raise StandardError( 'The input parameters are incorrect')

        # combining data
        result= list()
        for test in tests:
            if   test == 'chisquare':
                fcn= chisquare()
            
            elif test == 'ks_2samp':
                fcn= ks_2samp()
            
            elif test == 'linear regression':
                fcn= linregress()
            
            elif test == 'Mann Whitneyu':
                fcn= mannwhitneyu()
            
            elif test == 'ttest related':
                fcn= ttest_rel()
            
            elif test == 'ttest independent':
                fcn= ttest_ind()
            
            elif test == 'Rank Sums':
                fcn= ranksums()
            
            elif test == 'Wilcoxon t-test <signed ranks>':
                fcn= wilcoxont()
            else:
                continue
            
            res= [fcn.name]
            try:
                resultado= fcn.evaluate(*columns)
                for  name, res1 in zip(fcn.nameResults, resultado):
                    res.extend([name, res1])
            except:
                res.append('There is a runtime error')
            res.append('')
            result.append(res)           
                
        return result
        
    def _report( self, result):
        
       self.outputGrid.addColData( result[0], self.name)
       if len(result) > 1:
           for res in result[1:]:
               self.outputGrid.addColData( res)
               
       self.outputGrid.addRowData( ['Selected columns'] ,currRow= 0)
       self.outputGrid.addRowData( self.colNameSelect ,currRow= 1)
       self.outputGrid.addRowData( ['Output'] ,currRow= 2)
       self.Logg.write( 'Two sample test succesfull')
            
#---------------------------------------------------------------------------
# dialog for single factor tests with 3+ conditions
class threeConditionTest(oneConditionTest):
    name= u'Three or more condition test'
    statName= 'threeConditionTest'
    def __init__( self):
        oneConditionTest.__init__(self)
        self.name=     'Three or more condition test'
        self.statName= 'threeConditionTest'
        self.minRequiredCols= 3
        self.aviableTest= ['kruskawallish', 'friedmanchisquare']
        self.colNameSelect= []
        self.tests= []
        self.hypotesis= None
    
    def _dialog( self, *arg, **params):
        setting= {'Title': self.name,
                  '_size':  Size(280,430)}
        self._updateColsInfo() # update self.columnames and self.colnums
        btn1= ['StaticText',   ['Select the columns to analyse']]
        btn2= ['CheckListBox', [self.columnNames]]
        btn3= ['StaticText',   ['Choose test(s)']]
        btn4= ['CheckListBox',  [self.aviableTest,]]
        structure= list()
        structure.append( [btn1,])
        structure.append( [btn2,])
        structure.append( [btn3,])
        structure.append( [btn4,])
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
            self.Logg.write("you don't select any items")
            return
        
        if len( self.colNameSelect ) < self.minRequiredCols:
            self.Logg.write("you have to select at least %i column(s)"%self.minRequiredCols)
            return
        
        columns=  [numpy.ravel(self._convertColName2Values( [colName] )) for colName in self.colNameSelect]
        # se homogeniza las columnas
        columns= homogenize(*columns)
        self.tests=     values[1]
        return ( columns, self.tests)

    def evaluate( self, *args, **params):
        # computations here
        columns=   args[0]
        tests=     args[1]
        if len(columns) == 0 or len(tests) == 0:
            raise StandardError( 'The input parameters are incorrect')

        # combining data
        result= list()
        for test in tests:
            if   test == 'kruskawallish':
                fcn= kruskalwallish()
            
            elif test == 'friedmanchisquare':
                fcn= friedmanchisquare()
            
            else:
                continue
            
            res= [fcn.name]
            try:
                resultado= fcn.evaluate(*columns)
                for  name, res1 in zip(fcn.nameResults, resultado):
                    res.extend([name, res1])
            except:
                res.append('There is a runtime error')
            res.append('')
            result.append(res)           
                
        return result
        
    def _report( self, result):
        
       self.outputGrid.addColData( result[0], self.name)
       if len(result) > 1:
           for res in result[1:]:
               self.outputGrid.addColData( res)
               
       self.outputGrid.addRowData( ['Selected columns'] ,currRow= 0)
       self.outputGrid.addRowData( self.colNameSelect ,currRow= 1)
       self.outputGrid.addRowData( ['Output'] ,currRow= 2)
       self.Logg.write( 'Two sample test succesfull')