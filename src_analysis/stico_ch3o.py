import scan.stico as stico
import matplotlib.pyplot as plt
import config
import scantools
var1 = 'FMO1DCH3O'
var2 = 'FOZCH3O'
# var1='FMO1DHCHO'
# var2='FOZHCHO'

xlabs = [r'\ch{'+var1+'}/\ch{'+var2+'}']
ylabs = ['$p$ (hPa)']
fig, axes = scantools.plot_init(1, 1, xlabs=xlabs, ylabs=ylabs)
stico.echamfx(axes, var1, var2)
plt.savefig(config.FigDir+'stico_'+var1.lower() +
            '_'+var2.lower()+'.pdf', format='pdf')
plt.close()

