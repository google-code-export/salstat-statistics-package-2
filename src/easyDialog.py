'''
Created on 16/05/2012

@author: USUARIO
'''
'''Easily create a dialog'''

import wx
from dialogs import CheckListBox, NumTextCtrl

def _siguiente():
    i = 0
    while 1:
        i+= 1
        yield str(i)

class Dialog ( wx.Dialog ):
    def __init__( self, parent = None , settings= dict(), struct = []):
        '''Dialog(parent,settings, struct)

        a function to easily create a wx dialog

        paramteres
        settings = {'Tile': String title of the wxdialog ,
                    'icon': wxbitmap,
                    '_size': wx.Size(xsize, ysize) the size of the dialog ,
                    '_pos':  wx.Position(-1, -1) the position of the frame,
                    '_style': wx.DIALOG__STYLE of the dialog ,
        struct = list() information with the data

        allowed controls: 'StaticText',   'TextCtrl',    'Choice',
                          'CheckListBox', 'StaticLine',  'RadioBox',
                          'SpinCtrl',     'ToggleButton', 'NumTextCtrl'

        struct example:

        >> structure = list()

        >> bt1 = ('StaticText', ('hoja a Imprimir',))
        >> bt2 = ('Button', ('nuevo',))

        >> bt6=  ('TextCtrl', ('Parametro',))

        >> btnChoice = ('Choice',(['opt1','opcion2','opt3'],))

        >> btnListBox = ('CheckListBox',(['opt1','opcion2','opt3'],))

        >> listSeparator = ('StaticLine',('horz',))

        >> bt7 = ('RadioBox',('titulo',['opt1','opt2','opt3'],))
        >> bt8 = ('SpinCtrl', ( 0, 100, 5 )) # (min, max, start)
        >> bt9 = ('ToggleButton', ['toggle'])

        >> structure.append( [bt6, bt2] )
        >> structure.append( [bt6, bt5] )
        >> structure.append( [btnChoice, bt9 ] )
        >> structure.append( [listSeparator])
        >> structure.append( [btnListBox , bt1])
        >> structure.append( [bt7, ])
        >> structure.append( [bt8, ])

        to see an example run the class as a main script

        }'''
        self.ctrlNum = _siguiente()
        self.sizerNum= _siguiente()

        params = {'Title':  wx.EmptyString,
                  'icon':   None,
                  '_size':  wx.Size(-1,-1), #260,320
                  '_pos':   wx.DefaultPosition,
                  '_style': wx.DEFAULT_DIALOG_STYLE}

        for key, value in params.items():
            try:
                params[key] = settings[key]
            except:
                pass

        wx.Dialog.__init__ ( self, parent, 
                             id=     wx.ID_ANY,
                             title=  params.pop('Title'),
                             pos=    params.pop('_pos'),
                             size=   params.pop('_size'),
                             style=  params.pop('_style') )
        #< setting the icon
        icon= params.pop('icon')
        if icon == None:
            try:
                icon= wx.GetApp().icon
            except AttributeError:
                icon= wx.EmptyIcon()
        self.SetIcon(icon)
        # setting the icon/>

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        self.m_scrolledWindow1 = wx.ScrolledWindow( self, wx.ID_ANY,
                                     wx.DefaultPosition, wx.DefaultSize,
                                      wx.DOUBLE_BORDER|wx.HSCROLL|wx.VSCROLL )
        self.m_scrolledWindow1.SetScrollRate( 5, 5 )
        bSizer3 = wx.BoxSizer( wx.VERTICAL )
        self.sisers= list()
        self.ctrls= list()
        self._allow= ['StaticText','TextCtrl','Choice',
                      'CheckListBox','StaticLine','RadioBox',
                      'SpinCtrl','ToggleButton','NumTextCtrl']
        self._allow2get= ['TextCtrl','Choice',
                      'CheckListBox','RadioBox',
                      'SpinCtrl','ToggleButton','NumTextCtrl']
        
        self.adding(bSizer3, struct)

        self.m_scrolledWindow1.SetSizer( bSizer3 )
        self.m_scrolledWindow1.Layout()
        bSizer3.Fit( self.m_scrolledWindow1 )
        bSizer1.Add( self.m_scrolledWindow1, 1, wx.EXPAND |wx.ALL, 5 )
        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize()

        bSizer1.Add( m_sdbSizer1, 0, wx.ALL|wx.EXPAND, 5 )
        self.SetSizer( bSizer1 )
        self.Layout()
        self.Centre( wx.BOTH )

    def adding(self, parentSizer, struct ):
        diferents= ['CheckListBox','Choice',]
        for row in struct:
            namebox= 'boxSizer'+ self.ctrlNum.next()
            setattr(self, namebox, wx.FlexGridSizer( 0, len(row), 0, 0 ))
            currSizer= getattr(self, namebox)
            currSizer.SetFlexibleDirection( wx.BOTH )
            currSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
            characters= wx.ALIGN_CENTER_VERTICAL | wx.ALL
            for key, args in row:
                if hasattr(wx, key):
                    nameCtrl= 'ctrl' + self.sizerNum.next()
                    if key in diferents:
                        data= [wx.DefaultPosition, wx.DefaultSize, ]
                        data.extend(list(args))
                        data.append(0)
                        args= data
                    elif key == 'StaticLine':
                        data= [wx.DefaultPosition, wx.DefaultSize, ]
                        if args[0] == 'horz':
                            data.append(wx.LI_HORIZONTAL|wx.DOUBLE_BORDER)
                        else:
                            data.append(wx.LI_VERTICAL|wx.DOUBLE_BORDER)
                        args = data
                        characters = wx.ALL | wx.EXPAND
                    elif key == 'RadioBox':
                        data= [args[0] , wx.DefaultPosition, wx.DefaultSize]
                        data.append(args[1])
                        args= data
                    elif key == 'SpinCtrl':
                        data= [ wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS]
                        data.extend(list(args))
                        args= data
                    if key == 'CheckListBox':
                        self.ctrls.append((key, CheckListBox(self.m_scrolledWindow1, wx.ID_ANY, *args)))
                    else:
                        self.ctrls.append((key, getattr(wx, key)(self.m_scrolledWindow1, wx.ID_ANY, *args)))
                    currCtrl= self.ctrls[-1][1]
                    currSizer.Add(currCtrl, 0, characters , 5)

                elif key == 'NumTextCtrl':
                    self.ctrls.append((key, NumTextCtrl(self.m_scrolledWindow1, wx.ID_ANY, *args)))
                    currCtrl= self.ctrls[-1][1]
                    currSizer.Add(currCtrl, 0, characters , 5)

                #elif key == 'in':  # not used
                #    self.adding(parentSizer, [args])

            parentSizer.Add( currSizer, 0, wx.EXPAND, 5 )
            parentSizer.Layout()


    def GetValue(self):
        try:
            self.DECIMAL_POINT = wx.GetApp().DECIMAL_POINT
        except AttributeError:
            self.DECIMAL_POINT = '.'
            
        resultado = list()
        for typectrl, ctrl in self.ctrls:
            if typectrl in self._allow2get:
                if typectrl  in ['TextCtrl','ToggleButton','SpinCtrl']:
                    prevResult = ctrl.Value

                elif typectrl == 'Choice':
                    if len(ctrl.GetItems()) == 0:
                        prevResult = []
                    if ctrl.GetSelection() >= 0:
                        prevResult =  [ctrl.GetItems()[ctrl.GetSelection()]]
                    else:
                        prevResult= []

                elif typectrl == 'CheckListBox':
                    if len(ctrl.Checked) > 0:
                        prevResult= [ctrl.Items[pos] for pos in ctrl.Checked]
                    else:
                        prevResult= []

                elif typectrl == 'RadioBox':
                    prevResult= ctrl.Selection

                elif typectrl == 'NumTextCtrl':
                    prevResult = ctrl.GetValue()
                    if prevResult != None:
                        prevResult= float(prevResult.replace(self.DECIMAL_POINT,'.'))
                        if prevResult == int(prevResult):
                            prevResult == int(prevResult)
                    else:
                        prevResult=  None
                else:
                    continue
                resultado.append(prevResult)
        return resultado

class _example( wx.Frame ):
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY,
                     title = wx.EmptyString, pos = wx.DefaultPosition,
                     size = wx.Size( -1, -1 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer10 = wx.BoxSizer( wx.VERTICAL )

        self.m_button8 = wx.Button( self, wx.ID_ANY, u"Show Dialog", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer10.Add( self.m_button8, 0, wx.ALL, 5 )

        self.SetSizer( bSizer10 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_button8.Bind( wx.EVT_BUTTON, self.showDialog )

    # Virtual event handlers, overide them in your derived class
    def showDialog( self, evt ):
        dic= {'Title': 'title'}
        bt1= ('Button',     ['print'])
        bt2= ('StaticText', ['hoja a Imprimir'])
        bt3= ('Button',     ['nuevo'])
        bt4= ('StaticText', ['sebas'])
        bt5= ('StaticText', ['Ingrese la presion'])
        bt6= ('TextCtrl',   ['Parametro'])
        btnChoice=     ('Choice',       [['opt1', 'opcion2', 'opt3']])
        btnListBox=    ('CheckListBox', [['opt1', 'opcion2', 'opt3']])
        listSeparator= ('StaticLine',   ['horz'])
        bt7= ('RadioBox',     ['title', ['opt1', 'opt2', 'opt3']])
        bt8= ('SpinCtrl',     [ 0, 100, 5 ]) # (min, max, start)
        bt9= ('ToggleButton', ['toggle'])
        
        structure= list()
        structure.append( [bt6, bt2] )
        structure.append( [bt6, bt5] )
        structure.append( [btnChoice, bt9 ] )
        structure.append( [listSeparator])
        structure.append( [btnListBox , bt1])
        structure.append( [bt7, ])
        structure.append( [bt8, ])

        dlg= Dialog(self, settings = dic, struct= structure)
        if dlg.ShowModal() == wx.ID_OK:
            values= dlg.GetValue()
            print values
        dlg.Destroy()

if __name__ == '__main__':
    app= wx.App()
    frame= _example(None)
    frame.Show()
    app.MainLoop()
