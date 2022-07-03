# -*- coding: utf-8 -*-
"""
Created on Wed May 11 20:36:30 2022

@author: Felix
"""
import os
import numpy as np
import glob
import natsort
import math
import pandas as pd


folders = ['2500RPM','3000RPM','3500RPM']
V = pd.Series([[] for _ in range(len(folders)) ],index=folders)
J = pd.Series([[] for _ in range(len(folders)) ],index=folders)
T = pd.Series([[] for _ in range(len(folders)) ],index=folders)
Q = pd.Series([[] for _ in range(len(folders)) ],index=folders)
Ct = pd.Series([[] for _ in range(len(folders)) ],index=folders)
Cq = pd.Series([[] for _ in range(len(folders)) ],index=folders)
Cp = pd.Series([[] for _ in range(len(folders)) ],index=folders)
RPM = np.array([])
n = np.array([])
rpm=[]


rho = 1.225
D = 0.33

case_name = '0CLEAN'
for i in range(len(folders)):
    rpm.append(float(folders[i].replace('RPM','')))
RPM = np.array(rpm)
n = RPM/60 

for i in range(len(folders)):
    os.chdir(folders[i])
    U = []
    F = {'x':[],'y':[],'z':[]}
    M = {'x':[],'y':[],'z':[]}
    for root, dirs, files in os.walk('./'):
        for case in natsort.natsorted(dirs):
            if 'propCase' in case:
                str_split = case.split('_')
                U.append(float(str_split[5]) )
                
                
                with open(os.path.join('./', case, 'postProcessing', 'forces','0','force.dat')) as f:
                    data = f.readlines()
                    f.close()
                    
                    idx = data[-1].replace('(','').replace(')','').split()[0]
                    floor_idx = math.floor(float(idx)/100)*100 - 1
                    
                    force = data[floor_idx].replace('(','').replace(')','').split()
                    
                    # if len(F['y']) > 1 and float(force[2]) > 4*F['y'][-1]:
                    F['x'].append(float(force[1]))
                    F['y'].append(float(force[2]))
                    F['z'].append(float(force[3]))
                    
                with open(os.path.join(case, 'postProcessing', 'forces','0','moment.dat')) as f:
                    data = f.readlines()
                    f.close()
                    
                    moment = data[floor_idx].replace('(','').replace(')','').split()
                    
                    M['x'].append(float(moment[1]))
                    M['y'].append(float(moment[2]))
                    M['z'].append(float(moment[3]))
    
    # rpm.append(float(folders[i].replace('RPM','')))           
    V[folders[i]] = np.array(U)
    T[folders[i]] = np.array(F['y'])
    Q[folders[i]] = -np.array(M['y'])
    J[folders[i]] = np.array(U)/(n[i]*D)  
    Ct[folders[i]] = np.array(F['y'])/(rho*n[i]**2*D**4)
    Cq[folders[i]] = -np.array(M['y'])/(rho*n[i]**2*D**5)
    Cp[folders[i]] = 2*np.pi*np.array(M['y'])/(rho*n[i]**2*D**5)
    os.chdir('../')
    #%%
    
    with open('%sperfData%s.dat'%(case_name,folders[i]),'w') as f:
              print('J\tV\tT\tQ\tCt\tCq\tCp',file=f)
              for v,t,q,j,ct,cq,cp in zip(V[folders[i]],T[folders[i]],Q[folders[i]],J[folders[i]],Ct[folders[i]],Cq[folders[i]],Cp[folders[i]]):
                  print('%.4e\t%.4e\t%.4e\t%.4e\t%.4e\t%.4e\t%.4e'%(j,v,t,q,ct,cq,cp),file=f)

       
#%%

# with open('')

# with open('filename.txt', 'w') as outputfile:
#     print(tabulate(table), file=outputfile)

    
#%% Plot

import matplotlib.pyplot as plt
%matplotlib qt

fig, (ax1,ax2) = plt.subplots(2,2)

ax1 = plt.subplot(121)
ax1.plot(J['2500RPM'][:-3],Ct['2500RPM'][:-3],label='2500 RPM')
ax1.plot(J['3000RPM'][:-2],Ct['3000RPM'][:-2],label='3000 RPM')
ax1.plot(J['3500RPM'][:-1],Ct['3500RPM'][:-1],label='3500 RPM')
# ax1.plot(V[0:8],Ct[0:8])
ax1.set_xlabel('Uy [m/s]')
ax1.set_ylabel('Fy [N]')
ax1.grid(b='True',which='major',linestyle='-')
ax1.grid(b='True',which='minor',linestyle='--')
ax1.minorticks_on()
ax1.legend()
# ax1.set_ylim([0, 0.08])

ax2 = plt.subplot(122)
ax2.plot(J['2500RPM'][:-3],Cq['2500RPM'][:-3],label='2500 RPM')
ax2.plot(J['3000RPM'][:-2],Cq['3000RPM'][:-2],label='3000 RPM')
ax2.plot(J['3500RPM'][:-1],Cq['3500RPM'][:-1],label='3500 RPM')
ax2.set_xlabel('Uy [m/s]')
ax2.set_ylabel('My [N.m]')
ax2.grid(b='True',which='major',linestyle='-')
ax2.grid(b='True',which='minor',linestyle='--')
ax2.minorticks_on()
# ax2.set_ylim([0, 0.008])

fig.show()

