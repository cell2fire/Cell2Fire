# coding: utf-8
__version__ = "1.0"
__author__ = "Cristobal Pais"

# General importations
import os
import numpy as np
import glob
from argparse import ArgumentParser

# Classes importations
###import Cell2Fire.Cell2Fire.Plot as Plot

def make_parser():
    parser = ArgumentParser()
    # Folders 
    parser.add_argument("--input-instance-folder",
                        help="The path to the folder contains all the files for the simulation",
                        dest="InFolder",
                        type=str,
                        default=None)                
    parser.add_argument("--output-folder",
                        help="The path to the folder for simulation output files",
                        dest="OutFolder",
                        type=str,
                        default=None)                
    
    # Integers
    parser.add_argument("--sim-years",
                        help="Number of years per simulation (default 1)",
                        dest="sim_years",
                        type=int,
                        default=1)    
    parser.add_argument("--nsims",
                        help="Total number of simulations (replications)",
                        dest="nsims",
                        type=int,
                        default=1)    
    parser.add_argument("--seed",
                        help="Seed for random numbers (default is 123)",
                        dest="seed",
                        type=int,
                        default=123)        
    parser.add_argument("--nweathers",
                        help="Max index of weather files to sample for the random version (inside the Weathers Folder)",
                        dest="nweathers",
                        type=int,
                        default=1)
    parser.add_argument("--nthreads",
                        help="Number of threads to run the simulation",
                        dest="nthreads",
                        type=int,
                        default=1)
    parser.add_argument("--max-fire-periods",
                        help="Maximum fire periods per year (default 1000)",
                        dest="max_fire_periods",
                        type=int,
                        default=1000) 
    parser.add_argument("--IgnitionRad",
                        help="Adjacents degree for defining an ignition area (around ignition point)",
                        dest="IgRadius",
                        type=int,
                        default=0) 
    parser.add_argument("--gridsStep",
                        help="Grids are generated every n time steps",
                        dest="gridsStep",
                        type=int,
                        default=60)
    parser.add_argument("--gridsFreq",
                        help="Grids are generated every n episodes/sims",
                        dest="gridsFreq",
                        type=int,
                        default=-1)
    
    # Heuristic
    parser.add_argument("--heuristic",
                        help="Heuristic version to run (-1 default no heuristic, 0 all)",
                        dest="heuristic",
                        type=int,
                        default=-1)
    parser.add_argument("--MessagesPath",
                        help="Path with the .txt messages generated for simulators",
                        dest="messages_path",
                        type=str,
                        default=None)
    parser.add_argument("--GASelection",
                        help="Use the genetic algorithm instead of greedy selection when calling the heuristic",
                        dest="GASelection",
                        default=False,
                        action="store_true")
    parser.add_argument("--HarvestedCells",
                        help="File with initial harvested cells (csv with year, number of cells: e.g 1,1,2,3,4,10)",
                        dest="HCells",
                        type=str,
                        default=None)
    parser.add_argument("--msgheur",
                        help="Path to messages needed for Heuristics",
                        dest="msgHeur",
                        type=str,
                        default="")
    parser.add_argument("--applyPlan",
                        help="Path to Heuristic/Harvesting plan",
                        dest="planPath",
                        type=str,
                        default="")
    parser.add_argument("--DFraction",
                        help="Demand fraction w.r.t. total forest available",
                        dest="TFraction",
                        type=float,
                        default=1.0)
    parser.add_argument("--GPTree",
                        help="Use the Global Propagation tree for calculating the VaR and performing the heuristic plan",
                        dest="GPTree",
                        default=False,
                        action="store_true")
    parser.add_argument("--customValue",
                        help="Path to Heuristic/Harvesting custom value file",
                        dest="valueFile",
                        type=str,
                        default=None)
    parser.add_argument("--noEvaluation",
                        help="Generate the treatment plans without evaluating them",
                        dest="noEvaluation",
                        default=False,
                        action="store_true")
    
    
    
    # Genetic params
    parser.add_argument("--ngen",
                        help="Number of generations for genetic algorithm",
                        dest="ngen",
                        type=int,
                        default=500)
    parser.add_argument("--npop",
                        help="Population for genetic algorithm",
                        dest="npop",
                        type=int,
                        default=100)
    parser.add_argument("--tsize",
                        help="Tournament size",
                        dest="tSize",
                        type=int,
                        default=3)
    parser.add_argument("--cxpb",
                        help="Crossover prob.",
                        dest="cxpb",
                        type=float,
                        default=0.8)
    parser.add_argument("--mutpb",
                        help="Mutation prob.",
                        dest="mutpb",
                        type=float,
                        default=0.2)
    parser.add_argument("--indpb",
                        help="Individual prob.",
                        dest="indpb",
                        type=float,
                        default=0.5)
    
    # Booleans
    parser.add_argument("--weather",
                        help="The 'type' of weather: constant, random, rows (default rows)",
                        dest="WeatherOpt",
                        type=str,
                        default="rows")
    parser.add_argument("--spreadPlots",
                        help="Generate spread plots",
                        dest="spreadPlots",
                        default=False,
                        action='store_true')
    parser.add_argument("--finalGrid",
                        help="GGenerate final grid",
                        dest="finalGrid",
                        default=False,
                        action="store_true")
    parser.add_argument("--verbose",
                        help="Output all the simulation log",
                        dest="verbose",
                        default=False,
                        action='store_true')
    parser.add_argument("--ignitions",
                        help="Activates the predefined ignition points when using the folder execution",
                        dest="ignitions",
                        default=False,
                        action="store_true")    
    parser.add_argument("--grids",
                        help="Generate grids",
                        dest="grids",
                        default=False,
                        action='store_true')
    parser.add_argument("--simPlots",
                        help="generate simulation/replication plots",
                        dest="plots",
                        default=False,
                        action='store_true')
    parser.add_argument("--allPlots",
                        help="generate spread and simulation/replication plots",
                        dest="allPlots",
                        default=False,
                        action='store_true')
    parser.add_argument("--combine",
                        help="Combine fire evolution diagrams with the forest background",
                        dest="combine",
                        default=False,
                        action="store_true")                    
    parser.add_argument("--no-output",
                        help="Activates no-output mode ",
                        dest="no_output",
                        default=False,
                        action="store_true")            
    parser.add_argument("--gen-data",
                        help="Generates the Data.csv file before the simulation",
                        dest="input_gendata",
                        default=False,
                        action="store_true")
    parser.add_argument("--output-messages",
                        help="Generates a file with messages per cell, hit period, and hit ROS",
                        dest="OutMessages",
                        default=False,
                        action='store_true')
    parser.add_argument("--Prometheus-tuned",
                        help="Activates the predefined tuning parameters based on Prometheus",
                        dest="PromTuning",
                        default=False,
                        action="store_true") 
    parser.add_argument("--trajectories",
                        help="Save fire trajectories FI and FS for MSS",
                        dest="input_trajectories",
                        default=False,
                        action="store_true") 
    parser.add_argument("--stats",
                        help="Output statistics from the simulations",
                        dest="stats",
                        default=False,
                        action="store_true")
    parser.add_argument("--correctedStats",
                        help="Normalize the number of grids outputs for hourly stats",
                        dest="tCorrected",
                        default=False,
                        action="store_true")
    parser.add_argument("--onlyProcessing",
                        help="Read a previous simulation OutFolder and process it (Cell2Fire simulation is not called)",
                        dest="onlyProcessing",
                        default=False,
                        action="store_true")
    parser.add_argument("--bbo",
                        help="Use factors in BBOFuels.csv file",
                        dest="BBO",
                        default=False,
                        action="store_true")
    parser.add_argument("--fdemand",
                        help="Finer demand/treatment fraction",
                        dest="fdemand",
                        default=False,
                        action="store_true")
    parser.add_argument("--pdfOutputs",
                        help="Generate pdf versions of all plots",
                        dest="pdfOutputs",
                        default=False,
                        action="store_true")
    
    
    
    # Floats
    parser.add_argument("--Fire-Period-Length",
                        help="Fire Period length in minutes (needed for ROS computations). Default 60",
                        dest="input_PeriodLen",
                        type=float,
                        default=60)                    
    parser.add_argument("--Weather-Period-Length",
                        help="Weather Period length in minutes (needed weather update). Default 60",
                        dest="weather_period_len",
                        type=float,
                        default=60)                    
    parser.add_argument("--ROS-Threshold",
                        help="A fire will not start or continue to burn in a cell if the head ros\
                             is not above this value (m/min) default 0.1.",
                        dest="ROS_Threshold",
                        type=float,
                        default=0.1)                    
    parser.add_argument("--HFI-Threshold",
                        help="A fire will not start or continue to burn in a cell if the HFI is \
                              not above this value (Kw/m) default is 10.",
                        dest="HFI_Threshold",
                        type=float,
                        default=0.1)                    
    parser.add_argument("--ROS-CV",
                        help="Coefficient of Variation for normal random ROS (e.g. 0.13), \
                              but default is 0 (deteriministic)",
                        dest="ROS_CV",
                        type=float,
                        default=0.0)                    
    parser.add_argument("--HFactor",
                        help="Adjustement factor: HROS",
                        dest="HFactor",
                        type=float,
                        default=1.0)
    parser.add_argument("--FFactor",
                        help="Adjustement factor: FROS",
                        dest="FFactor",
                        type=float,
                        default=1.0)
    parser.add_argument("--BFactor",
                        help="Adjustement factor: BROS",
                        dest="BFactor",
                        type=float,
                        default=1.0)
    parser.add_argument("--EFactor",
                        help="Adjustement ellipse factor",
                        dest="EFactor",
                        type=float,
                        default=1.0)
    parser.add_argument("--BurningLen",
                        help="Burning length period (periods a cell is burning)",
                        dest="BurningLen",
                        type=float,
                        default=-1.0)
    return parser


'''
Returns       args object (containing command line arguments)

Inputs:
'''
def ParseInputs():
    parser = make_parser()        
    
    args = parser.parse_args()
    return args
    
    
    
    
    


'''
Returns          Plot class object

Inputs:
args             args object

def Init(args):
    #Initializing plot object and plot the initial forest
    if args.plots:
        PlotPath = os.path.join(args.OutFolder, "Plots")
        if not os.path.exists(PlotPath):
            print("creating", PlotPath)
            os.makedirs(PlotPath)
        Plotter = Plot.Plot()

    else:
        Plotter = None
    
    if args.grids:
        GridPath = os.path.join(args.OutFolder, "Grids")
        if not os.path.exists(GridPath):
            print("creating", GridPath)
            os.makedirs(GridPath)
        
    return Plotter
'''

'''
Returns          int array, int array, int array, array of 4D doubles tuples [(d1,d2,d3,d4),...,(d1n,d2n,d3n,d4n)]  

Inputs:
Ignitions        string
WeatherOpt       list of strings
DF               DataFrame
args             args object
verbose          boolean
nooutput         boolean
'''
def InitCells(NCells, FTypes2, ColorsDict, CellsGrid4, CellsGrid3):   
    FTypeCells = np.zeros(NCells).astype(int)   #[]
    StatusCells = np.zeros(NCells).astype(int)  #[]
    RealCells = np.zeros(NCells).astype(int)    #[]
    Colors = []
    cellcounter=1

    # Populate Status, FType, IDs, and Color of the cells
    for i in range(NCells):
        if str.lower(CellsGrid4[i]) not in FTypes2.keys():
            #FTypeCells[i] = 0 #0.append(0)
            StatusCells[i] = 4 #.append(4)
            CellsGrid4[i] = "s1"
            #RealCells[i] = 0 #append(0)
        else:
            FTypeCells[i] = 2 #.append(2)
            #StatusCells[i] = 0 #.append(0)
            RealCells[i] = cellcounter #.append(cellcounter)
            cellcounter+=1

        if str(CellsGrid3[i]) not in ColorsDict.keys():
            Colors.append((1.0,1.0,1.0,1.0))

        if str(CellsGrid3[i]) in ColorsDict.keys():
            Colors.append(ColorsDict[str(CellsGrid3[i])])

    return FTypeCells, StatusCells, RealCells, Colors

