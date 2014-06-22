__author__ = 'Selobu'
__all__= ['GetLocaleDict', 'GetLangId','GetAvailLocales']
import glob
import wx
import sei_glob
from os import path as Path
def GetLocaleDict(loc_list, opt=0):
    """
    Takes a list of canonical locale names and by default returns a
    dictionary of available language values using the canonical name as
    the key. Supplying the Option OPT_DESCRIPT will return a dictionary
    of language id's with languages description as the key.
    **Parameters:**
    * loc_list: list of locals
    **Keywords:**
    * opt: option for configuring return data
    **Returns:**
    *  dict of locales mapped to wx.LANGUAGE_*** values
    **Note:**
    *  from Editra.dev_tool
    """
    lang_dict = dict()
    for lang in [x for x in dir(wx) if x.startswith("LANGUAGE")]:
        loc_i = wx.Locale(wx.LANGUAGE_DEFAULT). \
            GetLanguageInfo(getattr(wx, lang))
        if loc_i:
            if loc_i.CanonicalName in loc_list:
                if opt == 1:
                    lang_dict[loc_i.Description] = getattr(wx, lang)
                else:
                    lang_dict[loc_i.CanonicalName] = getattr(wx, lang)
    return lang_dict

def GetLangId(installDir, lang_n):
    """
    Gets the ID of a language from the description string. If the
    language cannot be found the function simply returns the default language
    **Parameters:**
    * lang_n: Canonical name of a language
    **Returns:**
    *  wx.LANGUAGE_*** id of language
    **Note:**
    *  from Editra.dev_tool
    """
    lang_desc = GetLocaleDict(GetAvailLocales(installDir), 1)
    return lang_desc.get(lang_n, wx.LANGUAGE_DEFAULT)

def GetAvailLocales(installDir):
    """
    Gets a list of the available locales that have been installed.
    Returning a list of strings that represent the
    canonical names of each language.
    **Returns:**
    *  list of all available local/languages available
    **Note:**
    *  from Editra.dev_tool
    """
    avail_loc = []
    langDir = installDir
    loc = glob.glob(Path.join(langDir, "locale", "*"))
    for path in loc:
        the_path = Path.join(path, "LC_MESSAGES", sei_glob.PROG_NAME+".mo")
        if Path.exists(the_path):
            avail_loc.append(Path.basename(path))
    return avail_loc
