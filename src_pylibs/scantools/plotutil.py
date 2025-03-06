import pandas as pd
from scantools.statutil import regression
import matplotlib.pyplot as plt
import numpy as np
import config
from scipy.stats import pearsonr

fig_adjust_factor = 2/(1+np.sqrt(5))
colors = config.GruvBoxColors


def add_panels(axes):
    # run over axes and add panels lik (a) (b) end soforth
    for a, p in zip(axes.ravel(), config.Panels):
        a.set_title(p)
    return


def add_labs(axes, xlabs, ylabs):
    """TODO: Docstring for add_labs.
    Returns
    -------
    TODO

    """

    for a, x, y in zip(axes.ravel(), xlabs, ylabs):
        a.set_xlabel(x)
        a.set_ylabel(y)
    return


def get_figsize(nrow, ncol):
    if nrow == 1 and ncol == 1:
        w = config.figwidth*fig_adjust_factor
        h = w
    elif nrow == 2 and nrow == ncol:
        w = config.figwidth
        h = w*fig_adjust_factor
    elif nrow == 1 and ncol >= 2:
        w = config.figwidth
        h = w*fig_adjust_factor
    elif nrow >= 2 and ncol == 1:
        h = config.figwidth
        w = h*fig_adjust_factor
    elif nrow >= 2 and ncol >= 2:
        w = config.figwidth
        h = w*1.2#/fig_adjust_factor
    return h, w


def set_xlims(axes, xlims):
    for a, x in zip(axes.ravel(), xlims):
        if isinstance(x, tuple):
            a.set_xlim(*x)
    return


def set_ylims(axes, ylims):
    for a, y in zip(axes.ravel(), ylims):
        if isinstance(y, tuple):
            a.set_ylim(*y)
    return


def relax_factors(xl, xh):
    if (xl >= 0) & (xh >= 0):
        cl = 0.7
        ch = 1.3
    elif (xl < 0) & (xh < 0):
        cl = 1.3
        ch = 0.7
    elif (xl < 0) & (xh >= 0) | (xl >= 0) & (xh < 0):
        cl = 1.3
        ch = 1.3
    return cl, ch

def plot_add(axes, x, y, argsort=True,scatter=False, *args, **kwargs):
    if not isinstance(x,np.ndarray):
        x=np.array(x)
    if not isinstance(y,np.ndarray):
        y=np.array(y)
    if argsort==True:
        p=x.argsort()
        x=x[p]
        y=y[p]
    mask_finites=(np.isfinite(x))&(np.isfinite(y))
    x=x[mask_finites]
    y=y[mask_finites]
    xl, xh = axes.get_xlim()
    yl, yh = axes.get_ylim()
    cl, ch = relax_factors(xl, xh)
    if xl < xh: 
        xmask = (x > cl*xl) & (x < ch*xh) 
    else: 
        xmask = (x < ch*xl) & (x > cl*xh)

    cl, ch = relax_factors(yl, yh)
    if yl < yh:
        ymask = (y > cl*yl) & (y < ch*yh)
    else:
        ymask = (y < ch*yl) & (y > cl*yh)
    mask = xmask & ymask
    if scatter==True:
        if argsort==True:
            kwargs["c"]=kwargs["c"][p][mask]
        else:
            kwargs["c"]=kwargs["c"][mask]
        cm=axes.scatter(x[mask], y[mask], *args, **kwargs)
        return cm
    else:
        if 'yerr' in kwargs or 'xerr' in kwargs: 
            if argsort==True:
                if "yerr" in kwargs:
                    if isinstance(kwargs['yerr'],np.ndarray):
                        kwargs["yerr"]=kwargs["yerr"][p][mask]
                if "xerr" in kwargs:
                    if isinstance(kwargs['xerr'],np.ndarray):
                        kwargs["xerr"]=kwargs["xerr"][p][mask]
            else:
                if "yerr" in kwargs:
                    if isinstance(kwargs['yerr'],np.ndarray):
                        kwargs["yerr"]=kwargs["yerr"][mask]
                if "xerr" in kwargs:
                    if isinstance(kwargs['xerr'],np.ndarray):
                        kwargs["xerr"]=kwargs["xerr"][mask]
            axes.errorbar(x[mask], y[mask], *args, **kwargs)
        else:
            axes.plot(x[mask], y[mask], *args, **kwargs)
        return


def plot_init(nrow, ncol, xlabs=None, ylabs=None, xlims=None, ylims=None):
    """TODO: Docstring for plot1.

    Parameters
    ----------
    arg1 : TODO

    Returns
    -------
    TODO
    """
    h, w = get_figsize(nrow, ncol)
    fig, axes = plt.subplots(nrow, ncol, figsize=(w, h))
    if not ((ncol == 1) & (nrow == 1)):
        add_panels(axes)
        if isinstance(xlabs, list):
            add_labs(axes, xlabs, ylabs)
        if isinstance(ylims, list):
            set_ylims(axes, ylims)
        if isinstance(xlims, list):
            set_xlims(axes, xlims)
    else:
        if isinstance(xlabs, list):
            axes.set_xlabel(xlabs[0])
            axes.set_ylabel(ylabs[0])

        if isinstance(xlims, list):
            axes.set_xlim(xlims[0])

        if isinstance(ylims, list):
            axes.set_ylim(ylims[0])
    return fig, axes


def getUniqueLegend(axes):
    """
    Obtains unique entries legend handles and labels from
    a matplotlib matplotlib.axes._subplots.AxesSubplot instance
    Returns the get entries

    Parameters
    ----------
    axes : matplotlib.axes._subplots.AxesSubplot instance.

    Returns
    -------
    handles : list
    labels : list

    Examples
    --------
    """
    old_handles, old_labels = axes.get_legend_handles_labels()
    handles = []
    labels = []
    for l, h in zip(old_labels, old_handles):
        if l not in labels:
            labels.append(l)
            handles.append(h)
    return handles, labels


def statplot(axes, x, y, conf=0.95,plot_conf_band=True,plot_predic_band=True):
    """
    performs linear regression and returns confidence band
    and prediciton band in a plot.
    """
    x, y = zip(*sorted(zip(x, y)))
    conf = conf
    fitparams, r2, fittedvalues, cb_low, cb_upp, pb_low, pb_upp, ce,f_pvalue = regression(
        x, y, conf=conf)
    ce1 = ce[0]
    ce2 = ce[1]
    axes.plot(x, y, marker='o', linestyle='', color=colors[0])
    axes.plot(x, fittedvalues, color=colors[0], linestyle=':',
              label='fit intercept %.2f\nslope %.2f, \n$r^2$ %.2f\n CI intercept [%.2f,%.2f] CI\n slope [%.2f,%.2f]' % (*fitparams, r2, *ce1, *ce2))
    if plot_conf_band:
        axes.plot(x, cb_low, color=colors[2], linestyle='--', label=r'%.2f \%% confidence band' % conf)
        axes.plot(x, cb_upp, color=colors[2], linestyle='--')
    if plot_predic_band:
        axes.plot(x, pb_low, color=colors[3], linestyle='--', label=r'%.2f \%% prediction band' % conf)
        axes.plot(x, pb_upp, color=colors[3], linestyle='--')
    return fitparams


def axoneone(axes,  x, y, color, xlab=None, ylab=None, xylims=None, lab='_', leg=False, title=None, marker="o", xerr=None, yerr=None, with_r2=True):
    mask = ((np.isfinite(x)) & (np.isfinite(y)))
    if with_r2:
        if (len(x[mask]) > 2) & (len(y[mask]) > 2):
            rvalue, _ = pearsonr(x[mask], y[mask])
        else:
            rvalue = 0
        lab+=r" $\rho=%.2f$" % rvalue
    one = [*axes.get_ylim()]
    if isinstance(xerr, (list, np.ndarray)):
        axes.errorbar(x, y, fmt=marker, color=color, xerr=xerr, yerr=yerr, linestyle="None", label=lab)
    else:
        axes.plot(x, y, linestyle="None", marker=marker, color=color, label=lab)
    # axes.text(0.1*(x2-x1)+x1,0.8*(x2-x1)+x1,"$r=%.2f$" % rvalue)
    axes.plot(one, one, 'k', linestyle=':')
    if leg == True:
        axes.legend()
    if isinstance(title, str):
        axes.set_title(title)
    if isinstance(xlab, str):
        axes.set_xlabel(xlab)
    if isinstance(ylab, str):
        axes.set_ylabel(ylab)
    if isinstance(xylims, tuple):
        axes.set_xlim(xylims)
        axes.set_ylim(xylims)
    return
