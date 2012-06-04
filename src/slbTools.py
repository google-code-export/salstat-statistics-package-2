'''
Created on 17/05/2012

@author: sebastian lopez buritica
license: GPL3
'''
import tempfile, xlwt , os
try:
    import xlrd
except:
    pass
from  warnings import warn
from copy import deepcopy

class GroupData:
    # ingreso
    def __init__(self,xdata,ydata,names):
        # se verifica que la cantidad de datos
        # ingresados sea los mismos
        self._xdata = xdata
        self._ydata = ydata
        self._names = names
        self.__testAll()

    def __test__(self,*data):
        dimensiones = [len(datai) for datai in data]
        if sum([1 for dimen in dimensiones if dimen == dimensiones[0]]) != len(dimensiones):
            raise StandardError('all the data must have the same len')
    def __testAll(self):
        self.__test__(self._xdata)
        self.__test__(self._ydata)
        self.__test__((self._xdata[0],self._ydata[0]))

    def __setdictValue(self,diccionario,keys,nombreCampo,value):
        if not isinstance(keys,(list,tuple)):
            return
        if len(keys) == 1:
            try:
                (nombreCampo[-1],value[-1])
                for nombrei,valuei in zip(nombreCampo,value):
                    try:
                        diccionario[keys[0]][nombrei].append(valuei)
                    except KeyError:
                        diccionario[keys[0]][nombrei] = list()
                        diccionario[keys[0]][nombrei].append(valuei)
            except:
                try:
                    diccionario[keys[0]][nombreCampo].append(valuei)
                except KeyError:
                    diccionario[keys[0]][nombreCampo] = list()
                    diccionario[keys[0]][nombreCampo].append(valuei)
        else:
            self.__setdictValue(diccionario[keys[0]],keys[1:],nombreCampo,value)

    def calc(self):
        self.__testAll()
        diccionario = cols2dict(*self.xdata)
        for rowNumber in range(len(self.ydata[0])):
            rowData = [ydata[rowNumber] for ydata in self.ydata]
            # se convierte los caracteres u'' en None
            for pos,data in enumerate(rowData):
                if data == u'':
                    rowData[pos] = None
            self.__setdictValue(diccionario, keys= [valor[rowNumber] for valor in self.xdata],\
                               nombreCampo= self.names, value= rowData)
        return diccionario
    def _getxdata(self):
        return self._xdata
    def _setxdata(self,xdata):
        self.__test__(xdata)
        self._xdata = xdata
    def _getydata(self):
        return self._ydata
    def _setydata(self,ydata):
        self.__test__(ydata)
        self._ydata = ydata
    def _getnames(self):
        return self._names
    def _setnames(self,names):
        self._names = names
    xdata = property(_getxdata,_setxdata)
    ydata = property(_getydata,_setydata)
    names = property(_getnames,_setnames)
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
###################
###################

class GroupExcel(GroupData):
    # se utiliza para agrupar columnas de excel
    def __init__(self,
                 fullPath,
                 sheetName,
                 fileInit,
                 colNumbers,
                 colValues,
                 colNames ):
        self._wb = None
        self._sheets = None
        self._extension = None
        self._sheetDimensions = None
        self._sheetName = None
        self.setFullPath(fullPath)
        self.setSheetName(sheetName)
        self.setFileInit(fileInit)
        self.setColNumbers(colNumbers)
        self.setColValues(colValues)
        self._colNames = colNames


    def setFullPath(self,fullpath):
        if testFullPath(fullpath)[0]:
            self._fullPath = fullpath
        else:
            raise IOError('''The path doesn't exist''')

    def __getExtension(self,fullpath):
        # se verifica que la ruta sea valida
        resultado = testFullPath(fullpath)
        if not resultado[0]:
            raise IOError('''The path doesn't exist''')
        return resultado[2].split('.')[-1]

    def __testExtension(self,extension):
        # determina si la extension correponde
        # a un archivo de excel soportado
        if not isinstance(extension,(str,unicode)):
            raise TypeError('extension must be a string bu you introduce a\n' + str(type(extension)))
        extension= extension.upper()
        if not(extension == u'XLS' or extension == u'XLSX'):
            raise StandardError('The extension acepted are xls and xlsx only\n')
        return True

    def __setExtension(self,extension):
        try:
            self.__testExtension(extension)
        except:
            raise TypeError('the accepted file extensions are xls o xlsx only')
        self._extension = extension

    def __getSheetNames(self,extension):
        if extension == u'XLS':
            if self._wb == None:
                self._wb = xlrd.open_workbook(self._fullPath)
            if self._sheets == None:
                self._sheets = self._wb.sheets()
            return [sheet.name for sheet in self._sheets]
        elif extension == u'XLSX':
            if self._wb == None:
                self._wb = load_workbook(self._fullPath)
            if self._sheets == None:
                self._sheets = self._wb.get_sheet_names()
            return self._sheets

    def getSheetNames(self):
        # retorna el nombre de las hojas de calculo
        # en una lista, en caso de no existir el libro
        # entrega un mensaje de error indicando que no
        # existe la ruta

        extension = self.__getExtension(self._fullPath).upper()
        # se almacena la extension
        self.__setExtension(extension)
        return self.__getSheetNames(extension)

    def __existSheet(self,sheetName):
        if sheetName in self.getSheetNames():
            return True
        return False

    def setSheetName(self,sheetName):
        # selecciona una hoja con un nombre deteminado
        if self.__existSheet(sheetName):
            self._sheetName = sheetName
    def __getSheetDimensions(self):
        # retorna las dimensiones de la hoja seleccionada
        if self._sheetDimensions != None:
            return self._sheetDimensions
        if self._extension == u'XLS':
            sheet = self._wb.sheet_by_name(self._sheetName)
            self._sheetDimensions = (sheet.nrows,sheet.ncols)
        elif self._extension == u'XLSX':
            sheet = self._wb.get_sheet_by_name(self._sheetName)
            self._sheetDimensions = (len(sheet.rows),len(sheet.columns))
        return self._sheetDimensions

    def setFileInit(self,fileInit):
        # verifica que la fila inicial seleccionada sea consistente
        if fileInit <= self.__getSheetDimensions()[0]:
            self._fileInit = fileInit
        else:
            raise StandardError('the file init must be equal or less than ' +
                                str(self.__getSheetDimensions()[0]))
    def setColNumbers(self,colnumbers):
        # identifica que lo numeros de las columnas sean validas
        if len([1 for col in colnumbers if col <=
             self.__getSheetDimensions()[1]]
            ) < len(colnumbers):
            raise StandardError('The max number of colums must be '+
                                str(self.__getSheetDimensions()[1]))
        else:
            self._colNumbers = colnumbers

    def setColValues(self,colvalues):
        # identifica que lo numeros de las columnas sean validas
        if len([1 for col in colvalues if col <=
             self.__getSheetDimensions()[1]]
            ) < len(colvalues):
            raise StandardError('The max number of colums must be '+
                                str(self.__getSheetDimensions()[1]))
        else:
            self._colValues = colvalues
    def __getxdata(self):
        if self._extension == u'XLS':
            sheet = self._wb.sheet_by_name(self._sheetName)
            return [[cell.value for cell in sheet.col(colx,start_rowx= self._fileInit) ]
                    for colx in self._colNumbers]
        elif self._extension == u'XLSX':
            return [[cell[k].value for cell in self._wb.get_sheet_by_name(self._sheetName).rows ]
                           [self._fileInit:] for k in self._colNumbers]
    def __getydata(self):
        if self._extension == u'XLS':
            sheet = self._wb.sheet_by_name(self._sheetName)
            return [[cell.value for cell in sheet.col(colx,start_rowx= self._fileInit) ]
                    for colx in self._colValues]
        elif self._extension == u'XLSX':
            return [[cell[k].value for cell in self._wb.get_sheet_by_name(self._sheetName).rows ]
                           [self._fileInit:] for k in self._colValues]
    def calcular(self):
        # se lee las columnas de datos
        self._xdata = self.__getxdata()
        self._ydata = self.__getydata()
        self.names = self._colNames
        return self.calc()
    def generator(self, nivel=3):
        '''retorna un generador del diccionario
        con base en el valor maximo del subnivel'''
        return self._dict2list2(self.calcular(),nivel)

    def _dict2list2(self,diccionario,maximo):
        '''Dado un diccionario y un valor maximo de
        nivel retorna un generador con filas de la
        informacion.
        '''
        return self.__newdict(diccionario,actual= 1,maximo = 3)

    def __newdict(self,diccionario,actual,maximo):
        try:
            if actual > maximo:
                raise
            for key in diccionario.keys():
                for key2 in self.__newdict(diccionario[key],actual+1,maximo):
                    yield (key,) + key2
        except:
            yield (diccionario, )
def test_GroupExcel():
    '''verifica la clase Group Excel'''
    # ensayo con archivos en formato xlsx
    try:
        fullPath = 'd://ensayo para borrar.xlsx'
        sheetName = 'Hoja1'
        fileInit = 1
        ensayo = GroupExcel(fullPath,sheetName,fileInit,(1,),(3,),('temperatura','presion',))
        ensayo.calcular()
        resultado = ensayo.generator(nivel= 1)
        for res in resultado:
            print res
    except StandardError,e:
        print e


    try:
        fullPath = 'd://ensayo para borrar.xls'
        sheetName = 'Hoja0'
        fileInit = 0
        ensayo = GroupExcel(fullPath,sheetName,fileInit,(0,1,2,),(5,6,),('presion','temperatura',))
        resultado = ensayo.calcular()
        print resultado
    except StandardError,e:
        print e
    try:
        fullPath = 'd://ensayo.xls' # el archivo no existe
        ensayo = GroupExcel(fullPath,'noname',1,(1,3,4,),(5,6,),('presion','temperatura',))
    except IOError,e:
        print e
    try:
        fullPath = 'd://ensayo para borrar.xls'
        sheetName = 'None' # no existe la hoja
        ensayo = GroupExcel(fullPath,sheetName,1,(1,3,4,),(5,6,),('presion','temperatura',))
    except xlrd.biffh.XLRDError,e:
        print e
    try:
        fullPath = 'd://ensayo para borrar.xls'
        sheetName = 'Hoja0'
        fileInit = 300
        ensayo = GroupExcel(fullPath,sheetName,fileInit,(1,3,4,),(5,6,),('presion','temperatura',))
    except StandardError,e:
        print e
###################
###################

class GroupTxt(GroupData):
    def __init__(self,
                 fullPath,
                 fileInit,
                 separador,
                 colNumbers,
                 colValues,
                 colNames,
                 eol = '\r\n'): # eol: end of line
        self.__rowMax = None
        self.__colNames = colNames
        self.__eol= eol
        self.__separador = separador
        self._setFullPath(fullPath)
        self._setFileInit(fileInit)
        self._setColNumbers(colNumbers)
        self._setColValues(colValues)
    def _setFullPath(self, fullpath):
        if testFullPath(fullpath)[0]:
            self.__fullPath = fullpath
        else:
            raise IOError('''The path doesn't exist''')

    def _getRowMax(self):
        '''retorna el numero de filas del archivo'''
        # abrir el archivo
        if self.__rowMax != None:
            return self.__rowMax
        try:
            archivo = open(self.__fullPath,'rb')
            rows = 0
            try:
                while True:
                    archivo.next() # linea = archivo.next()
                    rows += 1
            except StopIteration:
                pass
            return rows
        except:
            raise
        finally:
            # se cierra el archivo
            archivo.close()

    def _setFileInit(self, fileInit):
        if fileInit <= self._getRowMax():
            self.__fileInit = fileInit
        else:
            raise StandardError('the init file must be less than ' +
                                str(self._getRowMax()))
    def _setColNumbers(self, colNumbers):
        maxColNumbers = self._getMaxColNumbers()
        if len([1 for col in colNumbers if col > maxColNumbers]) > 0:
            raise StandardError('All Column Numbers mus be equal or less than '+
                                str(maxColNumbers))
        self.__colNumbers= colNumbers
    def _setColValues(self, colValues):
        maxColNumbers = self._getMaxColNumbers()
        if len([1 for col in colValues if col > maxColNumbers]) > 0:
            raise StandardError('All Column Numbers mus be equal or less than '+
                                str(maxColNumbers))
        self.__colValues= colValues
    def _getMaxColNumbers(self):
        '''se determina el numero maximo de columnas considerando
        solo la primer fila'''
        try:
            archivo = open(self.__fullPath,'rb')
            if self._getRowMax() < 1:
                raise StandardError('the file numbers must be greather than 0')
            return len(archivo.readline().split(self.__separador))
        except:
            raise
        finally:
            archivo.close()
        pass
    def _getXdata(self):
        try:
            archivo = open(self.__fullPath,'rb')
            lista = [[] for x in self.__colNumbers]
            for posfila,fil in enumerate(archivo):
                if posfila >= self.__fileInit:
                    newlist = fil.split(self.__separador)
                    newlist[-1] = newlist[-1].split(self.__eol)[0]
                    for poscolnumber,posicion in enumerate(self.__colNumbers):
                        lista[poscolnumber].append(newlist[posicion])
            return lista
        except:
            raise
        finally:
            archivo.close()
    def _getYdata(self):
        try:
            archivo = open(self.__fullPath,'rb')
            lista = [[] for x in self.__colValues]
            for posfila,fil in enumerate(archivo):
                if posfila >= self.__fileInit:
                    newlist = fil.split(self.__separador)
                    newlist[-1] = newlist[-1].split(self.__eol)[0]
                    for poscolnumber,posicion in enumerate(self.__colValues):
                        lista[poscolnumber].append(newlist[posicion])
            return lista
        except:
            pass
        finally:
            archivo.close()
    def calcular(self):
        self._xdata = self._getXdata()
        self._ydata = self._getYdata()
        self.names = self.__colNames
        return self.calc()

    def generator(self, nivel=3):
        '''retorna un generador del diccionario
        con base en el valor maximo del subnivel'''
        return self._dict2list2(self.calcular(),nivel)

    def _dict2list2(self,diccionario,maximo):
        '''Dado un diccionario y un valor maximo de
        nivel retorna un generador con filas de la
        informacion.
        '''
        return self.__newdict(diccionario,actual= 1,maximo = 3)

    def __newdict(self,diccionario,actual,maximo):
        try:
            if actual > maximo:
                raise
            for key in diccionario.keys():
                for key2 in self.__newdict(diccionario[key],actual+1,maximo):
                    yield (key,) + key2
        except:
            yield (diccionario, )
def test_GroupTxt():
    fullpath= 'd://nuevo.txt'
    fileinit = 0
    separator = ';'
    colnumbers = (0,)
    colvalues = (1,2,)
    colnames = ('paso','comparativo')
    ensayo = GroupTxt(fullpath,fileinit,separator,colnumbers,colvalues,colnames)
    resultado = ensayo.generator(1)
    for res in resultado:
        print res
###################
###################
def getXlsDate(date,datemode):
    '''toma una fecha de un documento de Excel y los convierte en
    fecha correspondiente
    '''
    return datetime.datetime(*xlrd.xldate_as_tuple(date,datemode))


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

def openFile(parent=None ,filters='Todos los archivos (*.*)|*.*', message='seleccione el archivo para analizar....'):
    app = wx.App()
    # (path, existe): devuelve el nombre del archivo seleccionado y si existe como True o False
    if parent == None :
        # se crea el main app
        pass
    dialog = wx.FileDialog ( parent,\
                        message , \
                        wildcard = filters,  \
                        style = wx.OPEN )
    # Show the dialog and get user input
    if dialog.ShowModal() == wx.ID_OK:
        pathFile= dialog.GetPath()
    elif dialog.ShowModal() == wx.ID_CANCEL:
        return (None,False)
    else:
        # The user did not select anything
        return (None,False)
    # Destroy the dialog
    dialog.Destroy()
    return (pathFile,os.path.exists(pathFile))

class saveLoadVar:
    '''grava y carga una variable a un archivo de disco
    saveLoadVar(nombreVariable, rutaCompleta)
    saveLoadVar.path = # especificar la ruta del reporte
    saveLoadVar.load()  # lee el archivo a una variable'''
    def __init__(self,varName=None,path=None):
        if path == None:
            # la ruta es la ruta actual
            path = os.path.abspath(os.path.curdir)

        self.name= varName
        if self.__testPath__(path):
            self.path = path
        else:
            raise StandardError('Archivo no valido: ' + path)
    def setname(self,name):
        self.name = name

    def getname(self):
        return self.name

    def setpath(self,path):
        if self.__testPath__(path):
            self.path = path
        else:
            raise IOError("The path doesn t exist")

    def getpath(self,path):
        return self.path

    def __testPath__(self,path):
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            return False
        return True

    def save(self,obj):
        '''
        guarda la variable
        '''
        # open the file
        dump(obj,file(os.path.join(self.path,self.name)+'.sv','wb'))

    def load(self):
        '''
        carga la variable
        '''
        return load(file(os.path.join(self.path, self.name)+'.sv','rb'))

    path = property(getpath, setpath)
    name = property(getname, setname)

def identDup(data):
    '''identifica los numeros de los objetos repetidos
    >> identDup([1,2,1])
    >> [[2,0]]
    >> identDup([1,2,1,5,2])
    >>
    '''
    # se enumeran los datos
    res = list()
    control = list()
    for pos,value  in enumerate(data[:-1]):
        if pos in control:
            continue
        res2 = list()
        for pos2,dat in enumerate(data[(pos+1):]):
            if dat == value:
                ppos= pos+pos2+1
                res2.append(ppos)
                control.append(ppos)
        if len(res2)> 0:
            res2 = res2[::-1]
            res2.append(pos)
            res.append(res2[::-1])
    return res

def distinctxls(sheetobj,colNumbers=(1,), colValues=(2,),fileInit=0,colNames=(u'salida1')):
    '''
    '''
    # especie de tabla dinamica
    # sheetobj : objeto sheet de xlr
    if not isinstance(colNumbers,(list,tuple)) or\
       not isinstance(colValues,(list,tuple)) or\
       not isinstance(colNames,(list,tuple)):
        raise TypeError('solo ingrese tuplas o listas')
    # se verifica las dimensiones de la matriz
    maxcol = sheetobj.ncols
    if max(max(colNumbers),max(colValues)) > maxcol:
        raise StandardError(u'Ha excedido el numero maximo de columnas posibles : '+ str(maxcol))
    # se crea el diccionario con las columnas de los numeros
    diccionario = cols2dict(*[[cell.value for cell in sheetobj.col(k)][fileInit:] for k in colNumbers])
    if len(colNames) != len(colValues):
        colNames = range(len(colValues))
    if len(colNames) > 0 and len(colNames) != len(colValues):
        newdict= dict()
        for nombreCampo in colNames:
            newdict[nombreCampo] = list()
    # se almacenan los datos en el diccionario:
    for row in range(fileInit,sheetobj.nrows):
        lista = [cell.value for cell in sheetobj.row(row)]
        for colName,colValue in zip(colNames,colValues):
            if lista[colValue] == u'':
                lista[colValue] = None
            __setdictValue(diccionario, keys=[lista[i] for i in colNumbers],\
                           nombreCampo=colName, value=lista[colValue])
    return diccionario

def __setdictValue(self,diccionario,keys,nombreCampo,value):
        if not isinstance(keys,(list,tuple)):
            return
        if len(keys) == 1:
            try:
                diccionario[keys[0]][nombreCampo].append(value)
            except KeyError:
                diccionario[keys[0]][nombreCampo] = list()
                diccionario[keys[0]][nombreCampo].append(value)
        else:
            __setdictValue(diccionario[keys[0]],keys[1:],nombreCampo,value)

class distinctxlsx:
    '''Para archivos de excel xlsx
    '''
    def __init__(self,
                 fullPath=   None,
                 sheetName=  None,
                 fileInit=   0,
                 colNumbers= (1,),
                 colValues=  (2,),
                 colNames=   (u'salida1')):
        ''' se toman los parametros ingresados
        '''
        self._fullPath =   fullPath
        self.wb =          load_workbook
        self._sheetName =  sheetName
        self._fileInit =   fileInit
        self._colNumbers = colNumbers
        self._colValues =  colValues
        self._colNames =   colNames
        self.sheets =      []
        self.sheetSize =   (None,None)
        self.__setParams()

    def __setParams(self):
        # se ejecuta al iniciar el codigo
        try:
            self._setPath(self._fullPath)
        except:
            pass
        try:
            self._setSheet(self._sheetName)
        except:
            pass
        try:
            self._setFileInit(self._fileInit)
        except:
            pass
        try:
            self._setColNumbers(self._colNumbers)
        except:
            pass
        try:
            self._setColValues(self._colValues)
        except:
            pass
        try:
            self._setColNames(self._colNames)
        except:
            pass

    def calc(self):
        if not self._testAll():
            raise StandardError("One or mores parameters doesn't rigth")

        diccionario = cols2dict(*[[cell[k].value for cell in self.sheetObj.rows ][self.fileInit:] for k in range(self.colNumbers)])
        # se almacenan los datos en el diccionario:
        for row in range(self.fileInit,self.sheetSize[0]):
            lista = [cell.value for cell in self.sheetObj.row(row)]
            for colName,colValue in zip(self.colNames,self.colValues):
                if lista[colValue] == u'':
                    lista[colValue] = None
                self.__setdictValue(diccionario, keys=[lista[i] for i in self.colNumbers],\
                               nombreCampo=colName, value=lista[colValue])
        return diccionario

    def getSheetNames(self):
        pass

    def __setdictValue(self,diccionario,keys,nombreCampo,value):
        if not isinstance(keys,(list,tuple)):
            return
        if len(keys) == 1:
            try:
                diccionario[keys[0]][nombreCampo].append(value)
            except KeyError:
                diccionario[keys[0]][nombreCampo] = list()
                diccionario[keys[0]][nombreCampo].append(value)
        else:
            self.__setdictValue(diccionario[keys[0]],keys[1:],nombreCampo,value)

    def __testPath(self,fullPath):
        return os.path.isfile(fullPath)

    def __testSheetName(self,sheetName):
        if not self.__testPath(self.fullPath):
            return False
        if sheetName in self.sheets:
            return True
        return False

    def __testFileInit(self,fileInit):
        if not self.__testSheetName(self.sheetName):
            return False
        if fileInit > self.sheetSize[0]:
            return False
        return True

    def __testColValues(self,colValues):
        if not isinstance(colValues,(list,tuple)):
            return False #raise TypeError('solo ingrese tuplas o listas')
        if max(colValues) > self.sheetSize[1]:
            #raise StandardError(u'Ha excedido el numero maximo de columnas posibles : '+
            #                    str(self.sheetSize[1]))
            return False
        return True

    def __testColNumbers(self,colNumbers):
        if not isinstance(colNumbers,(list,tuple)):
            return False #raise TypeError('solo ingrese tuplas o listas')
        if max(colNumbers) > self.sheetSize[1]:
            #raise StandardError(u'Ha excedido el numero maximo de columnas posibles : '+
            #                    str(self.sheetSize[1]))
            return False
        return True

    def __testColNames(self,colNames):
        if not isinstance(colNames,(list,tuple)):
            return False
        if len(colNames) != len(self.colValues):
            return False
        return True

    def _testAll(self):
        if False in  [ self.__testPath(self.fullPath),
            self.__testSheetName(self.sheetName),
            self.__testFileInit(self.fileInit),
            self.__testColNumbers(self.colNumbers),
            self.__testColValues(self.colValues),
            self.__testColNames(self.colNames)]:
            return False
        return True

    def _getPath(self):
        return self._fullPath

    def _setPath(self,fullPath):
        if not self.__testPath(fullPath):
            raise StandardError(u"the path is'nt a file: \n"+self.fullpath)
        self._fullPath = fullPath
        self.wb =  load_workbook(filename = fullPath)
        # actualizar los nombres de las hojas
        self.sheets= [sheet.name for sheet in self.wb.get_sheet_names()]

    def _getSheet(self):
        return self._sheetName

    def _setSheet(self,sheetName):
        if not self.__testSheetName(sheetName):
            texto = ""
            for texti in self.sheets:
                texto += texti + u"\n"
            raise StandardError("the possible names of the sheets are:\n"
                                + texto)
        self._sheetName = sheetName
        self.sheetObj = self.wb.get_sheet_by_name(sheetName)
        self.sheetSize = (self.sheetObj.get_highest_row(), self.sheetObj.get_highest_column())

    def _getFileInit(self):
        return self._fileInit

    def _setFileInit(self,fileInit):
        if not self.__testFileInit(fileInit):
            raise StandardError("The init file can't be greater than " + str(self.sheetSize[0]))
        self._fileInit = fileInit

    def _getColNumbers(self):
        return self._colNumbers

    def _setColNumbers(self,colNumbers):
        if not self.__testColNumbers(colNumbers):
            raise StandardError(u'Ha excedido el numero maximo de columnas posibles : '+
                                str(self.sheetSize[1]))
        self._colNumbers = colNumbers

    def _getColValues(self):
        return self._colValues

    def _setColValues(self,colValues):
        if not self.__testColNumbers(colValues):
            raise StandardError(u'Ha excedido el numero maximo de columnas posibles : '+
                                str(self.sheetSize[1]))
        self._colValues = colValues

    def _getColNames(self):
        return self._colNames

    def _setColNames(self,colNames):
        if not self.__testColNames(colNames):
            raise StandardError("the elements of colValues and colNames must be the same")
        self._colNames = colNames
    fullPath = property(_getPath, _setPath)
    sheetName = property(_getSheet, _setSheet)
    fileInit = property(_getFileInit, _setFileInit)
    colNumbers = property(_getColNumbers, _setColNumbers)
    colValues = property(_getColValues, _setColValues)
    colNames = property(_getColNames, _setColNames)



class distinctxls2:
    '''Actualmente solo funciona para archivos con formato xls unicamente
    '''
    def __init__(self, fullPath=None, sheetName= None, fileInit=0, colNumbers=(1,), colValues=(2,) ,colNames=(u'salida1')):
        '''
        '''
        self._fullPath = fullPath
        self._sheetName = sheetName
        self._fileInit = fileInit
        self._colNumbers= colNumbers
        self._colValues = colValues
        self._colNames = colNames
        self.sheets = []
        self.sheetSize = (None,None)
        self.__setParams()

    def __setParams(self):
        # se ejecuta al iniciar el codigo
        try:
            self._setPath(self._fullPath)
        except:
            pass
        try:
            self._setSheet(self._sheetName)
        except:
            pass
        try:
            self._setFileInit(self._fileInit)
        except:
            pass
        try:
            self._setColNumbers(self._colNumbers)
        except:
            pass
        try:
            self._setColValues(self._colValues)
        except:
            pass
        try:
            self._setColNames(self._colNames)
        except:
            pass

    def calc(self):
        if not self._testAll():
            raise StandardError("One or mores parameters doesn't rigth")

        diccionario = cols2dict(*[[cell.value for cell in self.sheetObj.col(k)][self.fileInit:] for k in self.colNumbers])
        # se almacenan los datos en el diccionario:
        for row in range(self.fileInit,self.sheetSize[0]):
            lista = [cell.value for cell in self.sheetObj.row(row)]
            for colName,colValue in zip(self.colNames,self.colValues):
                if lista[colValue] == u'':
                    lista[colValue] = None
                self.__setdictValue(diccionario, keys=[lista[i] for i in self.colNumbers],\
                               nombreCampo=colName, value=lista[colValue])
        return diccionario

    def __setdictValue(self,diccionario,keys,nombreCampo,value):
        if not isinstance(keys,(list,tuple)):
            return
        if len(keys) == 1:
            try:
                diccionario[keys[0]][nombreCampo].append(value)
            except KeyError:
                diccionario[keys[0]][nombreCampo] = list()
                diccionario[keys[0]][nombreCampo].append(value)
        else:
            self.__setdictValue(diccionario[keys[0]],keys[1:],nombreCampo,value)

    def __testPath(self,fullPath):
        return os.path.isfile(fullPath)

    def __testSheetName(self,sheetName):
        if not self.__testPath(self.fullPath):
            return False
        if sheetName in self.sheets:
            return True
        return False

    def __testFileInit(self,fileInit):
        if not self.__testSheetName(self.sheetName):
            return False
        if fileInit > self.sheetSize[0]:
            return False
        return True

    def __testColValues(self,colValues):
        if not isinstance(colValues,(list,tuple)):
            return False #raise TypeError('solo ingrese tuplas o listas')
        if max(colValues) > self.sheetSize[1]:
            #raise StandardError(u'Ha excedido el numero maximo de columnas posibles : '+
            #                    str(self.sheetSize[1]))
            return False
        return True

    def __testColNumbers(self,colNumbers):
        if not isinstance(colNumbers,(list,tuple)):
            return False #raise TypeError('solo ingrese tuplas o listas')
        if max(colNumbers) > self.sheetSize[1]:
            #raise StandardError(u'Ha excedido el numero maximo de columnas posibles : '+
            #                    str(self.sheetSize[1]))
            return False
        return True

    def __testColNames(self,colNames):
        if not isinstance(colNames,(list,tuple)):
            return False
        if len(colNames) != len(self.colValues):
            return False
        return True

    def _testAll(self):
        if False in  [ self.__testPath(self.fullPath),
            self.__testSheetName(self.sheetName),
            self.__testFileInit(self.fileInit),
            self.__testColNumbers(self.colNumbers),
            self.__testColValues(self.colValues),
            self.__testColNames(self.colNames)]:
            return False
        return True

    def _getPath(self):
        return self._fullPath

    def _setPath(self,fullPath):
        if not self.__testPath(fullPath):
            raise StandardError(u"the path is'nt a file: \n"+self.fullpath)
        self._fullPath = fullPath
        self.wb = xlrd.open_workbook(fullPath)
        # actualizar los nombres de las hojas
        self.sheets= [sheet.name for sheet in self.wb.sheets()]

    def _getSheet(self):
        return self._sheetName

    def _setSheet(self,sheetName):
        if not self.__testSheetName(sheetName):
            texto = ""
            for texti in self.sheets:
                texto += texti + u"\n"
            raise StandardError("the possible names of the sheets are:\n"
                                + texto)
        self._sheetName = sheetName
        self.sheetObj = self.wb.sheet_by_name(sheetName)
        self.sheetSize = (self.sheetObj.nrows, self.sheetObj.ncols)

    def _getFileInit(self):
        return self._fileInit

    def _setFileInit(self,fileInit):
        if not self.__testFileInit(fileInit):
            raise StandardError("The init file can't be greater than " + str(self.sheetSize[0]))
        self._fileInit = fileInit

    def _getColNumbers(self):
        return self._colNumbers

    def _setColNumbers(self,colNumbers):
        if not self.__testColNumbers(colNumbers):
            raise StandardError(u'Ha excedido el numero maximo de columnas posibles : '+
                                str(self.sheetSize[1]))
        self._colNumbers = colNumbers

    def _getColValues(self):
        return self._colValues

    def _setColValues(self,colValues):
        if not self.__testColNumbers(colValues):
            raise StandardError(u'Ha excedido el numero maximo de columnas posibles : '+
                                str(self.sheetSize[1]))
        self._colValues = colValues

    def _getColNames(self):
        return self._colNames

    def _setColNames(self,colNames):
        if not self.__testColNames(colNames):
            raise StandardError("the elements of colValues and colNames must be the same")
        self._colNames = colNames
    fullPath = property(_getPath, _setPath)
    sheetName = property(_getSheet, _setSheet)
    fileInit = property(_getFileInit, _setFileInit)
    colNumbers = property(_getColNumbers, _setColNumbers)
    colValues = property(_getColValues, _setColValues)
    colNames = property(_getColNames, _setColNames)

def getdict(diccionario,keys):
    '''Dadas las llaves como lista se consulta los valores'''
    try:
        if len(keys) == 1:
            return diccionario[keys[0]]
        else:
            return getdict(diccionario[keys[0]],keys[1:])
    except KeyError:
        raise

def dict2list(diccionario):
    '''convierte un diccionario como una lista de datos'''
    try:
        for key in diccionario.keys():
            for key2 in dict2list(diccionario[key]):
                yield (key,) + key2
    except:
        yield (diccionario, )

def dict2list2(diccionario,maximo):
    '''Dado un diccionario y un valor maximo de
    nivel retorna un generador con filas de la
    informacion.
    '''
    return _newdict(diccionario,actual= 1,maximo = 3)

def _newdict(diccionario,actual,maximo):
    try:
        if actual > maximo:
            raise
        for key in diccionario.keys():
            for key2 in _newdict(diccionario[key],actual+1,maximo):
                yield (key,) + key2
    except:
        yield (diccionario, )

def rows2dict(*cols):
    '''convierte una serie de columnas en diccionario'''
    # se determinan que todas las filas tengan igual cantidad de elementos
    data = [len(col) for col in cols]
    if False in map(lambda x,y:  x == y, data[1:] ,data[:-1]):
        raise StandardError('Los argumentos deben tener igual cantidad de elementos')
    # se convierte las columnas a filas
    data = data[0]
    result = ()
    for pos in range(data):
        result += ([col[pos] for col in cols],)
    # se hace los calculos
    return list(fil2dict(list(result)))[0]

def cols2dict(*cols):
    '''convierte una serie de columnas en diccionario'''
    # se determinan que todas las filas tengan igual cantidad de elementos
    data = [len(col) for col in cols]
    if False in map(lambda x,y:  x == y, data[1:] ,data[:-1]):
        raise StandardError('Los argumentos deben tener igual cantidad de elementos')
    # se convierte las columnas a filas
    data = data[0]
    result = ()
    for pos in range(data):
        result += ([col[pos] for col in cols],)
    # se hace los calculos
    return list(fil2dict(list(result)))[0]

def setdict(diccionario,keys,newKeys):
    if len(keys) == 1:
        # se adiciona las llaves unicas
        llaves = distinct(diccionario[keys[0]])
        for llave in llaves:
            diccionario[keys][llave] = []

def fil2dict(data):
    '''convierte una serie de filas en diccionario'''
    result = dict()
    for dato in data:
        try:
            key = dato[0]
            result[key] += (dato[1:],)
        except KeyError:
            result[key] = (dato[1:],)
        except IndexError:
            break
    for key in result.keys():
        for key2 in fil2dict(result[key]):
            result[key] = key2
    yield result

def vacio(data):
    if True in list(vacioIter(data)):
        return True
    return False

def vacioIter(data):
    if isinstance(data,(str,int,long,bool)):
            yield False
    else:
        try:
            if len(data) == 0:
                yield True
        except:
            pass
        for dato in data:
            if isinstance(dato,(str,int,long)):
                yield False
            else:
                for dat in vacio(dato):
                    yield dat


def findNames(obj):
    frame = sys._getframe()
    for frame in iter(lambda: frame.f_back, None):
        frame.f_locals
    result = []
    for referrer in gc.get_referrers(obj):
        if isinstance(referrer, dict):
            for k, v in referrer.iteritems():
                if v is obj:
                    result.append(k)
    print result
    keylist= globals().keys()
    keylist.extend(locals().keys())
    for i in result:
        if i in keylist:
            return i
    if len(result) == 1:
        return result
    return None

def variable_for_value(value):
    for key in globals().keys():
        if key == value:
            return True
    return False

def getAllData(lista):
    if isinstance(lista,(str,)):
        yield lista
    else:
        try:
            for dat in lista:
                for val in getAllData(dat):
                    yield val
        except:
            yield lista

def testFullPath(path):
    '''determina si el full path es correcto entrega tambien
    la ruta y el nombre del archivo seleccionado

    path = ruta completa

    entrega:

    (bool, dirpath, filemane, fullpath)
    bool: True si el archivo existe
    dirpath: ruta del directorio
    filemane: nombre del archivo seleccionado
    fullpath: ruta completa para el sistema opreativo seleccioando
    '''
    path= os.path.abspath(path)
    if not os.path.isfile(path):
        return (False,None,None)
    directorio = os.path.dirname(path)
    file = os.path.split(path)[-1]
    return (True,directorio, file, os.path.join(directorio, file))

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
            raise StandardError("SaveClass: doesn't have permisions on the selected dir")
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


class existeEnDict:
    def __init__(self):
        pathDict = u'd:\\Proyecto SSPD\\NACIONAL DE CALIDAD DEL AGUA\\2009\\diccionario.txt'
        file= open(pathDict,'rb')
        self.words = [word[:-1] for word in file.readlines()] # [unicode(word[:-1], "utf-8" ) for word in file.readlines()]
        file.close()

    def consulta(self,word):
        word = word.lower()
        for i in self.words:
            if i == word:
                return True
        return False

    def __getvalue__(self,word):
        return self.consulta(word)

def organizaEsp(texto):
    try:
        texto = texto.upper()
    except:
        #print u'no se logro convertir en mayusculas: '
        #print  texto
        if type(texto) == type(list()):
            return (False,texto[0])
        return (False,texto)
    # dado una cadena de texto se filtra el nombre con base en el criterio
    # esp como una tupla
    # retorna (ContineESP, cadenaOrganizada) donde
    #  ContieneESP: corresponde a un boolean indicando si contiene o no informacion.
    #  cadenaOrganizada: cadena organizada segun los criterios

    # 1- se eliminan los espacios vacios
    texto = eliminaBadDot(eliminaBadBlanc(texto))
    # se determina si la cadena de texto contiene la palabra esp
    ContieneESP = False
    for i in ESP:
        texto= texto.split(i)
        if len(texto) > 1:
            if texto[0] == i:
                texto = texto[0]
            else:
                texto = texto[0] + u' E.S.P.'
            ContieneESP = True
            break
        else:
            texto = texto[0]
    if ContieneESP:
        return (ContieneESP,eliminaBadDot(eliminaBadBlanc(texto)))
    # se verifica que no tenga una de las variaciones de esp definidas
    # en ESP_NO
    for i in ESP_NO:
        if len(texto.split(i)) > 1:
            return (ContieneESP,eliminaBadDot(eliminaBadBlanc(texto)))
    # En caso de no contener una de las variaciones se trata de separar
    # la palabra esp
    texto2= texto.split(u'ESP')
    if len(texto2) == 1:
        return (ContieneESP,eliminaBadDot(eliminaBadBlanc(texto)))
    texto = texto2[0] + u' E.S.P.'
    ContieneESP = True
    return (ContieneESP,eliminaBadDot(eliminaBadBlanc(texto)))

def organizaSA(texto):
    try:
        texto = texto.upper()
    except:
        print u'no se logro convertir en mayusculas: '
        print  texto
        if type(texto) == type(list()):
            return (False,texto[0])
        return (False,texto)
    # dado una cadena de texto se filtra el nombre con base en el criterio
    # esp como una tupla
    # retorna (ContineSA, cadenaOrganizada) donde
    #  ContieneSA: corresponde a un boolean indicando si contiene o no informacion.
    #  cadenaOrganizada: cadena organizada segun los criterios

    # 1- se eliminan los espacios vacios
    texto = eliminaBadDot(eliminaBadBlanc(texto))
    # se determina si la cadena de texto contiene la palabra SA
    ContieneSA = False
    for i in SA:
        texto= texto.split(i)
        if len(texto) > 1:
            if texto[0] == i:
                texto = texto[0]
            else:
                texto = texto[0] + u' S.A.'
            ContieneSA = True
            break
        else:
            texto = texto[0]
    if ContieneSA:
        return (ContieneSA,eliminaBadDot(eliminaBadBlanc(texto)))
    # se verifica que no tenga una de las variaciones de SA definidas
    # en SA_NO
    for i in SA_NO:
        if len(texto.split(i)) > 1:
            return (ContieneSA,eliminaBadDot(eliminaBadBlanc(texto)))
    for i in SA_NO2:
        if len(texto.split(i)) > 1:
            return (ContieneSA,eliminaBadDot(eliminaBadBlanc(texto)))
    # En caso de no contener una de las variaciones se trata de separar
    # la palabra SA
    texto2= texto.split(u'SA')
    if len(texto2) == 1:
        return (ContieneSA,eliminaBadDot(eliminaBadBlanc(texto)))
    texto = texto2[0] + u' S.A.'
    ContieneSA = True
    return (ContieneSA,eliminaBadDot(eliminaBadBlanc(texto)))

def eliminaMinus(texto):
    # elimina los menos en la cadena de texto
    # si la longitud de la cadena es de mas de 2
    # se verifica la posicion incial que no sea un numero
    #  si es un numero solo se toma la posicion 1 de la
    #  cadena.
    texto = texto.split(u'-')
    if len(texto) == 1:
        return (False,texto[0])
    caracter = texto[0][0]
    if len([True for i in range(10) if str(i) == caracter]) > 0:
        texto = texto[1]
    else:
        texto = texto[0]
    if type(texto) == type(list()):
        print texto
    return (True,texto)

def eliminaBadDot(texto):
    '''Elimina los blancos mal situados
    '''
    if texto == u'':
        return texto
    caracter = u'.'
    if len(texto.split(caracter)) == 1:
        return texto
    texto = texto.split(caracter)
    puntoFinal = False
    if texto[-1] == u'':
        puntoFinal = True
    # se eliminan todos los u'.'
    texto= [textoi for textoi in texto if textoi != u'']
    # se juntan los textos obtenidos
    newtext = u''
    for textoi in texto:
        newtext += textoi + caracter
    if puntoFinal:
        return newtext
    return newtext[:-1]

def eliminaBadBlanc(texto,caracter = u' '):
    if texto == u'':
        return texto
    if len(texto.split(u' ')) == 1:
        return texto
    texto = texto.split(caracter)
    # se eliminan todos los u''
    texto= [textoi for textoi in texto if textoi != u'']
    # se juntan los textos obtenidos
    newtext = u''
    for textoi in texto:
        newtext += textoi + caracter
    return newtext[:-1]

def delEndWord(word):
    # se elimina los espacios en blancco finales de la palabra
    word = eliminaBadBlanc(word)
    # elimna de la cadena la palbra final que cumpla con las condiciones:
    eliminar = [u'1',u'2',u'3']
    if len(word) < 3:
        return word
    if len([True for letra in eliminar if letra == word[-1]]) > 0:
        return word[:-1]
    if len(word) < 5:
        return word
    if word[-2:] == u'II':
        return word[:-2]
    if word[-1] == u'I':
        return word[:-1]
    if len(word) < 7:
        return word
    if word[-4:] == u'ALTO' or word[-4:] == u'BAJO' \
        or word[-4:] == u'BAJA' or word[-4:] == u'ALTA' \
        or word[-5:] == u'MEDIO':
        return word[:-4]
    return word

def distinctOld(data):
    # entrega un tipo de datos diferente
    if len(data) == 0:
        return data
    unicos = list()
    unicos.append(data.pop(0))
    while len(data) > 0:
        valor = data.pop(0)
        test = 1
        for i in unicos:
            if i == valor:
                test = 0
        if test:
            unicos.append(valor)
    return unicos

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


if __name__ == '__main__':
    if test_GroupData():
        print "la funcion groupdata funciona correctamente"
    test_GroupTxt()
    test_GroupExcel()
    if 0:
        path = u'D:\\Proyecto SSPD\\DISE\xd1O DE REPORTES PARA LA CALIDAD DEL AGUA\\IRCAS REPORTADOS\\test\\IRCA mensual entregado.xlsx'
        diccionario = {'casa':{'pieza':{'personas':{'ojos':2, 'piernas': 2}}}, 'auto':{'caminoneta':{'llantas':4}}}
        #resultado = dict2listSubNivel(diccionario,maxSubnivel = None)
        # from SlbTools import setdictValue
        import xlrd
        # from SlbTools import distinctxls
        PATH = u'd:\\Proyecto SSPD\\SECTORIAL SSPD 2010\\entregable\\2011 sept 12\\'
        filename = u'IRCA por Empresa.xls'
        wb = xlrd.open_workbook(PATH + filename)
        sheet = wb.sheet_by_name(u'Total')
        diccionario = distinctxls(sheet, colNumbers=[0,1,5], colValues=[18,20], colNames=['IRCApoderado','IRCApromedio'])
        if 0:
            identDup([1,2,4,1])
            result = rows2dict(('caldas','risaralda','caldas','caldas'),('manizales','pereira','anserma','riosucio'),)
            print list(rows2dict(('caldas','risaralda','caldas','caldas'),('manizales','pereira','anserma','riosucio'),))
            print list(fil2dict((('mani','anserma',550),('mani','aguadas',789),('risaralda','pereira'),('mani','caldas',611))))
            perro = 8
            print findNames(perro)
            hoja = ReportaExcel(path= 'd:\\',file='ensayo para borrar.xls')
            hoja.writeByRow(range(20))
            hoja.writeByRow(range(2,54,5), 3)
            hoja.writeByRow(range(2,54,5))
            #hoja.write(range(2,20))
            #hoja.write(range(2,20))
            #hoja.write(range(2,10),1)
            #hoja.write(range(2,10),3)
            hoja.save()