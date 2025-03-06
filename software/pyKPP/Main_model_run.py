#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 11:03:05 2019

@author: joram
"""

import time
tstart=time.time()
from glob import glob
import pandas as pd
import numpy as np
import os
import subprocess
import multiprocessing
import sys
import matplotlib
from datetime import datetime

def save_input(INPUT_DICTIONARY,sim_name):
    f = open(sim_name+'.txt', 'w') 
    f.write(str(INPUT_DICTIONARY))
    f.close()
    return 

def run_model(INPUT_DICTIONARY):
# =============================================================================
# copy kpp input files to a new folder using a shell script
# =============================================================================
    sim_name=filename_constructor(INPUT_DICTIONARY)
    print 
    print "Preparing simulation ",sim_name
    print 
    subprocess.call([py_kpp_dir+r'cpfile.sh',sim_name,kpp_def,kpp_model],stdout=devnull, stderr=devnull)
    os.chdir(kpp_dir+'CO_iso/'+sim_name) # kpp_dir is global variable
    save_input(INPUT_DICTIONARY,sim_name)
# =============================================================================
# Change .def file with pres/temp/ndens/lat/values. 
# =============================================================================
    change_kpp_base_path(sim_name)
    change_kpp_input(INPUT_DICTIONARY,sim_name,kpp_dir)
    print 
    print "Integrating simulation ",sim_name
    print 
    subprocess.call([py_kpp_dir+r'run_model.sh',sim_name,kpp_dir],stdout=devnull, stderr=devnull)
    
    data=kpp_load_data()
    
    data=post_process(ini_con,data)
#    os.mkdir('fig')
#    os.chdir('fig')
#    check_kpp_balance(data,'Br')
#    check_kpp_balance(data,'N')
#    check_kpp_balance(data,'Cl')
#    make_kpp_figures(data)
#    os.chdir('..')
    data.to_csv(sim_name+'.kppdat',index=False)
    print 
    print "Cleaning up for ",sim_name
    print 
    subprocess.call([py_kpp_dir+r'copy_results.sh',sim_name,kpp_dir,batch_results_dir])
    
    os.chdir(py_kpp_dir)
    
    
    return

def main():


    sims_to_run=prep_input(LISA,ini_con)
    print '########################################################'
    print
    print 'Starting to run ',len(sims_to_run),' simulations'
    print
    print '########################################################'
    pool = multiprocessing.Pool()
    pool.map(run_model,sims_to_run)
    print '########################################################'
    print
    print 'Finished ',len(sims_to_run),' simulations in ',np.round((time.time()-tstart)/60.,2),' minutes'
    print
    print '########################################################'
    return
if __name__ == '__main__':
    #matplotlib.use('Agg')
    #%%
    import matplotlib.pyplot as plt
    # =============================================================================
    # GLOBAL VARIABLES
    # =============================================================================
    LISA_dir='/Users/joram/Documents/Data_Scientific/LISA_Measurements/'
    kpp_dir='/Users/joram/scripts/Modelling/kpp/'
    
    py_kpp_dir=r'/Users/joram/scripts/Modelling/kpp_py_interface/'
    os.chdir(py_kpp_dir)
    batchname=sys.argv[1]
    rdir='Results_'+batchname
    os.mkdir(rdir)
    if sys.argv[2] == 'ini':
        kpp_def='strato_CO_ini'
        kpp_model='strato_CO_ini'
    else:
        kpp_def='strato_CO_base'
        kpp_model='strato_CO'
    batch_results_dir=py_kpp_dir+rdir 
    print '########################################################'
    print
    print 'Working Directory is set to: ',os.getcwd()
    print
    print '########################################################'
    from LIBisokpp import *
    print '########################################################'
    print
    print 'Succesfully loaded functions: '
    print
    print '########################################################'
  
    LISA=import_LISA(LISA_dir)
    
    devnull = open(os.devnull, 'w')
    
    ini_con=pd.read_csv(py_kpp_dir+'/initial_condition.csv',sep=',')
    
    print
    print 'Succesfully loaded LISA data and stable isotope definitinos'
    print
    # =============================================================================
    # RUNNING MAIN CODE 
    # =============================================================================
    main()
    subprocess.call(['./checkdata.py',batchname])


