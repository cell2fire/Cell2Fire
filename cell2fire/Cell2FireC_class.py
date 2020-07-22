# coding: utf-8
__version__ = "1.0"
__author__ = "Cristobal Pais"
# name change to Cell2FireC_class by DLW (confusion with the dir name)

# General imporations
import os
import glob 
import shutil
import signal
import subprocess
import sys
import cell2fire.utils.DataGeneratorC as DataGenerator
import cell2fire.utils.ReadDataPrometheus as ReadDataPrometheus
from cell2fire.utils.ParseInputs import InitCells
from cell2fire.utils.Stats import *
import cell2fire  # for path finding
p = str(cell2fire.__path__)
l = p.find("'")
r = p.find("'", l+1)
cell2fire_path = p[l+1:r]
print("cell2fire_path",cell2fire_path)

class Cell2FireC:
    # Constructor and initial run
    def __init__(self, args):
        # Store arguments
        self.args = args
        
        # Check if we need to generate DataC.csv
        self.generateDataC()

        # Main call 
        if self.args.onlyProcessing is False:
            self.run()
        else:
            print("Running Cell2FirePy as a post-processing tool for a previous simulation")
        
        # Containers 
        self._NCells = 0
        self._Rows = 0
        self._Cols = 0
        self._AdjCells = {}
        self._CoordCells = {}
        self._GForestType = []
        self._GForestN = []
        self._Colors = {}
        self._FTypeCells = []
        self._FTypes2 = {"m1": 0, "m2": 1, "m3": 2, "m4": 3,
                         "c1": 4, "c2": 5, "c3": 6, "c4": 7, "c5": 8, "c6": 9, "c7": 10,
                         "d1": 11, "s1": 12, "s2": 13, "s3": 14, "o1a": 15, "o1b": 16, "d2": 17}
        
    
    # Run C++ Sim
    def run(self):
        # Parse args for calling C++ via subprocess        
        # DLW June 2020: supporting calling with os.system
        execArray=[os.path.join(cell2fire_path,"Cell2FireC","Cell2Fire"),
                   '--input-instance-folder', self.args.InFolder,
                   '--output-folder', self.args.OutFolder if (self.args.OutFolder is not None) else '',
                   '--ignitions' if (self.args.ignitions) else '',
                   '--sim-years', str(self.args.sim_years),
                   '--nsims', str(self.args.nsims),
                   '--grids' if (self.args.grids) else '', '--final-grid' if (self.args.finalGrid) else '',
                   '--Fire-Period-Length', str(self.args.input_PeriodLen),
                   '--output-messages' if (self.args.OutMessages) else '',
                   '--weather', self.args.WeatherOpt,
                   '--nweathers', str(self.args.nweathers),
                   '--ROS-CV', str(self.args.ROS_CV),
                   '--IgnitionRad', str(self.args.IgRadius), 
                   '--seed', str(int(self.args.seed)),
                   '--ROS-Threshold', str(self.args.ROS_Threshold),
                   '--HFI-Threshold', str(self.args.HFI_Threshold),
                   '--bbo' if (self.args.BBO) else '',
                   '--verbose' if (self.args.verbose) else '',
                   '--HarvestPlan', self.args.HCells if(self.args.HCells is not None) else '',]
        
        # Output log
        if self.args.OutFolder is not None:
            # TBD: always delete and make the output dir (maybe not here)
            if not os.path.isdir(self.args.OutFolder):
                os.makedirs(self.args.OutFolder)
                os.makedirs(os.path.join(self.args.OutFolder, "Messages"))  # hack June 2020
            LogName = os.path.join(self.args.OutFolder, "LogFile.txt")
        else:
            LogName = os.path.join(self.args.InFolder, "LogFile.txt")   

        # Perform the call
        with open(LogName, 'w') as output:
            proc = subprocess.Popen(execArray, stdout=output)
            proc.communicate()
        proc.wait()
        if not proc.returncode == 0:
                sys.exit()        
        """
        cmdstr = ""
        for es in execArray:
            cmdstr += es+' '
        os.system(cmdstr + ">"+LogName)
        """
        # End of the replications
        print("End of Cell2FireC C++  execution...")
    
    # Pre-processing
    '''
    Generate the Data.csv file for the C++ core
    '''
    def generateDataC(self):
        dataName = os.path.join(self.args.InFolder, "Data.csv")
        if os.path.isfile(dataName) is False:
            print("Generating Data.csv File...")
            DataGenerator.GenDataFile(self.args.InFolder)
            
            
    
    # Post-processing    
    '''
    Data for stats/plots
    '''
    def getData(self):
        # Paths
        ForestFile = os.path.join(self.args.InFolder, "Forest.asc")
        FBPlookup = os.path.join(self.args.InFolder, "fbp_lookup_table.csv")
        
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
        self._GForestN = np.asarray(GForestN).reshape((Rows, Cols))        

        # Initialize main cells inputs
        FTypeCells, StatusCells, RealCells, Colors = InitCells(self._NCells, self._FTypes2, 
                                                               ColorsDict, GForestType, GForestN)
    
        self._Colors = Colors 
        self._FTypeCells = FTypeCells 
        self._StatusCells = StatusCells

    '''
    Generate empty MessageFiles if needed
    '''
    def DummyMsg(self):
        # Messages path and CWD for returning
        MPath = os.path.join(self.args.OutFolder, "Messages")
        CWD = os.getcwd()
        os.chdir(MPath)
        
        # Read files 
        MessagesFiles = glob.glob('*')
        existingIDs = [int(re.match('MessagesFile(\d+)', MessagesFiles[i]).groups()[0]) for i in range(0, len(MessagesFiles))]
        
        # Loop for filling with dummy files 
        for i in range(1, self.args.nsims + 1):
            if i not in existingIDs:
                # DLW June 2020: TBD: why do we do the CWD???
                #np.savetxt(os.path.join(MPath, "MessagesFile" + str(i).zfill(2) + ".csv"), np.asarray([]))
                np.savetxt("MessagesFile" + str(i).zfill(2) + ".csv", np.asarray([]))
        # Come back to the original directory
        os.chdir(CWD)
        
    
    '''
    Generate statistics from Grids
    '''
    def stats(self):
        # Get rows, cols 
        DFForest = pd.read_csv(os.path.join(self.args.InFolder, "Forest.asc"), 
                               sep=" ", header=None, nrows=2)
        Shape = DFForest[1].values
        
        # Initialize the Stats object
        StatsPrinter = Statistics(OutFolder=self.args.OutFolder,
                                  StatsFolder="",
                                  MessagesPath=os.path.join(self.args.OutFolder, "Messages"),
                                  Rows=Shape[0],
                                  Cols=Shape[1],
                                  NCells=Shape[0] * Shape[1],
                                  boxPlot=True,
                                  CSVs=True,
                                  statsGeneral=True, 
                                  statsHour=True,
                                  histograms=True,
                                  BurntProb=True,
                                  nSims=self.args.nsims,
                                  verbose=self.args.verbose,
                                  GGraph=None,
                                  tCorrected=False)

        # Dummy messages (general case if needed)
        self.DummyMsg()
        
        # Hourly Stats
        if self.args.grids:
            print("Hourly stats...")
            StatsPrinter.HourlyStats()

        # General Stats
        print("General stats...")
        StatsPrinter.GeneralStats()
        
        # Get Coordinates and colors
        if self.args.spreadPlots or self.args.plots or self.args.allPlots:
            print("Reading data...")
            self.getData()  
            print("Dummy if needed...")
            self.DummyMsg()
        
        # Spread plots
        if self.args.spreadPlots or self.args.allPlots:
            # Fire Spread Graphs
            print("Generating global fire spread evolution...")
            totalPlots = 1
            
            # If multiple sims, plots including freq are useful
            if self.args.nsims > 1:
                totalPlots = 3
            for v in tqdm(range(totalPlots)):
                StatsPrinter.GlobalFireSpreadEvo(self._CoordCells, 
                                                 onlyGraph=True,
                                                 version=v)

            # Fire Spread Graphs (individual)
            if self.args.grids:
                print("Generating individual Fire Spread plots...")
                for n in tqdm(range(1, self.args.nsims + 1)):
                    StatsPrinter.SimFireSpreadEvo(n, self._CoordCells, 
                                                  self._Colors, 
                                                  H=None, version=0,
                                                  print_graph=True, 
                                                  analysis_degree=False,
                                                  onlyGraph=True)
                    
            
            # Generate Initial Forest
            print("Generating initial forest plot...")
            FBPlookup = os.path.join(self.args.InFolder, "fbp_lookup_table.csv")
            if self.args.HCells is not None: 
                HCarray = np.loadtxt(self.args.HCells, skiprows=1, delimiter=",")[1:].astype(np.int)
                print("HCArray:", HCarray)
                print("GForestN:", self._GForestN)
                self._GForestN = self._GForestN.flatten()
                for i in HCarray:
                    self._GForestN[i-1] = -1                    
                    #self._GForestN[i // Shape[1] - 1, i - i // Shape[1] * i // Shape[0] - 1] = -1
            
                self._GForestN = self._GForestN.reshape((Shape[0], Shape[1]))
            StatsPrinter.ForestPlot(FBPlookup, self._GForestN, 
                                    self.args.OutFolder, namePlot="InitialForest")


        # Individual plots 
        if self.args.plots or self.args.allPlots:            
            if self.args.grids:
                # Plotting
                print("Generating fire evolution plots...")
                StatsPrinter.plotEvo()
                
                # Combine them with background
                if self.args.combine:
                    print("Combining Fires with background (initial forest)...")
                    StatsPrinter.mergePlot()

            print("Generating detailed individual propagation trees...")
            for n in tqdm(range(1, self.args.nsims + 1)):
                for v in range(1,4):
                    StatsPrinter.SimFireSpreadEvoV2(n, self._CoordCells,
                                                    self._Colors, 
                                                    H=None, version=v, 
                                                    onlyGraph=True)        
        
    
    
