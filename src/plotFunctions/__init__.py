"""a module thath will be used as a container of different functions

Created on 11/05/2012
New plot system

@author: Sebastian lopez Buritica   selobu at gmail dot com <Colombia>
License: GPL3
"""
version = "0.0.1"
__all__ = ['histogramPlot', 'bar',
           'lines', 'scatter',
           'others',]

# wxPython module
import wx
if not (wx.__version__ > '2.9.4'):
    import wx.aui
import wx.lib.agw.aui as aui
import wx.propgrid as wxpg
# Matplotlib Figure object
from matplotlib.figure import Figure
from matplotlib import font_manager
from matplotlib.widgets import Cursor
# Numpy functions for image creation
import numpy as np

# import the WxAgg FigureCanvas object, that binds Figure to
# WxAgg backend. In this case, this is a wxPanel
from matplotlib.backends.backend_wxagg import \
     FigureCanvasWxAgg as FigureCanvas
from matplotlib.backend_bases import MouseEvent
from matplotlib.backends.backend_wx import NavigationToolbar2Wx, Artist, StatusBarWx
import matplotlib.mlab as mlab
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.cm as cm

from matplotlib.pylab import setp
from multiPlotDialog import selectDialogData2plot, scatterDialog
from easyDialog.easyDialog import NumTextCtrl

PROPLEGEND=   {'size': 11}
markerStyles= [ 'None', '.', '+', 'o', 'v',
                '^', '<', '>', '8', 's', 'p',
                '*', 'h', 'H', 'D', 'd']
faceColors=   ['b', 'g', 'r', 'c', 'm', 'y', 'k']
lineStyles=   ['_', '-', '--', ':']
lineSizes=    [str( x*0.5) for x in range( 1, 15, 1)]
markerSizes=  [str( x) for x in range( 1, 16, 1)]
alpha=        [str( x/float( 10)) for x in range( 1, 11)]

from easyDialog import Dialog as _dialog

def _(data):
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
    _= wx.GetApp()._
    txt1= ['StaticText',   [_(u"Select data to plot")]]
    btn1= ['CheckListBox', [columnNames]]
    setting= {'Title': _(title)}
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
    def __init__( self, pltobj,  *args, **params):
        wx.ScrolledWindow.__init__( self, *args[1:], **params)
        self.figpanel=  self.Parent.Parent.figpanel
        self.plt= pltobj
        graphParams= args[0]
        if params.has_key('parent'):
            parent= params['parent']
        else:
            parent= args[1]
        self.SetScrollRate( 5, 5 )
        mainSizer=            wx.BoxSizer( wx.VERTICAL )
        self.pg = pg = wxpg.PropertyGridManager(self, style=wxpg.PG_SPLITTER_AUTO_CENTER |  wxpg.PG_AUTO_SORT)# | wxpg.PG_TOOLBAR)
        pg.AddPage( _("Main options") )

        # title
        pg.Append( wxpg.PropertyCategory( _("1 - Title")) )
        pg.Append( wxpg.StringProperty( _("title string"),  value= _("Title") ) )
        pg.Append( wxpg.ColourProperty( _("title colour"),  value= (0,0,0) ) )
        pg.Append( wxpg.FontProperty(   _("title font"),   value= self.GetFont()) )
        pg.Append( wxpg.BoolProperty( _("title clip_on"), value= False) )
        pg.SetPropertyAttribute( _("title clip_on"), "UseCheckbox", True)
        pg.Append( wxpg.EnumProperty( _("title multialignment"),_("title multialignment"),
                                            ['left' , 'right' , 'center' ],
                                            [0, 1, 2, ],  2))
        if 0:
            pg.Append( wxpg.PropertyCategory( _("1.1 - TitleFont")) )

            pg.SetPropertyAttribute( _("title clip_on"), "UseCheckbox", True)
            pg.Append( wxpg.BoolProperty( _("title visible"), value= True) )
            pg.SetPropertyAttribute( _("title visible"), "UseCheckbox", True)
            pg.Append( wxpg.EnumProperty( _("title fontweight"),_("title fontweight"),
                                            [ 'normal','bold','heavy','light','ultrabold','ultralight']
                                            ,  [0, 1, 2, 3, 4, 5],  0) )
            pg.Append( wxpg.EnumProperty( _("title verticalalignment"),_("title verticalalignment"),
                                           [ 'center','top','bottom','baseline']
                                            ,  [0, 1, 2, 3],  0) )
            pg.Append( wxpg.EnumProperty( _("title fontstyle"),_("title fontstyle"),
                                                   [ 'normal','italic','oblique',]
                                                    ,  [0, 1, 2],  0) )
        
        # xaxis
        pg.Append( wxpg.PropertyCategory( _("2 - x axis")) )
        pg.Append( wxpg.StringProperty( _("xlabel string"), value= _("xlabel") ) )
        pg.Append( wxpg.ColourProperty( _("xlabel colour"), value= (0,0,0) ) )
        pg.Append( wxpg.FontProperty(   _("xlabel font"),   value= self.GetFont()) )
        pg.Append( wxpg.FloatProperty(  _("xmin"),          value= 0.0) )
        pg.Append( wxpg.FloatProperty(  _("xmax"),          value= 100.0) )
        pg.Append( wxpg.IntProperty(   _("xlabel angle"),   value=0) )
        pg.SetPropertyEditor( _("xlabel angle"),"SpinCtrl")
        pg.Append( wxpg.EnumProperty( _("xaxis scale"),_("xaxis scale"),
                                        ['linear','symlog',],  [0,1],  0) )   
        
        
        # yaxis
        pg.Append( wxpg.PropertyCategory( _("3 - y axis")) )
        pg.Append( wxpg.StringProperty( _("ylabel string"), value= _("ylabel") ) )
        pg.Append( wxpg.ColourProperty( _("ylabel colour"), value= (0,0,0) ) )
        pg.Append( wxpg.FontProperty(   _("ylabel font"),   value= self.GetFont()) )
        pg.Append( wxpg.FloatProperty(  _("ymin"),          value= 0.0) )
        pg.Append( wxpg.FloatProperty(  _("ymax"),          value= 100.0) )
        pg.Append( wxpg.IntProperty(   _("ylabel angle"),   value=0) )
        pg.SetPropertyEditor( _("ylabel angle"),"SpinCtrl")
        pg.Append( wxpg.EnumProperty( _("yaxis scale"),_("yaxis scale"),
                                        ['linear','symlog',],  [0,1], 0) )
        
        # legend
        pg.Append( wxpg.PropertyCategory( _("4 - Legend")) )
        pg.Append( wxpg.BoolProperty( _("Show legend"), value= False) )
        pg.SetPropertyAttribute( _("Show legend"), "UseCheckbox", True)

        # grid
        pg.Append( wxpg.PropertyCategory( _("5 - Grid")) )
        pg.Append( wxpg.BoolProperty( _("Show grid"),   value= False) )
        pg.SetPropertyAttribute( _("Show grid"), "UseCheckbox", True)
        pg.Append( wxpg.BoolProperty( _("View cursor"), value= False) )
        pg.SetPropertyAttribute( _("View cursor"), "UseCheckbox", True)
  
        if not self.__createDispatcher():
            raise StandardError("Cannot create the graph dispatcher")
        
        pg.Bind( wxpg.EVT_PG_CHANGED, self.__OnPropGridChange )
        #========----===========
        mainSizer.Add( self.pg , 1, wx.EXPAND, 5 )
        self.SetSizer(mainSizer)
        self.Layout()
        mainSizer.Fit( self )
    def __OnPropGridChange(self, evt):
            p = evt.GetProperty()
            if p:
                self.__dispatcher[p.GetName()](evt, p.GetValue())
    def __createDispatcher( self):
        self.__dispatcher=  dispatcher = dict()
        dispatcher[ _("title string")]= self.__TitleChange
        dispatcher[ _("title colour")]= self.__titleFontColour
        dispatcher[ _("title font")]= self.__titleFontProp
        dispatcher[ _("title clip_on")]= self.__titleClipOn
        dispatcher[ _("title multialignment")]= self.__titleMultialignment
        
        dispatcher[ _("xlabel string")]= self._xlabelChange
        dispatcher[ _("xlabel colour")]= self._xlabelFontColour
        dispatcher[ _("xlabel font")]= self._xlabelFontProp
        dispatcher[ _("xmin")]= self._xminValue
        dispatcher[ _("xmax")]= self._xmaxValue
        dispatcher[ _("xlabel angle")]= self._xAngleChange
        dispatcher[ _("xaxis scale")]= self._OnXaxisScale
        
        dispatcher[ _("ylabel string")]= self._ylabelChange
        dispatcher[ _("ylabel colour")]= self._ylabelFontColour
        dispatcher[ _("ylabel font")]= self._ylabelFontProp
        dispatcher[ _("ymin")]= self._yminValue
        dispatcher[ _("ymax")]= self._ymaxValue
        dispatcher[ _("ylabel angle")]= self._yAngleChange
        dispatcher[ _("yaxis scale")]= self._OnYaxisScale
        
        dispatcher[ _("Show legend")]= self._OnLegend
        dispatcher[ _("Show grid")]= self._OnGrid
        dispatcher[ _("View cursor")]= self._OnViewCursor
        return True

    def __TitleChange( self, evt , *args, **params):
        newtitle= args[0]
        self.plt.title= newtitle
        self.figpanel.canvas.draw()
        print 'Title= ' + "'" + newtitle+ "'"
        print 'plt.gca().set_title(Title)'
        self.__titleFontProp(evt)
    def __titleFontProp( self, evt, *args, **params):
        p = evt.GetValue()
        pg0= self.pg.GetPage(0)
        if len(args) == 0:
            fontprop= pg0.GetProperty(_("title font")).m_value
        else:
            fontprop= args[0]
        clip_on= pg0.GetProperty(_("title clip_on")).m_value
        multialignment= pg0.GetProperty(_("title multialignment")).m_value
        multialignment= ['left' , 'right' , 'center' ][multialignment]

        colour= pg0.GetProperty(_("title colour")).m_value
        fontDictWeigth={u'wxFONTWEIGHT_NORMAL': 'normal',
                        u'wxFONTWEIGHT_BOLD':   'bold',
                        u'wxFONTWEIGHT_LIGHT':  'light'}
        fontAsDict= {'fontsize':       fontprop.PointSize,
                     'fontname':       fontprop.FaceName,
                     'fontweight':     fontDictWeigth[fontprop.GetWeightString()],
                     'color':          [col/float(255) for col in colour.asTuple()],
                     'clip_on':        clip_on,
                     'multialignment': multialignment,
                     }
        self.plt.gca().set_title( self.plt.title, fontAsDict)
        self.figpanel.canvas.draw()
        evt.Skip()
    def __titleFontColour(self, evt , *args, **params):
        self.__titleFontProp(evt)
    def __titleClipOn(self, evt, *args, **params):
        self.__titleFontProp(evt)
    def __titleMultialignment(self, evt, *args, **params):
        self.__titleFontProp(evt)

    def _xlabelChange( self, evt, *args, **params):
        newXlabel= args[0]
        self.plt.xlabel= newXlabel
        self.figpanel.canvas.draw()
        print 'xlabel= ' + "'" +  newXlabel + "'"
        print 'plt.xlabel = xlabel'
        self._xlabelFontProp(evt)
    def _xlabelFontProp( self, evt, *args, **params):
        if len(args) == 0:
            pg0=self.pg.GetPage(0)
            fontprop= pg0.GetProperty(_("xlabel font")).m_value
        else:
            fontprop= args[0]
        p = evt.GetProperty()
        pg0=self.pg.GetPage(0)
        colour= pg0.GetProperty(_("xlabel colour")).m_value
        fontDictWeigth={u'wxFONTWEIGHT_NORMAL': 'normal',
                        u'wxFONTWEIGHT_BOLD':   'bold',
                        u'wxFONTWEIGHT_LIGHT':  'light'}
        fontAsDict= {'fontsize':   fontprop.PointSize,
                     'fontname':   fontprop.FaceName,
                     'fontweight': fontDictWeigth[fontprop.GetWeightString()],
                     'color':      [col/float(255) for col in colour.asTuple()],
                     }
        self.plt.gca().set_xlabel( self.plt.xlabel, fontAsDict)
        self.figpanel.canvas.draw()
        evt.Skip()
    def _xlabelFontColour(self, evt , *args, **params):
        self._xlabelFontProp(evt)
    def _OnXaxisScale( self, evt, *args, **params):
        p= evt.GetValue()
        print '# changing x axis scale'
        value = 'linear'
        if p == 1:
            value = 'symlog'
        self.plt.set_xscale(value)
        self.figpanel.canvas.draw()
        print 'plt.gca().set_xscale('+ "'" + value.__str__()+ "'" +')'
    def _xminValue( self, evt, *args, **params):
        evt.Skip()
        p= evt.GetValue()
        currentAxisValue= self.plt.get_xbound()
        self.plt.set_xbound((p, currentAxisValue[1]))
        self.figpanel.canvas.draw()
        print 'plt.gca().set_xbound((float('+evt.GetString().__str__()+'),axisValue[1]))'
    def _xmaxValue( self, evt, *args, **params):
        evt.Skip()
        p= evt.GetValue()
        currentAxisValue= self.plt.get_xbound()
        self.plt.set_xbound((currentAxisValue[0],p))
        self.figpanel.canvas.draw()
        print 'plt.gca().set_xbound((axisValue[0],float('+evt.GetString().__str__()+')))'
    def _xAngleChange( self, evt, *args, **params):
        rotationAngle= evt.GetValue()
        labels = self.plt.get_xticklabels()
        currFontSize= self.plt.xaxis.get_label().get_fontsize()
        setp( labels, rotation= rotationAngle, fontsize= currFontSize)
        self.figpanel.canvas.draw()

    def _ylabelChange( self, evt, *args, **params):
        newYlabel= args[0]
        self.plt.ylabel= newYlabel
        self.figpanel.canvas.draw()
        print 'ylabel= ' + "'" +  newYlabel + "'"
        print 'plt.ylabel = ylabel'
        self._ylabelFontProp(evt)
    def _ylabelFontProp( self, evt, *args, **params):
        if len(args) == 0:
            pg0=self.pg.GetPage(0)
            fontprop= pg0.GetProperty(_("ylabel font")).m_value
        else:
            fontprop= args[0]
        p = evt.GetProperty()
        pg0=self.pg.GetPage(0)
        colour= pg0.GetProperty(_("ylabel colour")).m_value
        fontDictWeigth={u'wxFONTWEIGHT_NORMAL': 'normal',
                        u'wxFONTWEIGHT_BOLD':   'bold',
                        u'wxFONTWEIGHT_LIGHT':  'light'}
        fontAsDict= {'fontsize':   fontprop.PointSize,
                     'fontname':   fontprop.FaceName,
                     'fontweight': fontDictWeigth[fontprop.GetWeightString()],
                     'color':      [col/float(255) for col in colour.asTuple()],
                     }
        self.plt.gca().set_ylabel( self.plt.ylabel, fontAsDict)
        self.figpanel.canvas.draw()
        evt.Skip()
    def _ylabelFontColour(self, evt , *args, **params):
        self._ylabelFontProp(evt)
    def _OnYaxisScale( self, evt, *args, **params):
        p= evt.GetValue()
        print '# changing y axis scale'
        value = 'linear'
        if p == 1:
            value = 'symlog'
        self.plt.set_yscale(value)
        self.figpanel.canvas.draw()
        print 'plt.gca().set_yscale('+ "'" + value.__str__()+ "'" +')'
    def _yminValue( self, evt, *args, **params):
        evt.Skip()
        p= evt.GetValue()
        currentAxisValue= self.plt.get_ybound()
        self.plt.set_ybound((p, currentAxisValue[1]))
        self.figpanel.canvas.draw()
        print 'plt.set_ybound((float('+evt.GetString().__str__()+'),ayisValue[1]))'
    def _ymaxValue( self, evt, *args, **params):
        evt.Skip()
        p= evt.GetValue()
        currentAxisValue= self.plt.get_ybound()
        self.plt.set_ybound((currentAxisValue[0],p))
        self.figpanel.canvas.draw()
        print 'plt.gca().set_ybound((axisValue[0],float('+evt.GetString().__str__()+')))'
    def _yAngleChange( self, evt, *args, **params):
        rotationAngle= evt.GetValue()
        labels = self.plt.get_yticklabels()
        currFontSize= self.plt.yaxis.get_label().get_fontsize()
        setp( labels, rotation= rotationAngle, fontsize= currFontSize)
        self.figpanel.canvas.draw()

    def _OnLegend(self, evt , *args, **params):
        evt.Skip()
        print _("not implemented yet!")
    def _OnGrid( self, evt, *args, **params):
        p= evt.GetValue()
        print '# changing grid state'
        self.plt.grid(p)
        ## solved bug updating the state of the grid matplotlib state
        self.plt.gca()._gridOn= p
        self.figpanel.canvas.draw()
        print 'plt.grid('+p.__str__()+')'

    def _OnViewCursor( self, evt, *args, **params):
        #if self.Parent.ca == None:
        #    return
        #else:
        #    ca= self.Parent.ca
        # verify the cursor property created with
        # connectCursor
        if not hasattr(self.plt,'cursor'):
            return
        p= evt.GetValue()
        if not p:
            self.plt.statusbar.SetStatusText(( ""), 1)
        self.plt.cursor.horizOn = p
        self.plt.cursor.vertOn = p
        self.figpanel.canvas.draw()
    def _setItems(self, parent):
        self.parent= parent
        parent._addLabels( parent.graphParams)
        if len( parent.graphParams['xtics']) != 0:
            self.parent.ca.set_xticklabels( parent.graphParams['xtics'])
        if len( parent.graphParams['ytics']) != 0:
            self.parent.ca.set_yticklabels( parent.graphParams['ytics'])
        self.__updateLimits(None)
    def _Update(self, currAxes= None, evt= None, *args, **params):
        if currAxes== None:
            currAxes= self.plt.gca()
        self.__UpdateTitle( currAxes, evt, redraw= False)
        # to be fix
        #self.__UpdateXlabelFont( currAxes, evt, redraw= False)
        #self.__UpdateYlabelFont( currAxes, evt, redraw= False)
        self.__updateLimits( currAxes, evt)
        self.__UpdateAxisScale( currAxes, evt, )
    def __UpdateTitle(self, currAxes, evt= None, *args, **params):
        """updating the data contained from the draw to the propertygrid"""
        pg0=      self.pg.GetPage(0)
        title=    self.plt.title # get_title()
        xlabel=   self.plt.xlabel # ca.get_xlabel()
        ylabel=   self.plt.ylabel # ca.get_ylabel()
        gridState= self.plt.gca()._gridOn
        # getting states of the variables with the control actual ones
        actaulTitle=     pg0.GetProperty( _("title string")).m_value   # self.plt_textCtr1.GetLabel()
        actualXlabel=    pg0.GetProperty( _("xlabel string")).m_value   # self.plt_textCtr2.GetLabel()
        actualYlabel=    pg0.GetProperty( _("ylabel string")).m_value   # self.plt_textCtr3.GetLabel()
        actualGridState= pg0.GetProperty( _("Show grid")).m_value   # self.m_checkBox1.Value
        # updating the control values
        if title != actaulTitle:
            pg0.SetPropertyValue( _("title string"),  title)
        if xlabel != actualXlabel:
            pg0.SetPropertyValue( _("xlabel string"), xlabel)
        if ylabel != actualYlabel:
            pg0.SetPropertyValue( _("ylabel string"), ylabel)
        if gridState != actualGridState:
            pg0.SetPropertyValue( _("Show grid"),  gridState)

        # getting the parameters of the title string
        title=self.plt.gca().title
        fnt= title.get_fontproperties()
        titleFontAsDict= { 'fontsize':     int(fnt.get_size_in_points()),
                           'fontname':       fnt.get_name(),
                           'fontweight':     fnt.get_weight(),
                           'color':          title.get_color(),
                           'clip_on':        title.get_clip_on(),
                           'multialignment': title._get_multialignment(),
                           }
        # changing the contents of the pg
        pg0=   self.pg.GetPage(0)
        newfont= pg0.GetProperty(_("title font")).m_value

        newfont.SetPointSize( titleFontAsDict['fontsize'])
        newfont.SetFaceName( titleFontAsDict['fontname'])

        fontDictWeigth={'normal': wx.FONTWEIGHT_NORMAL,
                        'bold':   wx.FONTWEIGHT_BOLD,
                        'light':  wx.FONTWEIGHT_LIGHT}
        newfont.SetWeight( fontDictWeigth[titleFontAsDict['fontweight']])
        ##newfont.color= [0,0,0]
        ##newfont.clip_on= titleFontAsDict['clip_on']
        ##newfont.multialignment= titleFontAsDict['multialignment']
        pg0.SetPropertyValue(_("title font"), newfont)

    # to be fix
    def __UpdateXlabelFont(self, currAxes, evt= None, *args, **params):
        # getting the parameters of the title string
        title=self.plt.gca().get_xlabel()
        fnt= title.get_fontproperties()
        titleFontAsDict= { 'fontsize':     int(fnt.get_size_in_points()),
                           'fontname':       fnt.get_name(),
                           'fontweight':     fnt.get_weight(),
                           'color':          title.get_color(),
                           'clip_on':        title.get_clip_on(),
                           'multialignment': title._get_multialignment(),
                           }
        # changing the contents of the pg
        pg0=   self.pg.GetPage(0)
        newfont= pg0.GetProperty(_("xlabel font")).m_value
        newfont.SetPointSize( titleFontAsDict['fontsize'])
        newfont.SetFaceName( titleFontAsDict['fontname'])
        fontDictWeigth={'normal': wx.FONTWEIGHT_NORMAL,
                        'bold':   wx.FONTWEIGHT_BOLD,
                        'light':  wx.FONTWEIGHT_LIGHT}
        newfont.SetWeight( fontDictWeigth[titleFontAsDict['fontweight']])
        ##newfont.color= [0,0,0]
        ##newfont.clip_on= titleFontAsDict['clip_on']
        ##newfont.multialignment= titleFontAsDict['multialignment']
        pg0.SetPropertyValue(_("xlabel font"), newfont)
    def __UpdateYlabelFont(self, currAxes, evt= None, *args, **params):
        # getting the parameters of the title string
        title=self.plt.gca().get_ylabel()
        fnt= title.get_fontproperties()
        titleFontAsDict= { 'fontsize':     int(fnt.get_size_in_points()),
                           'fontname':       fnt.get_name(),
                           'fontweight':     fnt.get_weight(),
                           'color':          title.get_color(),
                           'clip_on':        title.get_clip_on(),
                           'multialignment': title._get_multialignment(),
                           }
        # changing the contents of the pg
        pg0=   self.pg.GetPage(0)
        newfont= pg0.GetProperty(_("ylabel font")).m_value

        newfont.SetPointSize( titleFontAsDict['fontsize'])
        newfont.SetFaceName( titleFontAsDict['fontname'])

        fontDictWeigth={'normal': wx.FONTWEIGHT_NORMAL,
                        'bold':   wx.FONTWEIGHT_BOLD,
                        'light':  wx.FONTWEIGHT_LIGHT}
        newfont.SetWeight( fontDictWeigth[titleFontAsDict['fontweight']])

        ##newfont.color= [0,0,0]
        ##newfont.clip_on= titleFontAsDict['clip_on']
        ##newfont.multialignment= titleFontAsDict['multialignment']

        pg0.SetPropertyValue(_("ylabel font"), newfont)

    def __updateLimits(self, currAxes, evt = None, *args, **params):
        ca= currAxes
        if ca == None:
            return
        xlim= self.plt.get_xlim()
        ylim= self.plt.get_ylim()
        # reading the data
        pg0=   self.pg.GetPage(0)
        xmin=  pg0.GetProperty( _("xmin")).m_value
        xmax=  pg0.GetProperty( _("xmax")).m_value
        ymin=  pg0.GetProperty( _("ymin")).m_value
        ymax=  pg0.GetProperty( _("ymax")).m_value
        oldxlim= (xmin, xmax)
        oldylim= (ymin, ymax)
        # setting the limits of the axis to the buttons
        if oldxlim != xlim:
            pg0.SetPropertyValue(_("xmin"), xlim[0])
            pg0.SetPropertyValue(_("xmax"), xlim[1])
        if oldylim != ylim:
            pg0.SetPropertyValue(_("ymin"), ylim[0])
            pg0.SetPropertyValue(_("ymax"), ylim[1])
    def __UpdateAxisScale(self, currAxes, evt,*args, **params):
        pg0= self.pg.GetPage(0)
        # readin the scales of the current axes
        xscale=    self.plt.get_xscale( )
        yscale=    self.plt.get_yscale( )
        oldxscale= ["linear","symlog"][pg0.GetProperty( _("xaxis scale")).m_value]
        oldyscale= ["linear","symlog"][pg0.GetProperty( _("yaxis scale")).m_value]
        # comparing the values with the graphic ones
        if xscale != oldxscale:
            pg0.SetPropertyValue( _("xaxis scale"), xscale)
        if yscale != oldyscale:
            pg0.SetPropertyValue( _("xaxis scale"), yscale)

class scrolled2(wx.ScrolledWindow):
    from matplotlib.colors import colorConverter
    def __init__( self, pltobj,  *args, **params):
        wx.ScrolledWindow.__init__(self, *args[1:], **params)
        self.figpanel= self.Parent.Parent.figpanel
        self.plt= pltobj
        self.__currLine= None # none line selected
        graphParams= args[0]
        self.gca= self.plt.gca()

        if params.has_key('parent'):
            parent= params['parent']
        else:
            parent = args[1]
        self.SetScrollRate( 5, 5 )
        bSizer21 = wx.BoxSizer( wx.VERTICAL )

        sbSizer8 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _( u"Choose a line") ), wx.VERTICAL )

        m_listBox1Choices = []
        self.m_listBox1 = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 130,80 ), m_listBox1Choices, 0 )
        sbSizer8.Add( self.m_listBox1, 0, wx.ALL, 5 )

        bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_button87 = wx.Button( self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button87.SetMinSize( wx.Size( 20,-1 ) )

        bSizer5.Add( self.m_button87, 0, wx.LEFT|wx.RIGHT, 5 )

        self.m_button41 = wx.Button( self, wx.ID_ANY, _( u"Refresh lines"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer5.Add( self.m_button41, 0, wx.ALIGN_RIGHT|wx.LEFT, 5 )

        sbSizer8.Add( bSizer5, 1, wx.EXPAND, 5 )

        bSizer21.Add( sbSizer8, 0, 0, 5 )
        #sbSizer71 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _( u"Some Properties") ), wx.VERTICAL )
        self.pg = pg = wxpg.PropertyGridManager(self, style=wxpg.PG_SPLITTER_AUTO_CENTER |  wxpg.PG_AUTO_SORT)# | wxpg.PG_TOOLBAR)
        pg.AddPage( _("Lines properties") )
        pg.Append( wxpg.PropertyCategory( _("1- line Properties")) )
        pg.Append( wxpg.StringProperty( _("Line Name"),  value= _("line Name") ) )
        pg.Append( wxpg.FloatProperty( _("Line Alpha"),      value= 1 ) )
        pg.Append( wxpg.BoolProperty( _("Line Animated"),  value= False ) )
        pg.Append( wxpg.BoolProperty( _("Line Antialiased"), value= False ) )
        pg.Append( wxpg.BoolProperty( _("Line Clip_on"),     value= False) )
        pg.SetPropertyAttribute( _("Line Animated"),    "UseCheckbox", True)
        pg.SetPropertyAttribute( _("Line Antialiased"), "UseCheckbox", True)
        pg.SetPropertyAttribute( _("Line Clip_on"),     "UseCheckbox", True)
        pg.Append( wxpg.ColourProperty( _("Line Colour"), value= (0,0,0) ) )
        pg.Append( wxpg.EnumProperty( _("Line Dash_capstyle"),_("Line Dash_capstyle"),
                                        ['butt','round', 'projecting'],
                                        [0, 1, 2],  0))
        pg.Append( wxpg.EnumProperty( _("Line Dash_joinstyle"),_("Line Dash_joinstyle"),
                                        ['miter','round','bevel'],
                                        [0, 1, 2],  0))
        pg.Append( wxpg.EnumProperty( _("Line Fillstyle"),_("Line Fillstyle"),
                                        ['full','left','right','bottom','top','none'],
                                        range(6),  0))
        pg.Append( wxpg.IntProperty( _("Line Width"),  value= 1 ) )
        pg.Append( wxpg.EnumProperty( _("Line Style"),_("Line Style"),
                                        ['-','--','-.',':'],
                                        [0, 1, 2, 3],  0))
        pg.Append( wxpg.BoolProperty( _("Line Lod"),  value= False ) )
        pg.SetPropertyAttribute( _("Line Lod"),    "UseCheckbox", True)
        pg.Append( wxpg.EnumProperty( _("Line Rasterized"),_("Line Rasterized"),
                                        ['True','Fase','None'],
                                        range(3),  0))
        pg.Append( wxpg.BoolProperty( _("Line Shown"), value= False) )
        pg.SetPropertyAttribute( _("Line Shown"), "UseCheckbox", True)
        pg.Append( wxpg.PropertyCategory( _("2- Marker Properties")) )
        markers=[".",",","o","v","^","<",">",
                 "1","2","3","4","8",
                 "s","p","*","h","H",
                 "+","x","D","d","|","_",
                 "TICKLEFT","TICKRIGHT","TICKUP","TICKDOWN",
                 "CARETLEFT","CARETRIGHT","CARETUP","CARETDOWN","None"]
        pg.Append( wxpg.EnumProperty( _("Marker Style"),_("Marker Style"),
                                        markers,
                                        range(len(markers)),  len(markers)-1))

        pg.Append( wxpg.IntProperty( _("Marker Size"),  value= 1 ) )
        bSizer21.Add( pg, 1,  wx.ALL|wx.EXPAND, 5 )
        #bSizer21.Fit(self)


        sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"Add ReferenceLine") ), wx.VERTICAL )

        fgSizer1 = wx.FlexGridSizer( 0, 3, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.HorLineTxtCtrl = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), 0 )
        fgSizer1.Add( self.HorLineTxtCtrl, 0, wx.ALL, 5 )

        self.m_button51 = wx.Button( self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        fgSizer1.Add( self.m_button51, 0, wx.TOP, 5 )

        self.m_staticText131 = wx.StaticText( self, wx.ID_ANY, _(u"Horizontal"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText131.Wrap( -1 )
        fgSizer1.Add( self.m_staticText131, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.HorVerTxtCtrl = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), 0 )
        fgSizer1.Add( self.HorVerTxtCtrl, 0, wx.ALL, 5 )

        self.m_button511 = wx.Button( self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size( 20,-1 ), 0 )
        fgSizer1.Add( self.m_button511, 0, wx.TOP, 5 )

        self.m_staticText14 = wx.StaticText( self, wx.ID_ANY, _(u"Vertical"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText14.Wrap( -1 )
        fgSizer1.Add( self.m_staticText14, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        sbSizer9.Add( fgSizer1, 1, wx.EXPAND, 5 )

        bSizer21.Add( sbSizer9, 0, 0, 5 )

        self.SetSizer( bSizer21 )
        self.Layout()
        bSizer21.Fit( self )
        self._OnRefreshLines( None)
        if not self.__createPgDispatcher():
            raise StandardError("Cannot create the graph dispatcher")
        pg.Bind( wxpg.EVT_PG_CHANGED, self.__OnPropGridChange )
        self._BindEvents()

    def __createPgDispatcher( self):
        self.__dispatcher=  dispatcher = dict()
        dispatcher[ _("Line Name")]= self.__OnLineChange
        dispatcher[ _("Line Alpha")]= self.__OnLineChange
        dispatcher[ _("Line Animated")]= self.__OnLineChange
        dispatcher[ _("Line Antialiased")]= self.__OnLineChange
        dispatcher[ _("Line Clip_on")]= self.__OnLineChange
        dispatcher[ _("Line Colour")]= self.__OnLineChange
        dispatcher[ _("Line Dash_capstyle")]= self.__OnLineChange
        dispatcher[ _("Line Dash_joinstyle")]= self.__OnLineChange
        dispatcher[ _("Line Fillstyle")]= self.__OnLineChange
        dispatcher[ _("Line Width")]= self.__OnLineChange
        dispatcher[ _("Line Style")]= self.__OnLineChange
        dispatcher[ _("Line Lod")]= self.__OnLineChange
        dispatcher[ _("Line Rasterized")]= self.__OnLineChange
        dispatcher[ _("Line Shown")]= self.__OnLineChange

        dispatcher[ _("Marker style")]= self.__OnMarkerChange
        dispatcher[ _("Marker size")]= self.__OnMarkerChange
        return True
    @property
    def currLine(self):
        return self.__currLine
    @currLine.setter
    def currLine(self, line):
        self.__currLine= line
    def __OnLineChange(self, evt):
        """the line data from the user input has changed"""
        # cheking for the current selected line
        # ----missing
        pg0 = self.pg.GetPage(0)
        # reading the data contained in the pg line
        newattrs= dict()
        for keyi  in [key for key in self.__dispatcher.keys() if key.startswith( _('Line'))]:
            # +1 to remove the space character from the key
            newattrs[keyi[ len( _('Line'))+1: ].lower()]= pg0.GetProperty(keyi).m_value
        # applying the new properties to the selected line
        # missing
        evt.Skip()

    def __OnMarkerChange(self, evt):
        evt.Skip()

    def __OnPropGridChange(self, evt):
            p = evt.GetProperty()
            if p:
                self.__dispatcher[p.GetName()](evt, p.GetValue())

    def _BindEvents( self):
        self.m_listBox1.Bind(   wx.EVT_LISTBOX,  self._OnListLinesChange )
        self.m_button87.Bind(   wx.EVT_BUTTON,   self._OnLineDel )
        self.m_button41.Bind(   wx.EVT_BUTTON,   self._OnRefreshLines )
        #self.plt_textCtr8.Bind( wx.EVT_TEXT_ENTER, self._OnLineNameChange )
        #self.m_choice7.Bind(    wx.EVT_CHOICE,   self._OnLineWidthChange )
        #self.m_button12.Bind(   wx.EVT_BUTTON,   self._OnLineColourChange )
        #self.m_choice4.Bind(    wx.EVT_CHOICE,   self._OnLineStyleChange )
        #self.m_choice6.Bind(    wx.EVT_CHOICE,   self._OnLineMarkerStyleChange )
        #self.m_choice8.Bind(    wx.EVT_CHOICE,   self._OnLineMarkerSizeChange )
        #self.m_checkBox4.Bind(  wx.EVT_CHECKBOX, self._OnLineVisibleChange )
        ###self.HorLineTxtCtrl.Bind( wx.EVT_TEXT,   self._OnTxtRefLineHorzChange )
        self.m_button51.Bind(   wx.EVT_BUTTON,   self._OnAddRefHorzLine )
        #self.HorVerTxtCtrl.Bind( wx.EVT_TEXT,    self._OnTxtRefLineVerChange )
        self.m_button511.Bind(  wx.EVT_BUTTON,   self._OnAddRefVertLine )

    def _setItems(self):
        return
        if self.plt.gca() == None:
            return
        lineListNames= [line.get_label() for line in self.plt.gca().get_lines()]
        self.m_listBox1.SetItems( lineListNames)
        self.m_choice7.SetItems( lineSizes)
        self.m_choice4.SetItems( lineStyles)
        self.m_choice6.SetItems( markerStyles)
        self.m_choice8.SetItems( markerSizes)

    def _updateLineSelectionPane(self, evt):
        """updating the contents of the pg scroll panel 2 from the content int the draw"""
        # current line selected:
        try:
            lineNumber= evt.GetInt()
        except:
            # se recomienda actualizar las lineas de la grafica
            return # No hay lineas seleccionadas

        # getting the list of lines
        self.currLine= self.plt.gca().get_lines()[lineNumber]
        if self.currLine == None:
            evt.Skip()
            return
        def find(texto, data):
            for pos, dat in enumerate(data):
                if texto == dat:
                    return pos
            return None
        selectedLine= self.currLine
        result= dict()
        result[_('Line Name')] =        selectedLine.get_label()
        result[_('Line Alpha')] =       selectedLine.get_alpha()
        result[_("Line Animated")] =    selectedLine.get_animated()
        result[_("Line Antialiased")] = selectedLine.get_antialiased()
        result[_("Line Clip_on")] =     selectedLine.get_clip_on()
        color= selectedLine.get_color()

        if isinstance(color, (str, unicode)):
            color= [col*255 for col in self.colorConverter.to_rgba(color)]
            color= wx.Colour(*color)
        result[_('Line Colour')] =      color,
        result[_('Line Dash_capstyle')] = find(selectedLine.get_dash_capstyle(), ['butt','round', 'projecting'])
        result[_('Line Dash_joinstyle')] = find(selectedLine.get_dash_joinstyle(), ['miter','round','bevel'])
        result[_('Line Fillstyle')] =   find(selectedLine.get_fillstyle(), ['full','left','right','bottom','top','none'])
        result[_('Line Width')] =       float(selectedLine.get_linewidth())
        result[_('Line Style')] =       find(selectedLine.get_linestyle(), ['-','--','-.',':'])
        result[_('Line Lod')] =         selectedLine._lod
        result[_('Line Rasterized')] =  find(selectedLine.get_rasterized(), ['True','Fase','None'])
        result[_('Line Shown')] =       selectedLine.get_visible()
        pg0= self.pg.GetPage(0)
        pg0.GetProperty(_("Line Alpha")).m_value
        markers=[".",",","o","v","^","<",">",
                 "1","2","3","4","8",
                 "s","p","*","h","H",
                 "+","x","D","d","|","_",
                 "TICKLEFT","TICKRIGHT","TICKUP","TICKDOWN",
                 "CARETLEFT","CARETRIGHT","CARETUP","CARETDOWN","None"]
        result[_('Marker Style')] =        find(selectedLine.get_marker(), markers)
        result[_('Marker Size')] =         float(selectedLine.get_markersize())

        # updating the pg data
        pg0= self.pg.GetPage(0)
        for key, value in  result.items():
            if key in [_('Line Colour')]:
                pg0.SetPropertyValue(_(key), value[0])
            else:
                pg0.SetPropertyValue(_(key), value)

    def _OnListLinesChange( self, evt ):
        self._updateLineSelectionPane(evt)

    def _OnLineDel(self,event):
        if len(self.plt.gca().get_lines())== 0:
            return
        selectedLine= self.plt.gca().get_lines()[self.m_listBox1.GetSelection()]
        selectedLine.remove()
        # se actualiza la linea seleccionada
        self._OnRefreshLines(None)
        self.figpanel.canvas.draw()

    def _OnRefreshLines( self, evt ):
        if len(self.plt.gca().get_lines())== 0:
            self.m_listBox1.SetItems([])
            return
        lineListNames= [line.get_label() for line in self.plt.gca().get_lines()]
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
        selectedLine= self.plt.gca().get_lines()[self.m_listBox1.GetSelection()]
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
        lineSelected = self.plt.gca().get_lines()[actualLineNumber]
        colors = [getattr(data.Colour,param)/float(255) for param in ['red','green','blue','alpha']]
        lineSelected.set_color(colors)
        self.figpanel.canvas.draw()

    def _OnLineStyleChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.plt.gca().get_lines()[actualLineNumber]
        newStyle = evt.GetString()
        lineSelected.set_linestyle(newStyle)
        self.figpanel.canvas.draw()

    def _OnLineMarkerStyleChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.plt.gca().get_lines()[actualLineNumber]

        newMarkerStyle = evt.GetString()
        lineSelected.set_marker(newMarkerStyle)

        self.figpanel.canvas.draw()

    def _OnLineMarkerSizeChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.plt.gca().get_lines()[actualLineNumber]

        newMarkerSize = float(evt.GetString())
        lineSelected.set_markersize(newMarkerSize)

        self.figpanel.canvas.draw()

    def _OnLineVisibleChange( self, evt ):
        if len(self.m_listBox1.Items) == 0 or \
           self.m_listBox1.GetSelection() == -1:
            return
        actualLineNumber= self.m_listBox1.GetSelection()
        lineSelected = self.plt.gca().get_lines()[actualLineNumber]
        visible = evt.Checked()
        lineSelected.set_visible(visible)
        self.figpanel.canvas.draw()

    def _OnAddRefHorzLine( self, evt, **params ):
        print '# adding reference horizontal line'
        if params.has_key('ypos'):
            ypos = params.pop('ypos')
            self.plt.gca().hold(True)
            # _('plt.gca().hold(True)', False)

            line= self.plt.axhline(ypos)
            print 'line= plt.axhline('+ypos.__str__()+')'
            self.plt.hold(False)
            # _('plt.gca().hold(False)', False)
        else:
            try:
                ypos= self.HorLineTxtCtrl.GetValue()
                if ypos== None:
                    return
                self.plt.hold(True)
                print 'plt.hold(True)'
                line= self.plt.axhline(ypos)
                print 'plt.axhline('+ypos.__str__()+')'
                self.plt.hold(False)
                print 'plt.hold(False)'
                self.HorLineTxtCtrl.SetValue('')
                self._OnRefreshLines(None)
            except:
                return
        if params.has_key('color'):
            line.set_color(params['color'])
            print 'line.set_color('+"'"+params['color'].__str__()+"'"+')'
        self.figpanel.canvas.draw()
        # _('plt.draw()',False)

    def _OnAddRefVertLine( self, evt ):
        print '# adding reference vertical line'
        xpos= self.HorVerTxtCtrl.GetValue()
        if xpos == None:
            return

        self.plt.hold(True)
        print 'plt.gca().hold(True)'
        self.plt.axvline(xpos)
        print 'plt.gca().axvline('+xpos.__str__()+')'
        self.plt.hold(False)
        print 'plt.hold(False)'
        self.figpanel.canvas.draw()
        self.HorVerTxtCtrl.SetValue('')
        self._OnRefreshLines(None)
        self.figpanel.canvas.draw()

class scrolled3(wx.ScrolledWindow):
    def __init__( self,pltobj, *args, **params):
        wx.ScrolledWindow.__init__(self, *args[1:], **params)
        self.figpanel= self.Parent.Parent.figpanel
        self.plt= pltobj
        try:
            self._ = wx.GetApp()._
        except AttributeError:
            self._= _
        graphParams= args[0]
        self.gca= self.plt.gca()

        if params.has_key('parent'):
            parent= params['parent']
        else:
            parent = args[1]

        self.SetScrollRate( 5, 5 )
        bSizer3 = wx.BoxSizer( wx.VERTICAL )

        sbSizer15 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _( u"Choose a patchs") ), wx.VERTICAL )

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

        self.m_button11 = wx.Button( self, wx.ID_ANY, _(u"Refresh Patchs"), wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer6.Add( self.m_button11, 0, wx.LEFT, 5 )

        sbSizer15.Add( fgSizer6, 1, wx.EXPAND, 5 )

        bSizer3.Add( sbSizer15, 0, 0, 5 )

        sbSizer16 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"Some Properties") ), wx.VERTICAL )

        self.m_staticText28 = wx.StaticText( self, wx.ID_ANY, _(u"Patch Name"), wx.DefaultPosition, wx.DefaultSize, 0 )
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

        self.m_staticText29 = wx.StaticText( self, wx.ID_ANY, _(u"Face Colour"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText29.Wrap( -1 )
        fgSizer7.Add( self.m_staticText29, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        m_choice14Choices = []
        self.m_choice14 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 70,-1 ), m_choice14Choices, 0 )
        self.m_choice14.SetSelection( 0 )
        fgSizer7.Add( self.m_choice14, 0, wx.ALL, 5 )

        self.m_staticText30 = wx.StaticText( self, wx.ID_ANY, _(u"Alpha"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText30.Wrap( -1 )
        fgSizer7.Add( self.m_staticText30, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        sbSizer16.Add( fgSizer7, 1, wx.EXPAND, 5 )

        bSizer3.Add( sbSizer16, 0, 0, 5 )

        sbSizer12 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, _(u"add an span") ), wx.VERTICAL )

        sbSizer13 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )

        fgSizer4 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer4.SetFlexibleDirection( wx.BOTH )
        fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText15 = wx.StaticText( self, wx.ID_ANY, _(u"Horizontal"), wx.DefaultPosition, wx.DefaultSize, 0 )
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

        self.m_staticText17 = wx.StaticText( self, wx.ID_ANY, _(u"Y axis position 1"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText17.Wrap( -1 )
        fgSizer3.Add( self.m_staticText17, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        self.plt_textCtr12 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.plt_textCtr12.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer3.Add( self.plt_textCtr12, 0, wx.ALL, 5 )

        self.m_staticText16 = wx.StaticText( self, wx.ID_ANY, _(u"Y axis position 2"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText16.Wrap( -1 )
        fgSizer3.Add( self.m_staticText16, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_choice81Choices = []
        self.m_choice81 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice81Choices, 0 )
        self.m_choice81.SetSelection( 0 )
        self.m_choice81.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer3.Add( self.m_choice81, 0, wx.ALL, 5 )

        self.m_staticText22 = wx.StaticText( self, wx.ID_ANY, _(u"Face Colour"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText22.Wrap( -1 )
        fgSizer3.Add( self.m_staticText22, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_choice12Choices = []
        self.m_choice12 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice12Choices, 0 )
        self.m_choice12.SetSelection( 0 )
        self.m_choice12.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer3.Add( self.m_choice12, 0, wx.ALL, 5 )

        self.m_staticText26 = wx.StaticText( self, wx.ID_ANY, _(u"Alpha"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText26.Wrap( -1 )
        fgSizer3.Add( self.m_staticText26, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )


        sbSizer13.Add( fgSizer3, 0, 0, 5 )


        sbSizer12.Add( sbSizer13, 0, 0, 5 )

        sbSizer14 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )

        fgSizer5 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer5.SetFlexibleDirection( wx.BOTH )
        fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText19 = wx.StaticText( self, wx.ID_ANY, _(u"Vertical"), wx.DefaultPosition, wx.DefaultSize, 0 )
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

        self.m_staticText20 = wx.StaticText( self, wx.ID_ANY, _(u"X axis position 1"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText20.Wrap( -1 )
        gSizer3.Add( self.m_staticText20, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        self.plt_textCtr14 = NumTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.plt_textCtr14.SetMinSize( wx.Size( 60,-1 ) )

        gSizer3.Add( self.plt_textCtr14, 0, wx.ALL, 5 )

        self.m_staticText21 = wx.StaticText( self, wx.ID_ANY, _(u"X axis position 2"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText21.Wrap( -1 )
        gSizer3.Add( self.m_staticText21, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_choice10Choices = []
        self.m_choice10 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice10Choices, 0 )
        self.m_choice10.SetSelection( 0 )
        self.m_choice10.SetMinSize( wx.Size( 60,-1 ) )

        gSizer3.Add( self.m_choice10, 0, wx.ALL, 5 )

        self.m_staticText24 = wx.StaticText( self, wx.ID_ANY, _(u"Face Colour"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText24.Wrap( -1 )
        gSizer3.Add( self.m_staticText24, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5 )

        m_choice11Choices = []
        self.m_choice11 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice11Choices, 0 )
        self.m_choice11.SetSelection( 0 )
        self.m_choice11.SetMinSize( wx.Size( 60,-1 ) )

        gSizer3.Add( self.m_choice11, 0, wx.ALL, 5 )

        self.m_staticText25 = wx.StaticText( self, wx.ID_ANY, _(u"Alpha"), wx.DefaultPosition, wx.DefaultSize, 0 )
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
        for patch in self.plt.gca().patches:
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
        print '# adding horizontal span'
        pos1 = self.plt_textCtr11.GetValue()
        pos2 = self.plt_textCtr12.GetValue()
        if pos1 == None or pos2 == None:
            return

        print 'pos1= ' + pos1.__str__()
        print 'pos2= ' + pos2.__str__()

        faceColor= self.m_choice81.GetItems()[self.m_choice81.GetSelection()]
        print 'faceColor= '+"'"+faceColor.__str__()+"'"

        Alpha= float(self.m_choice12.GetItems()[self.m_choice12.GetSelection()])
        print 'Alpha= '+Alpha.__str__()

        patch= self.plt.axhspan( pos1, pos2, facecolor = faceColor, alpha = Alpha)
        print 'patch= plt.axhspan(pos1,pos2, facecolor= faceColor, alpha= Alpha)'
        patch.set_gid(wx.NewId())
        self._patchListboxUpdate()
        self.figpanel.canvas.draw()

    def _OnAddVerSpan( self, event):
        print'# adding vertical span'
        pos1 = self.plt_textCtr13.GetValue()
        pos2 = self.plt_textCtr14.GetValue()
        try:
            pos1= float(pos1)
            pos2= float(pos2)
        except:
            return
        print'pos1= ' + pos1.__str__()
        print'pos2= ' + pos2.__str__()

        faceColor= self.m_choice10.GetItems()[self.m_choice10.GetSelection()]
        print 'faceColor= '+"'"+faceColor.__str__()+"'"

        Alpha= str(self.m_choice11.GetItems()[self.m_choice11.GetSelection()])
        print 'Alpha= '+Alpha.__str__()

        patch= self.plt.axvspan(pos1,pos2,facecolor= faceColor, alpha= Alpha)
        print 'patch= plt.axvspan(pos1,pos2,facecolor= faceColor, alpha= Alpha)'
        patch.set_gid(wx.NewId())
        self._patchListboxUpdate()
        self.figpanel.canvas.draw()

    def _patchListboxUpdate(self, *args):
        # se lista todos los patch
        if self.plt.gca()== None:
            return
        patches = self.plt.gca().patches
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
        for patch in self.plt.gca().patches:
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
        for patch in self.plt.gca().patches:
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
        for patch in self.plt.gca().patches:
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
        self.dialog=    _dialog    # to create de dialod
        self.log=       self.app.Logg   # to report
        self.outputGrid= self.app.output # the usern can use the plot functions
        self.data2Plotdiaglog= data2Plotdiaglog
        self.selectDialogData2plot= selectDialogData2plot
        self.scatterDialog = scatterDialog
    @property
    def grid(self):
        cs= wx.GetApp().frame.grid
        return cs
    def _updateColsInfo( self):
        # selectign the last selected panel
        gridCol = self.grid.GetUsedCols()
        self.columnNames = gridCol[0]
        self.columnNumbers= gridCol[1]
        #gridCol=            self.grid.GetUsedCols()
        #self.columnNames=   gridCol[0]
        #self.columnNumbers= gridCol[1]
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
        self._=          wx.GetApp()._
        if 0:
            self.dialog=         _dialog         # to create de dialog
            self.grid=           self.app.grid
            self.outputGrid=     self.app.output # the usern can use the plot functions
        self.data2Plotdiaglog=   data2Plotdiaglog
        self.selectDialogData2plot= selectDialogData2plot
        self.scatterDialog=      scatterDialog

    def __init__( self, parent= None, *args, **params):
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
                                CaptionVisible(True).Caption(_(u"Graph")).Centre().
                                MaximizeButton(True).MinimizeButton(False).Resizable(True).
                                PaneBorder( False ).CloseButton( False ))

            self.m_mgr.AddPane( self.m_notebook1, aui.AuiPaneInfo().Left().
                                CaptionVisible(True).Caption(_(u"Graph Properties")).CaptionVisible(True).
                                MaximizeButton(True).MinimizeButton(False).Resizable(True).
                                PaneBorder( False ).CloseButton( False ). BestSize(wx.Size(200,-1)))

        self.scrolledWindow1= scrolled1(self,  self.graphParams, self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL)
        self.scrolledWindow2= scrolled2(self, self.graphParams, self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL)
        self.scrolledWindow3= scrolled3(self, self.graphParams, self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL)

        self.m_notebook1.AddPage( self.scrolledWindow1, _( u"Main Options"), True )
        self.m_notebook1.AddPage( self.scrolledWindow2, _( u"Lines"), False )
        self.m_notebook1.AddPage( self.scrolledWindow3, _( u"patches"), False )

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

    # compatibility
    def show(self,*args, **params):
        return self.Show(*args, **params)
    def subplot(self, *args, **params):
        return self.add_subplot(*args, **params)
    def subplots(self):
        return self.get_axes()
    @property
    def title(self):
        return self.get_title()
    @title.setter
    def title(self,*args, **params):
        return self.set_title(*args, **params)
    @property
    def xlabel(self):
        return self.get_xlabel()
    @xlabel.setter
    def xlabel(self, *args, **params):
        return self.set_xlabel(*args, **params)
    @property
    def ylabel(self):
        return self.get_ylabel()
    @ylabel.setter
    def ylabel(self, *args, **params):
        return self.set_ylabel(*args, **params)
    @property
    def xlim(self):
        return self.get_xlim()
    @xlim.setter
    def xlim(self,*args, **params):
        return self.set_xlim(*args, **params)
    @property
    def ylim(self):
        return self.get_ylim()
    @ylim.setter
    def ylim(self,*args, **params):
        return self.set_ylim(*args, **params)

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
                self.scrolledWindow1._Update()
                ##self.scrolledWindow1.plt_textCtr2.Value= self.plt.xlabel
                # clear ylabel ctrl
                ##self.scrolledWindow1.plt_textCtr3.Value= self.plt.ylabel
                # clear title
                ##self.scrolledWindow1.plt_textCtr1.Value= self.plt.title
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
            try:
                return self.figpanel.__getattribute__(name)
            except AttributeError:
                return self.figpanel.gca().__getattribute__(name)

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
        pg0= self.scrolledWindow1.pg.GetPage(0)
        if evt.inaxes and pg0.GetProperty(_("View cursor")).m_value:
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
    app._= _
    app.Logg= log()
    # instantiate the Matplotlib wxFrame
    plt = pltobj( None,)# xlabel = "", ylabel = u"value", title= u"Titulo" )
    plt.delaxes( plt.gca())
    ax1= plt.add_subplot( 2, 1, 1)
    x= range( 20)
    y= [x1+3 for x1 in x]
    ax1.plot( range( 20), y, 'b*')
    ax2= plt.add_subplot( 2,1,2)
    ax2.plot( range( 10), range( 10),'r+')
    plt.gca()
    # update the controls
    plt.updateControls()
    # show it
    plt.Show( True)
    app.MainLoop()
