### README

### Introduction 

This repo contains a public backup of almost every script and program I wrote during and for my PhD. Also some of the analysis done for the following papers is presented here. 

#### Disclaimer 

Do note that I'm no longer maintaining this repo. Some of the code has not been ported from Python 2 to 3, and may be ill written, no longer working and/or is not very well annotated (sorry). If you do have questions about them, or in fact, anything that you may find in here, do contact me. The most important stuff is highlighted below.  

Some personal data may have been removed and so minor differences may exist with the published version

### Directory and file structure

## ``General rationale of this repo''

The dissertation consisted of four chapters presenting new analysis, preceded by an introduction, and followed by a general discussion. For each of these chapters, a python library was written containing chapter specific functionality providing the analysis. These are supported by libraries containing commonly used functionality and utilities. This in order to reuse code as much as possible. Nonetheless, the size of this repo has become quite extensive. Each chapter had its own codename: lisasd, limo, wisman, and stico. 

## ``thesis''
Yep, you can compile my thesis yourself. That is, after you have obtained the data, and successfully run all the scripts that perform the analyses using the python files, see [src_analysis](#src_analysis). The entire tex document is included here. 

The figures and tables presented in the dissertation can be found in the figures and table directories.    

## ``figures''

## ``tables''
 
## ``data''
On this online repo, data is an empty directory. It is there to put the data in, which can be obtained by contacting me. Since the data itself is a somewhat large file to distribute, and not all data used is mine to distribute, it is stored elsewhere. Only the version of this repo stored internally at the [Centre for Isotope research](https://www.rug.nl/cio), contains the data. 

## ``literature''
Empty directory. Literature cited in this work can be found in the file ``bibl.bib'' in the thesis directory. Like with some of the data, these files are not mine to distribute. Only the version stored internally at the [Centre for Isotope research](https://www.rug.nl/cio) contains the full set of PDFs. 

## ``src_pylibs''
This directory contains libraries used by the scripts to analysis mentioned above. 

This directory should be on your python path, so that imports work. This is taken care of by the configure_env.sh

## ``src_analysis'' {#src_analysis}
This folder contains the scripts that contain the analysis. The core functions are separated per chapter with code names lisasd (Chapter 2), limo (Chapter 3), wisman (Chapter 4), and stico (Chapter 5). These scripts typically spit out a figure, saved in the figures directory and/or a table into the table directory (formatted as a little texfile). A file will typically import the library of its respective chapter, and call one or a few functions from that library, do a small amount of further processing simply for display purposes, and produce a figure, a table or both. Hence, these scripts are used to do simply some of the figure or table aesthetics.

These files 

### dependencies 

Machine used at the time of publication (used my entire PhD), is 

In general a unix like operating system should work.

## Software


### Run the python files 


## ``configure_env.sh''

cd into the directory containing ``configure_env.sh''. It exports a couple of shell environmental variables: 

DATADIR
PYTHONPATH
FIGURESDIR
TABLESDIR
TEXINPUTS
BIBDIR
BIBINPUTS

These are needed to run the python files. The config.py looks for these.

## Run a python file. 

Go into the ``src_analysis''. 
``python <file.py>''

## Run them all

The script entitled ``ora'' (One to Run them All, I see you). Is a posix compliant shell scirpt (I use dash at the time of writing) thit finds all the python files in the ``src_analysis'' that contain the key otrta-p and runs them in parallel using [gnu parallel](https://www.gnu.org/software/parallel/)(link to [publication](https://doi.org/10.5281/zenodo.1146014)). A few scripts utilise the python multiprocessing library and have their own multithreading and hence these are run separately.  

## Compiling the thesis

``latexmk -pdf Thesis.tex''

# known warnings


