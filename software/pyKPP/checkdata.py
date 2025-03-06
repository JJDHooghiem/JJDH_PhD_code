#!/opt/local/bin/python2
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt 
from LIBisokpp import *
import sys
from glob import glob
import os
if __name__ == '__main__' :
    path_to_data = 'Results_'+sys.argv[1]
    data_files=glob(path_to_data+'/*')
    base_dir=os.getcwd()
    for f in data_files:
        data_path=glob(f+'/*kppdat')
        data=pd.read_csv(data_path[0])
        try:
            os.mkdir(f+'/fig')
        except OSError:
            pass
        os.chdir(f+'/fig')
        for species in ['Br','Cl','N']: 
            check_kpp_balance(data,species)
        make_kpp_figures(data)
        os.chdir(base_dir)
