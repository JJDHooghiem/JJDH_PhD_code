"""
Author: Joram Jan Dirk Hooghiem

This code was written for the analysis presented in the disseration of Joram Jan Dirk Hooghiem
Functions that do the core analysis are presented in here.  

This program is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software Foundation, 
version 3. This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this 
program. If not, see <http://www.gnu.org/licenses/>.
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from matplotlib.colors import LinearSegmentedColormap

if 'FIGURESDIR' in os.environ:
    DataDir = os.getenv('DATADIR')
else:
    print('Missing environmental variable "DATADIR". Cannot run without data \n Exiting\n')
    exit()
if 'FIGURESDIR' in os.environ:
    FigDir = os.getenv('FIGURESDIR')
else:
    print('Missing environmental variable "FIGURESDIR". Figures will be saved in your home directory. \n To set the variable put this in your shell\'s config:\n\n\t export FIGURESDIR=\'path/to/dir\'')
    FigDir = os.getenv('HOME')

if 'TABLESDIR' in os.environ:
    TabDir = os.getenv('TABLESDIR')
else:
    print('Missing environmental variable "TABLESDIR". Figures will be saved in your home directory. \n To set the variable put this in your shell\'s config:\n\n\t export TABLESDIR=\'path/to/dir\'')

    TabDir = os.getenv('HOME')


# plot configuration axes labels
axl={
'ls'        : r'LISA',
'cams'      : r'CAMS',
'echam'     : r'EMAC',
'ac'        : r'AirCore ',
'co2'       : r"$y(\mathrm{CO}_2)/$({\textmugreek}mol~mol$^{-1}$)",
'invco'     : r"(nmol~mol$^{-1}$)$/y(\mathrm{CO})$",
'co'        : r"$y(\mathrm{CO})/$(nmol~mol$^{-1}$)",
'ch4'       : r"$y(\mathrm{CH}_4)/$(nmol~mol$^{-1}$)",
'h2o'       : r"$y(\mathrm{H}_2\mathrm{O})/$(cmol~mol$^{-1}$)",
'n2o'       : r"$y(\mathrm{N}_2\mathrm{O})/$(nmol~mol$^{-1}$)",
'kch4cl'    : r'$k(\mathrm{CH}_{4}+\mathrm{Cl})$',
'kch4oh'    : r'$k(\mathrm{CH}_{4}+\mathrm{OH})$',
'kcooh'     : r'$k(\mathrm{CO}+\mathrm{OH})$',
'kco2'      : r'$j(\mathrm{CO}_2)/$(s$^{-1}$)',
'fco2co'    : r'$f(\mathrm{CO}_2/\mathrm{CO}_{\mathrm{tot}})$',
'fch4co'    : r'$f(\mathrm{CH}_4/\mathrm{CO}_{\mathrm{tot}})$',
'fosdco'    : r'$f(\mathrm{O}(^{1}\mathrm{D})/\mathrm{CO}_{\mathrm{tot}})$',
'fo3co'     : r'$f(\mathrm{O}_3/\mathrm{CO}_{\mathrm{tot}})$',
'osd'       : r"$y(\mathrm{O}(^{1}\mathrm{D}))$ $\times10^{18}$",
'cl'        : r"$y(\mathrm{Cl})/$ppq",
'oh'        : r"$y(\mathrm{OH})/$ppq",
'colife'    : r'$\tau(\mathrm{CO})/$a',
'dco2'      : r"$\Delta y(\mathrm{CO}_2)/$({\textmugreek}mol~mol${^-1}$)",
'dco'       : r"$\Delta y(\mathrm{CO})/$(nmol~mol$^{-1}$)",
'dch4'      : r"$\Delta y(\mathrm{CH}_4)/$(nmol~mol$^{-1}$)",
'dh2o'      : r"$\Delta y(\mathrm{H}_2\mathrm{O})/$(cmol~mol$^{-1}$)",
'dlch4'     : r'$\Delta L(\mathrm{CH}_{4})/$\\(nmol~mol$^{-1}$ a$^{-1}$)',
'lch4'      : r'$L(\mathrm{CH}_{4})/$(nmol~mol$^{-1}$ a$^{-1}$)',
'alt'       : r"$z/$km",
'th'        : r"$\theta/$K",
'T'         : r"$T/$K",
'DT'        : r"$\Delta T/$K",
'vres'      : r"$\Delta z/$m",
'vsize'     : r"$V/$l$_{\mathrm{stp}}$",
'sno'       : r"Sample \#",
'ts'        : r"$t/$s",
'tho'       : r"$t/$h",
'yr'        : r"$t/$a",
'lisasdfit' : r"$a/$(l$_{\mathrm{stp}}$ hPa$^{-1}$)",
'p'         : r"$p/$Pa",
'mfr'       : r'$\Delta y(\mathrm{X})$',
'pa'        : r"$p_{\mathrm{a}}/$hPa",
'pv'        : r"$p_{\mathrm{v}}/$hPa",
'ph'        : r"$p/$hPa",
'Dph'       : r"$\Delta p/$hPa",
'13c'       : r'$\delta(^{13}\mathrm{C})/$\textperthousand',
'18o'       : r'$\delta(^{18}\mathrm{O})/$\textperthousand',
'17o'       : r'$\delta(^{17}\mathrm{O})/$\textperthousand',
'D17o'      : r'$\Delta(^{17}\mathrm{O})/$\textperthousand',
'18oco'     : r'$\delta(\mathrm{C^{18}O})/$\textperthousand',
'13cco'     : r'$\delta(\mathrm{^{13}CO})/$\textperthousand',
'E13c'      : r'$E(\delta(^{13}\mathrm{CO}))/$\textperthousand',
'fstrat'    : r'$f_{\mathrm{strat}}$',
'D18o'      : r'$\Delta \delta(^{18}\textrm{O})/$\textperthousand',
'osigco2'   : r'$\delta^{18}\mathrm{O}(\mathrm{CO}_{2})/$\textperthousand',
'osigch4'   : r'$\delta^{18}\mathrm{O}(\mathrm{CH}_{4})/$\textperthousand',
'osigosd'   : r'$\delta^{18}\mathrm{O}(\mathrm{O}(^{1}\mathrm{D}))/$\textperthousand',
'enr'       : r'$\varepsilon/$\textperthousand',
'f'         : r'$f$',
'fres'         : r'$f_{\mathrm{r}}$',
'pdens'     : r'$\rho(f)$',
'pdensn'    : r'$\rho$',
'fx'        : r'$f(\mathrm{X})$'
        }
# a thesis is printed on modified B5: 170mm by 240mm (B5 is 176 by 250 in mm)
figwidth = 5.1191099 # Inch
# for A4 this will do:
# figwidth = 6.26894 

Panels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)', '(g)', '(h)', '(i)', '(j)', '(k)']
Markers = ['d', 'o', '*', 'v', '^', '<', '>', 'h',  'p', 'x', '.', '8']
Linestyles = ['-' ,
        ':',
        '--',
        '-.',
      (0, (3, 1, 1, 1          )  )   ,
      (0, (3, 5, 1, 5, 1, 5    )  )   ,

      (0, (3, 10, 1, 10        )  )   ,
      (0, (3, 5, 1, 5          )  )   ,

      (0, (3, 10, 1, 10, 1, 10 )  )   ,
      (0, (1, 10               )  )   ,
      (0, (1, 1                )  )   ,

      (0, (5, 10               )  )   ,
      (0, (5, 5                )  )   ,
      (0, (5, 1                )  )   ,

      (0, (3, 1, 1, 1, 1, 1))]

# GruvBoxcolorsk
GruvBoxColors = ['#282828',
                 '#cc241d',
                 '#98971a',
                 '#d79921',
                 '#458588',
                 '#b16286',
                 '#689d6a',
                 '#a89984',
                 '#928374',
                 '#fb4934',
                 '#b8bb26',
                 '#fabd2f',
                 '#83a598',
                 '#d3869b',
                 '#8ec07c',
                 '#ebdbb2']
a=GruvBoxColors[0:5]
del(a[3])
GruvBox_cm= LinearSegmentedColormap.from_list('gruvbox',a,N=100)

SolarizedColors = [
    "#061419",
    "#214956",
    "#616344",
    "#95704A",
    "#628E41",
    "#9D9956",
    "#CFA665",
    "#b2bab9",
    "#7c8281",
    "#214956",
    "#616344",
    "#95704A",
    "#628E41",
    "#9D9956",
    "#CFA665",
    "#b2bab9"]
