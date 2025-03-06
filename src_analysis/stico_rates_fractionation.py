import atmos
import numpy as np
import scantools
import stisolib

import config
a = np.linspace(1, 80000, 80000)
t, p = atmos.Standard_atmos_ar(a)

def corate(temp, press):
    k_G4110_k0 = 1.661E-11*np.exp(-8050./temp) + 1.494E-12 * \
        np.exp(-2300./temp) + 1.677E-13*np.exp(-30./temp)
    k_G4110_ki = 2.042E-09*np.exp(-7520./temp) + 1.827E-11 * \
        np.exp(-1850./temp) + 1.328E-12*np.exp(-120./temp)

    k_G4110_atp = 5.9 * np.exp(-temp/161) * (press*1E-5)
    k_G4110_fc = 0.49 + 0.51 * np.exp(-temp/300.0)
    k_G4110_fx = k_G4110_fc**(1.0/(1.0 + (np.log10(k_G4110_atp *
                                                   k_G4110_k0/(k_G4110_ki - k_G4110_k0)))**2))
    k_G4110_x = k_G4110_atp * (k_G4110_k0 / (k_G4110_ki - k_G4110_k0))
    k_G4110_kab = k_G4110_k0 * \
        (1.0 - k_G4110_fx * k_G4110_x / (1.0 + k_G4110_x))
    k_G4110_kac = k_G4110_atp * k_G4110_k0 * k_G4110_fx * \
        (1.0 + k_G4110_x / k_G4110_atp) / (1.0 + k_G4110_x)
    k_G4110_kr = k_G4110_kab + k_G4110_kac
    return k_G4110_kr


co_rate_troe = corate(t, p)

nden = atmos.ndens(t, p)


co_rate = (1.57E-13+(3.54E-33)*nden)


e_13CO_OH_simple = 1000*(stisolib.alpha_oh_c13(p)-1)
e_17CO_OH_simple = 1000*(stisolib.alpha_oh_o17(p)-1)
e_18CO_OH_simple = 1000*(stisolib.alpha_oh_o18(p)-1)


def eps_3step(p, t):
    k_oh_co, k_13CO_OH_3step, k_17CO_OH_3step, k_18CO_OH_3step = stisolib.co_3step_OH(
        p, t)

    e_13CO_OH_3step = 1000*(k_13CO_OH_3step/k_oh_co-1)
    e_17CO_OH_3step = 1000*(k_17CO_OH_3step/k_oh_co-1)
    e_18CO_OH_3step = 1000*(k_18CO_OH_3step/k_oh_co-1)
    return e_13CO_OH_3step, e_17CO_OH_3step, e_18CO_OH_3step


e_13CO_OH_3step, e_17CO_OH_3step, e_18CO_OH_3step = eps_3step(p, t)
xlabs = [r"k \ch{CO + OH}", r"$\eta$ \textperthousand", r"$p$ hPa", r"$T$"]
ylabs = [r"$p$ hPa", r"$p$ hPa", r"$\eta$ \textperthousand",
         r"$\eta$ \textperthousand"]
xlims = [(1.5E-13, 1.9E-13), (-15, 0), (0, 1000), (0, 300)]
ylims = [(200, 0), (200, 0), (-15, 15), (-15, 25)]
fig, axes = scantools.plot_init(
    2, 2, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)

b, r, g = config.GruvBoxColors[0:3]
axes[0, 0].plot(co_rate_troe, p/100, color=b, label="Troe")
axes[0, 0].plot(co_rate, p/100, color=g, label="McCabe")


def eps_to_kie(eps):
    a = eps/1000+1

    kie = 1000*(1-a)/a
    return kie


print(1000*(1-stisolib.alpha_oh_c13(1E5))/stisolib.alpha_oh_c13(1E5))
print(1000*(1-stisolib.alpha_oh_o17(1E5))/stisolib.alpha_oh_o17(1E5))
print(1000*(1-stisolib.alpha_oh_o18(1E5))/stisolib.alpha_oh_o18(1E5))
# e13_b = -5.4+0.014*(p/100)-3.1E-6*(p/100)**2
# axes[1, 0].plot(p/100, e13_b,  '-',
# color=b, label="$^{13}\ch{C}$ simple Berg.")
axes[0, 1].plot(eps_to_kie(e_13CO_OH_simple), p/100, '-', color=b, label=r"$^{13}\textrm{C}$ simple")
axes[0, 1].plot(eps_to_kie(e_17CO_OH_simple), p/100, '-', color=r, label=r"$^{17}\textrm{O}$ simple")
axes[0, 1].plot(eps_to_kie(e_18CO_OH_simple), p/100, '-', color=g, label=r"$^{18}\textrm{O}$ simple")
axes[0, 1].plot(eps_to_kie(e_13CO_OH_3step), p/100, ':', color=b,  label=r"$^{13}\textrm{C}$ 3-step")
axes[0, 1].plot(eps_to_kie(e_17CO_OH_3step), p/100, ':', color=r,  label=r"$^{17}\textrm{O}$ 3-step")
axes[0, 1].plot(eps_to_kie(e_18CO_OH_3step), p/100, ':', color=g,  label=r"$^{17}\textrm{O}$ 3-step")


t = np.array([298]*len(p))
e_13CO_OH_3step, e_17CO_OH_3step, e_18CO_OH_3step = eps_3step(p, t)

axes[1, 0].plot(p/100, eps_to_kie(e_13CO_OH_3step),  ':', color=b,  label=r"$^{13}\textrm{C}$ 3-step")
axes[1, 0].plot(p/100, eps_to_kie(e_17CO_OH_3step),  ':', color=r,  label=r"$^{17}\textrm{O}$ 3-step")
axes[1, 0].plot(p/100, eps_to_kie(e_18CO_OH_3step),  ':', color=g,  label=r"$^{17}\textrm{O}$ 3-step")
axes[1, 0].plot(p/100, eps_to_kie(e_13CO_OH_simple),  '-', color=b, label=r"$^{13}\textrm{C}$ simple")
axes[1, 0].plot(p/100, eps_to_kie(e_17CO_OH_simple),  '-', color=r, label=r"$^{17}\textrm{O}$ simple")
axes[1, 0].plot(p/100, eps_to_kie(e_18CO_OH_simple),  '-', color=g, label=r"$^{18}\textrm{O}$ simple")


t = np.linspace(1, 300, 301)
p = np.array([10000]*len(t))
e_13CO_OH_3step, e_17CO_OH_3step, e_18CO_OH_3step = eps_3step(p, t)
axes[1, 1].plot(t, eps_to_kie(e_13CO_OH_3step),  ':', color=b, label=r"$^{13}\textrm{C}$ 100 hPa")
axes[1, 1].plot(t, eps_to_kie(e_17CO_OH_3step),  ':', color=r, label=r"$^{17}\textrm{O}$ 100 hPa")
axes[1, 1].plot(t, eps_to_kie(e_18CO_OH_3step),  ':', color=g, label=r"$^{17}\textrm{O}$ 100 hPa")

t = np.linspace(1, 300, 301)
p = np.array([100000]*len(t))
e_13CO_OH_3step, e_17CO_OH_3step, e_18CO_OH_3step = eps_3step(p, t)
axes[1, 1].plot(t, eps_to_kie(e_13CO_OH_3step),  '-', color=b, label=r"$^{13}\textrm{C}$ 1000 hPa")
axes[1, 1].plot(t, eps_to_kie(e_17CO_OH_3step),  '-', color=r, label=r"$^{17}\textrm{O}$ 1000 hPa")
axes[1, 1].plot(t, eps_to_kie(e_18CO_OH_3step),  '-', color=g, label=r"$^{17}\textrm{O}$ 1000 hPa")
for ax, n in zip(axes.ravel(), [1, 1, 2, 1]):
    ax.legend(ncol=n)
fig.tight_layout()
fig.savefig(config.FigDir+'stico_rates_fractionation.pdf')
