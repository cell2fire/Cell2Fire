# coding: utf-8
__version__ = "1.0"
__author__ = "Cristobal Pais"
# Minor edits by David L. Woodruff

# Statistics Class
# Importations
import pandas as pd
import numpy as np
import glob
import os 
import re

# Plot
import matplotlib
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import rcParams
import matplotlib.pyplot as plt
from matplotlib.pylab import *
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import matplotlib.colors as colors
import cv2

# Extra
import multiprocessing
from multiprocessing import Process

# Extra
from operator import itemgetter
import itertools
from cell2fire.utils.coord_xy import *  # TBD: drop import *
from tqdm import tqdm
import networkx as nx
from shutil import copy2

# Cell2Fire
### import cell2fire.utils.ReadDataPrometheus as ReadDataPrometheus


class Statistics(object):
    # Initializer
    def __init__(self,
                 OutFolder="",
                 StatsFolder="",
                 MessagesPath="",
                 Rows=0,
                 Cols=0,
                 NCells=0,
                 boxPlot=True,
                 CSVs=True,
                 statsGeneral=True, 
                 statsHour=True,
                 histograms=True,
                 BurntProb=True,
                 nSims=1,
                 verbose=False,
                 GGraph=None,
                 tCorrected=False,
                 pdfOutputs=False):
    
        # Containers
        self._OutFolder = OutFolder
        self._MessagesPath = MessagesPath
        self._Rows = Rows
        self._Cols = Cols
        self._NCells = NCells
        self._boxPlot = boxPlot
        self._CSVs = CSVs
        self._statsGeneral = statsGeneral
        self._statsHour = statsHour
        self._histograms = histograms
        self._BurntProb = BurntProb
        self._nSims = nSims
        self._verbose = verbose
        self._GGraph = GGraph
        self._tCorrected = tCorrected
        self._pdfOutputs = pdfOutputs

        # Create Stats path (if needed)
        if StatsFolder != "":
            self._StatsFolder = StatsFolder
        else:
            self._StatsFolder = os.path.join(OutFolder, "Stats")
        if not os.path.exists(self._StatsFolder):
            if self._verbose:
                print("creating", self._StatsFolder)
            os.makedirs(self._StatsFolder)
            
        ## local utility ##
    def _GridDir(self, SimNum):
        """ Factored code to deal with grid files from the C++ side.
        Args:
            SimNum (int): simulation number (zero based)
        
        Returns:
            GridPath (str), GridFiles (list of str): C++ output files
               with GridFiles sorted by the trailing number in the base filename (e.g. hour)
        """
        def fnum(fname):
            parts = fname.split(".")
            assert(parts[1] == "csv")
            return int(re.compile(r'(\d+)$').search(parts[0]).group(1))

        GridPath = os.path.join(self._OutFolder, "Grids", "Grids"+str(SimNum+1))
        GridFiles = os.listdir(GridPath)
        GridFiles.sort(key=fnum)
        return GridPath, GridFiles
            
    ####################################
    #                                  #
    #            Methods               #
    #                                  #
    ####################################
    # Plot style
    def plt_style(self):
        # Figure
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
    
    # Boxplot function
    def BoxPlot(self, Data, xx="Hour", yy="Burned", xlab="Hours", ylab="# Burned Cells", 
                pal="Reds", title="Burned Cells Evolution", Path=None, namePlot="BoxPlot",
                swarm=True):
        
        # Figure
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
        plt.title(title)

        #sns.set(style="darkgrid", font_scale=1.5)
        ax = sns.boxplot(x=xx, y=yy, data=Data, linewidth=2.5, palette=pal).set(xlabel=xlab,ylabel=ylab)    
        if swarm:
            ax = sns.swarmplot(x=xx, y=yy, data=Data, linewidth=2.5, palette=pal).set(xlabel=xlab,ylabel=ylab)   

        # Save it
        if Path is None:
            Path = os.getcwd() + "/Stats/"
            if not os.path.exists(Path):
                os.makedirs(Path)

        plt.savefig(os.path.join(Path, namePlot + ".png"), dpi=200, bbox_inches='tight')
        if self._pdfOutputs:
            plt.savefig(os.path.join(Path, namePlot + ".pdf"), dpi=200, bbox_inches='tight')
        plt.close("all")
        
    
    # Final forest boxplot
    def FinalBoxPlots(self, OutFolder=None, title="Final Forest Status",
                      namePlot="FinalStats_BoxPlot"):

        # Style
        self.plt_style()

        # Title and labels
        plt.title(title)

        # DFs containers (with results from heuristics)
        DFs = {}

        # Populate DF
        filePath = os.path.join(self._StatsFolder, "FinalStats.csv")
        DF = pd.read_csv(filePath)
        DF = DF[["Burned", "NonBurned", "Harvested"]]

        # Plot
        my_pal = {"Burned": "r", "NonBurned": "g", "Harvested":"b"}
        ax = sns.boxplot(data=DF, linewidth=2.5, palette=my_pal).set(xlabel="Final State", ylabel="Hectares")    

        # Save it
        plt.savefig(os.path.join(self._StatsFolder, namePlot + ".png"), dpi=200, bbox_inches='tight')
        if self._pdfOutputs:
            plt.savefig(os.path.join(self._StatsFolder, namePlot + ".pdf"), dpi=200, bbox_inches='tight')
        plt.close("all")
    
    # Histograms
    def plotHistogram(self, df, NonBurned=False, xx="Hour", xmax=6, KDE=True, title="Histogram: Burned Cells",
                      Path=None, namePlot="Histogram"):
        
        # Modify rc parameters (Matplotlib/Seaborn)
        rcParams['patch.force_edgecolor'] = True
        rcParams['patch.facecolor'] = 'b'

        # Figure Size
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
        plt.title(title)

        # Make default histogram of sepal length
        if KDE is True:
            g = sns.distplot(df[df[xx] == xmax]["Burned"], bins=10, kde=KDE, rug=False).set(xlabel="Number of Cells", ylabel="Density")
            if NonBurned is True: 
                g += sns.distplot(df[df[xx] == xmax]["NonBurned"], bins=10, kde=KDE, rug=False).set(xlabel="Number of Cells", ylabel="Density")
        else:
            g = sns.distplot(df[df[xx] == xmax]["Burned"], bins=10,  kde=KDE, rug=False).set(xlabel="Number of Cells", ylabel="Frequency")
            if NonBurned is True:
                g += sns.distplot(df[df[xx] == xmax]["NonBurned"], bins=10, kde=KDE, rug=False).set(xlabel="Number of Cells", ylabel="Frequency")

        # Save it
        if Path is None:
            Path = os.getcwd() + "/Stats/"
            if not os.path.exists(Path):
                os.makedirs(Path)

        plt.savefig(os.path.join(Path, namePlot + ".png"), dpi=200, bbox_inches='tight')
        plt.close("all")

    # Burnt Probability Heatmap
    #   cbarF seems to indicate no legend when true.
    def BPHeatmap(self, WeightedScar, Path=None, nscen=10, sq=False, namePlot="BP_HeatMap", 
                  Title=None, cbarF=True, ticks=100, transparent=False):
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
        if Title is None:
            plt.title("Fire Probability Heatmap (nscen="+str(nscen)+")")
        else:
            plt.title(Title)

        # Modify existing map to have white values
        cmap = cm.get_cmap('RdBu_r')
        lower = plt.cm.seismic(np.ones(1)*0.50)  # Original is ones 
        upper = cmap(np.linspace(0.5, 1, 100))
        colors = np.vstack((lower,upper))
        tmap = matplotlib.colors.LinearSegmentedColormap.from_list('terrain_map_white', colors)

        # Create Heatmap
        ax = sns.heatmap(WeightedScar, xticklabels=ticks, yticklabels=ticks, linewidths=0.0, linecolor="w",
                         square=sq, cmap=tmap, vmin=0.0, vmax=1, annot=False, cbar=False)#cbarF)
        
        # If cbarF is false, we want the legend
        if cbarF == False:
            sm = plt.cm.ScalarMappable(cmap=tmap)#, norm=plt.Normalize(vmin=np.min(0), vmax=np.max(1)))
            sm._A = []
            divider = make_axes_locatable(ax)
            cax1 = divider.append_axes("right", size="5%", pad=0.15)
            plt.colorbar(sm, cax=cax1)

        # Save it
        if Path is None:
            Path = os.getcwd() + "/Stats/"
            if not os.path.exists(Path):
                os.makedirs(Path)

        for _, spine in ax.spines.items():
            spine.set_visible(True)

        plt.savefig(os.path.join(Path, namePlot + ".png"), dpi=200, bbox_inches='tight', 
                    pad_inches=0, transparent=transparent)
        if self._pdfOutputs:
            plt.savefig(os.path.join(Path, namePlot + ".pdf"), dpi=200, bbox_inches='tight', 
                    pad_inches=0, transparent=transparent)
        
        
        plt.close("all")
    
    # ROS Heatmap
    def ROSHeatmap(self, ROSM, Path=None, nscen=1, sq=True, namePlot="ROS_HeatMap",
                   Title=None, cbarF=True, ticks="auto", transparent=False, 
                   annot=False, lw=0.01, vmin=0, vmax=None):
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
        if Title is None:
            plt.title("ROS Heatmap (nscen="+str(nscen)+")")
        else:
            plt.title(Title)

        # Modify existing map to have white values
        cmap = cm.get_cmap('RdBu_r')
        lower = plt.cm.seismic(np.ones(1)*0.50)  # Original is ones 
        upper = cmap(np.linspace(0.5, 1, 100))
        colors = np.vstack((lower,upper))
        tmap = matplotlib.colors.LinearSegmentedColormap.from_list('terrain_map_white', colors)

        # Limits
        if vmax is None:
            vmax = np.max(ROSM)

        ax = sns.heatmap(ROSM, xticklabels=ticks, yticklabels=ticks, linewidths=lw, linecolor="w",
                         square=sq, cmap=tmap, vmin=vmin, vmax=vmax, annot=False, cbar=False)
        sm = plt.cm.ScalarMappable(cmap=tmap)
        sm._A = []
        divider = make_axes_locatable(ax)
        cax1 = divider.append_axes("right", size="5%", pad=0.15)
        plt.colorbar(sm, cax=cax1)  

        # Save it
        if Path is None:
            Path = os.getcwd() + "/Stats/"
            if not os.path.exists(Path):
                os.makedirs(Path)

        for _, spine in ax.spines.items():
            spine.set_visible(True)

        plt.savefig(os.path.join(Path, namePlot + ".png"), dpi=200, bbox_inches='tight', 
                    pad_inches=0, transparent=transparent)
        
        if self._pdfOutputs:
            plt.savefig(os.path.join(Path, namePlot + ".pdf"), dpi=200, bbox_inches='tight', 
                        pad_inches=0, transparent=transparent)
        
        plt.close("all")
    
    # ROS Matrix individual
    def ROSMatrix_ind(self, nSim): 
        msgFileName = "MessagesFile0" if (nSim < 10) else "MessagesFile"
        DF = pd.read_csv(os.path.join(self._MessagesPath, msgFileName), delimiter=",", header=None,)
        DF.columns = ["i", "j", "time", "ROS"]

        # Array
        ROSM = np.zeros(self._Rows * self._Cols)

        # Fill
        for j in DF["j"]:
            ROSM[j-1] = DF[DF["j"] == j]["ROS"].values[0]
        ROSM = ROSM.reshape((self._Rows, self._Cols))
        
        # Create plots folder
        PlotPath = os.path.join(self._OutFolder, "Plots", "Plots" + str(nSim))
        if os.path.isdir(PlotPath) is False:
            os.makedirs(PlotPath)

        # Heatmap
        self.ROSHeatmap(ROSM, Path=PlotPath, nscen=1, sq=True, namePlot="ROS_Heatmap", 
                        Title="ROS Heatmap", cbarF=True)
        
    
    # ROS Matrix
    def ROSMatrix_AVG(self, nSims): 
        # Container 
        ROSMs = {}

        # Read all files
        for nSim in range(1, nSims + 1):
            msgFileName = "MessagesFile0" if (nSim < 10) else "MessagesFile"
            msgFileName = msgFileName + str(nSim) + '.csv'
            DF = pd.read_csv(os.path.join(self._MessagesPath, msgFileName), delimiter=",", header=None,)
            DF.columns = ["i", "j", "time", "ROS"]

            # Array
            ROSM = np.zeros(self._Rows * self._Cols)

            # Fill
            for j in DF["j"]:
                ROSM[j-1] = DF[DF["j"] == j]["ROS"].values[0]
            ROSM = ROSM.reshape((self._Rows, self._Cols))

            # Save
            ROSMs[nSim] = ROSM
        
        # AVG ROS
        AVGROSM = np.zeros((Rows, Cols))
        for k in ROSMs.keys():
            if k == 1:
                AVGROSM = ROSMs[k].copy()
            else:
                AVGROSM += ROSMs[k]
        AVGROSM = AVGROSM / k

        # Create plots folder
        PlotPath = os.path.join(self._OutFolder, "Plots", "Plots" + str(nSim))
        if os.path.isdir(PlotPath) is False:
            os.makedirs(PlotPath)
        
        # Heatmap
        self.ROSHeatmap(AVGROSM, 
                        Path=PlotPath,
                        nscen=1,
                        sq=True,
                        namePlot="AVG_ROS_Heatmap", 
                        Title="AVG ROS Heatmap",
                        cbarF=True)

        
    
    # Generate G graph
    def GGraphGen(self, full=False):
        # Graph generation
        nodes = range(1, self._NCells + 1)

        # We build a Digraph (directed graph, general graph for the instance)
        self._GGraph = nx.DiGraph()

        # We add nodes to the list
        self._GGraph.add_nodes_from(nodes)
        for n in nodes:
            self._GGraph.nodes[n]["ros"] = 0
            self._GGraph.nodes[n]["time"] = 0
            self._GGraph.nodes[n]["count"] = 0
        
        # If full, get edges
        if full:
            for k in range(1, self._nSims + 1):
                msgFileName = "MessagesFile0" if (k < 10) else "MessagesFile"
                HGraphs = nx.read_edgelist(path=self._MessagesPath + '/' + msgFileName + str(k) + '.csv',
                                           create_using=nx.DiGraph(),
                                           nodetype=int,
                                           data=[('time', float), ('ros', float)],
                                           delimiter=',')

                for e in HGraphs.edges():
                    if self._GGraph.has_edge(*e):
                        self._GGraph.get_edge_data(e[0], e[1])["weight"] += 1
                        self._GGraph.nodes[e[1]]["ros"] += HGraphs[e[0]][e[1]]["ros"]
                        self._GGraph.nodes[e[1]]["time"] += HGraphs[e[0]][e[1]]["time"]
                        self._GGraph.nodes[e[1]]["count"] += 1
                    else:
                        self._GGraph.add_weighted_edges_from([(*e,1.)])
                    
        # Average ROS, time 
        for n in nodes:
            if self._GGraph.nodes[n]['count'] > 0:
                self._GGraph.nodes[n]['ros'] /= self._GGraph.nodes[n]['count']
                self._GGraph.nodes[n]['time'] /= self._GGraph.nodes[n]['count']

    
    # Fire Spread evolution plot (global sims)
    def GlobalFireSpreadEvo(self, CoordCells, onlyGraph=True, version=0):
        # V0 Frequency
        if self._GGraph is None:
            self.GGraphGen(full=True)
            
        coord_pos = dict() # Cartesian coordinates
        for i in self._GGraph.nodes:
            coord_pos[i] = CoordCells[i-1] + 0.5
        
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
        ax.get_xaxis().tick_bottom()  
        ax.get_yaxis().tick_left() 
        plt.ylim(bottom=0)
        for _, spine in ax.spines.items():
            spine.set_visible(True)


        # Dimensionamos el eje X e Y
        #plt.axis([-1, self._Rows, -1, self._Cols])
        
        # Print nodes
        if onlyGraph is False:
            nx.draw_networkx_nodes(self._GGraph, pos = coord_pos,
                                   node_size = 5,
                                   nodelist = list(self._GGraph.nodes),
                                   node_shape='s',
                                   node_color = Colors)

        edges = self._GGraph.edges()
        weights = [self._GGraph[u][v]['weight'] for u,v in edges]
        outname = ""

        # Check non-zeros
        all_zeros = not np.asarray(weights).any()

        if all_zeros is False:
            if version == 0:
                # Fixed edge color (red), different scaled width
                outname = "NWFreq"
                plt.title(r"Global Propagation Tree ${GT}$ ($|R| =$ " +str(self._nSims)+")", y=1.08)
                
                nx.draw_networkx_edges(self._GGraph, pos = coord_pos, edge_color = 'r', node_size = 0,
                                       width = weights/np.max(weights), arrowsize=3)
                #nx.draw(self._GGraph, with_labels=False, pos = coord_pos, node_color='w', node_size=0, 
                #    edge_color='r', width=weights/np.max(weights), arrows=True, arrowsize=3, ax=ax)

            if version == 4:
                # Edge = Frequency, width = frequency
                outname = "CFreq_NWFreq"
                plt.title(r"Global Propagation Tree ${GT}$ ($|R| =$ " +str(self._nSims)+")", y=1.08)
                nx.draw_networkx_edges(self._GGraph, pos = coord_pos, edge_color = weights, edge_cmap=plt.cm.Reds,
                                       width = weights/np.max(weights), arrowsize=3, node_size = 0)
                sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin=np.min(weights), vmax=np.max(weights)))
                sm._A = []
                #plt.colorbar(sm)
                #nx.draw(self._GGraph, with_labels=False, pos = coord_pos, node_color='w', node_size=0, edge_cmap=plt.cm.Reds,
                #        edge_color=weights, width=weights/np.max(weights), arrows=True, arrowsize=3, ax=ax)


            if version == 1:
                # Edge = Frequency, width = frequency
                outname = "CNFreq_NWFreq"
                plt.title(r"Global Propagation Tree ${GT}$ ($|R| =$ " +str(self._nSims)+") - Freq Color|Width", y=1.08)
                nx.draw_networkx_edges(self._GGraph, pos = coord_pos, edge_color = weights/np.max(weights), edge_cmap=plt.cm.Reds,
                                      width = weights/np.max(weights), arrowsize=3, node_size = 0)
                sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin=np.min(0), vmax=np.max(1)))
                sm._A = []
                #plt.colorbar(sm)
                #nx.draw(self._GGraph, with_labels=False, pos = coord_pos, node_color='w', node_size=0, edge_cmap=plt.cm.Reds,
                #        edge_color=weights/np.max(weights), width=weights/np.max(weights), arrows=True, arrowsize=3, ax=ax)

                
            if version == 2:
                # Edge = frequency, fixed width
                outname = "CFreq"
                plt.title(r"Global Propagation Tree ${GT}$ ($|R| =$ " +str(self._nSims)+") - Freq Color", y=1.08)
                nx.draw_networkx_edges(self._GGraph, pos = coord_pos, edge_color = weights, edge_cmap=plt.cm.Reds,
                                      width = 1.0, arrowsize=3, node_size = 0)
                sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin=np.min(weights), vmax=np.max(weights)))
                sm._A = []
                #nx.draw(self._GGraph, with_labels=False, pos = coord_pos, node_color='w', node_size=0, edge_cmap=plt.cm.Reds,
                #        edge_color=weights, width=1.0, arrows=True, arrowsize=3, ax=ax)

            #Title
            plt.axis('scaled')
            if version != 0:
                divider = make_axes_locatable(ax)
                cax1 = divider.append_axes("right", size="5%", pad=0.15)
                plt.colorbar(sm, cax=cax1)
                
            plt.savefig(os.path.join(self._StatsFolder, "SpreadTree_FreqGraph_" + outname + ".png"), 
                        dpi=200, figsize=(200, 200), 
                        bbox_inches='tight', transparent=False)
            if self._pdfOutputs:
                plt.savefig(os.path.join(self._StatsFolder, "SpreadTree_FreqGraph_" + outname + ".pdf"), 
                            dpi=200, figsize=(200, 200), 
                            bbox_inches='tight', transparent=False)
            plt.close("all")

    # Fire Spread evolution plots (per sim)
    def SimFireSpreadEvo(self, nSim, CoordCells, Colors, H=None, version=0,
                         print_graph=True, analysis_degree=True, onlyGraph=False):
        # V1
        # If no graph, read it
        if H is None:
            msgFileName = "MessagesFile0" if (nSim < 10) else "MessagesFile"
            H = nx.read_edgelist(path = os.path.join(self._MessagesPath, msgFileName + str(nSim) + ".csv"),
                                 create_using = nx.DiGraph(),
                                 nodetype = int,
                                 data = [('time', float), ('ros', float)],
                                 delimiter=',')
            
        # Cartesian positions
        coord_pos = dict() 

        # Generate G graph (empty)
        if self._GGraph is None:
            self.GGraphGen()
        for i in self._GGraph.nodes:
            coord_pos[i] = CoordCells[i-1] + 0.5
        
        # We generate the plot
        if print_graph:

            # plt.figure(figsize = (15, 9)) 

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
            for _, spine in ax.spines.items():
                spine.set_visible(True)
            ax.get_xaxis().tick_bottom()  
            ax.get_yaxis().tick_left() 

            # Dimensionamos el eje X e Y
            plt.axis([-1, self._Rows, -1, self._Cols])

            # Print graph and nodes
            if onlyGraph is False:
                nx.draw_networkx_nodes(self._GGraph, pos = coord_pos,
                                       node_size = 5,
                                       nodelist = list(self._GGraph.nodes),
                                       node_shape='s',
                                       node_color = Colors)

            #nx.draw(H, with_labels=False, pos = coord_pos, node_color='w', node_size=0, 
            #        edge_color= 'r', width=0.5, edge_cmap=plt.cm.Reds,
            #        arrows=True, arrowsize=3, ax=ax)

            nx.draw_networkx_edges(H, pos = coord_pos, edge_color = 'r', width = 0.5, arrowsize=3, node_size=0)
            
            #Title
            plt.title("Propagation Tree")
            plt.axis('scaled')

            # Save plot
            PlotPath = os.path.join(self._OutFolder, "Plots", "Plots" + str(nSim))
            if os.path.isdir(PlotPath) is False:
                os.makedirs(PlotPath)
            
            plt.savefig(os.path.join(PlotPath, "PropagationTree" + str(nSim) +".png"), 
                        dpi=200, figsize=(200, 200), edgecolor='b', 
                        bbox_inches='tight', transparent=False)
            
            if self._pdfOutputs:
                plt.savefig(os.path.join(PlotPath, "PropagationTree" + str(nSim) +".pdf"), 
                            dpi=200, figsize=(200, 200), edgecolor='b', 
                            bbox_inches='tight', transparent=False)
            

        # Hitting times and ROSs
        if analysis_degree is True:
            dg_ros_out = sorted(list(H.out_degree(weight = 'ros')), key = itemgetter(1), reverse = True)
            dg_time_out = sorted(list(H.out_degree(weight = 'time')), key = itemgetter(1))

            PlotPath = os.path.join(self._OutFolder, "Plots", "Plots" + str(nSim))
            if os.path.isdir(PlotPath) is False:
                os.makedirs(PlotPath)
            
            plt.figure(2)
            dg_ros = dict(H.degree(weight='ros'))
            plt.hist(dg_ros.values())
            plt.title('ROS hit Histogram')
            plt.savefig(os.path.join(PlotPath, 'HitROS_Histogram.png'))
            
            plt.figure(3)
            dg_time = dict(H.degree(weight='time'))
            plt.hist(dg_time.values())
            plt.title('Time hit Histogram')
            plt.savefig(os.path.join(PlotPath, 'HitTime_Histogram.png'))

        plt.close("all")
              
    
    # Fire Spread evolution plots (per sim, version 2)
    def SimFireSpreadEvoV2(self, nSim, CoordCells, Colors, H=None, version=0, onlyGraph=True):
        if H is None:
            msgFileName = "MessagesFile0" if (nSim < 10) else "MessagesFile"
            H = nx.read_edgelist(path = os.path.join(self._MessagesPath, msgFileName + str(nSim) + ".csv"),
                                 create_using = nx.DiGraph(),
                                 nodetype = int,
                                 data = [('time', float), ('ros', float)],
                                 delimiter=',')
        
        # If MessageFile is empty, skip
        if len(H.nodes) > 0:
            # Cartesian positions
            coord_pos = dict() 

            # Generate G graph (empty)
            if self._GGraph is None:
                self.GGraphGen()
            for i in self._GGraph.nodes:
                coord_pos[i] = CoordCells[i-1] + 0.5

            # No nodes
            if onlyGraph is False:
                nx.draw_networkx_nodes(self._GGraph, pos = coord_pos,
                                       node_size = 4,
                                       nodelist = list(G.nodes),
                                       node_shape='s',
                                       node_color = Colors)

            # plt.figure(figsize = (15, 9)) 

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
            for _, spine in ax.spines.items():
                spine.set_visible(True)
            ax.get_xaxis().tick_bottom()  
            ax.get_yaxis().tick_left() 

            # Dimensionamos el eje X e Y
            plt.axis([-1, self._Rows, -1, self._Cols])    

            # Simple red
            if version == 0:
                nx.draw_networkx_edges(H, pos = coord_pos, node_size=0, 
                        edge_color= 'r', width=0.5, edge_cmap=plt.cm.Reds,
                        arrows=True, arrowsize=3, ax=ax, label="ROS messages")


            # Different plot versions
            elif version != 0 and H is not None:
                edges = H.edges()
                ross = [H[u][v]['ros'] for u,v in edges]
                times = [H[u][v]['time'] for u,v in edges]

                # Edge color = ROSs
                if version == 1:
                    plt.title("Propagation Tree: hitting ROS [m/min]")
                    nx.draw_networkx_edges(H, pos = coord_pos,  
                        edge_color=ross, width=1.0, edge_cmap=plt.cm.Reds,
                        arrows=True, arrowsize=3, ax=ax)
                    sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin=np.min(ross), vmax=np.max(ross)))                

                # Edge color = hit Times (normalized)
                if version == 2:
                    plt.title("Propagation Tree: traveling times [min]")
                    nx.draw_networkx_edges(H, pos = coord_pos,
                            edge_color=times, width=1.0, edge_cmap=plt.cm.Reds,  #edge_color=times/np.max(times)
                            arrows=True, arrowsize=3, ax=ax)
                    sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin=np.min(times), vmax=np.max(times)))

                # Edge color = Weights (Ross) and width = hit times (normalized)
                if version == 3:
                    plt.title("Propagation Tree: ROS (c) and times (w)")
                    nx.draw_networkx_edges(H, pos = coord_pos,
                            edge_color= ross/np.max(ross), width= times/np.max(times), edge_cmap=plt.cm.Reds,
                            arrows=True, arrowsize=3, ax=ax)
                    sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin=np.min(0), vmax=np.max(1)))


            # Add legend and coordinates (if needed)
            # plt.legend()
            XCoord = None
            YCoord = None

            # Create plots folder
            PlotPath = os.path.join(self._OutFolder, "Plots", "Plots" + str(nSim))
            if os.path.isdir(PlotPath) is False:
                os.makedirs(PlotPath)

            # Save Figure
            plt.axis('scaled')
            sm._A = []
            #plt.colorbar(sm, fraction=0.046, pad=0.04)
            #cax = ax.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])
            
            #ax.set_aspect('auto')
            divider = make_axes_locatable(ax)
            cax1 = divider.append_axes("right", size="5%", pad=0.05)
            plt.colorbar(sm, cax=cax1) 
            plt.savefig(os.path.join(PlotPath, "FireSpreadTree" + str(nSim) + "_" + str(version) + ".png"),
                        dpi=200,  figsize=(200, 200), 
                        bbox_inches='tight', transparent=False)
            
            if self._pdfOutputs:
                plt.savefig(os.path.join(PlotPath, "FireSpreadTree" + str(nSim) + "_" + str(version) + ".pdf"),
                            dpi=200,  figsize=(200, 200), 
                            bbox_inches='tight', transparent=False)
            plt.close("all")
        
    
    # Individual BP maps (for plotting the evolution of the fire)
    def plotEvo(self):
        # If nSims = -1, read the output folder
        if self._nSims == -1:
            # Read folders with Grids (array with name of files) 
            Grids = glob.glob(self._OutFolder + 'Grids/')
            self._nSims = len(Grids)
            
        # Grids files (final scars)
        a = 0
        
        #print("NSims:", self._nSims)
        
        # Stats per simulation
        for i in tqdm(range(self._nSims)):
            GridPath, GridFiles = self._GridDir(i)
            
            # Reset container
            a = 0         
            
            for j in range(len(GridFiles)):
                # Reset container
                a = 0         
            
                #print("J from GridGiles:", j, GridFiles[j])
                if len(GridFiles) > 0: 
                    a = pd.read_csv(GridPath +"/"+ GridFiles[j], delimiter=',', header=None).values
                    
                else:
                    if i != 0:
                        a = np.zeros([a.shape[0], a.shape[1]]).astype(np.int64)
                        
                    else:
                        a = np.zeros([self._Rows,self._Cols]).astype(np.int64)
                        
                # Set harvested to null prob
                a[a == 2] = 0
                #print("a:", a)

                # Generate BPHeatmap
                PlotPath = os.path.join(self._OutFolder, "Plots/Plots" + str(i + 1))
                if os.path.isdir(PlotPath) is False:
                    os.makedirs(PlotPath)
                
                num = str(j+1).zfill(2)
                self.BPHeatmap(a, Path=PlotPath, nscen=1, sq=True, namePlot="Fire" + num, 
                               Title="Burned Cells Fire Period " + str(j + 1), cbarF=True, ticks=False,
                               transparent=True)
            
    
    # Plot full forest (all cells and colors)
    def ForestPlot(self, LookupTable, data, Path, namePlot="InitialForest"):
        # Colors dictionary (container)
        myColorsD = {}

        # DF from lookup table
        DFColors = pd.read_csv(LookupTable)
        ColorsID = DFColors["grid_value"].values

        # Populate dict
        MColors = DFColors[[" r", " g", " b"]].values / 255.0
        MColors = [tuple(np.concatenate((i,[1.0]))) for i in MColors]

        aux = 0
        myColorsD = {}
        for i in ColorsID:
            myColorsD[i] = MColors[aux]
            aux += 1
        myColorsD[9999] = (1.0, 1.0, 1.0, 1.0)
        myColorsD[-1] = (6/255., 150/255., 165/255., 1.0) 
        
        mykeys = np.unique(data)

        aux = 0
        for val in mykeys:
            data[data == val] = aux
            aux += 1

        #print("Unique values:", mykeys)
        myColors = [myColorsD[x] for x in mykeys]
        #print("myColors:", myColors)

        # Plot
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
        plt.title(" ")

        if len(mykeys) > 1: 
            cmap = LinearSegmentedColormap.from_list('Custom', myColors, len(myColors))
            ax = sns.heatmap(data, cmap=cmap, linewidths=.0, linecolor='lightgray', annot=False, cbar=False,
                             square=True, xticklabels=False, yticklabels=False)

        else:
            cmap = colors.ListedColormap(myColors)
            boundaries = [-1, 1]
            norm = colors.BoundaryNorm(boundaries, cmap.N, clip=True)
            ax = sns.heatmap(data, cmap=cmap, linewidths=.0, linecolor='lightgray', 
                             annot=False, cbar=False, norm=norm, square=True,   # Testing new options for combining
                             xticklabels=False, yticklabels=False)       
        
            
        # Only y-axis labels need their rotation set, x-axis labels already have a rotation of 0
        _, labels = plt.yticks()
        plt.setp(labels, rotation=0)
        plt.savefig(os.path.join(Path, namePlot + ".png"), dpi=200, bbox_inches='tight', 
                    pad_inches=0, transparent=False)
        
        if self._pdfOutputs:
            plt.savefig(os.path.join(Path, namePlot + ".pdf"), dpi=200, bbox_inches='tight', 
                    pad_inches=0, transparent=False)

        plt.close("all")

    # Merge evolution plots with background (Initial forest)
    def combinePlot(self, BackgroundPath, fileN, Sim):
        # Read Forest
        ForestFile = os.path.join(BackgroundPath, "InitialForest.png")
        p1 = cv2.imread(ForestFile) 

        # Read Evo plot
        fstr = str(fileN).zfill(2)
        PathFile = os.path.join(BackgroundPath, "Plots", "Plots"+ str(Sim), "Fire" + fstr + ".png")
        p2 = cv2.imread(PathFile) 

        # Alpha channels
        p1 = cv2.cvtColor(p1, cv2.COLOR_BGR2RGBA)
        p2 = cv2.cvtColor(p2, cv2.COLOR_BGR2RGBA)
        p2[np.all(p2 >= [230, 230, 230, 230], axis=2)] = [0, 0, 0, 1]

        # Axis
        gca().set_axis_off()
        subplots_adjust(top = 1, bottom = 0, 
                        right = 1, left = 0, 
                        hspace = 0, wspace = 0)
        margins(0,0)
        gca().xaxis.set_major_locator(NullLocator())
        gca().yaxis.set_major_locator(NullLocator())

        # Create plot
        plt.imshow(p1, zorder=0)
        plt.imshow(p2, zorder=1)
        plt.savefig(PathFile, dpi=200, bbox_inches='tight', pad_inches=0, transparent=False)
        if self._pdfOutputs:
            PathFile = os.path.join(BackgroundPath, "Plots", "Plots"+ str(Sim), "Fire" + fstr + ".pdf")
            plt.savefig(PathFile, dpi=200, bbox_inches='tight', pad_inches=0, transparent=False)
        plt.close('all')
     
        
    
    # Merge the plots
    def mergePlot(self, multip=True):
        # Stats per simulation
        for i in tqdm(range(self._nSims)):
            PlotPath = os.path.join(self._OutFolder, "Plots", "Plots" + str(i + 1))
            PlotFiles = glob.glob(os.path.join(PlotPath, 'Fire[0-9]*.*'))
            
            if multip is False:
                for (j, _) in enumerate(PlotFiles):
                    self.combinePlot(self._OutFolder, j + 1, i + 1)  
            
            else:
                # Multiprocess
                jobs = []

                for (j, _) in enumerate(PlotFiles):
                    p = Process(target=self.combinePlot, args=(self._OutFolder, j + 1, i + 1,))
                    jobs.append(p)
                    p.start()

                # complete the processes
                for job in jobs:
                    job.join()            
    
    # General Stats (end of the fire stats per scenario) 
    def GeneralStats(self):
        # If nSims = -1, read the output folder
        if self._nSims == -1:
            # Read folders with Grids (array with name of files) 
            Grids = glob.glob(self._OutFolder + 'Grids/')
            self._nSims = len(Grids)

        # Grids files (final scars)
        a = 0
        b = []
        statDict = {}
        statDF = pd.DataFrame(columns=[["ID", "NonBurned", "Burned", "Harvested"]])

        # Stats per simulation
        for i in range(self._nSims):
            GridPath, GridFiles = self._GridDir(i)
            #print(GridPath, GridFiles)
            if len(GridFiles) > 0: 
                a = pd.read_csv(GridPath +"/"+ GridFiles[-1], delimiter=',', header=None).values
                b.append(a)
                statDict[i] = {"ID": i+1,
                               "NonBurned": len(a[(a == 0) | (a == 2)]),
                               "Burned": len(a[a == 1]), 
                               "Harvested": len(a[a == -1])}
            else:
                if i != 0:
                    a = np.zeros([a.shape[0], a.shape[1]]).astype(np.int64)
                    b.append(a)
                    statDict[i] = {"ID": i+1,
                                   "NonBurned": len(a[(a == 0) | (a == 2)]),
                                   "Burned": len(a[a == 1]), 
                                   "Harvested": len(a[a == -1])}
                else:
                    a = np.zeros([self._Rows,self._Cols]).astype(np.int64)
                    b.append(a)
                    statDict[i] = {"ID": i+1,
                                   "NonBurned": len(a[(a == 0) | (a == 2)]),
                                   "Burned": len(a[a == 1]), 
                                   "Harvested": len(a[a == -1])}
                                        
        # Generate CSV files
        if self._CSVs:
            # Dict to DataFrame
            A = pd.DataFrame(data=statDict, dtype=np.int32)
            A = A.T
            A = A[["ID", "NonBurned", "Burned", "Harvested"]]
            Aux = (A["NonBurned"] + A["Burned"] + A["Harvested"])
            A["%NonBurned"], A["%Burned"], A["%Harvested"] = A["NonBurned"] / Aux, A["Burned"] / Aux, A["Harvested"] / Aux
            A.to_csv(os.path.join(self._StatsFolder, "FinalStats.csv"), 
                     columns=A.columns, index=False, header=True, 
                     float_format='%.3f')
            
            # Final forest status boxplot
            self.FinalBoxPlots(OutFolder=self._StatsFolder)
            
            # Info
            if self._verbose:
                print("General Stats:\n", A)
                print(A[["Burned","Harvested"]].std())
            
            # General Summary
            SummaryDF = A.describe()
            SummaryDF.to_csv(os.path.join(self._StatsFolder, "General_Summary.csv"), header=True, 
                             index=True, columns=SummaryDF.columns, float_format='%.3f')
            if self._verbose:
                print("Summary DF:\n", SummaryDF)

        # Burnt Probability Heatmap
        if self._BurntProb:
            # Compute the global weighted Scar for heatmap
            #print("self._StatsFolder:", self._StatsFolder)
            WeightedScar = 0
            for i in range(len(b)):
                WeightedScar += b[i]                
            WeightedScar =  WeightedScar / len(b)    
            
            # Set harvested to null prob
            WeightedScar[WeightedScar == 2] = 0
            
            if self._verbose:
                print("Weighted Scar:\n", WeightedScar)
            
            # Generate BPHeatmap
            ticks = 5
            #print("self._Rows:", self._Rows)
            if self._Rows < 10:
                ticks = 2
            
            if self._Rows >= 10  and self._Rows <= 100:
                ticks = 10
            
            if self._Rows > 100 and self._Rows <= 1000:
                ticks = 100 
            #print("Ticks", ticks)
            self.BPHeatmap(WeightedScar, Path=self._StatsFolder, nscen=self._nSims, sq=True, ticks=ticks, cbarF=False)
            
            # Save BP Matrix
            np.savetxt(os.path.join(self._StatsFolder, "BProb.csv"), WeightedScar, 
                       delimiter=" ", fmt="%.3f")

    # Hourly stats (comparison of each hour evolution per fire)
    def HourlyStats(self):
        # If nSims = -1, read the output folder
        if self._nSims == -1:
            # Read folders with Grids (array with name of files) 
            Grids = glob.glob(self._OutFolder + 'Grids/')
            self._nSims = len(Grids)

        # Correct the number of grids (equal to all replications)
        if self._tCorrected:
            maxStep = 0
            for i in range(self._nSims):
                GridPath, GridFiles = self._GridDir(i)
                if len(GridFiles) > maxStep:
                    maxStep = len(GridFiles)
                        
            for i in range(self._nSims):
                GridPath, GridFiles = self._GridDir(i)
                if len(GridFiles) < maxStep:
                    for j in range(len(GridFiles), maxStep):
                        file = 'ForestGrid{:02d}.csv'.format(j)
                        copy2(os.path.join(GridPath, GridFiles[-1]),
                              os.path.join(GridPath, file))
            
        
        # Grids files (per hour)  
        ah = 0
        bh = {}
        statDicth = {}
        statDFh = pd.DataFrame(columns=[["ID", "NonBurned", "Burned", "Harvested"]])
        for i in range(self._nSims):
            GridPath, GridFiles = self._GridDir(i)
            if len(GridFiles) > 0:
                for j in range(len(GridFiles)):
                    ah = pd.read_csv(GridPath +"/"+ GridFiles[j], delimiter=',', header=None).values
                    bh[(i,j)] = ah
                    statDicth[(i,j)] = {"ID": i+1,
                                       "NonBurned": len(ah[(ah == 0) | (ah == 2)]),
                                       "Burned": len(ah[ah == 1]), 
                                       "Harvested": len(ah[ah == -1]),
                                       "Hour": j+1}
            else:
                if i != 0:
                    ah = np.zeros([ah.shape[0], ah.shape[1]]).astype(np.int64)
                    bh[(i,j)] = ah
                    statDicth[(i,j)] = {"ID": i+1,
                                        "NonBurned": len(ah[(ah == 0) | (ah == 2)]),
                                        "Burned": len(ah[ah == 1]), 
                                        "Harvested": len(ah[ah == -1]),
                                        "Hour": j+1}
                else:
                    ah = np.zeros([self._Rows,self.Cols]).astype(np.int64)
                    bh[(i,0)] = ah
                    statDicth[(i,0)] = {"ID": i+1,
                                        "NonBurned": len(ah[(ah == 0) | (ah == 2)]),
                                        "Burned": len(ah[ah == 1]), 
                                        "Harvested": len(ah[ah == -1]),
                                        "Hour": 0 + 1}
           
        # Generate CSV files
        if self._CSVs:
            # Dict to DataFrame   
            Ah = pd.DataFrame(data=statDicth, dtype=np.int32)
            Ah = Ah.T
            Ah[["Hour", "NonBurned", "Burned", "Harvested"]] = Ah[["Hour", "NonBurned", "Burned", "Harvested"]].astype(np.int32)
            Ah = Ah[["ID", "Hour", "NonBurned", "Burned", "Harvested"]]
            Aux = (Ah["NonBurned"] + Ah["Burned"] + Ah["Harvested"])
            Ah["%NonBurned"], Ah["%Burned"], Ah["%Harvested"] = Ah["NonBurned"] / Aux, Ah["Burned"] / Aux, Ah["Harvested"] / Aux
            Ah.to_csv(os.path.join(self._StatsFolder, "HourlyStats.csv"), columns=Ah.columns, index=False, 
                      header=True, float_format='%.3f')
            if self._verbose:
                print("Hourly Stats:\n",Ah)

            # Hourly Summary
            SummaryDF = Ah[["NonBurned", "Burned", "Harvested", "Hour"]].groupby('Hour')["NonBurned", "Burned", "Harvested"].mean()
            SummaryDF.rename(columns={"NonBurned":"AVGNonBurned", "Burned":"AVGBurned", "Harvested":"AVGHarvested"}, inplace=True)
            SummaryDF[["STDBurned", "STDHarvested"]] = Ah[["NonBurned", "Burned", "Harvested", "Hour"]].groupby('Hour')["Burned","Harvested"].std()[["Burned","Harvested"]]
            SummaryDF[["MaxNonBurned", "MaxBurned"]] = Ah[["NonBurned", "Burned", "Harvested", "Hour"]].groupby('Hour')["NonBurned", "Burned"].max()[["NonBurned", "Burned"]]
            SummaryDF[["MinNonBurned", "MinBurned"]] = Ah[["NonBurned", "Burned", "Harvested", "Hour"]].groupby('Hour')["NonBurned", "Burned"].min()[["NonBurned", "Burned"]]
            Aux = (SummaryDF["AVGNonBurned"] + SummaryDF["AVGBurned"] + SummaryDF["AVGHarvested"])
            SummaryDF["%AVGNonBurned"], SummaryDF["%AVGBurned"], SummaryDF["%AVGHarvested"] = SummaryDF["AVGNonBurned"] / Aux, SummaryDF["AVGBurned"] / Aux, SummaryDF["AVGHarvested"] / Aux
            SummaryDF.reset_index(inplace=True)
            SummaryDF.to_csv(os.path.join(self._StatsFolder, "HourlySummaryAVG.csv"), header=True, 
                             index=False, columns=SummaryDF.columns, float_format='%.3f')
            if self._verbose:
                print("Summary DF:\n", SummaryDF)

        # Hourly BoxPlots
        if self._boxPlot:
            self.BoxPlot(Ah, yy="Burned", ylab="# Burned Cells", pal="Reds", title="Burned Cells evolution", 
                         Path=self._StatsFolder, namePlot="BurnedCells_BoxPlot", swarm=False)
            self.BoxPlot(Ah, yy="NonBurned", ylab="# NonBurned Cells", pal="Greens", title="NonBurned Cells evolution", 
                         Path=self._StatsFolder, namePlot="NonBurnedCells_BoxPlot", swarm=False)
            self.BoxPlot(Ah, yy="Harvested", ylab="# Harvested Cells", pal="Blues", title="Harvested Cells evolution", 
                         Path=self._StatsFolder, namePlot="HarvestedCells_BoxPlot", swarm=False)
            
        
        # Hourly histograms
        all_zeros = not Ah["Burned"].any()
        if self._histograms is True and self._nSims > 1 and all_zeros is False:
            self.plotHistogram(Ah, NonBurned=True, xx="Hour", xmax=6, KDE=True, 
                               title="Histogram: Burned and NonBurned Cells",
                               Path=self._StatsFolder, namePlot="Densities")
