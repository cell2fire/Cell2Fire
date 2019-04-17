
# coding: utf-8
from argparse import ArgumentParser
import numpy as np
import pandas as pd
import os
pd.options.mode.chained_assignment = None


# Reads fbp_lookup_table.csv and creates dictionaries for the fuel types and cells' colors
def Dictionary(filename):
    aux = 1
    file = open(filename, "r") 
    row = {}
    colors = {} 
    all = {}
    
    # Read file and save colors and ftypes dictionaries
    for line in file: 
        if aux > 1:
            aux +=1
            line = line.replace("-","")
            line = line.replace("\n","")
            line = line.replace("No","NF")
            line = line.split(",")
            
            if line[3][0:3] in ["O1a", "O1b"]:
                row[line[0]] = line[3][0:3]
            else:
                row[line[0]] = line[3][0:2]
            colors[line[0]] = (float(line[4]) / 255.0, 
                               float(line[5]) / 255.0,
                               float(line[6]) / 255.0,
                               1.0)
            all[line[0]] = line
    
        if aux == 1:
            aux +=1
            
    return row, colors

# Reads the ASCII file with the forest grid structure and returns an array with all the cells and grid dimensions nxm
# Modified Feb 2018 by DLW to read the forest params (e.g. cell size) as well
def ForestGrid(filename, Dictionary):
    with open(filename, "r") as f:
        filelines = f.readlines()

    line = filelines[4].replace("\n","")
    parts = line.split()
    
    if parts[0] != "cellsize":
        print ("line=",line)
        raise RuntimeError("Expected cellsize on line 5 of "+ filename)
    cellsize = float(parts[1])
    
    cells = 0
    row = 1
    trows = 0 
    tcols = 0
    gridcell1 = []
    gridcell2 = []
    gridcell3 = []
    gridcell4 = []
    grid = []
    grid2 = []
    
    # Read the ASCII file with the grid structure
    for row in range(6, len(filelines)):
        line = filelines[row]
        line = line.replace("\n","")
        line = ' '.join(line.split())
        line = line.split(" ")
        #print(line)
        
        
        for c in line: #range(0,len(line)-1):
            if c not in Dictionary.keys():
                gridcell1.append("NData")
                gridcell2.append("NData")
                gridcell3.append("NData")
                gridcell4.append("NData")
            else:
                gridcell1.append(c)
                gridcell2.append(Dictionary[c])
                gridcell3.append(int(c))
                gridcell4.append(Dictionary[c])
            tcols = np.max([tcols,len(line)])

        grid.append(gridcell1)
        grid2.append(gridcell2)
        gridcell1 = []
        gridcell2 = []
    
    # Adjacent list of dictionaries and Cells coordinates
    CoordCells = np.empty([len(grid)*(tcols), 2]).astype(int)
    n = 1
    tcols += 1
    
    return gridcell3, gridcell4, len(grid), tcols-1, cellsize

# Reads the ASCII files with forest data elevation, saz, slope, and (future) curing degree and returns arrays
# with values
def DataGrids(InFolder, NCells):
    filenames = ["elevation.asc", "saz.asc", "slope.asc", "cur.asc"]
    Elevation =  np.full(NCells, np.nan)
    SAZ = np.full(NCells, np.nan)
    PS = np.full(NCells, np.nan)
    Curing = np.full(NCells, np.nan)
    
    for name in filenames:
        ff = os.path.join(InFolder, name)
        if os.path.isfile(ff) == True:
            aux = 0
            with open(ff, "r") as f:
                filelines = f.readlines()

                line = filelines[4].replace("\n","")
                parts = line.split()

                if parts[0] != "cellsize":
                    print ("line=",line)
                    raise RuntimeError("Expected cellsize on line 5 of "+ ff)
                cellsize = float(parts[1])

                row = 1

                # Read the ASCII file with the grid structure
                for row in range(6, len(filelines)):
                    line = filelines[row]
                    line = line.replace("\n","")
                    line = ' '.join(line.split())
                    line = line.split(" ")
                    #print(line)


                    for c in line: 
                        if name == "elevation.asc":
                            Elevation[aux] = float(c)
                            aux += 1
                        if name == "saz.asc":
                            SAZ[aux] = float(c)
                            aux += 1
                        if name == "slope.asc":
                            PS[aux] = float(c)
                            aux += 1
                        if name == "curing.asc":
                            Curing[aux] = float(c)
                            aux += 1

        else:
            print("   No", name, "file, filling with NaN")
            
    return Elevation, SAZ, PS, Curing

# Generates the Data.dat file (csv) from all data files (ready for the simulator)
def GenerateDat(GFuelType, Elevation, PS, SAZ, Curing, InFolder):
    # DF columns
    Columns = ["fueltype", "mon", "jd", "M", "jd_min", 
               "lat", "lon", "elev", "ffmc", "ws", "waz", 
               "bui", "ps", "saz", "pc", "pdf", "gfl", 
               "cur", "time", "pattern"]
    
    # GFL dictionary
    GFLD = {"C1": 0.75, "C2": 0.8, "C3": 1.15, "C4": 1.2, "C5":1.2, "C6":1.2, "C7":1.2, 
            "D1": np.nan, "D2": np.nan, 
            "S1":np.nan, "S2": np.nan, "S3": np.nan, 
            "O1a":0.35, "O1b":0.35, 
            "M1": np.nan, "M2": np.nan, "M3":np.nan, "M4":np.nan, "NF":np.nan,
            "M1_5": 0.1, "M1_10": 0.2,  "M1_15": 0.3, "M1_20": 0.4, "M1_25": 0.5, "M1_30": 0.6, 
            "M1_35": 0.7, "M1_40": 0.8, "M1_45": 0.8, "M1_50": 0.8, "M1_55": 0.8, "M1_60": 0.8, 
            "M1_65": 1.0, "M1_70": 1.0, "M1_75": 1.0, "M1_80": 1.0, "M1_85": 1.0, "M1_90": 1.0, "M1_95": 1.0}
    
    # PDF dictionary
    PDFD ={"M3_5": 5,"M3_10": 10,"M3_15": 15,"M3_20": 20,"M3_25": 25,"M3_30": 30,"M3_35": 35,"M3_40": 40,"M3_45": 45,"M3_50": 50,
           "M3_55": 55,"M3_60": 60,"M3_65": 65,"M3_70": 70,"M3_75": 75,"M3_80": 80,"M3_85": 85,"M3_90": 90,"M3_95": 95,"M4_5": 5,
           "M4_10": 10,"M4_15": 15,"M4_20": 20,"M4_25": 25,"M4_30": 30,"M4_35": 35,"M4_40": 40,"M4_45": 45,"M4_50": 50,"M4_55": 55,
           "M4_60": 60,"M4_65": 65,"M4_70": 70,"M4_75": 75,"M4_80": 80,"M4_85": 85,"M4_90": 90,"M4_95": 95,"M3M4_5": 5,"M3M4_10": 10,
           "M3M4_15": 15,"M3M4_20": 20,"M3M4_25": 25,"M3M4_30": 30,"M3M4_35": 35,"M3M4_40": 40,"M3M4_45": 45,"M3M4_50": 50,"M3M4_55": 55,
           "M3M4_60": 60,"M3M4_65": 65,"M3M4_70": 70,"M3M4_75": 75,"M3M4_80": 80,"M3M4_85": 85,"M3M4_90": 90,"M3M4_95": 95}
    
    # PCD dictionary
    PCD = {"M1_5":5,"M1_10":10,"M1_15":15,"M1_20":20,"M1_25":25,"M1_30":30,"M1_35":35,"M1_40":40,"M1_45":45,
           "M1_50":50,"M1_55":55,"M1_60":60,"M1_65":65,"M1_70":70,"M1_75":75,"M1_80":80,"M1_85":85,"M1_90":90,
           "M1_95":95,"M2_5":5,"M2_10":10,"M2_15":15,"M2_20":20,"M2_25":25,"M2_30":30,"M2_35":35,"M2_40":40,
           "M2_45":45,"M2_50":50,"M2_55":55,"M2_60":60,"M2_65":65,"M2_70":70,"M2_75":75,"M2_80":80,"M2_85":85,
           "M2_90":90,"M2_95":95,"M1M2_5":5,"M1M2_10":10,"M1M2_15":15,"M1M2_20":20,"M1M2_25":25,"M1M2_30":30,
           "M1M2_35":35,"M1M2_40":40,"M1M2_45":45,"M1M2_50":50,"M1M2_55":55,"M1M2_60":60,"M1M2_65":65,"M1M2_70":70,
           "M1M2_75":75,"M1M2_80":80,"M1M2_85":85,"M1M2_90":90,"M1M2_95":95}
    
    DF = pd.DataFrame(columns=Columns)
    DF["fueltype"] = [x for x in GFuelType]
    DF["elev"] = Elevation
    DF["ps"] = PS
    DF["saz"] = SAZ
    DF["time"] = np.zeros(len(GFuelType)).astype(int) + 20
    DF["pattern"] = np.full(len(GFuelType), np.nan)
    DF["lat"] = np.zeros(len(GFuelType)) + 51.621244
    DF["lon"] = np.zeros(len(GFuelType)).astype(int) - 115.608378
    
    # If no Curing file (or all NaN) check special cases for grass type O1 (default cur = 60)
    if np.sum(np.isnan(Curing)) == len(Curing):
        DF["cur"][DF.fueltype == "O1a"] = 60.0
        DF["cur"][DF.fueltype == "O1b"] = 60.0
        
    # Populate gfl
    for i in GFLD.keys():
        DF["gfl"][DF.fueltype == i] = GFLD[i]
        
    # Populate pdf
    for i in PDFD.keys():
        DF["pdf"][DF.fueltype == i] = PDFD[i]
    
    # Populate pc
    for i in PCD.keys():
        DF["pc"][DF.fueltype == i] = PCD[i]
    
    
    filename = os.path.join(InFolder, "Data.csv")
    print(filename)
    DF.to_csv(path_or_buf=filename, index=False, index_label=False, header=True)
    
    return DF

# Main function 
def GenDataFile(InFolder):
    FBPlookup = os.path.join(InFolder, "fbp_lookup_table.csv")
    FBPDict, ColorsDict =  Dictionary(FBPlookup)
    
    FGrid = os.path.join(InFolder, "Forest.asc")
    GFuelTypeN, GFuelType, Rows, Cols, CellSide = ForestGrid(FGrid, FBPDict)
    
    NCells = len(GFuelType)
    Elevation, SAZ, PS, Curing = DataGrids(InFolder, NCells)
    GenerateDat(GFuelType, Elevation, PS, SAZ, Curing, InFolder)