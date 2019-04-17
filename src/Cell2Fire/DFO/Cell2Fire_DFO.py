# coding: utf-8
__version__ = "1.0"
__author__ = "Cristobal Pais"

# Importations
import numpy as np
import pandas as pd
import os
import shutil
import time
import subprocess

# Deal with Paths
import os.path

# Scipy for linear algebra
from scipy.sparse import *
from scipy import sparse
from scipy.sparse.linalg import norm

# No warnings
import warnings
warnings.simplefilter("error", RuntimeWarning)

'''
Function for BOBYQUA
Description:
Call to the simulator norm difference function
'''
def Cell2Fire_Norm(x, grad, OutFolder, PathC, PScars, PInstance, weights, ntype='fro',
                   TuningParams={}, LengthParams={}, EllipticalROS=np.ones(4), 
                   ROS_Threshold=0.1, verbose=False):
    # X point
    if grad.size > 0:
        pass
    
    x = np.abs(x).flatten()
    print("****************************************************************************************")
    print("\nInitial x:", x)
   
    #Cell2Fire_Norm function
    PathOut = OutFolder
    PathScars = PScars
    PathCSim = PathC
    PathInstance = PInstance
    Precision = 1.0
    maxidx = 0
    
    # Objective function
    Fobj = 0
    
    # Command line 
    # Parse args for calling C++ via subprocess        
    execArray=[os.path.join(os.getcwd(),'Cell2FireC/Cell2Fire'), 
               '--input-instance-folder', PathInstance,
               '--output-folder', OutFolder,
               '--ignitions',
               '--final-grid',
               '--Fire-Period-Length', str(1.0),
               '--HFactor' if ("EllipticalROS" in TuningParams.keys()) else '',
               str(x[1]) if ("EllipticalROS" in TuningParams.keys()) else '',
               '--FFactor' if ("EllipticalROS" in TuningParams.keys()) else '',
               str(x[2]) if ("EllipticalROS" in TuningParams.keys()) else '',
               '--BFactor' if ("EllipticalROS" in TuningParams.keys()) else '',
               str(x[3]) if ("EllipticalROS" in TuningParams.keys()) else '',
               '--EFactor' if ("EllipticalROS" in TuningParams.keys()) else '',
               str(x[4]) if ("EllipticalROS" in TuningParams.keys()) else '',
               '--ROS_Threshold' if ("CriticalSROS" in TuningParams.keys()) else '',   
               str(x[0]) if ("CriticalSROS" in TuningParams.keys()) else '',
              ]
    
    if verbose:
        print("ExecArray:", execArray)

    # Information
    print("Running the simulation with:")
    if "CriticalSROS" in TuningParams.keys():
        print("SROS Threshold:", x[0]) 
    
    if "EllipticalROS" in TuningParams.keys():      
        print("EllipticalROS (HROS, FROS, BROS, EFactor):\t", x[1:4])
        
    
    # Output log
    if OutFolder is not None:
        if os.path.isdir(OutFolder) is False:
            os.makedirs(OutFolder)
    LogName = os.path.join(OutFolder, "LogFile.txt")
    
    # Perform the call
    try:
        with open(LogName, 'w') as output:
            proc = subprocess.Popen(execArray, stdout=output)
            proc.communicate()
            proc.wait()
        print("done running sim...")
                
        # Reading original scar
        GridPath = os.path.join(OutFolder, "Grids", "Grids1")
        if os.path.exists(GridPath):
            GridFiles = os.listdir(GridPath)
            print("Info:", GridPath, GridFiles)
            if len(GridFiles) > 0: 
                ForestGridM = pd.read_csv(GridPath +"/"+ GridFiles[-1], delimiter=',', header=None).values
                sM1 = sparse.csr_matrix(ForestGridM)

                # Comparison grids
                filenameScar = PathScars + "/FinalScarGrid.csv"
                RealForestGridM = pd.read_csv(filenameScar, delimiter = ",", header=None).values
                sM2 = sparse.csr_matrix(RealForestGridM)

                # Verbosity 
                if verbose:
                    print("Real Scar:\n", PForestGridM)
                    print("Simulated Scar:\n", ForestGridM)

                # Compute the norm
                Fobj+= norm(sM1 - sM2, ntype)

                # Test objective function 
                shutil.rmtree(PathOut + "/Grids") 

        else:
            print("No grids were generated from the simulation, check parameters...")
            Fobj = 99999.
        
    
    except Exception as e:
        # No solution, then, return inf
        print("Algorithm failed due to:", e)
        Fobj = 99999.
        
    
    # Delta time
    print("Fobj:", Fobj)
    time.sleep(1)
    
    # Return
    return Fobj