# coding: utf-8
from __future__ import division
__version__ = "2.0"
__author__ = "Cristobal Pais"
__maintainer__ = "Jaime Carrasco, Cristobal Pais, David Woodruff"
__status__ = "Alpha Operational"

# Importations
import os 
import numpy as np

# Generates scenario.dat files for optimization (Beta)
def ScenarioTrajectories(TotalYears, Sim, FI, FS, NCells, Cells_Obj, AdjCells, Folder, Demand,
                         alpha=0.15, probs=False, spotting=False, verbose=False):
    # Sets
    HPeriods = np.arange(0, TotalYears + 2, 2)      # Even periods are harvesting periods (0, 2, ...)
    FPeriods = np.arange(1, TotalYears + 2, 2)      # Odd periods are fire periods (1, 3, ...)
    Stands = np.arange(1, NCells + 1, 1)            # All stands
    BStands = [i + 1 for i in Cells_Obj.keys()]         # Stands that are part of the burning trajectory
   
    # Printing forest's data to a txt file
    if spotting == True:
        Folder = os.path.join(Folder, "ScenariosSpotting")
    else:
        Folder = os.path.join(Folder, "Scenarios")
    if not os.path.exists(Folder):
        os.makedirs(Folder)
    filed = open(os.path.join(Folder, "Scenario" + str(Sim) + ".dat"),"w")
                
    # Scenario Header
    filed.write("############################################################################\n")
    filed.write("# Author: CP\n")
    filed.write("# Date:   October 2018\n")
    filed.write("# NCells: " +str(NCells)+ ", FPeriods: " +str(TotalYears)+", alpha: " +str(alpha) +"\n")
    filed.write("############################################################################\n\n")
    
    if verbose == True:
        print("HPeriods:", HPeriods)
        print("FPeriods:", FPeriods)
        
    filed.write("#########################################################################################################################################################################################################"+"\n")
    filed.write("#																																																		   																																																															 "+"\n")
    filed.write("#                                                      Sets																																																																																																		 "+"\n")
    filed.write("#																																																																																																																	 "+"\n")							
    filed.write("#########################################################################################################################################################################################################"+"\n")
        
    # HPeriods
    filed.write("set HPeriods:= ")
    for i in sorted(HPeriods):
        if np.max(HPeriods) != i:
            filed.write(str(i) + " ")
        else:
            filed.write(str(i))
    filed.write(";\n")
        
    # FPeriods
    filed.write("set FPeriods:= ")
    for i in sorted(FPeriods):
        if np.max(FPeriods) != i:
            filed.write(str(i) + " ")
        else:
            filed.write(str(i))            
    filed.write(";\n")
    
    # Stands
    filed.write("set Stands:= ")
    for i in sorted(Stands):
        if np.max(Stands) != i:
            filed.write(str(i) + " ")
        else:
            filed.write(str(i))
    filed.write(";\n")
    
    # Burned Stands (trajectory)
    filed.write("set BStands:=")
    for i in BStands:
        filed.write(" " + str(i))
    filed.write(";\n\n")
    
    # Adjacents
    for c in Cells_Obj.keys():
        filed.write("set Adjacents[" + str(c) + "]:=")
        auxSet = set(a[0] for a in AdjCells[c-1].values() if a != None)
        for i in auxSet:
            filed.write(" "+ str(i))
        filed.write(";\n")
            
        
    filed.write("\n#########################################################################################################################################################################################################"+"\n")
    filed.write("#																																																		   																																																															 "+"\n")
    filed.write("#                                                      Parameters																																																																																																		 "+"\n")
    filed.write("#																																																																																																																	 "+"\n")							
    filed.write("#########################################################################################################################################################################################################"+"\n")
                    
    # Alpha
    filed.write("param alpha:= "+ str(alpha) + ";\n\n")
    
    # Demand
    
    # Volume
    
    # Final Volume
    
    # FPV values
    
        
    # Write FI
    filed.write("param FI:=\n")
    for i,tf,s in FI.keys():
        filed.write(str(i) + " " + str(tf) + " 1\n")
    filed.write(";\n\n")
            
    # Write FS
    filed.write("param FS:=\n")
    for i,j,tf,s in FS.keys():
        filed.write(str(i) + " " + str(j) + " " + str(tf) + " 1\n")
    filed.write(";\n\n")
    
    # Close the file                                
    filed.close()


  

def ScenarioTrajectoriesLite(TotalYears, Sim, FI, FS, NCells, Cells_Obj, AdjCells, HCells, Folder, Demand,
                                               alpha=0.15, probs=False, spotting=False, verbose=False):
    # Sets
    HPeriods = np.arange(0, TotalYears + 2, 2)      # Even periods are harvesting periods (0, 2, ...)
    FPeriods = np.arange(1, TotalYears + 2, 2)      # Odd periods are fire periods (1, 3, ...)
    Stands = np.arange(1, NCells + 1, 1)            # All stands
    BStands = [i + 1 for i in Cells_Obj.keys() if i+1 not in HCells]         # Stands that are part of the burning trajectory
   
    # Printing forest's data to a txt file
    if spotting == True:
        Folder = os.path.join(Folder, "ScenariosSpotting")
    else:
        Folder = os.path.join(Folder, "Scenarios")
    if not os.path.exists(Folder):
        os.makedirs(Folder)
    filed = open(os.path.join(Folder, "Scenario" + str(Sim) + ".dat"),"w")
                
    # Scenario Header
    filed.write("############################################################################\n")
    filed.write("# Author:     CP\n")
    filed.write("# Date:        October 2018\n")
    filed.write("# Instance:  NCells: " +str(NCells)+ ", FPeriods: " +str(TotalYears)+", alpha: " +str(alpha) +"\n")
    filed.write("############################################################################\n\n")
    
    if verbose == True:
        print("HPeriods:", HPeriods)
        print("FPeriods:", FPeriods)
        
    filed.write("#########################################################################################################################################################################################################"+"\n")
    filed.write("#																																																		   																																																															 "+"\n")
    filed.write("#                                                      Sets																																																																																																		 "+"\n")
    filed.write("#																																																																																																																	 "+"\n")							
    filed.write("#########################################################################################################################################################################################################"+"\n")
        
    # HPeriods
    filed.write("set HPeriods:= ")
    for i in sorted(HPeriods):
        if np.max(HPeriods) != i:
            filed.write(str(i) + " ")
        else:
            filed.write(str(i))
    filed.write(";\n")
        
    # FPeriods
    filed.write("set FPeriods:= ")
    for i in sorted(FPeriods):
        if np.max(FPeriods) != i:
            filed.write(str(i) + " ")
        else:
            filed.write(str(i))            
    filed.write(";\n")
    
    # Stands
    filed.write("set Stands:= ")
    for i in sorted(Stands):
        if np.max(Stands) != i:
            filed.write(str(i) + " ")
        else:
            filed.write(str(i))
    filed.write(";\n")
    
    # Burned Stands (trajectory)
    filed.write("set BStands:=")
    for i in BStands:
        filed.write(" " + str(i))
    filed.write(";\n\n")
    
    # Adjacents
    for c in Cells_Obj.keys():
        filed.write("set Adjacents[" + str(c+1) + "]:=")
        if c+1 not in HCells:
            auxSet = set(a[0] for a in AdjCells[c].values() if a is not None and a[0] in BStands)
        else:
            auxSet = set()
        for i in auxSet:
            filed.write(" "+ str(i))
        filed.write(";\n")
            
        
    filed.write("\n#########################################################################################################################################################################################################"+"\n")
    filed.write("#																																																		   																																																															 "+"\n")
    filed.write("#                                                      Parameters																																																																																																		 "+"\n")
    filed.write("#																																																																																																																	 "+"\n")							
    filed.write("#########################################################################################################################################################################################################"+"\n")
                    
    # Alpha
    filed.write("param alpha:= "+ str(alpha) + ";\n\n")
    
    # Demand
    
    # Volume
    
    # Final Volume
    
    # FPV values
    
        
    # Write FI
    filed.write("param FI:=\n")
    for i,tf,s in FI.keys():
        filed.write(str(i) + " " + str(tf) + " 1\n")
    filed.write(";\n\n")
            
    # Write FS
    filed.write("param FS:=\n")
    for i,j,tf,s in FS.keys():
        filed.write(str(i) + " " + str(j) + " " + str(tf) + " 1\n")
    filed.write(";\n\n")
    
    # Close the file                                
    filed.close()
	
