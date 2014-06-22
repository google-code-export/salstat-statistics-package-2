__all__ = ['AUTHOR','VERSION','PROG_NAME','HOME_PAGE','CONTACT_MAIL', 'HOME']

import os
import sys
import wx
__ = wx.GetTranslation
HOME = os.getcwd().decode( sys.getfilesystemencoding())
from info import *