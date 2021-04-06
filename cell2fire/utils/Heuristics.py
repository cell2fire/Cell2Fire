# coding: utf-8
__version__ = "2.0"
__author__ = "Cristobal Pais, Jaime Carrasco"
__maintainer__ = "Jaime Carrasco, Cristobal Pais, David Woodruff"
__status__ = "Alpha Operational"

# Importations
import networkx as nx 
import seaborn as sns
import matplotlib

from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import rcParams
from matplotlib.pylab import *
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap

# General ones
import glob
import os
import numpy as np
import numpy.random as npr
import random

# Genetic algorithm 
from deap import algorithms, base, creator, tools
from scipy.ndimage.measurements import label

# Genetic selection object 
class GenHeur(object):
    # Constructor
    def __init__(self, Rows, Cols, FPVMatrix, verbose=False,
                 gaStats=False, ngen=500, npop=100, 
                 tSize=3, cxpb=0.8, mutpb=0.2, indpb=0.05):
    
        # Forest
        self._Rows = Rows
        self._Cols = Cols
        self._NCells = Rows * Cols
        self._FPVMatrix = FPVMatrix
    
        # Genetic alg parameters
        self._gaStats = gaStats
        self._ngen = ngen
        self._npop = npop
        self._tsize = tSize 
        self._cxpb = cxpb
        self._mutpb = mutpb
        self._indpb = indpb 
        
        # Extra
        self._verbose = verbose
        self._firstCall = True
        
        self._counter = 1
        self._a = []
                 
    
    # Genetic algorithm solution (for FPV maximization)
    def GeneticSel(self, AvailCells, VolCells, Demand, Utility, Year):
        # Auxiliary functions
        """
        Given an individual, check the number of adjacent components (in matricial form) 
        """
        def adjConstraint(individual):
            structure = np.ones((3, 3), dtype=np.int)
            labeled, ncomponents = label(individual, structure)
            return ncomponents
        """
        Given an individual, calculate the total fitness function as:
        Fitness = + FPV harvested: total FPV value harvested
                  - Demand deviation: penalty w.r.t. the extra/lower demand satisfaction
                  - Adjacency penalty: if cells are not adjacent (connected graph), 
                                       penalyze by the number of non-connected components
                  - Feasibility (availability) penalty: if a cell is not available, 
                                                        huge penalty since the solution
                                                        is not feasible
        """
        def evalFPV(individual, rhoDemand=10000, rhoAdj=1e6):
            # Maximize FPV
            mask = np.asarray(individual, dtype=np.bool)
            #print(individual, mask, self._FPVMatrix)
            sumFPV = np.sum(np.asarray(self._FPVMatrix)[mask])

            # Satisfy demand
            sumVol = np.sum(VolCells[mask])
            demandC = np.abs(sumVol - Demand[Year-1]) * rhoDemand

            # Satisfy adjacency
            adjC = 0
            nComp = adjConstraint(np.reshape(individual, (self._Rows, self._Cols)))
            if nComp > 1:
                adjC = (nComp - 1) * rhoAdj        

            # Feasible (harvesting available cells)
            feasC = 0
            HCells = np.arange(1, self._NCells + 1)
            HCells = HCells[mask]
            HCells = set(HCells)
            
            if len(HCells - AvailCells) > 0:
                feasC = 1e10

            # Total fitness
            fitness = sumFPV - demandC - adjC - feasC
            
            return (fitness,)
        
        """
        Individual initialization functions
        Creates a list of 0s-1s with 1s = demand/number of cells to be harvested
        CP: Will be modified to account for the volume or simply use random initialization.
        """
        def ddshf():
            a = np.zeros(self._NCells)
            idx = npr.randint(0, high=len(a), size=Demand[Year-1])
            a[idx] = 1
            return a
        def ddshfV2():
            if self._counter == 1:
                self._a = ddshf()
            
            aSel = npr.choice(self._a, replace=False)
        
            self._counter += 1
            if self._counter == self._NCells:
                self._counter = 1
                
            return aSel
                
        
        # Register relevant classes for the first call
        toolbox = base.Toolbox()
        if self._firstCall:
            # Create the problem: max fitness, list individuals
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
            creator.create("Individual", list, fitness=creator.FitnessMax)
            
        
        # Genes [0,1] at random
        toolbox.register("attr_bool", random.randint, 0, 1)
        toolbox.register("demand_shf", ddshfV2)

        # Individual (First version: Random, Second version: Initial individual satisfying demand (units))
        #toolbox.register("individual", tools.initRepeat, creator.Individual, 
        #                 toolbox.attr_bool, self._NCells)
        toolbox.register("individual", tools.initRepeat, creator.Individual, 
                         toolbox.demand_shf, self._NCells)

        
        # Population
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # Register Operations
        toolbox.register("evaluate", evalFPV)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutFlipBit, indpb=self._indpb)
        toolbox.register("select", tools.selTournament, tournsize=self._tsize)

        if self._gaStats:
            fit_stats = tools.Statistics(key=operator.attrgetter("fitness.values"))
            fit_stats.register('mean', np.mean)
            fit_stats.register('min', np.min)

        # Results
        pop = toolbox.population(n=self._npop)
        result, log = algorithms.eaSimple(pop, toolbox,
                                          cxpb=self._cxpb, mutpb=self._mutpb,
                                          ngen=self._ngen, verbose=False)

        best_individual = tools.selBest(result, k=1)[0]

        # Translate best individual to cells
        HCells = np.arange(1, self._NCells + 1)
        mask2 = np.asarray(best_individual, dtype=np.bool)
        HCells = set(HCells[mask2])
        
        # Print-out Information
        if self._verbose:
            print("Best individual:\n", np.reshape(best_individual, (self._Rows, self._Cols)))
            print('Fitness of the best individual:\n', evalFPV(best_individual)[0])
            print('Cells harvested:', HCells)

        # Update first call
        self._firstCall = False
        
        # Print fitness
        print("Total fitness (FPV):", evalFPV(best_individual))
        
        # Return harvested cells set 
        return HCells
    
    # Set FPV Matrix
    def setFPV(self, Matrix):
        self._FPVMatrix = Matrix
                        
    # set GeneticAlg Parameters
    def setGAParams(self, ngen, npop, tSize, cxpb, mutpb, indpb, gaStats=False):
        self._gaStats = gaStats
        self._ngen = ngen
        self._npop = npop
        self._tsize = tSize 
        self._cxpb = cxpb
        self._mutpb = mutpb
        self._indpb = indpb 
            

    # Properties
    @property
    def getFPVMatrix(self):
        return self._FPVMatrix


class Heuristic(object):
    # Initializer
    def __init__(self,
                 version=0,              # Heuristic ID
                 MessagePath="",         # Path to the messages (for FPV and graphs)
                 InFolder="",            # Instance Folder path
                 OutFolder="",           # Output Folder path
                 AvailCells=set(),       # AvailCells
                 BurntCells=set(),       # BurntCells
                 HarvestedCells=set(),   # Harvested Cells
                 AdjCells=[],            # Adjacent cells info
                 NCells=0,               # Number of cells inside the forest
                 Cols=0,                 # Number of columns inside the forest 
                 Rows=0,                 # Number of rows inside the forest
                 Year=1,                 # Current year
                 FPVGrids=False,         # Boolean flag: Generate FPV grids/Heatmaps
                 onlyGraphs=False,       # Boolean flag: do not use the heuristic but generate the messages graph
                 GeneticSelection=False, # Genetic algorithm for selecting the best connected patch (adjacency)
                 GreedySelection=True,   # Greedy selection (top to bottom) for adjacency constraints
                 verbose=False):         # Verbosity level (False = minimum)
        
        # Populate inner values
        self._version = version
        self._MessagePath = MessagePath
        self._InFolder = InFolder
        self._OutFolder = OutFolder
        self._AvailCells = AvailCells
        self._BurntCells = BurntCells
        self._HarvestedCells = HarvestedCells
        self._AdjCells = AdjCells
        self._NCells = NCells
        self._Cols = Cols
        self._Rows = Rows
        self._Year = Year
        self._FPVGrids = FPVGrids
        self._onlyGraphs = onlyGraphs
        self._GeneticSelection = GeneticSelection
        self._GreedySelection = GreedySelection
        self._verbose = verbose
        
        # Extra 
        self._FPVMatrix = []
        self._bp_val = [] 
        self._fpv_val = []
        
        # Adjacency constraint
        if self._version in [0,2,4,6,8,10,12,14,16,18]:
            self._Adj = False
        else:
            self._Adj = True

        # Title and labels
        if self._version == 11:
            self.Alg = "DPV"
        elif self._version == 9:
            self.Alg = "DPV_Vol"
        elif self._version == 19:
            self.Alg = "BC"
        elif self._version == 5:
            self.Alg = "BP"
        elif self._version == 10:
            self.Alg = "DPV_NoAdj"
        elif self._version == 18:
            self.Alg = "BC_NoAdj"
        elif self._version == 4:
            self.Alg = "BP_NoAdj"
        elif self._version == 0:
            self.Alg = "Random_NoAdj"
        elif self._version == 1:
            self.Alg = "Random"
        else:
            self.Alg = f"algorithm_{self._version}"
    
    # Init Graph for FPV based heuristics
    def initGraph_FPV(self, VolCells, ngen=500, npop=100, tSize=3, cxpb=0.8, mutpb=0.2, indpb=0.05, 
                      GPTree=False):
        
        # Read txt files with messages (array with name of files) 
        msgFiles = glob.glob(self._MessagePath + '/*.csv')
        nsim = len(msgFiles)

        # Info 
        if self._verbose:
            print("We have", nsim, "message files, generating the graphs...")

        # Keep FPV for each simulation 
        FPVMatrices = []

        # Graph generation
        nodes = range(1, self._NCells + 1)

        # We build a Digraph (directed graph, general graph for the instance)
        self._GGraph = nx.DiGraph()

        # We add nodes to the list
        self._GGraph.add_nodes_from(nodes)

        # Populate nodes fields for the general graph (no edges)
        for i in self._GGraph.nodes:
            self._GGraph.nodes[i]['price'] = 1
            self._GGraph.nodes[i]['vol'] = VolCells[i - 1]
            self._GGraph.nodes[i]['cost'] = 0
            self._GGraph.nodes[i]['profit'] = (self._GGraph.nodes[i]['price'] - self._GGraph.nodes[i]['cost']) *\
                                              self._GGraph.nodes[i]['vol']
            if GPTree is False:
                self._GGraph.nodes[i]['fpv'] = 0
            else:
                self._GGraph.nodes[i]['fpv'] = VolCells[i - 1]

        # For each simulation, we create a graph with edges containing time and ROS at the moment of the message
        for k in range(1, nsim + 1):
            msgFileName = "MessagesFile0" if (k < 10) else "MessagesFile"
            self._HGraphs = nx.read_edgelist(path=self._MessagePath + '/'+ msgFileName + str(k) + '.csv',
                                             create_using=nx.DiGraph(),
                                             nodetype=int,
                                             data=[('time', float), ('ros', float)],
                                             delimiter=',')

            # Assign the profit from the main graph
            for i in self._HGraphs.nodes:
                self._HGraphs.nodes[i]['profit'] = self._GGraph.nodes[i]['profit']
                self._HGraphs.nodes[i]['fpv'] = VolCells[i - 1]

            # Tree dictionary
            Tree = dict()

            # Aux FPV Matrix for individual FPV values
            AuxFPVMatrix = np.zeros([self._Rows, self._Cols])

            # For each nodes inside the simulation graphs, calculate the FPV based on the descendants
            # Call the FPV function and update the HGraph
            alpha = None
            basic = True        # Version = 8 or 9 (even are no adjacent) default
            degreeW = False
            layerDecay = False
            AvgTime = False
            hitTime = False
            All = False
            old = False
            bcentrality = False
            
            # Version 
            if self._version == 6 or self._version == 7:
                old = True
                basic = False
                
            elif self._version == 10 or self._version == 11:
                basic = False
                degreeW = True
                    
            elif self._version == 12 or self._version == 13:
                basic = False
                degreeW = True
                hitTime = True
                
            elif self._version == 14 or self._version == 15:
                basic = False
                degreeW = True
                hitTime = True
                layerDecay = True
                
            elif self._version == 16 or self._version == 17:
                basic = False
                All = True
                
            elif self._version == 18 or self._version == 19:
                basic = False
                bcentrality = True
                
            
            # Add edges to G including the frequency of the message from one cell to another
            for e in self._HGraphs.edges():
                #print("e:",e, e[0],e[1])
                if self._GGraph.has_edge(*e):
                    self._GGraph.get_edge_data(e[0], e[1])["weight"] += 1
                else:
                    self._GGraph.add_weighted_edges_from([(*e,1.)])
            
            # Graph: Compute the VaR for each Propagation Tree and then sum all of them 
            if GPTree is False:
                self._HGraphs = self.FPV(self._HGraphs, tFactor=60., alpha=alpha, basic=basic, degreeW=degreeW, 
                                         layerDecay=layerDecay, AvgTime=AvgTime, hitTime=hitTime, All=All, Old=old,
                                         bcentrality=bcentrality)

                # Sum the FPV to the G Graph
                for i in self._HGraphs.nodes:
                    self._GGraph.nodes[i]['fpv'] += self._HGraphs.nodes[i]['fpv']

                    if self._FPVGrids:
                        AuxFPVMatrix[(i-1)//self._Cols, i - self._Cols * ((i-1)//self._Cols) - 1 ] = self._HGraphs.nodes[i]['fpv']
                                
            
                # Append the instance FPV matrix 
                if self._FPVGrids:
                    FPVPaths = os.path.join(self._OutFolder, "FPVMatrices")
                    if not os.path.exists(FPVPaths):
                        os.makedirs(FPVPaths)
                    FPVMatrices.append(AuxFPVMatrix)
                    np.savetxt(os.path.join(FPVPaths, "FPV_Matrix_" + str(k) + ".csv"),
                               AuxFPVMatrix, delimiter=" ", fmt="%.f")
                
                # Check FPVMatrices
                if self._verbose:
                    print("FPV Matrices:\n", FPVMatrices)
            
        
        # Otherwise, compute the VaR of the Global Propagation Tree generated
        if GPTree:
            self._GGraph = self.FPV(self._GGraph, tFactor=60., alpha=alpha, basic=basic, degreeW=degreeW, 
                                    layerDecay=layerDecay, AvgTime=AvgTime, hitTime=hitTime, All=All, Old=old,
                                    bcentrality=bcentrality, GPTree=GPTree)
        
        # Total / Average FPV Matrix
        self._FPVMatrix = np.zeros([self._Rows, self._Cols])
        for i in self._GGraph.nodes():
            self._FPVMatrix[(i-1)//self._Cols, i - self._Cols * ((i-1)//self._Cols) - 1 ] = self._GGraph.nodes[i]['fpv']
            if self._verbose:
                print("FPV Matrix:\n", self._FPVMatrix)
        
        if self._FPVGrids:
            # Record global FPV values to matrices
            np.savetxt(os.path.join(self._OutFolder, "Global_" + self.Alg + "_Matrix.csv"), 
                       self._FPVMatrix, delimiter=" ", fmt="%.f")
            np.savetxt(os.path.join(self._OutFolder, "Global_" + self.Alg + "_Matrix_Normalized.csv"), 
                       self._FPVMatrix / np.max(self._FPVMatrix), delimiter=" ", fmt="%.3f")
            np.savetxt(os.path.join(self._OutFolder, "Global_FPV_Matrix.csv"), 
                       self._FPVMatrix, delimiter=" ", fmt="%.f")
            np.savetxt(os.path.join(self._OutFolder, "Global_FPV_Matrix_Normalized.csv"), 
                       self._FPVMatrix / np.max(self._FPVMatrix), delimiter=" ", fmt="%.3f")
            
            
    
        # Genetic selection
        if self._GeneticSelection:        
            # GA object
            self._GA = GenHeur(self._Rows, 
                               self._Cols, 
                               np.reshape(self._FPVMatrix, (self._NCells,)), 
                               self._verbose, 
                               ngen=ngen, npop=npop, 
                               tSize=tSize, cxpb=cxpb, 
                               mutpb=mutpb, indpb=indpb)
   
    # Init Grah for BurntProb heuristic
    def initGraph_BP(self, BPExisting=False):
        # Read txt files with messages (array with name of files) 
        msgFiles = glob.glob(self._MessagePath + '/*.txt')
        nsim = len(msgFiles)
        
        if self._verbose:
            print("We have", nsim, "message files, generating the BP graphs...")
        
        # Generate graph
        nodes = range(1, self._NCells + 1)

        # We build a multigraph (directed graph)
        self._GGraph = nx.MultiDiGraph()
        
        # If BP matrix already inside the OutputFolder, we do not need to read the messages
        if BPExisting:
            pass
            
        # Else, we generate the graph from scratch 
        else:
            # We add nodes to the nodes list of G
            self._GGraph.add_nodes_from(nodes)
            for i in self._GGraph.nodes:
                self._GGraph.nodes[i]['freq_burn'] = 0

            for k in range(1, nsim + 1):
                # Read the message files
                self._HGraphs = nx.read_edgelist(path=self._MessagePath + '/MessagesFile' + str(k) + '.txt',
                                                 create_using=nx.MultiDiGraph(),
                                                 nodetype=int,
                                                 data=[('time', float), ('ros', float)])

                self._GGraph.add_weighted_edges_from(self._HGraphs.edges(data='time'), weight='time')
                for i in self._HGraphs.nodes:
                    self._GGraph.nodes[i]['freq_burn'] = self._GGraph.nodes[i]['freq_burn'] + 1
                    
    
    # DPV calculations (all versions)
    def FPV(self, Graph, tFactor=60., alpha=None, basic=True, degreeW=False, 
            layerDecay=False, AvgTime=False, hitTime=False, All=False, Old=False,
            bcentrality=False, GPTree=False):

        # Containers
        Trees = {}
        
        # Info
        if self._verbose:
            print("----- FPV Calculation ------")
            print("\tBasic:", basic)
            print("\tDegree:", degreeW)
            print("\tLayer:", layerDecay)
            print("\tAVGTime:", AvgTime)
            print("\tHit Time:", hitTime)
            print("\tOlf FPV:", Old)
            print("\tBCentrality:", bcentrality)
            print("\tGPTree:", GPTree)
            print("----------------------------")

        # Burnt Probability for Adapted FPV 
        if GPTree:
            # Initialize BP values if needed
            if len(self._bp_val) == 0:
                BProb = np.loadtxt(os.path.join(self._OutFolder[:-9], "Stats", "BProb.csv"), 
                                   delimiter=" ", dtype=np.float32)
                BProb = np.reshape(BProb, (self._Rows * self._Cols,))
            else:
                BProb = self._bp_val
                
        else:
            BProb = np.ones(self._Rows * self._Cols)
                
        
        # Special Case: Betweenness centrality does not need calculations per nodes
        if bcentrality is False:
            # Main Loop
            for i in Graph.nodes:
                if self._verbose:
                    print("Processing nodes:", i)

                # Layer Decay components
                if layerDecay:
                    # Shortest paths dictionary
                    SP = nx.shortest_path_length(Graph, source=i, weight=None)

                # AVG Time components
                if AvgTime:
                    # Reset layers Times and nodes to layers dict
                    LayersT = []
                    NodesL = {}

                    # Calculate LP for the current nodes
                    LP = nx.single_source_shortest_path_length(Graph, source=i, cutoff=1e7)
                    LP = np.max([i for i in LP.values()])

                    # Get nodes from layer
                    for l in range(1, LP + 1):
                        # Nodes from the layer
                        LNodes = nx.single_source_shortest_path_length(Graph, source=i, cutoff=l)
                        LNodes = [i for i in LNodes.keys() if LNodes[i] == l]

                        # Populate dictionary Node to layer
                        for n in LNodes:
                            NodesL[n] = l

                        # Array with traveling times to nodes in the layer
                        LayerT = np.empty(len(LNodes))
                        aux = 0

                        # For each nodes, get the hitting time and then calculate the mean hit time of the layer
                        for r in LNodes:
                            LayerT[aux] = Graph.in_degree(nbunch=r, weight='time')
                            aux += 1

                        # Append the mean time of the layer to global array
                        LayersT.append(np.mean(LayerT) / tFactor)    

                # If hitTime, we compute the time correction value
                if hitTime:
                    # Time correction: indegree time for propagating adjusted time downstream
                    tCorrection = Graph.in_degree(nbunch=i, weight='time')
                    #print("Time correction nodes", i,":", tCorrection)

                # Get sub graph starting from i
                Trees[i] = nx.subgraph(Graph, {i} | nx.descendants(Graph, i))

                ##############################################################################################################

                # Trio of FPV  
                if AvgTime * layerDecay * degreeW:
                    Graph.nodes[i]['fpv'] = (sum([Graph.nodes[j]['fpv'] * (1 / SP[j]) * (1 / LayersT[NodesL[j]-1]) \
                                                   for j in Trees[i].nodes if j != i]) \
                                                   + Graph.nodes[i]['fpv']) * Graph.degree(i, weight="weight")

                elif hitTime * layerDecay * degreeW:
                    Graph.nodes[i]['fpv'] = (sum([Graph.nodes[j]['fpv'] * (1 / SP[j]) *\
                                                  (tFactor / ( Graph.in_degree(nbunch=j, weight='time') - tCorrection) ) \
                                                   for j in Trees[i].nodes if j != i]) + \
                                                   Graph.nodes[i]['fpv']) * Graph.degree(i, weight="weight")

                elif hitTime * AvgTime * degreeW:
                    GraphG.nodes[i]['fpv'] = (sum([Graph.nodes[j]['fpv'] *\
                                                   (tFactor / ( Graph.in_degree(nbunch=j, weight='time') - tCorrection) ) *\
                                                   (1 / LayersT[NodesL[j]-1]) for j in Trees[i].nodes if j != i]) \
                                                   + Graph.nodes[i]['fpv']) * Graph.degree(i, weight="weight")

                elif AvgTime * layerDecay * hitTime:
                    Graph.nodes[i]['fpv'] = (sum([Graph.nodes[j]['fpv'] * (1 / SP[j]) *\
                                                  (tFactor / ( Graph.in_degree(nbunch=j, weight='time') - tCorrection) ) *\
                                                  (1 / LayersT[NodesL[j]-1]) for j in Trees[i].nodes if j != i]) + \
                                                  Graph.nodes[i]['fpv']) * Graph.degree(i, weight="weight")

                ##############################################################################################################

                # Pairs of FPV  
                elif AvgTime * degreeW:
                    Graph.nodes[i]['fpv'] = (sum([Graph.nodes[j]['fpv'] * (1 / LayersT[NodesL[j]-1]) for j in Trees[i].nodes if j != i]) \
                                        + Graph.nodes[i]['fpv']) * Graph.degree(i, weight="weight")

                elif layerDecay * degreeW:
                    Graph.nodes[i]['fpv'] = (sum([Graph.nodes[j]['fpv'] * (1 / SP[j]) for j in Trees[i].nodes if j != i]) + \
                                        Graph.nodes[i]['fpv']) * Graph.degree(i, weight="weight")

                elif hitTime * degreeW:
                    Graph.nodes[i]['fpv'] = (sum([Graph.nodes[j]['fpv'] * \
                                            (tFactor / ( Graph.in_degree(nbunch=j, weight='time') - tCorrection) ) \
                                             for j in Trees[i].nodes if j != i]) + \
                                         Graph.nodes[i]['fpv']) * Graph.degree(i, weight="weight")

                elif layerDecay * AvgTime:
                    Graph.nodes[i]['fpv'] = (sum([Graph.nodes[j]['fpv'] * (1 / SP[j]) * (1 / LayersT[NodesL[j]-1]) \
                                             for j in Trees[i].nodes if j != i]) \
                                        + Graph.nodes[i]['fpv'])

                elif hitTime * AvgTime:
                    Graph.nodes[i]['fpv'] = (sum([Graph.nodes[j]['fpv'] * \
                                            (tFactor / ( Graph.in_degree(nbunch=j, weight='time') - tCorrection) ) * \
                                            (1 / LayersT[NodesL[j]-1]) for j in Trees[i].nodes if j != i]
                                            ) + Graph.nodes[i]['fpv'])

                elif hitTime * layerDecay:
                    Graph.nodes[i]['fpv'] = (sum([Graph.nodes[j]['fpv'] * \
                                            (tFactor / ( Graph.in_degree(nbunch=j, weight='time') - tCorrection) ) *\
                                            (1 / SP[j]) for j in Trees[i].nodes if j != i]
                                           ) + Graph.nodes[i]['fpv'])

                ##############################################################################################################

                # Individual FPV approaches (5)
                elif basic:
                    Graph.nodes[i]['fpv'] = sum([Graph.nodes[j]['fpv'] for j in Trees[i].nodes])   

                elif degreeW:
                    E = np.zeros(2)
                    E[0] = 1
                    E[1] = 1000
                    Graph.nodes[i]['fpv'] = (sum([Graph.nodes[j]['fpv']*E[0] for j in Trees[i].nodes if j != i]) + Graph.nodes[i]['fpv']) *\
                                        Graph.degree(i, weight="weight")

                elif AvgTime:
                    Graph.nodes[i]['fpv'] = (sum([Graph.nodes[j]['fpv'] * (1 / LayersT[NodesL[j]-1]) for j in Trees[i].nodes if j != i]) +\
                                        Graph.nodes[i]['fpv'])

                elif layerDecay:
                    Graph.nodes[i]['fpv'] = (sum([Graph.nodes[j]['fpv'] * (1 / SP[j]) for j in Trees[i].nodes if j != i]) + \
                                        Graph.nodes[i]['fpv'])

                elif hitTime:
                    Graph.nodes[i]['fpv'] = (sum([Graph.nodes[j]['fpv'] * \
                                            (tFactor / ( Graph.in_degree(nbunch=j, weight='time') - tCorrection) ) \
                                             for j in Trees[i].nodes if j != i]) + Graph.nodes[i]['fpv'])

                ##############################################################################################################

                # Old FPV version (Palma et. al)
                elif Old:                
                    # Root
                    if len(nx.ancestors(Graph, source=i)) == 0:
                        Graph.nodes[i]['fpv'] = self.FPVsource(source=i, G=Graph) * BProb[i - 1]
                    # No root
                    else:
                        Graph.nodes[i]['fpv'] = self.FPVnodes(source=i, G=Graph) * BProb[i - 1]


                ##############################################################################################################

        # BCentrality calculations
        else:
            # Weighted by freq (Global Propagation Tree version)
            if GPTree:
                fpv_av = nx.betweenness_centrality(self._GGraph, k=None, normalized=True, 
                                                   weight="weight", endpoints=False, seed=None)
            # Raw
            else:
                fpv_av = nx.betweenness_centrality(self._GGraph, k=None, normalized=True, 
                                                   weight=None, endpoints=False, seed=None)
            # Fill fpv values
            for i in Graph.nodes:
                Graph.nodes[i]['fpv'] = fpv_av[i]
                
            
        
        # Display info
        if self._verbose:
            print("---- FPV ----")
            print(Graph.nodes(data=True))
            
            for i in Graph.nodes:
                print("Node", i, "FPV =", Graph.nodes[i]["fpv"])
                    
        
        # Return graph
        return Graph
                    
    
    # Palma FPV calculations
    def FPVsource(self, source, G):
        fpv = 0
        for i in nx.descendants(G, source=source):
            for j in nx.descendants(G, source=i):
                if j != i:
                    Paths = nx.simple_paths.all_simple_paths(G=G, cutoff=1e10, source=i, target=j)
                    for p in Paths:
                        fpv += G.nodes[p[-1]]['fpv']
        return fpv
    def FPVnodes(self, source, G):
        fpv = 0
        for i in nx.ancestors(G, source=source):
            for j in nx.descendants(G, source=source):
                if j != i:
                    Paths = nx.simple_paths.all_simple_paths(G=G, cutoff=1e10, source=i, target=j)
                    for p in Paths:
                        fpv += G.nodes[p[-1]]['fpv']

        for i in nx.descendants(G, source=source):
            for j in nx.descendants(G, source=source):
                if j != i:
                    Paths = nx.simple_paths.all_simple_paths(G=G, cutoff=1e10, source=i, target=j)
                    for p in Paths:
                        fpv += G.nodes[p[-1]]['fpv']
        return fpv

    # Run the curret heuristic        
    def runHeur(self, AvailCells, Adjacents, VolCells, Demand, Utility, Year):
        # Initialize toHarvestCells set (cells to be harvested this period)
        toHarvestCells = set()

        # Demand should be at least 1 if non negative
        if Demand == 0:
            Demand = 1
        # If -1, run the forest without any harvesting plan 
        if Demand < 0:
            Demand = 0
        
        # Genetic Selection
        if self._GeneticSelection and self._GreedySelection is False:
            # GA Parameters
            #self._GA.setGAParams(ngen=1000, npop=200, tSize=3, cxpb=0.8, 
            #                     mutpb=0.2, indpb=0.05, gaStats=False)
            
            # Info if nooutput false
            print("--------- Using Genetic Selection --------")
            print("ngen:\t", self._GA._ngen, 
                  "\nnpop:\t", self._GA._npop,
                  "\ntsize:\t", self._GA._tsize,
                  "\ncxpb:\t", self._GA._cxpb,
                  "\nmutpb:\t", self._GA._mutpb,
                  "\nindpb:\t", self._GA._indpb)

            # Get action
            toHarvestCells = self._GA.GeneticSel(AvailCells, VolCells, Demand, 
                                                 Utility, Year)
        
        # Greedy Selection 
        elif self._GreedySelection and self._GeneticSelection is False:
            # Global vars
            aux_util = {}
            HCs = []
            TotalProduction = 0
            TotalUtility = 0

            # Check if adjacency constraint is active
            print("Adjacent Constraint:", self._Adj)

            ''' First version (0): Random selection, no adjacency'''
            # If version = 0, Random no Adjacent
            if self._version == 0:
                if self._verbose:
                    print("----- Random Selection Version (no adjacent, version", self._version, ") ------")

                if self._verbose:
                    print("Initial values")
                    print("\ttoHarvestCells:", toHarvestCells)
                    print("\tTotal Production:", TotalProduction)
                    print("\tTotal Utility:", TotalUtility)

                # Main loop for satisfying the demand
                toSelect = np.asarray([i for i in AvailCells])
                randomCells = npr.choice(toSelect, replace=False, size=Demand)
                toHarvestCells |= set(randomCells)
                AvailCells -= set(randomCells)
                HCs += list(randomCells - 1)
                TotalProduction += VolCells[randomCells - 1]
                TotalUtility += Utility[randomCells - 1]

                if self._verbose:
                    print("--- Adding", randomCell, "to the harvested cells ---")
                    print("\ttoHarvestCells:", toHarvestCells)
                    print("\tTotal Production:", TotalProduction)
                    print("\tTotal Utility:", TotalUtility)
                    
                    
            
            ''' Second version (1): Random selection, adjacency'''
            # If version = 1, Random Adjacent
            if self._version == 1:
                if self._verbose:
                    print("----- Random Selection Version (adjacent, version", self._version, ") ------")

                # Initialize utility dictionary
                for i in AvailCells:
                    aux_util[i] = Utility[i-1]

                # Get indexes in decreasing value order (FPV)
                idx = sorted(aux_util, key = aux_util.__getitem__, reverse=True)
                if self._verbose:
                    print("idx:", idx)

                # Random selection 
                toSelect = np.asarray([i for i in AvailCells])
                randomCells = npr.choice(toSelect, replace=False, size=1)
                AvailCells -= set(randomCells)
                    
                # Iintialize Harvested cells array
                HCs += list(randomCells - 1)

                # Update auxiliary sets
                toHarvestCells = set(randomCells)
                AdjHarvested = set([adj[0] for adj in Adjacents[randomCells[0] - 1].values() if adj != None])
                TotalProduction += VolCells[randomCells[0] - 1]
                TotalUtility += Utility[randomCells[0] - 1]
                j = 0

                if self._verbose:
                    print("Initial values")
                    print("\ttoHarvestCells:", toHarvestCells)
                    print("\tAdjHarvested:", AdjHarvested)
                    print("\tTotal Production:", TotalProduction)
                    print("\tTotal Utility:", TotalUtility)

                # Auxiliary flag
                noUpdate = True
                
                # Main loop for satisfying the demand
                while TotalProduction < Demand:
                    noUpdate = True
                    # Greedy Selection
                    if self._GreedySelection:
                        for j in range(len(idx.copy())):
                            # If cell is adjacent to the previous harvested, harvest it (greedy)
                            if idx[j] in AdjHarvested and idx[j] in AvailCells:
                                toAdd = idx.pop(j)
                                toHarvestCells.add(toAdd)
                                HCs += [toAdd]

                                # Adjacent constraint
                                ADJ = set([adj[0] for adj in Adjacents[toAdd - 1].values() if adj != None])
                                AdjHarvested |= ADJ
                                AdjHarvested.remove(toAdd)
                                AvailCells -= set([toAdd])
                                TotalProduction += VolCells[toAdd - 1]
                                TotalUtility += Utility[toAdd - 1]
                                noUpdate=False
                                                                        
                                if self._verbose:
                                    print("--- Adding", toAdd, "to the harvested cells ---")
                                    print("\ttoHarvestCells:", toHarvestCells)
                                    print("\tAdjHarvested:", AdjHarvested)
                                    print("\tTotal Production:", TotalProduction)
                                    print("\tTotal Utility:", TotalUtility)
                                    print("j:", j)

                                # Break for loop, 
                                break 
                                    
                            
                        
                        # Check if for loop did not update the harvesting plan (break while, infeasible)
                        if noUpdate:
                            print("Demand was not satisfied... Infeasible period", Year)
                            break

                    # Genetic Selection
                    elif self._GeneticSelection:
                        # To be implemented
                        pass

                     
            
            ''' Third version (2): Economical selection, no adjacency (TODO)'''
            # Economical value no adjacency
            if self._version == 2:
                if self._verbose:
                    print("----- Profit Heuristic Version ( no adjacent, version", self._version, ") ------")

                # Initialize utility dictionary
                for i in AvailCells:
                    aux_util[i] = Utility[i-1]

                # Get indexes in decreasing value order (FPV)
                idx = sorted(aux_util, key = aux_util.__getitem__, reverse=True)
                if self._verbose:
                    print("idx:", idx)

               # Initialize Harvested cells array
                HCs = HCs + [idx[:Demand]]
                
                # Update auxiliary sets
                toHarvestCells = set(idx[:Demand])
                TotalProduction += VolCells[np.asarray(idx[:Demand]).astype(np.int) - 1]
                TotalUtility += Utility[np.asarray(idx[:Demand]).astype(np.int) - 1]
                
                if self._verbose:
                    print("Initial values")
                    print("\ttoHarvestCells:", toHarvestCells)
                    print("\tTotal Production:", TotalProduction)
                    print("\tTotal Utility:", TotalUtility)

            ''' Forth version (3): Economical selection, adjacency (TODO)'''
            # Economical value, adjacency
            if self._version == 3:
                if self._verbose:
                    print("----- Economic Heuristic Version ( adjacent, version", self._version, ") ------")

                # Initialize utility dictionary
                for i in AvailCells:
                    aux_util[i] = Utility[i-1]

                # Get indexes in decreasing value order (FPV)
                idx = sorted(aux_util, key = aux_util.__getitem__, reverse=True)
                if self._verbose:
                    print("idx:", idx)

                # Iintialize Harvested cells array
                HCs = HCs + [idx[0]]

                # Update auxiliary sets
                toHarvestCells = set([idx[0]])
                AdjHarvested = set([adj[0] for adj in Adjacents[idx[0] - 1].values() if adj != None])
                TotalProduction += VolCells[idx[0] - 1]
                TotalUtility += Utility[idx[0] - 1]
                j = 1

                if self._verbose:
                    print("Initial values")
                    print("\ttoHarvestCells:", toHarvestCells)
                    print("\tAdjHarvested:", AdjHarvested)
                    print("\tTotal Production:", TotalProduction)
                    print("\tTotal Utility:", TotalUtility)

                # Auxiliary flag
                noUpdate = True
                
                # Main loop for satisfying the demand
                while TotalProduction <= Demand:
                    noUpdate = True
                    # Greedy Selection
                    if self._GreedySelection:
                        for j in range(len(idx.copy())):
                            # If cell is adjacent to the previous harvested, harvest it (greedy)
                            if idx[j] in AdjHarvested and idx[j] in AvailCells:
                                toAdd = idx.pop(j)
                                toHarvestCells.add(toAdd)
                                HCs += [toAdd]

                                # Adjacent constraint
                                ADJ = set([adj[0] for adj in Adjacents[toAdd - 1].values() if adj != None])
                                AdjHarvested |= ADJ
                                AdjHarvested.remove(toAdd)
                                AvailCells -= set([toAdd])
                                TotalProduction += VolCells[toAdd - 1]
                                TotalUtility += Utility[toAdd - 1]
                                noUpdate=False
                                                                        
                                if self._verbose:
                                    print("--- Adding", toAdd, "to the harvested cells ---")
                                    print("\ttoHarvestCells:", toHarvestCells)
                                    print("\tAdjHarvested:", AdjHarvested)
                                    print("\tTotal Production:", TotalProduction)
                                    print("\tTotal Utility:", TotalUtility)
                                    print("j:", j)

                                # Break for loop, 
                                break 
                                    
                            
                        
                        # Check if for loop did not update the harvesting plan (break while, infeasible)
                        if noUpdate:
                            print("Demand was not satisfied... Infeasible period", Year)
                            break

                    # Genetic Selection
                    elif self._GeneticSelection:
                        # To be implemented
                        pass
            
            ''' Forth version (4): Burnt Probability selection, no adjacency'''
            # Burnt Probability no adjacency
            if self._version == 4:
                if self._verbose:
                    print("----- BP Heuristic Version ( no adjacent, version", self._version, ") ------")

                # Initialize BP values if needed
                if len(self._bp_val) == 0:
                    self._bp_val = np.loadtxt(os.path.join(self._OutFolder[:-9], "Stats", "BProb.csv"), 
                                              delimiter=" ", dtype=np.float32)
                    self._bp_val = np.reshape(self._bp_val, (self._Rows * self._Cols,))

                # Initialize utility dictionary
                for i in AvailCells:
                    aux_util[i] = self._bp_val[i-1]

                # Get indexes in decreasing value order (FPV)
                idx = sorted(aux_util, key = aux_util.__getitem__, reverse=True)
                if self._verbose:
                    print("idx:", idx)
                    print("Total harvested:", len(idx[:Demand]))
                print("Demand:", Demand)
                
                
                # Initialize Harvested cells array
                HCs = HCs + [idx[:Demand]]
                
                # Update auxiliary sets
                toHarvestCells = set(idx[:Demand])
                TotalProduction += VolCells[np.asarray(idx[:Demand]).astype(np.int) - 1]
                TotalUtility += Utility[np.asarray(idx[:Demand]).astype(np.int) - 1]
                
                if self._verbose:
                    print("Initial values")
                    print("\ttoHarvestCells:", toHarvestCells)
                    print("\tTotal Production:", TotalProduction)
                    print("\tTotal Utility:", TotalUtility)
                
            
            ''' Fifth version (5): Burnt Probability selection, adjacency'''
            # Burnt Probability, adjacency
            if self._version == 5:
                if self._verbose:
                    print("----- BP Heuristic Version ( adjacent, version", self._version, ") ------")

                # Initialize BP values if needed
                if len(self._bp_val) == 0:
                    self._bp_val = np.loadtxt(os.path.join(self._OutFolder[:-9], "Stats", "BProb.csv"), 
                                              delimiter=" ", dtype=np.float32)
                    self._bp_val = np.reshape(self._bp_val, (self._Rows * self._Cols,))
                    
                # Initialize utility dictionary
                for i in AvailCells:
                    aux_util[i] = self._bp_val[i-1]

                # Get indexes in decreasing value order (FPV)
                idx = sorted(aux_util, key = aux_util.__getitem__, reverse=True)
                if self._verbose:
                    print("idx:", idx)

                # Iintialize Harvested cells array
                HCs = HCs + [idx[0]]

                # Update auxiliary sets
                toHarvestCells = set([idx[0]])
                AdjHarvested = set([adj[0] for adj in Adjacents[idx[0] - 1].values() if adj != None])
                AvailCells -= set([idx[0]])
                TotalProduction += VolCells[idx[0] - 1]
                TotalUtility += Utility[idx[0] - 1]
                j = 1

                if self._verbose:
                    print("Initial values")
                    print("\ttoHarvestCells:", toHarvestCells)
                    print("\tAdjHarvested:", AdjHarvested)
                    print("\tTotal Production:", TotalProduction)
                    print("\tTotal Utility:", TotalUtility)

                # Auxiliary flag
                noUpdate = True
                
                # Main loop for satisfying the demand
                while TotalProduction < Demand:
                    noUpdate = True
                    # Greedy Selection
                    if self._GreedySelection:
                        for j in range(len(idx.copy())):
                            # If cell is adjacent to the previous harvested, harvest it (greedy)
                            if idx[j] in AdjHarvested and idx[j] in AvailCells:
                                toAdd = idx.pop(j)
                                toHarvestCells.add(toAdd)
                                HCs += [toAdd]

                                # Adjacent constraint
                                ADJ = set([adj[0] for adj in Adjacents[toAdd - 1].values() if adj != None])
                                AdjHarvested |= ADJ
                                AdjHarvested.remove(toAdd)
                                AvailCells -= set([toAdd])
                                TotalProduction += VolCells[toAdd - 1]
                                TotalUtility += Utility[toAdd - 1]
                                noUpdate=False
                                                                        
                                if self._verbose:
                                    print("--- Adding", toAdd, "to the harvested cells ---")
                                    print("\ttoHarvestCells:", toHarvestCells)
                                    print("\tAdjHarvested:", AdjHarvested)
                                    print("\tTotal Production:", TotalProduction)
                                    print("\tTotal Utility:", TotalUtility)
                                    print("j:", j)

                                # Break for loop, 
                                break 
                                    
                            
                        
                        # Check if for loop did not update the harvesting plan (break while, infeasible)
                        if noUpdate:
                            print("Demand was not satisfied... Infeasible period", Year)
                            break

                    
                    elif self._GeneticSelection:
                        # To be implemented
                        pass

            ''' Sixth version (6): FPV Palma et al selection, no adjacency (TEST)'''
            # FPV Palma et al (to be added in new format)
            if self._version == 6:
                if self._verbose:
                    print("----- FPV Old Heuristic Version", self._version, "------")
                fpv_av = dict(self._GGraph.nodes(data='fpv'))
                if self._verbose:
                    print("FPV from G:\n", fpv_av)

                # Initialize utility dictionary
                for i in AvailCells:
                    aux_util[i] = fpv_av[i]

                # Get indexes in decreasing value order (FPV)
                idx = sorted(aux_util, key = aux_util.__getitem__, reverse=True)                
                if self._verbose:
                    print(idx)
                    print("")
                    print(idx[:Demand])  
                    
                # No Adjacency
                # Initialize Harvested cells array
                HCs = HCs + [idx[:Demand]]

                # Update auxiliary sets
                toHarvestCells = set(idx[:Demand])
                TotalProduction += VolCells[np.asarray(idx[:Demand]).astype(np.int) - 1]
                TotalUtility += Utility[np.asarray(idx[:Demand]).astype(np.int) - 1]
                AvailCells -= set(idx[:Demand])

                # Information
                if self._verbose:
                    print("Initial values")
                    print("\ttoHarvestCells:", toHarvestCells)
                    print("\tTotal Production:", TotalProduction)
                    print("\tTotal Utility:", TotalUtility)
                    
                    
                    

            ''' Sixth version (7): FPV Palma et al selection, adjacency (TEST)'''
            # FPV Palma et al (to be added in new format)
            if self._version == 7:
                if self._verbose:
                    print("----- FPV Old Heuristic Adj Version", self._version, "------")
                fpv_av = dict(self._GGraph.nodes(data='fpv'))
                if self._verbose:
                    print("FPV from G:\n", fpv_av)

                # Initialize utility dictionary
                for i in AvailCells:
                    aux_util[i] = fpv_av[i]

                # Get indexes in decreasing value order (FPV)
                idx = sorted(aux_util, key = aux_util.__getitem__, reverse=True)                
                if self._verbose:
                    print(idx)
                    print("")
                    print(idx[:Demand])  
                    
                # Iintialize Harvested cells array
                HCs = HCs + [idx[0]]

                # Update auxiliary sets
                toHarvestCells = set([idx[0]])
                AdjHarvested = set([adj[0] for adj in Adjacents[idx[0] - 1].values() if adj != None])
                TotalProduction += VolCells[idx[0] - 1]
                TotalUtility += Utility[idx[0] - 1]
                j = 1

                # Info
                if self._verbose:
                    print("Initial values")
                    print("\ttoHarvestCells:", toHarvestCells)
                    print("\tAdjHarvested:", AdjHarvested)
                    print("\tTotal Production:", TotalProduction)
                    print("\tTotal Utility:", TotalUtility)
                    
                # Main loop for satisfying the demand (Adjacency version)
                noUpdate = True
                while TotalProduction <= Demand and Demand > 1:
                    noUpdate = True
                    # Greedy Selection
                    if self._GreedySelection:
                        for j in range(len(idx.copy())):
                            # If cell is adjacent to the previous harvested, harvest it (greedy)
                            if idx[j] in AdjHarvested and idx[j] in AvailCells:
                                toAdd = idx.pop(j)
                                toHarvestCells.add(toAdd)
                                HCs += [toAdd]

                                # Adjacent constraint
                                ADJ = set([adj[0] for adj in Adjacents[toAdd - 1].values() if adj != None])
                                AdjHarvested |= ADJ
                                AdjHarvested.remove(toAdd)
                                AvailCells -= set([toAdd])
                                TotalProduction += VolCells[toAdd - 1]
                                TotalUtility += Utility[toAdd - 1]
                                noUpdate=False
                                
                                if self._verbose:
                                    print("--- Adding", toAdd, "to the harvested cells ---")
                                    print("\ttoHarvestCells:", toHarvestCells)
                                    print("\tAdjHarvested:", AdjHarvested)
                                    print("\tTotal Production:", TotalProduction)
                                    print("\tTotal Utility:", TotalUtility)
                                    print("j:", j)
                                    
                                # Break for loop
                                break 
                                    
                            
                        # Check if for loop did not update the harvesting plan (break while, infeasible)
                        if noUpdate:
                            print("Demand was not satisfied... Infeasible period", Year)
                            break

                    elif self._GeneticSelection:
                        # To be implemented
                        pass    
                
                
                
                    
                
            
            ''' Rest of versions (8-18): Downstream Protection Value'''
            # New FPV 
            if self._version in np.arange(8,18):
                if self._verbose:
                    print("----- DPV Heuristic Version", self._version, "------")
                fpv_av = dict(self._GGraph.nodes(data='fpv'))
                if self._verbose:
                    print("DPV from G:\n", fpv_av)

                # Initialize utility dictionary
                for i in AvailCells:
                    aux_util[i] = fpv_av[i]

                # Get indexes in decreasing value order (FPV)
                idx = sorted(aux_util, key = aux_util.__getitem__, reverse=True)                
                if self._verbose:
                    print(idx)
                    print("")
                    print(idx[:Demand])

                # If adjacency, create set
                if self._Adj is True:
                    # Iintialize Harvested cells array
                    HCs = HCs + [idx[0]]

                    # Update auxiliary sets
                    toHarvestCells = set([idx[0]])
                    AdjHarvested = set([adj[0] for adj in Adjacents[idx[0] - 1].values() if adj != None])
                    TotalProduction += VolCells[idx[0] - 1]
                    TotalUtility += Utility[idx[0] - 1]
                    j = 1

                # Info
                if self._verbose:
                    print("Initial values")
                    print("\ttoHarvestCells:", toHarvestCells)
                    if self._Adj is True:
                        print("\tAdjHarvested:", AdjHarvested)
                    print("\tTotal Production:", TotalProduction)
                    print("\tTotal Utility:", TotalUtility)

                # Main loop for satisfying the demand (Adjacency version)
                noUpdate = True
                if self._Adj:
                    while TotalProduction <= Demand:
                        noUpdate = True
                        # Greedy Selection
                        if self._GreedySelection:
                            for j in range(len(idx.copy())):
                                # If cell is adjacent to the previous harvested, harvest it (greedy)
                                if idx[j] in AdjHarvested and idx[j] in AvailCells:
                                    toAdd = idx.pop(j)
                                    toHarvestCells.add(toAdd)
                                    HCs += [toAdd]

                                    # Adjacent constraint
                                    ADJ = set([adj[0] for adj in Adjacents[toAdd - 1].values() if adj != None])
                                    AdjHarvested |= ADJ
                                    AdjHarvested.remove(toAdd)
                                    AvailCells -= set([toAdd])
                                    TotalProduction += VolCells[toAdd - 1]
                                    TotalUtility += Utility[toAdd - 1]
                                    noUpdate=False
                                                                        
                                    if self._verbose:
                                        print("--- Adding", toAdd, "to the harvested cells ---")
                                        print("\ttoHarvestCells:", toHarvestCells)
                                        print("\tAdjHarvested:", AdjHarvested)
                                        print("\tTotal Production:", TotalProduction)
                                        print("\tTotal Utility:", TotalUtility)
                                        print("j:", j)
                                    
                                    # Break for loop, 
                                    break 
                                    
                            
                            # Check if for loop did not update the harvesting plan (break while, infeasible)
                            if noUpdate:
                                print("Demand was not satisfied... Infeasible period", Year)
                                break

                        elif self._GeneticSelection:
                            # To be implemented
                            pass

                # No Adjacency
                else:
                    # Initialize Harvested cells array
                    HCs = HCs + [idx[:Demand]]

                    # Update auxiliary sets
                    toHarvestCells = set(idx[:Demand])
                    TotalProduction += VolCells[np.asarray(idx[:Demand]).astype(np.int) - 1]
                    TotalUtility += Utility[np.asarray(idx[:Demand]).astype(np.int) - 1]
                    AvailCells -= set(idx[:Demand])

                    if self._verbose:
                        print("Initial values")
                        print("\ttoHarvestCells:", toHarvestCells)
                        print("\tTotal Production:", TotalProduction)
                        print("\tTotal Utility:", TotalUtility)
                    
                 
            
            '''  Eighteen version (18) Betweenness centrality, no adjacency'''
            # BC version GPTree version
            if self._version == 18:
                if self._verbose:
                    print("----- BC Heuristic Version ( no adjacent, version", self._version, ") ------")
                fpv_av = dict(self._GGraph.nodes(data='fpv'))
                
                if self._verbose:
                    print("FPV from G:\n", fpv_av)

                # Initialize utility dictionary
                for i in AvailCells:
                    aux_util[i] = fpv_av[i]

                # Get indexes in decreasing value order (FPV)
                idx = sorted(aux_util, key = aux_util.__getitem__, reverse=True)                
                if self._verbose:
                    print(idx)
                    print("")
                    print(idx[:Demand])
                    
                # No Adjacency
                # Initialize Harvested cells array
                HCs = HCs + [idx[:Demand]]

                # Update auxiliary sets
                toHarvestCells = set(idx[:Demand])
                TotalProduction += VolCells[np.asarray(idx[:Demand]).astype(np.int) - 1]
                TotalUtility += Utility[np.asarray(idx[:Demand]).astype(np.int) - 1]
                AvailCells -= set(idx[:Demand])

                # Information
                if self._verbose:
                    print("Initial values")
                    print("\ttoHarvestCells:", toHarvestCells)
                    print("\tTotal Production:", TotalProduction)
                    print("\tTotal Utility:", TotalUtility)
               
            
            '''  Nineteenth version (19) Betweenness centrality, adjacency'''
            # BC version, adjacency GPTree version
            if self._version == 19:
                if self._verbose:
                    print("----- BC Heuristic Version ( adjacent, version", self._version, ") ------")
                fpv_av = dict(self._GGraph.nodes(data='fpv'))
                
                if self._verbose:
                    print("FPV from G:\n", fpv_av)

                # Initialize utility dictionary
                for i in AvailCells:
                    aux_util[i] = fpv_av[i]

                # Get indexes in decreasing value order (FPV)
                idx = sorted(aux_util, key = aux_util.__getitem__, reverse=True)                
                if self._verbose:
                    print(idx)
                    print("")
                    print(idx[:Demand])  
                    
                # Iintialize Harvested cells array
                HCs = HCs + [idx[0]]

                # Update auxiliary sets
                toHarvestCells = set([idx[0]])
                AdjHarvested = set([adj[0] for adj in Adjacents[idx[0] - 1].values() if adj != None])
                TotalProduction += VolCells[idx[0] - 1]
                TotalUtility += Utility[idx[0] - 1]
                j = 1

                # Info
                if self._verbose:
                    print("Initial values")
                    print("\ttoHarvestCells:", toHarvestCells)
                    print("\tAdjHarvested:", AdjHarvested)
                    print("\tTotal Production:", TotalProduction)
                    print("\tTotal Utility:", TotalUtility)
                    
                
                # Main loop for satisfying the demand (Adjacency version)
                noUpdate = True
                while TotalProduction <= Demand and Demand > 1:
                    noUpdate = True
                    # Greedy Selection
                    if self._GreedySelection:
                        for j in range(len(idx.copy())):
                            # If cell is adjacent to the previous harvested, harvest it (greedy)
                            if idx[j] in AdjHarvested and idx[j] in AvailCells:
                                toAdd = idx.pop(j)
                                toHarvestCells.add(toAdd)
                                HCs += [toAdd]

                                # Adjacent constraint
                                ADJ = set([adj[0] for adj in Adjacents[toAdd - 1].values() if adj != None])
                                AdjHarvested |= ADJ
                                AdjHarvested.remove(toAdd)
                                AvailCells -= set([toAdd])
                                TotalProduction += VolCells[toAdd - 1]
                                TotalUtility += Utility[toAdd - 1]
                                noUpdate=False
                                
                                if self._verbose:
                                    print("--- Adding", toAdd, "to the harvested cells ---")
                                    print("\ttoHarvestCells:", toHarvestCells)
                                    print("\tAdjHarvested:", AdjHarvested)
                                    print("\tTotal Production:", TotalProduction)
                                    print("\tTotal Utility:", TotalUtility)
                                    print("j:", j)
                                    
                                # Break for loop
                                break 
                                    
                            
                        # Check if for loop did not update the harvesting plan (break while, infeasible)
                        if noUpdate:
                            print("Demand was not satisfied... Infeasible period", Year)
                            break

                    elif self._GeneticSelection:
                        # To be implemented
                        pass    
                
                
                
                    
                
                        
            
            # Display harvested cells
            if self._verbose:
                print("Heuristic toHarvestCells:", toHarvestCells)

        # Return harvested cells set
        auxFPV = np.reshape(self._FPVMatrix, (self._NCells,))
        auxCells = [i-1 for i in toHarvestCells]

        return toHarvestCells, np.sum(auxFPV[auxCells]) 
    
    # Plot style
    def pltStyle(self):
        # Figure size
        plt.figure(figsize = (15, 9)) 

        # Font sizes
        plt.rcParams['font.size'] = 32
        plt.rcParams['axes.labelsize'] = 32
        plt.rcParams['axes.titlesize'] = 32
        plt.rcParams['xtick.labelsize'] = 32
        plt.rcParams['ytick.labelsize'] = 32
        plt.rcParams['legend.fontsize'] = 32
        plt.rcParams['figure.titlesize'] = 32 
        plt.rcParams['axes.linewidth'] = 2.5
        
        # axes
        ax = plt.subplot(111)                    
        ax.spines["top"].set_visible(False)  
        ax.spines["right"].set_visible(False)
        ax.get_xaxis().tick_bottom()  
        ax.get_yaxis().tick_left() 
    
    # Print FPV plots (global)
    def Global_FPVPlot(self, normalized=False, xticks=50, yticks=50):
        # Plt Style
        self.pltStyle()
        matplotlib.rcParams['axes.linewidth'] = 2.5
        
        # Title and labels
        plt.title(self.Alg + " Heatmap $|R| = 100$", y=1.02)

        # Modify existing map to have white values
        cmap = cm.get_cmap('RdBu_r')
        lower = plt.cm.seismic(np.ones(2)*0.50)  # Original is ones 
        range = cmap(np.linspace(0.5, np.max((self._FPVMatrix / np.max(self._FPVMatrix))), 100))
        colors = np.vstack((lower,range))
        tmap = matplotlib.colors.LinearSegmentedColormap.from_list('terrain_map_white', colors)
        
        # Plot if matrix is non-empty
        all_zeros = not self._FPVMatrix.any()
        
        if all_zeros is False:
            # Normalized
            ax = sns.heatmap(self._FPVMatrix / np.max(self._FPVMatrix), 
                             center=0.5, xticklabels=xticks, yticklabels=yticks, 
                             square=True, cmap=tmap, cbar=False, linewidths=0.05, linecolor="w",
                             vmin=0, vmax=np.max((self._FPVMatrix / np.max(self._FPVMatrix)))) 
            
            # Color bar
            sm = plt.cm.ScalarMappable(cmap=tmap, norm=plt.Normalize(vmin=np.min(0), vmax=np.max((self._FPVMatrix / np.max(self._FPVMatrix)))))
            sm._A = []
            divider = make_axes_locatable(ax)
            cax1 = divider.append_axes("right", size="5%", pad=0.15)
            plt.colorbar(sm, cax=cax1)  
            
            for _, spine in ax.spines.items():spine.set_visible(True)
			
            # Save
            plt.savefig(os.path.join(self._OutFolder, "Global_FPV_Graph_Normalized_v" + str(self._version)+  ".png"),
                    dpi=200,  figsize=(200, 200), 
                    bbox_inches='tight', transparent=False)
            plt.close("all")
            
            # Not-Normalized
            # Plt Style
            self.pltStyle()

            # Title and labels
            plt.title(self.Alg + " Heatmap $|R| = 100$", y=1.02)

			# Plot
            ax2 = sns.heatmap(self._FPVMatrix / np.max(self._FPVMatrix), 
                             center=0.5, xticklabels=xticks, yticklabels=yticks, 
                             square=True, cmap=tmap, cbar=False, linewidths=0.05, linecolor="w",
                             vmin=0, vmax=1) 
        

            for _, spine in ax2.spines.items():spine.set_visible(True)
            
            sm = plt.cm.ScalarMappable(cmap=tmap, norm=plt.Normalize(vmin=np.min(0), vmax=np.max((self._FPVMatrix))) )
            sm._A = []
            divider = make_axes_locatable(ax2)
            cax = divider.append_axes("right", size="5%", pad=0.15)
            plt.colorbar(sm, cax=cax)  
            
            # Save it to Heuristic folder
            plt.savefig(os.path.join(self._OutFolder, "Global_FPV_Graph_v" + str(self._version)+  ".png"),
                        dpi=200,  figsize=(200, 200), 
                        bbox_inches='tight', transparent=False)
            plt.close("all")
    
    # Print FPV plots (individual)
    def Ind_FPVPlot(self, nSim, FPVMatrix, normalized=False):
        # Figure size
        plt.figure(figsize = (15, 9)) 

        # Font sizes
        plt.rcParams['font.size'] = 16
        plt.rcParams['axes.labelsize'] = 16
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['xtick.labelsize'] = 16
        plt.rcParams['ytick.labelsize'] = 16
        plt.rcParams['legend.fontsize'] = 16
        plt.rcParams['figure.titlesize'] = 18

        # axes
        ax = plt.subplot(111)                    
        ax.spines["top"].set_visible(False)  
        ax.spines["right"].set_visible(False)
        ax.get_xaxis().tick_bottom()  
        ax.get_yaxis().tick_left() 

        # Title and labels
        plt.title("FPV Heatmap")

        # Modify existing map to have white values
        cmap = cm.get_cmap('RdBu_r')
        lower = plt.cm.seismic(np.ones(100)*0.50)
        upper = cmap(np.linspace(1-0.5, 1, 90))
        colors = np.vstack((lower, upper))
        tmap = matplotlib.colors.LinearSegmentedColormap.from_list('terrain_map_white', colors)

        # Normalized
        if normalized:
            ax = sns.heatmap(FPVMatrix / np.max(FPVMatrix), 
                             center=0.0, xticklabels="auto", yticklabels="auto", 
                             square=True, cmap=tmap, 
                             vmin=0, vmax=np.max((FPVMatrix / np.max(FPVMatrix)))) 
        
        # Not-Normalized
        else:
            ax = sns.heatmap(FPVMatrix, 
                             center=0.0, xticklabels="auto", yticklabels="auto", 
                             square=True, cmap=tmap, 
                             vmin=0, vmax=np.max((FPVMatrix))) 

        # Save it to plots folder
        plt.savefig(os.path.join(self._OutFolder, "Plots", "Plots" + str(nSim), 
                                 "FPV_Graph" + str(nSim) + ".png"),
                    dpi=200,  figsize=(200, 200), 
                    bbox_inches='tight', transparent=False)
        plt.close("all")
        
        
     
    
    # Heuristics boxplots comparison
    def HeurBoxPlots(self, Paths, Heuristics=["BP", "FPV", "Random", "DPV", "Utility"], 
                     pal="Reds", title="Heuristics comparison alpha % (Greedy)",
                     namePlot="HeuristicsComparison_BoxPlots"):

        # Style
        plt_style()

        # Title and labels
        plt.title(title)

        # DFs containers (with results from heuristics)
        DFs = {}

        # Populate all sets
        for i in range(1, len(Heuristics) + 1):
            DFs[i] = pd.read_csv(os.path.join(Paths[i - 1], "Stats", "FinalStats.csv")).assign(Heuristic=Heuristics[i - 1])
            DFs[i] = DFs[i][["Burned", "Heuristic"]]

        # Concat all DFs
        cdf = pd.concat([df for df in DFs.values()])                                         
        mdf = pd.melt(cdf, id_vars=['Heuristic'], var_name=['Burned'])     

        # Plot
        ax = sns.boxplot(x="Heuristic", y="value", data=mdf, linewidth=2.5, palette=pal).set(ylabel="Burned Cells") 
        #plt.xticks(rotation=65)

        plt.savefig(os.path.join(self._OutFolder, namePlot + ".png"), dpi=200,
                    bbox_inches='tight', figsize=(200, 200))
        plt.close("all")
    
    # Per % comparison (x-axis = % of treatment, y-axis = burned cells)
    def HeurFractions(self, Paths, Fractions=[0.0,0.25,0.5,0.75,0.8,0.9], 
                      Heurs=["BP", "FPV", "Random", "DPV", "Utiliy"],
                      title="Heuristic treatments comparison (all %)",
                      namePlot="HeuristicsFractionsComparison", verbose=False):

        # Style
        plt_style()

        # Populate DF
        aux = 0
        aux2 = 0
        DFS = {}
        keepCols = ["Burned", "NonBurned", "Harvested", "TreatedFraction", "Criterion"]

        # Get all final stats
        for path in Paths:
            for j in range(len(Fractions)):
                fr = Fractions[j]
                filePath = os.path.join(path, "Fraction" + str(fr), "Stats", "FinalStats.csv")
                DF = pd.read_csv(filePath).assign(TreatedFraction=fr, Criterion=Heurs[aux])
                DF = DF[keepCols]
                DFS[aux2] = DF
                aux2 += 1

                if verbose:
                    print("Added fraction", fr, "for type", Heurs[aux])
            aux += 1

        # Concat
        DFs = pd.concat([df for df in DFS.values()])
        if verbose:
            print(np.unique(DFs["TreatedFraction"]))

        # Plot
        ax = sns.lineplot(x="TreatedFraction", y="Burned", 
                          hue="Criterion", data=DFs).set(xlabel="Treated Fraction", 
                                                         ylabel="Burned Cells",
                                                         title=title)    

        # Save
        plt.savefig(os.path.join(self._OutFolder, namePlot + ".png"), dpi=200, 
                    bbox_inches='tight', figsize=(200,200))

        # Close
        plt.close("all")
    
    # Set OutFolder
    def setOutFolder(self, OutFolder):
        self._OutFolder = OutFolder
        
    # Set InFolder
    def setInFolder(self, InFolder):
        self._InFolder = InFolder
        
    # Set version
    def setVersion(self, version):
        self._version = version
        
    # Set FPVGrids
    def setFPVGrids(self, fpvgrids):
        self._FPVGrids = fpvgrids
        
    # Set MessagesPath
    def setMessagesPath(self, msgPath):
        self._MessagePath = msgPath
    
    @property 
    def getGraphG(self):
        return self._GGraph
    
    @property 
    def getGraphH(self):
        return self._HGraphs
    
    @property
    def getVersion(self):
        return self._version
    
    @property 
    def getFPVGrids(self):
        return self._FPVGrids
    
    @property
    def getFPVMatrix(self):
        return self._FPVMatrix
