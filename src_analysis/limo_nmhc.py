#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import scan.limo as limo
import config

fig, ax = limo.echamNMHC()
fig.tight_layout()
ax.legend()
fig.savefig(config.FigDir+'limo_nmhc.pdf', format='pdf', bbox_inches='tight')
