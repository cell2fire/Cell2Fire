# Was called Cell2Fire.py; now called pyCell2Fire.py
# This seems to be superceded by C++ code and not used (DLW June 2020)
# coding: utf-8
__version__ = "2.0"
__author__ = "Cristobal Pais, David Woodruff"
__maintainer__ = "Jaime Carrasco, Cristobal Pais, David Woodruff"
__status__ = "Alpha Operational"

# Importations
import os
import platform
import glob
import shutil
import numpy.random as npr
import numpy as np
import pandas as pd
from itertools import repeat
import time
import ctypes
import pickle
#from Cell2Fire.ParseInputs import ParseInputs, Init, InitCells, InitForest
from Cell2Fire.ParseInputs import ParseInputs, InitCells

raise RuntimeError("Cell2Fire.py imported, but that doesn't make sense.")

# Shared library .so (CP: Careful with Windows vs UNIX)
sonames = ["FBPfunc5Unix.so", "FBPfunc5Win.so", "FBPfunc5MAC.so"]
OS = platform.system()
if OS == "Windows":
    soname = sonames[1]
elif OS == "Linux":
    soname = sonames[0]
elif OS == "Darwin":
    soname = sonames[2]
try:
    lib_path = os.path.join(os.getcwd(), 'Cell2Fire', soname)
    lib = ctypes.cdll.LoadLibrary(lib_path)    
except:
    raise RuntimeError("Could not load the library=" + lib_path)
print("Loaded the library=" + lib_path)
    

    
    

# General Utils
def CSVGrid(rows, cols, AvailCells, HarvestedCells, 
            NonBurnableCells, plotnumber, GridPath):
    status = np.ones(rows * cols).astype(int)
    if len(AvailCells) > 0:
        status[list(AvailCells) - np.ones(len(AvailCells)).astype(int)] = 0
    if len(HarvestedCells) > 0:
        status[list(HarvestedCells) - np.ones(len(HarvestedCells)).astype(int)] = 2
    if len(NonBurnableCells) > 0:
        status[list(NonBurnableCells) - np.ones(len(NonBurnableCells)).astype(int)] = 0
    
    if plotnumber < 10:
        plotnumber = "0" + str(plotnumber)
    else:
        plotnumber = str(plotnumber)
        
    fileName = GridPath + "/ForestGrid" + plotnumber + ".txt"
    np.savetxt(fileName, status.reshape(rows, cols).astype(int), delimiter=',', fmt='%i')

def save_obj(obj, name, OutFolder, Sim, noOutput):
    if not os.path.exists(OutFolder + "/Trajectories"):
        if noOutput is False:
            print("Creating a new, empty folder =", OutFolder + "/Trajectories")
        os.makedirs(OutFolder + "/Trajectories")
    with open(OutFolder + '/Trajectories/'+ name + '_'+str(Sim)+'.pkl', 'wb+') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        
    

# Main class with all the simulation scheme   (NOT USED? checked June 2020)
class Cell2FireObj(object):
    # Initializer
    def __init__(self,
                 InFolder,
                 OutFolder,
                 HCells=set(),
                 BCells=set(),
                 OutMessages=False,
                 SaveMem=False,
                 trajectories=False,
                 nooutput=False,
                 MinutesPerWP=60.0,
                 verbose=False,
                 Max_Fire_Periods=100000,
                 TotalYears=10,
                 TotalSims=1,
                 FirePeriodLen=1.0,
                 Ignitions=True,
                 WeatherOpt="rows",
                 combine=False,
                 GenData=False,
                 FinalPlot=False,
                 gridsFreq=-1,
                 gridsStep=60,
                 IgnitionRad=0,
                 seed=0,
                 ROS_Threshold=1e-3,
                 HFactor=1.0,
                 FFactor=1.0,
                 BFactor=1.0,
                 EFactor=1.0,
                 PromTuned=True,
                 ROSThreshold=1e-3,
                 HFIThreshold=1e-3,
                 ROSCV=0.0,
                 Stats=False,
                 observationSpace=1,
                 plotStep=-1,
                 plotFreq=60,
                 stats=False,
                 heuristic=0,
                 msgHeur="",
                 GASelection=False):
        
        # Initialization info
        print("Initializing the forest object from Cell2Fire class...")
        
        # Keep arguments inside the class object (self)
        self._InFolder = InFolder
        self._OutFolder = OutFolder
        self._HCells = HCells
        self._BCells = BCells
        self._OutMessages = OutMessages
        self._SaveMem = SaveMem
        self._trajectories = trajectories
        self._nooutput = nooutput
        self._MinutesPerWP = MinutesPerWP
        self._verbose = verbose
        self._Max_Fire_Periods = Max_Fire_Periods
        self._TotalYears = TotalYears
        self._TotalSims = TotalSims
        self._FirePeriodLen = FirePeriodLen
        self._Ignitions = Ignitions
        self._WeatherOpt = WeatherOpt
        self._combine = combine
        self._GenData = GenData
        self._FinalPlot = FinalPlot
        self._IgnitionRad = IgnitionRad
        self._seed = seed
        self._ROS_Threshold = ROS_Threshold
        self._HFactor = HFactor
        self._FFactor = FFactor
        self._BFactor =BFactor
        self._EFactor = EFactor
        self._PromTuned = PromTuned
        self._ROSThreshold = ROSThreshold
        self._HFIThreshold = HFIThreshold
        self._ROSCV = ROSCV
        self._previous_action = 0
        self._Stats = Stats
        self._observationSpace = observationSpace
        self._plotStep = plotStep
        self._plotFreq = plotFreq
        self._gridsFreq = gridsFreq
        self._gridsStep = gridsStep
        self._stats = stats
        self._heuristic = heuristic
        self._msgHeur = msgHeur
        self._GASelection = GASelection

        print ("DLW debug 000, noout, verb", self._nooutput, self._verbose)
        
        # Step -1: FBP
        ##########################################################################################################
        #                                    FBP Coefficients and types
        ##########################################################################################################
        # FType coefficients and data from FBP library
        listlen = 18
        ListOfCoefs = listlen * CellsFBP.fuel_coeffs
        self._coef_ptr = ListOfCoefs()
        lib.setup_const(self._coef_ptr)
        self._FTypes2 = {"m1": 0, "m2": 1, "m3": 2, "m4": 3,
                   "c1": 4, "c2": 5, "c3": 6, "c4": 7, "c5": 8, "c6": 9, "c7": 10,
                   "d1": 11, "s1": 12, "s2": 13, "s3": 14, "o1a": 15, "o1b": 16, "d2": 17}

        ##########################################################################################################
        #                                    Init main inputs
        ##########################################################################################################
        
        # Generate Data.dat if needed
        dataName = os.path.join(self._InFolder, "Data.dat")
        if self._GenData is True or os.path.isfile(dataName) is False:
            print("Generating Data.dat File")
            if self._InFolder is not None:
                DataGenerator.GenDataFile(self._InFolder)
            else:
                DataGenerator.GenDataFile("")

        # Data
        if self._InFolder is not None:
            filename = os.path.join(self._InFolder, "Data.dat")
            if os.path.isfile(filename) == False:
                print("Data.dat file does not exists, generating it from files inside", self._InFolder)
                DataGenerator.GenDataFile(self._InFolder)

        else:
            filename = "Data.dat"
            if os.path.isfile(filename) is False:
                print("Data.dat file does not exists, generating it from files inside current directory")
                DataGenerator.GenDataFile("")

        # Folder existence
        if not os.path.exists(self._OutFolder):
            print("Creating a new, empty folder =", self._OutFolder)
            #shutil.rmtree(OutFolder)
            os.makedirs(self._OutFolder)

        print ("DLW debug, noout, verb", self._nooutput, self._verbose)
        # No output dominates verbose
        if self._nooutput:
            self._verbose = False

        # Random seed
        if self._verbose:
            print("Setting initial pseudo-random number stream seed to ", str(self._seed))
        if self._seed is not None:
            npr.seed(int(self._seed))

        # If we have a folder with an instance read files
        if self._InFolder is not None:
            ForestFile = os.path.join(self._InFolder, "Forest.asc")
            FBPlookup = os.path.join(self._InFolder, "fbp_lookup_table.csv")
           
            if self._Ignitions == True:
                self._Ignitions = os.path.join(self._InFolder, "IgnitionPoints.csv")

        # Fire Period length
        print("-----------------------------------------------------------------------------------")
        if self._FirePeriodLen > self._MinutesPerWP:
            print("Fire Period Length > Weather Period: setting Fire Period Length = Weather Period")
            self._FirePeriodLen = self._MinutesPerWP
        print("Fire Period Length for ROS computations [min]: ", self._FirePeriodLen)

        # Harvested Cells (initial)
        if len(self._HCells) > 0:
            initHarvested = np.asarray([i for i in self._HCells])
            print("Initial harvested cells:", initHarvested)
        else:
            initHarvested = []

        if self._WeatherOpt == 'multiple' or self._WeatherOpt == 'random':
            self._WFolder = self._InFolder + "Weathers"
            self._Wfiles = os.listdir(self._WFolder)

        print("-----------------------------------------------------------------------------------")
        ##########################################################################################################

    
        ##########################################################################################################
        #                                    Read Data Frame & Fuel types
        ##########################################################################################################
        # Read DataFrame
        self._DF = FBP2PY.inputData(filename)
        if self._GenData is False:
            Elevation, SAZ, PS = ReadDataPrometheus.DataGrids(self._InFolder, len(self._DF))
            self._DF["elev"] = Elevation
            self._DF["saz"] = SAZ
            self._DF["ps"] = PS
            self._DF["time"] = np.zeros(self._DF.shape[0]) + 20
        if self._verbose is True:
            print("DF:", self._DF)

        # Getting FType for each cell from data 
        self._FTypeCells2 = np.array(self._DF['fueltype'], dtype=object)

        # Periods and Initialize simulation number
        self._max_weeks = 12  # weeks
        self._Sim = 1
        ##########################################################################################################
        #                                           
        ##########################################################################################################


        ##########################################################################################################
        #                                          Global Forest Data
        ##########################################################################################################
        # Read Forest
        if self._nooutput is False:
            print("\n----------------- Forest Data -----------------")

        # Obtain FBP and Color dictionaries from FBP file, read the ForestGrid file
        FBPDict, ColorsDict = ReadDataPrometheus.Dictionary(FBPlookup)
        GForestN, GForestType, Rows, Cols, AdjCells, CoordCells, CellSide = ReadDataPrometheus.ForestGrid(ForestFile,
                                                                                                          FBPDict)

        # Number of cells
        self._NCells = Rows * Cols
        self._Rows = Rows
        self._Cols = Cols
        self._AdjCells = AdjCells
        self._CoordCells = CoordCells
        self._GForestType = GForestType

        # Initialize main cells inputs
        FTypeCells, StatusCells, RealCells, Colors = InitCells(self._NCells, self._FTypes2, 
                                                               ColorsDict, GForestType, GForestN)

        # if Initially harvested cells, update status
        if self._HCells != None:
            for i in initHarvested:
                StatusCells[i-1] = 4
                
        self._StatusCells = StatusCells
        self._OrigStatusCells = StatusCells.copy()
        self._Colors = Colors
        self._FTypeCells = FTypeCells
        self._RealCells = RealCells

        ###################################################################
        # Print information for debug
        # if verbose == True:
        #    print("\nCoord Cells:", CoordCells)
        #    print("\nCells GForestType:", GForestType)
        #    print("\nFTypeCells:", FTypeCells)
        #    print("\nFTypeCells2:", FTypeCells2)
        #    print("\nlist of coef:", ListOfCoefs)
        #    print("\nRealCells:", RealCells)
        #    print("\nStatus Cells:", StatusCells)
        #    print("\nColors:", Colors)
        #    print("\nCells GForestN:", GForestN)
        #    print("\nCoef pointer:", coef_ptr)
        #    print("\nlen DF fueltype:", DF['fueltype'].shape[0])
        #    print("\nFBPDict:", FBPDict)
        #    print("\nColorsDict:",ColorsDict)
        #    print("\nAdj cells:",AdjCells)
        #    print("\nCell side:", CellSide)
        ###################################################################

        # Releasing memory
        del GForestN
        del ColorsDict

        # Cell instance data (explicit for the moment, final version may read it from a source file)
        self._VolCells, self._AgeCells = ReadDataPrometheus.CellsInfo(ForestFile, self._NCells)
        self._AreaCells = CellSide * CellSide
        self._CellSide = CellSide
        self._PerimeterCells = CellSide * 4

        if self._nooutput is False:
            print("Rows:", self._Rows, "Cols:", self._Cols, "NCells:", self._NCells)
            print("------------ End read forest data -------------")

        ##########################################################################################################
        #                               Ignition, Weather, Plot, Lightning Options/Data
        ##########################################################################################################    
        self._weatherperiod = 0
        print("\n XXXX debug about to call Init XXXXX \n")
        self._Ignitions, self._Weather_Obj, self._Plotter, self._DF = Init(self._Ignitions, 
                                                                           self._WeatherOpt, 
                                                                           self._plotFreq,
                                                                           self._gridsFreq,
                                                                           self._OutFolder, 
                                                                           self._DF,
                                                                           self._InFolder,
                                                                           self._verbose, 
                                                                           self._nooutput)

        print("Current Ignitions:", self._Ignitions)
        print("Ignition Radius:", self._IgnitionRad)

        # if ignition radius, then generate the sets
        if self._IgnitionRad > 0:
            self._IgnitionSets = {}
            auxSet = set()
            auxIg = 1

            for i in self._Ignitions.values():
                # initialize aux set
                auxSet = set()

                # Debugging ignition year and given ignition cell
                print("Ignition Year", auxIg, ":", i)

                if self._IgnitionRad == 1:
                    self._IgnitionSets[auxIg] = set([a[0] for a in AdjCells[i-1].values() if a != None])
                    self._IgnitionSets[auxIg].add(i)
                    #print("Ignition sets:", self._IgnitionSets[1], "size:", len(self._IgnitionSets[1]))
                    #auxIg += 1

                if self._IgnitionRad > 1:
                    # Initial ignition set (first year for 1 degree)
                    self._IgnitionSets[auxIg] = set([a[0] for a in AdjCells[i-1].values() if a != None])
                    auxR = 1
                    auxSet.add(i)
                    #print("Ignition Set (radius = 1):", IgnitionSets[auxIg])

                    # loop over radius of adjacents
                    while auxR < IgnitionRad:
                        for c in self._IgnitionSets[auxIg].copy():

                            # Populate Aux Set
                            auxSet |= set(a[0] for a in AdjCells[c-1].values() if a != None)
                            #print("Aux Set:", auxSet, "AuxR:", auxR, "IgnitionRad:", IgnitionRad, "AuxIg:", auxIg)


                        # Save aux set as Ignition Set
                        self._IgnitionSets[auxIg] = auxSet
                        #print("IgnitionSet:", IgnitionSets[auxIg], "AuxIg:", auxIg)
                        auxR += 1
                if self._verbose:
                    print("Ignition set radius ge 2:", self._IgnitionSets[auxIg], 
                          "size:", len(self._IgnitionSets[auxIg]))

                # Next iter (next year)
                auxIg += 1

    ##############################
    #                            #
    #          Methods           #
    #                            #
    ##############################
                
    # Init Sim (reset)
    def InitSim(self):    
        # Global Parameters (reseting)
        self._ep_reward = 0
        self._Year = 1
        self._max_weatherperiod = 0
        self._max_plotnumber = 1
        self._weatherperiod = 0
        self._NoIgnition = None
        self._MessagesSent = None
        self._plotnumber = 0
        self._gridnumber = 0
        self._Plotter = Plot.Plot()
        self._StatusCells = self._OrigStatusCells.copy()
        self._FireProgressMatrix_Prev = np.zeros(self._NCells)
        self._FProgressMatrix = np.zeros(self._NCells)
        self._ROSMatrix = np.zeros(self._NCells)
        self._GridPath = ""
        self._PlotPath = ""
        
        # New trajectories logic
        if self._trajectories:
            self._FI = {}
            self._FS = {}
            self._HPeriod = 0
            self._FPeriod = 1

        # Reset DF if not initial sim
        if self._Sim != 1:
            # If multiple weather, pick the next one for the next simulation
            if self._WeatherOpt == 'multiple':
                self._selWeather = str(self._Wfiles[self._Sim-1])
                print("Selected weather file:", self._selWeather)
                self._Weather_Obj = WeatherFBP.Weather(self._InFolder + "Weathers/" +self._selWeather)
            
            # If random weather, pick a new random one for the next simulation 
            if self._WeatherOpt == 'random':
                self._selWeather = str(np.random.choice(self._Wfiles))
                print("Selected weather file:", self._selWeather)
                self._Weather_Obj = WeatherFBP.Weather(self._InFolder + "Weathers/" + self._selWeather)
            
            # Read original dataframe
            self._DF = self._Weather_Obj.update_Weather_FBP(self._DF, self._WeatherOpt, self._weatherperiod)

        # Current fire period in a year (also records last fire period)
        self._Fire_Period = np.zeros(self._TotalYears).astype(int)

        # BurntP is an array (by period) of the array of cells burned in the period (migrating to dict)
        self._BurntP = {}  

        # Record current clock for measuring running time (including data reading)
        self._Initial_Time = time.time()

        ##########################################################################################################
        #                               Ignition, Weather, Plot, Lightning Options/Data
        ##########################################################################################################    
    
        # Plot folders
        if (self._plotStep > 0 and self._plotFreq > 0) or self._FinalPlot == True:
            self._PlotPath = os.path.join(self._OutFolder, "Plots")
            if not os.path.exists(self._PlotPath):
                os.makedirs(self._PlotPath)
            
            # Initial Plot
            self.InitPlot()
    
        # Generate grids folders
        if self._gridsStep > 0 and self._gridsFreq > 0:
            self._GridPath = os.path.join(self._OutFolder, "Grids/Grids" + str(self._Sim))
            if not os.path.exists(self._GridPath):
                os.makedirs(self._GridPath)

        # Generate messages folders 
        if self._OutMessages == True:
            #MessagesPath = os.path.join(OutFolder, "Messages/Messages" + str(Sim))
            self._MessagesPath = os.path.join(self._OutFolder, "Messages")
            if not os.path.exists(self._MessagesPath):
                os.makedirs(self._MessagesPath)
                
        
        # Generate stats folder
        if self._Stats:
            self._StatsPath = os.path.join(self._OutFolder, "Stats")
            if not os.path.exists(self._StatsPath):
                os.makedirs(self._StatsPath)

        # Maximum fire periods validity
        if self._WeatherOpt == "rows" or self._WeatherOpt == "random" or self._WeatherOpt == "multiple":
            MaxFP = int(self._MinutesPerWP / self._FirePeriodLen) * (self._Weather_Obj.rows)
            if self._Max_Fire_Periods > MaxFP:
                self._Max_Fire_Periods = MaxFP - 1
                if self._verbose == True:
                    print("Maximum fire periods are set to:", self._Max_Fire_Periods,
                          "based on the weather file, Fire Period Length, and Minutes per WP")
            else:
                pass #print("Maximum fire periods:", self._Max_Fire_Periods)

        # Number of years and Ignitions
        if self._Ignitions != "":
            IgYears = len(self._Ignitions.keys())
            if self._TotalYears > IgYears:
                print("Total Years set to", IgYears, "based on Ignitions points provided")
                self._TotalYears = IgYears

                
        
        ##########################################################################################################
        #                                   Cells Obj Dictionary and Main Sets
        ##########################################################################################################    
        # Cells Dictionary: Will have active cells (burnin/burnt and potentially active ones - getting messages)
        self._Cells_Obj = {}

        # Sets (Available cells, burning cells, burnt cells and harvest cells: starting from array and cast later)
        self._AvailCells_Set = set(np.where(self._StatusCells != 4)[0] + 1)
        self._NonBurnableCells_Set = set(np.where(self._StatusCells == 4)[0] + 1)
        self._BurningCells_Set = set()
        self._BurntCells_Set = self._BCells.copy()
        self._HarvestCells_Set = self._HCells.copy()

        # Printing info about the cells' status
        if self._verbose:
            print("Available Cells:", self._AvailCells_Set)
            print("Non Burnable Cells:", self._NonBurnableCells_Set)
            print("Burning Cells:", self._BurningCells_Set)
            print("Burnt Cells:", self._BurntCells_Set)
            print("Harvest Cells:", self._HarvestCells_Set)
        
        return self.getState
        
    
    # Ignition
    def RunIgnition(self):
        ##########################################################################################################
        #                   Step 1: Lightning/Ignition loop in order to find the first week with fire
        ##########################################################################################################
        # Loop for finding next fire week
        # Printing information if verbose is true
        if self._verbose:
            print("\n------------------------------------ Current Year:", 
                  self._Year," ------------------------------------")
            print("---------------------- Step 1: Ignition ----------------------")

        # Save Memory mode: Burnt cells are deleted from Cells_Obj dictionary (Inactive)
        if self._SaveMem:
            if self._verbose == True:
                print("Deleting burnt cells from Cells_Obj dict...")
            for c in self._BurntCells_Set:
                thrash = self._Cells_Obj.pop(c - 1, None)
                if self._verbose == True and thrash != None:
                    print("Deleted:", c)

        ##########################################################################################################
        #                                      Ignite the cell (or not)
        ##########################################################################################################
        aux = 0
        loops = 0
        NoIgnition = False

        # Select the "burning" cell
        # If no ignition points, take one cell at random
        if self._Ignitions == "":
            while True:
                aux = int(npr.uniform(0, 1) * self._NCells)

                #print("aux:", aux)
                print("Selected Cell (at random):", self._RealCells[aux])

                # If cell is available (global properties)
                if StatusCells[aux] != 4 and (aux + 1) not in BurntCells_Set:

                    # Initialize cell if needed
                    if aux not in self._Cells_Obj.keys():
                        self._Cells_Obj[aux] = self.InitCell(aux + 1)

                        # If the cell is available and burnable (from object properties)
                        if self._Cells_Obj[aux].get_Status() == "Available" and self._Cells_Obj[aux].FType != 0:
                            if self._Cells_Obj[aux].ignition(self._Fire_Period[Year - 1], 
                                                             self._Year, 
                                                             self._Ignitions, 
                                                             self._DF, 
                                                             self._coef_ptr,
                                                             self._ROS_Threshold, 
                                                             self._HFactor,
                                                             self._HFIThreshold, 
                                                             self._verbose):
          
                                # Printing info about ignitions
                                if self._verbose == True:
                                    print("Cell ", self._Cells_Obj[aux].ID, " Ignites")
                                    print("Cell ", self._Cells_Obj[aux].ID, 
                                          " Status: ", self._Cells_Obj[aux].get_Status())

                                # We get the ignition point, break
                                break

                    # Updating parameters inside the loop
                    loops += 1

                    # Maximum number of iterations
                    if loops > self._NCells:
                        NoIgnition = True
                        break

        # If we have specific ignitions
        if self._Ignitions != "":
            # Check if we have ignition radius and pick one ignition point at random from the set
            if self._IgnitionRad > 0:
                # Pick any at random and set Ignitions[Years] with that cell
                self._Ignitions[self._Year] = npr.choice(list(self._IgnitionSets[self._Year]))
                if self._nooutput is False:
                    print("Selected ignition point for Year", self._Year,
                          ":", self._Ignitions[self._Year])

            # Check ignition points are not already burnt and the cell is burnable
            if self._Ignitions[self._Year] not in self._BurntCells_Set \
                and self._StatusCells[self._Ignitions[self._Year] - 1] != 4:

                # Initialize it if needed
                if (self._Ignitions[self._Year] - 1) not in self._Cells_Obj.keys():
                    self._Cells_Obj[self._Ignitions[self._Year] - 1] = self.InitCell(self._Ignitions[self._Year])
                    
                # If not available, no ignition
                if self._Cells_Obj[self._Ignitions[self._Year] - 1].get_Status() != "Available" or self._Cells_Obj[self._Ignitions[self._Year] - 1].FType == 0:
                    NoIgnition = True

                # If available, ignites
                if self._Cells_Obj[self._Ignitions[self._Year] - 1].get_Status() == "Available" and self._Cells_Obj[self._Ignitions[self._Year] - 1].FType != 0:
                    if self._Cells_Obj[self._Ignitions[self._Year] - 1].ignition(self._Fire_Period[self._Year - 1], self._Year, 
                                                                                 self._Ignitions, self._DF, self._coef_ptr,
                                                                                 self._ROS_Threshold, self._HFactor,
                                                                                 self._HFIThreshold, self._verbose):

                        # Printing info about ignitions
                        if self._verbose:
                            print("Cell", self._Cells_Obj[self._Ignitions[self._Year] - 1].ID, "Ignites")
                            print("Cell", self._Cells_Obj[self._Ignitions[self._Year] - 1].ID, 
                                  "Status:", self._Cells_Obj[self._Ignitions[self._Year] -1].get_Status())

            # Otherwise, no ignitions (already burnt or non burnable)
            else:
                NoIgnition = True
                if self._nooutput == False:
                    print("No ignition during year", self._Year,
                          ", cell", self._Ignitions[self._Year], "is already burnt or non-burnable type")

        # If ignition occurs, we update the forest status
        if NoIgnition is False:

            # Updating AvailCells and BurningCells sets
            if self._Ignitions == "":
                NewID = self._Cells_Obj[aux].ID
                Aux_set = set([NewID])
                self._BurningCells_Set = self._BurningCells_Set.union(Aux_set)
                self._AvailCells_Set = self._AvailCells_Set.difference(self._BurningCells_Set)
                if self._trajectories:
                    self._FI[(NewID, self._FPeriod, self._Sim)] = 1

            else:
                NewID = self._Cells_Obj[self._Ignitions[self._Year] - 1].ID
                Aux_set = set([self._Ignitions[self._Year]])
                self._BurningCells_Set = self._BurningCells_Set.union(Aux_set)
                self._AvailCells_Set = self._AvailCells_Set.difference(self._BurningCells_Set)
                self._BurntCells_Set = self._BurntCells_Set.union(Aux_set)
                if self._trajectories:
                    self._FI[(NewID, self._FPeriod, self._Sim)] = 1

        # Printing information about the forest
        if self._verbose:
            print("Available cells:", self._AvailCells_Set)
            print("Non Burnable Cells:", self._NonBurnableCells_Set)
            print("Burning cells:", self._BurningCells_Set)
            print("Harvest cells:", self._HarvestCells_Set)
            print("Burnt cells (including burning):", self._BurntCells_Set)

        ##########################################################################################################
        #                                      Next period t+1
        ##########################################################################################################
        
        # Update weather (consistently)
        self.updateWeather()    
            
        # Print info
        if self._verbose:
            print("Fire Period Starts:", self._Fire_Period[self._Year - 1], "\n")
            self._Weather_Obj.print_info(self._weatherperiod)
            print("DF:", self._DF[["fueltype", "ws", "waz", "ffmc", "bui", "saz", "elev", "ps"]])

            if self._WeatherOpt == 'constant':
                print("(NOTE: current weather is not used for ROS with constant option)")

            # End of the ignition step
            print("\nNext Fire Period:", self._Fire_Period[self._Year - 1])

        # If no ignition occurs, go to next year (no multiple ignitions per year, only one)
        if NoIgnition:
            if self._verbose:
                print("No ignition in year", self._Year)
            # Next year, reset the week
            self._Year += 1
            
            
        
        # Return No Ignition flag
        return NoIgnition
                    
    
    # Send messages (1 step and potential repetition flag)
    def SendMessages(self):
        # Ending condition and message to user
        if self._Fire_Period[self._Year - 1] == self._Max_Fire_Periods - 1 and self._nooutput == False:
            print("\n *** WARNING!!!! About to hit Max_Fire_Periods=", self._Max_Fire_Periods, " ***\n\n")

        ##################################################################################################
        #                                      Step 2: Send messages
        ##################################################################################################
        # Initial Parameters
        self._MessagesSent = False
        SendMessageList = {}          

        # Printing info before sending messages
        if self._verbose:
            print(
                "\n---------------------- Step 2: Sending Messages from Ignition ----------------------")
            print("Current Fire Period:", self._Fire_Period[self._Year - 1])
            print("Harvested Cels:", self._HarvestCells_Set)
            print("Burning Cells:", self._BurningCells_Set)
            print("Burnt Cells (should include burning):", self._BurntCells_Set)
            print(" -------------------- NEW CLEANING STEP ------------------------")

        '''
        Cleaning ROSAngleDir dictionaries based on the current burning cells
        '''

        # For all the cells already initialized (SIMPLE Embarrasingly Parallel) we clean
        # angles if nb cells are not available
        for cell in self._Cells_Obj.keys():
            # Check those cells with at least one possible neighbor to send fire
            if len(self._Cells_Obj[cell].ROSAngleDir) > 0:

                # Delete adjacent cells that are not available
                for angle in self._Cells_Obj[cell].angle_to_nb:
                    nb = self._Cells_Obj[cell].angle_to_nb[angle]

                    if nb not in self._AvailCells_Set and angle in self._Cells_Obj[cell].ROSAngleDir:
                        if self._verbose == True:
                            print("Cell", cell + 1, ": clearing ROSAngleDir")

                        self._Cells_Obj[cell].ROSAngleDir.pop(angle)

        if self._verbose:
            print("----------------------------------------------------------------")

        ##################################################################################################
        #                             Core: Sending messages (to be parallelized)
        ##################################################################################################

        # RepeatFire
        self._RepeatFire = False
        self._BurnedOutList = []

        ##################################################################################################
        #                                         Parallel Zone
        ##################################################################################################

        # Burning cells loop: sending messages (Embarrasingly parallel?: CP: should be)
        # Each burning cell updates its fire progress and (if needed) populates their message
        # dictionary {ID:[list with int]}
        for cell in self._BurningCells_Set:
            # Info of fire fields
            if self._verbose == True:
                print("\nCell object new fields")
                print("ID:", self._Cells_Obj[cell - 1].ID)
                print("FireProgress:", self._Cells_Obj[cell - 1].FireProgress)
                print("AngleDict:", self._Cells_Obj[cell - 1].AngleDict)
                print("ROSAngleDir:", self._Cells_Obj[cell - 1].ROSAngleDir)
                print("DistToCenter:", self._Cells_Obj[cell - 1].DistToCenter)
                print("angle_to_nb:", self._Cells_Obj[cell - 1].angle_to_nb)


            # Check if the burning cell can send more messages or not (based on ROSAngleDir)
            # If no angle is available, no more messages
            if len(self._Cells_Obj[cell - 1].ROSAngleDir) > 0:
                # Cell can still send messages (info to user) based on nb conditions
                if self._verbose == True:
                    print("Cell", cell, "can still send messages to neighbors\n")

                Aux_List = self._Cells_Obj[cell - 1].manageFire(self._Fire_Period[self._Year - 1], 
                                                                self._AvailCells_Set,
                                                                self._verbose, 
                                                                self._DF, 
                                                                self._coef_ptr,
                                                                self._CoordCells, 
                                                                self._Cells_Obj, 
                                                                self._ROSCV,
                                                                self._HFactor,
                                                                self._FFactor,
                                                                self._BFactor,
                                                                self._EFactor,
                                                                self._ROSThreshold,
                                                                self._HFIThreshold,
                                                                self._PromTuned,
                                                                self._FirePeriodLen)

                
           
            # No more neighbors to send messages (empty list)
            else:
                if self._verbose == True:
                    print("\nCell", cell, "does not have any neighbor available for receiving messages")
                Aux_List = []

            # Print for Debug
            if self._verbose:
                print("\nAux list:", Aux_List)

            # Cases
            # 1) If messages and not empty, populate message list
            if len(Aux_List) > 0 and Aux_List[0] != "True":
                if self._verbose:
                    print("\nList is not empty")
                self._MessagesSent = True
                SendMessageList[self._Cells_Obj[cell - 1].ID] = Aux_List
                if self._trajectories:
                    for i in Aux_List:
                        self._FS[(cell, i, self._FPeriod, self._Sim)] = self._Fire_Period[self._Year - 1]
                if self._verbose:
                    print("\nSendMessageList: ", SendMessageList)

            # 2) If message is True, then we update and repeat the fire
            if len(Aux_List) > 0 and Aux_List[0] == "True":
                if self._verbose:
                    print("\nFire is still alive and we may repeat if no other messages......")
                self._RepeatFire = True

            # 3) If empty list, cell is burnt and no messages are added
            if len(Aux_List) == 0:
                self._BurnedOutList.append(self._Cells_Obj[cell - 1].ID)
                if self._verbose:
                    print("\nMessage and Aux Lists are empty; adding to BurnedOutList")
        # End burn loop (parallel zone)

        ##################################################################################################
        #
        ##################################################################################################

        # Update burning cells
        self._BurningCells_Set.difference(set(self._BurnedOutList))

        # Check the conditions for repeating, stopping, etc.
        # Global message list
        self._Global_Message_Aux = [val for sublist in SendMessageList.values() for val in sublist]
        if self._verbose:
            print("Global_Message_Aux:", self._Global_Message_Aux)
            print("RepeatFire:", self._RepeatFire)

        return SendMessageList
        
    
    # Get messages (1 step always)
    def GetMessages(self, SendMessageList):
        ##################################################################################################
        #                                      Step 3: Receive messages
        ##################################################################################################

        # Global list with messages (all messages)
        Global_Message_List = [val for sublist in SendMessageList.values() for val in sublist]
        Global_Message_List.sort()

        if self._verbose:
            print("Lists of messages per Cell:", SendMessageList)
            print("Global Message Lists:", Global_Message_List)
            print("We have at least one message:", self._MessagesSent)

        ##################################################################################################
        #                                         Parallel Zone
        ##################################################################################################
        # Initialize cell (getting a message) if needed
        for bc in set(Global_Message_List):
            if (bc - 1) not in self._Cells_Obj.keys() and bc not in self._BurntCells_Set:
                self._Cells_Obj[bc - 1] = self.InitCell(bc)
                
        
        ##################################################################################################
        #
        ##################################################################################################

        # Releasing Memory
        del SendMessageList

        ##################################################################################################
        #                                      Receive messages dynamic
        ##################################################################################################
        # Printing information
        if self._verbose == True:
            print("\n---------------------- Step 3: Receiving and processing messages from Ignition ----------------------")

        # Initializing Parameters
        BurntList = []
        NMessages = {}
        GotMsg_Set = set(Global_Message_List)

        # Check which cells got messages and how many of them
        if self._verbose == True:
            print("Cells receiving messages: " + str(GotMsg_Set))

        # Number of messages by each cell
        # for i in range(1, NCells+1):  migrating to GotMsg_Set
        for i in GotMsg_Set:
            NMessages[i - 1] = Global_Message_List.count(i)
            if self._verbose == True:
                print("Cell", i, "receives", NMessages[i - 1], "messages")

        # Releasing Memory
        del Global_Message_List
        if self._verbose == True:
            print("\nCells status")

        ##################################################################################################
        #                                         Parallel Zone
        ##################################################################################################
        # Initialize cells getting messages (if needed)
        for bc in GotMsg_Set:
            if bc not in self._BurntCells_Set:
                if (bc - 1) not in self._Cells_Obj.keys():
                    self._Cells_Obj[bc - 1] = self.InitCell(bc)

                # Check if cell is burnt or not (since it gets a message)
                if self._Cells_Obj[bc - 1].FType != 0:
                    Check_Burnt = self._Cells_Obj[bc - 1].get_burned(self._Fire_Period[self._Year - 1],
                                                                     NMessages[bc - 1],
                                                                     self._Year, 
                                                                     self._verbose, 
                                                                     self._DF, 
                                                                     self._coef_ptr,
                                                                     self._ROS_Threshold, 
                                                                     self._HFactor, 
                                                                     self._FFactor, 
                                                                     self._BFactor)

                # Else, not burnt
                else:
                    Check_Burnt = False

                # Print out info w.r.t. status
                if self._verbose == True:
                    print("Cell", self._Cells_Obj[bc - 1].ID, "got burnt:", Check_Burnt)

                # If burnt, update Burnlist
                if Check_Burnt == True:
                    BurntList.append(self._Cells_Obj[bc - 1].ID)

        ##################################################################################################
        #
        ##################################################################################################

        if self._verbose == True:
            print("\nResults")
            print("Newly Burnt (and/or burning) List:", BurntList)

        # Update cells status (burnt or not burnt), Update AvailCells and BurntCells sets
        Aux_set = set(BurntList)  # newly burning
        self._BurntCells_Set = self._BurntCells_Set.union(Aux_set)
        self._BurntCells_Set = self._BurntCells_Set.union(set(self._BurnedOutList))
        self._BurningCells_Set = self._BurningCells_Set.union(Aux_set)
        self._AvailCells_Set = self._AvailCells_Set.difference(Aux_set)

        # Releasing Memory
        del Aux_set

        # Check current status 
        if self._verbose is True:
            print("Available cells:", self._AvailCells_Set)
            print("Non Burnable Cells:", self._NonBurnableCells_Set)
            print("Burning cells:", self._BurningCells_Set)
            print("Harvest cells:", self._HarvestCells_Set)
            print("Burnt and Burning cells:", self._BurntCells_Set) 
         
        # Update weather if needed based on Period lengths
        print("New Update of weather")
        self.updateWeather()
        print("self._weatherperiod:", self._weatherperiod)

    # Init harvested objects (useful for ploting and stats later on)
    def InitHarvested(self):
        # Check harvested cells that have not been initialized and do it
        for h in self._HarvestCells_Set:
            ID = h - 1
            if ID not in self._Cells_Obj.keys():
                self._Cells_Obj[ID] = self.InitCell(ID + 1)
                self._Cells_Obj[ID].Status = 3
                              
    
    # Results
    def Results(self):
        ##################################################################################################
        #                                       Step 4: Results
        ##################################################################################################         
        # End of the code for one sim, output files with statistics and plots (if asked)
        for br in self._BurntCells_Set:
            if (br - 1) in self._Cells_Obj.keys():
                self._Cells_Obj[br - 1].Status = 2
        for bn in self._BurningCells_Set:
            if (bn - 1) in self._Cells_Obj.keys():
                self._Cells_Obj[bn - 1].Status = 2

        # Print information 
        if self._nooutput is False:
            print("\n----------------------------- Results -----------------------------")
            
            # General results
            print("Total Available Cells:    ", len(self._AvailCells_Set), "- % of the Forest: ",
                  np.round(len(self._AvailCells_Set) / self._NCells * 100.0, 3), "%")
            print("Total Burnt Cells:        ", len(self._BurntCells_Set), "- % of the Forest: ",
                  np.round(len(self._BurntCells_Set) / self._NCells * 100.0, 3), "%")
            print("Total Non-Burnable Cells: ", len(self._NonBurnableCells_Set), "- % of the Forest: ",
                  np.round(len(self._NonBurnableCells_Set) / self._NCells * 100.0, 3), "%")
            print("Total Harvested Cells: ", len(self._HarvestCells_Set), "- % of the Forest: ",
                  np.round(len(self._HarvestCells_Set) / self._NCells * 100.0, 3), "%")
           
            # Statistics: Cells' status, Fire periods, start, end.
            if self._SaveMem is not True:
                print("\n" + "Cells status")
                for i in self._Cells_Obj.keys():
                    if self._Cells_Obj[i].get_Status() == "Burnt":
                        print("Cell", i + 1, "status:", self._Cells_Obj[i].get_Status(), "Year:",
                              self._Cells_Obj[i].FireStartsSeason,
                              ", Fire starts (fire period):", self._Cells_Obj[i].Firestarts)

            if self._SaveMem:
                for br in self._BurntCells_Set:
                    print("Cell", br, "status: Burnt")
                if self._verbose:
                    for av in self._AvailCells_Set:
                        print("Cell", av, "status: Available")

            # Total simulation time 
            Final_Time = time.time()  
            print("\nSimulation time:", np.round(Final_Time - self._Initial_Time, 3), " [s]")
            #print("Total simulation Time:", np.round(Final_Time - startT, 3), "[s]")

        # Check combine flag: if true, plots are combined with background
        if self._combine:
            for i in range(1, self._plotnumber):
                self._Plotter.Mix(self._OutFolder, i, self._Sim)

        # Messages
        if self._OutMessages:
            if self._verbose:
                print("\n--------------- Cell[i], Cell[j], hitPeriod, hitROS -------------")

            file = open(self._MessagesPath + "/MessagesFile"+str(self._Sim)+".txt", "w")
            # file.write("Cell[i]  Cell[j]  hitPeriod[min]  hitROS[m/min]\n") 
            for c in self._Cells_Obj.keys():
                for nb in self._Cells_Obj[c].FSCell.keys():
                    file.write(str(c + 1) + " " + str(nb) + " " + str(self._Cells_Obj[c].FSCell[nb][0]) + " " + str(
                        self._Cells_Obj[c].FSCell[nb][1]) + "\n")
                    if self._verbose == True:
                        print(c + 1, nb, self._Cells_Obj[c].FSCell[nb][0], self._Cells_Obj[c].FSCell[nb][1])
            file.close()

        # Trajectories (New October 2018)
        if self._trajectories:
            #Output_Grid.ScenarioTrajectories(TotalYears, Sim, FI, FS, NCells, Cells_Obj, AdjCells, OutFolder, Demand=1,
            #            alpha=0.15, probs=False, spotting=False, verbose=False)
            
            # Lite version (for light model version just for adjacents that were burned)
            Output_Grid.ScenarioTrajectoriesLite(self._TotalYears, 
                                                 self._Sim, 
                                                 self._FI, 
                                                 self._FS, 
                                                 self._NCells, 
                                                 self._Cells_Obj, 
                                                 self._AdjCells,
                                                 self._HarvestCells_Set,
                                                 self._OutFolder, 
                                                 Demand=1,
                                                 alpha=0.15, 
                                                 probs=False, 
                                                 spotting=False, 
                                                 verbose=self._verbose)
        
    
    # Adjacency fn V1
    def AdjacencyFnV1(self, actionArray):
        # Initialize penalty = 0 (total distance from largest patch)
        adjDistance = 0
        #print("------Debugging Adjacency FnV1-----")
        
        # Importantions (temporarily here during tests)
        from scipy.ndimage.measurements import label
        from scipy.spatial.distance import cdist
        from scipy import ndimage

        # Distance between features function (connected components inside the array)
        def feature_dist(input):
            """
            Takes a labeled array as returned by scipy.ndimage.label and 
            returns an intra-feature distance matrix.
            """
            I, J = np.nonzero(input)
            labels = input[I,J]
            coords = np.column_stack((I,J))

            sorter = np.argsort(labels)
            labels = labels[sorter]
            coords = coords[sorter]

            sq_dists = cdist(coords, coords, 'chebyshev')#'cityblock')#'sqeuclidean')

            start_idx = np.flatnonzero(np.r_[1, np.diff(labels)])
            nonzero_vs_feat = np.minimum.reduceat(sq_dists, start_idx, axis=1)
            feat_vs_feat = np.minimum.reduceat(nonzero_vs_feat, start_idx, axis=0)

            return np.sqrt(feat_vs_feat)

        # Idea: Calculate the number of components, find the largest one, compute the distance (chebyshev)
        #       from each component to it, to penalyze the reward function
        array = np.zeros([self._Rows * self._Cols], dtype=np.int)
        array[[actionArray]] = 1
        array = np.reshape(array, (self._Rows, self._Cols))
        structure = np.ones((3, 3), dtype=np.int)
        labeled, ncomponents = label(array, structure)
        #print("Testing Adjacency function V1:\n", labeled)
        #print("N components:", ncomponents)
        
        
        # If more than 1 component, make calculations for penalty 
        # (CP: Can modify the penalty to account the volume of the non-connected patches, weighted by distance
        #      from the largest connected component)
        if ncomponents > 1:
        
            # Calculate the size of each component
            sizeComponents = ndimage.sum(array, labeled, index=[i for i in range(1, ncomponents+1)])
            #print("Size components:", sizeComponents)
            largestComp = np.argmax(sizeComponents)
            #print("Largest component:", largestComp + 1)

            # Compute the total distance from maximum patch to the rest of the components
            adjDistance = np.sum(feature_dist(labeled)[largestComp,])
            #print("Adj Distance:", adjDistance)
    
    
        return adjDistance
             
    
    # Reward function
    def RewardFN_Tactical(self, state, action, new_burnt, done=False):
        actionArray = [i-1 for i in action]
        
        # Economic value of a cell (need to add a harvesting cost to measure the utility, just volume for the moment)
        econF = 0
        if np.max(actionArray) > -1:    # if -1 then no cell is harvested
            econF = np.sum(self._VolCells[actionArray])
        
        # BurntCells by the end of the period penalty
        burntF = 0
        if len(new_burnt) > 0:
            burntF = np.sum(self._VolCells[[i-1 for i in new_burnt]])
        
        # Demand constraint: Penalize non-satisfied demand (CP: and excess, for the moment)
        demandF = 0
        if self._demandC:
            if np.sum(self._VolCells[actionArray]) != self._PeriodDemand[self._Year - 2]:
                demandF = np.abs(self._PeriodDemand[self._Year - 2] - np.sum(self._VolCells[actionArray]))
            
            
        # Even Flow constraint: if t>0, check previous production level within an alpha %
        # Penalize by the deviation
        evenflowF = 0
        if self._evenFlowC and self._Year > 2:
            if self._verbose:
                print("Year:", self._Year)
                print("self previous action:", self._previous_action)
            prev_actionArray = [i-1 for i in self._previous_action]

            # UB
            if np.sum(self._VolCells[actionArray]) > np.sum(self._VolCells[prev_actionArray]) * (1 + self._alpha):
                evenflowF += np.sum(self._VolCells[actionArray]) - \
                             np.sum(self._VolCells[prev_actionArray]) * (1 + self._alpha)

            # LB
            elif np.sum(self._VolCells[actionArray]) < np.sum(self._VolCells[prev_actionArray]) * (1 - self._alpha):
                evenflowF += np.sum(self._VolCells[prev_actionArray]) * (1 - self._alpha) - \
                             np.sum(self._VolCells[actionArray])

        # Adjacency (CP: check function, penalizing by distance between patches for the moment)
        adjF = 0
        if self._adjC:
            adjF = self.AdjacencyFnV1(actionArray)
        
        # Done factor: Total available at the end of the episode bonus
        doneF = 0
        if done and self._finalC:
            doneF = np.sum(self._VolCells[[i-1 for i in self._AvailCells_Set]])
        
        
        # Total Reward of the period 
        # (volume harvested - burned - non-satisfied demand - flow deviation - adj violation + final bonus)
        reward = econF - burntF - demandF - evenflowF - adjF + doneF
        
        if self._nooutput == False:
            print("Reward components:", econF, burntF, demandF, evenflowF, adjF, doneF)
        
        # Next simulation (if we passed the horizon or the episode is done)
        #if self._Year > self._TotalYears or self._done = True:
        #    self._Sim += 1
        
        return reward
        
    
    # Apply action and get to next state (Tactical)
    def TacticalStep(self, action):
        # For completeness: output when user runs a tactical step AFTER the horizon
        if self._Year > self._TotalYears:
            if self._verbose:
                print("Year is greater than the Horizon, no more steps")
            done = 1
            self._Sim += 1
            return -1, -1, done # (returning error values)          
        
        # Reset global values
        self._Fire_Period[self._Year - 1] = 0
        self._plotnumber = self._max_plotnumber
        new_burnt = set()
        
        # Process the action and update the HCells
        if self._verbose == True:
            print("\nSimulating season", self._Year, "\n", "Out of totalYears:", self._TotalYears)
         
        
        # Trajectories and scenarios
        if self._Year > 1 and self._trajectories == True:
            self._HPeriod += 2
            self._FPeriod += 2
        
        # Apply action and update relevant sets
        if -1 not in action:
            actionSet = set([i for i in action])
            if self._verbose:
                print("Action (Cells to be harvested):", actionSet)
            self._HarvestCells_Set |= actionSet
            self._AvailCells_Set = self._AvailCells_Set.difference(self._HarvestCells_Set)
            self._StatusCells[[i-1 for i in actionSet]] = 4 
        
        # Init Harvested Cells (if they haven't)
        self.InitHarvested()                
        
        # Continue only if ignition        
        if self.RunIgnition() is False:
        
            # Fire Spread loop (time step of RL - Tactical)
            while self._Fire_Period[self._Year - 1] < self._Max_Fire_Periods:
                
                # Send messages after ignition
                SendMessageList = self.SendMessages()

                # If we have at least one cell that needs repetition and no other messages exists
                # We repeat
                if self._RepeatFire is True and len(self._Global_Message_Aux) == 0:
                    # Update fire period
                    self._Fire_Period[self._Year - 1] += 1
                    
                    # Update weather if needed based on Period lengths
                    self.updateWeather()
                    
                    # Plot
                    self.PlotStateGlobal(self._nepisode)
                    
                    # Grid
                    
                       
                    if self._verbose:
                        print("Weather has been updated!, weather period", self._weatherperiod)
                        print("DF:", self._DF[["fueltype", "ws", "waz", "ffmc", "bui", "saz", "elev", "ps"]])

                # If repetition and messages are sent, send them!
                if self._RepeatFire is True and len(self._Global_Message_Aux) > 0:
                    self._RepeatFire = False

                # Checking if the list is empty and no repeat flag, then if it is empty,
                # end of the actual fire dynamic period, go to next year
                if self._MessagesSent is False and self._RepeatFire is False:
                    if self._verbose:
                        print("\nNo messages during the fire period, end of year", self._Year)
                    
                    # Next year, reset weeks, weather period, and update burnt cells from burning cells
                    self._Year += 1
                    self._weatherperiod = 0
                
                    # Burning cells are labeled as Burnt cells (no more messages), then
                    # if save memory flag is True, we delete the cells objects saving memory...
                    new_burnt = self._BurningCells_Set.copy()
                    #print("Debugging new burnt:", new_burnt)
                    self._BurntCells_Set = self._BurntCells_Set.union(self._BurningCells_Set)
                    self._BurningCells_Set = set()

                    # if no savemem flag, keep the cell object and update status
                    if self._SaveMem is not True:
                        for br in self._BurntCells_Set:
                            self._Cells_Obj[br - 1].Status = 2

                    # Otherwise, delete the inactive (burnt cells)
                    if self._SaveMem:
                        for c in self._BurntCells_Set:
                            if (c - 1) in self._Cells_Obj.keys():
                                if self._verbose == True:
                                    print("Deleting burnt cells from dictionary...")
                                    print("Deleted:", c)
                                del self._Cells_Obj[c - 1]

                    break

                # Otherwise, go to next fire period and receiving messages loop
                if self._MessagesSent is True and self._RepeatFire is False:

                    # Process Messages (if needed)
                    self.GetMessages(SendMessageList)
                    new_burnt = self._BurningCells_Set.copy()
                    #print("Debugging new burnt:", new_burnt)
                    
                    # Next Period: t=t+1. Update Weather
                    self._Fire_Period[self._Year - 1] += 1
    
                    # Check weather update
                    self.updateWeather()
                    
                    if self._verbose:
                        print("Weather has been updated, weather period:", self._weatherperiod)
                        self._Weather_Obj.print_info(self._weatherperiod)

                        if self._WeatherOpt == 'constant':
                            print("\n(NOTE: current weather is not used for ROS with constant option)")
                            print("Current Fire Period:", self._Fire_Period[self._Year - 1])

            # Extra breaking condition: Max fire periods then go to next year
            if self._verbose:
                print("Next year...")

            # Next Year/Season update
            self._Year += 1
            self._weatherperiod = 0
            new_burnt = self._BurningCells_Set.copy()
            self._AvailCells_Set = self._AvailCells_Set.difference(self._BurningCells_Set)
            self._BurntCells_Set = self._BurntCells_Set.union(self._BurningCells_Set)
            self._BurningCells_Set = set()

            # if no savemem flag, keep the cell object and update status
            if self._SaveMem is not True:
                for br in self._BurntCells_Set:
                    self._Cells_Obj[br - 1].Status = 2

            # Otherwise, delete the inactive (burnt cells)
            if self._SaveMem:
                for c in self._BurntCells_Set:
                    if (c - 1) in self._Cells_Obj.keys():
                        if self._verbose == True:
                            print("Deleting burnt cells from dictionary...")
                            print("Deleted:", c)
                        del self._Cells_Obj[c - 1]

            # Save trajectories to pkl (if needed)
            if self._trajectories:
                save_obj(self._FI, "FI", self._OutFolder, self._Sim, self._nooutput)
                save_obj(self._FS, "FS", self._OutFolder, self._Sim, self._nooutput)

        # Else, generate new grid
        else:
            if self._Year == 1:
                CSVGrid(self._Rows, self._Cols, self._AvailCells_Set, self._HarvestCells_Set,
                    self._NonBurnableCells_Set, self._weatherperiod, 
                    self._GridPath)
            else:
                CSVGrid(self._Rows, self._Cols, self._AvailCells_Set, self._HarvestCells_Set,
                    self._NonBurnableCells_Set, self._max_weatherperiod + 3, 
                    self._GridPath)
 
        # Print-out results to folder
        self.Results()        
        
        # Done flag
        done = 0
        if self._Year > self._TotalYears or len(self._AvailCells_Set) == 0:
            done = 1
            self._Sim += 1
        
        # Testing reward function (state = 0 as a dummy since we are not using it)
        reward = self.RewardFN_Tactical(0, action, new_burnt, done)
        
        # Previous action container (for next period)
        self._previous_action = action.copy()
        
        # Get number of plot for next period
        self._max_plotnumber = self._plotnumber
        self._max_gridnumber = self._gridnumber
        
        # Next state
        next_state = self.getState
        
        return next_state, reward, done
    
    

    
    
    # Operational Step given an action
    def OperationalStep(self, action):        
        # For completeness: just in case user runs it longer than the horizon (should not happen)
        if self._Year > self._TotalYears:
            if self._verbose:
                print("Year is greater than the Horizon, no more steps")
            done = 1
            
            # Plot and grids if needed
            self.PlotStateGlobal(self._Sim, done)
            self.outputGrid(self._Sim, done)
            
            # Print-out results to folder
            self.Results()        
            
            # Next Sim
            self._Sim += 1
            
            return 0, 0, done # (returning error values)          
        
        # Reset global values
        new_burnt = set()
        done = 0
        
        # Process the action and update the HCells
        if self._verbose:
            print("\nSimulating season", self._Year, "\n", "Out of totalYears:", self._TotalYears)
                       
        
        # Operational dynamic
        # Ignition if we are in the first period                     
        if self._Fire_Period[self._Year - 1] == 0:
            
            # Prev Burned
            self._prev_burnt = set()
            
            # Apply tactical action
            if -1 not in action:
                actionSet = set([i for i in action])
                if self._verbose:
                    print("Action (Cells to be harvested):", actionSet)
                self._HarvestCells_Set |= actionSet
                self._AvailCells_Set = self._AvailCells_Set.difference(self._HarvestCells_Set)
                self._StatusCells[[i-1 for i in actionSet]] = 4 

                # Init Harvested Cells (if they haven't)
                self.InitHarvested() 

                # Plot and grid
                self.PlotState()
                self.outputGrid(self._gridsFreq, done=1)     
            
            # Continue only if ignition        
            if self.RunIgnition() is False:

                # Send messages after ignition
                SendMessageList = self.SendMessages()

                # If we have at least one cell that needs repetition and no other messages exists
                # We repeat
                if self._RepeatFire is True and len(self._Global_Message_Aux) == 0:
                    # Update fire period
                    self._Fire_Period[self._Year - 1] += 1
                    
                    # Update weather if needed based on Period lengths
                    self.updateWeather()
                       
                    if self._verbose:
                        print("Weather has been updated!, weather period", self._weatherperiod)
                        print("DF:", self._DF[["fueltype", "ws", "waz", "ffmc", "bui", "saz", "elev", "ps"]])

                # If repetition and messages are sent, send them!
                if self._RepeatFire is True and len(self._Global_Message_Aux) > 0:
                    self._RepeatFire = False

                # Checking if the list is empty and no repeat flag, then if it is empty,
                # end of the actual fire dynamic period, go to next year
                if self._MessagesSent is False and self._RepeatFire is False:
                    if self._verbose:
                        print("\nNo messages during the fire period, end of year", self._Year)
                    
                    # Next year, reset weeks, weather period, and update burnt cells from burning cells
                    self._Year += 1
                    self._weatherperiod = 0

                    # Burning cells are labeled as Burnt cells (no more messages), then
                    # if save memory flag is True, we delete the cells objects saving memory...
                    new_burnt = self._BurningCells_Set.copy()
                    self._BurntCells_Set = self._BurntCells_Set.union(self._BurningCells_Set)
                    self._BurningCells_Set = set()

                    # if no savemem flag, keep the cell object and update status
                    if self._SaveMem is not True:
                        for br in self._BurntCells_Set:
                            self._Cells_Obj[br - 1].Status = 2

                    # Otherwise, delete the inactive (burnt cells)
                    if self._SaveMem:
                        for c in self._BurntCells_Set:
                            if (c - 1) in self._Cells_Obj.keys():
                                if self._verbose == True:
                                    print("Deleting burnt cells from dictionary...")
                                    print("Deleted:", c)
                                del self._Cells_Obj[c - 1]

                    # End of the year
                    print("End of the fire season")
                    
                    '''
                    # If more than planning horizon, next sim
                    if self._Year > self._TotalYears:
                        # Print-out results to folder
                        self.Results()        

                        # Next Sim if max year
                        self._Sim += 1
                        done = 1
                    '''
                    
                    

                # Otherwise, go to next fire period and receiving messages loop
                if self._MessagesSent is True and self._RepeatFire is False:

                    # Process Messages (if needed)
                    self.GetMessages(SendMessageList)
                    new_burnt = self._BurningCells_Set.copy()
                    #print("Debugging new burnt:", new_burnt)
                    
                    # Next Period: t=t+1. Update Weather
                    self._Fire_Period[self._Year - 1] += 1
    
                    # Check weather update
                    self.updateWeather()
                    
                    if self._verbose:
                        print("Weather has been updated, weather period:", self._weatherperiod)
                        self._Weather_Obj.print_info(self._weatherperiod)

                        if self._WeatherOpt == 'constant':
                            print("\n(NOTE: current weather is not used for ROS with constant option)")
                            print("Current Fire Period:", self._Fire_Period[self._Year - 1])

            # No ignition: done
            else:
                # Next year
                self._weatherperiod = 0
                
                # If more than planning horizon, next sim
                if self._Year > self._TotalYears:
                    # Print-out results to folder
                    self.Results()        

                    # Next Sim if max year
                    self._Sim += 1
                    done = 1
                
                            
        
        # New operational step (ONE fire period)
        elif self._Fire_Period[self._Year - 1] > 0:
            # New Fire Period
            # Fire Spread (one time step of RL - Operational)
            # Send messages after ignition
            SendMessageList = self.SendMessages()

            # If we have at least one cell that needs repetition and no other messages exists
            # We repeat
            if self._RepeatFire is True and len(self._Global_Message_Aux) == 0:
                # Update fire period
                self._Fire_Period[self._Year - 1] += 1
    
                # Update weather if needed based on Period lengths
                self.updateWeather()
                
                if self._verbose:
                    print("Weather has been updated!, weather period", self._weatherperiod)
                    print("DF:", self._DF[["fueltype", "ws", "waz", "ffmc", "bui", "saz", "elev", "ps"]])

            # If repetition and messages are sent, send them!
            if self._RepeatFire is True and len(self._Global_Message_Aux) > 0:
                self._RepeatFire = False

            # Checking if the list is empty and no repeat flag, then if it is empty,
            # end of the actual fire dynamic period, go to next year
            if self._MessagesSent is False and self._RepeatFire is False:
                if self._verbose:
                    print("\nNo messages during the fire period, end of year", self._Year)
                
                # Next year, reset weeks, weather period, and update burnt cells from burning cells
                self._Year += 1
                self._weatherperiod = 0

                # Burning cells are labeled as Burnt cells (no more messages), then
                # if save memory flag is True, we delete the cells objects saving memory...
                new_burnt = self._BurningCells_Set.copy()
                self._BurntCells_Set = self._BurntCells_Set.union(self._BurningCells_Set)
                self._BurningCells_Set = set()

                # if no savemem flag, keep the cell object and update status
                if self._SaveMem is not True:
                    for br in self._BurntCells_Set:
                        self._Cells_Obj[br - 1].Status = 2

                # Otherwise, delete the inactive (burnt cells)
                if self._SaveMem is True:
                    for c in self._BurntCells_Set:
                        if (c - 1) in self._Cells_Obj.keys():
                            if self._verbose == True:
                                print("Deleting burnt cells from dictionary...")
                                print("Deleted:", c)
                            del self._Cells_Obj[c - 1]

                # End of the year/fire season, go to next fire (can be the end of the operational episode)
                if self._verbose:
                    print("End of the fire season")
                    
                # If more than planning horizon, next sim
                '''if self._Year > self._TotalYears:
                    # Print-out results to folder
                    self.Results()        

                    # Next Sim if max year
                    self._Sim += 1
                    done = 1
                '''

            # Otherwise, go to next fire period and receiving messages loop
            if self._MessagesSent is True and self._RepeatFire is False:

                # Process Messages (if needed)
                self.GetMessages(SendMessageList)
                new_burnt = self._BurningCells_Set.copy()
                
                # Next Period: t=t+1. Update Weather
                self._Fire_Period[self._Year - 1] += 1
                           
                # Check weather update
                self.updateWeather()
                
                # Info about weather
                if self._verbose:
                    print("Weather has been updated, weather period:", self._weatherperiod)
                    self._Weather_Obj.print_info(self._weatherperiod)

                    if self._WeatherOpt == 'constant':
                        print("\n(NOTE: current weather is not used for ROS with constant option)")
                        print("Current Fire Period:", self._Fire_Period[self._Year - 1])

        # End of the operational episode condition
        if self._Year - 1 >= len(self._Fire_Period):
            self._Year = len(self._Fire_Period)
        if self._Fire_Period[self._Year - 1] > self._Max_Fire_Periods:
            # Extra breaking condition: Max fire periods then go to next year
            if self._verbose:
                print("Next year...")

            # Next Year/Season update
            self._Year += 1
            self._weatherperiod = 0
            new_burnt = self._BurningCells_Set.copy()

            self._AvailCells_Set = self._AvailCells_Set.difference(self._BurningCells_Set)
            self._BurntCells_Set = self._BurntCells_Set.union(self._BurningCells_Set)
            self._BurningCells_Set = set()

            # if no savemem flag, keep the cell object and update status
            if self._SaveMem != True:
                for br in self._BurntCells_Set:
                    self._Cells_Obj[br - 1].Status = 2

            # Otherwise, delete the inactive (burnt cells)
            if self._SaveMem == True:
                for c in self._BurntCells_Set:
                    if (c - 1) in self._Cells_Obj.keys():
                        if self._verbose == True:
                            print("Deleting burnt cells from dictionary...")
                            print("Deleted:", c)
                        del self._Cells_Obj[c - 1]

            # Save trajectories to pkl (if needed)
            if self._trajectories:
                save_obj(self._FI, "FI", self._OutFolder, self._Sim, self._nooutput)
                save_obj(self._FS, "FS", self._OutFolder, self._Sim, self._nooutput)
 
            # Print-out results to folder
            #self.Results()       
        
        # If more than planning horizon, next sim
        if self._Year > self._TotalYears:
                        
            # Plot and grids if needed
            self.PlotStateGlobal(self._Sim, done, final=1)
            self.outputGrid(self._Sim, done)
            
            # Print-out results to folder
            self.Results()        

            # Next Sim if max year
            self._Sim += 1
            done = 1
        
        # Done flag (extra condition: no available cells or death of the team)
        if len(self._AvailCells_Set) == 0:
            done = 1
            
            # Plot and grids if needed
            self.PlotStateGlobal(self._Sim, done)
            self.outputGrid(self._Sim, done)
            
            # Print-out results to folder
            self.Results()        
            
            # Next Sim if max year
            self._Sim += 1
            
            
        
        # Individual rewards (reset, and get new burnt cells)
        reward = 0
        new_burnt = self._BurntCells_Set - self._prev_burnt
        
        # Info
        if self._verbose:
            print("\tPre-Reward")
            print("\tBurning:", self._BurningCells_Set)
            print("\tBurnt:", self._BurntCells_Set)
            print("\tPrev Burning:", self._prev_burnt)
            print("\tnew burnt:", new_burnt)
        self._prev_burnt |= self._BurntCells_Set
        
        # Reward computations
        

        # Get number of plot for next period
        self._max_plotnumber = self._plotnumber
        self._max_gridnumber = self._gridnumber
        
        # Reward, done, next state
        step_reward = reward
        self._ep_reward += step_reward
        next_state = self.getState
       
        # Print current status
        if done == 0 and self._verbose is True:
            print("Fire Period:", self._Fire_Period[self._Year - 1], "Year:", self._Year)
            print("Step reward:", step_reward)
    
        # Info
        if self._verbose:
            print("\tStep reward:", step_reward)
            print("\tEP Reward:", self._ep_reward)  
        
        # Return new states, rewards obtained, and dones array
        return next_state, step_reward, done
    
    #####################
    #                   #
    #       Utils       #
    #                   #
    #####################
    # Set no output
    def setNoOutput(self, val):
        self._nooutput = val
         
    # Set current year
    def setYear(self, year):
        self._Year = year
    
    # Get fire period given a year
    def getFirePeriodYear(self, year):
        return self._Fire_Period[year - 1]
    
    # Update the plot number
    def updatePlotNumber(self):
        self._plotnumber += 1
    
    # Update grid number
    def updateGridNumber(self):
        self._gridnumber += 1
    
    
    # Plots every _plotStep time-steps of an episode
    def PlotState(self, final=0):
        # Get fire period
        FPeriod = self.getFirePeriod
        
        # Plot every _plotStep time-steps
        if self._plotStep >= 1 and FPeriod % self._plotStep == 0:
            # Aux empty list for the plot function            
            self._emptylist = dict.fromkeys([i for i in range(1, self._NCells + 1)], [])
            
            # Directory
            PlotPath = os.path.join(self.getOutput, "Plots")
            if not os.path.exists(PlotPath):
                os.makedirs(PlotPath)
            
            # Plot
            self._Plotter.forest_plotV3(self.getCells, 
                                        self._emptylist, 
                                        self._plotnumber, 
                                        self.getFirePeriod, 
                                        self.getYear - final,
                                        False, 
                                        self.getRows,
                                        self.getCols,
                                        PlotPath, 
                                        self.getSim)
            
            # Update Plot number
            self.updatePlotNumber()
            
            
    
    # Plots every _plotStep time-steps of an episode every _plotFreq 
    def PlotStateGlobal(self, nEpisode, done=0, final=0):
        # Get fire period
        FPeriod = self.getFirePeriod
        
        # Plot every _plotStep time-steps
        if self._plotFreq > 0 and self._plotStep >= 1 and (FPeriod % self._plotStep == 0 or done == 1) and nEpisode % self._plotFreq == 0:
            # Aux empty list for the plot function
            self._emptylist = dict.fromkeys([i for i in range(1, self._NCells + 1)], [])
            
            # Directory
            PlotPath = os.path.join(self.getOutput, "Plots")
            if not os.path.exists(PlotPath):
                os.makedirs(PlotPath)
            
            # Plot
            self._Plotter.forest_plotV3(self.getCells, 
                                        self._emptylist, 
                                        self._plotnumber, 
                                        self.getFirePeriod, 
                                        self.getYear - final,
                                        False, 
                                        self.getRows,
                                        self.getCols,
                                        PlotPath, 
                                        self.getSim)
            # Update the plot number
            self.updatePlotNumber()
    
    # Initial Forest (full info)
    def InitPlot(self):
        # Check if file exists
        if os.path.isfile(os.path.join(self._OutFolder, "ForestInitial.png")) == True:
            if self._nooutput == False:
                print("Forest already exists")
        # Otherwise, generate it
        else:
            self._Plotter.PlotForestOnly(self._Colors, 
                                         self._CoordCells, 
                                         self._plotnumber, 
                                         0, 
                                         self._Year, 
                                         False, 
                                         self._Rows, 
                                         self._Cols, 
                                         self._OutFolder)
        
    
    # Multi Fire Plot
    def MultiFire(self):
        if (self._WeatherOpt == 'multiple' or self._WeatherOpt == "random" or self._ROSCV != 0 or self._IgnitionRad > 0) \
            and self._TotalSims > 1 and self._plotFreq > 0:
            self._Plotter.MultiFireMix(self._OutFolder, self._TotalSims, mode="Scale",probs=[])
            self._Plotter.MultiFireMix(self._OutFolder, self._TotalSims, mode="Sum",probs=[])
    
    
    # Initialize a Cell
    def InitCell(self, ID):
        newCell = CellsFBP.Cells(ID,
                                 self._AreaCells,
                                 self._CoordCells[ID - 1], 
                                 self._AgeCells,
                                 self._FTypeCells[ID - 1],
                                 self._coef_ptr[self._FTypes2[str.lower(self._GForestType[ID - 1])]],
                                 self._VolCells[ID - 1], 
                                 self._PerimeterCells,
                                 self._StatusCells[ID - 1],
                                 self._AdjCells[ID - 1],
                                 self._Colors[ID - 1],
                                 self._RealCells[ID - 1], 
                                 False)
        
        newCell.InitializeFireFields(self._CoordCells, self._AvailCells_Set)       
        return newCell    
    
    # Generate grid
    def outputGrid(self, nEpisode, done=0, bypass=False):
        # Get fire period
        FPeriod = self.getFirePeriod
        
        # Plot every _plotStep time-steps
        if self._gridsFreq > 0 and self._gridsStep >= 1 and (FPeriod % self._gridsStep == 0 or done == 1) and nEpisode % self._gridsFreq == 0:
 
            CSVGrid(self._Rows, 
                    self._Cols, 
                    self._AvailCells_Set,
                    self._HarvestCells_Set,
                    self._NonBurnableCells_Set, 
                    self._gridnumber, 
                    self._GridPath)
            
            # Update grid number
            self.updateGridNumber()

    # Update weather
    def updateWeather(self):
        if self._WeatherOpt != 'constant' and \
        self._Fire_Period[self._Year - 1] * self._FirePeriodLen / self._MinutesPerWP > self._weatherperiod + 1:
            self._weatherperiod += 1
            print("Testing weather period:", self._weatherperiod)
            self._DF = self._Weather_Obj.update_Weather_FBP(self._DF, self._WeatherOpt, self._weatherperiod)
            self._max_weatherperiod += 1
                        
    
    # Properties
    @property
    def getPlotStep(self):
        return self._plotStep
    
    @property
    def getPlotFreq(self):
        return self._plotFreq
    
    @property
    def getFirePeriodLength(self):
        return self._FirePeriodLen

    @property
    def getIgRadius(self):
        return self._IgnitionRad

    @property
    def getInstance(self):
        return self._InFolder

    @property
    def getOutput(self):
        return self._OutFolder

    @property
    def getIgnitions(self):
        return self._Ignitions

    @property
    def getTYears(self):
        return self._TotalYears
    
    @property
    def getYear(self):
        return self._Year

    @property
    def getNSims(self):
        return self._TotalSims

    @property
    def Init_HCells(self):
        return self._HCells

    @property
    def Init_BCells(self):
        return self._BCells

    @property
    def getWeatherOpt(self):
        return self._WeatherOpt

    @property
    def getSeed(self):
        return self._seed
    
    @property
    def getDF(self):
        return self._DF
    
    @property
    def getWeatherObj(self):
        return self._Weather_Obj
    
    @property
    def getFI(self):
        return self._FI
    
    @property
    def getFS(self):
        return self._FS
    
    @property
    def getFirePeriod(self):
        if self._Year - 1 < len(self._Fire_Period): 
            return self._Fire_Period[self._Year-1]
        else:
            return self._Fire_Period[-1]
    
    @property
    def getWeatherPeriod(self):
        return self._weatherperiod
    
    @property
    def getStatusCells(self):
        return self._StatusCells
    
    @property
    def getSets(self):
        return self._HarvestCells_Set, self._AvailCells_Set, self._BurntCells_Set
    
    @property
    def getStatusArrays(self):
        return [i for i in self._HarvestCells_Set], [j for j in self._AvailCells_Set], [l for l in self._BurntCells_Set]
    
    @property
    def getCells(self):
        return self._Cells_Obj
    
    @property
    def getGlobalMessage(self):
        return self._Global_Message_Aux
    
    @property
    def getRepeatFire(self):
        return self._RepeatFire
    
    @property
    def getSim(self):
        return self._Sim
    
    @property
    def getAdj(self):
        return self._AdjCells
    
    @property
    def getVol(self):
        return self._VolCells
    
    @property 
    def getCoords(self):
        return self._CoordCells
    
    @property 
    def getColorsDict(self):
        return self._Colors
    
    @property 
    def getAvailCells(self):
        return self._AvailCells_Set
    
    @property 
    def getBurnedCells(self):
        return self._BurntCells_Set
    
    @property 
    def getHarvestedCells(self):
        return self._HarvestCells_Set
    
    @property
    def getCols(self):
        return self._Cols
        
    @property
    def getRows(self):
        return self._Rows
    
    @property
    def getMessagesPath(self):
        return self._MessagesPath
    
    @property
    def getVerbose(self):
        return self._verbose
    
    @property
    def getNCells(self):
        return self._NCells
    
    @property
    def getGlobalState(self):
        globalState = np.ones(self._Rows * self._Cols).astype(int)
        if len(self._AvailCells_Set) > 0:
            globalState[list(self._AvailCells_Set) - np.ones(len(self._AvailCells_Set)).astype(int)] = 0
        if len(self._HarvestCells_Set) > 0:
            globalState[list(self._HarvestCells_Set) - np.ones(len(self._HarvestCells_Set)).astype(int)] = 2
        if len(self._NonBurnableCells_Set) > 0:
            globalState[list(self._NonBurnableCells_Set) - np.ones(len(self._NonBurnableCells_Set)).astype(int)] = -1
        globalState = globalState.reshape(self._Rows, self._Cols).astype(int)
        return globalState
    
    @property
    def getState(self):
        # 1: Fire Progress Matrix 
        if self._observationSpace == 1:
            return self.getFireProgressMatrix.flatten()
        
        # 2: 1 + Current weather
        elif self._observationSpace == 2:
            WMatrix = self._Weather_Obj.getDF[self._Weather_Obj.getDF.columns[1:]].iloc[[self._weatherperiod]].values
            return np.concatenate((self.getFireProgressMatrix.flatten(), 
                                   WMatrix.flatten()))
            
        # 3: 2 + Topography (elevation, slope) + Fueltype
        elif self._observationSpace == 3:
            WMatrix = self._Weather_Obj.getDF[self._Weather_Obj.getDF.columns[1:]].iloc[[self._weatherperiod]].values
            ElMatrix = np.reshape(self.getDF["elev"].fillna(0).values, 
                                  (self.getRows, self.getCols))
            SlMatrix = np.reshape(self.getDF["ps"].fillna(0).values, 
                                  (self.getRows, self.getCols))
            FTMatrix = np.reshape([self._FTypes2[i] if i != "nf" else -1 for i in self.getDF["fueltype"]], 
                                  (self.getRows, self.getCols))
            return np.concatenate((self.getFireProgressMatrix.flatten(), 
                                   WMatrix.flatten(), 
                                   ElMatrix.flatten(), 
                                   SlMatrix.flatten(), 
                                   FTMatrix.flatten()))
        
        else:
            raise RuntimeError("Wrong Observation Space version (select: 1, 2, or 3)")
    
    @property
    def getObsSpace_n(self):
        obsDim = 0
        
        # 1: Fire Progress Matrix 
        if self._observationSpace == 1:
            obsDim = self._NCells 
        # 2: 1 + Current weather
        elif self._observationSpace == 2:
            obsDim = self._NCells + len(self._Weather_Obj.getDF.columns[1:])
        # 3: 2 + Topography (elevation, slope) + Fueltype 
        elif self._observationSpace == 3:
            obsDim = self._NCells * 4 + len(self._Weather_Obj.getDF.columns[1:])
        return obsDim
 
    @property
    def getPlotter(self):
        # Returns plotter object
        return self._Plotter
    
    @property 
    def getEpReward(self):
        # Episode reward (sum of all rewards)
        return self._ep_reward
    
    @property
    def getFireProgressMatrix(self):
        # Burnt Cells = 1
        if len(self._BurntCells_Set) > 0:
            idxBurnt = np.asarray([int(i-1) for i in self._BurntCells_Set])
            self._FProgressMatrix[idxBurnt] = 1
            
        # Harvest Cells = 1
        if len(self._HarvestCells_Set) > 0:
            idxHarvest = np.asarray([int(i-1) for i in self._HarvestCells_Set])
            self._FProgressMatrix[idxHarvest] = 0
            
        # Update Fire Progress Matrix based on current state
        for i in self.getCells.keys():
            for nb in self.getCells[i].FireProgress.keys():
                if nb in self._AvailCells_Set:
                    self._FProgressMatrix[nb-1] = np.max([1, 
                                                          self._FProgressMatrix[nb-1], 
                                                          self.getCells[i].FireProgress[nb]]) / self._CellSide
                    
        
        # Return the matrix
        return self._FProgressMatrix.flatten()
    
    @property 
    def getROSMatrix(self):
        # Burnt Cells = 1
        if len(self._BurntCells_Set) > 0:
            idxBurnt = np.asarray([int(i-1) for i in self._BurntCells_Set])
            self._ROSMatrix[idxBurnt] = 9999
            
        # Harvest Cells = 1
        if len(self._HarvestCells_Set) > 0:
            idxHarvest = np.asarray([int(i-1) for i in self._HarvestCells_Set])
            self._ROSMatrix[idxHarvest] = -1
            
        # Update Fire Progress Matrix based on current state
        for i in self.getCells.keys():
            for nb in self.getCells[i].FireProgress.keys():
                if nb in self._AvailCells_Set:
                    cell_i = self.getCells[i]
                    angle_i = cell_i.AngleDict[nb]
                    ros_i_nb = cell_i.ROSAngleDir[angle_i]
                    
                    if ros_i_nb is not None:
                        self._ROSMatrix[nb-1] = np.max([0, ros_i_nb]) 
        
        # Return the matrix
        return self._ROSMatrix.flatten()
    
    
