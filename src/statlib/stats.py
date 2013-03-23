__all__=['F_oneway', 'F_value', 'F_value_multivariate', 
         '_N','betai','betacf', 
         #'aglm','amasslinregress','ap2t','sign',
         #'_athreshold','atmax','atmin','_atsem','_atstdev',
         #'_atvar','_azmap',
         'chisqprob', 'chisquare', 'correlation', 'covariance',
         'cumfreq', 'cumsum', 'describe',
         'erfcc', 'findwithin', 'firstquartilescore', 'fprob', 'friedmanchisquare',
         'gammln', 'geometricmean',  'harmonicmean', 'histogram',
         'itemfreq', 'kendalltau', 'kruskalwallish', 'ks_2samp', 'ksprob',
         'kurtosis', 'kurtosistest', 'lincc', 'linregress', 'mannwhitneyu',
         'mean', 'median', 'medianscore', 'mode', 'moment',
         'normaltest', 'obrientransform', 'paired', 'pearsonr',
         'percentileofscore', 'pointbiserialr', 'rankdata', 'ranksums',
         'relfreq', 'samplestdev', 'samplevar', 'scoreatpercentile',
         'sem', 'shellsort',  'signaltonoise', 'skew', 'skewtest',
         'spearmanr', 'square_of_sums', 'ss', 'stdev', 'sterr', 'sum',
         'sumdiffsquared', 'summult', 'thirdquartilescore', 
         'tiecorrect', 'tmean', 'trim1', 'trimboth',  
         'ttest_1samp', 'ttest_ind', 'ttest_rel', 'var',
         'variation', 'wilcoxont', 'z', 'zprob', 'zs',]

"""
Module stats.py
===============

A collection of basic statistical functions for python.

B{Important:}  There are really B{3} sets of functions.  The first set has an C{l}
prefix, which can be used with list or tuple arguments.  The second set has
an C{a} prefix, which can accept U{numpy <http://numpy.scipy.org>} array arguments.  These latter
functions are defined only when C{numpy} is available on the system.  The third
type has NO prefix (i.e., has the name that appears below).  Functions of
this set are members of a L{_Dispatch} class, c/o David Ascher.  This class
allows different functions to be called depending on the type of the passed
arguments.  Thus, L{stats.mean} is a member of the L{_Dispatch} class and
C{stats.mean(range(20))} will call L{stats._lmean} while
C{stats.mean(numpy.arange(20))} will call L{stats._amean}.

This is a handy way to keep consistent function names when different
argument types require different functions to be called. Having
implemented the L{_Dispatch} class, however, means that to get info on
a given function, you must use the REAL function name ... that is
C{print stats._lmean.__doc__} or C{print stats._amean.__doc__} work fine,
while C{print stats.mean.__doc__} will print the doc for the L{_Dispatch}
class.  U{Numpy <http://numpy.scipy.org>} functions (C{a} prefix)
generally have more argument options but
should otherwise be consistent with the corresponding list functions.

Function List
=============

Central Tendency
----------------
    - geometricmean
    - harmonicmean
    - mean
    - firstquartilescore
    - median
    - thirdquartilescore
    - interquartilerange
    - medianscore
    - mode

Moments
-------
    - moment
    - variation
    - skew
    - kurtosis
    - skewtest   (for Numpy arrays only)
    - kurtosistest (for Numpy arrays only)
    - normaltest (for Numpy arrays only)

Altered Versions
----------------
    - tmean  (for Numpy arrays only)
    - tvar   (for Numpy arrays only)
    - tmin   (for Numpy arrays only)
    - tmax   (for Numpy arrays only)
    - tstdev (for Numpy arrays only)
    - tsem   (for Numpy arrays only)
    - describe

Frequency Stats
---------------
    - itemfreq
    - scoreatpercentile
    - percentileofscore
    - histogram
    - cumfreq
    - relfreq

Variability
-----------
    - obrientransform
    - samplevar
    - samplestdev
    - signaltonoise (for Numpy arrays only)
    - var
    - stdev
    - sterr
    - sem
    - z
    - zs
    - zmap (for Numpy arrays only)

Trimming Fcns
-------------
    - threshold (for Numpy arrays only)
    - trimboth
    - trim1
    - round (round all vals to 'n' decimals; Numpy only)

Correlation Fcns
----------------
    - covariance  (for Numpy arrays only)
    - correlation (for Numpy arrays only)
    - paired
    - pearsonr
    - spearmanr
    - pointbiserialr
    - kendalltau
    - linregress

Inferential Stats
-----------------
    - ttest_1samp
    - ttest_ind
    - ttest_rel
    - chisquare
    - ks_2samp
    - mannwhitneyu
    - ranksums
    - wilcoxont
    - kruskalwallish
    - friedmanchisquare

Probability Calcs
-----------------
    - chisqprob
    - erfcc
    - zprob
    - ksprob
    - fprob
    - betacf
    - gammln
    - betai

Anova Functions
---------------
    - F_oneway
    - F_value

Support Functions
-----------------
    - writecc
    - _incr
    - sign  (for Numpy arrays only)
    - sum
    - cumsum
    - ss
    - summult
    - sumdiffsquared
    - square_of_sums
    - shellsort
    - rankdata
    - outputpairedstats
    - findwithin

B{Disclaimer:}  The function list is obviously incomplete and, worse, the
functions are not optimized.  All functions have been tested (some more
so than others), but they are far from bulletproof.  Thus, as with any
free software, no warranty or guarantee is expressed or implied. :-)  A
few extra functions that don't appear in the list below can be found by
interested treasure-hunters.  These functions don't necessarily have
both list and array versions but were deemed useful.

For further references see the U{python-statlib homepage
<http://python-statlib.googlecode.com>}

@author: Gary Strangman
@copyright: (c) 1999-2007 Gary Strangman; All Rights Reserved.
@license: MIT license
"""
#################################################
#######  Written by:  Gary Strangman  ###########
#######  Last modified:  Dec 18, 2007 ###########
#################################################
# Copyright (c) 1999-2007 Gary Strangman; All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a _copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, _copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Comments and/or additions are welcome (send e-mail to:
# strang@nmr.mgh.harvard.edu).
#

## CHANGE LOG:
## ===========
## 07-11.26 ... conversion for numpy started
## 07-05-16 ... added Lin's Concordance Correlation Coefficient (_alincc) and _acov
## 05-08-21 ... added "Dice's coefficient"
## 04-10-26 ... added ap2t(), an ugly fcn for converting p-vals to T-vals
## 04-04-03 ... added amasslinregress() function to do regression on _N-D arrays
## 03-01-03 ... CHANGED VERSION TO 0.6
##              fixed _atsem() to properly handle limits=None case
##              improved histogram and median functions (estbinwidth) and
##                   fixed _atvar() function (wrong answers for neg numbers?!?)
## 02-11-19 ... fixed _attest_ind and _attest_rel for div-by-zero Overflows
## 02-05-10 ... fixed _lchisqprob indentation (failed when df=even)
## 00-12-28 ... removed aanova() to separate module, fixed licensing to
##                   match Python License, fixed doc _string & imports
## 00-04-13 ... pulled all "global" statements, except from aanova()
##              added/fixed lots of documentation, removed io.py dependency
##              changed to version 0.5
## 99-11-13 ... added asign() function
## 99-11-01 ... changed version to 0.4 ... enough incremental changes now
## 99-10-25 ... added _acovariance and _acorrelation functions
## 99-10-10 ... fixed _askew/_akurtosis to avoid divide-by-zero errors
##              added aglm function (crude, but will be improved)
## 99-10-04 ... upgraded _acumsum, _ass, _asummult, _asamplevar, _avar, etc. to
##                   all handle lists of 'dimension's and keepdims
##              REMOVED ar0, ar2, ar3, ar4 and replaced them with around
##              reinserted fixes for _abetai to avoid _math overflows
## 99-09-05 ... rewrote _achisqprob/_aerfcc/_aksprob/_afprob/_abetacf/_abetai to
##                   handle multi-dimensional arrays (whew!)
## 99-08-30 ... fixed l/_amoment, l/_askew, l/_akurtosis per D'Agostino (1990)
##              added _anormaltest per same reference
##              re-wrote _azprob to calc arrays of probs all at once
## 99-08-22 ... edited _attest_ind printing section so arrays could be rounded
## 99-08-19 ... fixed _amean and _aharmonicmean for non-error(!) overflow on
##                   short/byte arrays (mean of #s btw 100-300 = -150??)
## 99-08-09 ... fixed _asum so that the None case works for Byte arrays
## 99-08-08 ... fixed 7/3 'improvement' to handle t-calcs on _N-D arrays
## 99-07-03 ... improved _attest_ind, _attest_rel (zero-division errortrap)
## 99-06-24 ... fixed bug(?) in _attest_ind (n1=a.shape[0])
## 04/11/99 ... added _asignaltonoise, _athreshold functions, changed all
##                   max/min in array section to _N.maximum/_N.minimum,
##                   fixed square_of_sums to prevent integer overflow
## 04/10/99 ... !!! Changed function name ... sumsquared ==> square_of_sums
## 03/18/99 ... Added ar0, ar2, ar3 and ar4 rounding functions
## 02/28/99 ... Fixed _aobrientransform to return an array rather than a list
## 01/15/99 ... Essentially ceased updating list-versions of functions (!!!)
## 01/13/99 ... CHANGED TO VERSION 0.3
##              fixed bug in a/_lmannwhitneyu p-value calculation
## 12/31/98 ... fixed variable-name bug in _ldescribe
## 12/19/98 ... fixed bug in findwithin (fcns needed pstat. prefix)
## 12/16/98 ... changed _amedianscore to return float (not array) for 1 score
## 12/14/98 ... added atmin and atmax functions
##              removed umath from import line (not needed)
##              l/_ageometricmean modified to reduce chance of overflows (take
##                   nth root first, then multiply)
## 12/07/98 ... added __version__variable (now 0.2)
##              removed all 'stats.' from anova() fcn
## 12/06/98 ... changed those functions (except shellsort) that altered
##                   arguments in-place ... cumsum, ranksort, ...
##              updated (and fixed some) doc-strings
## 12/01/98 ... added anova() function (requires NumPy)
##              incorporated _Dispatch class
## 11/12/98 ... added functionality to _amean, _aharmonicmean, _ageometricmean
##              added '_asum' function (added functionality to _N.add.reduce)
##              fixed both moment and _amoment (two errors)
##              changed name of skewness and _askewness to skew and _askew
##              fixed (a)histogram (which sometimes counted points <lowerlimit)

import pstat               # required 3rd party module
import math as _math
import string as _string
import copy as _copy  # required python modules
from types import ListType as _ListType, TupleType as _TupleType
from types import IntType as _IntType, FloatType as _FloatType
## from types import * # possible not needed
import scipy.stats as sc

__version__ = 0.6

############# DISPATCH CODE ##############


class _Dispatch:
    #"""
    #The _Dispatch class, care of David Ascher, allows different functions to
    #be called depending on the argument types.  This way, there can be one
    #function name regardless of the argument type.  To access function doc
    #in stats.py module, prefix the function with an 'l' or 'a' for list or
    #array arguments, respectively.  That is, print stats._lmean.__doc__ or
    #print stats._amean.__doc__ or whatever.
    #"""

    def __init__(self, *tuples):
        self._dispatch = {}
        for func, types in tuples:
            for t in types:
                if t in self._dispatch.keys():
                    raise ValueError, "can't have two dispatches on "+str(t)
                self._dispatch[t] = func
        self.__doc__= func.__doc__
        self._types = self._dispatch.keys()

    def __call__(self, arg1, *args, **kw):
        if type(arg1) not in self._types:
            raise TypeError, "don't know how to dispatch %s arguments" %  type(arg1)
        return apply(self._dispatch[type(arg1)], (arg1,) + args, kw)


##########################################################################
########################   LIST-BASED FUNCTIONS   ########################
##########################################################################

### Define these regardless

####################################
#######  CENTRAL TENDENCY  #########
####################################

def _lgeometricmean (inlist):
    """
    Calculates the geometric mean of the values in the passed list.
    That is:  n-th root of (x1 * x2 * ... * xn).  Assumes a '1D' list.

    Usage:   _lgeometricmean(inlist)
    """
    mult = 1.0
    one_over_n = 1.0/len(inlist)
    for item in inlist:
        mult = mult * pow(item,one_over_n)
    return mult


def _lharmonicmean (inlist):
    """
    The harmonic mean is defined as:  C{n / (1/x1 + 1/x2 + ... + 1/xn)}.
    @parameter inlist: assumes a '1D' list.
    @return: the harmonic mean of the values in the passed list.
    """
    sum = 0
    for item in inlist:
        sum = sum + 1.0/item
    return len(inlist) / sum


def _lmean (inlist):
    """
    Returns the arithmetic mean of the values in the passed list.
    Assumes a '1D' list, but will function on the 1st dim of an array(!).

    Usage:   _lmean(inlist)
    """
    sum = 0
    for item in inlist:
        sum = sum + item
    return sum/float(len(inlist))


def _lmedian (inlist,numbins=1000):
    """
    Returns the computed median value of a list of numbers, given the
    number of bins to use for the histogram (more bins brings the computed value
    closer to the median score, default number of bins = 1000).  See G.W.
    Heiman's Basic Stats (1st Edition), or CRC Probability & Statistics.

    Usage:   _lmedian (inlist, numbins=1000)
    """
    # ordering the data
    (hist, smallest, binsize, extras) = histogram(inlist,numbins,[min(inlist),max(inlist)]) # make histogram
    if binsize == 0:
        return None
    cumhist = cumsum(hist)              # make cumulative histogram
    # gives a default value to the cfbin in case
    cfbin= len(cumhist)-1
    for i in range(len(cumhist)):        # get 1st(!) index holding 50%ile score
        if cumhist[i]>=len(inlist)/2.0:
            cfbin = i
            break
    LRL = smallest + binsize*cfbin        # get lower read limit of that bin
    cfbelow = cumhist[cfbin-1]
    freq = float(hist[cfbin])               # frequency IN the 50%ile bin
    median = LRL + ((len(inlist)/2.0 - cfbelow)/float(freq))*binsize  # median formula
    return median


def _lmedianscore (inlist):
    """
    Returns the 'middle' score of the passed list.  If there is an even
    number of scores, the mean of the 2 middle scores is returned.

    Usage:   _lmedianscore(inlist)
    """

    newlist = _copy.deepcopy(inlist)
    newlist.sort()
    if len(newlist) % 2 == 0:   # if even number of scores, average middle 2
        index = len(newlist)/2  # integer division correct
        median = float(newlist[index] + newlist[index-1]) /2
    else:
        index = len(newlist)/2  # int division gives mid value when count from 0
        median = newlist[index]
    return median


def _lfirstquartilescore(inlist):
    """
    Returns the 'first' quartile score of the passed list. If there is an even
    number of scores, the mean of the two 25 percentile scores is returned.

    Usage:  lfirstquartile(inlist)
    """

    #newlist = _copy.deepcopy(inlist) ## the memory could be deprecated by a large amount of data
    newlist = inlist
    newlist.sort()
    firstquartile = sc.scoreatpercentile(newlist, 25)
    return firstquartile


def _lthirdquartilescore(inlist):
    """
    Returns the 'third' quartile score of the passed list. If there is an even
    number of scores, the mean of the two 75 percentile scores is returned.

    Usage:  lthirdquartile(inlist)
    """

    newlist = _copy.deepcopy(inlist)
    newlist.sort()
    thirdquartile = sc.scoreatpercentile(newlist, 75)
    return thirdquartile


def _lmode(inlist):
    """
    Returns a list of the modal (most common) score(s) in the passed
    list.  If there is more than one such score, all are returned.  The
    bin-count for the mode(s) is also returned.

    Usage:   _lmode(inlist)
    Returns: bin-count for mode(s), a list of modal value(s)
    """

    scores = pstat.unique(inlist)
    scores.sort()
    freq = []
    for item in scores:
        freq.append(inlist.count(item))
    maxfreq = max(freq)
    mode = []
    stillmore = 1
    while stillmore:
        try:
            indx = freq.index(maxfreq)
            mode.append(scores[indx])
            del freq[indx]
            del scores[indx]
        except ValueError:
            stillmore=0
    return maxfreq, mode


####################################
############  MOMENTS  #############
####################################

def _lmoment(inlist,moment=1):
    """
    Calculates the nth moment about the mean for a sample (defaults to
    the 1st moment).  Used to calculate coefficients of skewness and kurtosis.

    Usage:   _lmoment(inlist,moment=1)
    Returns: appropriate moment (r) from ... 1/n * SUM((inlist(i)-mean)**r)
    """
    if moment == 1:
        return 0.0
    else:
        mn = mean(inlist)
        n = len(inlist)
        s = 0
        for x in inlist:
            s = s + (x-mn)**moment
        return s/float(n)


def __lvariation(inlist):
    """
    Returns the coefficient of variation, as defined in CRC Standard
    Probability and Statistics, p.6.

    Usage:   __lvariation(inlist)
    """
    return 100.0*samplestdev(inlist)/float(mean(inlist))


def _lskew(inlist):
    """
    Returns the skewness of a distribution, as defined in Numerical
    Recipes (alternate defn in CRC Standard Probability and Statistics, p.6.)

    Usage:   _lskew(inlist)
    """
    try:
        return moment(inlist,3)/pow(moment(inlist,2),1.5)
    except ZeroDivisionError:
        return None


def _lkurtosis(inlist):
    """
    Returns the kurtosis of a distribution, as defined in Numerical
    Recipes (alternate defn in CRC Standard Probability and Statistics, p.6.)

    Usage:   _lkurtosis(inlist)
    """
    try:
        return moment(inlist,4)/pow(moment(inlist,2),2.0)
    except ZeroDivisionError:
        return None


def _ldescribe(inlist):
    """
    Returns some descriptive statistics of the passed list (assumed to be 1D).

    Usage:   _ldescribe(inlist)
    Returns: n, mean, standard deviation, skew, kurtosis
    """
    n = len(inlist)
    mm = (min(inlist),max(inlist))
    m = mean(inlist)
    sd = stdev(inlist)
    sk = skew(inlist)
    kurt = kurtosis(inlist)
    return n, mm, m, sd, sk, kurt


####################################
#######  FREQUENCY STATS  ##########
####################################

def _litemfreq(inlist):
    """
    Returns a list of pairs.  Each pair consists of one of the scores in inlist
    and it's frequency count.  Assumes a 1D list is passed.

    Usage:   _litemfreq(inlist)
    Returns: a 2D frequency table (col [0:n-1]=scores, col n=frequencies)
    """
    scores = pstat.unique(inlist)
    scores.sort()
    freq = []
    for item in scores:
        freq.append(inlist.count(item))
    return pstat.abut(scores, freq)


def _lscoreatpercentile (inlist, percent):
    """
    Returns the score at a given percentile relative to the distribution
    given by inlist.

    Usage:   _lscoreatpercentile(inlist,percent)
    """
    if percent > 1:
        print "\nDividing percent>1 by 100 in _lscoreatpercentile().\n"
        percent = percent / 100.0
    targetcf = percent*len(inlist)
    h, lrl, binsize, extras = histogram(inlist)
    cumhist = cumsum(_copy.deepcopy(h))
    for i in range(len(cumhist)):
        if cumhist[i] >= targetcf:
            break
    score = binsize * ((targetcf - cumhist[i-1]) / float(h[i])) + (lrl+binsize*i)
    return score


def _lpercentileofscore (inlist, score,histbins=10,defaultlimits=None):
    """
    Returns the percentile value of a score relative to the distribution
    given by inlist.  Formula depends on the values used to histogram the data(!).

    Usage:   _lpercentileofscore(inlist,score,histbins=10,defaultlimits=None)
    """

    h, lrl, binsize, extras = histogram(inlist,histbins,defaultlimits)
    cumhist = cumsum(_copy.deepcopy(h))
    i = int((score - lrl)/float(binsize))
    pct = (cumhist[i-1]+((score-(lrl+binsize*i))/float(binsize))*h[i])/float(len(inlist)) * 100
    return pct


def _lhistogram (inlist,numbins=10,defaultreallimits=None,printextras=0):
    """
    Returns (i) a list of histogram bin counts, (ii) the smallest value
    of the histogram binning, and (iii) the bin width (the last 2 are not
    necessarily integers).  Default number of bins is 10.  If no sequence object
    is given for defaultreallimits, the routine picks (usually non-pretty) bins
    spanning all the numbers in the inlist.

    Usage:   _lhistogram (inlist, numbins=10, defaultreallimits=None,suppressoutput=0)
    Returns: list of bin values, lowerreallimit, binsize, extrapoints
    """
    if (defaultreallimits <> None):
        if type(defaultreallimits) not in [_ListType,_TupleType] or len(defaultreallimits)==1: # only one limit given, assumed to be lower one & upper is calc'd
            lowerreallimit = defaultreallimits
            upperreallimit = 1.000001 * max(inlist)
        else: # assume both limits given
            lowerreallimit = defaultreallimits[0]
            upperreallimit = defaultreallimits[1]
        binsize = (upperreallimit-lowerreallimit)/float(numbins)
    else:     # no limits given for histogram, both must be calc'd
        estbinwidth=(max(inlist)-min(inlist))/float(numbins) +1e-6 #1=>cover all
        binsize = ((max(inlist)-min(inlist)+estbinwidth))/float(numbins)
        lowerreallimit = min(inlist) - binsize/2 #lower real limit,1st bin
    bins = [0]*(numbins)
    extrapoints = 0
    inlist= shellsort(inlist)[0]
    for num in inlist: # ordering the list of data in order to work correctly
        try:
            if (num-lowerreallimit) < 0:
                extrapoints = extrapoints + 1
            else:
                bintoincrement = int((num-lowerreallimit)/float(binsize))
                if bintoincrement >= numbins:
                    bintoincrement= numbins-1
                bins[bintoincrement] = bins[bintoincrement] + 1
        except:
            extrapoints = extrapoints + 1
    if (extrapoints > 0 and printextras == 1):
        print '\nPoints outside given histogram range =',extrapoints
    return (bins, lowerreallimit, binsize, extrapoints)


def _lcumfreq(inlist,numbins=10,defaultreallimits=None):
    """
    Returns a cumulative frequency histogram, using the histogram function.

    Usage:   _lcumfreq(inlist,numbins=10,defaultreallimits=None)
    Returns: list of cumfreq bin values, lowerreallimit, binsize, extrapoints
    """
    h,l,b,e = histogram(inlist,numbins,defaultreallimits)
    cumhist = cumsum(_copy.deepcopy(h))
    return cumhist,l,b,e


def _lrelfreq(inlist,numbins=10,defaultreallimits=None):
    """
    Returns a relative frequency histogram, using the histogram function.

    Usage:   _lrelfreq(inlist,numbins=10,defaultreallimits=None)
    Returns: list of cumfreq bin values, lowerreallimit, binsize, extrapoints
    """
    h,l,b,e = histogram(inlist,numbins,defaultreallimits)
    for i in range(len(h)):
        h[i] = h[i]/float(len(inlist))
    return h,l,b,e


####################################
#####  VARIABILITY FUNCTIONS  ######
####################################

def _lobrientransform(*args):
    """
    Computes a transform on input data (any number of columns).  Used to
    test for homogeneity of variance prior to running one-way stats.  From
    Maxwell and Delaney, p.112.

    Usage:   _lobrientransform(*args)
    Returns: transformed data for use in an ANOVA
    """
    TINY = 1e-10
    k = len(args)
    n = [0.0]*k
    v = [0.0]*k
    m = [0.0]*k
    nargs = []
    for i in range(k):
        nargs.append(_copy.deepcopy(args[i]))
        n[i] = float(len(nargs[i]))
        v[i] = var(nargs[i])
        m[i] = mean(nargs[i])
    for j in range(k):
        for i in range(n[j]):
            t1 = (n[j]-1.5)*n[j]*(nargs[j][i]-m[j])**2
            t2 = 0.5*v[j]*(n[j]-1.0)
            t3 = (n[j]-1.0)*(n[j]-2.0)
            nargs[j][i] = (t1-t2) / float(t3)
    check = 1
    for j in range(k):
        if v[j] - mean(nargs[j]) > TINY:
            check = 0
    if check <> 1:
        raise ValueError, 'Problem in obrientransform.'
    else:
        return nargs


def _lsamplevar (inlist):
    """
    Returns the variance of the values in the passed list using
    _N for the denominator (i.e., DESCRIBES the sample variance only).

    Usage:   _lsamplevar(inlist)
    """
    n = len(inlist)
    mn = mean(inlist)
    deviations = []
    for item in inlist:
        deviations.append(item-mn)
    return ss(deviations)/float(n)


def _lsamplestdev (inlist):
    """
    Returns the standard deviation of the values in the passed list using
    _N for the denominator (i.e., DESCRIBES the sample stdev only).

    Usage:   _lsamplestdev(inlist)
    """
    return _math.sqrt(samplevar(inlist))


def _lcov (x,y, keepdims=0):
    """
    Returns the estimated covariance of the values in the passed
    array (i.e., _N-1).  Dimension can equal None (ravel array first), an
    integer (the dimension over which to operate), or a sequence (operate
    over multiple dimensions).  Set keepdims=1 to return an array with the
    same number of dimensions as inarray.

    Usage:   _lcov(x,y,keepdims=0)
    """

    n = len(x)
    xmn = mean(x)
    ymn = mean(y)
    xdeviations = [0]*len(x)
    ydeviations = [0]*len(y)
    for i in range(len(x)):
        xdeviations[i] = x[i] - xmn
        ydeviations[i] = y[i] - ymn
    ss = 0.0
    for i in range(len(xdeviations)):
        ss = ss + xdeviations[i]*ydeviations[i]
    return ss/float(n-1)


def _lvar (inlist):
    """
    Returns the variance of the values in the passed list using _N-1
    for the denominator (i.e., for estimating population variance).

    Usage:   _lvar(inlist)
    """
    n = len(inlist)
    mn = mean(inlist)
    deviations = [0]*len(inlist)
    for i in range(len(inlist)):
        deviations[i] = inlist[i] - mn
    try:
        return ss(deviations)/float(n-1)
    except ZeroDivisionError:
        return None


def _lstdev (inlist):
    """
    Returns the standard deviation of the values in the passed list
    using _N-1 in the denominator (i.e., to estimate population stdev).

    Usage:   _lstdev(inlist)
    """
    return _math.sqrt(var(inlist))


def _lsterr(inlist):
    """
    Returns the standard error of the values in the passed list using _N-1
    in the denominator (i.e., to estimate population standard error).

    Usage:   _lsterr(inlist)
    """
    return stdev(inlist) / float(_math.sqrt(len(inlist)))


def _lsem (inlist):
    """
    Returns the estimated standard error of the mean (sx-bar) of the
    values in the passed list.  sem = stdev / sqrt(n)

    Usage:   _lsem(inlist)
    """
    sd = stdev(inlist)
    n = len(inlist)
    return sd/_math.sqrt(n)


def _lz (inlist, score):
    """
    Returns the z-score for a given input score, given that score and the
    list from which that score came.  Not appropriate for population calculations.

    Usage:   _lz(inlist, score)
    """
    z = (score-mean(inlist))/samplestdev(inlist)
    return z


def _lzs (inlist):
    """
    Returns a list of z-scores, one for each score in the passed list.

    Usage:   _lzs(inlist)
    """
    zscores = []
    for item in inlist:
        zscores.append(z(inlist,item))
    return zscores


####################################
#######  TRIMMING FUNCTIONS  #######
####################################

def _ltrimboth (l,proportiontocut):
    """
    Slices off the passed proportion of items from BOTH ends of the passed
    list (i.e., with proportiontocut=0.1, slices 'leftmost' 10% AND 'rightmost'
    10% of scores.  Assumes list is sorted by magnitude.  Slices off LESS if
    proportion results in a non-integer slice index (i.e., conservatively
    slices off proportiontocut).

    Usage:   _ltrimboth (l,proportiontocut)
    Returns: trimmed version of list l
    """
    lowercut = int(proportiontocut*len(l))
    uppercut = len(l) - lowercut
    return l[lowercut:uppercut]


def _ltrim1 (l,proportiontocut,tail='right'):
    """
    Slices off the passed proportion of items from ONE end of the passed
    list (i.e., if proportiontocut=0.1, slices off 'leftmost' or 'rightmost'
    10% of scores).  Slices off LESS if proportion results in a non-integer
    slice index (i.e., conservatively slices off proportiontocut).

    Usage:   _ltrim1 (l,proportiontocut,tail='right')  or set tail='left'
    Returns: trimmed version of list l
    """
    if tail == 'right':
        lowercut = 0
        uppercut = len(l) - int(proportiontocut*len(l))
    elif tail == 'left':
        lowercut = int(proportiontocut*len(l))
        uppercut = len(l)
    return l[lowercut:uppercut]


####################################
#####  CORRELATION FUNCTIONS  ######
####################################

def _lpaired(x,y):
    """
    Interactively determines the type of data and then runs the
    appropriated statistic for paired group data.

    Usage:   _lpaired(x,y)
    Returns: appropriate statistic name, value, and probability
    """
    samples = ''
    while samples not in ['i','r','I','R','c','C']:
        print '\nIndependent or related samples, or correlation (i,r,c): ',
        samples = raw_input()

    if samples in ['i','I','r','R']:
        print '\nComparing variances ...',
        # USE O'BRIEN'S TEST FOR HOMOGENEITY OF VARIANCE, Maxwell & delaney, p.112
        r = obrientransform(x,y)
        f,p = F_oneway(pstat.colex(r,0),pstat.colex(r,1))
        if p<0.05:
            vartype='unequal, p='+str(_round(p,4))
        else:
            vartype='equal'
        print vartype
        if samples in ['i','I']:
            if vartype[0]=='e':
                t,p = ttest_ind(x,y,0)
                print '\nIndependent samples t-test:  ', _round(t,4), _round(p,4)
            else:
                if len(x)>20 or len(y)>20:
                    z,p = ranksums(x,y)
                    print '\nRank Sums test (NONparametric, n>20):  ', _round(z,4), _round(p,4)
                else:
                    u,p = mannwhitneyu(x,y)
                    print '\nMann-Whitney U-test (NONparametric, ns<20):  ', _round(u,4), _round(p,4)

        else:  # RELATED SAMPLES
            if vartype[0]=='e':
                t,p = ttest_rel(x,y,0)
                print '\nRelated samples t-test:  ', _round(t,4), _round(p,4)
            else:
                t,p = ranksums(x,y)
                print '\nWilcoxon T-test (NONparametric):  ', _round(t,4), _round(p,4)
    else:  # CORRELATION ANALYSIS
        corrtype = ''
        while corrtype not in ['c','C','r','R','d','D']:
            print '\nIs the data Continuous, Ranked, or Dichotomous (c,r,d): ',
            corrtype = raw_input()
        if corrtype in ['c','C']:
            m,b,r,p,see = linregress(x,y)
            print '\nLinear regression for continuous variables ...'
            lol = [['Slope','Intercept','r','Prob','SEestimate'],[ _round(m,4), _round(b,4), _round(r,4), _round(p,4), _round(see,4)]]
            pstat.printcc(lol)
        elif corrtype in ['r','R']:
            r,p = spearmanr(x,y)
            print '\nCorrelation for ranked variables ...'
            print "Spearman's r: ", _round(r,4), _round(p,4)
        else: # DICHOTOMOUS
            r,p = pointbiserialr(x,y)
            print '\nAssuming x contains a dichotomous variable ...'
            print 'Point Biserial r: ', _round(r,4), _round(p,4)
    print '\n\n'
    return None


def _lpearsonr(x,y):
    """
    Calculates a Pearson correlation coefficient and the associated
    probability value.  Taken from Heiman's Basic Statistics for the Behav.
    Sci (2nd), p.195.

    Usage:   _lpearsonr(x,y)      where x and y are equal-length lists
    Returns: Pearson's r value, two-tailed p-value
    """
    TINY = 1.0e-30
    if len(x) <> len(y):
        raise ValueError, 'Input values not paired in pearsonr.  Aborting.'
    n = len(x)
    x = map(float,x)
    y = map(float,y)
    xmean = mean(x)
    ymean = mean(y)
    r_num = n*(summult(x,y)) - sum(x)*sum(y)
    r_den = _math.sqrt((n*ss(x) - square_of_sums(x))*(n*ss(y)-square_of_sums(y)))
    r = (r_num / r_den)  # denominator already a float
    df = n-2
    t = r*_math.sqrt(df/((1.0-r+TINY)*(1.0+r+TINY)))
    prob = betai(0.5*df,0.5,df/float(df+t*t))
    return r, prob


def _llincc(x,y):
    """
    Calculates Lin's concordance correlation coefficient.

    Usage:   _alincc(x,y)    where x, y are equal-length arrays
    Returns: Lin's CC
    """
    try:
        covar = _lcov(x,y)*(len(x)-1)/float(len(x))  # correct denom to n
        xvar = _lvar(x)*(len(x)-1)/float(len(x))  # correct denom to n
        yvar = _lvar(y)*(len(y)-1)/float(len(y))  # correct denom to n
        lincc = (2 * covar) / ((xvar+yvar) +((_amean(x)-_amean(y))**2))
    except ZeroDivisionError:
        return None
    return lincc


def _lspearmanr(x,y):
    """
    Calculates a Spearman rank-order correlation coefficient.  Taken
    from Heiman's Basic Statistics for the Behav. Sci (1st), p.192.

    Usage:   _lspearmanr(x,y)      where x and y are equal-length lists
    Returns: Spearman's r, two-tailed p-value
    """
    TINY = 1e-30
    if len(x) <> len(y):
        raise ValueError, 'Input values not paired in spearmanr.  Aborting.'
    n = len(x)
    rankx = rankdata(x)
    ranky = rankdata(y)
    dsq = sumdiffsquared(rankx,ranky)
    try:
        rs = 1 - 6*dsq / float(n*(n**2-1))
        t = rs * _math.sqrt((n-2) / ((rs+1.0)*(1.0-rs)))
        df = n-2
        probrs = betai(0.5*df,0.5,df/(df+t*t))  # t already a float
    except ZeroDivisionError:
        return None, None
    # probability values for rs are from part 2 of the spearman function in
    # Numerical Recipes, p.510.  They are close to tables, but not exact. (?)
    return rs, probrs


def _lpointbiserialr(x,y):
    """
    Calculates a point-biserial correlation coefficient and the associated
    probability value.  Taken from Heiman's Basic Statistics for the Behav.
    Sci (1st), p.194.

    Usage:   _lpointbiserialr(x,y)      where x,y are equal-length lists
    Returns: Point-biserial r, two-tailed p-value
    """
    TINY = 1e-30
    if len(x) <> len(y):
        raise ValueError, 'INPUT VALUES NOT PAIRED IN pointbiserialr.  ABORTING.'
    data = pstat.abut(x,y)
    categories = pstat.unique(x)
    if len(categories) <> 2:
        raise ValueError, "Exactly 2 categories required for pointbiserialr()."
    else:   # there are 2 categories, continue
        codemap = pstat.abut(categories,range(2))
        recoded = pstat.recode(data,codemap,0)
        x = pstat.linexand(data,0,categories[0])
        y = pstat.linexand(data,0,categories[1])
        xmean = mean(pstat.colex(x,1))
        ymean = mean(pstat.colex(y,1))
        n = len(data)
        try:
            adjust = _math.sqrt((len(x)/float(n))*(len(y)/float(n)))
            rpb = (ymean - xmean)/samplestdev(pstat.colex(data,1))*adjust
            df = n-2
            t = rpb*_math.sqrt(df/((1.0-rpb+TINY)*(1.0+rpb+TINY)))
            prob = betai(0.5*df,0.5,df/(df+t*t))  # t already a float
        except ZeroDivisionError:
            return None, None
        return rpb, prob


def _lkendalltau(x,y):
    """
    Calculates Kendall's tau ... correlation of ordinal data.  Adapted
    from function kendl1 in Numerical Recipes.  Needs good test-routine.@@@

    Usage:   _lkendalltau(x,y)
    Returns: Kendall's tau, two-tailed p-value
    """
    n1 = 0
    n2 = 0
    iss = 0
    for j in range(len(x)-1):
        for k in range(j,len(y)):
            a1 = x[j] - x[k]
            a2 = y[j] - y[k]
            aa = a1 * a2
            if (aa):             # neither list has a tie
                n1 = n1 + 1
                n2 = n2 + 1
                if aa > 0:
                    iss = iss + 1
                else:
                    iss = iss -1
            else:
                if (a1):
                    n1 = n1 + 1
                else:
                    n2 = n2 + 1
    try:
        tau = iss / _math.sqrt(n1*n2)
        svar = (4.0*len(x)+10.0) / (9.0*len(x)*(len(x)-1))
        z = tau / _math.sqrt(svar)
        prob = erfcc(abs(z)/1.4142136)
    except ZeroDivisionError:
        return None, None
    return tau, prob


def _llinregress(x,y):
    """
    Calculates a regression line on x,y pairs.

    Usage:   _llinregress(x,y)      x,y are equal-length lists of x-y coordinates
    Returns: slope, intercept, r, two-tailed prob, sterr-of-estimate, number of pairs
    """
    TINY = 1.0e-20
    if len(x) <> len(y):
        raise ValueError, 'Input values not paired in linregress.  Aborting.'
    n = len(x)
    x = map(float,x)
    y = map(float,y)
    xmean = mean(x)
    ymean = mean(y)
    r_num = float(n*(summult(x,y)) - sum(x)*sum(y))
    r_den = _math.sqrt((n*ss(x) - square_of_sums(x))*(n*ss(y)-square_of_sums(y)))
    try:
        r = r_num / r_den
        z = 0.5*_math.log((1.0+r+TINY)/(1.0-r+TINY))
        df = n-2
        t = r*_math.sqrt(df/((1.0-r+TINY)*(1.0+r+TINY)))
        prob = betai(0.5*df,0.5,df/(df+t*t))
        slope = r_num / float(n*ss(x) - square_of_sums(x))
    except ZeroDivisionError:
        return None, None, None, None, None
    intercept = ymean - slope*xmean
    sterrest = _math.sqrt(1-r*r)*samplestdev(y)
    return slope, intercept, r, prob, sterrest, n


####################################
#####  INFERENTIAL STATISTICS  #####
####################################

def _lttest_1samp(a,popmean,printit=0,name='Sample',writemode='a'):
    """
    Calculates the t-obtained for the independent samples T-test on ONE group
    of scores a, given a population mean.  If printit=1, results are printed
    to the screen.  If printit='filename', the results are output to 'filename'
    using the given writemode (default=append).  Returns t-value, and prob.

    Usage:   _lttest_1samp(a,popmean,Name='Sample',printit=0,writemode='a')
    Returns: t-value, two-tailed prob
    """
    x = mean(a)
    v = var(a)
    n = len(a)
    df = n-1
    try:
        svar = ((n-1)*v)/float(df)
        t = (x-popmean)/_math.sqrt(svar*(1.0/n))
        prob = betai(0.5*df,0.5,float(df)/(df+t*t))
    except ZeroDivisionError:
        return None, None

    if printit <> 0:
        statname = 'Single-sample T-test.'
        outputpairedstats(printit,writemode,
                          'Population','--',popmean,0,0,0,
                          name,n,x,v,min(a),max(a),
                          statname,t,prob)
    return t,prob


def _lttest_ind (a, b, printit=0, name1='Samp1', name2='Samp2', writemode='a'):
    """
    Calculates the t-obtained T-test on TWO INDEPENDENT samples of
    scores a, and b.  From Numerical Recipes, p.483.  If printit=1, results
    are printed to the screen.  If printit='filename', the results are output
    to 'filename' using the given writemode (default=append).  Returns t-value,
    and prob.

    Usage:   _lttest_ind(a,b,printit=0,name1='Samp1',name2='Samp2',writemode='a')
    Returns: t-value, two-tailed prob
    """
    x1 = mean(a)
    x2 = mean(b)
    v1 = stdev(a)**2
    v2 = stdev(b)**2
    n1 = len(a)
    n2 = len(b)
    df = n1+n2-2
    try:
        svar = ((n1-1)*v1+(n2-1)*v2)/float(df)
        t = (x1-x2)/_math.sqrt(svar*(1.0/n1 + 1.0/n2))
        prob = betai(0.5*df,0.5,df/(df+t*t))
    except ZeroDivisionError:
        return None, None

    if printit <> 0:
        statname = 'Independent samples T-test.'
        outputpairedstats(printit,writemode,
                          name1,n1,x1,v1,min(a),max(a),
                          name2,n2,x2,v2,min(b),max(b),
                          statname,t,prob)
    return t,prob


def _lttest_rel (a,b,printit=0,name1='Sample1',name2='Sample2',writemode='a'):
    """
    Calculates the t-obtained T-test on TWO RELATED samples of scores,
    a and b.  From Numerical Recipes, p.483.  If printit=1, results are
    printed to the screen.  If printit='filename', the results are output to
    'filename' using the given writemode (default=append).  Returns t-value,
    and prob.

    Usage:   _lttest_rel(a,b,printit=0,name1='Sample1',name2='Sample2',writemode='a')
    Returns: t-value, two-tailed prob
    """
    if len(a)<>len(b):
        raise ValueError, 'Unequal length lists in ttest_rel.'
    x1 = mean(a)
    x2 = mean(b)
    v1 = var(a)
    v2 = var(b)
    n = len(a)
    cov = 0
    for i in range(len(a)):
        cov = cov + (a[i]-x1) * (b[i]-x2)
    df = n-1
    try:
        cov = cov / float(df)
        sd = _math.sqrt((v1+v2 - 2.0*cov)/float(n))
        t = (x1-x2)/sd
        prob = betai(0.5*df,0.5,df/(df+t*t))
    except ZeroDivisionError:
        return None, None

    if printit <> 0:
        statname = 'Related samples T-test.'
        outputpairedstats(printit,writemode,
                          name1,n,x1,v1,min(a),max(a),
                          name2,n,x2,v2,min(b),max(b),
                          statname,t,prob)
    return t, prob


def _lchisquare(f_obs,f_exp=None):
    """
    Calculates a one-way chi square for list of observed frequencies and returns
    the result.  If no expected frequencies are given, the total _N is assumed to
    be equally distributed across all groups.

    Usage:   _lchisquare(f_obs, f_exp=None)   f_obs = list of observed cell freq.
    Returns: chisquare-statistic, associated p-value
    """
    k = len(f_obs)                 # number of groups
    if f_exp == None:
        f_exp = [sum(f_obs)/float(k)] * len(f_obs) # create k bins with = freq.
    chisq = 0
    for i in range(len(f_obs)):
        chisq += (f_obs[i]-f_exp[i])**2 / float(f_exp[i])
    return chisq, chisqprob(chisq, k-1)


def _lks_2samp (data1,data2):
    """
    Computes the Kolmogorov-Smirnov statistic on 2 samples.  From
    Numerical Recipes in C, page 493.

    Usage:   _lks_2samp(data1,data2)   data1&2 are lists of values for 2 conditions
    Returns: KS D-value, associated p-value
    """
    j1 = 0
    j2 = 0
    fn1 = 0.0
    fn2 = 0.0
    n1 = len(data1)
    n2 = len(data2)
    en1 = n1
    en2 = n2
    d = 0.0
    data1.sort()
    data2.sort()
    while j1 < n1 and j2 < n2:
        d1=data1[j1]
        d2=data2[j2]
        if d1 <= d2:
            fn1 = (j1)/float(en1)
            j1 = j1 + 1
        if d2 <= d1:
            fn2 = (j2)/float(en2)
            j2 = j2 + 1
        dt = (fn2-fn1)
        if _math.fabs(dt) > _math.fabs(d):
            d = dt
    try:
        en = _math.sqrt(en1*en2/float(en1+en2))
        prob = ksprob((en+0.12+0.11/en)*abs(d))
    except ZeroDivisionError:
        return None, None
    return d, prob


def _lmannwhitneyu(x,y):
    """
    Calculates a Mann-Whitney U statistic on the provided scores and
    returns the result.  Use only when the n in each condition is < 20 and
    you have 2 independent samples of ranks.  NOTE: Mann-Whitney U is
    significant if the u-obtained is LESS THAN or equal to the critical
    value of U found in the tables.  Equivalent to Kruskal-Wallis H with
    just 2 groups.

    Usage:   _lmannwhitneyu(data)
    Returns: u-statistic, one-tailed p-value (i.e., p(z(U)))
    """
    n1 = len(x)
    n2 = len(y)
    ranked = rankdata(x+y)
    rankx = ranked[0:n1]       # get the x-ranks
    ranky = ranked[n1:]        # the rest are y-ranks
    u1 = n1*n2 + (n1*(n1+1))/2.0 - sum(rankx)  # calc U for x
    u2 = n1*n2 - u1                            # remainder is U for y
    bigu = max(u1,u2)
    smallu = min(u1,u2)
    T = _math.sqrt(tiecorrect(ranked))  # correction factor for tied scores
    if T == 0:
        raise ValueError, 'All numbers are identical in _lmannwhitneyu'
    sd = _math.sqrt(T*n1*n2*(n1+n2+1)/12.0)
    try:
        z = abs((bigu-n1*n2/2.0) / sd)  # normal approximation for prob calc
    except ZeroDivisionError:
        return None, None
    return smallu, 1.0 - zprob(z)


def _ltiecorrect(rankvals):
    """
    Corrects for ties in Mann Whitney U and Kruskal Wallis H tests.  See
    Siegel, S. (1956) Nonparametric Statistics for the Behavioral Sciences.
    New York: McGraw-Hill.  Code adapted from |Stat rankind.c code.

    Usage:   _ltiecorrect(rankvals)
    Returns: T correction factor for U or H
    """
    sorted,posn = shellsort(rankvals)
    n = len(sorted)
    T = 0.0
    i = 0
    while (i<n-1):
        if sorted[i] == sorted[i+1]:
            nties = 1
            while (i<n-1) and (sorted[i] == sorted[i+1]):
                nties = nties +1
                i = i +1
            T = T + nties**3 - nties
        i = i+1
    try:
        T = T / float(n**3-n)
    except ZeroDivisionError:
        return None
    return 1.0 - T


def _lranksums(x,y):
    """
    Calculates the rank sums statistic on the provided scores and
    returns the result.  Use only when the n in each condition is > 20 and you
    have 2 independent samples of ranks.

    Usage:   _lranksums(x,y)
    Returns: a z-statistic, two-tailed p-value
    """
    n1 = len(x)
    n2 = len(y)
    alldata = x+y
    ranked = rankdata(alldata)
    x = ranked[:n1]
    y = ranked[n1:]
    s = sum(x)
    expected = n1*(n1+n2+1) / 2.0
    try:
        z = (s - expected) / _math.sqrt(n1*n2*(n1+n2+1)/12.0)
    except ZeroDivisionError:
        return None, None
    prob = 2*(1.0 -zprob(abs(z)))
    return z, prob


def _lwilcoxont(x,y):
    """
    Calculates the Wilcoxon T-test for related samples and returns the
    result.  A non-parametric T-test.

    Usage:   _lwilcoxont(x,y)
    Returns: a t-statistic, two-tail probability estimate
    """
    if len(x) <> len(y):
        raise ValueError, 'Unequal _N in wilcoxont.  Aborting.'
    d=[]
    for i in range(len(x)):
        diff = x[i] - y[i]
        if diff <> 0:
            d.append(diff)
    count = len(d)
    absd = map(abs,d)
    absranked = rankdata(absd)
    r_plus = 0.0
    r_minus = 0.0
    for i in range(len(absd)):
        if d[i] < 0:
            r_minus = r_minus + absranked[i]
        else:
            r_plus = r_plus + absranked[i]
    wt = min(r_plus, r_minus)
    mn = count * (count+1) * 0.25
    se =  _math.sqrt(count*(count+1)*(2.0*count+1.0)/24.0)
    try:
        z = _math.fabs(wt-mn) / se
    except ZeroDivisionError:
        return None, None
    prob = 2*(1.0 -zprob(abs(z)))
    return wt, prob


def _lkruskalwallish(*args):
    """
    The Kruskal-Wallis H-test is a non-parametric ANOVA for 3 or more
    groups, requiring at least 5 subjects in each group.  This function
    calculates the Kruskal-Wallis H-test for 3 or more independent samples
    and returns the result.

    Usage:   _lkruskalwallish(*args)
    Returns: H-statistic (corrected for ties), associated p-value
    """
    args = list(args)
    n = [0]*len(args)
    all = []
    n = map(len,args)
    for i in range(len(args)):
        all = all + args[i]
    ranked = rankdata(all)
    T = tiecorrect(ranked)
    for i in range(len(args)):
        args[i] = ranked[0:n[i]]
        del ranked[0:n[i]]
    rsums = []
    for i in range(len(args)):
        rsums.append(sum(args[i])**2)
        rsums[i] = rsums[i] / float(n[i])
    ssbn = sum(rsums)
    totaln = sum(n)
    h = 12.0 / (totaln*(totaln+1)) * ssbn - 3*(totaln+1)
    df = len(args) - 1
    if T == 0:
        raise ValueError, 'All numbers are identical in _lkruskalwallish'
    h = h / float(T)
    return h, chisqprob( h, df)


def _lfriedmanchisquare(*args):
    """
    Friedman Chi-Square is a non-parametric, one-way within-subjects
    ANOVA.  This function calculates the Friedman Chi-square test for repeated
    measures and returns the result, along with the associated probability
    value.  It assumes 3 or more repeated measures.  Only 3 levels requires a
    minimum of 10 subjects in the study.  Four levels requires 5 subjects per
    level(??).

    Usage:   _lfriedmanchisquare(*args)
    Returns: chi-square statistic, associated p-value
    """
    k = len(args)
    if k < 3:
        raise ValueError, 'Less than 3 levels.  Friedman test not appropriate.'
    n = len(args[0])
    data = apply(pstat.abut,tuple(args))
    for i in range(len(data)):
        data[i] = rankdata(data[i])
    ssbn = 0
    for i in range(k):
        ssbn = ssbn + sum(args[i])**2
    chisq = 12.0 / (k*n*(k+1)) * ssbn - 3*n*(k+1)
    return chisq, chisqprob(chisq,k-1)


####################################
####  PROBABILITY CALCULATIONS  ####
####################################

def _lchisqprob(chisq,df):
    """
    Returns the (1-tailed) probability value associated with the provided
    chi-square value and df.  Adapted from chisq.c in Gary Perlman's |Stat.

    Usage:   _lchisqprob(chisq,df)
    """
    BIG = 20.0
    def ex(x):
        BIG = 20.0
        if x < -BIG:
            return 0.0
        else:
            return _math.exp(x)

    if chisq <=0 or df < 1:
        return 1.0
    a = 0.5 * chisq
    if df%2 == 0:
        even = 1
    else:
        even = 0
    if df > 1:
        y = ex(-a)
    if even:
        s = y
    else:
        s = 2.0 * zprob(-_math.sqrt(chisq))
    if (df > 2):
        chisq = 0.5 * (df - 1.0)
        if even:
            z = 1.0
        else:
            z = 0.5
        if a > BIG:
            if even:
                e = 0.0
            else:
                e = _math.log(_math.sqrt(_math.pi))
            c = _math.log(a)
            while (z <= chisq):
                e = _math.log(z) + e
                s = s + ex(c*z-a-e)
                z = z + 1.0
            return s
        else:
            if even:
                e = 1.0
            else:
                e = 1.0 / _math.sqrt(_math.pi) / _math.sqrt(a)
            c = 0.0
            while (z <= chisq):
                e = e * (a/float(z))
                c = c + e
                z = z + 1.0
            return (c*y+s)
    else:
        return s


def _lerfcc(x):
    """
    Returns the complementary error function erfc(x) with fractional
    error everywhere less than 1.2e-7.  Adapted from Numerical Recipes.

    Usage:   _lerfcc(x)
    """
    z = abs(x)
    t = 1.0 / (1.0+0.5*z)
    ans = t * _math.exp(-z*z-1.26551223 + t*(1.00002368+t*(0.37409196+t*(0.09678418+t*(-0.18628806+t*(0.27886807+t*(-1.13520398+t*(1.48851587+t*(-0.82215223+t*0.17087277)))))))))
    if x >= 0:
        return ans
    else:
        return 2.0 - ans


def _lzprob(z):
    """
    Returns the area under the normal curve 'to the left of' the given z value.
    Thus,
        - for z<0, zprob(z) = 1-tail probability
        - for z>0, 1.0-zprob(z) = 1-tail probability
        - for any z, 2.0*(1.0-zprob(abs(z))) = 2-tail probability
    Adapted from z.c in Gary Perlman's |Stat.

    Usage:   _lzprob(z)
    """
    Z_MAX = 6.0    # maximum meaningful z-value
    if z == 0.0:
        x = 0.0
    else:
        y = 0.5 * _math.fabs(z)
        if y >= (Z_MAX*0.5):
            x = 1.0
        elif (y < 1.0):
            w = y*y
            x = ((((((((0.000124818987 * w
                        -0.001075204047) * w +0.005198775019) * w
                      -0.019198292004) * w +0.059054035642) * w
                    -0.151968751364) * w +0.319152932694) * w
                  -0.531923007300) * w +0.797884560593) * y * 2.0
        else:
            y = y - 2.0
            x = (((((((((((((-0.000045255659 * y
                             +0.000152529290) * y -0.000019538132) * y
                           -0.000676904986) * y +0.001390604284) * y
                         -0.000794620820) * y -0.002034254874) * y
                       +0.006549791214) * y -0.010557625006) * y
                     +0.011630447319) * y -0.009279453341) * y
                   +0.005353579108) * y -0.002141268741) * y
                 +0.000535310849) * y +0.999936657524
    if z > 0.0:
        prob = ((x+1.0)*0.5)
    else:
        prob = ((1.0-x)*0.5)
    return prob


def _lksprob(alam):
    """
    Computes a Kolmolgorov-Smirnov t-test significance level.  Adapted from
    Numerical Recipes.

    Usage:   _lksprob(alam)
    """
    fac = 2.0
    sum = 0.0
    termbf = 0.0
    a2 = -2.0*alam*alam
    for j in range(1,201):
        term = fac*_math.exp(a2*j*j)
        sum = sum + term
        if _math.fabs(term) <= (0.001*termbf) or _math.fabs(term) < (1.0e-8*sum):
            return sum
        fac = -fac
        termbf = _math.fabs(term)
    return 1.0             # Get here only if fails to converge; was 0.0!!


def _lfprob (dfnum, dfden, F):
    """
    Returns the (1-tailed) significance level (p-value) of an F
    statistic given the degrees of freedom for the numerator (dfR-dfF) and
    the degrees of freedom for the denominator (dfF).

    Usage:   _lfprob(dfnum, dfden, F)   where usually dfnum=dfbn, dfden=dfwn
    """
    p = betai(0.5*dfden, 0.5*dfnum, dfden/float(dfden+dfnum*F))
    return p


def _lbetacf(a,b,x):
    """
    This function evaluates the continued fraction form of the incomplete
    Beta function, betai.  (Adapted from: Numerical Recipes in C.)

    Usage:   _lbetacf(a,b,x)
    """
    ITMAX = 200
    EPS = 3.0e-7

    bm = _az = am = 1.0
    qab = a+b
    qap = a+1.0
    qam = a-1.0
    bz = 1.0-qab*x/qap
    for i in range(ITMAX+1):
        em = float(i+1)
        tem = em + em
        d = em*(b-em)*x/((qam+tem)*(a+tem))
        ap = _az + d*am
        bp = bz+d*bm
        d = -(a+em)*(qab+em)*x/((qap+tem)*(a+tem))
        app = ap+d*_az
        bpp = bp+d*bz
        aold = _az
        am = ap/bpp
        bm = bp/bpp
        _az = app/bpp
        bz = 1.0
        if (abs(_az-aold)<(EPS*abs(_az))):
            return _az
    print 'a or b too big, or ITMAX too small in Betacf.'


def _lgammln(xx):
    """
    Returns the gamma function of xx.
    Gamma(z) = Integral(0,infinity) of t^(z-1)exp(-t) dt.
    (Adapted from: Numerical Recipes in C.)

    Usage:   _lgammln(xx)
    """

    coeff = [76.18009173, -86.50532033, 24.01409822, -1.231739516,
             0.120858003e-2, -0.536382e-5]
    x = xx - 1.0
    tmp = x + 5.5
    tmp = tmp - (x+0.5)*_math.log(tmp)
    ser = 1.0
    for j in range(len(coeff)):
        x = x + 1
        ser = ser + coeff[j]/x
    return -tmp + _math.log(2.50662827465*ser)


def _lbetai(a,b,x):
    """
    Returns the incomplete beta function:

    I-sub-x(a,b) = 1/B(a,b)*(Integral(0,x) of t^(a-1)(1-t)^(b-1) dt)

    where a,b>0 and B(a,b) = G(a)*G(b)/(G(a+b)) where G(a) is the gamma
    function of a.  The continued fraction formulation is implemented here,
    using the betacf function.  (Adapted from: Numerical Recipes in C.)

    Usage:   _lbetai(a,b,x)
    """
    if (x<0.0 or x>1.0):
        raise ValueError, 'Bad x in _lbetai'
    if (x==0.0 or x==1.0):
        bt = 0.0
    else:
        bt = _math.exp(gammln(a+b)-gammln(a)-gammln(b)+a*_math.log(x)+b*
                      _math.log(1.0-x))
    if (x<(a+1.0)/(a+b+2.0)):
        return bt*betacf(a,b,x)/float(a)
    else:
        return 1.0-bt*betacf(b,a,1.0-x)/float(b)


####################################
#######  ANOVA CALCULATIONS  #######
####################################

def _lF_oneway(*lists):
    """
    Performs a 1-way ANOVA, returning an F-value and probability given
    any number of groups.  From Heiman, pp.394-7.

    Usage:   F_oneway(*lists)    where *lists is any number of lists, one per treatment group
    Returns: F value, one-tailed p-value
    """
    a = len(lists)           # ANOVA on 'a' groups, each in it's own list
    means = [0]*a
    vars = [0]*a
    ns = [0]*a
    alldata = []
    tmp = map(_N.array,lists)
    means = map(_amean,tmp)
    vars = map(_avar,tmp)
    ns = map(len,lists)
    for i in range(len(lists)):
        alldata = alldata + lists[i]
    alldata = _N.array(alldata)
    bign = len(alldata)
    sstot = _ass(alldata)-(_asquare_of_sums(alldata)/float(bign))
    ssbn = 0
    for list in lists:
        ssbn = ssbn + _asquare_of_sums(_N.array(list))/float(len(list))
    ssbn = ssbn - (_asquare_of_sums(alldata)/float(bign))
    sswn = sstot-ssbn
    dfbn = a-1
    dfwn = bign - a
    msb = ssbn/float(dfbn)
    msw = sswn/float(dfwn)
    f = msb/msw
    prob = fprob(dfbn,dfwn,f)
    return f, prob


def _lF_value (ER,EF,dfnum,dfden):
    """
    Returns an F-statistic given the following:
    ER  = error associated with the null hypothesis (the Restricted model)
    EF  = error associated with the alternate hypothesis (the Full model)
    dfR-dfF = degrees of freedom of the numerator
    dfF = degrees of freedom associated with the denominator/Full model

    Usage:   _lF_value(ER,EF,dfnum,dfden)
    """
    return ((ER-EF)/float(dfnum) / (EF/float(dfden)))


####################################
########  SUPPORT FUNCTIONS  #######
####################################

def writecc (listoflists,file,writetype='w',extra=2):
    """
    Writes a list of lists to a file in columns, customized by the max
    size of items within the columns (max size of items in col, +2 characters)
    to specified file.  File-overwrite is the default.

    Usage:   writecc (listoflists,file,writetype='w',extra=2)
    Returns: None
    """
    if type(listoflists[0]) not in [_ListType,_TupleType]:
        listoflists = [listoflists]
    outfile = open(file,writetype)
    rowstokill = []
    list2print = _copy.deepcopy(listoflists)
    for i in range(len(listoflists)):
        if listoflists[i] == ['\n'] or listoflists[i]=='\n' or listoflists[i]=='dashes':
            rowstokill = rowstokill + [i]
    rowstokill.reverse()
    for row in rowstokill:
        del list2print[row]
    maxsize = [0]*len(list2print[0])
    for col in range(len(list2print[0])):
        items = pstat.colex(list2print,col)
        items = map(pstat.makestr,items)
        maxsize[col] = max(map(len,items)) + extra
    for row in listoflists:
        if row == ['\n'] or row == '\n':
            outfile.write('\n')
        elif row == ['dashes'] or row == 'dashes':
            dashes = [0]*len(maxsize)
            for j in range(len(maxsize)):
                dashes[j] = '-'*(maxsize[j]-2)
            outfile.write(pstat.lineincustcols(dashes,maxsize))
        else:
            outfile.write(pstat.lineincustcols(row,maxsize))
        outfile.write('\n')
    outfile.close()
    return None


def _lincr(l,cap):        # to increment a list up to a max-list of 'cap'
    """
    Simulate a counting system from an n-dimensional list.

    Usage:   _lincr(l,cap)   l=list to increment, cap=max values for each list pos'n
    Returns: next set of values for list l, OR -1 (if overflow)
    """
    l[0] = l[0] + 1     # e.g., [0,0,0] --> [2,4,3] (=cap)
    for i in range(len(l)):
        if l[i] > cap[i] and i < len(l)-1: # if carryover AND not done
            l[i] = 0
            l[i+1] = l[i+1] + 1
        elif l[i] > cap[i] and i == len(l)-1: # overflow past last column, must be finished
            l = -1
    return l


def _lsum (inlist):
    """
    Returns the sum of the items in the passed list.

    Usage:   _lsum(inlist)
    """
    s = 0
    for item in inlist:
        s = s + item
    return s


def _lcumsum (inlist):
    """
    Returns a list consisting of the cumulative sum of the items in the
    passed list.

    Usage:   _lcumsum(inlist)
    """
    newlist = _copy.deepcopy(inlist)
    for i in range(1,len(newlist)):
        newlist[i] = newlist[i] + newlist[i-1]
    return newlist


def _lss(inlist):
    """
    Squares each value in the passed list, adds up these squares and
    returns the result.

    Usage:   _lss(inlist)
    """
    ss = 0
    for item in inlist:
        ss = ss + item*item
    return ss


def _lsummult (list1,list2):
    """
    Multiplies elements in list1 and list2, element by element, and
    returns the sum of all resulting multiplications.  Must provide equal
    length lists.

    Usage:   _lsummult(list1,list2)
    """
    if len(list1) <> len(list2):
        raise ValueError, "Lists not equal length in summult."
    s = 0
    for item1,item2 in pstat.abut(list1,list2):
        s = s + item1*item2
    return s


def _lsumdiffsquared(x,y):
    """
    Takes pairwise differences of the values in lists x and y, squares
    these differences, and returns the sum of these squares.

    Usage:   _lsumdiffsquared(x,y)
    Returns: sum[(x[i]-y[i])**2]
    """
    sds = 0
    for i in range(len(x)):
        sds = sds + (x[i]-y[i])**2
    return sds


def _lsquare_of_sums(inlist):
    """
    Adds the values in the passed list, squares the sum, and returns
    the result.

    Usage:   _lsquare_of_sums(inlist)
    Returns: sum(inlist[i])**2
    """
    s = sum(inlist)
    return float(s)*s


def _lshellsort(inlist):
    """
    Shellsort algorithm.  Sorts a 1D-list.

    Usage:   _lshellsort(inlist)
    Returns: sorted-inlist, sorting-index-vector (for original list)
    """
    n = len(inlist)
    svec = _copy.deepcopy(inlist)
    ivec = range(n)
    gap = n/2   # integer division needed
    while gap >0:
        for i in range(gap,n):
            for j in range(i-gap,-1,-gap):
                while j>=0 and svec[j]>svec[j+gap]:
                    temp        = svec[j]
                    svec[j]     = svec[j+gap]
                    svec[j+gap] = temp
                    itemp       = ivec[j]
                    ivec[j]     = ivec[j+gap]
                    ivec[j+gap] = itemp
        gap = gap / 2  # integer division needed
    # svec is now sorted inlist, and ivec has the order svec[i] = vec[ivec[i]]
    return svec, ivec

def _lrankdata(inlist):
    """
    Ranks the data in inlist, dealing with ties appropriately.  Assumes
    a 1D inlist.  Adapted from Gary Perlman's |Stat ranksort.

    Usage:   _lrankdata(inlist)
    Returns: a list of length equal to inlist, containing rank scores
    """
    n = len(inlist)
    svec, ivec = shellsort(inlist)
    sumranks = 0
    dupcount = 0
    newlist = [0]*n
    for i in range(n):
        sumranks = sumranks + i
        dupcount = dupcount + 1
        if i==n-1 or svec[i] <> svec[i+1]:
            averank = sumranks / float(dupcount) + 1
            for j in range(i-dupcount+1,i+1):
                newlist[ivec[j]] = averank
            sumranks = 0
            dupcount = 0
    return newlist


def outputpairedstats(fname,writemode,name1,n1,m1,se1,min1,max1,name2,n2,m2,se2,min2,max2,statname,stat,prob):
    """
    Prints or write to a file stats for two groups, using the name, n,
    mean, sterr, min and max for each group, as well as the statistic name,
    its value, and the associated p-value.

    Usage:   outputpairedstats(fname,writemode, name1,n1,mean1,stderr1,min1,max1, name2,n2,mean2,stderr2,min2,max2,statname,stat,prob)
    Returns: None
    """
    suffix = ''                       # for *s after the p-value
    try:
        x = prob.shape
        prob = prob[0]
    except:
        pass
    if  prob < 0.001:  suffix = '  ***'
    elif prob < 0.01:  suffix = '  **'
    elif prob < 0.05:  suffix = '  *'
    title = [['Name','_N','Mean','SD','Min','Max']]
    lofl = title+[[name1,n1, _round(m1,3), _round(_math.sqrt(se1),3),min1,max1],
                  [name2,n2, _round(m2,3), _round(_math.sqrt(se2),3),min2,max2]]
    if type(fname)<>StringType or len(fname)==0:
        print
        print statname
        print
        pstat.printcc(lofl)
        print
        try:
            if stat.shape == ():
                stat = stat[0]
            if prob.shape == ():
                prob = prob[0]
        except:
            pass
        print 'Test statistic = ', _round(stat,3),'   p = ', _round(prob,3),suffix
        print
    else:
        file = open(fname,writemode)
        file.write('\n'+statname+'\n\n')
        file.close()
        writecc(lofl,fname,'a')
        file = open(fname,'a')
        try:
            if stat.shape == ():
                stat = stat[0]
            if prob.shape == ():
                prob = prob[0]
        except:
            pass
        file.write(pstat.list2string(['\nTest statistic = ',round(stat,4),'   p = ',  _round(prob,4),suffix,'\n\n']))
        file.close()
    return None


def _lfindwithin (data):
    """
    Returns an integer representing a binary vector, where 1=within-
    subject factor, 0=between.  Input equals the entire data 2D list (i.e.,
    column 0=random factor, column -1=measured values (those two are skipped).
    Note: input data is in |Stat format ... a list of lists ("2D list") with
    one row per measured value, first column=subject identifier, last column=
    score, one in-between column per factor (these columns contain level
    designations on each factor).  See also stats.anova.__doc__.

    Usage:   _lfindwithin(data)     data in |Stat format
    """

    numfact = len(data[0])-1
    withinvec = 0
    for col in range(1,numfact):
        examplelevel = pstat.unique(pstat.colex(data,col))[0]
        rows = pstat.linexand(data,col,examplelevel)  # get 1 level of this factor
        factsubjs = pstat.unique(pstat.colex(rows,0))
        allsubjs = pstat.unique(pstat.colex(data,0))
        if len(factsubjs) == len(allsubjs):  # fewer Ss than scores on this factor?
            withinvec = withinvec + (1 << col)
    return withinvec


#########################################################
#########################################################
####### DISPATCH LISTS AND TUPLES TO ABOVE FCNS #########
#########################################################
#########################################################

## CENTRAL TENDENCY:
geometricmean = _Dispatch ( (_lgeometricmean, (_ListType, _TupleType)), )
harmonicmean = _Dispatch ( (_lharmonicmean, (_ListType, _TupleType)), )
mean = _Dispatch ( (_lmean, (_ListType, _TupleType)), )
firstquartilescore = _Dispatch( (_lfirstquartilescore, (_ListType, _TupleType)), )
median = _Dispatch ( (_lmedianscore, (_ListType, _TupleType)), )  # replacing the media function to medianScore  _lmedian
thirdquartilescore = _Dispatch( (_lthirdquartilescore, (_ListType, _TupleType)), )
medianscore = _Dispatch ( (_lmedianscore, (_ListType, _TupleType)), )
mode = _Dispatch ( (_lmode, (_ListType, _TupleType)), )

## MOMENTS:
moment = _Dispatch ( (_lmoment, (_ListType, _TupleType)), )
variation = _Dispatch ( (__lvariation, (_ListType, _TupleType)), )
skew = _Dispatch ( (_lskew, (_ListType, _TupleType)), )
kurtosis = _Dispatch ( (_lkurtosis, (_ListType, _TupleType)), )
describe = _Dispatch ( (_ldescribe, (_ListType, _TupleType)), )

## FREQUENCY STATISTICS:
itemfreq = _Dispatch ( (_litemfreq, (_ListType, _TupleType)), )
scoreatpercentile = _Dispatch ( (_lscoreatpercentile, (_ListType, _TupleType)), )
percentileofscore = _Dispatch ( (_lpercentileofscore, (_ListType, _TupleType)), )
histogram = _Dispatch ( (_lhistogram, (_ListType, _TupleType)), )
cumfreq = _Dispatch ( (_lcumfreq, (_ListType, _TupleType)), )
relfreq = _Dispatch ( (_lrelfreq, (_ListType, _TupleType)), )

## VARIABILITY:
obrientransform = _Dispatch ( (_lobrientransform, (_ListType, _TupleType)), )
samplevar = _Dispatch ( (_lsamplevar, (_ListType, _TupleType)), )
samplestdev = _Dispatch ( (_lsamplestdev, (_ListType, _TupleType)), )
var = _Dispatch ( (_lvar, (_ListType, _TupleType)), )
stdev = _Dispatch ( (_lstdev, (_ListType, _TupleType)), )
sterr = _Dispatch ( (_lsterr, (_ListType, _TupleType)), )
sem = _Dispatch ( (_lsem, (_ListType, _TupleType)), )
z = _Dispatch ( (_lz, (_ListType, _TupleType)), )
zs = _Dispatch ( (_lzs, (_ListType, _TupleType)), )

## TRIMMING FCNS:
trimboth = _Dispatch ( (_ltrimboth, (_ListType, _TupleType)), )
trim1 = _Dispatch ( (_ltrim1, (_ListType, _TupleType)), )

## CORRELATION FCNS:
paired = _Dispatch ( (_lpaired, (_ListType, _TupleType)), )
pearsonr = _Dispatch ( (_lpearsonr, (_ListType, _TupleType)), )
spearmanr = _Dispatch ( (_lspearmanr, (_ListType, _TupleType)), )
pointbiserialr = _Dispatch ( (_lpointbiserialr, (_ListType, _TupleType)), )
kendalltau = _Dispatch ( (_lkendalltau, (_ListType, _TupleType)), )
linregress = _Dispatch ( (_llinregress, (_ListType, _TupleType)), )

## INFERENTIAL STATS:
ttest_1samp = _Dispatch ( (_lttest_1samp, (_ListType, _TupleType)), )
ttest_ind = _Dispatch ( (_lttest_ind, (_ListType, _TupleType)), )
ttest_rel = _Dispatch ( (_lttest_rel, (_ListType, _TupleType)), )
chisquare = _Dispatch ( (_lchisquare, (_ListType, _TupleType)), )
ks_2samp = _Dispatch ( (_lks_2samp, (_ListType, _TupleType)), )
mannwhitneyu = _Dispatch ( (_lmannwhitneyu, (_ListType, _TupleType)), )
ranksums = _Dispatch ( (_lranksums, (_ListType, _TupleType)), )
tiecorrect = _Dispatch ( (_ltiecorrect, (_ListType, _TupleType)), )
wilcoxont = _Dispatch ( (_lwilcoxont, (_ListType, _TupleType)), )
kruskalwallish = _Dispatch ( (_lkruskalwallish, (_ListType, _TupleType)), )
friedmanchisquare = _Dispatch ( (_lfriedmanchisquare, (_ListType, _TupleType)), )

## PROBABILITY CALCS:
chisqprob = _Dispatch ( (_lchisqprob, (_IntType, _FloatType)), )
zprob = _Dispatch ( (_lzprob, (_IntType, _FloatType)), )
ksprob = _Dispatch ( (_lksprob, (_IntType, _FloatType)), )
fprob = _Dispatch ( (_lfprob, (_IntType, _FloatType)), )
betacf = _Dispatch ( (_lbetacf, (_IntType, _FloatType)), )
betai = _Dispatch ( (_lbetai, (_IntType, _FloatType)), )
erfcc = _Dispatch ( (_lerfcc, (_IntType, _FloatType)), )
gammln = _Dispatch ( (_lgammln, (_IntType, _FloatType)), )

## ANOVA FUNCTIONS:
F_oneway = _Dispatch ( (_lF_oneway, (_ListType, _TupleType)), )
F_value = _Dispatch ( (_lF_value, (_ListType, _TupleType)), )

## SUPPORT FUNCTIONS:
_incr = _Dispatch ( (_lincr, (_ListType, _TupleType)), )
sum = _Dispatch ( (_lsum, (_ListType, _TupleType)), )
cumsum = _Dispatch ( (_lcumsum, (_ListType, _TupleType)), )
ss = _Dispatch ( (_lss, (_ListType, _TupleType)), )
summult = _Dispatch ( (_lsummult, (_ListType, _TupleType)), )
square_of_sums = _Dispatch ( (_lsquare_of_sums, (_ListType, _TupleType)), )
sumdiffsquared = _Dispatch ( (_lsumdiffsquared, (_ListType, _TupleType)), )
shellsort = _Dispatch ( (_lshellsort, (_ListType, _TupleType)), )
rankdata = _Dispatch ( (_lrankdata, (_ListType, _TupleType)), )
findwithin = _Dispatch ( (_lfindwithin, (_ListType, _TupleType)), )


#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============
#=============  THE ARRAY-VERSION OF THE STATS FUNCTIONS  ===============



#####################################
########  ACENTRAL TENDENCY  ########
#####################################

def _ageometricmean (inarray,dimension=None,keepdims=0):
    """
    Calculates the geometric mean of the values in the passed array.
    That is:  n-th root of (x1 * x2 * ... * xn).  Defaults to ALL values in
    the passed array.  Use dimension=None to flatten array first.  REMEMBER: if
    dimension=0, it collapses over dimension 0 ('rows' in a 2D array) only, and
    if dimension is a sequence, it collapses over all specified dimensions.  If
    keepdims is set to 1, the resulting array will have as many dimensions as
    inarray, with only 1 'level' per dim that was collapsed over.

    Usage:   _ageometricmean(inarray,dimension=None,keepdims=0)
    Returns: geometric mean computed over dim(s) listed in dimension
    """
    inarray = _N.array(inarray,_N.float_)
    if dimension == None:
        inarray = _N.ravel(inarray)
        size = len(inarray)
        mult = _N.power(inarray,1.0/size)
        mult = _N.multiply.reduce(mult)
    elif type(dimension) in [_IntType,_FloatType]:
        size = inarray.shape[dimension]
        mult = _N.power(inarray,1.0/size)
        mult = _N.multiply.reduce(mult,dimension)
        if keepdims == 1:
            shp = list(inarray.shape)
            shp[dimension] = 1
            sum = _N.reshape(sum,shp)
    else: # must be a SEQUENCE of dims to average over
        dims = list(dimension)
        dims.sort()
        dims.reverse()
        size = _N.array(_N.multiply.reduce(_N.take(inarray.shape,dims)),_N.float_)
        mult = _N.power(inarray,1.0/size)
        for dim in dims:
            mult = _N.multiply.reduce(mult,dim)
        if keepdims == 1:
            shp = list(inarray.shape)
            for dim in dims:
                shp[dim] = 1
            mult = _N.reshape(mult,shp)
    return mult


def _aharmonicmean (inarray,dimension=None,keepdims=0):
    """
    Calculates the harmonic mean of the values in the passed array.
    That is:  n / (1/x1 + 1/x2 + ... + 1/xn).  Defaults to ALL values in
    the passed array.  Use dimension=None to flatten array first.  REMEMBER: if
    dimension=0, it collapses over dimension 0 ('rows' in a 2D array) only, and
    if dimension is a sequence, it collapses over all specified dimensions.  If
    keepdims is set to 1, the resulting array will have as many dimensions as
    inarray, with only 1 'level' per dim that was collapsed over.

    Usage:   _aharmonicmean(inarray,dimension=None,keepdims=0)
    Returns: harmonic mean computed over dim(s) in dimension
    """
    inarray = inarray.astype(_N.float_)
    if dimension == None:
        inarray = _N.ravel(inarray)
        size = len(inarray)
        s = _N.add.reduce(1.0 / inarray)
    elif type(dimension) in [_IntType,_FloatType]:
        size = float(inarray.shape[dimension])
        s = _N.add.reduce(1.0/inarray, dimension)
        if keepdims == 1:
            shp = list(inarray.shape)
            shp[dimension] = 1
            s = _N.reshape(s,shp)
    else: # must be a SEQUENCE of dims to average over
        dims = list(dimension)
        dims.sort()
        nondims = []
        for i in range(len(inarray.shape)):
            if i not in dims:
                nondims.append(i)
        tinarray = _N.transpose(inarray,nondims+dims) # put keep-dims first
        idx = [0] *len(nondims)
        if idx == []:
            size = len(_N.ravel(inarray))
            s = _asum(1.0 / inarray)
            if keepdims == 1:
                s = _N.reshape([s],_N.ones(len(inarray.shape)))
        else:
            idx[0] = -1
            loopcap = _N.array(tinarray.shape[0:len(nondims)]) -1
            s = _N.zeros(loopcap+1,_N.float_)
            while _incr(idx,loopcap) <> -1:
                s[idx] = _asum(1.0/tinarray[idx])
            size = _N.multiply.reduce(_N.take(inarray.shape,dims))
            if keepdims == 1:
                shp = list(inarray.shape)
                for dim in dims:
                    shp[dim] = 1
                s = _N.reshape(s,shp)
    return size / s


def _amean (inarray,dimension=None,keepdims=0):
    """
    Calculates the arithmetic mean of the values in the passed array.
    That is:  1/n * (x1 + x2 + ... + xn).  Defaults to ALL values in the
    passed array.  Use dimension=None to flatten array first.  REMEMBER: if
    dimension=0, it collapses over dimension 0 ('rows' in a 2D array) only, and
    if dimension is a sequence, it collapses over all specified dimensions.  If
    keepdims is set to 1, the resulting array will have as many dimensions as
    inarray, with only 1 'level' per dim that was collapsed over.

    Usage:   _amean(inarray,dimension=None,keepdims=0)
    Returns: arithmetic mean calculated over dim(s) in dimension
    """
    if inarray.dtype in [_N.int_, _N.short,_N.ubyte]:
        inarray = inarray.astype(_N.float_)
    if dimension == None:
        inarray = _N.ravel(inarray)
        sum = _N.add.reduce(inarray)
        denom = float(len(inarray))
    elif type(dimension) in [_IntType,_FloatType]:
        sum = _asum(inarray,dimension)
        denom = float(inarray.shape[dimension])
        if keepdims == 1:
            shp = list(inarray.shape)
            shp[dimension] = 1
            sum = _N.reshape(sum,shp)
    else: # must be a TUPLE of dims to average over
        dims = list(dimension)
        dims.sort()
        dims.reverse()
        sum = inarray *1.0
        for dim in dims:
            sum = _N.add.reduce(sum,dim)
        denom = _N.array(_N.multiply.reduce(_N.take(inarray.shape,dims)),_N.float_)
        if keepdims == 1:
            shp = list(inarray.shape)
            for dim in dims:
                shp[dim] = 1
            sum = _N.reshape(sum,shp)
    return sum/denom


def _amedian (inarray,numbins=1000):
    """
    Calculates the COMPUTED median value of an array of numbers, given the
    number of bins to use for the histogram (more bins approaches finding the
    precise median value of the array; default number of bins = 1000).  From
    G.W. Heiman's Basic Stats, or CRC Probability & Statistics.
    NOTE:  THIS ROUTINE ALWAYS uses the entire passed array (flattens it first).

    Usage:   _amedian(inarray,numbins=1000)
    Returns: median calculated over ALL values in inarray
    """
    inarray = _N.ravel(inarray)
    (hist, smallest, binsize, extras) = _ahistogram(inarray,numbins,[min(inarray),max(inarray)])
    cumhist = _N.cumsum(hist)            # make cumulative histogram
    otherbins = _N.greater_equal(cumhist,len(inarray)/2.0)
    otherbins = list(otherbins)         # list of 0/1s, 1s start at median bin
    cfbin = otherbins.index(1)                # get 1st(!) index holding 50%ile score
    LRL = smallest + binsize*cfbin        # get lower read limit of that bin
    cfbelow = _N.add.reduce(hist[0:cfbin])        # cum. freq. below bin
    freq = hist[cfbin]                        # frequency IN the 50%ile bin
    median = LRL + ((len(inarray)/2.0-cfbelow)/float(freq))*binsize # MEDIAN
    return median


def _amedianscore (inarray,dimension=None):
    """
    Returns the 'middle' score of the passed array.  If there is an even
    number of scores, the mean of the 2 middle scores is returned.  Can function
    with 1D arrays, or on the FIRST dimension of 2D arrays (i.e., dimension can
    be None, to pre-flatten the array, or else dimension must equal 0).

    Usage:   _amedianscore(inarray,dimension=None)
    Returns: 'middle' score of the array, or the mean of the 2 middle scores
    """
    if dimension == None:
        inarray = _N.ravel(inarray)
        dimension = 0
    inarray = _N.sort(inarray,dimension)
    if inarray.shape[dimension] % 2 == 0:   # if even number of elements
        indx = inarray.shape[dimension]/2   # integer division correct
        median = _N.asarray(inarray[indx]+inarray[indx-1]) / 2.0
    else:
        indx = inarray.shape[dimension] / 2 # integer division correct
        median = _N.take(inarray,[indx],dimension)
        if median.shape == (1,):
            median = median[0]
    return median

def _afirstquartilescore (inarray,dimension=None):
    """
    Returns the 'first' quartile score of the passed array.  If there is an even
    number of scores, the mean of the 2 middle scores is returned.  Can function
    with 1D arrays, or on the FIRST dimension of 2D arrays (i.e., dimension can
    be None, to pre-flatten the array, or else dimension must equal 0).

    Usage:   _afirstquartilescore(inarray,dimension=None)
    Returns: 'first' quartile score of the array, or the mean of the two 25 percentile scores
    """
    if dimension == None:
        inarray = _N.ravel(inarray)
        dimension = 0
    inarray = _N.sort(inarray,dimension)
    if inarray.shape[dimension] % 2 == 0:   # if even number of elements
        indx = inarray.shape[dimension]/2   # integer division correct
        median = _N.asarray(inarray[indx]+inarray[indx-1]) / 2.0
    else:
        indx = inarray.shape[dimension] / 2 # integer division correct
        median = _N.take(inarray,[indx],dimension)
        if median.shape == (1,):
            median = median[0]
    return median


def _athirdquartilescore (inarray,dimension=None):
    """
    Returns the 'third' quartile score of the passed array.  If there is an even
    number of scores, the mean of the 2 middle scores is returned.  Can function
    with 1D arrays, or on the FIRST dimension of 2D arrays (i.e., dimension can
    be None, to pre-flatten the array, or else dimension must equal 0).

    Usage:   _athirdquartilescore(inarray,dimension=None)
    Returns: 'third' percentile score of the array, or the mean of the two 75 percentile scores
    """
    if dimension == None:
        inarray = _N.ravel(inarray)
        dimension = 0
    inarray = _N.sort(inarray,dimension)
    if inarray.shape[dimension] % 2 == 0:   # if even number of elements
        indx = inarray.shape[dimension]/2   # integer division correct
        median = _N.asarray(inarray[indx]+inarray[indx-1]) / 2.0
    else:
        indx = inarray.shape[dimension] / 2 # integer division correct
        median = _N.take(inarray,[indx],dimension)
        if median.shape == (1,):
            median = median[0]
    return median

def _amode(a, dimension=None):
    """
    Returns an array of the modal (most common) score in the passed array.
    If there is more than one such score, ONLY THE FIRST is returned.
    The bin-count for the modal values is also returned.  Operates on whole
    array (dimension=None), or on a given dimension.

    Usage:   _amode(a, dimension=None)
    Returns: array of bin-counts for mode(s), array of corresponding modal values
    """

    if dimension == None:
        a = _N.ravel(a)
        dimension = 0
    scores = pstat.aunique(_N.ravel(a))       # get ALL unique values
    testshape = list(a.shape)
    testshape[dimension] = 1
    oldmostfreq = _N.zeros(testshape)
    oldcounts = _N.zeros(testshape)
    for score in scores:
        template = _N.equal(a,score)
        counts = _asum(template,dimension,1)
        mostfrequent = _N.where(counts>oldcounts,score,oldmostfreq)
        oldcounts = _N.where(counts>oldcounts,counts,oldcounts)
        oldmostfreq = mostfrequent
    return oldcounts, mostfrequent


def _atmean(a,limits=None,inclusive=(1,1)):
    """
   Returns the arithmetic mean of all values in an array, ignoring values
   strictly outside the sequence passed to 'limits'.   Note: either limit
   in the sequence, or the value of limits itself, can be set to None.  The
   inclusive list/tuple determines whether the lower and upper limiting bounds
   (respectively) are open/exclusive (0) or closed/inclusive (1).

   Usage:   _atmean(a,limits=None,inclusive=(1,1))
   """
    if a.dtype in [_N.int_, _N.short,_N.ubyte]:
        a = a.astype(_N.float_)
    if limits == None:
        return mean(a)
    assert type(limits) in [_ListType,_TupleType,_N.ndarray], "Wrong type for limits in _atmean"
    if inclusive[0]:         lowerfcn = _N.greater_equal
    else:               lowerfcn = _N.greater
    if inclusive[1]:         upperfcn = _N.less_equal
    else:               upperfcn = _N.less
    if limits[0] > _N.maximum.reduce(_N.ravel(a)) or limits[1] < _N.minimum.reduce(_N.ravel(a)):
        raise ValueError, "No array values within given limits (_atmean)."
    elif limits[0]==None and limits[1]<>None:
        mask = upperfcn(a,limits[1])
    elif limits[0]<>None and limits[1]==None:
        mask = lowerfcn(a,limits[0])
    elif limits[0]<>None and limits[1]<>None:
        mask = lowerfcn(a,limits[0])*upperfcn(a,limits[1])
    s = float(_N.add.reduce(_N.ravel(a*mask)))
    n = float(_N.add.reduce(_N.ravel(mask)))
    return s/n


def _atvar(a,limits=None,inclusive=(1,1)):
    """
   Returns the sample variance of values in an array, (i.e., using _N-1),
   ignoring values strictly outside the sequence passed to 'limits'.
   Note: either limit in the sequence, or the value of limits itself,
   can be set to None.  The inclusive list/tuple determines whether the lower
   and upper limiting bounds (respectively) are open/exclusive (0) or
   closed/inclusive (1). ASSUMES A FLAT ARRAY (OR ELSE PREFLATTENS).

   Usage:   _atvar(a,limits=None,inclusive=(1,1))
   """
    a = a.astype(_N.float_)
    if limits == None or limits == [None,None]:
        return _avar(a)
    assert type(limits) in [_ListType,_TupleType,_N.ndarray], "Wrong type for limits in _atvar"
    if inclusive[0]:    lowerfcn = _N.greater_equal
    else:               lowerfcn = _N.greater
    if inclusive[1]:    upperfcn = _N.less_equal
    else:               upperfcn = _N.less
    if limits[0] > _N.maximum.reduce(_N.ravel(a)) or limits[1] < _N.minimum.reduce(_N.ravel(a)):
        raise ValueError, "No array values within given limits (_atvar)."
    elif limits[0]==None and limits[1]<>None:
        mask = upperfcn(a,limits[1])
    elif limits[0]<>None and limits[1]==None:
        mask = lowerfcn(a,limits[0])
    elif limits[0]<>None and limits[1]<>None:
        mask = lowerfcn(a,limits[0])*upperfcn(a,limits[1])

    a = _N.compress(mask,a)  # squish out excluded values
    return _avar(a)


def atmin(a,lowerlimit=None,dimension=None,inclusive=1):
    """
   Returns the minimum value of a, along dimension, including only values less
   than (or equal to, if inclusive=1) lowerlimit.  If the limit is set to None,
   all values in the array are used.

   Usage:   atmin(a,lowerlimit=None,dimension=None,inclusive=1)
   """
    if inclusive:         lowerfcn = _N.greater
    else:               lowerfcn = _N.greater_equal
    if dimension == None:
        a = _N.ravel(a)
        dimension = 0
    if lowerlimit == None:
        lowerlimit = _N.minimum.reduce(_N.ravel(a))-11
    biggest = _N.maximum.reduce(_N.ravel(a))
    ta = _N.where(lowerfcn(a,lowerlimit),a,biggest)
    return _N.minimum.reduce(ta,dimension)


def atmax(a,upperlimit,dimension=None,inclusive=1):
    """
   Returns the maximum value of a, along dimension, including only values greater
   than (or equal to, if inclusive=1) upperlimit.  If the limit is set to None,
   a limit larger than the max value in the array is used.

   Usage:   atmax(a,upperlimit,dimension=None,inclusive=1)
   """
    if inclusive:         upperfcn = _N.less
    else:               upperfcn = _N.less_equal
    if dimension == None:
        a = _N.ravel(a)
        dimension = 0
    if upperlimit == None:
        upperlimit = _N.maximum.reduce(_N.ravel(a))+1
    smallest = _N.minimum.reduce(_N.ravel(a))
    ta = _N.where(upperfcn(a,upperlimit),a,smallest)
    return _N.maximum.reduce(ta,dimension)


def _atstdev(a,limits=None,inclusive=(1,1)):
    """
   Returns the standard deviation of all values in an array, ignoring values
   strictly outside the sequence passed to 'limits'.   Note: either limit
   in the sequence, or the value of limits itself, can be set to None.  The
   inclusive list/tuple determines whether the lower and upper limiting bounds
   (respectively) are open/exclusive (0) or closed/inclusive (1).

   Usage:   _atstdev(a,limits=None,inclusive=(1,1))
   """
    return _N.sqrt(tvar(a,limits,inclusive))


def _atsem(a,limits=None,inclusive=(1,1)):
    """
   Returns the standard error of the mean for the values in an array,
   (i.e., using _N for the denominator), ignoring values strictly outside
   the sequence passed to 'limits'.   Note: either limit in the sequence,
   or the value of limits itself, can be set to None.  The inclusive list/tuple
   determines whether the lower and upper limiting bounds (respectively) are
   open/exclusive (0) or closed/inclusive (1).

   Usage:   _atsem(a,limits=None,inclusive=(1,1))
   """
    sd = tstdev(a,limits,inclusive)
    if limits == None or limits == [None,None]:
        n = float(len(_N.ravel(a)))
        limits = [min(a)-1, max(a)+1]
    assert type(limits) in [_ListType,_TupleType,_N.ndarray], "Wrong type for limits in _atsem"
    if inclusive[0]:         lowerfcn = _N.greater_equal
    else:               lowerfcn = _N.greater
    if inclusive[1]:         upperfcn = _N.less_equal
    else:               upperfcn = _N.less
    if limits[0] > _N.maximum.reduce(_N.ravel(a)) or limits[1] < _N.minimum.reduce(_N.ravel(a)):
        raise ValueError, "No array values within given limits (_atsem)."
    elif limits[0]==None and limits[1]<>None:
        mask = upperfcn(a,limits[1])
    elif limits[0]<>None and limits[1]==None:
        mask = lowerfcn(a,limits[0])
    elif limits[0]<>None and limits[1]<>None:
        mask = lowerfcn(a,limits[0])*upperfcn(a,limits[1])
    term1 = _N.add.reduce(_N.ravel(a*a*mask))
    n = float(_N.add.reduce(_N.ravel(mask)))
    return sd/_math.sqrt(n)

#####################################
############  _amomentS  #############
#####################################

def _amoment(a,moment=1,dimension=None):
    """
    Calculates the nth moment about the mean for a sample (defaults to the
    1st moment).  Generally used to calculate coefficients of skewness and
    kurtosis.  Dimension can equal None (ravel array first), an integer
    (the dimension over which to operate), or a sequence (operate over
    multiple dimensions).

    Usage:   _amoment(a,moment=1,dimension=None)
    Returns: appropriate moment along given dimension
    """
    if dimension == None:
        a = _N.ravel(a)
        dimension = 0
    if moment == 1:
        return 0.0
    else:
        mn = _amean(a,dimension,1)  # 1=keepdims
        s = _N.power((a-mn),moment)
        return _amean(s,dimension)


def __avariation(a,dimension=None):
    """
    Returns the coefficient of variation, as defined in CRC Standard
    Probability and Statistics, p.6. Dimension can equal None (ravel array
    first), an integer (the dimension over which to operate), or a
    sequence (operate over multiple dimensions).

    Usage:   __avariation(a,dimension=None)
    """
    return 100.0*_asamplestdev(a,dimension)/_amean(a,dimension)


def _askew(a,dimension=None):
    """
    Returns the skewness of a distribution (normal ==> 0.0; >0 means extra
    weight in left tail).  Use _askewtest() to see if it's close enough.
    Dimension can equal None (ravel array first), an integer (the
    dimension over which to operate), or a sequence (operate over multiple
    dimensions).

    Usage:   _askew(a, dimension=None)
    Returns: skew of vals in a along dimension, returning ZERO where all vals equal
    """
    denom = _N.power(_amoment(a,2,dimension),1.5)
    zero = _N.equal(denom,0)
    if type(denom) == _N.ndarray and _asum(zero) <> 0:
        print "Number of zeros in _askew: ",_asum(zero)
    denom = denom + zero  # prevent divide-by-zero
    return _N.where(zero, 0, _amoment(a,3,dimension)/denom)


def _akurtosis(a,dimension=None):
    """
    Returns the kurtosis of a distribution (normal ==> 3.0; >3 means
    heavier in the tails, and usually more peaked).  Use _akurtosistest()
    to see if it's close enough.  Dimension can equal None (ravel array
    first), an integer (the dimension over which to operate), or a
    sequence (operate over multiple dimensions).

    Usage:   _akurtosis(a,dimension=None)
    Returns: kurtosis of values in a along dimension, and ZERO where all vals equal
    """
    denom = _N.power(_amoment(a,2,dimension),2)
    zero = _N.equal(denom,0)
    if type(denom) == _N.ndarray and _asum(zero) <> 0:
        print "Number of zeros in _akurtosis: ",_asum(zero)
    denom = denom + zero  # prevent divide-by-zero
    return _N.where(zero,0,_amoment(a,4,dimension)/denom)


def _adescribe(inarray,dimension=None):
    """
   Returns several descriptive statistics of the passed array.  Dimension
   can equal None (ravel array first), an integer (the dimension over
   which to operate), or a sequence (operate over multiple dimensions).

   Usage:   _adescribe(inarray,dimension=None)
   Returns: n, (min,max), mean, standard deviation, skew, kurtosis
   """
    if dimension == None:
        inarray = _N.ravel(inarray)
        dimension = 0
    n = inarray.shape[dimension]
    mm = (_N.minimum.reduce(inarray),_N.maximum.reduce(inarray))
    m = _amean(inarray,dimension)
    sd = _astdev(inarray,dimension)
    skew = _askew(inarray,dimension)
    kurt = _akurtosis(inarray,dimension)
    return n, mm, m, sd, skew, kurt


#####################################
########  NORMALITY TESTS  ##########
#####################################

def _askewtest(a,dimension=None):
    """
    Tests whether the skew is significantly different from a normal
    distribution.  Dimension can equal None (ravel array first), an
    integer (the dimension over which to operate), or a sequence (operate
    over multiple dimensions).

    Usage:   _askewtest(a,dimension=None)
    Returns: z-score and 2-tail z-probability
    """
    if dimension == None:
        a = _N.ravel(a)
        dimension = 0
    b2 = _askew(a,dimension)
    n = float(a.shape[dimension])
    y = b2 * _N.sqrt(((n+1)*(n+3)) / (6.0*(n-2)) )
    beta2 = ( 3.0*(n*n+27*n-70)*(n+1)*(n+3) ) / ( (n-2.0)*(n+5)*(n+7)*(n+9) )
    W2 = -1 + _N.sqrt(2*(beta2-1))
    delta = 1/_N.sqrt(_N.log(_N.sqrt(W2)))
    alpha = _N.sqrt(2/(W2-1))
    y = _N.where(y==0,1,y)
    Z = delta*_N.log(y/alpha + _N.sqrt((y/alpha)**2+1))
    return Z, (1.0-zprob(float(Z)))*2


def _akurtosistest(a,dimension=None):
    """
    Tests whether a dataset has normal kurtosis (i.e.,
    kurtosis=3(n-1)/(n+1)) Valid only for n>20.  Dimension can equal None
    (ravel array first), an integer (the dimension over which to operate),
    or a sequence (operate over multiple dimensions).

    Usage:   _akurtosistest(a,dimension=None)
    Returns: z-score and 2-tail z-probability, returns 0 for bad pixels
    """
    if dimension == None:
        a = _N.ravel(a)
        dimension = 0
    n = float(a.shape[dimension])
    if n<20:
        print "_akurtosistest only valid for n>=20 ... continuing anyway, n=",n
    b2 = _akurtosis(a,dimension)
    E = 3.0*(n-1) /(n+1)
    varb2 = 24.0*n*(n-2)*(n-3) / ((n+1)*(n+1)*(n+3)*(n+5))
    x = (b2-E)/_N.sqrt(varb2)
    sqrtbeta1 = 6.0*(n*n-5*n+2)/((n+7)*(n+9)) * _N.sqrt((6.0*(n+3)*(n+5))/
                                                       (n*(n-2)*(n-3)))
    A = 6.0 + 8.0/sqrtbeta1 *(2.0/sqrtbeta1 + _N.sqrt(1+4.0/(sqrtbeta1**2)))
    term1 = 1 -2/(9.0*A)
    denom = 1 +x*_N.sqrt(2/(A-4.0))
    denom = _N.where(_N.less(denom,0), 99, denom)
    term2 = _N.where(_N.equal(denom,0), term1, _N.power((1-2.0/A)/denom,1/3.0))
    Z = ( term1 - term2 ) / _N.sqrt(2/(9.0*A))
    Z = _N.where(_N.equal(denom,99), 0, Z)
    return Z, (1.0-zprob(Z))*2


def _anormaltest(a,dimension=None):
    """
    Tests whether skew and/OR kurtosis of dataset differs from normal
    curve.  Can operate over multiple dimensions.  Dimension can equal
    None (ravel array first), an integer (the dimension over which to
    operate), or a sequence (operate over multiple dimensions).

    Usage:   _anormaltest(a,dimension=None)
    Returns: z-score and 2-tail probability
    """
    if dimension == None:
        a = _N.ravel(a)
        dimension = 0
    s,p = _askewtest(a,dimension)
    k,p = _akurtosistest(a,dimension)
    k2 = _N.power(s,2) + _N.power(k,2)
    return k2, _achisqprob(k2,2)

#####################################
######  AFREQUENCY FUNCTIONS  #######
#####################################

def _aitemfreq(a):
    """
    Returns a 2D array of item frequencies.  Column 1 contains item values,
    column 2 contains their respective counts.  Assumes a 1D array is passed.
    (sorting OK?)

    Usage:   _aitemfreq(a)
    Returns: a 2D frequency table (col [0:n-1]=scores, col n=frequencies)
    """
    scores = pstat.aunique(a)
    scores = _N.sort(scores)
    freq = _N.zeros(len(scores))
    for i in range(len(scores)):
        freq[i] = _N.add.reduce(_N.equal(a,scores[i]))
    return _N.array(pstat.aabut(scores, freq))


def _ascoreatpercentile (inarray, percent):
    """
    Usage:   _ascoreatpercentile(inarray,percent)   0<percent<100
    Returns: score at given percentile, relative to inarray distribution
    """
    percent = percent / 100.0
    targetcf = percent*len(inarray)
    h, lrl, binsize, extras = histogram(inarray)
    cumhist = cumsum(h*1)
    for i in range(len(cumhist)):
        if cumhist[i] >= targetcf:
            break
    score = binsize * ((targetcf - cumhist[i-1]) / float(h[i])) + (lrl+binsize*i)
    return score


def _apercentileofscore (inarray,score,histbins=10,defaultlimits=None):
    """
    Note: result of this function depends on the values used to histogram
    the data(!).

    Usage:   _apercentileofscore(inarray,score,histbins=10,defaultlimits=None)
    Returns: percentile-position of score (0-100) relative to inarray
    """
    h, lrl, binsize, extras = histogram(inarray,histbins,defaultlimits)
    cumhist = cumsum(h*1)
    i = int((score - lrl)/float(binsize))
    pct = (cumhist[i-1]+((score-(lrl+binsize*i))/float(binsize))*h[i])/float(len(inarray)) * 100
    return pct


def _ahistogram (inarray,numbins=10,defaultlimits=None,printextras=1):
    """
    Returns (i) an array of histogram bin counts, (ii) the smallest value
    of the histogram binning, and (iii) the bin width (the last 2 are not
    necessarily integers).  Default number of bins is 10.  Defaultlimits
    can be None (the routine picks bins spanning all the numbers in the
    inarray) or a 2-sequence (lowerlimit, upperlimit).  Returns all of the
    following: array of bin values, lowerreallimit, binsize, extrapoints.

    Usage:   _ahistogram(inarray,numbins=10,defaultlimits=None,printextras=1)
    Returns: (array of bin counts, bin-minimum, min-width, #-points-outside-range)
    """
    inarray = _N.ravel(inarray)               # flatten any >1D arrays
    if (defaultlimits <> None):
        lowerreallimit = defaultlimits[0]
        upperreallimit = defaultlimits[1]
        binsize = (upperreallimit-lowerreallimit) / float(numbins)
    else:
        Min = _N.minimum.reduce(inarray)
        Max = _N.maximum.reduce(inarray)
        estbinwidth = float(Max - Min)/float(numbins) + 1e-6
        binsize = (Max-Min+estbinwidth)/float(numbins)
        lowerreallimit = Min - binsize/2.0  #lower real limit,1st bin
    bins = _N.zeros(numbins)
    extrapoints = 0
    for num in inarray:
        try:
            if (num-lowerreallimit) < 0:
                extrapoints = extrapoints + 1
            else:
                bintoincrement = int((num-lowerreallimit) / float(binsize))
                bins[bintoincrement] = bins[bintoincrement] + 1
        except:                           # point outside lower/upper limits
            extrapoints = extrapoints + 1
    if (extrapoints > 0 and printextras == 1):
        print '\nPoints outside given histogram range =',extrapoints
    return (bins, lowerreallimit, binsize, extrapoints)


def _acumfreq(a,numbins=10,defaultreallimits=None):
    """
    Returns a cumulative frequency histogram, using the histogram function.
    Defaultreallimits can be None (use all data), or a 2-sequence containing
    lower and upper limits on values to include.

    Usage:   _acumfreq(a,numbins=10,defaultreallimits=None)
    Returns: array of cumfreq bin values, lowerreallimit, binsize, extrapoints
    """
    h,l,b,e = histogram(a,numbins,defaultreallimits)
    cumhist = cumsum(h*1)
    return cumhist,l,b,e


def _arelfreq(a,numbins=10,defaultreallimits=None):
    """
    Returns a relative frequency histogram, using the histogram function.
    Defaultreallimits can be None (use all data), or a 2-sequence containing
    lower and upper limits on values to include.

    Usage:   _arelfreq(a,numbins=10,defaultreallimits=None)
    Returns: array of cumfreq bin values, lowerreallimit, binsize, extrapoints
    """
    h,l,b,e = histogram(a,numbins,defaultreallimits)
    h = _N.array(h/float(a.shape[0]))
    return h,l,b,e


#####################################
######  _avarIABILITY FUNCTIONS  #####
#####################################

def _aobrientransform(*args):
    """
    Computes a transform on input data (any number of columns).  Used to
    test for homogeneity of variance prior to running one-way stats.  Each
    array in *args is one level of a factor.  If an F_oneway() run on the
    transformed data and found significant, variances are unequal.   From
    Maxwell and Delaney, p.112.

    Usage:   _aobrientransform(*args)    *args = 1D arrays, one per level of factor
    Returns: transformed data for use in an ANOVA
    """
    TINY = 1e-10
    k = len(args)
    n = _N.zeros(k,_N.float_)
    v = _N.zeros(k,_N.float_)
    m = _N.zeros(k,_N.float_)
    nargs = []
    for i in range(k):
        nargs.append(args[i].astype(_N.float_))
        n[i] = float(len(nargs[i]))
        v[i] = var(nargs[i])
        m[i] = mean(nargs[i])
    for j in range(k):
        for i in range(int(n[j])):
            t1 = (n[j]-1.5)*n[j]*(nargs[j][i]-m[j])**2
            t2 = 0.5*v[j]*(n[j]-1.0)
            t3 = (n[j]-1.0)*(n[j]-2.0)
            nargs[j][i] = (t1-t2) / float(t3)
    check = 1
    for j in range(k):
        if v[j] - mean(nargs[j]) > TINY:
            check = 0
    if check <> 1:
        raise ValueError, 'Lack of convergence in obrientransform.'
    else:
        return _N.array(nargs)


def _asamplevar (inarray,dimension=None,keepdims=0):
    """
    Returns the sample standard deviation of the values in the passed
    array (i.e., using _N).  Dimension can equal None (ravel array first),
    an integer (the dimension over which to operate), or a sequence
    (operate over multiple dimensions).  Set keepdims=1 to return an array
    with the same number of dimensions as inarray.

    Usage:   _asamplevar(inarray,dimension=None,keepdims=0)
    """
    if dimension == None:
        inarray = _N.ravel(inarray)
        dimension = 0
    if dimension == 1:
        mn = _amean(inarray,dimension)[:,_N.NewAxis]
    else:
        mn = _amean(inarray,dimension,keepdims=1)
    deviations = inarray - mn
    if type(dimension) == _ListType:
        n = 1
        for d in dimension:
            n = n*inarray.shape[d]
    else:
        n = inarray.shape[dimension]
    svar = _ass(deviations,dimension,keepdims) / float(n)
    return svar


def _asamplestdev (inarray, dimension=None, keepdims=0):
    """
    Returns the sample standard deviation of the values in the passed
    array (i.e., using _N).  Dimension can equal None (ravel array first),
    an integer (the dimension over which to operate), or a sequence
    (operate over multiple dimensions).  Set keepdims=1 to return an array
    with the same number of dimensions as inarray.

    Usage:   _asamplestdev(inarray,dimension=None,keepdims=0)
    """
    return _N.sqrt(_asamplevar(inarray,dimension,keepdims))


def _asignaltonoise(instack,dimension=0):
    """
    Calculates signal-to-noise.  Dimension can equal None (ravel array
    first), an integer (the dimension over which to operate), or a
    sequence (operate over multiple dimensions).

    Usage:   _asignaltonoise(instack,dimension=0):
    Returns: array containing the value of (mean/stdev) along dimension, or 0 when stdev=0
    """
    m = mean(instack,dimension)
    sd = stdev(instack,dimension)
    return _N.where(sd==0,0,m/sd)


def _acov (x,y, dimension=None,keepdims=0):
    """
    Returns the estimated covariance of the values in the passed
    array (i.e., _N-1).  Dimension can equal None (ravel array first), an
    integer (the dimension over which to operate), or a sequence (operate
    over multiple dimensions).  Set keepdims=1 to return an array with the
    same number of dimensions as inarray.

    Usage:   _acov(x,y,dimension=None,keepdims=0)
    """
    if dimension == None:
        x = _N.ravel(x)
        y = _N.ravel(y)
        dimension = 0
    xmn = _amean(x,dimension,1)  # keepdims
    xdeviations = x - xmn
    ymn = _amean(y,dimension,1)  # keepdims
    ydeviations = y - ymn
    if type(dimension) == _ListType:
        n = 1
        for d in dimension:
            n = n*x.shape[d]
    else:
        n = x.shape[dimension]
    covar = _N.sum(xdeviations*ydeviations)/float(n-1)
    return covar


def _avar (inarray, dimension=None,keepdims=0):
    """
    Returns the estimated population variance of the values in the passed
    array (i.e., _N-1).  Dimension can equal None (ravel array first), an
    integer (the dimension over which to operate), or a sequence (operate
    over multiple dimensions).  Set keepdims=1 to return an array with the
    same number of dimensions as inarray.

    Usage:   _avar(inarray,dimension=None,keepdims=0)
    """
    if dimension == None:
        inarray = _N.ravel(inarray)
        dimension = 0
    mn = _amean(inarray,dimension,1)
    deviations = inarray - mn
    if type(dimension) == _ListType:
        n = 1
        for d in dimension:
            n = n*inarray.shape[d]
    else:
        n = inarray.shape[dimension]
    var = _ass(deviations,dimension,keepdims)/float(n-1)
    return var


def _astdev (inarray, dimension=None, keepdims=0):
    """
    Returns the estimated population standard deviation of the values in
    the passed array (i.e., _N-1).  Dimension can equal None (ravel array
    first), an integer (the dimension over which to operate), or a
    sequence (operate over multiple dimensions).  Set keepdims=1 to return
    an array with the same number of dimensions as inarray.

    Usage:   _astdev(inarray,dimension=None,keepdims=0)
    """
    return _N.sqrt(_avar(inarray,dimension,keepdims))


def _asterr (inarray, dimension=None, keepdims=0):
    """
    Returns the estimated population standard error of the values in the
    passed array (i.e., _N-1).  Dimension can equal None (ravel array
    first), an integer (the dimension over which to operate), or a
    sequence (operate over multiple dimensions).  Set keepdims=1 to return
    an array with the same number of dimensions as inarray.

    Usage:   _asterr(inarray,dimension=None,keepdims=0)
    """
    if dimension == None:
        inarray = _N.ravel(inarray)
        dimension = 0
    return _astdev(inarray,dimension,keepdims) / float(_N.sqrt(inarray.shape[dimension]))


def _asem (inarray, dimension=None, keepdims=0):
    """
    Returns the standard error of the mean (i.e., using _N) of the values
    in the passed array.  Dimension can equal None (ravel array first), an
    integer (the dimension over which to operate), or a sequence (operate
    over multiple dimensions).  Set keepdims=1 to return an array with the
    same number of dimensions as inarray.

    Usage:   _asem(inarray,dimension=None, keepdims=0)
    """
    if dimension == None:
        inarray = _N.ravel(inarray)
        dimension = 0
    if type(dimension) == _ListType:
        n = 1
        for d in dimension:
            n = n*inarray.shape[d]
    else:
        n = inarray.shape[dimension]
    s = _asamplestdev(inarray,dimension,keepdims) / _N.sqrt(n-1)
    return s


def _az (a, score):
    """
    Returns the z-score of a given input score, given thearray from which
    that score came.  Not appropriate for population calculations, nor for
    arrays > 1D.

    Usage:   _az(a, score)
    """
    z = (score-_amean(a)) / _asamplestdev(a)
    return z


def _azs (a):
    """
    Returns a 1D array of z-scores, one for each score in the passed array,
    computed relative to the passed array.

    Usage:   _azs(a)
    """
    zscores = []
    for item in a:
        zscores.append(z(a,item))
    return _N.array(zscores)


def _azmap (scores, compare, dimension=0):
    """
    Returns an array of z-scores the shape of scores (e.g., [x,y]), compared to
    array passed to compare (e.g., [time,x,y]).  Assumes collapsing over dim 0
    of the compare array.

    Usage:   _azs(scores, compare, dimension=0)
    """
    mns = _amean(compare,dimension)
    sstd = _asamplestdev(compare,0)
    return (scores - mns) / sstd


#####################################
#######  ATRIMMING FUNCTIONS  #######
#####################################

## deleted around() as it's in numpy now

def _athreshold(a,threshmin=None,threshmax=None,newval=0):
    """
    Like Numeric.clip() except that values <threshmid or >threshmax are replaced
    by newval instead of by threshmin/threshmax (respectively).

    Usage:   _athreshold(a,threshmin=None,threshmax=None,newval=0)
    Returns: a, with values <threshmin or >threshmax replaced with newval
    """
    mask = _N.zeros(a.shape)
    if threshmin <> None:
        mask = mask + _N.where(a<threshmin,1,0)
    if threshmax <> None:
        mask = mask + _N.where(a>threshmax,1,0)
    mask = _N.clip(mask,0,1)
    return _N.where(mask,newval,a)


def _atrimboth (a,proportiontocut):
    """
    Slices off the passed proportion of items from BOTH ends of the passed
    array (i.e., with proportiontocut=0.1, slices 'leftmost' 10% AND
    'rightmost' 10% of scores.  You must pre-sort the array if you want
    "proper" trimming.  Slices off LESS if proportion results in a
    non-integer slice index (i.e., conservatively slices off
    proportiontocut).

    Usage:   _atrimboth (a,proportiontocut)
    Returns: trimmed version of array a
    """
    a= _N.ravel(a)
    lowercut = int(proportiontocut*len(a))
    uppercut = len(a) - lowercut
    return a[lowercut:uppercut]


def _atrim1 (a,proportiontocut,tail='right'):
    """
    Slices off the passed proportion of items from ONE end of the passed
    array (i.e., if proportiontocut=0.1, slices off 'leftmost' or 'rightmost'
    10% of scores).  Slices off LESS if proportion results in a non-integer
    slice index (i.e., conservatively slices off proportiontocut).

    Usage:   _atrim1(a,proportiontocut,tail='right')  or set tail='left'
    Returns: trimmed version of array a
    """
    a= _N.ravel(a)
    if _string.lower(tail) == 'right':
        lowercut = 0
        uppercut = len(a) - int(proportiontocut*len(a))
    elif _string.lower(tail) == 'left':
        lowercut = int(proportiontocut*len(a))
        uppercut = len(a)
    return a[lowercut:uppercut]


#####################################
#####  ACORRELATION FUNCTIONS  ######
#####################################

def _acovariance(X):
    """
    Computes the covariance matrix of a matrix X.  Requires a 2D matrix input.

    Usage:   _acovariance(X)
    Returns: covariance matrix of X
    """
    if len(X.shape) <> 2:
        raise TypeError, "_acovariance requires 2D matrices"
    n = X.shape[0]
    mX = _amean(X,0)
    return _N.dot(_N.transpose(X),X) / float(n) - _N.multiply.outer(mX,mX)


def _acorrelation(X):
    """
    Computes the correlation matrix of a matrix X.  Requires a 2D matrix input.

    Usage:   _acorrelation(X)
    Returns: correlation matrix of X
    """
    C = _acovariance(X)
    V = _N.diagonal(C)
    return C / _N.sqrt(_N.multiply.outer(V,V))

def _round(x, cifras):
    try:
        x= round(x, cifras)
    except:
        return x

def _apaired(x,y, allData= True):
    """
    Interactively determines the type of data in x and y, and then runs the
    appropriated statistic for paired group data.

    Usage:   _apaired(x,y)     x,y = the two arrays of values to be compared
    Returns: appropriate statistic name, value, and probability
    """
    result= list()
    if allData:
        samples= ['i','r','c']
    else:
        samples = ['']
    while not any([True for sample in samples if sample in ['i','r','c','I','R','C']]):
        print 'Independent or related samples, or correlation (i,r,c): ',
        samples = raw_input()

    if any([True for sample in samples if sample in ['i','I','r','R']]):
        result.append('Comparing variances ...')
        # USE O'BRIEN'S TEST FOR HOMOGENEITY OF VARIANCE, Maxwell & delaney, p.112
        r = obrientransform(x, y)
        f, p = F_oneway(pstat.colex(r,0), pstat.colex(r,1))
        if p < 0.05:
            vartype='unequal, p='+str(round(p,4))
        else:
            vartype='equal'
        result.append(vartype)
        if any([True for sample in samples if sample in ['i','I']]):
            if vartype[0]=='e':
                t,p = ttest_ind(x,y,None,0)
                result.append('')
                result.extend(['Independent samples t-test:  ',
                               "t-value",        _round(t,4),
                               "two-tailed prob", _round(p,4)])
            else:
                if len(x)>20 or len(y)>20:
                    z,p = ranksums(x, y)
                    result.extend(['Rank Sums test (NONparametric, n>20):  ',
                                   "a z-statistic",      round(z,4),
                                   "two-tailed p-value", round(p,4)])
                else:
                    u,p = mannwhitneyu(x, y)
                    result.extend(['Mann-Whitney U-test (NONparametric, ns<20):  ',
                                   "u-statistic",        round(u,4),
                                   "one-tailed p-value", round(p,4)])

        if any([True for sample in samples if sample in ['r','R']]):  # RELATED SAMPLES
            if vartype[0]=='e':
                t,p = ttest_rel(x,y,0)
                result.extend(['Related samples t-test:  ',
                               "t-value",         round(t,4),
                               "two-tailed prob", round(p,4)])
            else:
                t,p = ranksums(x,y)
                result.extend(['Wilcoxon T-test (NONparametric):  ',
                               'a z-statistic',      round(t,4),
                               'two-tailed p-value', round(p,4)])
        result.append('')
    if allData:
        corrtype=  ['c','r','d']  # CORRELATION ANALYSIS
    else:
        corrtype = ''
    if corrtype:
        while not any([True for sample in corrtype if sample in ['c','C','r','R','d','D']]):
            print '\nIs the data Continuous, Ranked, or Dichotomous (c,r,d): ',
            corrtype = raw_input()
        if any([True for sample in corrtype if sample in ['c','C']]):
            m,b,r,p,see,n = linregress(x,y)
            result.append('')
            result.append('Linear regression for continuous variables ...')
            lol = ['Slope',      round(m,4) ,
                   'Intercept',  round(b,4),
                   'r',          round(r,4),
                   'Prob',       round(p,4),
                   'SEestimate', round(see,4),
                   'n',          int(n)]
            result.extend(lol)
        if any([True for sample in corrtype if sample in ['r','R']]):
            r,p = spearmanr(x,y)
            result.append('')
            result.append('Correlation for ranked variables ...')
            result.extend([ "Spearman's r",       round(r,4),
                            "two-tailed p-value", round(p,4)])
        if any([True for sample in corrtype if sample in ['d','D']]): # DICHOTOMOUS
            r,p = pointbiserialr(x,y)
            result.append('')
            result.append('Assuming x contains a dichotomous variable ...')
            result.extend(["Point-biserial r",   _round(r,4),
                           "two-tailed p-value", _round(p,4)])
    return result


def dices(x,y):
    """
    Calculates Dice's coefficient ... (2*number of common terms)/(number of terms in x +
    number of terms in y). Returns a value between 0 (orthogonal) and 1.

    Usage:  dices(x,y)
    """
    import sets
    x = sets.Set(x)
    y = sets.Set(y)
    common = len(x.intersection(y))
    total = float(len(x) + len(y))
    return 2*common/total


def icc(x,y=None,verbose=0):
    """
    Calculates intraclass correlation coefficients using simple, Type I sums of squares.
    If only one variable is passed, assumed it's an Nx2 matrix

    Usage:   icc(x,y=None,verbose=0)
    Returns: icc rho, prob ####PROB IS A GUESS BASED ON PEARSON
    """
    TINY = 1.0e-20
    if y:
        all = _N.concatenate([x,y],0)
    else:
        all = x+0
        x = all[:,0]
        y = all[:,1]
    tota_lss = _ass(all-mean(all))
    pairmeans = (x+y)/2.
    withinss = _ass(x-pairmeans) + _ass(y-pairmeans)
    withindf = float(len(x))
    betwdf = float(len(x)-1)
    withinms = withinss / withindf
    betweenms = (tota_lss-withinss) / betwdf
    rho = (betweenms-withinms)/(withinms+betweenms)
    t = rho*_math.sqrt(betwdf/((1.0-rho+TINY)*(1.0+rho+TINY)))
    prob = _abetai(0.5*betwdf,0.5,betwdf/(betwdf+t*t),verbose)
    return rho, prob


def _alincc(x,y):
    """
    Calculates Lin's concordance correlation coefficient.

    Usage:   _alincc(x,y)    where x, y are equal-length arrays
    Returns: Lin's CC
    """
    x = _N.ravel(x)
    y = _N.ravel(y)
    covar = _acov(x,y)*(len(x)-1)/float(len(x))  # correct denom to n
    xvar = _avar(x)*(len(x)-1)/float(len(x))  # correct denom to n
    yvar = _avar(y)*(len(y)-1)/float(len(y))  # correct denom to n
    lincc = (2 * covar) / ((xvar+yvar) +((_amean(x)-_amean(y))**2))
    return lincc


def _apearsonr(x,y,verbose=1):
    """
    Calculates a Pearson correlation coefficient and returns p.  Taken
    from Heiman's Basic Statistics for the Behav. Sci (2nd), p.195.

    Usage:   _apearsonr(x,y,verbose=1)      where x,y are equal length arrays
    Returns: Pearson's r, two-tailed p-value
    """
    TINY = 1.0e-20
    n = len(x)
    xmean = _amean(x)
    ymean = _amean(y)
    r_num = n*(_N.add.reduce(x*y)) - _N.add.reduce(x)*_N.add.reduce(y)
    r_den = _math.sqrt((n*_ass(x) - _asquare_of_sums(x))*(n*_ass(y)-_asquare_of_sums(y)))
    r = (r_num / r_den)
    df = n-2
    t = r*_math.sqrt(df/((1.0-r+TINY)*(1.0+r+TINY)))
    prob = _abetai(0.5*df,0.5,df/(df+t*t),verbose)
    return r,prob


def _aspearmanr(x,y):
    """
    Calculates a Spearman rank-order correlation coefficient.  Taken
    from Heiman's Basic Statistics for the Behav. Sci (1st), p.192.

    Usage:   _aspearmanr(x,y)      where x,y are equal-length arrays
    Returns: Spearman's r, two-tailed p-value
    """
    TINY = 1e-30
    n = len(x)
    rankx = rankdata(x)
    ranky = rankdata(y)
    dsq = _N.add.reduce((rankx-ranky)**2)
    rs = 1 - 6*dsq / float(n*(n**2-1))
    t = rs * _math.sqrt((n-2) / ((rs+1.0)*(1.0-rs)))
    df = n-2
    probrs = _abetai(0.5*df,0.5,df/(df+t*t))
    # probability values for rs are from part 2 of the spearman function in
    # Numerical Recipes, p.510.  They close to tables, but not exact.(?)
    return rs, probrs


def _apointbiserialr(x,y):
    """
    Calculates a point-biserial correlation coefficient and the associated
    probability value.  Taken from Heiman's Basic Statistics for the Behav.
    Sci (1st), p.194.

    Usage:   _apointbiserialr(x,y)      where x,y are equal length arrays
    Returns: Point-biserial r, two-tailed p-value
    """
    TINY = 1e-30
    categories = pstat.aunique(x)
    data = pstat.aabut(x,y)
    if len(categories) <> 2:
        return None, None #'Cannot be calculated', "Exactly 2 categories required (in x) for pointbiserialr()."
    else:   # there are 2 categories, continue
        codemap = pstat.aabut(categories,_N.arange(2))
        recoded = pstat.arecode(data,codemap,0)
        x = pstat.alinexand(data,0,categories[0])
        y = pstat.alinexand(data,0,categories[1])
        xmean = _amean(pstat.acolex(x,1))
        ymean = _amean(pstat.acolex(y,1))
        n = len(data)
        adjust = _math.sqrt((len(x)/float(n))*(len(y)/float(n)))
        rpb = (ymean - xmean)/_asamplestdev(pstat.acolex(data,1))*adjust
        df = n-2
        t = rpb*_math.sqrt(df/((1.0-rpb+TINY)*(1.0+rpb+TINY)))
        prob = _abetai(0.5*df,0.5,df/(df+t*t))
        return rpb, prob


def _akendalltau(x,y):
    """
    Calculates Kendall's tau ... correlation of ordinal data.  Adapted
    from function kendl1 in Numerical Recipes.  Needs good test-cases.@@@

    Usage:   _akendalltau(x,y)
    Returns: Kendall's tau, two-tailed p-value
    """
    n1 = 0
    n2 = 0
    iss = 0
    for j in range(len(x)-1):
        for k in range(j,len(y)):
            a1 = x[j] - x[k]
            a2 = y[j] - y[k]
            aa = a1 * a2
            if (aa):             # neither array has a tie
                n1 = n1 + 1
                n2 = n2 + 1
                if aa > 0:
                    iss = iss + 1
                else:
                    iss = iss -1
            else:
                if (a1):
                    n1 = n1 + 1
                else:
                    n2 = n2 + 1
    tau = iss / _math.sqrt(n1*n2)
    svar = (4.0*len(x)+10.0) / (9.0*len(x)*(len(x)-1))
    z = tau / _math.sqrt(svar)
    prob = erfcc(abs(z)/1.4142136)
    return tau, prob


def _alinregress(*args):
    """
    Calculates a regression line on two arrays, x and y, corresponding to x,y
    pairs.  If a single 2D array is passed, _alinregress finds dim with 2 levels
    and splits data into x,y pairs along that dim.

    Usage:   _alinregress(*args)    args=2 equal-length arrays, or one 2D array
    Returns: slope, intercept, r, two-tailed prob, sterr-of-the-estimate, n
    """
    TINY = 1.0e-20
    if len(args) == 1:  # more than 1D array?
        args = args[0]
        if len(args) == 2:
            x = args[0]
            y = args[1]
        else:
            x = args[:,0]
            y = args[:,1]
    else:
        x = args[0]
        y = args[1]
    n = len(x)
    xmean = _amean(x)
    ymean = _amean(y)
    r_num = n*(_N.add.reduce(x*y)) - _N.add.reduce(x)*_N.add.reduce(y)
    r_den = _math.sqrt((n*_ass(x) - _asquare_of_sums(x))*(n*_ass(y)-_asquare_of_sums(y)))
    r = r_num / r_den
    z = 0.5*_math.log((1.0+r+TINY)/(1.0-r+TINY))
    df = n-2
    t = r*_math.sqrt(df/((1.0-r+TINY)*(1.0+r+TINY)))
    prob = _abetai(0.5*df,0.5,df/(df+t*t))
    slope = r_num / (float(n)*_ass(x) - _asquare_of_sums(x))
    intercept = ymean - slope*xmean
    sterrest = _math.sqrt(1-r*r)*_asamplestdev(y)
    return slope, intercept, r, prob, sterrest, n

def amasslinregress(*args):
    """
    Calculates a regression line on one 1D array (x) and one _N-D array (y).

    Returns: slope, intercept, r, two-tailed prob, sterr-of-the-estimate, n
    """
    TINY = 1.0e-20
    if len(args) == 1:  # more than 1D array?
        args = args[0]
        if len(args) == 2:
            x = _N.ravel(args[0])
            y = args[1]
        else:
            x = _N.ravel(args[:,0])
            y = args[:,1]
    else:
        x = args[0]
        y = args[1]
    x = x.astype(_N.float_)
    y = y.astype(_N.float_)
    n = len(x)
    xmean = _amean(x)
    ymean = _amean(y,0)
    shp = _N.ones(len(y.shape))
    shp[0] = len(x)
    x.shape = shp
    print x.shape, y.shape
    r_num = n*(_N.add.reduce(x*y,0)) - _N.add.reduce(x)*_N.add.reduce(y,0)
    r_den = _N.sqrt((n*_ass(x) - _asquare_of_sums(x))*(n*_ass(y,0)-_asquare_of_sums(y,0)))
    zerodivproblem = _N.equal(r_den,0)
    r_den = _N.where(zerodivproblem,1,r_den)  # avoid zero-division in 1st place
    r = r_num / r_den  # need to do this nicely for matrix division
    r = _N.where(zerodivproblem,0.0,r)
    z = 0.5*_N.log((1.0+r+TINY)/(1.0-r+TINY))
    df = n-2
    t = r*_N.sqrt(df/((1.0-r+TINY)*(1.0+r+TINY)))
    prob = _abetai(0.5*df,0.5,df/(df+t*t))

    ss = float(n)*_ass(x)-_asquare_of_sums(x)
    s_den = _N.where(ss==0,1,ss)  # avoid zero-division in 1st place
    slope = r_num / s_den
    intercept = ymean - slope*xmean
    sterrest = _N.sqrt(1-r*r)*_asamplestdev(y,0)
    return slope, intercept, r, prob, sterrest, n

#####################################
#####  AINFERENTIAL STATISTICS  #####
#####################################

def _attest_1samp(a,popmean,printit=0,name='Sample',writemode='a'):
    """
    Calculates the t-obtained for the independent samples T-test on ONE group
    of scores a, given a population mean.  If printit=1, results are printed
    to the screen.  If printit='filename', the results are output to 'filename'
    using the given writemode (default=append).  Returns t-value, and prob.

    Usage:   _attest_1samp(a,popmean,Name='Sample',printit=0,writemode='a')
    Returns: t-value, two-tailed prob
    """
    if type(a) != _N.ndarray:
        a = _N.array(a)
    x = _amean(a)
    v = _avar(a)
    n = len(a)
    df = n-1
    svar = ((n-1)*v) / float(df)
    t = (x-popmean)/_math.sqrt(svar*(1.0/n))
    prob = _abetai(0.5*df,0.5,df/(df+t*t))

    if printit <> 0:
        statname = 'Single-sample T-test.'
        outputpairedstats(printit,writemode,
                          'Population','--',popmean,0,0,0,
                          name,n,x,v,_N.minimum.reduce(_N.ravel(a)),
                          _N.maximum.reduce(_N.ravel(a)),
                          statname,t,prob)
    return t,prob


def _attest_ind (a, b, dimension=None, printit=0, name1='Samp1', name2='Samp2',writemode='a'):
    """
    Calculates the t-obtained T-test on TWO INDEPENDENT samples of scores
    a, and b.  From Numerical Recipes, p.483.  If printit=1, results are
    printed to the screen.  If printit='filename', the results are output
    to 'filename' using the given writemode (default=append).  Dimension
    can equal None (ravel array first), or an integer (the dimension over
    which to operate on a and b).

    Usage:   _attest_ind (a,b,dimension=None,printit=0, Name1='Samp1',Name2='Samp2',writemode='a')
    Returns: t-value, two-tailed p-value
    """
    if dimension == None:
        a = _N.ravel(a)
        b = _N.ravel(b)
        dimension = 0
    x1 = _amean(a,dimension)
    x2 = _amean(b,dimension)
    v1 = _avar(a,dimension)
    v2 = _avar(b,dimension)
    n1 = a.shape[dimension]
    n2 = b.shape[dimension]
    df = n1+n2-2
    svar = ((n1-1)*v1+(n2-1)*v2) / float(df)
    zerodivproblem = _N.equal(svar,0)
    svar = _N.where(zerodivproblem,1,svar)  # avoid zero-division in 1st place
    t = (x1-x2)/_N.sqrt(svar*(1.0/n1 + 1.0/n2))  # _N-D COMPUTATION HERE!!!!!!
    t = _N.where(zerodivproblem,1.0,t)     # replace NaN/wrong t-values with 1.0
    probs = _abetai(0.5*df,0.5,float(df)/(df+t*t))

    if type(t) == _N.ndarray:
        probs = _N.reshape(probs,t.shape)
    if probs.shape == (1,):
        probs = probs[0]

    if printit <> 0:
        if type(t) == _N.ndarray:
            t = t[0]
        if type(probs) == _N.ndarray:
            probs = probs[0]
        statname = 'Independent samples T-test.'
        outputpairedstats(printit,writemode,
                          name1,n1,x1,v1,_N.minimum.reduce(_N.ravel(a)),
                          _N.maximum.reduce(_N.ravel(a)),
                          name2,n2,x2,v2,_N.minimum.reduce(_N.ravel(b)),
                          _N.maximum.reduce(_N.ravel(b)),
                          statname,t,probs)
        return
    return t, probs

def ap2t(pval,df):
    """
    Tries to compute a t-value from a p-value (or pval array) and associated df.
    SLOW for large numbers of elements(!) as it re-computes p-values 20 times
    (smaller step-sizes) at which point it decides it's done. Keeps the signs
    of the input array. Returns 1000 (or -1000) if t>100.

    Usage:  ap2t(pval,df)
    Returns: an array of t-values with the shape of pval
    """
    pval = _N.array(pval)
    signs = _N.sign(pval)
    pval = abs(pval)
    t = _N.ones(pval.shape,_N.float_)*50
    step = _N.ones(pval.shape,_N.float_)*25
    print "Initial ap2t() prob calc"
    prob = _abetai(0.5*df,0.5,float(df)/(df+t*t))
    print 'ap2t() iter: ',
    for i in range(10):
        print i,' ',
        t = _N.where(pval<prob,t+step,t-step)
        prob = _abetai(0.5*df,0.5,float(df)/(df+t*t))
        step = step/2
    print
    # since this is an ugly hack, we get ugly boundaries
    t = _N.where(t>99.9,1000,t)      # hit upper-boundary
    t = t+signs
    return t #, prob, pval


def _attest_rel (a,b,dimension=None,printit=0,name1='Samp1',name2='Samp2',writemode='a'):
    """
    Calculates the t-obtained T-test on TWO RELATED samples of scores, a
    and b.  From Numerical Recipes, p.483.  If printit=1, results are
    printed to the screen.  If printit='filename', the results are output
    to 'filename' using the given writemode (default=append).  Dimension
    can equal None (ravel array first), or an integer (the dimension over
    which to operate on a and b).

    Usage:   _attest_rel(a,b,dimension=None,printit=0, name1='Samp1',name2='Samp2',writemode='a')
    Returns: t-value, two-tailed p-value
    """
    if dimension == None:
        a = _N.ravel(a)
        b = _N.ravel(b)
        dimension = 0
    if len(a)<>len(b):
        raise ValueError, 'Unequal length arrays.'
    x1 = _amean(a,dimension)
    x2 = _amean(b,dimension)
    v1 = _avar(a,dimension)
    v2 = _avar(b,dimension)
    n = a.shape[dimension]
    df = float(n-1)
    d = (a-b).astype('d')

    denom = _N.sqrt((n*_N.add.reduce(d*d,dimension) - _N.add.reduce(d,dimension)**2) /df)
    zerodivproblem = _N.equal(denom,0)
    denom = _N.where(zerodivproblem,1,denom)  # avoid zero-division in 1st place
    t = _N.add.reduce(d,dimension) / denom      # _N-D COMPUTATION HERE!!!!!!
    t = _N.where(zerodivproblem,1.0,t)     # replace NaN/wrong t-values with 1.0
    probs = _abetai(0.5*df,0.5,float(df)/(df+t*t))
    if type(t) == _N.ndarray:
        probs = _N.reshape(probs,t.shape)
    if probs.shape == (1,):
        probs = probs[0]

    if printit <> 0:
        statname = 'Related samples T-test.'
        outputpairedstats(printit,writemode,
                          name1,n,x1,v1,_N.minimum.reduce(_N.ravel(a)),
                          _N.maximum.reduce(_N.ravel(a)),
                          name2,n,x2,v2,_N.minimum.reduce(_N.ravel(b)),
                          _N.maximum.reduce(_N.ravel(b)),
                          statname,t,probs)
        return
    return t, probs


def _achisquare(f_obs,f_exp=None):
    """
    Calculates a one-way chi square for array of observed frequencies and returns
    the result.  If no expected frequencies are given, the total _N is assumed to
    be equally distributed across all groups (NOT RIGHT??)

    Usage:   _achisquare(f_obs, f_exp=None)   f_obs = array of observed cell freq.
    Returns: chisquare-statistic, associated p-value
    """

    k = len(f_obs)
    if f_exp == None:
        f_exp = _N.array([sum(f_obs)/float(k)] * len(f_obs),_N.float_)
    f_exp = f_exp.astype(_N.float_)
    chisq = _N.add.reduce((f_obs-f_exp)**2 / f_exp)
    return chisq, _achisqprob(chisq, k-1)


def _aks_2samp (data1,data2):
    """
    Computes the Kolmogorov-Smirnov statistic on 2 samples.  Modified from
    Numerical Recipes in C, page 493.  Returns KS D-value, prob.  Not ufunc-
    like.

    Usage:   _aks_2samp(data1,data2)  where data1 and data2 are 1D arrays
    Returns: KS D-value, p-value
    """
    j1 = 0    # _N.zeros(data1.shape[1:]) TRIED TO MAKE THIS UFUNC-LIKE
    j2 = 0    # _N.zeros(data2.shape[1:])
    fn1 = 0.0 # _N.zeros(data1.shape[1:],_N.float_)
    fn2 = 0.0 # _N.zeros(data2.shape[1:],_N.float_)
    n1 = data1.shape[0]
    n2 = data2.shape[0]
    en1 = n1*1
    en2 = n2*1
    d = _N.zeros(data1.shape[1:],_N.float_)
    data1 = _N.sort(data1,0)
    data2 = _N.sort(data2,0)
    while j1 < n1 and j2 < n2:
        d1=data1[j1]
        d2=data2[j2]
        if d1 <= d2:
            fn1 = (j1)/float(en1)
            j1 = j1 + 1
        if d2 <= d1:
            fn2 = (j2)/float(en2)
            j2 = j2 + 1
        dt = (fn2-fn1)
        if abs(dt) > abs(d):
            d = dt
    #    try:
    en = _math.sqrt(en1*en2/float(en1+en2))
    prob = _aksprob((en+0.12+0.11/en)*_N.fabs(d))
    #    except:
    #        prob = 1.0
    return d, prob


def _amannwhitneyu(x,y):
    """
    Calculates a Mann-Whitney U statistic on the provided scores and
    returns the result.  Use only when the n in each condition is < 20 and
    you have 2 independent samples of ranks.  REMEMBER: Mann-Whitney U is
    significant if the u-obtained is LESS THAN or equal to the critical
    value of U.

    Usage:   _amannwhitneyu(x,y)     where x,y are arrays of values for 2 conditions
    Returns: u-statistic, one-tailed p-value (i.e., p(z(U)))
    """
    n1 = len(x)
    n2 = len(y)
    ranked = rankdata(_N.concatenate((x,y)))
    rankx = ranked[0:n1]       # get the x-ranks
    ranky = ranked[n1:]        # the rest are y-ranks
    u1 = n1*n2 + (n1*(n1+1))/2.0 - sum(rankx)  # calc U for x
    u2 = n1*n2 - u1                            # remainder is U for y
    bigu = max(u1,u2)
    smallu = min(u1,u2)
    T = _math.sqrt(tiecorrect(ranked))  # correction factor for tied scores
    if T == 0:
        raise ValueError, 'All numbers are identical in _amannwhitneyu'
    sd = _math.sqrt(T*n1*n2*(n1+n2+1)/12.0)
    z = abs((bigu-n1*n2/2.0) / sd)  # normal approximation for prob calc
    return smallu, 1.0 - _azprob(z)


def _atiecorrect(rankvals):
    """
    Tie-corrector for ties in Mann Whitney U and Kruskal Wallis H tests.
    See Siegel, S. (1956) Nonparametric Statistics for the Behavioral
    Sciences.  New York: McGraw-Hill.  Code adapted from |Stat rankind.c
    code.

    Usage:   _atiecorrect(rankvals)
    Returns: T correction factor for U or H
    """
    sorted,posn = _ashellsort(_N.array(rankvals))
    n = len(sorted)
    T = 0.0
    i = 0
    while (i<n-1):
        if sorted[i] == sorted[i+1]:
            nties = 1
            while (i<n-1) and (sorted[i] == sorted[i+1]):
                nties = nties +1
                i = i +1
            T = T + nties**3 - nties
        i = i+1
    T = T / float(n**3-n)
    return 1.0 - T


def _aranksums(x,y):
    """
    Calculates the rank sums statistic on the provided scores and returns
    the result.

    Usage:   _aranksums(x,y)     where x,y are arrays of values for 2 conditions
    Returns: z-statistic, two-tailed p-value
    """
    n1 = len(x)
    n2 = len(y)
    alldata = _N.concatenate((x,y))
    ranked = _arankdata(alldata)
    x = ranked[:n1]
    y = ranked[n1:]
    s = sum(x)
    expected = n1*(n1+n2+1) / 2.0
    z = (s - expected) / _math.sqrt(n1*n2*(n1+n2+1)/12.0)
    prob = 2*(1.0 - _azprob(abs(z)))
    return z, prob


def _awilcoxont(x,y):
    """
    Calculates the Wilcoxon T-test for related samples and returns the
    result.  A non-parametric T-test.

    Usage:   _awilcoxont(x,y)     where x,y are equal-length arrays for 2 conditions
    Returns: t-statistic, two-tailed p-value
    """
    if len(x) <> len(y):
        raise ValueError, 'Unequal _N in _awilcoxont.  Aborting.'
    d = x-y
    d = _N.compress(_N.not_equal(d,0),d) # Keep all non-zero differences
    count = len(d)
    absd = abs(d)
    absranked = _arankdata(absd)
    r_plus = 0.0
    r_minus = 0.0
    for i in range(len(absd)):
        if d[i] < 0:
            r_minus = r_minus + absranked[i]
        else:
            r_plus = r_plus + absranked[i]
    wt = min(r_plus, r_minus)
    mn = count * (count+1) * 0.25
    se =  _math.sqrt(count*(count+1)*(2.0*count+1.0)/24.0)
    z = _math.fabs(wt-mn) / se
    z = _math.fabs(wt-mn) / se
    prob = 2*(1.0 -zprob(abs(z)))
    return wt, prob


def _akruskalwallish(*args):
    """
    The Kruskal-Wallis H-test is a non-parametric ANOVA for 3 or more
    groups, requiring at least 5 subjects in each group.  This function
    calculates the Kruskal-Wallis H and associated p-value for 3 or more
    independent samples.

    Usage:   _akruskalwallish(*args)     args are separate arrays for 3+ conditions
    Returns: H-statistic (corrected for ties), associated p-value
    """
    assert len(args) > 2, "Need at least 3 groups in stats._akruskalwallish()"
    args = list(args)
    n = [0]*len(args)
    n = map(len,args)
    all = []
    for i in range(len(args)):
        all = all + args[i].tolist()
    ranked = rankdata(all)
    T = tiecorrect(ranked)
    for i in range(len(args)):
        args[i] = ranked[0:n[i]]
        del ranked[0:n[i]]
    rsums = []
    for i in range(len(args)):
        rsums.append(sum(args[i])**2)
        rsums[i] = rsums[i] / float(n[i])
    ssbn = sum(rsums)
    totaln = sum(n)
    h = 12.0 / (totaln*(totaln+1)) * ssbn - 3*(totaln+1)
    df = len(args) - 1
    if T == 0:
        raise ValueError, 'All numbers are identical in _akruskalwallish'
    h = h / float(T)
    return h, chisqprob(h,df)


def _afriedmanchisquare(*args):
    """
    Friedman Chi-Square is a non-parametric, one-way within-subjects
    ANOVA.  This function calculates the Friedman Chi-square test for
    repeated measures and returns the result, along with the associated
    probability value.  It assumes 3 or more repeated measures.  Only 3
    levels requires a minimum of 10 subjects in the study.  Four levels
    requires 5 subjects per level(??).

    Usage:   _afriedmanchisquare(*args)   args are separate arrays for 2+ conditions
    Returns: chi-square statistic, associated p-value
    """
    k = len(args)
    if k < 3:
        raise ValueError, '\nLess than 3 levels.  Friedman test not appropriate.\n'
    n = len(args[0])
    data = apply(pstat.aabut,args)
    data = data.astype(_N.float_)
    for i in range(len(data)):
        data[i] = _arankdata(data[i])
    ssbn = _asum(_asum(args,1)**2)
    chisq = 12.0 / (k*n*(k+1)) * ssbn - 3*n*(k+1)
    return chisq, _achisqprob(chisq,k-1)

#####################################
####  APROBABILITY CALCULATIONS  ####
#####################################

def _achisqprob(chisq,df):
    """
    Returns the (1-tail) probability value associated with the provided chi-square
    value and df.  Heavily modified from chisq.c in Gary Perlman's |Stat.  Can
    handle multiple dimensions.

    Usage:   _achisqprob(chisq,df)    chisq=chisquare stat., df=degrees of freedom
    """
    BIG = 200.0
    def ex(x):
        BIG = 200.0
        exponents = _N.where(_N.less(x,-BIG),-BIG,x)
        return _N.exp(exponents)

    if type(chisq) == _N.ndarray:
        arrayflag = 1
    else:
        arrayflag = 0
        chisq = _N.array([chisq])
    if df < 1:
        return _N.ones(chisq.shape,_N.float)
    probs = _N.zeros(chisq.shape,_N.float_)
    probs = _N.where(_N.less_equal(chisq,0),1.0,probs)  # set prob=1 for chisq<0
    a = 0.5 * chisq
    if df > 1:
        y = ex(-a)
    if df%2 == 0:
        even = 1
        s = y*1
        s2 = s*1
    else:
        even = 0
        s = 2.0 * _azprob(-_N.sqrt(chisq))
        s2 = s*1
    if (df > 2):
        chisq = 0.5 * (df - 1.0)
        if even:
            z = _N.ones(probs.shape,_N.float_)
        else:
            z = 0.5 *_N.ones(probs.shape,_N.float_)
        if even:
            e = _N.zeros(probs.shape,_N.float_)
        else:
            e = _N.log(_N.sqrt(_N.pi)) *_N.ones(probs.shape,_N.float_)
        c = _N.log(a)
        mask = _N.zeros(probs.shape)
        a_big = _N.greater(a,BIG)
        a_big_frozen = -1 *_N.ones(probs.shape,_N.float_)
        totalelements = _N.multiply.reduce(_N.array(probs.shape))
        while _asum(mask)<>totalelements:
            e = _N.log(z) + e
            s = s + ex(c*z-a-e)
            z = z + 1.0
    #            print z, e, s
            newmask = _N.greater(z,chisq)
            a_big_frozen = _N.where(newmask*_N.equal(mask,0)*a_big, s, a_big_frozen)
            mask = _N.clip(newmask+mask,0,1)
        if even:
            z = _N.ones(probs.shape,_N.float_)
            e = _N.ones(probs.shape,_N.float_)
        else:
            z = 0.5 *_N.ones(probs.shape,_N.float_)
            e = 1.0 / _N.sqrt(_N.pi) / _N.sqrt(a) * _N.ones(probs.shape,_N.float_)
        c = 0.0
        mask = _N.zeros(probs.shape)
        a_notbig_frozen = -1 *_N.ones(probs.shape,_N.float_)
        while _asum(mask)<>totalelements:
            e = e * (a/z.astype(_N.float_))
            c = c + e
            z = z + 1.0
    #            print '#2', z, e, c, s, c*y+s2
            newmask = _N.greater(z,chisq)
            a_notbig_frozen = _N.where(newmask*_N.equal(mask,0)*(1-a_big),
                                      c*y+s2, a_notbig_frozen)
            mask = _N.clip(newmask+mask,0,1)
        probs = _N.where(_N.equal(probs,1),1,
                        _N.where(_N.greater(a,BIG),a_big_frozen,a_notbig_frozen))
        return probs
    else:
        return s


def _aerfcc(x):
    """
    Returns the complementary error function erfc(x) with fractional error
    everywhere less than 1.2e-7.  Adapted from Numerical Recipes.  Can
    handle multiple dimensions.

    Usage:   _aerfcc(x)
    """
    z = abs(x)
    t = 1.0 / (1.0+0.5*z)
    ans = t * _N.exp(-z*z-1.26551223 + t*(1.00002368+t*(0.37409196+t*(0.09678418+t*(-0.18628806+t*(0.27886807+t*(-1.13520398+t*(1.48851587+t*(-0.82215223+t*0.17087277)))))))))
    return _N.where(_N.greater_equal(x,0), ans, 2.0-ans)


def _azprob(z):
    """
    Returns the area under the normal curve 'to the left of' the given z value.
    Thus,
        - for z < 0, zprob(z) = 1-tail probability
        - for z > 0, 1.0-zprob(z) = 1-tail probability
        - for any z, 2.0*(1.0-zprob(abs(z))) = 2 - tail probability
    Adapted from z.c in Gary Perlman's |Stat.  Can handle multiple dimensions.

    Usage:   _azprob(z)    where z is a z-value
    """
    def yfunc(y):
        x = (((((((((((((-0.000045255659 * y
                         +0.000152529290) * y -0.000019538132) * y
                       -0.000676904986) * y +0.001390604284) * y
                     -0.000794620820) * y -0.002034254874) * y
                   +0.006549791214) * y -0.010557625006) * y
                 +0.011630447319) * y -0.009279453341) * y
               +0.005353579108) * y -0.002141268741) * y
             +0.000535310849) * y +0.999936657524
        return x

    def wfunc(w):
        x = ((((((((0.000124818987 * w
                    -0.001075204047) * w +0.005198775019) * w
                  -0.019198292004) * w +0.059054035642) * w
                -0.151968751364) * w +0.319152932694) * w
              -0.531923007300) * w +0.797884560593) * _N.sqrt(w) * 2.0
        return x

    Z_MAX = 6.0    # maximum meaningful z-value
    x = _N.zeros(z.shape,_N.float_) # initialize
    y = 0.5 * _N.fabs(z)
    x = _N.where(_N.less(y,1.0),wfunc(y*y),yfunc(y-2.0)) # get x's
    x = _N.where(_N.greater(y,Z_MAX*0.5),1.0,x)          # kill those with big Z
    prob = _N.where(_N.greater(z,0),(x+1)*0.5,(1-x)*0.5)
    return prob


def _aksprob(alam):
    """
   Returns the probability value for a K-S statistic computed via ks_2samp.
   Adapted from Numerical Recipes.  Can handle multiple dimensions.

   Usage:   _aksprob(alam)
   """
    if type(alam) == _N.ndarray:
        frozen = -1 *_N.ones(alam.shape,_N.float64)
        alam = alam.astype(_N.float64)
        arrayflag = 1
    else:
        frozen = _N.array(-1.)
        alam = _N.array(alam,_N.float64)
        arrayflag = 1
    mask = _N.zeros(alam.shape)
    fac = 2.0 *_N.ones(alam.shape,_N.float_)
    sum = _N.zeros(alam.shape,_N.float_)
    termbf = _N.zeros(alam.shape,_N.float_)
    a2 = _N.array(-2.0*alam*alam,_N.float64)
    totalelements = _N.multiply.reduce(_N.array(mask.shape))
    for j in range(1,201):
        if _asum(mask) == totalelements:
            break
        exponents = (a2*j*j)
        overflowmask = _N.less(exponents,-746)
        frozen = _N.where(overflowmask,0,frozen)
        mask = mask+overflowmask
        term = fac*_N.exp(exponents)
        sum = sum + term
        newmask = _N.where(_N.less_equal(abs(term),(0.001*termbf)) +
                          _N.less(abs(term),1.0e-8*sum), 1, 0)
        frozen = _N.where(newmask*_N.equal(mask,0), sum, frozen)
        mask = _N.clip(mask+newmask,0,1)
        fac = -fac
        termbf = abs(term)
    if arrayflag:
        return _N.where(_N.equal(frozen,-1), 1.0, frozen)  # 1.0 if doesn't converge
    else:
        return _N.where(_N.equal(frozen,-1), 1.0, frozen)[0]  # 1.0 if doesn't converge


def _afprob (dfnum, dfden, F):
    """
    Returns the 1-tailed significance level (p-value) of an F statistic
    given the degrees of freedom for the numerator (dfR-dfF) and the degrees
    of freedom for the denominator (dfF).  Can handle multiple dims for F.

    Usage:   _afprob(dfnum, dfden, F)   where usually dfnum=dfbn, dfden=dfwn
    """
    if type(F) == _N.ndarray:
        return _abetai(0.5*dfden, 0.5*dfnum, dfden/(1.0*dfden+dfnum*F))
    else:
        return _abetai(0.5*dfden, 0.5*dfnum, dfden/float(dfden+dfnum*F))


def _abetacf(a,b,x,verbose=1):
    """
    Evaluates the continued fraction form of the incomplete Beta function,
    betai.  (Adapted from: Numerical Recipes in C.)  Can handle multiple
    dimensions for x.

    Usage:   _abetacf(a,b,x,verbose=1)
    """
    ITMAX = 200
    EPS = 3.0e-7

    arrayflag = 1
    if type(x) == _N.ndarray:
        frozen = _N.ones(x.shape,_N.float_) *-1  #start out w/ -1s, should replace all
    else:
        arrayflag = 0
        frozen = _N.array([-1])
        x = _N.array([x])
    mask = _N.zeros(x.shape)
    bm = _az = am = 1.0
    qab = a+b
    qap = a+1.0
    qam = a-1.0
    bz = 1.0-qab*x/qap
    for i in range(ITMAX+1):
        if _N.sum(_N.ravel(_N.equal(frozen,-1)))==0:
            break
        em = float(i+1)
        tem = em + em
        d = em*(b-em)*x/((qam+tem)*(a+tem))
        ap = _az + d*am
        bp = bz+d*bm
        d = -(a+em)*(qab+em)*x/((qap+tem)*(a+tem))
        app = ap+d*_az
        bpp = bp+d*bz
        aold = _az*1
        am = ap/bpp
        bm = bp/bpp
        _az = app/bpp
        bz = 1.0
        newmask = _N.less(abs(_az-aold),EPS*abs(_az))
        frozen = _N.where(newmask*_N.equal(mask,0), _az, frozen)
        mask = _N.clip(mask+newmask,0,1)
    noconverge = _asum(_N.equal(frozen,-1))
    if noconverge <> 0 and verbose:
        print 'a or b too big, or ITMAX too small in Betacf for ',noconverge,' elements'
    if arrayflag:
        return frozen
    else:
        return frozen[0]


def _agammln(xx):
    """
    Returns the gamma function of xx.
    Gamma(z) = Integral(0,infinity) of t^(z-1)exp(-t) dt.

    Adapted from: Numerical Recipes in C.  Can handle multiple dims ... but
    probably doesn't normally have to.

    Usage:   _agammln(xx)
    """
    coeff = [76.18009173, -86.50532033, 24.01409822, -1.231739516,
             0.120858003e-2, -0.536382e-5]
    x = xx - 1.0
    tmp = x + 5.5
    tmp = tmp - (x+0.5)*_N.log(tmp)
    ser = 1.0
    for j in range(len(coeff)):
        x = x + 1
        ser = ser + coeff[j]/x
    return -tmp + _N.log(2.50662827465*ser)


def _abetai(a,b,x,verbose=1):
    """
    Returns the incomplete beta function:

    I-sub-x(a,b) = 1/B(a,b)*(Integral(0,x) of t^(a-1)(1-t)^(b-1) dt)

    where a,b>0 and B(a,b) = G(a)*G(b)/(G(a+b)) where G(a) is the gamma
    function of a.  The continued fraction formulation is implemented
    here, using the betacf function.  (Adapted from: Numerical Recipes in
    C.)  Can handle multiple dimensions.

    Usage:   _abetai(a,b,x,verbose=1)
    """
    TINY = 1e-15
    if type(a) == _N.ndarray:
        if _asum(_N.less(x,0)+_N.greater(x,1)) <> 0:
            raise ValueError, 'Bad x in _abetai'
    x = _N.where(_N.equal(x,0),TINY,x)
    x = _N.where(_N.equal(x,1.0),1-TINY,x)

    bt = _N.where(_N.equal(x,0)+_N.equal(x,1), 0, -1)
    exponents = ( gammln(a+b)-gammln(a)-gammln(b)+a*_N.log(x)+b*
                  _N.log(1.0-x) )
    # 746 (below) is the MAX POSSIBLE BEFORE OVERFLOW
    exponents = _N.where(_N.less(exponents,-740),-740,exponents)
    bt = _N.exp(exponents)
    if type(x) == _N.ndarray:
        ans = _N.where(_N.less(x,(a+1)/(a+b+2.0)),
                      bt*_abetacf(a,b,x,verbose)/float(a),
                      1.0-bt*_abetacf(b,a,1.0-x,verbose)/float(b))
    else:
        if x<(a+1)/(a+b+2.0):
            ans = bt*_abetacf(a,b,x,verbose)/float(a)
        else:
            ans = 1.0-bt*_abetacf(b,a,1.0-x,verbose)/float(b)
    return ans

#####################################
#######  AANOVA CALCULATIONS  #######
#####################################

def aglm(data,para):
    """
    Calculates a linear model fit ... anova/ancova/lin-regress/t-test/etc. Taken
    from:

    Peterson et al. Statistical limitations in functional neuroimaging
    I. Non-inferential methods and statistical models.  Phil Trans Royal Soc
    Lond B 354: 1239-1260.

    Usage:   aglm(data,para)
    Returns: statistic, p-value ???
    """
    if len(para) <> len(data):
        print "data and para must be same length in aglm"
        return
    n = len(para)
    p = pstat.aunique(para)
    x = _N.zeros((n,len(p)))  # design matrix
    for l in range(len(p)):
        x[:,l] = _N.equal(para,p[l])
    b = _N.dot(_N.dot(_LA.inv(_N.dot(_N.transpose(x),x)),  # i.e., b=inv(X'X)X'Y
                    _N.transpose(x)),
              data)
    diffs = (data - _N.dot(x,b))
    s_sq = 1./(n-len(p)) * _N.dot(_N.transpose(diffs), diffs)

    if len(p) == 2:  # ttest_ind
        c = _N.array([1,-1])
        df = n-2
        fact = _asum(1.0/_asum(x,0))  # i.e., 1/n1 + 1/n2 + 1/n3 ...
        t = _N.dot(c,b) / _N.sqrt(s_sq*fact)
        probs = _abetai(0.5*df,0.5,float(df)/(df+t*t))
        return t, probs


def _aF_oneway(*args):
    """
    Performs a 1-way ANOVA, returning an F-value and probability given
    any number of groups.  From Heiman, pp.394-7.

    Usage:   _aF_oneway (*args)    where *args is 2 or more arrays, one per treatment group
    Returns: f-value, probability
    """
    na = len(args)            # ANOVA on 'na' groups, each in it's own array
    means = [0]*na
    vars = [0]*na
    ns = [0]*na
    alldata = []
    tmp = map(_N.array,args)
    means = map(_amean,tmp)
    vars = map(_avar,tmp)
    ns = map(len,args)
    alldata = _N.concatenate(args)
    bign = len(alldata)
    sstot = _ass(alldata)-(_asquare_of_sums(alldata)/float(bign))
    ssbn = 0
    for a in args:
        ssbn = ssbn + _asquare_of_sums(_N.array(a))/float(len(a))
    ssbn = ssbn - (_asquare_of_sums(alldata)/float(bign))
    sswn = sstot-ssbn
    dfbn = na-1
    dfwn = bign - na
    msb = ssbn/float(dfbn)
    msw = sswn/float(dfwn)
    f = msb/msw
    prob = fprob(dfbn,dfwn,f)
    return f, prob


def _aF_value (ER,EF,dfR,dfF):
    """
    Returns an F-statistic given the following:
    ER  = error associated with the null hypothesis (the Restricted model)
    EF  = error associated with the alternate hypothesis (the Full model)
    dfR = degrees of freedom the Restricted model
    dfF = degrees of freedom associated with the Restricted model
    """
    return ((ER-EF)/float(dfR-dfF) / (EF/float(dfF)))

def outputfstats(Enum, Eden, dfnum, dfden, f, prob):
    Enum = round(Enum,3)
    Eden = round(Eden,3)
    dfnum = round(Enum,3)
    dfden = round(dfden,3)
    f = round(f,3)
    prob = round(prob,3)
    suffix = ''                       # for *s after the p-value
    if  prob < 0.001:  suffix = '  ***'
    elif prob < 0.01:  suffix = '  **'
    elif prob < 0.05:  suffix = '  *'
    title = [['EF/ER','DF','Mean Square','F-value','prob','']]
    lofl = title+[[Enum, dfnum, round(Enum/float(dfnum),3), f, prob, suffix],
                  [Eden, dfden, round(Eden/float(dfden),3),'','','']]
    pstat.printcc(lofl)
    return


def F_value_multivariate(ER, EF, dfnum, dfden):
    """
    Returns an F-statistic given the following:
    ER  = error associated with the null hypothesis (the Restricted model)
    EF  = error associated with the alternate hypothesis (the Full model)
    dfR = degrees of freedom the Restricted model
    dfF = degrees of freedom associated with the Restricted model
    where ER and EF are matrices from a multivariate F calculation.
    """
    if type(ER) in [_IntType, _FloatType]:
        ER = _N.array([[ER]])
    if type(EF) in [_IntType, _FloatType]:
        EF = _N.array([[EF]])
    n_um = (_LA.det(ER) - _LA.det(EF)) / float(dfnum)
    d_en = _LA.det(EF) / float(dfden)
    return n_um / d_en

#####################################
#######  ASUPPORT FUNCTIONS  ########
#####################################

def asign(a):
    """
    Usage:   asign(a)
    Returns: array shape of a, with -1 where a<0 and +1 where a>=0
    """
    a = _N.asarray(a)
    if ((type(a) == type(1.4)) or (type(a) == type(1))):
        return a-a-_N.less(a,0)+_N.greater(a,0)
    else:
        return _N.zeros(_N.shape(a))-_N.less(a,0)+_N.greater(a,0)


def _asum (a, dimension=None,keepdims=0):
    """
   An alternative to the Numeric.add.reduce function, which allows one to
   (1) collapse over multiple dimensions at once, and/or (2) to retain
   all dimensions in the original array (squashing one down to size.
   Dimension can equal None (ravel array first), an integer (the
   dimension over which to operate), or a sequence (operate over multiple
   dimensions).  If keepdims=1, the resulting array will have as many
   dimensions as the input array.

   Usage:   _asum(a, dimension=None, keepdims=0)
   Returns: array summed along 'dimension'(s), same _number_ of dims if keepdims=1
   """
    if type(a) == _N.ndarray and a.dtype in [_N.int_, _N.short, _N.ubyte]:
        a = a.astype(_N.float_)
    if dimension == None:
        s = _N.sum(_N.ravel(a))
    elif type(dimension) in [_IntType,_FloatType]:
        s = _N.add.reduce(a, dimension)
        if keepdims == 1:
            shp = list(a.shape)
            shp[dimension] = 1
            s = _N.reshape(s,shp)
    else: # must be a SEQUENCE of dims to sum over
        dims = list(dimension)
        dims.sort()
        dims.reverse()
        s = a *1.0
        for dim in dims:
            s = _N.add.reduce(s,dim)
        if keepdims == 1:
            shp = list(a.shape)
            for dim in dims:
                shp[dim] = 1
            s = _N.reshape(s,shp)
    return s


def _acumsum (a,dimension=None):
    """
    Returns an array consisting of the cumulative sum of the items in the
    passed array.  Dimension can equal None (ravel array first), an
    integer (the dimension over which to operate), or a sequence (operate
    over multiple dimensions, but this last one just barely makes sense).

    Usage:   _acumsum(a,dimension=None)
    """
    if dimension == None:
        a = _N.ravel(a)
        dimension = 0
    if type(dimension) in [_ListType, _TupleType, _N.ndarray]:
        dimension = list(dimension)
        dimension.sort()
        dimension.reverse()
        for d in dimension:
            a = _N.add.accumulate(a,d)
        return a
    else:
        return _N.add.accumulate(a,dimension)


def _ass(inarray, dimension=None, keepdims=0):
    """
    Squares each value in the passed array, adds these squares & returns
    the result.  Unfortunate function name. :-) Defaults to ALL values in
    the array.  Dimension can equal None (ravel array first), an integer
    (the dimension over which to operate), or a sequence (operate over
    multiple dimensions).  Set keepdims=1 to maintain the original number
    of dimensions.

    Usage:   _ass(inarray, dimension=None, keepdims=0)
    Returns: sum-along-'dimension' for (inarray*inarray)
    """
    if dimension == None:
        inarray = _N.ravel(inarray)
        dimension = 0
    return _asum(inarray*inarray,dimension,keepdims)


def _asummult (array1,array2,dimension=None,keepdims=0):
    """
    Multiplies elements in array1 and array2, element by element, and
    returns the sum (along 'dimension') of all resulting multiplications.
    Dimension can equal None (ravel array first), an integer (the
    dimension over which to operate), or a sequence (operate over multiple
    dimensions).  A trivial function, but included for completeness.

    Usage:   _asummult(array1,array2,dimension=None,keepdims=0)
    """
    if dimension == None:
        array1 = _N.ravel(array1)
        array2 = _N.ravel(array2)
        dimension = 0
    return _asum(array1*array2,dimension,keepdims)


def _asquare_of_sums(inarray, dimension=None, keepdims=0):
    """
    Adds the values in the passed array, squares that sum, and returns the
    result.  Dimension can equal None (ravel array first), an integer (the
    dimension over which to operate), or a sequence (operate over multiple
    dimensions).  If keepdims=1, the returned array will have the same
    NUMBER of dimensions as the original.

    Usage:   _asquare_of_sums(inarray, dimension=None, keepdims=0)
    Returns: the square of the sum over dim(s) in dimension
    """
    if dimension == None:
        inarray = _N.ravel(inarray)
        dimension = 0
    s = _asum(inarray,dimension,keepdims)
    if type(s) == _N.ndarray:
        return s.astype(_N.float_)*s
    else:
        return float(s)*s


def _asumdiffsquared(a,b, dimension=None, keepdims=0):
    """
    Takes pairwise differences of the values in arrays a and b, squares
    these differences, and returns the sum of these squares.  Dimension
    can equal None (ravel array first), an integer (the dimension over
    which to operate), or a sequence (operate over multiple dimensions).
    keepdims=1 means the return shape = len(a.shape) = len(b.shape)

    Usage:   _asumdiffsquared(a,b)
    Returns: sum[ravel(a-b)**2]
    """
    if dimension == None:
        inarray = _N.ravel(a)
        dimension = 0
    return _asum((a-b)**2,dimension,keepdims)


def _ashellsort(inarray):
    """
    Shellsort algorithm.  Sorts a 1D-array.

    Usage:   _ashellsort(inarray)
    Returns: sorted-inarray, sorting-index-vector (for original array)
    """
    n = len(inarray)
    svec = inarray *1.0
    ivec = range(n)
    gap = n/2   # integer division needed
    while gap >0:
        for i in range(gap,n):
            for j in range(i-gap,-1,-gap):
                while j>=0 and svec[j]>svec[j+gap]:
                    temp        = svec[j]
                    svec[j]     = svec[j+gap]
                    svec[j+gap] = temp
                    itemp       = ivec[j]
                    ivec[j]     = ivec[j+gap]
                    ivec[j+gap] = itemp
        gap = gap / 2  # integer division needed
    # svec is now sorted input vector, ivec has the order svec[i] = vec[ivec[i]]
    return svec, ivec


def _arankdata(inarray):
    """
    Ranks the data in inarray, dealing with ties appropriately.  Assumes
    a 1D inarray.  Adapted from Gary Perlman's |Stat ranksort.

    Usage:   _arankdata(inarray)
    Returns: array of length equal to inarray, containing rank scores
    """
    n = len(inarray)
    svec, ivec = _ashellsort(inarray)
    sumranks = 0
    dupcount = 0
    newarray = _N.zeros(n,_N.float_)
    for i in range(n):
        sumranks = sumranks + i
        dupcount = dupcount + 1
        if i==n-1 or svec[i] <> svec[i+1]:
            averank = sumranks / float(dupcount) + 1
            for j in range(i-dupcount+1,i+1):
                newarray[ivec[j]] = averank
            sumranks = 0
            dupcount = 0
    return newarray


def _afindwithin(data):
    """
    Returns a binary vector, 1=within-subject factor, 0=between.  Input
    equals the entire data array (i.e., column 1=random factor, last
    column = measured values.

    Usage:   _afindwithin(data)     data in |Stat format
    """
    numfact = len(data[0])-2
    withinvec = [0]*numfact
    for col in range(1,numfact+1):
        rows = pstat.linexand(data,col,pstat.unique(pstat.colex(data,1))[0])  # get 1 level of this factor
        if len(pstat.unique(pstat.colex(rows,0))) < len(rows):   # if fewer subjects than scores on this factor
            withinvec[col-1] = 1
    return withinvec


try:
    # DEFINE THESE *ONLY* IF NUMPY IS AVAILABLE
    import numpy as _N
    import numpy.linalg as _LA
    import operator
    #########################################################
    #########################################################
    ######  RE-DEFINE DISPATCHES TO INCLUDE ARRAYS  #########
    #########################################################
    #########################################################

    ## CENTRAL TENDENCY:
    geometricmean = _Dispatch ( (_lgeometricmean, (_ListType, _TupleType)),
                               (_ageometricmean, (_N.ndarray,)) )
    harmonicmean = _Dispatch ( (_lharmonicmean, (_ListType, _TupleType)),
                              (_aharmonicmean, (_N.ndarray,)) )
    mean = _Dispatch ( (_lmean, (_ListType, _TupleType)),
                      (_amean, (_N.ndarray,)) )
    median = _Dispatch ( (_lmedianscore, (_ListType, _TupleType)),  # changing the median to medianscore _lmedian, _amedian
                        (_amedianscore, (_N.ndarray,)) )
    firstquartilescore = _Dispatch ( (_lfirstquartilescore, (_ListType, _TupleType)),
                                    (_afirstquartilescore, (_N.ndarray,)) )
    thirdquartilescore = _Dispatch ( (_lthirdquartilescore, (_ListType, _TupleType)),
                                    (_athirdquartilescore, (_N.ndarray,)) )
    medianscore = _Dispatch ( (_lmedianscore, (_ListType, _TupleType)),
                             (_amedianscore, (_N.ndarray,)) )
    mode = _Dispatch ( (_lmode, (_ListType, _TupleType)),
                      (_amode, (_N.ndarray,)) )
    tmean = _Dispatch ( (_atmean, (_N.ndarray,)) )
    tvar = _Dispatch ( (_atvar, (_N.ndarray,)) )
    tstdev = _Dispatch ( (_atstdev, (_N.ndarray,)) )
    tsem = _Dispatch ( (_atsem, (_N.ndarray,)) )

    ## VARIATION:
    moment = _Dispatch ( (_lmoment, (_ListType, _TupleType)),
                        (_amoment, (_N.ndarray,)) )
    variation = _Dispatch ( (__lvariation, (_ListType, _TupleType)),
                           (__avariation, (_N.ndarray,)) )
    skew = _Dispatch ( (_lskew, (_ListType, _TupleType)),
                      (_askew, (_N.ndarray,)) )
    kurtosis = _Dispatch ( (_lkurtosis, (_ListType, _TupleType)),
                          (_akurtosis, (_N.ndarray,)) )
    describe = _Dispatch ( (_ldescribe, (_ListType, _TupleType)),
                          (_adescribe, (_N.ndarray,)) )

    ## DISTRIBUTION TESTS

    skewtest = _Dispatch ( (_askewtest, (_ListType, _TupleType)),
                          (_askewtest, (_N.ndarray,)) )
    kurtosistest = _Dispatch ( (_akurtosistest, (_ListType, _TupleType)),
                              (_akurtosistest, (_N.ndarray,)) )
    normaltest = _Dispatch ( (_anormaltest, (_ListType, _TupleType)),
                            (_anormaltest, (_N.ndarray,)) )

    ## FREQUENCY STATS:
    itemfreq = _Dispatch ( (_litemfreq, (_ListType, _TupleType)),
                          (_aitemfreq, (_N.ndarray,)) )
    scoreatpercentile = _Dispatch ( (_lscoreatpercentile, (_ListType, _TupleType)),
                                   (_ascoreatpercentile, (_N.ndarray,)) )
    percentileofscore = _Dispatch ( (_lpercentileofscore, (_ListType, _TupleType)),
                                    (_apercentileofscore, (_N.ndarray,)) )
    histogram = _Dispatch ( (_lhistogram, (_ListType, _TupleType)),
                           (_ahistogram, (_N.ndarray,)) )
    cumfreq = _Dispatch ( (_lcumfreq, (_ListType, _TupleType)),
                         (_acumfreq, (_N.ndarray,)) )
    relfreq = _Dispatch ( (_lrelfreq, (_ListType, _TupleType)),
                         (_arelfreq, (_N.ndarray,)) )

    ## VARIABILITY:
    obrientransform = _Dispatch ( (_lobrientransform, (_ListType, _TupleType)),
                                 (_aobrientransform, (_N.ndarray,)) )
    samplevar = _Dispatch ( (_lsamplevar, (_ListType, _TupleType)),
                           (_asamplevar, (_N.ndarray,)) )
    samplestdev = _Dispatch ( (_lsamplestdev, (_ListType, _TupleType)),
                             (_asamplestdev, (_N.ndarray,)) )
    signaltonoise = _Dispatch( (_asignaltonoise, (_N.ndarray,)),)
    var = _Dispatch ( (_lvar, (_ListType, _TupleType)),
                     (_avar, (_N.ndarray,)) )
    stdev = _Dispatch ( (_lstdev, (_ListType, _TupleType)),
                       (_astdev, (_N.ndarray,)) )
    sterr = _Dispatch ( (_lsterr, (_ListType, _TupleType)),
                       (_asterr, (_N.ndarray,)) )
    sem = _Dispatch ( (_lsem, (_ListType, _TupleType)),
                     (_asem, (_N.ndarray,)) )
    z = _Dispatch ( (_lz, (_ListType, _TupleType)),
                   (_az, (_N.ndarray,)) )
    zs = _Dispatch ( (_lzs, (_ListType, _TupleType)),
                    (_azs, (_N.ndarray,)) )
    zmap= _Dispatch( (_azmap, (_N.ndarray,)) )

    ## TRIMMING FCNS:
    threshold = _Dispatch( (_athreshold, (_N.ndarray,)),)
    trimboth = _Dispatch ( (_ltrimboth, (_ListType, _TupleType)),
                          (_atrimboth, (_N.ndarray,)) )
    trim1 = _Dispatch ( (_ltrim1, (_ListType, _TupleType)),
                       (_atrim1, (_N.ndarray,)) )

    ## CORRELATION FCNS:
    covariance = _Dispatch((_lcov, (_ListType, _TupleType)),
                          (_acov, (_N.ndarray,)) )
    paired = _Dispatch ( (_lpaired, (_ListType, _TupleType)),
                        (_apaired, (_N.ndarray,)) )
    lincc = _Dispatch ( (_llincc, (_ListType, _TupleType)),
                          (_alincc, (_N.ndarray,)) )
    pearsonr = _Dispatch ( (_lpearsonr, (_ListType, _TupleType)),
                          (_apearsonr, (_N.ndarray,)) )
    spearmanr = _Dispatch ( (_lspearmanr, (_ListType, _TupleType)),
                           (_aspearmanr, (_N.ndarray,)) )
    pointbiserialr = _Dispatch ( (_lpointbiserialr, (_ListType, _TupleType)),
                                (_apointbiserialr, (_N.ndarray,)) )
    kendalltau = _Dispatch ( (_lkendalltau, (_ListType, _TupleType)),
                            (_akendalltau, (_N.ndarray,)) )
    linregress = _Dispatch ( (_llinregress, (_ListType, _TupleType)),
                            (_alinregress, (_N.ndarray,)) )

    ## INFERENTIAL STATS:
    ttest_1samp = _Dispatch ( (_lttest_1samp, (_ListType, _TupleType)),
                             (_attest_1samp, (_N.ndarray,)) )
    ttest_ind = _Dispatch ( (_lttest_ind, (_ListType, _TupleType)),
                           (_attest_ind, (_N.ndarray,)) )
    ttest_rel = _Dispatch ( (_lttest_rel, (_ListType, _TupleType)),
                           (_attest_rel, (_N.ndarray,)) )
    chisquare = _Dispatch ( (_lchisquare, (_ListType, _TupleType)),
                           (_achisquare, (_N.ndarray,)) )
    ks_2samp = _Dispatch ( (_lks_2samp, (_ListType, _TupleType)),
                          (_aks_2samp, (_N.ndarray,)) )
    mannwhitneyu = _Dispatch ( (_lmannwhitneyu, (_ListType, _TupleType)),
                              (_amannwhitneyu, (_N.ndarray,)) )
    tiecorrect = _Dispatch ( (_ltiecorrect, (_ListType, _TupleType)),
                            (_atiecorrect, (_N.ndarray,)) )
    ranksums = _Dispatch ( (_lranksums, (_ListType, _TupleType)),
                          (_aranksums, (_N.ndarray,)) )
    wilcoxont = _Dispatch ( (_lwilcoxont, (_ListType, _TupleType)),
                           (_awilcoxont, (_N.ndarray,)) )
    kruskalwallish = _Dispatch ( (_lkruskalwallish, (_ListType, _TupleType)),
                                (_akruskalwallish, (_N.ndarray,)) )
    friedmanchisquare = _Dispatch ( (_lfriedmanchisquare, (_ListType, _TupleType)),
                                   (_afriedmanchisquare, (_N.ndarray,)) )

    ## PROBABILITY CALCS:
    chisqprob = _Dispatch ( (_lchisqprob, (_IntType, _FloatType)),
                           (_achisqprob, (_N.ndarray,)) )
    zprob = _Dispatch ( (_lzprob, (_IntType, _FloatType)),
                       (_azprob, (_N.ndarray,)) )
    ksprob = _Dispatch ( (_lksprob, (_IntType, _FloatType)),
                        (_aksprob, (_N.ndarray,)) )
    fprob = _Dispatch ( (_lfprob, (_IntType, _FloatType)),
                       (_afprob, (_N.ndarray,)) )
    betacf = _Dispatch ( (_lbetacf, (_IntType, _FloatType)),
                        (_abetacf, (_N.ndarray,)) )
    betai = _Dispatch ( (_lbetai, (_IntType, _FloatType)),
                       (_abetai, (_N.ndarray,)) )
    erfcc = _Dispatch ( (_lerfcc, (_IntType, _FloatType)),
                       (_aerfcc, (_N.ndarray,)) )
    gammln = _Dispatch ( (_lgammln, (_IntType, _FloatType)),
                        (_agammln, (_N.ndarray,)) )

    ## ANOVA FUNCTIONS:
    F_oneway = _Dispatch ( (_lF_oneway, (_ListType, _TupleType)),
                          (_aF_oneway, (_N.ndarray,)) )
    F_value = _Dispatch ( (_lF_value, (_ListType, _TupleType)),
                         (_aF_value, (_N.ndarray,)) )

    ## SUPPORT FUNCTIONS:
    _incr = _Dispatch ( (_lincr, (_ListType, _TupleType, _N.ndarray)), )
    sum = _Dispatch ( (_lsum, (_ListType, _TupleType)),
                     (_asum, (_N.ndarray,)) )
    cumsum = _Dispatch ( (_lcumsum, (_ListType, _TupleType)),
                        (_acumsum, (_N.ndarray,)) )
    ss = _Dispatch ( (_lss, (_ListType, _TupleType)),
                    (_ass, (_N.ndarray,)) )
    summult = _Dispatch ( (_lsummult, (_ListType, _TupleType)),
                         (_asummult, (_N.ndarray,)) )
    square_of_sums = _Dispatch ( (_lsquare_of_sums, (_ListType, _TupleType)),
                                (_asquare_of_sums, (_N.ndarray,)) )
    sumdiffsquared = _Dispatch ( (_lsumdiffsquared, (_ListType, _TupleType)),
                                (_asumdiffsquared, (_N.ndarray,)) )
    shellsort = _Dispatch ( (_lshellsort, (_ListType, _TupleType)),
                           (_ashellsort, (_N.ndarray,)) )
    rankdata = _Dispatch ( (_lrankdata, (_ListType, _TupleType)),
                          (_arankdata, (_N.ndarray,)) )
    findwithin = _Dispatch ( (_lfindwithin, (_ListType, _TupleType)),
                            (_afindwithin, (_N.ndarray,)) )

######################  END OF NUMERIC FUNCTION BLOCK  #####################

######################  END OF STATISTICAL FUNCTIONS  ######################

except ImportError, exc:
    #print exc
    pass
