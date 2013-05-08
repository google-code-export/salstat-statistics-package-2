#-------------------------
# try to import win32com
# to be used into excel 

# ModuleFinder can't handle runtime changes to __path__, but win32com uses them
try:
    # py2exe 0.6.4 introduced a replacement modulefinder.
    # This means we have to add package paths there, not to the built-in
    # one.  If this new modulefinder gets integrated into Python, then
    # we might be able to revert this some day.
    # if this doesn't work, try import modulefinder
    try:
        import py2exe.mf as modulefinder
    except ImportError:
        import modulefinder
    import win32com, sys
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell"]: #,"win32com.mapi"
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass
#-------------------------

from distutils.core import setup
import py2exe
import matplotlib
import sqlalchemy

distdir = '..\\..\\campo'
iconPath = "salstat.ico"

opts = { "py2exe":
            { "unbuffered": True,
              "optimize": 1,
              "includes": ["wx",
                           "numpy",
                           "matplotlib",
                           "matplotlib.backends",
                           "matplotlib.backends.backend_qt4agg",
                           'matplotlib.backends.backend_tkagg', # matplotlib 1.2
                           "PyQt4",
                           "statFunctions.*",  # importing the statistical functions
                           "plotFunctions.*", 
                           "statsmodels.*",
                           "scipy.interpolate",
                           "scipy.stats",
                           "sqlalchemy",
                           "sqlalchemy.dialects.sqlite",
                           "sqlalchemy.dialects.mysql", "mysql", # mysql is a connector library
                           ],
              "excludes":['_gtkagg',       '_tkagg',             '_agg2',    
                          '_fltkagg',      '_gtk',               '_gtkcairo',
                          "pywin",         "pywin.debugger",     "pywin.debugger.dbgcon",
                          "pywin.dialogs", "pywin.dialogs.list",  "scipy.sparce",
                          #"Tkinter",       "tcl",               "Tkconstants", 
                           '_cairo',       '_cocoaagg',          ], # "scipy.optimize",
              "dist_dir": distdir,
              "dll_excludes" : ['_gtkagg',
                                "libzmq.dll",
                                "libzmq.pyd",
                                '_tkagg',
                                "MSVCP90.DLL",
                                "API-MS-Win-Security-Base-L1-1-0.dll",
                                "API-MS-Win-Security-Base-L1-1-0.dll",
                                "API-MS-Win-Core-ProcessThreads-L1-1-0.dll",
                                "POWRPROF.dll",
                                "API-MS-Win-Core-LocalRegistry-L1-1-0.dll",
                                "OLEAUT32.dll",
                                "USER32.dll",
                                "COMCTL32.dll",
                                "SHELL32.dll",
                                "ole32.dll",
                                "WINMM.dll",
                                "WSOCK32.dll",
                                "COMDLG32.dll",
                                "ADVAPI32.dll",
                                "GDI32.dll",
                                "msvcrt.dll",
                                "NETAPI32.dll",
                                "IMM32.dll",
                                "MPR.dll",
                                "ntdll.dll",
                                "WS2_32.dll",
                                "mfc90.dll",
                                "RPCRT4.dll",
                                "VERSION.dll",
                                "WINSPOOL.DRV",
                                "KERNEL32.dll",
                                "UxTheme.dll",
                                ]
              }
          }

setup(name=         'S2',
      version=      '0.1',
      description=  'Campo adquisition data',
      url=          '',
      license=      'privativa',
      windows=[
          {"script":         'main.py',
           "icon_resources": [(0, iconPath)]
           }
          ],
      data_files= matplotlib.get_py2exe_datafiles(),
      zipfile = None,
      options = opts,
      )
