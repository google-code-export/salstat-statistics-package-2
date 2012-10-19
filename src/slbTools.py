'''
Created on 17/05/2012

@author: sebastian lopez buritica
license: GPL3
'''
from imagenes import imageEmbed
import collections
import tempfile, xlwt
import os
import sys
import wx
import numpy as np
from openStats import statistics

from  warnings import warn
from copy import deepcopy

__WILDCARD= "Supported Files (*.txt;*.csv;*.xls)|*.txt;*.csv;*.xls|"\
            "Excel 2003 File (*.xls)|*.xls|" \
            "Txt file (*.txt)|*.txt|"    \
            "Csv file (*.csv)|*.csv" 

def getPath(wildcard= __WILDCARD):
    dlg = wx.FileDialog(None, "Load Data File", "","",
                        wildcard= wildcard,
                        style = wx.OPEN)
    icon = imageEmbed().logo16()
    dlg.SetIcon(icon)
    
    if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        return None
    
    fileName= dlg.GetFilename()
    fullPath= dlg.Path 
    junk, filterIndex = os.path.splitext(fileName)
    try:
        if filterIndex == '.xls':
            return fullPath
        elif filterIndex in ('.txt', '.csv'):
            return fullPath
    except (Exception, TypeError) as e:
        traceback.print_exc( file = self.log)
            
def siguiente():
    '''genera una serie de datos continuos
    >> sig = siguiente()
    >> sig.next()
    0
    >> sig.netx()
    1'''
    i = 0
    while True:
        yield i
        i+= 1


class ReportaExcel(object):
    def __init__(self,  path = None, cell_overwrite_ok = False):
        if not isinstance(cell_overwrite_ok, (bool,)):
            cell_overwrite_ok= False
        self.cell_overwrite_ok = cell_overwrite_ok
        if path == None:
            self.path = tempfile.mkdtemp(suffix='.xls')
        else:
            self.path = path
        self._suffix = os.path.split(self.path)[1].split('.')[-1]
        self._wbk = xlwt.Workbook()
        self._hojas = list()
        self.pagenum = self.__numPage()

    def __numPage(self):
        i = 0
        while True:
            yield i
            i+= 1
            
    @property
    def suffix(self):
        return self._suffix
    @suffix.setter
    def suffix(self, suf):
        if suf in ('xls', 'xlsx'):
            self._suffix = suf
            
    @property
    def path(self):
        return self._path
    @path.setter
    def path(self,ruta):
        # cambia la ruta en la que se guardara la informacion
        if ruta == None:
            # se toma la ruta actual como la seleccionada para
            #  guardar la informacion
            warn('debe ingresar una ruta')
            return
        ruta = os.path.abspath(ruta)
        (dirPath, fileName) = os.path.split(ruta)
        if not os.access(dirPath, os.R_OK):
            raise StandardError("SaveClass: doesn't have permissions on the selected dir")
        if fileName =='':
            raise StandardError("Debe ingresar un nombre de arhivo")
        self._path = ruta
        self._file = fileName
        if os.path.isfile(self.path):
            print('Warning: the selected file already exists, the object could fail')
        self._path = ruta

    @property
    def file(self):
        return self._file
    @file.setter
    def file(self, nameFile):
        if nameFile == u'':
            raise StandardError('debe ingresar un nombre de archivo')

        self._file = nameFile
        self.path =  os.path.join(os.path.split(self.path)[0], nameFile)

        if os.path.isfile(fullpath):
            print('Warning: the selected file already exists, the object could fail')

    def __addSheet(self):
        # adiciona una hoja para el reporte
        col = self.pagenum.next()
        texto = u'Hoja'+ str(col)
        hoja = self._wbk.add_sheet(texto, cell_overwrite_ok = self.cell_overwrite_ok)
        self._hojas.append( (hoja, self.__numPage(), self.__numPage()) )
        # objeto hoja, iterador sobre columnas, iterador sobre filas

    def write(self,lista,sheet = None, cell_overwrite_ok = False):
        '''reporte al contenido considerando que se ha ingresado una columna'''
        # se verifica si existen hojas para el reporte
        if len(self._hojas) < 1:
            # se crea una hoja
            self.__addSheet()
        if sheet == None:
            # se considera que la hoja utilizada sera la primera(hoja numero cero)
            sheet = 0
        else:
            if sheet < 0:
                raise StandardError('las hojas solo pueden ser valores enteros')
            else:
                if int(sheet) > len(self._hojas):
                    # se crean tantas hojas como la posicion solicitada
                    for hoja in range(len(self._hojas),int(sheet)+1):
                        self.__addSheet()
        # para la hoja seleccionada se determina la ultima columna escrita
        sheetObj=  self._hojas[sheet][0]
        sheetCol=  self._hojas[sheet][1].next()
        # se reporta el contenido de la lista en la columna
        style0 = xlwt.easyxf(num_format_str='#,##0.00')
        lista= self._filterlist(lista)
        for posicion,contenido in enumerate(lista):
            if isinstance(contenido,(int,float)):
                sheetObj.write(posicion, sheetCol, contenido, style0)
            else:
                sheetObj.write(posicion, sheetCol, contenido)
                
    def _filterlist(self, lista):
        if len(lista) == 0:
            return lista
        # quita los campos vacios al final
        if isinstance(lista, (tuple)):
            lista = list(lista)
        lista2 = deepcopy(lista)
        
        lista2.reverse()
        for pos,val in enumerate(lista2):
            if val != u'':
                break
        pos = len(lista) - pos
        lista = lista[0:pos]
        # se cambia las posiciones vacias por None
        for pos,val in enumerate(lista):
            if val == u'':
                lista[pos] = None
            else:
                # se intenta convertir a numero el campo
                try:
                    lista[pos] = float(val)
                except:
                    pass
        return lista
        
    def writeByRow(self,lista,sheet= None):
        '''escribe los resultados por filas'''
        # se verifica si existen hojas para el reporte
        if len(self._hojas) < 1:
            # se crea una hoja
            self.__addSheet()
        if sheet == None:
            # se considera que la hoja utilizada sera la primera(hoja numero cero)
            sheet = 0
        else:
            if sheet < 0:
                raise StandardError('las hojas solo pueden se valores enteros')
            else:
                if int(sheet)+1 > len(self._hojas):
                    # se crean tantas hojas como la posicion solicitada
                    for hoja in range(len(self._hojas),int(sheet)+1):
                        self.__addSheet()
        # para la hoja seleccionada se determina la ultima fila escrita

        sheetObj=  self._hojas[sheet][0]
        sheetRow=  self._hojas[sheet][2].next()
        # se reporta el contenido de la lista en la columna
        style0 = xlwt.easyxf(num_format_str='#,##0.00')
        lista = self._filterlist(lista)
        for posicion,contenido in enumerate(lista):
            if isinstance(contenido,(int,float)):
                sheetObj.write(sheetRow, posicion, contenido,style0)
            else:
                sheetObj.write(sheetRow, posicion, contenido)

    def writeByCols(self,lista,sheet = None):
        for col in lista:
            self.write(col,sheet)

    def save(self):
        # se determina si no se han adicionado hojas nuevas
        if len(self._hojas) == 0:
            # se adiciona una hoja y se guarda
            self.__addSheet()
        return self._wbk.save(self.path)
    def _loadData(self,ntbookObj):
        # se cargan los datos
        for sheet in self._wbk.sheets():
            data={'name':sheet.name(),
                  'size': (),
                  }
        #       size: data size (#rows, #ncols)
        #       data: matrix data
        #       nameCol: objeto iterable con el nombre de las columnas
        #              Si no se escribe aparece por defecto a, b,.. la
        #              nomenclatura comun
            pass

    def view(self):
        '''Muestra el contenido de los datos almancenados mediante una interfase
        de wxpython
        '''
        # utiliza con interface grafica de usuario a notebookSheet
        app = wx.App()
        wx.Frame.__init__(self, parent=-1, id= wx.ID_ANY, title= None, size=(480, 520))
        ##customPanel = NtbBook2(self)
        customPanel  = 1
        self._loadData(customPanel)
        self.Show(True)
        app.MainLoop()
def quicksort(datos,primero,ultimo,returnOrderer= False):
    # se cambia el numero de recursiones posible a 10.000
    recursionActual = sys.getrecursionlimit()
    try:
        sys.setrecursionlimit(10000)
        if not returnOrderer:
            result= quicksortfilter(datos,primero, ultimo)
        else:
            pass
        sys.setrecursionlimit(recursionActual)
        return result
    except:
        sys.setrecursionlimit(recursionActual)

def quicksortfilter(datos, primero, ultimo):
    i = primero
    j = ultimo
    try:
        pivote = (datos[primero] + datos[ultimo]) / 2
    except:
        pivote = datos[len(datos)/2]
    while i < j:
        while datos[i] < pivote:
            i+=1
        while datos[j] > pivote:
            j-=1
        if i <= j:
            aux = datos[i]
            datos[i] = datos[j]
            datos[j] = aux
            i+=1
            j-=1
    if primero < j:
        datos = quicksort(datos, primero, j)
    if ultimo > i:
        datos = quicksort(datos, i, ultimo)
    return datos

def qsort(list):
    try:
        x=list.pop()
    except:
        return []
    return qsort(filter((lambda y: y<x), list)) + [x] + qsort(filter((lambda y: y>=x), list))

def distinct(data):
    # entrega un tipo de datos diferente
    # se ordena los numeros de menor a mayor
    if len(data) == 0:
        return data
    data = quicksort(data, 0,len(data)-1)
    unicos = list()
    unicos.append(data.pop(0))
    while len(data) > 0:
        valor = data.pop(0)
        if valor != unicos[-1]:
            unicos.append(valor)
    return unicos

def homogenize(*args, **params):
    '''given a serie of vectors it check the values and 
    groups it depens on its value. 
    arg1: iterable with numerical data'''
    returnPos= False
    try:
        returnPos= params['returnPos']
    except KeyError:
        pass
    
    maxlen= min( [len(arg) for arg in args])
    nelements= len( args)
    passPos= list()
    for pos in range( maxlen):
        dat= [args[i][pos] for i in range(nelements)]
        if _allnumeric(dat):
            passPos.append(pos)
    if sum( [isinstance( arg,(np.ndarray,)) for arg in args]) == len(args):
        return [np.array([arg[pos] for pos in passPos]) for arg in args]
    if not returnPos:
        return [[arg[pos] for pos in passPos] for arg in args]
    else:
        return ([[arg[pos] for pos in passPos] for arg in args], passPos)

def homogenizeNonNumerical(*args):
    '''given a serie of vectors it check the values and 
    groups it depens on its value. 
    arg1: iterable with numerical data'''
    maxlen= min( [len(arg) for arg in args])
    nelements= len( args)
    passPos= list()
    for pos in range( maxlen):
        dat= [args[i][pos] for i in range(nelements)]
        if not(None in dat or '' in dat):
            passPos.append(pos)
    if sum( [isinstance( arg,(np.ndarray,)) for arg in args]) == len(args):
        return [np.array([arg[pos] for pos in passPos]) for arg in args]
    return [[arg[pos] for pos in passPos] for arg in args]
        
def _allnumeric(data):
    return all([isnumeric(dat) for dat in data])

def isnumeric(data):
    if isinstance(data, (int, float, long, np.ndarray)):
        return True
    return False
def isiterable(data):
    '''check if the data is iterable'''
    if isinstance(data, collections.Iterable):
        return True
    return False
########
def __dict2list(diccionario):
    '''convierte un diccionario como una lista de datos'''
    try:
        for key in diccionario.keys():
            for key2 in __dict2list(diccionario[key]):
                yield (key,) + key2
    except:
        yield (diccionario, )

def dict2list( diccionario, maximo = None):
    '''Dado un diccionario y un valor maximo de
    nivel retorna un generador con filas de la
    informacion.
    '''
    if maximo== None:
        return __dict2list(diccionario)
    return _newdict(diccionario,actual= 1,maximo = 3)

def _newdict(diccionario,actual,maximo):
    try:
        if actual > maximo:
            raise
        for key in diccionario.keys():
            for key2 in _newdict(diccionario[key],actual+1,maximo):
                yield (key,) + key2 # (key,) + key2
    except:
        yield (diccionario, )


class GroupData(object):
    '''Grouping data similar to a pivot table
    xdata= [[col1], [col2], ..., [colU]]
    ydata= [[yda1], [ydat2], ..., [[ydataN]]]
    yalias= [ydata1name, ydata2name,..., ydataNname] # alias name for the ydata, it's optional
    restictions = [' ydata1name > ydata2name ','ydataNname == 0']
    res= GroupData()
    res.xdata= xdata
    res.ydata= ydata
    res.names= names # optional
    dictionary= res.calc()
    listOfData= res.getAsList()
    '''
    def __init__( self, xdata= [], ydata= [], yalias= [], restrictions= [], yvalues= [], yvaluesAlias= []):
        # se verifica que la cantidad de datos
        # ingresados sean los mismos
        self.xdata= xdata
        self.ydata= ydata
        self._homogenized= False
        self.filterPos= []
        self.yvalues = yvalues
        self.yvaluesAlias = yvaluesAlias
        self.restrictions= restrictions
        
    def _cols2dict(self, *cols):
        result= self._filterPos()
        '''convierte una serie de columnas en diccionario'''
        # se determinan que todas las filas tengan igual cantidad de elementos
        data = [len( col) for col in cols]
        if False in map( lambda x,y:  x == y, data[1:] ,data[:-1]):
            raise StandardError( 'Los argumentos deben tener igual cantidad de elementos')
        
        # se identifica las posiciones que cumplen con las restricciones
        if len(self.restrictions) != 0:
            # Aplaying the restrictions to the data
            cols= [np.array(col) for col in cols]
            cols= [col[result] for col in cols]
            data= len( cols[0])
        else:
            data= data[0]
            
        length= data
        result= ()
        for pos in range( length):
            res1= [col[pos] for col in cols]
            result += (res1,)
        
        # se hace los calculos
        return list( self._fil2dict( list( result)))[0]
    
    def __homogenizeData(self):
        # se homogeniza la informacion
        if self._homogenized == True:
            return
        
        alldata= list()
        for xdat in self.xdata:
            alldata.append(xdat)
            
        for ydat in self.ydata:
            alldata.append(ydat)
        
        # homogenize numerical and non numerical data
        cols= homogenizeNonNumerical( *alldata)
        self._xdata= [cols.pop(0) for i in range(len(self.xdata))]
        self._ydata= cols
        self._homogenized == True
    
    def _fil2dict(self, data):
        '''convierte una serie de filas en diccionario'''
        dictionary = dict()
        for dato in data:
            try:
                key= dato[0]
                if not isinstance(key, (str, unicode)):
                    key= key.__str__()
            except IndexError:
                break
            try:
                dictionary[key] += (dato[1:],)
            except KeyError:
                dictionary[key] = (dato[1:],)
            except IndexError:
                break
            
        for key in dictionary.keys():
            for key2 in self._fil2dict(dictionary[key]):
                dictionary[key] = key2
                
        yield dictionary
    
    def _filterPos(self):
        '''applying the general initital filter to the data by the given conditions'''
        # se identifica las posiciones que cumplen con las restricciones
        if len(self.restrictions) == 0:
            return
        
        # joining the restrictions
        restrictiones= ['('+rest+')' for rest in self.restrictions]
        if len( self.restrictions) == 1:
            restrictiones= restrictiones[0]
        else:
            u= lambda x,y: x+' & '+y
            restrictiones= reduce( u, restrictiones[1:], restrictiones[0])
        
        self.filterPos= []
        xcols= [np.array(x) for x in self.xdata]
        ycols= [np.array(x) for x in self.ydata]
        localsDict= dict( )
        
        for key, value in zip( self.xdataNames, xcols):
            localsDict[key]= value
        
        for key, value in zip( self.ydataNames, ycols):
            localsDict[key]= value
        
        self.filterPos= eval(restrictiones, {}, localsDict)
        
        return self.filterPos
    
    def __test__( self, *data):
        dimensiones = [len(datai) for datai in data]
        if sum([1 for dimen in dimensiones if dimen == dimensiones[0]]) != len(dimensiones):
            raise StandardError('all the data must have the same len')
        
    def __testAll( self):
        self.__test__( self._xdata)
        self.__test__( self._ydata)
        self.__test__( (self._xdata[0], self._ydata[0]))

    def __setdictValue( self, diccionario, keys, nombreCampo, value):
        if not isinstance(keys,(list,tuple)):
            return
        
        if len(keys) >= 1:
            key0= keys[0]
            if not isinstance( keys[0], (str,unicode)):
                key0= keys[0].__str__()
                
        if len(keys) == 1:
            if not diccionario.has_key(key0):
                diccionario[key0]= dict()
            try:
                (nombreCampo[-1],value[-1])
                for nombrei,valuei in zip(nombreCampo,value):
                    try:
                        diccionario[key0][nombrei].append(valuei)
                    except KeyError:
                        diccionario[key0][nombrei] = list()
                        diccionario[key0][nombrei].append(valuei)
            except:
                try:
                    diccionario[key0][nombreCampo].append(value)
                except KeyError:
                    diccionario[key0][nombreCampo] = list()
                    diccionario[key0][nombreCampo].append(value)
        else:
            try:
                self.__setdictValue(diccionario[key0],keys[1:],nombreCampo,value)
            except KeyError:
                diccionario[key0]= dict()
                self.__setdictValue(diccionario[key0],keys[1:],nombreCampo,value)
                
    
    def getAsDict( self):
        self.__testAll()
        self.__homogenizeData()
        if len( self.xdata[0]) == 0 or len( self.ydata[0]) == 0:
            return dict()
        
        diccionario= self._cols2dict( *self.xdata)
        if len(self.filterPos) > 0:
            for rowNumber in range( len( self.xdata[0])): # self.ydata[0]
                if not self.filterPos[rowNumber]: 
                    continue
                
                rowData= [ydata[rowNumber] for ydata in self.ydata]
                # changing empty string u'' to None
                for pos,data in enumerate( rowData):
                    if data == u'':
                        rowData[pos] = None
                        
                self.__setdictValue( diccionario,
                        keys= [valor[rowNumber] for valor in self.xdata],
                        nombreCampo= self.yalias,
                        value= rowData)
                
        else:
            for rowNumber in range( len( self.xdata[0])): # self.ydata[0]
                rowData= [ydata[rowNumber] for ydata in self.ydata]
                # changing empty string u'' to None
                for pos,data in enumerate( rowData):
                    if data == u'':
                        rowData[pos] = None
        
                self.__setdictValue( diccionario,
                        keys= [valor[rowNumber] for valor in self.xdata],
                        nombreCampo= self.yalias,
                        value= rowData)
        
        # applying filters to obtain ydata
        return self._applyYfilters(diccionario)
    
    def _applyYfilters(self, diccionario):
        # defining the dictionary of variables to be used as
        # local variables
        if len(self.yvalues) == 0:
            return diccionario
        
        if len( self.yvaluesAlias) != len( self.yvalues):
            self.yvaluesAlias= self.yvalues[:]
        
        localdict= dict()
        newdict= self.dict2list( diccionario, maximun= len( self.xdata))
        responseDict= dict()
        for dat in newdict:
            xValues= dat[:-1]
            dictValues= dat[-1]
            for key, value in zip( self.xdataNames, xValues):
                dictValues[key]= value
            dictValues['statistics']= statistics
            
            # evaluating the conditions with the local dict
            # for all values
            for colY, alias in zip(self.yvalues, self.yvaluesAlias): # colY correspond
                try:
                    yvalues= eval( colY, {}, dictValues)
                except:
                    yvalues= ''
   
                # send the data to construct a dictionary
                self.__setdictValue( responseDict, keys = xValues,
                                     nombreCampo = alias, value= yvalues)
            
        return responseDict
    
    def dict2list(self, diccionario, maximun = None ):
        if maximun== None:
            return self.__dict2list(diccionario)
        return _newdict(diccionario,actual= 1, maximo = maximun)
    
    def __dict2list(self, diccionario):
        '''convierte un diccionario como una lista de datos'''
        try:
            for key in diccionario.keys():
                for key2 in self.__dict2list(diccionario[key]):
                    yield (key,) + key2
        except:
            yield (diccionario, )
        
    def getAsList(self, maximum= None):
        return [lis for lis in self.getAsGen(maximum)]
    
    def getAsGen(self, maximun= None):
        return self.dict2list(self.getAsDict(), maximun= maximun)
    @property
    def xdata( self):
        return self._xdata
    @xdata.setter
    def xdata( self, data):
        self._xdata = data
        self.xdataNames= list()
        for pos in range( len( self.xdata)):
            xdat= self.xdata[pos].pop( 0)
            if not( isinstance( xdat , (str, unicode))):
                xdat= xdat.__str__()
            self.xdataNames.append( xdat)
    @property       
    def ydata( self):
        return self._ydata
    @ydata.setter
    def ydata( self, data):
        self._ydata = data
        self.ydataNames= list()
        for pos in range( len( self._ydata)):
            ydat= self._ydata[pos].pop( 0)
            if not isinstance(ydat, (str, unicode)):
                ydat= ydat.__str__()
            self.ydataNames.append(ydat)
        self.yalias= self.ydataNames
    @property
    def yalias( self):
        return self.ydataNames
    @yalias.setter
    def yalias( self, yalias):
        if isinstance(yalias, (str, unicode)):
            yalias= [yalias]
        if len( yalias) == len(self.ydata):
            self.ydataNames= yalias
        else:
            raise StandardError('the len of yalias = %i data is different from the ydata =%i'%
                                (len( yalias), len( self.ydata)))
    @property
    def yvalues(self):
        return self._yvalues
    @yvalues.setter
    def yvalues(self, data):
        self._yvalues= data
    @property
    def yvaluesAlias(self):
        return self._yvaluesAlias
    @yvaluesAlias.setter
    def yvaluesAlias(self, data):
        self._yvaluesAlias= data
    @property
    def restrictions(self):
        return self._restrictions
    @restrictions.setter
    def restrictions(self, data):
        if isinstance(data, (str, unicode)):
            self._restrictions= [data]
        else:
            self._restrictions= data
            
def test_GroupData():
    xdata= (('colombia','colombia','colombia'),
        ('pasto','pasto','manizales'),
        ('casas','personas','hospitales'))
    ydata = ((20, 21, 22,),('alta','media','baja'))
    names =('temperatura','prerion')
    resumen = GroupData(xdata, ydata,names)
    data = resumen.calc()
    if sum([data['colombia']['pasto']['casas'].has_key('temperatura'),
            data['colombia']['pasto']['personas'].has_key('temperatura'),
            data['colombia']['manizales']['hospitales'].has_key('temperatura'),
            data['colombia']['pasto']['casas'].has_key('presion'),
            data['colombia']['pasto']['personas'].has_key('presion'),
            data['colombia']['manizales']['hospitales'].has_key('presion')]) == 6:
        return True
    return False