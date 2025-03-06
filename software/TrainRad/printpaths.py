
from glob import glob
p=glob('/home/joram/research/data/LISA_Measurements/*Sampler_flight/Radiosonde/FLEDT*.tsv')

for i in p:
    print(i)
