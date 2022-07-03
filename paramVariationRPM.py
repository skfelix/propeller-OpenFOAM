from os import path
import numpy as np
import os
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Basics.DataStructures import Vector
from numpy import linspace

from PyFoam.Execution.ConvergenceRunner import ConvergenceRunner
from PyFoam.Execution.UtilityRunner import UtilityRunner
from PyFoam.Execution.BasicRunner import BasicRunner
from PyFoam.Applications.Decomposer import Decomposer
from PyFoam.Applications.PlotRunner import PlotRunner
from PyFoam.Applications.Runner import Runner

# Solver variables
solver = 'rhoSimpleFoam'
nproc = 6

# Case variables
rpm = np.array([2500])
n = rpm/60
D = 0.33
omega = 2*np.pi*n
J = np.array([0.6, 0.5, 0.4, 0.3, 0.25, 0.20, 0.15, 0.1, 0.05])
#J = np.array([0.05])
# Base directory
templateCase = SolutionDirectory('propTemplate', archive=None, paraviewLink=False)
sourceCase = SolutionDirectory('propBase', archive=None, paraviewLink=False).name
# Simulation time
endTime = 400
caseControlDict = ParsedParameterFile(path.join(templateCase.name,'system','controlDict'))
caseControlDict['endTime'] = endTime
caseControlDict.writeFile()

# Clone folders and run
k = 19;
for j in range(len(rpm)):
    V = J*n[j]*D
    for i in range(len(V)):
        #i = 0;
        if i > 1:
            endTime = 300
        UInf = Vector(0,-V[i],0)
        # Clone folders
        case = templateCase.cloneCase('%dpropCase-RPM%.0f_U%.1f' %(k,rpm[j],V[i])).name
        os.system('cp Residuals FM %s' %(case))
        # Change RPM boundary condition
        rpmBC = ParsedParameterFile(path.join(case,'constant','MRFProperties'))
        rpmBC['MRF1']['omega']=omega[j] # y-axis velocity must be negative
        rpmBC.writeFile() 
         
        # Change velocity boundary condition
        velBC = ParsedParameterFile(path.join(case,'0','include','initialConditions'))
        velBC['UInf']=UInf # y-axis velocity must be negative
        velBC.writeFile()
        os.chdir(case)
        os.system("mapFields " + sourceCase + " -consistent -sourceTime 'latestTime'")
        velBC = ParsedParameterFile('0/U')
        velBC['boundaryField']['inlet']['value'] = 'uniform ' + str(UInf) # y-axis velocity must be negative
        velBC['boundaryField']['outlet']['inletValue'] = 'uniform ' + str(UInf)
        velBC.writeFile()
        
        # Simulation time
        caseControlDict = ParsedParameterFile('system/controlDict')
        caseControlDict['endTime'] = endTime
        caseControlDict.writeFile()
        os.chdir('../')
        
        # Decompose case
        Decomposer(args=[case,nproc])
        # Run solver in parallel
        PlotRunner(args=["--proc=%d"%nproc,'--no-default',solver,'-case',case])
        Runner(args=["reconstructPar","-case",case])
        os.chdir(case)
        os.system('rm -rf processor*')
        os.system('./Residuals')
        os.system('./FM')
        os.chdir('../')
        # Updates base case to last run
        sourceCase = SolutionDirectory(case, archive=None, paraviewLink=False).name
        # Next Step
        k = k + 1
