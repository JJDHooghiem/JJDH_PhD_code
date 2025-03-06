import lodautil
import scipy.stats
import lodautil
import config
import scantools
import numpy as np
lisa = lodautil.var_select(lodautil.flattened_LISA(), 'd18O(CO)')
print(scipy.stats.pearsonr(lisa['d18O(CO)'],lisa['PT'])[0])
print(np.min(lisa['T']),np.max(lisa['T']))

data=lodautil.flattened_LISA()

lisa = lodautil.flattened_LISA()
colors = config.GruvBoxColors
markers = config.Markers
xkey="CH4"
ykey='PT'
# Figure 1
xlabs = [config.axl['co']]#, r'\ch{CH4} (ppb)', r'$\delta^{18}$O (\textperthousand)', r'$\delta^{13}$C (\textperthousand)']

ylabs = [config.axl['th']]
fig, axes = scantools.plot_init( 1, 1, xlabs=xlabs, ylabs=ylabs) 
for dat, m, c in zip(lodautil.get_dates(lisa), markers, colors):
    data = lodautil.date_select(lisa, dat)
    ykey = 'PT'
    # for ax, xkey in zip(axes.ravel(), ['CO', 'CH4', 'd18O(CO)', 'd13C(CO)']):
    axes.plot(data[xkey]/data['CO2'], data[ykey], marker=m, linestyle='-', color=c, label=dat)
# axes.plot(data[xkey], data[ykey],color=colors[0],linestyle='',marker='o')
# axes.plot(data[xkey]/data['CO2'], data[ykey],color=colors[0],linestyle='',marker='o')
# axes[0].legend()
fig.tight_layout()
fig.savefig(config.FigDir+'stico_lisa_%s.pdf' % xkey, format='pdf', bbox_inches='tight')

