__author__ = 'Selobu'
def test():
    try:
        import wx
        if wx.__version__ < '2.9.4':
            raise ImportError("Required wx 2.9.4 at least")
    except ImportError:
        print wx.__version__
        raise ImportError("Required wx 2.9.4")
    # -----------------
    try:
        import numpy
    except ImportError:
        raise ImportError("numpy required")
    
    try:
        import scipy
        if scipy.__version__ < '0.11':
            raise ("scipy >= 0.11.0 required")
    except ImportError:
        raise ("scipy >= 0.11.0 required")
    
    try:
        import matplotlib
        if matplotlib.__version__ < '1.2.1':
            raise ("matplotlib >= 1.2.1 required")
    except ImportError:
        raise ImportError("matplotlib required")
    
    