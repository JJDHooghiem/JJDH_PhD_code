#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 14:03:44 2018

@author: joram
"""
import os
import pandas as pd
import numpy as np
from shutil import copyfile
from glob import glob

from io import StringIO

def LoadLisa(path):
  
    #path='2017-04-26_LISA_flight.csv'
    with open(path,'r') as result:
        headerstring=result.read()
        header,data=headerstring.split('End of header information\n')
        data = StringIO(data)
        data = pd.read_csv(data, sep=",")       
    return header,data

# create tex file 
header,data=LoadLisa(glob('Processed/*LISA_flight.csv')[0])
finfo,header=header.split('end Flight info')
finfo=finfo.replace('Flight info','')
unit,header=header.split('End of unit declaration\n')
unit=unit.replace('Units are defined here','')
unit=unit.replace("\t",'')
unit=unit.replace(r'  ','')
unit=pd.read_csv(StringIO(unit),sep=',')
header=header.replace("_","\\_")
#print(header
with open('LISA_config.py') as configfile:
    config=configfile.readlines()
    configfile.close()
copyfile('/home/joram/.local/src/python/LIptool/makefile','makefile')
# 
date=data['Date'][0]   
f = open('/home/joram/.local/src/python/LIptool/template.tex','r')
contents=f.readlines()

f.close()
print(date)
name=date.replace('-','')+'report.tex'
with open(name,'w') as newfile:
    for line in contents:
        if 'title' in line:
            newfile.write(line.replace('<++>','LISA flight report '+date))
        else:       
            newfile.write(line)
        if 'maketitle' in line:
            
            newfile.write(finfo)
            newfile.write('\n')
            newfile.write(header+'\n')
            newfile.write('\\footnotesize\n')
            
            newfile.write('\\begin{table}[htpb]\n\\centering\n')
            newfile.write(unit.to_latex(index=False))
            newfile.write('\\end{table}\n\\newpage')
            for i in range(0,int( len(data.keys())/7 )):
                newfile.write('\\begin{table}[htpb]\n\\centering\n')
                newfile.write(data.iloc[:,i*7:i*7+7].to_latex(index=False))
                newfile.write('\\end{table}\n\n')
            if len(data.keys())%7>0:
                num= len(data.keys())%7
                newfile.write('\\begin{table}[htpb]\n\\centering\n')
                newfile.write(data.iloc[:,-num:].to_latex(index=False))
                newfile.write('\\end{table}\n\n')
            newfile.write('\\newpage\n')
            newfile.write('\\begin{verbatim}\n')
            for configline in config:
                newfile.write(configline)
            newfile.write('\\end{verbatim}\n')
            newfile.write('\\newpage\n')                    
            pdfs=glob('Figures/*.pdf')   
            print(len(pdfs))
            u=0
            for pdf in sorted(pdfs):
                u+=1
                newfile.write('\\begin{{figure}}[htpb]\n\\centering\n\\includegraphics[width=0.8\\textwidth]{{{filename}}}\n\\caption{{Automatic figure generation{{{0}}}}}\n\\label{{fig:{{{1}}}}}\n\\end{{figure}}\n\\newpage\n'.format(u,u,filename=pdf))

    newfile.close()
# Generate the makefile 
makefile='''
# Tools
LATEXMK = latexmk
RM = rm -f

# Filename
DOCNAME = {}report
# Targets
all: doc
doc: pdf
pdf: $(DOCNAME).pdf

# Rules
%.pdf: %.tex
	$(LATEXMK) -silent -pdf -M -MP -MF $*.d $*

mostlyclean:
	$(LATEXMK) -silent -c 

clean: mostlyclean
	$(LATEXMK) -silent -C
	$(RM) *.run.xml *.synctex.gz
	$(RM) *.d

.PHONY: all clean doc mostlyclean pdf
'''
with open('makefile','w') as make:
    make.write(makefile.format(date.replace('-','')))
    make.close()
import subprocess
subprocess.call(['make']) 

subprocess.call(['make','mostlyclean']) 
#pdfs=glob('Figures/*.pdf')   
#for pdf in sorted(pdfs):
#    os.remove(pdf)
#from PyPDF2 import PdfFileMerger
#master='report.pdf'
#pdfs=glob('Figures/*.pdf')   
#print(pdfs
#merger=PdfFileMerger()
#merger.append(master)
#for pdf in pdfs:
#    merger.append(pdf)
#
#merger.write("report_final.pdf")
#merger.close()

exit()
