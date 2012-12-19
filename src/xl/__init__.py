__all__ = ['Xl']

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
    def __init__(self, xl):
        self._xl= xl
    def open(self):
        pass
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
        self._wb=  default['wb']
        self._sh=  None
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
    @property
    def wb(self):
        if self._wb == None:
            self._xl.Workbooks.Add()
            self._wb= self._xl.ActiveWorkbook
            # update the sheets
            self.sh
        return self._wb

    @wb.setter
    def wb(self, wbPath):
        # wbPath: path of the workbook
        if not isinstance(wbPath, (str, unicode)):
            raise StandardError("only accept string or unicode value for wbPath parameter")

        if not _isfile(wbPath):
            raise IOError("the path is not a valid or existent file: " + wbPath)

        self._wb = self._xl.Workbooks.open(wbPath)
        # update the sheets
        self._sh = self._updateSheets()

    def _updateSheets(self):
        sh= Sheets(self.wb)
        return sh # a list
    @property
    def sh(self):
        #sheetNumber: number or name of the sheet
        if self._sh == None:
            self._sh= self._updateSheets()
        return self._sh
    def activeSheet(self):
        return Sheet(self.wb.ActiveSheet)
    @property
    def ScreenUpdating(self):
        return self._xl.ScreenUpdating
    @ScreenUpdating.setter
    def ScreenUpdating(self, state):
        if state== True or state == False:
            self._xl.ScreenUpdating= state
        else:
            raise StandardError(" state not available only True/False is allowed")

if 0:
    # add a new Workbook
    wb= xl.Workbooks.Add()
    # the number of sheets
    nSheets= wb.Sheets.Count
    # changing the name of the first sheet
    ShNames= [sh.name for sh in wb.Sheets]
    sh= wb.Sheets(ShNames[0])
    # changing the name of the selected sheet
    sh.name= u"Selobu"

    #=======================
    # creating a chart
    chart= wb.Charts.Add()
    chart.SetSourceData(sh.Range("$A:$B"))
    # destroy the chart
    #chart.Delete()

    # deleting all charts in a worksheet
    try:
        sh.ChartObjects().Delete()
    except:
        pass

    # getting a range of data
    rg= numpy.array(sh.Range("A1:C5").value)

    if 0:
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


        def PutCol(colNumber, values, sheet= None):
            if sheet== None:
                sheet = wb.ActiveSheet
            sheet.Range( sheet.Cells(1,colNumber), sheet.Cells(len(values), colNumber)).Value= [(val,) for val in values]

        def GetCol(colNumber,sheet= None):
            if sheet== None:
                sheet = wb.ActiveSheet
            lastRow= sheet.Cells( sheet.Rows.Count,colNumber).End(-4162).Row
            values=  sheet.Range( sheet.Cells(1,colNumber), sheet.Cells(lastRow, colNumber)).Value
            return [val[0] for val in values]

    def GetColRange(colNumber,sheet= None):
        if sheet== None:
            sheet = wb.ActiveSheet
        lastRow= sheet.Cells( sheet.Rows.Count,colNumber).End(-4162).Row
        return sheet.Range( sheet.Cells(1,colNumber), sheet.Cells(lastRow, colNumber))

    # clear a col
    def ClearCol(colNumber, sheet= None):
        if sheet== None:
            sheet = wb.ActiveSheet
        lastRow= sheet.Cells( sheet.Rows.Count,colNumber).End(-4162).Row
        sheet.Range( sheet.Cells(1,colNumber), sheet.Cells(lastRow, colNumber)).ClearContents()

    # calling a function from excel
    xl.WorksheetFunction.Pmt(0.0825 /12.0, 360, -150000)