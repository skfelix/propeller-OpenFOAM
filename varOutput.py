from os import path
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from numpy import linspace


# Solver variables
solver = 'rhoSimpleFoam'
nproc = 6

# Case variables
Uy = linspace(12,30,5)

# Simulation time
endTime = 1000

#%% Get outputs
import numpy as np

F = {}
F['x'] = []
F['y'] = []
F['z'] = []
M = {}
M['x'] = []
M['y'] = []
M['z'] = []



for i in range(len(Uy)):
    case = SolutionDirectory('propCase2-Uy%.1f' %Uy[i], archive=None, paraviewLink=False)
    with open(path.join(case.name, 'PyFoamRunner.'+solver+'.logfile')) as f:
        data = f.readlines()
        f.close()
        
        idxLastTime = data.index('Time = %d\n' %endTime)
        dataLastTime = data[idxLastTime:]
        
        idxTotalString = [i for i, s in enumerate(dataLastTime) if 'Total' in s]
        forceLine = dataLastTime[idxTotalString[0]]
        momentLine = dataLastTime[idxTotalString[1]]
        
        F['x'].append(float(forceLine.split()[2].replace('(','')))
        F['y'].append(float(forceLine.split()[3]))
        F['z'].append(float(forceLine.split()[4].replace(')','')))
        
        M['x'].append(float(momentLine.split()[2].replace('(','')))
        M['y'].append(float(momentLine.split()[3]))
        M['z'].append(float(momentLine.split()[4].replace(')','')))
        

    
#%% Plot

import matplotlib.pyplot as plt

ax1 = plt.subplot(121)
ax1.plot(Uy,F['y'])
ax1.set_xlabel('Uy [m/s]')
ax1.set_ylabel('Fy [N]')
ax1.grid(b='True',which='major',color='k',linestyle='-')
ax1.grid(b='True',which='minor',color='k',linestyle='--')
ax1.minorticks_on()

ax2 = plt.subplot(122)
ax2.plot(Uy,M['y'])
ax2.set_xlabel('Uy [m/s]')
ax2.set_ylabel('My [N.m]')
ax2.grid(b='True',which='major',linestyle='-')
ax2.grid(b='True',which='minor',linestyle='--')
ax2.minorticks_on()

