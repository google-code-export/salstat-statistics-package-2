import wx
import sys

# Application Information
APP = "salstat.py"
NAME = 'SalStat'
VERSION = '2.2'
PACKAGES = ['']
URL = 'http://code.google.com/p/salstat-statistics-package-2/'
LICENSE = 'GPL 2'
AUTHOR = 'Sebastian lopez, S2 Team'
AUTHOR_EMAIL = 'selobu@gmail.com'
DESCRIPTION = 'Statistics Package'
YEAR = 2012
# End of Application Information


def BuildOSXApp():
    """
    Build the OSX Applet
    """

    from setuptools import setup

    # py2app uses this to generate the plist xml for the applet
    copyright = "Copyright %s %s" % (AUTHOR, YEAR)
    appid = "com.%s.%s" % (NAME, NAME)
    PLIST = dict(CFBundleName = NAME,
            CFBundleIconFile = 'salstat.ico',
            CFBundleShortVersionString = VERSION,
            CFBundleGetInfoString = NAME + " " + VERSION,
            CFBundleExecutable = NAME,
            CFBundleIdentifier = appid,
            CFBundleTypeMIMETypes = ['text/plain'],
            CFBundleDevelopmentRegion = 'English',
            NSHumanReadableCopyright = copyright
    )
    PY2APP_OPTS = dict(iconfile = "salstat.ico",
    argv_emulation = True,
    plist = PLIST)
    setup(
        app = [APP,],
        version = VERSION,
        options = dict( py2app = PY2APP_OPTS),
        description = NAME,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        url = URL,
        setup_requires = ['py2app'],
    )


if __name__ == '__main__':
    if wx.Platform == '__WXMAC__':
        # OS X
        BuildOSXApp()
    else:
        print "Unsupported platform: %s" % wx.Platform
