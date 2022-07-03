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
rpm = 3000;
n = rpm/60;
J = np.array([0.6, 0.5, 0.4, 0.3, 0.25, 0.20, 0.15, 0.1, 0.05])
V = J*n*D
# Base directory
templateCase = SolutionDirectory('propTemplate', archive=None, paraviewLink=False)
sourceCase = SolutionDirectory('propBase', archive=None, paraviewLink=False).name
# Simulation time
endTime = 500
caseControlDict = ParsedParameterFile(path.join(templateCase.name,'system','controlDict'))
caseControlDict['endTime'] = endTime
caseControlDict.writeFile()

# Run mesh in template case
#UtilityRunner(argv =["blockMesh","-case",templateCase.name],silent=True).start()

# Clone folders and run
for i in range(len(V)):
    #i = 0;
    UInf = Vector(0,-V[i],0)
    # Clone folders
    case = templateCase.cloneCase('%dpropCase-Uy%.1f' %(i,V[i])).name
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
    os.chdir('../')
    # Updates base case to last run
    sourceCase = SolutionDirectory(case, archive=None, paraviewLink=False).name
    # Next Step
