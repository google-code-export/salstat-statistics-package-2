__all__ = ['Xl']
# check http://win32com.goermezer.de/component/option,com_frontpage/Itemid,239/

from os.path import isfile as _isfile

class Sheet:
    def __init__( self, sheetObj):
        self._sh= sheetObj
    @property
    def sh( self):
        return self._sh
    @property
    def Name( self):
        return self.sh.Name
    @Name.setter
    def Name( self, newName):
        if not isinstance( newName, (str, unicode)):
            raise StandardError()

        self.sh.Name= newName

    def GetCol( self, colNumber):
        maxColNumber=  self.sh.Columns.Count
        if colNumber > maxColNumber:
            raise StandardError( "Column Number %i > maximun column Number %i"%(colNumber, maxColNumber))
        lastRow=  self.sh.Cells( self.sh.Rows.Count, colNumber).End( -4162).Row
        values=   self.sh.Range( self.sh.Cells( 1,colNumber), self.sh.Cells( lastRow, colNumber)).Value
        return [val[0] for val in values]

    def PutCol( self, colNumber, colValues, overwriteColum= True):
        if len(colValues) > 0:
            self.sh.Range( self.sh.Cells( 1,colNumber), 
                           self.sh.Cells( len(colValues), colNumber)).Value= [(val,) for val in colValues]
        lastRow= self.sh.Cells( self.sh.Rows.Count, colNumber).End(-4162).Row
            # clear the existent contents
        if overwriteColum:
            if len(colValues) < lastRow:
                self.sh.Range( self.sh.Cells( len(colValues)+1 ,colNumber), 
                               self.sh.Cells( lastRow, colNumber)).ClearContents()
    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.Name)
    @property
    def Range(self):
        return self.sh.Range
    @property
    def Cells(self):
        return self.sh.Cells
class Sheets(object):
    def __init__(self, wb):
        self._wb =    wb
        self._sheets= [Sheet( self.wb.Sheets( shNumber)) for shNumber in range( 1, self.wb.Sheets.Count +1)]
    @property
    def wb( self):
        return self._wb
    def __getitem__( self, sheet):
        if isinstance(sheet, (int, float)):
            if sheet < 0:
                sheet= self.__len__()+sheet-1
            return self._sheets[sheet]
                
        elif isinstance(sheet, (str, unicode)):
            for sh in self._sheets:
                if sh.Name== sheet:
                    return sh
            raise KeyError(sheet.__str__ + " not found")
    def __len__(self):
        return len(self._sheets)

class Wb(object):
    def __init__(self, xl, wbObject= None):
        self._xl= xl
        # wbPath: path of the workbook
        if wbObject == None:
            # Try to set the wb to a new workbook
            self._xl.Workbooks.Add()
            self._wb= self.xl.ActiveWorkbook
            self._sh = self._updateSheets()
        elif isinstance(wbObject, (str,unicode)):
            if _isfile(wbObject):
                self._wb = self.xl.Workbooks.open( wbPath)
                self._sh = self._updateSheets()
            else:
                raise IOError(wbObject + " is not a file")
        else:
            self._wb= wbObject
            self._sh = self._updateSheets()
                    
    def _updateSheets(self):
        sh= Sheets(self)
        return sh # a list
    
    @property
    def Sheets(self):
        return self._wb.Sheets
    @property
    def xl(self):
        return self._xl
    @property
    def sh(self):
        #sheetNumber: number or name of the sheet
        if self._sh == None:
            self._sh= self._updateSheets()
        return self._sh
    
    def addSheet(self, sheetName= None):
        sh= self._wb.Add()
        if sheetName != None:
            if isinstance( sheetName, (str, unicode)):
                sh.Name= sheetName
            else:
                sh.Name= sheetName.__str__()
        self._sh= self._updateSheets()
    @property
    def name(self):
        return self._wb.name
    @property
    def activeSheet(self):
        return Sheet(self._xl.ActiveWorkbook.ActiveSheet)

class Wbs(object):
    def __init__(self, xl):
        self._xl=  xl
        self._wbs= [ Wb( self.xl, self.xl.Workbooks[wbNumber]) for wbNumber in range( self.xl.Workbooks.Count)]
        
    @property
    def xl( self):
        return self._xl
    
    def __getitem__( self, wbNumber):
        wbName= wbNumber 
        if isinstance( wbNumber, (int, float)):
            if wbNumber < 0:
                wbNumber= self.__len__() + wbNumber - 1
            return self._wbs[wbNumber]
        # try to find for a number
        elif isinstance( wbName, (str, unicode)):
            for sh in self._wbs:
                if sh.Name== wbName:
                    return sh
            raise KeyError( wbName.__str__ + " not found")
        
    def __len__(self):
        return len(self._wbs)
    
class Xl(object):
    def __init__(self,**params):
        from win32com.client import Dispatch
        self._xl=   Dispatch("Excel.Application")
        default= {'Visible': True,
                  'wb':      None,}
        for key in default.keys():
            try:
                default[key]= params.pop(key)
            except KeyError:
                pass
        self._xl.Visible = default['Visible']
        #self._wb= Wbs(self)
    @property
    def wb(self):
        return Wbs(self)
    
    @property
    def Workbooks(self):
        return self._xl.Workbooks
    
    @property
    def addwb(self):
        self._xl.Workbooks.Add() 
        return self.wb[-1]
    
    def _rgb_to_hex(self,r,g,b):
        return '%02x%02x%02x'%(r,g,b)
    def rgb(self, *rgb):
        # changes an rgb to its int corresponding
        s= self._rgb_to_hex(*rgb)
        return int(s, 16)
    @property
    def Visible(self):
        return self._xl
    
    @Visible.setter
    def Visible(self, value):
        if value == True:
            self._xl.Visible = True
        elif value == False:
            self._xl.Visible = False
        else:
            raise StandardError("Available options True/False")
        return Sheet(self._xl.ActiveWorkbook.ActiveSheet)
        
    @property
    def ScreenUpdating(self):
        return self._xl.ScreenUpdating
    @ScreenUpdating.setter
    def ScreenUpdating(self, state):
        if state== True or state == False:
            self._xl.ScreenUpdating= state
        else:
            raise StandardError(" state not available only True/False is allowed")
    @property
    def ActiveWorkbook(self):
        return Wb(self._xl, self._xl.ActiveWorkbook)

if 0:
    #=======================
    # creating a chart
    chart= wb.Charts.Add()
    chart.SetSourceData(sh.Range("$A:$B"))
    # destroy the chart
    chart.Delete()

    # deleting all charts in a worksheet
    try:
        sh.ChartObjects().Delete()
    except:
        pass

    

    #  reading the maximum num of columns and row of existing data
    [maxRows, maxCols] = (sh.Rows.Count,sh.Columns.Count)
    # readign the non empty columns and rows
    [ lastColumn, lastRow]=(sh.Cells( 1, sh.Columns.Count).End(-4159).Column, sh.Cells(sh.Rows.Count,1).End(-4162).Row)
    print [ lastColumn, lastRow]
    # Setting cell value
    sh.Cells(1,1).Value= 1

    # stop screen updating
    xl.ScreenUpdating = False
    # continue screen updating
    xl.ScreenUpdating = True

    # calling a function from excel
    xl.WorksheetFunction.Pmt(0.0825 /12.0, 360, -150000)