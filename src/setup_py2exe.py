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

distdir = '..\\..\\SalStatdist'
iconPath = "salstat.ico"

opts = { "py2exe":
            { "unbuffered": True,
              "optimize": 1,
              "includes": ["wx",
                           "numpy",
                           "matplotlib",
                           "matplotlib.backends",
                           "matplotlib.backends.backend_qt4agg",
                           "PyQt4",
                           "statFunctions.*",  # importing the statistical functions
                           "plotFunctions.*", #       "statsmodels.*",
                           "scipy.interpolate",
                           "scipy.stats" 
                           ],
              "excludes":['_gtkagg',       '_tkagg',             '_agg2',
                          '_fltkagg',      '_gtk',               '_gtkcairo',
                          "pywin",         "pywin.debugger",     "pywin.debugger.dbgcon",
                          "pywin.dialogs", "pywin.dialogs.list", "Tkconstants",
                          "Tkinter",       "tcl",                "scipy.sparce",
                           '_cairo',       '_cocoaagg',          ], # "scipy.optimize",
              "dist_dir": distdir,
              "dll_excludes" : ['_gtkagg', 
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
                                "WS2_32.dll",
                                "mfc90.dll",
                                "RPCRT4.dll",
                                "VERSION.dll",
                                "KERNEL32.dll",
                                "UxTheme.dll",
                                ]
              }
          }

setup(name=         'S2',
      version=      '2.1',
      description=  'Statistics Package',
      url=          'http://code.google.com/p/salstat-statistics-package-2/',
      license=      'GPL 3',
      windows=[
          {"script":         'salstat.py',
           "icon_resources": [(0, iconPath)]
           }
          ],
      data_files= matplotlib.get_py2exe_datafiles(),
      zipfile = None,
      options = opts,
      )
