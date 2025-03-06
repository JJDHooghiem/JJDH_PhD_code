import lodautil
import stisolib
import atmos
import pyKPP
import numpy as np
dat="2017-04-26"
sample=3
LISA=lodautil.flattened_LISA()
data=lodautil.date_select(LISA,dat).reset_index()

time=np.floor(lodautil.get_sample_dt(data)[0][sample])+0.5
data=data.iloc[sample]

flight_variables={}
# flight_variables['ALT']=data['Altitude']
flight_variables['PRES']=data['p']
flight_variables['TEMP']=data['T']
flight_variables['LAT']=data['Lat']
# flight_variables['LON']=data['Lon']
flight_variables['LEV']=pyKPP.obtain_jval_lev(flight_variables['PRES'])
flight_variables['CAIR']=atmos.ndens(flight_variables['TEMP'],flight_variables['PRES'])
# handle chemistry
df={}
ncfid=lodautil.get_ncfid(interpolated=True,daymean=True)
df['O1D']=lodautil.get_echam_at_LISA(time, [data['p']*100], 'tracer_gp_O1D', ncfid, method='hyb', ch4=[data['CH4']])[0]
df['Cl']=lodautil.get_echam_at_LISA(time, [data['p']*100], 'tracer_gp_Cl', ncfid, method='hyb', ch4=[data['CH4']])[0]
df['OH']=lodautil.get_echam_at_LISA(time, [data['p']*100], 'tracer_gp_OH', ncfid, method='hyb', ch4=[data['CH4']])[0]

x12,x13=stisolib.stat_distr_full_C(stisolib.ch4_to_c13(data[ 'CH4'],'w'),1)
df['CH4']=x12*data[ 'CH4']*1E-9
df['_13_CH4']=x13*data[ 'CH4']*1E-9

d13C, d17O, d18O=atmos.CO2iso(data[ 'CO2']*1E-6,data[ 'CH4']*1E-9)
x626, x636, x628, x627, _, _, _, _, _, _, _, _=stisolib.stat_distr_full_CO2(d13C, d17O, d18O)
df['CFACTOR']=flight_variables['CAIR']
df['CO2']     = x626*data[ 'CO2']*1E-6
df['C_18_OO'] = x628*data[ 'CO2']*1E-6
df['_13_CO2'] = x636*data[ 'CO2']*1E-6
x26, x36, x28, x27,_, _=stisolib.stat_distr_full_CO(data[ 'd13C(CO)'],stisolib.calc_d17o_mdf(data[ 'd18O(CO)']),data[ 'd18O(CO)'])

df['CO']    =x26*data[ 'CO']*1E-9
df['_13_CO']=x36*data[ 'CO']*1E-9
df['C_18_O']=x28*data[ 'CO']*1E-9

df['H2']=0
df['H2O']=0

df['O2']=0.209
df['N2']=0.781

df['C_18_O']=x28*data[ 'CO']*1E-9

with open('/home/joram/.local/src/kpp/models/init_tp','w') as f:
    for key in flight_variables.keys():
        f.write(key+'='+ str(flight_variables[key])+';\n')
f.close()
with open('/home/joram/.local/src/kpp/models/init_val','w') as f:
    for key in df.keys():
        f.write(key+'='+ str(df[key])+';\n')
f.close()
