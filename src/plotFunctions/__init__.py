'''a module thath will be used as a container of different functions'''
version = "0.0.1"
__all__ = ['histogramPlot', 'bar',
           'lines', 'scatter',
           'others']

'''
Created on 11/05/2012
New plot system

@author: Sebastian lopez Buritica <Colombia>
License: GPL3
'''
# wxPython module
import wx
import wx.aui
import wx.lib.agw.aui as aui
import matplotlib.mlab as mlab
# Matplotlib Figure object
from matplotlib.figure import Figure
from matplotlib import font_manager
from matplotlib.widgets import Cursor
# Numpy functions for image creation
import numpy as np
import matplotlib.path as mpath
import matplotlib.patches as mpatches

# import the WxAgg FigureCanvas object, that binds Figure to
# WxAgg backend. In this case, this is a wxPanel
from matplotlib.backends.backend_wxagg import \
     FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.backends.backend_wx import StatusBarWx
from matplotlib.backend_bases import MouseEvent
import matplotlib.cm as cm

from pylab import setp
from multiPlotDialog import selectDialogData2plot, scatterDialog
from easyDialog import NumTextCtrl

PROPLEGEND=   {'size':11}
markerStyles= [ 'None', '.', '+', 'o', 'v', 
                '^', '<', '>', '8', 's', 'p',
                '*', 'h', 'H', 'D', 'd']
faceColors=   ['b', 'g', 'r', 'c', 'm', 'y', 'k']
lineStyles=   ['_', '-', '--', ':']
lineSizes=    [str( x*0.5) for x in range( 1, 15, 1)]
markerSizes=  [str( x) for x in range( 1, 16, 1)]
alpha=        [str( x/float( 10)) for x in range( 1, 11)]

from easyDialog import Dialog as _dialog

def translate(data):
    return data

class log:
    def __init__(self):
        pass
    def write(a, *args, **params):
        print a

def generateColors():
    opt= ['r','b','g','m','c','y','k']
    newOpt= opt[:]
    while True:
        try:
            value= newOpt.pop(0)
        except IndexError:
            newOpt= opt[:]
            value= newOpt.pop(0)
        yield value
# <p/> INIT GAUSS FUNCTION
def smooth1d(x, window_len):
    # copied from http://www.scipy.org/Cookbook/SignalSmooth

    s=np.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
    w = np.hanning(window_len)
    y=np.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]

def smooth2d(A, sigma = 3):
    window_len = max(int(sigma), 3)*2+1
    A1 = np.array([smooth1d(x, window_len) for x in np.asarray(A)])
    A2 = np.transpose(A1)
    A3 = np.array([smooth1d(x, window_len) for x in A2])
    A4 = np.transpose(A3)
    return A4

class BaseFilter(object):
    def prepare_image(self, src_image, dpi, pad):
        ny, nx, depth = src_image.shape
        #tgt_image = np.zeros([pad*2+ny, pad*2+nx, depth], dtype="d")
        padded_src = np.zeros([pad*2+ny, pad*2+nx, depth], dtype="d")
        padded_src[pad:-pad, pad:-pad,:] = src_image[:,:,:]

        return padded_src#, tgt_image

    def get_pad(self, dpi):
        return 0

    def __call__(self, im, dpi):
        pad = self.get_pad(dpi)
        padded_src = self.prepare_image(im, dpi, pad)
        tgt_image = self.process_image(padded_src, dpi)
        return tgt_image, -pad, -pad


class OffsetFilter(BaseFilter):
    def __init__(self, offsets=None):
        if offsets is None:
            self.offsets = (0, 0)
        else:
            self.offsets = offsets

    def get_pad(self, dpi):
        return int(max(*self.offsets)/72.*dpi)

    def process_image(self, padded_src, dpi):
        ox, oy = self.offsets
        a1 = np.roll(padded_src, int(ox/72.*dpi), axis=1)
        a2 = np.roll(a1, -int(oy/72.*dpi), axis=0)
        return a2

class GaussianFilter(BaseFilter):
    "simple gauss filter"
    def __init__(self, sigma, alpha=0.5, color=None):
        self.sigma = sigma
        self.alpha = alpha
        if color is None:
            self.color=(0, 0, 0)
        else:
            self.color=color

    def get_pad(self, dpi):
        return int(self.sigma*3/72.*dpi)


    def process_image(self, padded_src, dpi):
        #offsetx, offsety = int(self.offsets[0]), int(self.offsets[1])
        tgt_image = np.zeros_like(padded_src)
        aa = smooth2d(padded_src[:,:,-1]*self.alpha,
                      self.sigma/72.*dpi)
        tgt_image[:,:,-1] = aa
        tgt_image[:,:,:-1] = self.color
        return tgt_image

class DropShadowFilter(BaseFilter):
    def __init__(self, sigma, alpha=0.3, color=None, offsets=None):
        self.gauss_filter = GaussianFilter(sigma, alpha, color)
        self.offset_filter = OffsetFilter(offsets)

    def get_pad(self, dpi):
        return max(self.gauss_filter.get_pad(dpi),
                   self.offset_filter.get_pad(dpi))

    def process_image(self, padded_src, dpi):
        t1 = self.gauss_filter.process_image(padded_src, dpi)
        t2 = self.offset_filter.process_image(t1, dpi)
        return t2


# EN GAUSS FUNCTIONS</p>

def data2Plotdiaglog(parent, columnNames, title= None):
    translate= wx.GetApp().translate
    txt1= ['StaticText',   [translate(u"Select data to plot")]]
    btn1= ['CheckListBox', [columnNames]]
    setting= {'Title': translate(title)}
    structure= list()
    structure.append( [txt1])
    structure.append( [btn1])
    return _dialog(parent = parent, struct= structure, settings= setting)

def gene():
    u= 1
    while True:
        yield u
        u+= 1
def passlog(data):
    print data

class scrolled1(wx.ScrolledWindow):
    def __init__( self, *args, **params):
        wx.ScrolledWindow.__init__( self, *args[1:], **params)
        self.figpanel=  self.Parent.Parent.figpanel
        self.log=       self.Parent.Parent.log
        try:
            self.translate= wx.GetApp().translate
        except AttributeError:
            self.translate= translate
        graphParams= args[0]
        
        if params.has_key('parent'):
            parent= params['parent']
        else:
            parent= args[1]        
        self.SetScrollRate( 5, 5 )
        
        bSizer2=            wx.BoxSizer( wx.VERTICAL )
        sbSizer3=           wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, self.translate(u"Title") ), wx.HORIZONTAL )
        self.plt_textCtr1=  wx.TextCtrl( self, wx.ID_ANY, graphParams['title'], wx.DefaultPosition, wx.Size( 135,-1 ), 0 )
        self.m_button3=     wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        
        sbSizer3.Add( self.plt_textCtr1, 0, 0, 5 )        
        sbSizer3.Add( self.m_button3, 0, 0, 5 )
        bSizer2.Add(  sbSizer3, 0, 0, 5 )

        sbSizer4 =          wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, self.translate(u"X label") ), wx.HORIZONTAL )
        self.plt_textCtr2=  wx.TextCtrl( self, wx.ID_ANY, graphParams['xlabel'], wx.DefaultPosition, wx.Size( 135,-1 ), 0 )
        self.m_button4 =    wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        sbSizer4.Add( self.plt_textCtr2, 0, 0, 5 )       
        sbSizer4.Add( self.m_button4, 0, 0, 5 )

        bSizer2.Add( sbSizer4, 0, 0, 5 )

        sbSizer5 =           wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, self.translate(u"Y label") ), wx.HORIZONTAL )
        self.plt_textCtr3=   wx.TextCtrl( self, wx.ID_ANY, graphParams['ylabel'], wx.DefaultPosition, wx.Size( 135,-1 ), 0 )
        self.m_button5 =     wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        sbSizer5.Add( self.plt_textCtr3, 0, 0, 5 )
        sbSizer5.Add( self.m_button5, 0, 0, 5 )
        
        bSizer2.Add( sbSizer5, 0, 0, 5 )

        gSizer1 =            wx.GridSizer( 2, 2, 0, 0 )
        self.m_checkBox1=    wx.CheckBox( self, wx.ID_ANY, self.translate( u"Show Grid"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_checkBox3 =   wx.CheckBox( self, wx.ID_ANY, self.translate( u"View Cursor"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer1.Add( self.m_checkBox1, 0, wx.LEFT|wx.TOP, 5 )
        gSizer1.Add( self.m_checkBox3, 0, wx.LEFT|wx.TOP, 5 )

        #self.m_checkBox2 = wx.CheckBox( self, wx.ID_ANY, u"Legend", wx.DefaultPosition, wx.DefaultSize, 0 )
        #gSizer1.Add( self.m_checkBox2, 0, wx.ALL, 5 )

        bSizer2.Add( gSizer1, 0, 0, 5 )

        sbSizer10 =          wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, self.translate(u"X axis") ), wx.VERTICAL )
        bSizer51 =           wx.BoxSizer( wx.HORIZONTAL )
        self.m_staticText1=  wx.StaticText( self, wx.ID_ANY, self.translate(u"min"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl4 =   NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        self.m_staticText1.Wrap( -1 )
        bSizer51.Add( self.m_staticText1, 0, wx.ALL, 5 )
        bSizer51.Add( self.m_textCtrl4, 0, wx.ALL, 5 )
        
        self.m_staticText2=  wx.StaticText( self, wx.ID_ANY, self.translate(u"max"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl5=    NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        self.m_staticText2.Wrap( -1 )
        bSizer51.Add( self.m_staticText2, 0, wx.ALL, 5 )
        bSizer51.Add( self.m_textCtrl5, 0, wx.ALL, 5 )
        
        sbSizer10.Add( bSizer51, 1, wx.EXPAND, 5 )
        
        bSizer6 =             wx.BoxSizer( wx.HORIZONTAL )
        self.m_staticText281= wx.StaticText( self, wx.ID_ANY, self.translate(u"angle"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_spinCtrl2 =    wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 60,-1 ), wx.SP_ARROW_KEYS, -90, 90, 0 )
        self.m_staticText281.Wrap( -1 )
        bSizer6.Add( self.m_staticText281, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
        bSizer6.Add( self.m_spinCtrl2, 0, wx.ALL, 5 )
        
        sbSizer10.Add( bSizer6, 1, wx.EXPAND, 5 )
        
        bSizer2.Add( sbSizer10, 0, 0, 5 )
        
        sbSizer11 =          wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, self.translate(u"Y axis") ), wx.VERTICAL )
        bSizer7 =            wx.BoxSizer( wx.HORIZONTAL )
        self.m_staticText3=  wx.StaticText( self, wx.ID_ANY, self.translate(u"min"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl6 =   NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        self.m_staticText3.Wrap( -1 )
        bSizer7.Add( self.m_staticText3, 0, wx.ALL, 5 )
        bSizer7.Add( self.m_textCtrl6, 0, wx.ALL, 5 )
        
        self.m_staticText4=  wx.StaticText( self, wx.ID_ANY, self.translate(u"max"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl7 =   NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 40,-1 ), 0 )
        self.m_staticText4.Wrap( -1 )
        bSizer7.Add( self.m_staticText4, 0, wx.ALL, 5 )
        bSizer7.Add( self.m_textCtrl7, 0, wx.ALL, 5 )
        
        sbSizer11.Add( bSizer7, 1, wx.EXPAND, 5 )
        
        bSizer8 =              wx.BoxSizer( wx.HORIZONTAL )
        self.m_staticText291=  wx.StaticText( self, wx.ID_ANY, self.translate(u"angle"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_spinCtrl3 =     wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 60,-1 ), wx.SP_ARROW_KEYS, -90, 90, 0 )
        self.m_staticText291.Wrap( -1 )
        bSizer8.Add( self.m_staticText291, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        bSizer8.Add( self.m_spinCtrl3, 0, wx.ALL, 5 )
        
        sbSizer11.Add( bSizer8, 1, wx.EXPAND, 5 )
        
        bSizer2.Add( sbSizer11, 0, 0, 5 )
        
        sbSizer7 =            wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, self.translate(u"axis scale") ), wx.VERTICAL )
        gSizer2 =             wx.GridSizer( 0, 2, 0, 0 )
        self.m_staticText5=   wx.StaticText( self, wx.ID_ANY, self.translate(u"X axis"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6=   wx.StaticText( self, wx.ID_ANY, self.translate(u"Y axis"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        self.m_staticText6.Wrap( -1 )
        gSizer2.Add( self.m_staticText5, 0, wx.ALL, 5 )
        gSizer2.Add( self.m_staticText6, 0, wx.ALL, 5 )

        m_choice2Choices=     [ u"linear", u"symlog" ]
        self.m_choice2=       wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 69,-1 ), m_choice2Choices, 0 )
        self.m_choice2.SetSelection( 0 )
        gSizer2.Add( self.m_choice2, 0, wx.LEFT|wx.RIGHT, 5 )

        m_choice1Choices=     [ u"linear", u"symlog" ]
        self.m_choice1=       wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 69,-1 ), m_choice1Choices, 0 )
        self.m_choice1.SetSelection( 0 )
        gSizer2.Add( self.m_choice1, 0, wx.LEFT|wx.RIGHT, 5 )

        sbSizer7.Add( gSizer2, 0, 0, 5 )

        bSizer2.Add( sbSizer7, 0, 0, 5 )

        self.SetSizer( bSizer2 )
        self.Layout()
        bSizer2.Fit( self )
        # callbacks
        self._BindEvents()
        
    def _BindEvents( self):
        # scrolledWindow1
        self.plt_textCtr1.Bind( wx.EVT_TEXT,     self._TitleChange )
        self.plt_textCtr2.Bind( wx.EVT_TEXT,     self._xlabelChange )
        self.plt_textCtr3.Bind( wx.EVT_TEXT,     self._ylabelChange )        
        self.m_button3.Bind(    wx.EVT_BUTTON,   self._titleFontProp )
        self.m_button4.Bind(    wx.EVT_BUTTON,   self._xlabelFontProp )        
        self.m_button5.Bind(    wx.EVT_BUTTON,   self._ylabelFontProp )
        self.m_checkBox1.Bind(  wx.EVT_CHECKBOX, self._OnGrid )
        self.m_checkBox3.Bind(  wx.EVT_CHECKBOX, self._OnViewCursor )
        ##self.m_checkBox2.Bind( wx.EVT_CHECKBOX, self._OnLegend )# leggend callback
        self.m_textCtrl4.Bind(  wx.EVT_TEXT,     self._xminValue )
        self.m_textCtrl5.Bind(  wx.EVT_TEXT,     self._xmaxValue )
        self.m_textCtrl6.Bind(  wx.EVT_TEXT,     self._yminValue )
        self.m_textCtrl7.Bind(  wx.EVT_TEXT,     self._ymaxValue )
        self.m_spinCtrl2.Bind(  wx.EVT_SPINCTRL, self._xAngleChange )
        self.m_spinCtrl3.Bind(  wx.EVT_SPINCTRL, self._yAngleChange )
        self.m_choice2.Bind(    wx.EVT_CHOICE,   self._OnXaxisScale )
        self.m_choice1.Bind(    wx.EVT_CHOICE,   self._OnYaxisScale )
        
    def _setItems(self, parent):
        self.parent= parent
        parent._addLabels( parent.graphParams)
        if len( parent.graphParams['xtics']) != 0:
            self.parent.ca.set_xticklabels( parent.graphParams['xtics'])
        if len( parent.graphParams['ytics']) != 0:
            self.parent.ca.set_yticklabels( parent.graphParams['ytics'])
        self._updateLimits(None)
        
    def _Update(self, currAxes, evt= None):
        self._updateLimits( currAxes, evt)
        self._UpdateTiteLabels( currAxes, evt, redraw= False)
        self._UpdateAxisScale( currAxes, evt, )
        
    def _UpdateTiteLabels(self, currAxes, evt= None, **params):
        ca=     currAxes
        if ca == None:
            return
        redraw= True
        
        try:
            redraw= params['redraw']
        except KeyError:
            pass
        
        title=  ca.get_title()
        xlabel= ca.get_xlabel()
        ylabel= ca.get_ylabel()
        gridState= ca._gridOn
        # getting states of the variables with the control actual ones
        actaulTitle=  self.plt_textCtr1.GetLabel()
        actualXlabel= self.plt_textCtr2.GetLabel()
        actualYlabel= self.plt_textCtr3.GetLabel()
        actualGridState= self.m_checkBox1.Value
        # updating the controls
        self.Parent.ca= ca
        if title != actaulTitle:
            self.plt_textCtr1.SetLabel( title)
        if xlabel != actualXlabel:
            self.plt_textCtr2.SetLabel( xlabel)
        if ylabel != actualYlabel:
            self.plt_textCtr3.SetLabel( ylabel)
        if gridState != actualGridState:
            self.m_checkBox1.Value = gridState
        
    def _updateLimits(self, currAxes, evt = None):
        ca= currAxes
        if ca == None:
            return
        xlim= ca.get_xlim()
        ylim= ca.get_ylim()
        self.Parent.ca= ca
        # changing the limits with current punctuation symbol
        dp= wx.GetApp().DECIMAL_POINT
        xlim= [x.__str__().replace('.', dp) for x in xlim]
        ylim= [y.__str__().replace('.', dp) for y in ylim]
        # setting the limits of the axis to the buttons
        if self.m_textCtrl4.GetLabel() != xlim[0]:
            self.m_textCtrl4.SetLabel(u''+ xlim[0])
        if self.m_textCtrl5.GetLabel() != xlim[-1]:
            self.m_textCtrl5.SetLabel(u''+ xlim[-1])
        if self.m_textCtrl6.GetLabel() != ylim[0]:
            self.m_textCtrl6.SetLabel(u''+ ylim[0])
        if self.m_textCtrl7.GetLabel() != ylim[-1]:
            self.m_textCtrl7.SetLabel(u''+ ylim[-1])
    
    def _UpdateAxisScale(self, currAxes, evt):
        if currAxes == None:
            return
        
        ca= currAxes
        # readin the scales of the current axes
        xscale= ca.get_xscale( )
        yscale= ca.get_yscale( )
        # comparing the values with the graphic ones
        posible= ["linear", "symlog"]
        oldXscale= posible[self.m_choice2.GetSelection()]
        oldYscale= posible[self.m_choice1.GetSelection()]
        # updating the control values symlog
        posible= {"linear": 0, "symlog": 1}
        try:
            if xscale != oldXscale:
                self.m_choice2.SetSelection( posible[xscale])
            
            if yscale != oldYscale:
                self.m_choice1.SetSelection( posible[yscale])
        except KeyError:
            pass
            
    def _TitleChange( self, evt ):
        if self.Parent.ca ==None:
            return
        ca= self.Parent.ca
        if evt.GetString() == self.plt_textCtr1.GetLabel():
            return
        ca.set_title(evt.GetString())
        self.figpanel.canvas.draw()

        #self.log.write('Title= ' + "'" + self.figpanel.gca().get_title().__str__()+ "'", False)
        #self.log.write('plt.gca().set_title(Title)', False)
        
    def _xlabelChange( self, evt ):
        if self.Parent.ca ==None:
            return
        
        ca= self.Parent.ca
        if evt.GetString() == self.plt_textCtr2.GetLabel():
            return
        
        ca.set_xlabel(evt.GetString())
        self.figpanel.canvas.draw()
        #self.log.write('xlabel= ' + "'" +  self.figpanel.gca().get_xlabel().__str__()+ "'" , False)
        #self.log.write('plt.gca().set_xlabel(xlabel)', False)

    def _ylabelChange( self, evt ):
        if self.Parent.ca ==None:
            return
        
        ca= self.Parent.ca
        if evt.GetString() == self.plt_textCtr3.GetLabel():
            return
        ca.set_ylabel(evt.GetString())
        self.figpanel.canvas.draw()
        #self.log.write('ylabel= ' + "'" + self.figpanel.gca().get_ylabel().__str__()+ "'" , False)
        #self.log.write('plt.gca().set_xlabel(ylabel)', False)
    
    def _titleFontProp( self, evt ):
        if self.Parent.ca ==None:
            return
        
        ca= self.Parent.ca
        fontprop= fontDialog(self)
        currtitle = ca.get_title()
        ca.set_title(currtitle,fontprop)
        self.figpanel.canvas.draw()
        
    def _xlabelFontProp( self, evt ):
        if self.Parent.ca ==None:
            return
        
        ca= self.Parent.ca
        fontprop= fontDialog(self)
        currtitle = ca.get_xlabel()
        ca.set_xlabel(currtitle,fontprop)
        self.figpanel.canvas.draw()

    def _ylabelFontProp( self, evt ):
        if self.Parent.ca ==None:
            return
        
        ca= self.Parent.ca
        fontprop= fontDialog(self)
        currtitle = ca.get_ylabel()
        ca.set_ylabel(currtitle,fontprop)
        self.figpanel.canvas.draw()
        
    def _OnGrid( self, evt ):
        if self.Parent.ca ==None:
            return
        
        ca= self.Parent.ca
        self.log.write('# changing grid state', False)
        value = evt.Checked()
        ca.grid(value)
        ## updating the state of the grid matplotlib state
        ca._gridOn= value 
        self.figpanel.canvas.draw()
        self.log.write('plt.gca().grid('+value.__str__()+')', False)
        
    def _OnViewCursor( self, evt ):
        # verify the cursor property created with
        # connectCursor
        if not hasattr(self.Parent.Parent,'cursor'):
            return
        
        value = evt.Checked()
        if not value:
            self.Parent.Parent.statusbar.SetStatusText(( ""), 1)

        self.Parent.Parent.cursor.horizOn = value
        self.Parent.Parent.cursor.vertOn = value
        self.figpanel.canvas.draw()
    
    def _xminValue( self, evt ):
        evt.Skip()
        if self.Parent.ca == None:
            return
        ca = self.Parent.ca
        
        #self.log.write('# changing x axis min value', False)
        axisValue= ca.get_xbound()
        #self.log.write('axisValue= plt.gca().get_xbound()', False)
        value= self.m_textCtrl4.GetValue()
        if value== None:
            return
        
        if axisValue[0] == value:
            return
        ca.set_xbound((value, axisValue[1]))
        self.figpanel.canvas.draw()
        # self.log.write('plt.gca().set_xbound((float('+evt.GetString().__str__()+'),axisValue[1]))', False)

    def _xmaxValue( self, evt ):
        evt.Skip()
        if self.Parent.ca == None:
            return
        ca = self.Parent.ca
        
        #self.log.write('# changing x axis max value', False)
        axisValue = ca.get_xbound()
        value= self.m_textCtrl5.GetValue()
        if value== None:
            return
        
        if axisValue[1] == value:
            return
        ca.set_xbound((axisValue[0], value))
        self.figpanel.canvas.draw()
        #self.log.write('plt.gca().set_xbound((axisValue[0],float('+evt.GetString().__str__()+')))', False)

    def _yminValue( self, evt ):
        evt.Skip()
        if self.Parent.ca == None:
            return
        ca = self.Parent.ca
        
        #self.log.write('# changing y axis min value', False)
        axisValue = ca.get_ybound()
        #self.log.write('axisValue= plt.gca().get_ybound()', False)

        value= self.m_textCtrl6.GetValue()
        if value== None:
            return
        
        if axisValue[0] == value:
            return
        
        ca.set_ybound((value, axisValue[1]))
        self.figpanel.canvas.draw()
        #self.log.write('plt.gca().set_ybound((float('+evt.GetString().__str__()+'),axisValue[1]))', False)

    def _ymaxValue( self, evt ):
        evt.Skip()
        if self.Parent.ca == None:
            return
        
        ca = self.Parent.ca
        #self.log.write('# changing y axis max value', False)
        axisValue = ca.get_ybound()
        #self.log.write('axisValue= plt.gca().get_ybound()', False)
        value= self.m_textCtrl7.GetValue()
        if value== None:
            return
        
        if axisValue[1] == value:
            return
        
        ca.set_ybound((axisValue[0], value))
        self.figpanel.canvas.draw()
        #self.log.write('plt.gca().set_ybound((axisValue[0],float('+evt.GetString().__str__()+')))', False)
        
    def _xAngleChange( self, evt):
        if self.Parent.ca == None:
            return
        
        ca = self.Parent.ca
        labels = ca.get_xticklabels()
        currFontSize= ca.xaxis.get_label().get_fontsize()
        setp( labels, rotation= evt.GetSelection(), fontsize= currFontSize)
        self.figpanel.canvas.draw()
    
    def _yAngleChange( self, evt):
        if self.Parent.ca == None:
            return
        
        ca = self.Parent.ca
        labels = ca.get_yticklabels()
        currFontSize= currFontSize= ca.yaxis.get_label().get_fontsize()
        setp( labels, rotation= evt.GetSelection(), fontsize= currFontSize)
        self.figpanel.canvas.draw()
    
    def _OnXaxisScale( self, evt ):
        if self.Parent.ca == None:
            return
        
        ca = self.Parent.ca
        self.log.write('# changing x axis scale', False)
        value = 'linear'
        if evt.Selection == 1:
            value = 'symlog'
        ca.set_xscale(value)
        self.figpanel.canvas.draw()
        self.log.write('plt.gca().set_xscale('+ "'" + value.__str__()+ "'" +')', False)

    def _OnYaxisScale( self, evt ):
        if self.Parent.ca == None:
            return
        
        ca = self.Parent.ca        
        self.log.write('# changing y axis scale', False)
        value = 'linear'
        if evt.Selection == 1:
            value = 'symlog'
        ca.set_yscale(value)
        self.figpanel.canvas.draw()
        self.log.write('plt.gca().set_yscale('+ "'" + value.__str__()+ "'" +')', False)
        
        
class scrolled2(wx.ScrolledWindow):    
    def __init__( self, *args, **params):
        wx.ScrolledWindow.__init__(self, *args[1:], **params)
        self.figpanel= self.Parent.Parent.figpanel
        self.log= self.Parent.Parent.log
        try:
            self.translate = wx.GetApp().translate
        except AttributeError:
            self.translate= translate
        graphParams= args[0]
        self.gca= self.Parent.Parent.gca
        
        if params.has_key('parent'):
            parent= params['parent']
        else:
            parent = args[1]
            
        ##self = wx.ScrolledWindow( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
        self.SetScrollRate( 5, 5 )
        bSizer21 = wx.BoxSizer( wx.VERTICAL )

        sbSizer8 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, self.translate( u"Choose a line") ), wx.VERTICAL )

        m_listBox1Choices = []
        self.m_listBox1 = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 130,80 ), m_listBox1Choices, 0 )
        sbSizer8.Add( self.m_listBox1, 0, wx.ALL, 5 )

        bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_button87 = wx.Button( self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button87.SetMinSize( wx.Size( 20,-1 ) )

        bSizer5.Add( self.m_button87, 0, wx.LEFT|wx.RIGHT, 5 )

        self.m_button41 = wx.Button( self, wx.ID_ANY, self.translate( u"Refresh lines"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer5.Add( self.m_button41, 0, wx.ALIGN_RIGHT|wx.LEFT, 5 )

        sbSizer8.Add( bSizer5, 1, wx.EXPAND, 5 )

        bSizer21.Add( sbSizer8, 0, 0, 5 )

        sbSizer71 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, self.translate( u"Some Properties") ), wx.VERTICAL )

        self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, self.translate( u"Name"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText11.Wrap( -1 )
        sbSizer71.Add( self.m_staticText11, 0, wx.LEFT, 5 )

        self.plt_textCtr8 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 130,-1 ), 0 )
        self.plt_textCtr8.Enable( False )

        sbSizer71.Add( self.plt_textCtr8, 0, wx.BOTTOM|wx.LEFT|wx.TOP, 5 )

        fgSizer2 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer2.SetFlexibleDirection( wx.BOTH )
        fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        m_choice7Choices = []
        self.m_choice7 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 60,-1 ), m_choice7Choices, 0 )
        self.m_choice7.SetSelection( 0 )
        fgSizer2.Add( self.m_choice7, 0, wx.ALL, 5 )

        self.m_staticText12 = wx.StaticText( self, wx.ID_ANY, self.translate( u"Line Width"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText12.Wrap( -1 )
        fgSizer2.Add( self.m_staticText12, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_button12 = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 60,-1 ), 0 )
        fgSizer2.Add( self.m_button12, 0, wx.ALL, 5 )

        self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, self.translate( u"Line Colour"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )
        fgSizer2.Add( self.m_staticText7, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        m_choice4Choices = []
        self.m_choice4 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 60,-1 ), m_choice4Choices, 0 )
        self.m_choice4.SetSelection( 0 )
        fgSizer2.Add( self.m_choice4, 0, wx.ALL, 5 )

        self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Line Style"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText8.Wrap( -1 )
        fgSizer2.Add( self.m_staticText8, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        m_choice6Choices = []
        self.m_choice6 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 60,-1 ), m_choice6Choices, 0 )
        self.m_choice6.SetSelection( 0 )
        fgSizer2.Add( self.m_choice6, 0, wx.ALL, 5 )

        self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Marker Style"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText10.Wrap( -1 )
        fgSizer2.Add( self.m_staticText10, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        m_choice8Choices = []
        self.m_choice8 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 60,-1 ), m_choice8Choices, 0 )
        self.m_choice8.SetSelection( 0 )
        fgSizer2.Add( self.m_choice8, 0, wx.ALL, 5 )

        self.m_staticText13 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Marker Size"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText13.Wrap( -1 )
        fgSizer2.Add( self.m_staticText13, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        sbSizer71.Add( fgSizer2, 1, wx.EXPAND, 5 )

        self.m_checkBox4 = wx.CheckBox( self, wx.ID_ANY, self.translate(u"Shown"), wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer71.Add( self.m_checkBox4, 0, wx.ALL, 5 )

        bSizer21.Add( sbSizer71, 0, 0, 5 )

        sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, self.translate(u"Add ReferenceLine") ), wx.VERTICAL )

        fgSizer1 = wx.FlexGridSizer( 0, 3, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.HorLineTxtCtrl = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), 0 )
        fgSizer1.Add( self.HorLineTxtCtrl, 0, wx.ALL, 5 )

        self.m_button51 = wx.Button( self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        fgSizer1.Add( self.m_button51, 0, wx.TOP, 5 )

        self.m_staticText131 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Horizontal"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText131.Wrap( -1 )
        fgSizer1.Add( self.m_staticText131, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.HorVerTxtCtrl = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), 0 )
        fgSizer1.Add( self.HorVerTxtCtrl, 0, wx.ALL, 5 )

        self.m_button511 = wx.Button( self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        fgSizer1.Add( self.m_button511, 0, wx.TOP, 5 )

        self.m_staticText14 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Vertical"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText14.Wrap( -1 )
        fgSizer1.Add( self.m_staticText14, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        sbSizer9.Add( fgSizer1, 1, wx.EXPAND, 5 )

        bSizer21.Add( sbSizer9, 0, 0, 5 )

        self.SetSizer( bSizer21 )
        self.Layout()
        bSizer21.Fit( self )
        self._OnRefreshLines( None)
        self._BindEvents()
        
    def _BindEvents( self):
        self.m_listBox1.Bind(   wx.EVT_LISTBOX,  self._OnListLinesChange )
        self.m_button87.Bind(   wx.EVT_BUTTON,   self._OnLineDel )
        self.m_button41.Bind(   wx.EVT_BUTTON,   self._OnRefreshLines )
        self.plt_textCtr8.Bind( wx.EVT_TEXT_ENTER, self._OnLineNameChange )
        self.m_choice7.Bind(    wx.EVT_CHOICE,   self._OnLineWidthChange )
        self.m_button12.Bind(   wx.EVT_BUTTON,   self._OnLineColourChange )
        self.m_choice4.Bind(    wx.EVT_CHOICE,   self._OnLineStyleChange )
        self.m_choice6.Bind(    wx.EVT_CHOICE,   self._OnLineMarkerStyleChange )
        self.m_choice8.Bind(    wx.EVT_CHOICE,   self._OnLineMarkerSizeChange )
        self.m_checkBox4.Bind(  wx.EVT_CHECKBOX, self._OnLineVisibleChange )
        #self.HorLineTxtCtrl.Bind( wx.EVT_TEXT,   self._OnTxtRefLineHorzChange )
        self.m_button51.Bind(   wx.EVT_BUTTON,   self._OnAddRefHorzLine )
        #self.HorVerTxtCtrl.Bind( wx.EVT_TEXT,    self._OnTxtRefLineVerChange )
        self.m_button511.Bind(  wx.EVT_BUTTON,   self._OnAddRefVertLine )
            
    def _setItems(self):
        if self.Parent.ca == None:
            return
        lineListNames= [line.get_label() for line in self.Parent.ca.get_lines()]
        self.m_listBox1.SetItems( lineListNames)
        self.m_choice7.SetItems( lineSizes)
        self.m_choice4.SetItems( lineStyles)
        self.m_choice6.SetItems( markerStyles)
        self.m_choice8.SetItems( markerSizes)
    
    def _updateLineSelectionPane(self, evt):
        if len( self.m_listBox1.GetItems()) == 0:
            self.plt_textCtr8.SetValue("")
            return
        if self.m_listBox1.GetSelection() == -1:
            self.plt_textCtr8.SetValue("")
            return
        selectedLine= self.Parent.ca.get_lines()[self.m_listBox1.GetSelection()]
        lineName = selectedLine.get_label()
        lineWidht= float(selectedLine.get_linewidth())
        lineColour= selectedLine.get_color()
        lineStyle = selectedLine.get_linestyle()
        markerStyle= selectedLine.get_marker()
        markerSize= float(selectedLine.get_markersize())
        visible = selectedLine.get_visible()
        # pass all data an update the notebookpane
        self.plt_textCtr8.SetValue(lineName)
        for pos,value in enumerate(self.m_choice7.GetItems()):
            if float(value) == lineWidht:
                self.m_choice7.SetSelection(pos)
                break
        #for pos,value in enumerate(self.m_choice3.GetItems()):
            #if value == lineColour:
                #self.m_choice3.SetSelection(pos)
                #break
        for pos,value in enumerate(self.m_choice4.GetItems()):
            if value == lineStyle:
                self.m_choice4.SetSelection(pos)
                break
        for pos,value in enumerate(self.m_choice6.GetItems()):
            if value == markerStyle:
                self.m_choice6.SetSelection(pos)
                break
        for pos,value in enumerate(self.m_choice8.GetItems()):
            if float(value) == markerSize:
                self.m_choice8.SetSelection(pos)
                break
        self.m_checkBox4.SetValue(visible)
        
    def _OnListLinesChange( self, evt ):
        self._updateLineSelectionPane(evt)
        
    def _OnLineDel(self,event):
        if len(self.Parent.ca.get_lines())== 0:
            return
        selectedLine= self.Parent.ca.get_lines()[self.m_listBox1.GetSelection()]
        selectedLine.remove()
        # se actualiza la linea seleccionada
        self._OnRefreshLines(None)
        self.figpanel.canvas.draw()
        
    def _OnRefreshLines( self, evt ):
        if self.Parent.ca== None:
            return
        if len(self.Parent.ca.get_lines())== 0:
            self.m_listBox1.SetItems([])
            return
        lineListNames= [line.get_label() for line in self.Parent.ca.get_lines()]
        self.m_listBox1.SetItems(lineListNames)
        self.m_listBox1.SetSelection(0)
        self._updateLineSelectionPane(self.m_listBox1)
        
    def _OnLineNameChange( self, evt ):
        # pendeinte por implementar.. el evento wx.EVT_TEXT_TEXTENTER
        evt.Skip()
        
    def _OnLineWidthChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        newWidth= float(evt.String)
        selectedLine= self.Parent.ca.get_lines()[self.m_listBox1.GetSelection()]
        selectedLine.set_linewidth(newWidth)
        self.figpanel.canvas.draw()
        
    def _OnLineColourChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            # If the user selected OK, then the dialog's wx.ColourData will
            # contain valid information. Fetch the data ...
            data = dlg.GetColourData()
        else:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.Parent.ca.get_lines()[actualLineNumber]
        colors = [getattr(data.Colour,param)/float(255) for param in ['red','green','blue','alpha']]
        lineSelected.set_color(colors)
        self.figpanel.canvas.draw()
        
    def _OnLineStyleChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.Parent.ca.get_lines()[actualLineNumber]
        newStyle = evt.GetString()
        lineSelected.set_linestyle(newStyle)
        self.figpanel.canvas.draw()

    def _OnLineMarkerStyleChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.Parent.ca.get_lines()[actualLineNumber]

        newMarkerStyle = evt.GetString()
        lineSelected.set_marker(newMarkerStyle)

        self.figpanel.canvas.draw()

    def _OnLineMarkerSizeChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.Parent.ca.get_lines()[actualLineNumber]

        newMarkerSize = float(evt.GetString())
        lineSelected.set_markersize(newMarkerSize)

        self.figpanel.canvas.draw()

    def _OnLineVisibleChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.Parent.ca.get_lines()[actualLineNumber]
        visible = evt.Checked()
        lineSelected.set_visible(visible)
        self.figpanel.canvas.draw()

    def _OnAddRefHorzLine( self, evt, **params ):
        self.log.write('# adding reference horizontal line', False)
        if params.has_key('ypos'):
            ypos = params.pop('ypos')
            self.Parent.ca.hold(True)
            #self.log.write('plt.gca().hold(True)', False)

            line= self.Parent.ca.axhline(ypos)
            self.log.write('line= pltgca().axhline('+ypos.__str__()+')', False)
            self.Parent.ca.hold(False)
            #self.log.write('plt.gca().hold(False)', False)
        else:
            try:
                ypos= self.HorLineTxtCtrl.GetValue()
                if ypos== None:
                    return
                self.Parent.ca.hold(True)
                self.log.write('plt.gca().hold(True)', False)
                line= self.Parent.ca.axhline(ypos)
                self.log.write('plt.gca().axhline('+ypos.__str__()+')', False)
                self.Parent.ca.hold(False)
                self.log.write('plt.gca().hold(False)', False)
                self.HorLineTxtCtrl.SetValue('')
                self._OnRefreshLines(None)
            except:
                return
        if params.has_key('color'):
            line.set_color(params['color'])
            self.log.write('line.set_color('+"'"+params['color'].__str__()+"'"+')', False)
        self.figpanel.canvas.draw()
        #self.log.write('plt.draw()',False)

    def _OnAddRefVertLine( self, evt ):
        self.log.write('# adding reference vertical line', False)
        xpos= self.HorVerTxtCtrl.GetValue()
        if xpos == None:
            return
        
        self.Parent.ca.hold(True)
        self.log.write('plt.gca().hold(True)', False)
        self.Parent.ca.axvline(xpos)
        self.log.write('plt.gca().axvline('+xpos.__str__()+')', False)
        self.gca().hold(False)
        self.log.write('plt.gca().hold(False)', False)
        self.figpanel.canvas.draw()
        self.HorVerTxtCtrl.SetValue('')
        self._OnRefreshLines(None)
        self.figpanel.canvas.draw()

class scrolled3(wx.ScrolledWindow):    
    def __init__( self, *args, **params):
        wx.ScrolledWindow.__init__(self, *args[1:], **params)
        self.figpanel= self.Parent.Parent.figpanel
        self.log= self.Parent.Parent.log
        try:
            self.translate = wx.GetApp().translate
        except AttributeError:
            self.translate= translate
        graphParams= args[0]
        self.gca= self.Parent.Parent.gca
        
        if params.has_key('parent'):
            parent= params['parent']
        else:
            parent = args[1]
        
        self.SetScrollRate( 5, 5 )
        bSizer3 = wx.BoxSizer( wx.VERTICAL )

        sbSizer15 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, self.translate( u"Choose a patchs") ), wx.VERTICAL )

        patchListBoxChoices = []
        self.patchListBox = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, patchListBoxChoices, 0 )
        self.patchListBox.SetMinSize( wx.Size( 140,60 ) )

        sbSizer15.Add( self.patchListBox, 0, wx.ALL, 5 )

        fgSizer6 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer6.SetFlexibleDirection( wx.BOTH )
        fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_button9 = wx.Button( self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, wx.BU_BOTTOM )
        self.m_button9.SetMinSize( wx.Size( 20,-1 ) )

        fgSizer6.Add( self.m_button9, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        self.m_button11 = wx.Button( self, wx.ID_ANY, self.translate(u"Refresh Patchs"), wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer6.Add( self.m_button11, 0, wx.LEFT, 5 )

        sbSizer15.Add( fgSizer6, 1, wx.EXPAND, 5 )

        bSizer3.Add( sbSizer15, 0, 0, 5 )

        sbSizer16 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, self.translate(u"Some Properties") ), wx.VERTICAL )

        self.m_staticText28 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Patch Name"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText28.Wrap( -1 )
        sbSizer16.Add( self.m_staticText28, 0, wx.ALL, 5 )

        self.textCtrlPatchName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.textCtrlPatchName.Enable( False )

        sbSizer16.Add( self.textCtrlPatchName, 0, wx.ALL, 5 )

        fgSizer7 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer7.SetFlexibleDirection( wx.BOTH )
        fgSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_button13 = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
        fgSizer7.Add( self.m_button13, 0, wx.ALL, 5 )

        self.m_staticText29 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Face Colour"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText29.Wrap( -1 )
        fgSizer7.Add( self.m_staticText29, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        m_choice14Choices = []
        self.m_choice14 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 70,-1 ), m_choice14Choices, 0 )
        self.m_choice14.SetSelection( 0 )
        fgSizer7.Add( self.m_choice14, 0, wx.ALL, 5 )

        self.m_staticText30 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Alpha"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText30.Wrap( -1 )
        fgSizer7.Add( self.m_staticText30, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        sbSizer16.Add( fgSizer7, 1, wx.EXPAND, 5 )

        bSizer3.Add( sbSizer16, 0, 0, 5 )

        sbSizer12 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, self.translate(u"add an span") ), wx.VERTICAL )

        sbSizer13 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )

        fgSizer4 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer4.SetFlexibleDirection( wx.BOTH )
        fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText15 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Horizontal"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText15.Wrap( -1 )
        fgSizer4.Add( self.m_staticText15, 0, wx.ALL, 5 )

        self.m_button7 = wx.Button( self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button7.SetMinSize( wx.Size( 20,-1 ) )

        fgSizer4.Add( self.m_button7, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, 5 )

        sbSizer13.Add( fgSizer4, 0, 0, 5 )

        fgSizer3 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer3.SetFlexibleDirection( wx.BOTH )
        fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.plt_textCtr11 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.plt_textCtr11.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer3.Add( self.plt_textCtr11, 0, wx.ALL, 5 )

        self.m_staticText17 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Y axis position 1"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText17.Wrap( -1 )
        fgSizer3.Add( self.m_staticText17, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        self.plt_textCtr12 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.plt_textCtr12.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer3.Add( self.plt_textCtr12, 0, wx.ALL, 5 )

        self.m_staticText16 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Y axis position 2"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText16.Wrap( -1 )
        fgSizer3.Add( self.m_staticText16, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_choice81Choices = []
        self.m_choice81 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice81Choices, 0 )
        self.m_choice81.SetSelection( 0 )
        self.m_choice81.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer3.Add( self.m_choice81, 0, wx.ALL, 5 )

        self.m_staticText22 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Face Colour"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText22.Wrap( -1 )
        fgSizer3.Add( self.m_staticText22, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_choice12Choices = []
        self.m_choice12 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice12Choices, 0 )
        self.m_choice12.SetSelection( 0 )
        self.m_choice12.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer3.Add( self.m_choice12, 0, wx.ALL, 5 )

        self.m_staticText26 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Alpha"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText26.Wrap( -1 )
        fgSizer3.Add( self.m_staticText26, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )


        sbSizer13.Add( fgSizer3, 0, 0, 5 )


        sbSizer12.Add( sbSizer13, 0, 0, 5 )

        sbSizer14 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )

        fgSizer5 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer5.SetFlexibleDirection( wx.BOTH )
        fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText19 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Vertical"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText19.Wrap( -1 )
        fgSizer5.Add( self.m_staticText19, 0, wx.ALL, 5 )

        self.m_button8 = wx.Button( self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button8.SetMinSize( wx.Size( 20,-1 ) )

        fgSizer5.Add( self.m_button8, 0, wx.ALIGN_CENTER_VERTICAL, 5 )


        sbSizer14.Add( fgSizer5, 0, 0, 5 )

        gSizer3 = wx.FlexGridSizer( 0, 2, 0, 0 )
        gSizer3.SetFlexibleDirection( wx.BOTH )
        gSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.plt_textCtr13 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.plt_textCtr13.SetMinSize( wx.Size( 60,-1 ) )

        gSizer3.Add( self.plt_textCtr13, 0, wx.ALL, 5 )

        self.m_staticText20 = wx.StaticText( self, wx.ID_ANY, self.translate(u"X axis position 1"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText20.Wrap( -1 )
        gSizer3.Add( self.m_staticText20, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        self.plt_textCtr14 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.plt_textCtr14.SetMinSize( wx.Size( 60,-1 ) )

        gSizer3.Add( self.plt_textCtr14, 0, wx.ALL, 5 )

        self.m_staticText21 = wx.StaticText( self, wx.ID_ANY, self.translate(u"X axis position 2"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText21.Wrap( -1 )
        gSizer3.Add( self.m_staticText21, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_choice10Choices = []
        self.m_choice10 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice10Choices, 0 )
        self.m_choice10.SetSelection( 0 )
        self.m_choice10.SetMinSize( wx.Size( 60,-1 ) )

        gSizer3.Add( self.m_choice10, 0, wx.ALL, 5 )

        self.m_staticText24 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Face Colour"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText24.Wrap( -1 )
        gSizer3.Add( self.m_staticText24, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_choice11Choices = []
        self.m_choice11 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice11Choices, 0 )
        self.m_choice11.SetSelection( 0 )
        self.m_choice11.SetMinSize( wx.Size( 60,-1 ) )

        gSizer3.Add( self.m_choice11, 0, wx.ALL, 5 )

        self.m_staticText25 = wx.StaticText( self, wx.ID_ANY, self.translate(u"Alpha"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText25.Wrap( -1 )
        gSizer3.Add( self.m_staticText25, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        sbSizer14.Add( gSizer3, 0, 0, 5 )

        sbSizer12.Add( sbSizer14, 0, 0, 5 )

        bSizer3.Add( sbSizer12, 0, 0, 5 )

        self.SetSizer( bSizer3 )
        self.Layout()
        bSizer3.Fit( self )
        self._patchListboxUpdate()
        self._BindEvents()
        
    def _BindEvents( self):
        self.patchListBox.Bind(  wx.EVT_LISTBOX, self._OnPatchListboxChange )
        self.m_button9.Bind(     wx.EVT_BUTTON,  self._OnDelPatch )
        self.m_button13.Bind(    wx.EVT_BUTTON,  self._OnPatchFaceColorChange )
        self.m_choice14.Bind(    wx.EVT_CHOICE,  self._OnPatchAlphaChange )
        self.m_button7.Bind(     wx.EVT_BUTTON,  self._OnAddHorzSpan )
        self.m_button8.Bind(     wx.EVT_BUTTON,  self._OnAddVerSpan )
        self.m_button11.Bind(    wx.EVT_BUTTON,  self._patchListboxUpdate )
        
    def _setItems( self):
        self.m_choice14.SetItems(alpha)
        self.m_choice81.SetItems(faceColors)
        self.m_choice12.SetItems(alpha)
        self.m_choice10.SetItems(faceColors)
        self.m_choice11.SetItems(alpha)
        self.m_choice14.SetSelection(0)
        self.m_choice81.SetSelection(0)
        self.m_choice12.SetSelection(0)
        self.m_choice10.SetSelection(0)
        self.m_choice11.SetSelection(0)
        
    def _OnPatchListboxChange( self, event):
        if len(self.patchListBox.GetItems()) == 0:
            self.textCtrlPatchName.SetValue(u"")
            return
        if self.patchListBox.GetSelection() == -1:
            self.textCtrlPatchName.SetValue(u"")
            return
        selectedPatch= self.patchListBox.GetItems()[self.patchListBox.GetSelection()]
        currPatch= None
        for patch in self.Parent.ca.patches:
            if str(patch.get_gid()) == selectedPatch:
                currPatch= patch
                break
        if currPatch == None:
            # se actualiza el patch actual
            self._patchListboxUpdate()
            return
        Alpha = str(currPatch.get_alpha())
        faceColor = currPatch.get_facecolor()
        name = str(currPatch.get_gid())
        self.textCtrlPatchName.SetValue(name)
        for pos,value in enumerate(self.m_choice14.GetItems()):
            if value == Alpha:
                self.m_choice14.SetSelection(pos)
                break
        #for pos,value in enumerate(self.m_choice13.GetItems()):
            #if value == faceColor:
                #self.m_choice13.SetSelection(pos)
                #break

    def _OnAddHorzSpan( self, event):
        self.log.write('# adding horizontal span', False)
        pos1 = self.plt_textCtr11.GetValue()
        pos2 = self.plt_textCtr12.GetValue()
        if pos1 == None or pos2 == None:
            return
        
        self.log.write( 'pos1= ' + pos1.__str__(), False)
        self.log.write( 'pos2= ' + pos2.__str__(), False)

        faceColor= self.m_choice81.GetItems()[self.m_choice81.GetSelection()]
        self.log.write( 'faceColor= '+"'"+faceColor.__str__()+"'", False)

        Alpha= float(self.m_choice12.GetItems()[self.m_choice12.GetSelection()])
        self.log.write( 'Alpha= '+Alpha.__str__(), False)

        patch= self.Parent.ca.axhspan( pos1, pos2, facecolor = faceColor, alpha = Alpha)
        self.log.write( 'patch= plt.gca().axhspan(pos1,pos2, facecolor= faceColor, alpha= Alpha)', False)
        patch.set_gid(wx.NewId())
        self._patchListboxUpdate()
        self.figpanel.canvas.draw()

    def _OnAddVerSpan( self, event):
        self.log.write('# adding vertical span', False)
        pos1 = self.plt_textCtr13.GetValue()
        pos2 = self.plt_textCtr14.GetValue()
        try:
            pos1= float(pos1)
            pos2= float(pos2)
        except:
            return
        self.log.write('pos1= ' + pos1.__str__(), False)
        self.log.write('pos2= ' + pos2.__str__(), False)

        faceColor= self.m_choice10.GetItems()[self.m_choice10.GetSelection()]
        self.log.write('faceColor= '+"'"+faceColor.__str__()+"'", False)

        Alpha= str(self.m_choice11.GetItems()[self.m_choice11.GetSelection()])
        self.log.write('Alpha= '+Alpha.__str__(), False)

        patch= self.Parent.ca.axvspan(pos1,pos2,facecolor= faceColor, alpha= Alpha)
        self.log.write('patch= plt.gca().axvspan(pos1,pos2,facecolor= faceColor, alpha= Alpha)', False)
        patch.set_gid(wx.NewId())
        self._patchListboxUpdate()
        self.figpanel.canvas.draw()

    def _patchListboxUpdate(self, *args):
        # se lista todos los patch
        if self.Parent.ca== None:
            return
        patches = self.Parent.ca.patches
        if len(patches) == 0:
            self.patchListBox.SetItems([])
        # se agrega un id para los patches que no lo tengan
        for patch in patches:
            if patch.get_gid() == None:
                patch.set_gid(wx.NewId())
        # se crea un listado con los nombres de los patches
        patches= [str(patch.get_gid()) for patch in patches]
        # se acutaliza el listado
        self.patchListBox.SetItems(patches)
        # se actualiza el frame
        if len(patches) > 0:
            self.patchListBox.SetSelection(0)
        self._OnPatchListboxChange(None)

    def _OnDelPatch( self, event):
        items = self.patchListBox.GetItems()
        if len(items) == 0:
            return
        selected = self.patchListBox.GetSelection()
        if selected == -1:
            return
        selectedPatch = items[selected]
        for patch in self.Parent.ca.patches:
            if str(patch.get_gid()) == selectedPatch:
                patch.remove()
                break
        if len(items) > 0:
            self.patchListBox.SetSelection(0)
        self._patchListboxUpdate()
        self.figpanel.canvas.draw()

    def _OnPatchFaceColorChange( self, event):
        items= self.patchListBox.GetItems()
        if len(items) == 0:
            return
        selected = self.patchListBox.GetSelection()
        if  selected == -1:
            return
        selectedPatch= self.patchListBox.GetItems()[self.patchListBox.GetSelection()]
        currPatch= None
        for patch in self.Parent.ca.patches:
            if str(patch.get_gid()) == selectedPatch:
                currPatch= patch
                break
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            # If the user selected OK, then the dialog's wx.ColourData will
            # contain valid information. Fetch the data ...
            data = dlg.GetColourData()
        else:
            return
        actualLineNumber= self.patchListBox.GetSelection() # m_listBox1
        lineSelected = self.gca().get_lines()[actualLineNumber]
        colors = [getattr(data.Colour,param)/float(255) for param in ['red','green','blue','alpha']]
        currPatch.set_facecolor(colors)
        self.figpanel.canvas.draw()

    def _OnPatchAlphaChange( self, event):
        items= self.patchListBox.GetItems()
        if len(items) == 0:
            return
        selected = self.patchListBox.GetSelection()
        if  selected == -1:
            return
        selectedPatch= self.patchListBox.GetItems()[self.patchListBox.GetSelection()]
        currPatch= None
        for patch in self.Parent.ca.patches:
            if str(patch.get_gid()) == selectedPatch:
                currPatch= patch
                break
        alpha = float(self.m_choice14.GetItems()[self.m_choice14.GetSelection()])
        currPatch.set_alpha(alpha)
        self.figpanel.canvas.draw()


class _neededLibraries(object):
    icon = None
    id= None
    image= wx.NullBitmap
    name= ''
    def __init__( self):
        if hasattr( wx.GetApp(), 'Logg'):
            self.log= wx.GetApp().Logg  # to write the actions
        else:
            self.log= passlog
            
        self.name=  ""
        self.plotName= ""
        self.setminRequiredCols= 0
        self.app=       wx.GetApp()
        self.dialog=    _dialog         # to create de dialod
        self.grid=      self.app.grid
        self.log=       self.app.Logg   # to report
        self.outputGrid= self.app.output # the usern can use the plot functions
        self.data2Plotdiaglog= data2Plotdiaglog
        self.selectDialogData2plot= selectDialogData2plot
        self.scatterDialog = scatterDialog
        self.translate = self.app.translate
    
    def _updateColsInfo( self):
        gridCol=            self.grid.GetUsedCols()
        self.columnNames=   gridCol[0]
        self.columnNumbers= gridCol[1]
        
    @property
    def name( self):
        return self.__name__
    @name.setter
    def name( self, name):
        if not isinstance(name, (str, unicode)):
            return
        self.__name__ = name
    @property
    def plotName( self):
        return self.__statName__
    @plotName.setter
    def plotName( self, name):
        if not isinstance(name, (str,)):
            return
        self.__statName__ = name
    @property
    def minRequiredCols( self):
        return self._minRequiredCols
    @minRequiredCols.setter
    def minRequiredCols( self, value):
        if not isinstance(value, (int, float,np.ndarray )):
            return
        self._minRequiredCols= value

class pltobj( wx.Frame, object ):
    def _requeridos( self):
        self.ca=                 None
        self.log=                wx.GetApp().Logg  # to write the actions
        self.name=               ""
        self.plotName=           ""
        self.setminRequiredCols= 0
        self.app=                wx.GetApp()
        self.translate=          wx.GetApp().translate
        if 0:
            self.dialog=         _dialog         # to create de dialog
            self.grid=           self.app.grid
            self.outputGrid=     self.app.output # the usern can use the plot functions
        self.data2Plotdiaglog=   data2Plotdiaglog
        self.selectDialogData2plot= selectDialogData2plot
        self.scatterDialog=      scatterDialog
        
    def __init__( self, parent, *args, **params):
        self.i =        gene()
        self.currAxes=  None
        self._requeridos()
        if parent == None:
            try:
                parent= wx.GetApp().frame
            except AttributeError:
                pass
        self.graphParams= {'xlabel': '',
                           'ylabel': '',
                           'title': '',
                           'xtics': [],
                           'ytics': []}
        
        for key in self.graphParams.keys():
            try:
                self.graphParams[key] = params.pop(key)
            except KeyError:
                continue
            
        wx.Frame.__init__ ( self, parent,
                            id = wx.ID_ANY,
                            title = wx.EmptyString,
                            pos = wx.DefaultPosition,
                            size = wx.Size( 642,465 ),
                            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        self.figpanel= MplCanvasFrame( self )
        
        self.m_notebook1= wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_notebook1.ca= None # setting the current axis
        
        if wx.Platform == '__WXGTK__':
            mainSizer= wx.BoxSizer( wx.HORIZONTAL )
            mainSizer.Add( self.m_notebook1, 1, wx.EXPAND |wx.ALL, 5 )
            mainSizer.Add( self.figpanel, 3, wx.EXPAND |wx.ALL, 5 )
        else:
            self.m_mgr = aui.AuiManager()
            self.m_mgr.SetManagedWindow( self )
            self.m_mgr.AddPane( self.figpanel, aui.AuiPaneInfo().Left().
                                CaptionVisible(True).Caption(self.translate(u"Graph")).Centre().
                                MaximizeButton(True).MinimizeButton(False).Resizable(True).
                                PaneBorder( False ).CloseButton( False ))
            
            self.m_mgr.AddPane( self.m_notebook1, aui.AuiPaneInfo().Left().
                                CaptionVisible(True).Caption(self.translate(u"Graph Properties")).CaptionVisible(True).
                                MaximizeButton(True).MinimizeButton(False).Resizable(True).
                                PaneBorder( False ).CloseButton( False ). BestSize(wx.Size(200,-1)))
        
        self.scrolledWindow1= scrolled1( self.graphParams, self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL)
        self.scrolledWindow2= scrolled2( self.graphParams, self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL)
        self.scrolledWindow3= scrolled3( self.graphParams, self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL)
        
        self.m_notebook1.AddPage( self.scrolledWindow1, self.translate( u"Main Options"), True )
        self.m_notebook1.AddPage( self.scrolledWindow2, self.translate( u"Lines"), False )
        self.m_notebook1.AddPage( self.scrolledWindow3, self.translate( u"patches"), False )

        self.statusbar = self.CreateStatusBar( 2, wx.ST_SIZEGRIP, wx.ID_ANY )
 
        if wx.Platform == '__WXGTK__':
            self.SetSizer( mainSizer )
            self.Fit()
            self.Layout()
        else:
            self.m_mgr.Update()
            
        self.Centre( wx.BOTH )
        # Connect Events
        self.Bind( wx.EVT_ACTIVATE, self.OnActivate )
        self.figpanel.canvas.mpl_connect( 'motion_notify_event', self._UpdateStatusBar)
        self.figpanel.canvas.mpl_connect( 'axes_enter_event',    self._enter)
        self.figpanel.canvas.mpl_connect( 'axes_leave_event',    self._leave)
        
    def _enter(self, evt):
        currAxes = evt.inaxes
        self._Update( currAxes, evt)
        
    def _leave(self, evt):
        self.currAxes = None
        self._Update(evt)
                
    def updateControls( self):
        # connect cursos with a selected axes
        # self._connectCursor(self.gca())
        self.scrolledWindow1._setItems(self)
        self.scrolledWindow2._setItems()
        self.scrolledWindow3._setItems()

    def OnActivate( self, evt):
        # read the actual axes
        if hasattr(self, 'axes'):
            if len(self.axes) == 0:
                # clear the title, x and ylabel contents
                self._cleartitles()
            else:
                # update the title, x and ylabel contents
                self.scrolledWindow1.plt_textCtr2.Value= self.gca().get_xlabel()
                # clear ylabel ctrl
                self.scrolledWindow1.plt_textCtr3.Value= self.gca().get_ylabel()
                # clear title
                self.scrolledWindow1.plt_textCtr1.Value= self.gca().get_title()
                # connect the cursor to current axes
                self._connectCursor( self.gca())
                
        
    def _clearTitles( self, evt):
        # clear xlabel ctrl
        self.scrolledWindow1.plt_textCtr2.Value= u''
        # clear ylabel ctrl
        self.scrolledWindow1.plt_textCtr3.Value= u''
        # clear title
        self.scrolledWindow1.plt_textCtr1.Value= u''


    def _connectCursor( self, axes):
        # connect the cursor to the axes selected
        self.cursor= Cursor( axes, useblit = True, color = 'blue', linewidth = 1)
        self.cursor.horizOn= False
        self.cursor.vertOn=  False


    def __getattribute__( self, name):
        '''wraps the funtions to the figure
        emulating a plot frame control'''
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self.figpanel.__getattribute__(name)

    def _addLabels( self, labels):
        self.figpanel.gca().set_title(labels['title'])
        self.figpanel.gca().set_xlabel(labels['xlabel'])
        self.figpanel.gca().set_ylabel(labels['ylabel'])
        self.figpanel.canvas.draw()

    def _plotTest( self):
        x = np.arange(0, 6, .01)
        y = np.sin(x**2)*np.exp(-x)
        self.gca().plot(x, y)
    def _convertColName2Values( self, colNamesSelected, *args, **params):
        '''geting the selected columns of the InputGrid'''
        columns  = list()
        for colName in colNamesSelected:
            col= np.array( self.grid.GetColNumeric( colName))
            col.shape = ( len(col),1)
            columns.append( col)
        
        return columns
    
    def _OnLegend( self, evt ):
        value = evt.Checked()
        try:
            legend= self.figpanel.gca().legend()
            legend.set_visible(value)
        except:
            pass
    def _Update(self, currAxes, evt):
        self.scrolledWindow1._Update( currAxes, evt)
        self._UpdateStatusBar(evt)
        # updating the x,y axis limit values
        
    def _UpdateStatusBar( self, evt):
        if evt.inaxes and self.scrolledWindow1.m_checkBox3.GetValue():
            x, y = evt.xdata, evt.ydata
            self.statusbar.SetStatusText(( "x= " + str(round(x,5)) +
                                           "  y=" + str(round(y,5)) ),
                                         1)
    def Destroy(self, *args, **params):
        if wx.Platform != '__WXGTK__':
            self.m_mgr.UnInit()
def fontDialog( parent):
    curClr = wx.Colour(0,0,0,0)#r,g,b,ALPHA
    fuente = wx.Font(wx.FONTSIZE_MEDIUM,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL)
    data = wx.FontData()
    data.EnableEffects(True)
    data.SetColour(curClr)         # set colour
    data.SetInitialFont(fuente)

    dlg = wx.FontDialog(parent, data)
    if dlg.ShowModal() == wx.ID_OK:
        data = dlg.GetFontData()
        font = data.GetChosenFont()

        colour = data.GetColour()
        return {"name":   font.GetFaceName(),
                "size":   font.GetPointSize(),#  "stretch":font.stretch,
                "style":  "normal", #font.GetStyle(), #    "variant":font.variant,
                "weight": font.GetWeight(),#     "colour":  data.GetColour(),
                }

class fontmanager:
    def __init__( self):
        self.fontlist = font_manager.createFontList(font_manager.findSystemFonts())
        self._font2dict()

    def _font2dict( self):
        self.fontdict = dict()
        k = 0
        for font in self.fontlist:
            font1 = dict()
            try:
                for nombre,valor in [("fname",font.fname),
                                     ("name",font.name),
                                     ("size",font.size),
                                     ("stretch",font.stretch),
                                     ("style",font.style),
                                     ("variant",font.variant),
                                     ("weight", font.weight)]:
                    if nombre == "size":
                        if valor == 'scalable':
                            valor = 10
                    font1[nombre] = valor
            except AttributeError:
                k+= 1
                continue
            self.fontdict[k] = font1
            k+= 1

class test ( wx.Frame ):
    def __init__( self, parent):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY,
                            title='Matplotlib in Wx', pos = wx.DefaultPosition,
                            size = wx.DefaultSize,
                            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )

        self.figpanel= MplCanvasFrame( self )
        
        self.m_mgr.AddPane( self.figpanel, aui.AuiPaneInfo() .Left() .
                            Caption("matplotlib embeded").
                            MaximizeButton( False ).MinimizeButton( False ).
                            PinButton( False ).PaneBorder( False ).Dock().
                            Resizable().FloatingSize( wx.DefaultSize ).
                            DockFixed( False ).CentrePane().Row(0).Layer(0) )
        self.axes = self.figpanel.add_subplot(111)
        x = np.arange(0, 6, .01)
        y = np.sin(x**2)*np.exp(-x)
        self.axes.plot(x, y)
        self.axes.set_title( "Primer grafica")
        self.axes.set_xlabel( "Xlabel")
        self.axes.set_ylabel( "Ylabel")

        self.m_mgr.Update()
        self.Centre(wx.BOTH)

class MplCanvasFrame( wx.Panel, Figure):
    """Class to represent a Matplotlib Figure as a wxPanel with Figure properties"""
    def __init__( self, parent, *args, **params):
        # initialize the superclass, the wx.Frame
        wx.Panel.__init__( self, parent, wx.ID_ANY)
        Figure.__init__(self,)
        self.canvas=  FigureCanvas( self, wx.ID_ANY, self)
        self.sizer=   wx.BoxSizer( wx.VERTICAL)
        # instantiate the Navigation Toolbar
        self.toolbar= NavigationToolbar2Wx( self.canvas)
        # needed to support Windows systems
        self.toolbar.Realize()
        # add it to the sizer
        self.sizer.Add( self.toolbar, 0, wx.LEFT | wx.EXPAND)
        # explicitly show the toolbar
        self.toolbar.Show()
        self.sizer.Add( self.canvas, 1,  wx.LEFT | wx.TOP | wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Fit()

if __name__ == '__main__':
    from random import random
    # Create a wrapper wxWidgets application
    app = wx.App()
    app.DECIMAL_POINT = '.'
    app.translate= translate
    app.Logg= log()
    # instantiate the Matplotlib wxFrame
    plt = pltobj( None,)# xlabel = "", ylabel = u"value", title= u"Titulo" )
    plt.delaxes(plt.gca())
    ax1= plt.add_subplot(2,1,1)
    x= range(20)
    y= [x1+3 for x1 in x]
    ax1.plot(range(20), y, 'b*')
    ax2= plt.add_subplot(2,1,2)
    ax2.plot(range(10), range(10),'r+')
    plt.gca()
    # update the controls
    plt.updateControls()
    # show it    
    plt.Show( True)
    app.MainLoop()