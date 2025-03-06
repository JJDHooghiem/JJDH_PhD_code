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
import datetime as dt  # Python standard library datetime  module
import numpy as np
from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/
import matplotlib.pyplot as plt
# replace basemap with cartopy<F5>
import pandas as pd
from stisolib import *
from lodautil.netcdf import data_selector
import config

Data_Dir = config.DataDir+'/ACE_FTS/V4/'
CO_26_nc = Dataset(Data_Dir+'ACEFTS_L2_v4p0_CO.nc', 'r')
CO_27_nc = Dataset(Data_Dir+'ACEFTS_L2_v4p0_CO_27.nc', 'r')
CO_28_nc = Dataset(Data_Dir+'ACEFTS_L2_v4p0_CO_28.nc', 'r')
CO_36_nc = Dataset(Data_Dir+'ACEFTS_L2_v4p0_CO_36.nc', 'r')
# Filter data based on year month latitude and longitude
filters = [['year', 2017, 2017],
           ['longitude', 0, 40],
           ['latitude', 65, 70],
           ['month', 4,  9],
           ]
max_alt = 30


CO_26 = CO_26_nc['CO'][data_selector('none', filters, CO_26_nc)][:, :max_alt]

CO_28 = CO_36_nc['CO_36'][data_selector(
    'none', filters, CO_28_nc)][:, :max_alt]
pres_36 = CO_36_nc['pressure'][data_selector(
    'none', filters, CO_36_nc)][:, :max_alt]*1013.25
pres_26 = CO_26_nc['pressure'][:max_alt]*1013.25
# print np.array([pres_36==pres_26]).all()
# CO_26=CO_26_nc['CO'][:,:40]

# CO_36=CO_36_nc['CO_36'][:,:40]
for major, minor, pres in zip(CO_26, CO_28, pres_36):
    major[(major == -999) | (major == -888)] = np.nan
    minor[(minor == -999) | (minor == -888)] = np.nan
    major = major*0.986544
    minor = minor*0.011084
    # minor = minor*0.001978
    # delta = ratio_to_delta(minor/major, 'VSMOW18')
    delta = ratio_to_delta(minor/major, 'VPDB13')
    plt.plot(delta, pres)
plt.xlim(-100, 50)
plt.ylim(200, 0)

plt.savefig('aceftscotest.pdf')
exit()
# %%


#CO2_626_nc=Dataset('ACEFTS_L2_v3p6_CO2.nc', 'r')
#CO2_636_nc=Dataset('ACEFTS_L2_v3p6_CO2_636.nc', 'r')
# Filter data based on year month latitude and longitude
# filters=[['year',2017,2017],
# ['longitude',0,360],
# ['latitude',60,70],
# ['month',9,9],
# ]
#
#
#
# CO_26=CO2_626_nc['CO2'][data_selector('none',filters,CO2_626_nc)][:,:40]
#
# CO_27=CO2_636_nc['CO2_636'][data_selector('none',filters,CO2_636_nc)][:,:40]
# altitude=CO_26_nc['altitude'][:40]
#
# %%
#
#
#
# %%
#import pandas as pd
#from glob import glob
# files=glob('*iso.asc')
# for f in files:
#    dat=pd.read_csv(f,header=0,sep='\s+',skiprows=9)
#    plt.plot(dat['CO'])
# print dat['(36)']
#
#
#
#
#
#
#
#
# %%
# nc_f = 'ACEFTS_L2_v3p6_OCS.nc'  # Your filename
# nc_f = 'ACEFTS_L2_v3p6_CO.nc'  # Your filename
##nc_f = 'ACEFTS_L2_v3p6_O2_2018-11.nc'
# nc_fid = Dataset(nc_f, 'r')  # Dataset is the class behavior to open the file
#                             # and create an instance of the ncCDF4 class
#nc_attrs, nc_dims, nc_vars = ncdump(nc_fid)
# %%
# max_lat=70.
# min_lat=60.
# max_lon=30.
# min_lon=20.
# c=0
# for i in range(0,len(nc_fid['latitude'])):
#    frac=np.round(float(i)/len(nc_fid['latitude']),3)*100
#    if nc_fid['year'][i]==2017:
#        if nc_fid['latitude'][i]<=max_lat and nc_fid['latitude'][i]>=min_lat and nc_fid['longitude'][i]<=max_lon and nc_fid['longitude'][i]>=min_lon:
#            plt.plot(nc_fid['OCS'][i]*1e12,nc_fid['altitude'],label=nc_fid['month'][i])
#            label=nc_fid['month'][i]
#    print(frac)
#    plt.legend()
#    plt.ylim(0,30)
#    plt.xlim(0,1000)
#    plt.ylabel('COS (ppt)')
#    plt.xlabel('altitude (km)')
# plt.savefig('COS_2017_lat60_lat70_lon20_lon30.pdf',format='pdf')
#
# %%
#
# for data in nc_fid['OCS'][nc_fid['year'][:]==2017]:
#    plt.plot(data)
# %%
#
#year_sel=(nc_fid['year'][:]==2017) & (nc_fid['month'][:]==1)
##sel=(nc_fid['latitude'][year_sel]>=60) & (nc_fid['latitude'][year_sel]<=70)
# data=nc_fid['OCS'][year_sel]
# lon=nc_fid['longitude'][year_sel]
# lat=nc_fid['latitude'][year_sel]
#
# data[:][data==-999]=np.nan
# data[:][data==-888]=np.nan
# lon=np.array(lon[:][np.isfinite(data[:,15])])
# lat=np.array(lat[:][np.isfinite(data[:,15])])
# data=np.array(data[:,15][np.isfinite(data[:,15])])*1e12
#
#
# %%
#
# 2D proj
#
#import matplotlib.pyplot as plt
#import matplotlib as mpl
#from mpl_toolkits.basemap import Basemap, cm
# requires netcdf4-python (netcdf4-python.googlecode.com)
#from netCDF4 import Dataset as NetCDFFile
#import numpy as np
#import matplotlib.pyplot as plt
#import os
# mpl.style.use('/Users/joram/.matplotlib/matplotlibrc/paper_copernicus.mplstyle')    # use custom mplstyle, maybe path should be changed
# os.environ["PATH"] += os.pathsep + '/Library/TeX/texbin/' # add latex to path so that latex compilation is possible
#
#
# year=2017
# for i in range(1,13):
#    month=i
#    monvec=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
#    os.mkdir(monvec[i-1])
#    os.chdir(monvec[i-1])
#    for j in [7,10,12,15,20,22,25,28,30]:
#        alt=j
#        altitude=nc_fid['altitude'][alt]
#
#        # plot rainfall from NWS using special precipitation
#        # colormap used by the NWS, and included in basemap.
#        year_sel=(nc_fid['year'][:]==year) & (nc_fid['month'][:]==month)
#        #sel=(nc_fid['latitude'][year_sel]>=60) & (nc_fid['latitude'][year_sel]<=70)
#        data=nc_fid['OCS'][year_sel]
#        lon=nc_fid['longitude'][year_sel]
#        lat=nc_fid['latitude'][year_sel]
#
#        data[:][data==-999]=np.nan
#        data[:][data==-888]=np.nan
#        lon=np.array(lon[:][np.isfinite(data[:,alt])])
#        lat=np.array(lat[:][np.isfinite(data[:,alt])])
#        data=np.array(data[:,alt][np.isfinite(data[:,alt])])*1e12
#        #nc = nc_fid
#        # data from http://water.weather.gov/precip/
#        #prcpvar = nc.variables['OCS']
#        #data = prcpvar[:,10]
#        #latcorners = nc.variables['latitude'][:,10]
#        #loncorners = -nc.variables['longitude'][:,10]
#        #lon_0 = nc.variables['latitude'][:]
#        #lat_0 = nc.variables['longitude'][:]
#        # create figure and axes instances
#        fig = plt.figure(figsize=(8,8))
#        ax = fig.add_axes([0.1,0.1,0.8,0.8])
#        # create polar stereographic Basemap instance.
#        m = Basemap(projection='mill',resolution='l',area_thresh=10000)
#        # draw coastlines, state and country boundaries, edge of map.
#        m.drawcoastlines()
#        #m.drawstates()
#        m.drawcountries()
#        # draw parallels.
#        #parallels = np.arange(0.,90,10.)
#        #m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10)
#        # draw meridians
#        #meridians = np.arange(180.,360.,10.)
#        #m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10)
#        #ny = data#.shape[0]; nx = data.shape[1]
#        lons, lats = np.meshgrid(lon, lat) # get lat/lons of ny by nx evenly space grid.
#        x, y = m(lon, lat) # compute map proj coordinates.
#        # draw filled contours.
#        clevs = [0,20,30,50,100,140,180,200,240,280,300,350,400,450,500]
#        cs = m.contourf(x,y,data,clevs,tri=True,linestyles='solid')#,latlon=True,tri=True,cmap=cm.s3pcpn)
#        # add colorbar.
#        monvec=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
#        cbar = m.colorbar(cs,location='bottom',pad="5%")
#        cbar.set_label('COS ppt')
#        # add title
#        plt.title('ACE-FTS COS '+monvec[month-1]+'-'+str(year)+' Altitude: '+ str(altitude)+' km' )
#
#        #plt.savefig('ACEFTS_COS_'+monvec[month-1]+'_'+str(year)+str(altitude)+'_km.pdf',format='pdf',bbox_inches='tight')
#        plt.close()
#    os.chdir('..')
#
#
#
# %%
#
#import matplotlib.pyplot as plt
#import matplotlib as mpl
#from mpl_toolkits.basemap import Basemap, cm
# requires netcdf4-python (netcdf4-python.googlecode.com)
#from netCDF4 import Dataset as NetCDFFile
#import numpy as np
#import matplotlib.pyplot as plt
#import os
#import numpy as np
#
#
# latbin=np.linspace(-90,90,180)
# %%
# data=np.array([np.array([1,2,3]),np.array([2,3,4]),np.array([2,3,4])])
# data=np.linspace(3,6,30)**2+np.linspace(3,6,30)
# def zonal_mean(lat,latbin,data):
#    lat=lat
#    latbin=latbin
#    digitized = np.digitize(lat, latbin)
#    zonal_means = [np.nanmean(data[digitized == i],axis=0) for i in range(1, len(latbin))]
#    return zonal_means
# %%
# s=np.linspace(0,100,30)
# for i in range(0,len(s)):
#    if s[i]>=50:
#        print(i)
#        break
#
# f=[i if s[i]>=50 break for i in range(0,len(s))]
##binned_statistic(lat, data, bins=46, range=(-90,90))[0]
# %%
#from scipy.interpolate import interp1d
# year=2017
# m=np.array([[12,1,2],[3,4,5],[6,7,8],[9,10,11]])
# times=['DJF','MAM','JJA','SON']
# latbin=np.linspace(-90,90,91)
# des_alt=31
# for ms,t in zip(m,times):
# for lol in range(0,1):
#    i,j,k=ms
#    monvec=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
# os.mkdir(monvec[i-1])
# os.chdir(monvec[i-1])
# for j in [7,10,12,15,20,22,25,28,30]:
# alt=j
# altitude=nc_fid['altitude'][alt]
#
#        # plot rainfall from NWS using special precipitation
#        # colormap used by the NWS, and included in basemap.
#    year_sel=(nc_fid['month'][:]==i) | (nc_fid['month'][:]==j) | (nc_fid['month'][:]==k)
#    #sel=(nc_fid['latitude'][year_sel]>=60) & (nc_fid['latitude'][year_sel]<=70)
#    alt=nc_fid['altitude'][:des_alt]
#    pres=np.array(nc_fid['pressure'][year_sel,:des_alt])
#    temp=np.array(nc_fid['temperature'][year_sel,:des_alt])
#    theta=temp*(1/pres)**(2./7.)
#    lat=nc_fid['latitude'][year_sel]
#    zonal_theta=zonal_mean(lat,latbin,theta)
#
#    pot380=[]
#    for i in zonal_theta:
#        a=alt[np.isfinite(i)]
#        i=i[np.isfinite(i)]
#
#        if len(i)!=0:
#            s=interp1d(i,a)
#            pot380.append(np.nanmin(s(380)))
#        else:
#            pot380.append(np.nan)
#
#
#
#    data=nc_fid['CO'][year_sel,:des_alt]
#    data[:][data==-999]=np.nan
#    data[:][data==-888]=np.nan
#    data=data*1e9
#
#
#    lat=nc_fid['latitude'][year_sel]
#
#    zonal=zonal_mean(lat,latbin,data)
#    bins=latbin[:-1]+np.diff(latbin)/2
#    y,x=np.meshgrid(alt,bins)
#    plt.figure(dpi=300)
#    cs = plt.contourf(x,y,zonal,levels=np.linspace(0,150,31))
#    plt.contour(x,y,zonal,levels=np.linspace(0,150,31),linewidths=0.1,colors='k')
#    plt.plot(bins,pot380,'k')
#    plt.xlim(85,-85)
#    plt.ylim(0,30)
#    plt.xlabel('Latitude')
#    plt.ylabel('Altitude')
#    plt.title('ACE-FTS CO 2003-2018 Zonal mean '+t)
#    plt.tight_layout()
#    cbar = plt.colorbar(cs,ticks=np.linspace(0,150,11))
#    cbar.set_label('CO ppb')
#    cbar.set_clim(0, 150)
# plt.savefig(t+'_ACEFTS_CO.pdf',format='pdf')
#    plt.close()
# %%
#
#        data[:][data==-999]=np.nan
#        data[:][data==-888]=np.nan
#        lon=np.array(lon[:][np.isfinite(data[:,alt])])
#        lat=np.array(lat[:][np.isfinite(data[:,alt])])
#        data=np.array(data[:,alt][np.isfinite(data[:,alt])])*1e12
#        #nc = nc_fid
#        # data from http://water.weather.gov/precip/
#        #prcpvar = nc.variables['OCS']
#        #data = prcpvar[:,10]
#        #latcorners = nc.variables['latitude'][:,10]
#        #loncorners = -nc.variables['longitude'][:,10]
#        #lon_0 = nc.variables['latitude'][:]
#        #lat_0 = nc.variables['longitude'][:]
#        # create figure and axes instances
#        fig = plt.figure(figsize=(8,8))
#        ax = fig.add_axes([0.1,0.1,0.8,0.8])
#        # create polar stereographic Basemap instance.
#        m = Basemap(projection='mill',resolution='l',area_thresh=10000)
#        # draw coastlines, state and country boundaries, edge of map.
#        m.drawcoastlines()
#        #m.drawstates()
#        m.drawcountries()
#        # draw parallels.
#        #parallels = np.arange(0.,90,10.)
#        #m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10)
#        # draw meridians
#        #meridians = np.arange(180.,360.,10.)
#        #m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10)
#        #ny = data#.shape[0]; nx = data.shape[1]
#        lons, lats = np.meshgrid(lon, lat) # get lat/lons of ny by nx evenly space grid.
#        x, y = m(lon, lat) # compute map proj coordinates.
#        # draw filled contours.
#        clevs = [0,20,30,50,100,140,180,200,240,280,300,350,400,450,500]
#        cs = m.contourf(x,y,data,clevs,tri=True,linestyles='solid')#,latlon=True,tri=True,cmap=cm.s3pcpn)
#        # add colorbar.
#        monvec=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
#        cbar = m.colorbar(cs,location='bottom',pad="5%")
#        cbar.set_label('COS ppt')
#        # add title
#        plt.title('ACE-FTS COS '+monvec[month-1]+'-'+str(year)+' Altitude: '+ str(altitude)+' km' )
#
# plt.savefig('ACEFTS_COS_'+monvec[month-1]+'_'+str(year)+str(altitude)+'_km.pdf',format='pdf',bbox_inches='tight')
#        plt.close()
#    os.chdir('..')
