import matplotlib.pyplot as plt
import numpy as np
from matplotlib.image import BboxImage

from matplotlib._png import read_png
import matplotlib.colors

from matplotlib.transforms import Bbox, TransformedBbox
from matplotlib.ticker import ScalarFormatter

import os.path

class _RibbonBox(object):
    def __init__(self, color, figName, 
                 path='.//images//barplot//'):
        
        print str(os.path.relpath(  path + figName + '.png'))
        self.original_image = read_png( str(os.path.relpath(
                    path + figName + '.png')))
        
        self.cut_location = 70
        self.b_and_h= self.original_image[:,:,2]
        self.color=   self.original_image[:,:,2] - self.original_image[:,:,0]
        self.alpha=   self.original_image[:,:,3]
        self.nx=      self.original_image.shape[1]
        
        rgb= matplotlib.colors.colorConverter.to_rgb(color)
        im=  np.empty(self.original_image.shape,
                      self.original_image.dtype)
        im[:,:,:3]  = self.b_and_h[:,:,np.newaxis]
        im[:,:,:3] -= self.color[:,:,np.newaxis]*(1.-np.array(rgb))
        im[:,:,3]   = self.alpha
        self.im = im

    def get_stretched_image(self, stretch_factor):
        stretch_factor = max(stretch_factor, 1)
        ny, nx, nch = self.im.shape
        ny2 = int(ny*stretch_factor)
        stretched_image = np.empty((ny2, nx, nch),
                                   self.im.dtype)
        cut = self.im[self.cut_location,:,:]
        stretched_image[:,:,:] = cut
        stretched_image[:self.cut_location,:,:] = \
                self.im[:self.cut_location,:,:]
        stretched_image[-(ny-self.cut_location):,:,:] = \
                self.im[-(ny-self.cut_location):,:,:]
        self._cached_im = stretched_image
        return stretched_image

class _RibbonBoxImage(BboxImage):
    zorder = 1
    def __init__(self, bbox, color,
                 figName= 'redunca01',
                 path=  None,
                 cmap=  None,
                 norm=  None,
                 interpolation=None,
                 origin=       None,
                 filternorm=   1,
                 filterrad=    4.0,
                 resample=     False,
                 **kwargs
                 ):
        BboxImage.__init__(self, bbox,
                           cmap = cmap,
                           norm = norm,
                           interpolation=interpolation,
                           origin=origin,
                           filternorm=filternorm,
                           filterrad=filterrad,
                           resample = resample,
                           **kwargs
                           )
        self._ribbonbox = _RibbonBox( color, figName, path)
        self._cached_ny = None

    def draw(self, renderer, *args, **kwargs):
        bbox = self.get_window_extent(renderer)
        stretch_factor = bbox.height / bbox.width
        ny = int(stretch_factor*self._ribbonbox.nx)
        if self._cached_ny != ny:
            arr = self._ribbonbox.get_stretched_image(stretch_factor)
            self.set_array(arr)
            self._cached_ny = ny
        BboxImage.draw(self, renderer, *args, **kwargs)

def plothist(xdata= np.arange(4, 9), ydata= np.random.random(5), colors = 'random',figName='redunca03'):
    if len(xdata) != len(ydata):
        raise StandardError('xdata and ydata must have the same len()')
    # se generan los colores en forma aleatoria
    box_colors = _generatecolors(colors,len(xdata))   
    # se genera la figura
    fig = plt.gcf()
    fig.clf()
    ax = plt.subplot(111)
    fmt = ScalarFormatter(useOffset=False)
    ax.xaxis.set_major_formatter(fmt)
    for year, h, bc in zip(xdata, ydata, box_colors):
        bbox0 = Bbox.from_extents(year-0.48, 0.0, year+0.48, h) # year-0.4, 0., year+0.4, year-1 year+1
        bbox = TransformedBbox(bbox0, ax.transData)
        rb_patch = _RibbonBoxImage(bbox, bc, figName, path= './/images//histplot//', interpolation="bicubic")
        ax.add_artist(rb_patch)
        if 0:
            if type(h) == type(1):
                ax.annotate(r"%d" % h,
                        (year, h), va="bottom", ha="center")
            elif type(h) == type(1.1):
                ax.annotate(r"%f" % h,
                        (year, h), va="bottom", ha="center")
            elif str(type(h)) == "<type 'numpy.int32'>":
                ax.annotate(r"%d" % h,
                        (year, h), va="bottom", ha="center")
    patch_gradient = BboxImage(ax.bbox,
                               interpolation="bicubic",
                               zorder=0.1,
                               )
    gradient = np.zeros((2, 2, 4), dtype=np.float)
    gradient[:,:,:3] = [1, 1, 1]
    gradient[:,:,3] = [[0.2, 0.3],[0.2, 0.5]] # alpha channel
    patch_gradient.set_array(gradient)
    ax.add_artist(patch_gradient)
    ax.set_xlim(xdata[0]-1.0, xdata[-1]+1.0)
    # se determinan los limites para el eje Y
    try:
        ydatamax = ydata.max() # en el caso de informacion proveniente de numpy
    except AttributeError:
        ydatamax = max(ydata)
    if ydatamax > 0.0:
        maxYlimit = ydatamax*1.05
    elif ydatamax == 0.0:
        maxYlimit = 1.0
    else:
        maxYlimit = ydatamax*(1.0-0.05)
    ax.set_ylim(0, maxYlimit)
    return (fig,plt)

def _generatecolors(colors, ndata):
    if isinstance(colors,(str,unicode)):
        colors= [colors.upper() for i in range(ndata)]
    else:
        colors= [color.upper() for color in colors]
    box_colors = ()
    for color in colors: 
        if color == u'RED':
            colori = (1.0, 0.0, 0.0)
        elif color == u'GREEN':
            colori = (0.0, 1.0, 0.0)
        elif color == u'BLUE':
            colori = (0.0, 0.0, 1.0)
        elif color == u'YELLOW':
            colori = (1.0, 1.0, 0.0)
        elif color == u'WHITE':
            colori = ( 1.0, 1.0, 1.0)
        elif color == u'BLACK':
            colori = ( 0.0, 0.0, 0.0)
        elif color == u'PINK':
            colori = (1.0, 0.0, 1.0)
        elif color == u'DARKBLUE':
            colori = (0.1, 0.0, 0.8)
        elif color == u'LIGTHGREEN':
            colori = (0.2, 1.0, 0.1)
        elif color == u'GREY':
            colori = (0.3, 0.5, 0.6)
        elif color == u'RANDOM':
            precisioncolor= 200
            color = list()
            colori= np.random.random_integers(0,precisioncolor,3)
            colori=(colori[0]/float(precisioncolor),colori[1]/float(precisioncolor),colori[2]/float(precisioncolor))
        else:
            colori = (0.1, 0.1, 0.1)
        box_colors += (colori,)
            
    return box_colors
    
def orderData(*params):
    newdata = list()
    for datos in params:
        newdatos = (quicksort(datos),)
        newdata += (newdatos)

def plotBar(ax=      None,
            xdata=   np.arange(4, 9),
            ydata=   np.random.random(5),
            labels=  None,
            colors=  'Random',
            figName= 'cilindro',
            path=    None):
    '''box_colors: 'random'|'blue'|'red'|'green'|'ligthgreen'|'darkblue'|'hsv'
    figure: redunca02|blue|aluminio|cilindro| 
    ''' 
    if len(xdata) != len(ydata):
        raise StandardError('xdata and ydata must have the same len()')
    
    if isinstance(figName,(str,unicode)):
        figName = [figName.lower() for i in range(len(xdata))]
    else:
        figName = [fig.lower() for fig in figName]
    ##xdata,ydata = orderData(xdata,ydata)
    # se generan los colores en forma aleatoria
    box_colors = _generatecolors(colors,len(xdata))           
    fig = plt.gcf()
    ## fig.clf()
    if ax == None:
        ax = plt.gca()## subplot(111)
    fmt = ScalarFormatter(useOffset=False)
    ax.xaxis.set_major_formatter(fmt)
    if labels== None:
        labels = [None for i in ydata]
    if path == None:
        path= './/images//barplot//'
    for year, h, bc,label,figi in zip(xdata, ydata, box_colors,labels,figName):
        bbox0 = Bbox.from_extents(year-0.5, 0., year+0.5, h) # year-0.4, 0., year+0.4,
        bbox = TransformedBbox(bbox0, ax.transData)
        rb_patch = _RibbonBoxImage(bbox, bc, figi, path, interpolation='bicubic') #bicubic
        ax.add_artist(rb_patch)
        if isinstance(label,(str,unicode)):
            ax.annotate(label, (year, h), va="bottom", ha="center")
            if type(labels) == type(1):
                ax.annotate(r"%d" % labels,
                        (year, labels), va="bottom", ha="center")
            elif type(labels) == type(1.1):
                ax.annotate(r"%f" % labels,
                        (year, labels), va="bottom", ha="center")
            elif str(type(labels)) == "<type 'numpy.int32'>":
                ax.annotate(r"%d" % labels,
                        (year, labels), va="bottom", ha="center")
    patch_gradient = BboxImage(ax.bbox,
                               interpolation= 'bicubic', # "bicubic"
                               zorder=0.1,
                               )
    gradient = np.zeros((2, 2, 4), dtype=np.float)
    gradient[:,:,:3] = [1, 1, 1]
    #gradient[:,:,:3] = [0.5, 0.5, 0.5]
    gradient[:,:,3] = [[0.2, 0.3],[0.2, 0.5]] # alpha channel
    patch_gradient.set_array(gradient)
    ax.add_artist(patch_gradient)
    ax.set_xlim(xdata[0]-0.5, xdata[-1]+0.5)
    # se determinan los limites para el eje Y
    if max(ydata) > 0.0:
        maxYlimit = max(ydata)*1.05
    elif max(ydata) == 0.0:
        maxYlimit = 1.0
    else:
        maxYlimit = max(ydata)*(1-0.05)
    ax.set_ylim(0, maxYlimit)
    return (fig, plt)

if __name__ == '__main__':
    fig,plot = plotBar(xdata= (1,2,3,4,8),
                       ydata = (1,8,5,4,10),
                       labels= ('MANZANA','DURAZNO','PERA','MANGO','LULO',),
                       colors= 'random',
                       figName= 'redunca'
                       )
    plot.show()
    fig,plot = plothist(xdata=  np.arange( 1, 40),
                        ydata=  np.arange( 2, 41), 
                        colors= 'blue',
                        figName= 'redunca')
    plot.show()
    # fig.savefig('D:\\proyecto Nice plot\\redunca\\histograma.png')