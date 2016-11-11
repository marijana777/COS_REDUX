""" Trace the source in Data file
"""
from __future__ import (print_function, absolute_import, division, unicode_literals)

import numpy as np
from astropy.table import Table

from xastropy.xutils import xdebug as xdb


def crude_histogram(yfull, ymin=300, ymax=700, ytl=550, pk_window=4.5, verbose=False):
    """ Derive a trace given an input COS image

    Parameters
    ----------
    yfull : ndarray
      y pixel values of the counts
        (typically taken from YFULL column of data file)
    ymin : int, optional
      Minimum search window for the trace
    ymax : int, optional
      Minimum search window for the trace
    ytl : int, optinal
      Estimated y-position to separate arc from object

    Returns
    -------
    obj_y : float
      Estimated y position of the object
    arc_y : float
      Estimated y position of the arc

    """
    # ytr=y trace of sp; precision 0.1; ytrl=trace of lamp
    # array with densities: yd; nd=N_el of yd
    # assume (for now): 300-520

    ymin=300 #min(ya) #300
    ymax=700 #550 #max(ya) #550
    nh=ymax-ymin    # bins of width = 1

    # Generate histogram
    ycen=np.arange(nh)+ymin+0.5
    yedges=np.arange(nh+1)+ymin
    yhist, edges = np.histogram(yfull, bins=yedges)

    # Find Object
    iobj = np.where(ycen < ytl)[0]
    ihist_pk = np.argmax(yhist[iobj])
    obj_y_guess = ycen[iobj[ihist_pk]]


    # Find arc
    iarc = np.where(ycen > ytl)[0]
    ihist_pk = np.argmax(yhist[iarc])
    arc_y_guess = ycen[iarc[ihist_pk]]
    if verbose:
        print("Crude: Obj={:g}, Arc={:g}".format(obj_y_guess,arc_y_guess))

    # Refine
    obj_y = refine_peak(yfull, obj_y_guess)
    arc_y = refine_peak(yfull, arc_y_guess)
    if verbose:
        print("Refined: Obj={:g}, Arc={:g}".format(obj_y,arc_y))

    # Return
    return obj_y, arc_y


def refine_peak(yfull, y_guess, pk_window=5., per_lim=(0.25,0.75)):
    """
    Parameters
    ----------
    yfull
    y_guess
    per_lim : tuple

    Returns
    -------

    """
    # Cut to y values near the peak
    cut = np.abs(yfull-y_guess) < pk_window
    ycut = yfull[cut]

    # Sort
    ycut.sort()

    # Cumulative sum
    ysum = np.cumsum(ycut)

    left = np.argmin(np.abs(per_lim[0]-ysum/ysum[-1]))
    right = np.argmin(np.abs(per_lim[1]-ysum/ysum[-1]))

    # Average
    pk = (ycut[left]+ycut[right])/2.

    # Return
    return pk



def show_traces(wave, yfull, obj_y, arc_y):
    """
    Parameters
    ----------
    xfull
    yfull
    obj_y
    arc_y

    Returns
    -------

    """
    from matplotlib import pyplot as plt

    plt.clf()   # clears a plot
    ax = plt.gca()   # set axis
    ax.scatter(wave,yfull,s=1)
    wvmin = np.maximum(np.min(wave), 1100)
    wvmax = np.max(wave)
    ax.plot([wvmin, wvmax],[obj_y,obj_y], color='blue')
    ax.plot([wvmin,wvmax],[arc_y,arc_y], color='red')
    ax.set_xlabel('Wavelength')
    ax.set_ylabel('YFULL')
    ax.set_xlim(wvmin, wvmax)
    # Y range
    gdp = (wave > wvmin) & (wave < wvmax)
    ymin = np.min(yfull[gdp])
    ymax = np.max(yfull[gdp])
    ax.set_ylim(ymin, ymax)
    plt.show()


