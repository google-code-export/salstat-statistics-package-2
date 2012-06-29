'''a module thath will be used as a container of different functions'''
version = "0.0.1"

from easyDialog import Dialog as _dialog
import wx
import numpy

class _genericFunc(object):
    def __init__(self):
        self.app=       wx.GetApp()
        self.inputGrid= self.app.inputGrid # to read the input data from the main grid
        self.dialog=    _dialog         # to create de dialod
        self.Logg=      self.app.Logg   # to report
        self.outpuGrid= self.app.output # the usern can use the plot functions
        self.plot=      self.app.plot   # acces to the plot system
        
    def _updateColsInfo(self):
        gridCol=            self.inputGrid.GetUsedCols()
        self.columnNames=   gridCol[0]
        self.columnNumbers= gridCol[1]
        
    def _convertColName2Values(self, colNamesSelected, *args, **params):
        '''geting the selected columns of the InputGrid'''
        values = [ [pos for pos, value in enumerate( self.columnNames )
                    if value == val
                    ][0]
                   for val in colNamesSelected
                   ]
        # -------------------
        columns  = list()
        for pos in values:
            col= numpy.array(self.inputGrid.CleanData(self.columnNumbers[ pos ]))
            col.shape = (len(col),1)
            columns.append(col)
            
        return columns

def _statsType1( function, grid, useNumpy = True,
                requiredcols= None, allColsOneCalc = False,
                nameResults= None, dataSquare= False):
    functionName= function.__name__
    setting = self.defaultDialogSettings
    setting['Title'] = functionName
    ColumnList, colnums  = grid.GetUsedCols()
    bt1= ['StaticText', ('Select the columns to analyse',) ]
    bt2= ['CheckListBox', (ColumnList,)]
    structure = list()
    structure.append([bt1,])
    structure.append([bt2,])
    dlg = dialog(settings = setting, struct= structure)
    if dlg.ShowModal() == wx.ID_OK:
        values = dlg.GetValue()
        dlg.Destroy()
    else:
        dlg.Destroy()
        return
    # -------------------
    # changing value strings to numbers
    colNameSelect = values[0]
    if len( colNameSelect ) == 0:
        self.logPanel.write("you don't select any items")
        return

    if len(colNameSelect) < requiredcols:
        self.logPanel.write("you have to select at least %i columns"%requiredcols)
        return

    values = [ [pos for pos, value in enumerate( ColumnList )
                if value == val
                ][0]
               for val in colNameSelect
               ]
    # -------------------
    if useNumpy:
        colums  = list()
        for pos in values:
            col = numpy.array(GetData(colnums[ pos ]))
            col.shape = (len(col),1)
            colums.append(col)
    else:
        colums = [ GetData(colnums[ pos ]) for pos in values]

    if dataSquare:
        # identifica que las columnas seleccionadas deben tener igual
        #  cantidad de elementos
        lendata= [len(col) for col in colums]
        if sum([1 for leni in lendata if leni == lendata[0]]) <> len(colums):
            return "the data must have the same size"

    if allColsOneCalc:
        result = function( *colums )
    else:
        # se hace los calculos para cada columna
        result = [function( col ) for col in colums]

    # se muestra los resultados
    if nameResults == None:
        wx.GetApp().output.addColData(colNameSelect, functionName)
    else:
        wx.GetApp().output.addColData(nameResults, functionName)
    if functionName in ['kurtosis','kurtosistest','skewtest',
                        'normaltest','mode']:
        opt = False
        try:
            len(result[0])
        except:
            opt = True

        if opt:
            wx.GetApp().output.addColData(result)
        else:
            for i in range(len(result[0])):
                res1= [res[i] for res in result]
                wx.GetApp().output.addColData(res1)

    else:
        wx.GetApp().output.addColData(result)

    self.logPanel.write(functionName + ' successfull')

def _statsType2( functionName, texto = 'moment',spinData= (1,100,1),
                factor = 1, useNumpy = True):
    ''''select plus spin crtl'''
    group = lambda x,y: (x,y)
    setting = self.defaultDialogSettings
    setting['Title'] = functionName
    ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()
    bt1= group('StaticText', ('Columns to analyse',) )
    bt2= group('CheckListBox', (ColumnList,))
    bt3= group('SpinCtrl', spinData)
    bt4= group('StaticText', (texto,) )
    structure = list()
    structure.append([bt2, bt1])
    structure.append([bt3, bt4])
    dlg = dialog(settings = setting, struct= structure)
    if dlg.ShowModal() == wx.ID_OK:
        values = dlg.GetValue()
        dlg.Destroy()
    else:
        dlg.Destroy()
        return
    # -------------------
    # changing value strings to numbers
    (colNameSelect, moment) = values
    moment = moment * factor
    if len( colNameSelect ) == 0:
        self.logPanel.write("you don't select any items")
        return
    if not isinstance(colNameSelect, (list, tuple)):
        colNameSelect = [colNameSelect]
        moment = [moment]

    values = [ [pos for pos, value in enumerate( ColumnList )
                if value == val
                ][0]
               for val in colNameSelect
               ]
    # -------------------
    if useNumpy:
        colums  = list()
        for pos in values:
            col = numpy.array(GetData(colnums[ pos ]))
            col.shape = (len(col),1)
            colums.append(col)
    else:
        colums = [ GetData(colnums[ pos ]) for pos in values]
    # se hace los calculos para cada columna
    result = [getattr(stats, functionName)( col, moment ) for col in colums]
    # se muestra los resultados
    wx.GetApp().output.addColData(colNameSelect, functionName)
    wx.GetApp().output.addColData(numpy.ravel(result))
    self.logPanel.write(functionName + ' successfull')

def _statsType3(functionName, texto1 = u'',
                texto2 = u'', **params):
    try:
        useNumpy= params.pop('useNumpy')
    except:
        useNumpy= False

    try:
        nameCols= params.pop('nameCols')
    except:
        nameCols= None

    group = lambda x,y: (x,y)
    setting = self.defaultDialogSettings
    setting['Title'] = functionName
    ColumnList, colnums  = wx.GetApp().frame.grid.GetUsedCols()

    bt1= group('StaticText',   (texto1,) )
    bt2= group('Choice',       (ColumnList,))
    bt3= group('StaticText',   (texto2,) )

    structure = list()
    structure.append([bt2, bt1])
    structure.append([bt2, bt3])
    dlg = dialog(settings = setting, struct= structure)
    if dlg.ShowModal() == wx.ID_OK:
        values = dlg.GetValue()
        dlg.Destroy()
    else:
        dlg.Destroy()
        return
    # -------------------
    # changing value strings to numbers
    (xcolname, ycolname) = values
    if len( xcolname ) == 0 or len( ycolname ) == 0:
        self.logPanel.write("you don't select any items")
        return
    if not isinstance(xcolname, (list, tuple)):
        xcolname = [xcolname]
        ycolname = [ycolname]
    xvalue= [ [pos for pos, value in enumerate( ColumnList )
               if value == val
               ][0]
              for val in xcolname
              ][0]
    yvalue= [ [pos for pos, value in enumerate( ColumnList )
               if value == val
               ][0]
              for val in ycolname
              ][0]
    # -------------------
    if useNumpy:
        xcolumn = numpy.array(GetData(colnums[ xvalue ]))
        ycolumn = numpy.array(GetData(colnums[ yvalue ]))
        xcolumn.shape= (len(xcolumn), 1)
        ycolumn.shape= (len(ycolumn), 1)
    else:
        xcolumn = GetData(colnums[ xvalue ])
        ycolumn = GetData(colnums[ yvalue ])

    # se hace los calculos
    result = getattr(stats, functionName)( xcolumn, ycolumn, **params)
    # se muestra los resultados
    if nameCols != None:
        wx.GetApp().output.addColData(nameCols, functionName)
        wx.GetApp().output.addColData(result)
    else:
        wx.GetApp().output.addColData(result, functionName)
    self.logPanel.write(functionName + ' successfull')

