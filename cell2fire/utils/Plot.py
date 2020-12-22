# coding: utf-8
__version__ = "2.0"
__author__ = "Cristobal Pais"
__maintainer__ = "Jaime Carrasco, Cristobal Pais, David Woodruff"
__status__ = "Alpha Operational"

# Importations
# import sys
import os
import imread

#Visual importations
from matplotlib.pylab import *
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.patches as patches
import itertools
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

'''
Returns      void

Inputs:
Colors       string array
Coords       array of 2D double arrays
counter      int
Year         int
showtrue     boolean
r            int
col          int
Folder       string
'''
# Plot class: All methods needed for plotting the forest status	
class Plot:
    # Plot initial forest
    def PlotForestOnly(self,Colors,Coords,counter,period,Year,showtrue,r,col,Folder):
        # Max and min status values (for colors)
        min_val = 0
        max_val = 2

        # Colorbar dictionary
        cdict1 = {'red':   ((0.0, 0.0, 0.0),(0.0, 0.0, 0.1),(1.0, 1.0, 1.0)),
                  'green':  ((0.0, 0.0, 0.6),(1.0, 0.0, 0.0),(1.0, 0.0, 0.0)),
                  'blue':   ((0.0, 0.0, 0.0),(1.0, 0.1, 0.0),(1.0, 0.0, 0.0))
                 }
                
        green_red = LinearSegmentedColormap('GreenRed', cdict1)
        plt.register_cmap(cmap=green_red)

        my_cmap = cm.get_cmap(green_red) # or any other one
        norm = matplotlib.colors.Normalize(min_val, max_val) # the color maps work for [0, 1]

        #Colours' definitions (status)
        # Available: Green 
        x_i = 0
        color_i = my_cmap(norm(x_i)) # returns an rgba value
            
        # Burnt: Orange
        x_i2 = 1
        color_i2 = my_cmap(norm(x_i2)) # returns an rgba value
        
        # Burning: Red and different levels depending on the period (decay factor)
        x_i3 = 2
        color_i3 = my_cmap(norm(x_i3)) # returns an rgba value
        x_i32 = 1.8
        color_i32 = my_cmap(norm(x_i32)) # returns an rgba value
        x_i33 = 1.6
        color_i33 = my_cmap(norm(x_i33)) # returns an rgba value
        x_i34 = 1.4
        color_i34 = my_cmap(norm(x_i34)) # returns an rgba value
        x_i35 = 1.2
        color_i35 = my_cmap(norm(x_i35)) # returns an rgba value
        
        # Harvested: green/orange
        x_i4 = 0.6
        color_i4 = my_cmap(norm(x_i4)) # returns an rgba value
        
        cmmapable = cm.ScalarMappable(norm, my_cmap)
        cmmapable.set_array(range(min_val, max_val))

        #Scatter data
        c = col
        x = np.linspace(0, c, c+1)
        y = np.linspace(0, r, r+1)
        pts = itertools.product(x, y)

        #Initializing figures
        figure()
        ax = gca()

        # Markers (if wanted, uncomment)
        #ax.scatter(*zip(*pts), marker='o', s=30, color='red', zorder=2)

        #Rectangle
        fillcolor=color_i
        edgecolor="None"#'k'
        lwidth=1.0
        
        rectangle = []
        
        # Fill figure
        for c in range(0, len(Colors)):
                rectangle.append(plt.Rectangle((Coords[c][0], Coords[c][1]), 1, 1, 
                                               fc=Colors[c], ec=edgecolor, linewidth=lwidth))
        for i in range(0, len(Colors)):
            ax.add_patch(rectangle[i])

        #Grid (if wanted, uncomment)
        #plt.grid()

        #Title (if wanted, uncomment)
        #plt.title('Fire simulation Year '+str(Year) +' period '+str(period))
        plt.title(".",color="white")
        plt.axis('scaled')
  
        XCoord = None
        YCoord = None
        
        #Path and name of the file
        PathFile = os.path.join(Folder, "ForestInitial.png")
        #plt.axis('off')
        
        #Save the file
        plt.savefig(PathFile,dpi=200, bbox_inches='tight')
        plt.close("all")
        
        # Show image if asked
        if showtrue == True:
            show()

            
    
    '''
    Returns      void
    
    Inputs:
    Cells_Obj    objects array (cells objects)
    msg_list     array of integer arrays (multidimensional)
    counter      int
    period       int
    Year         int
    showtrue     boolean
    r            int
    col          int
    Folder       string
    Sim          int
    '''
    def forest_plotV3(self,Cells_Obj,msg_list,counter,period,Year,showtrue,r,col,Folder,Sim):
        #Max and min status values
        min_val = 0
        max_val = 2

        #Colorbar dictionary
        cdict1 = {'red':   ((0.0, 0.0, 0.0),(0.0, 0.0, 0.1),(1.0, 1.0, 1.0)),
                  'green':  ((0.0, 0.0, 0.6),(1.0, 0.0, 0.0),(1.0, 0.0, 0.0)),
                  'blue':   ((0.0, 0.0, 0.0),(1.0, 0.1, 0.0),(1.0, 0.0, 0.0))
                 }
                
        green_red = LinearSegmentedColormap('GreenRed', cdict1)
        plt.register_cmap(cmap=green_red)

        my_cmap = cm.get_cmap(green_red) # or any other one
        norm = matplotlib.colors.Normalize(min_val, max_val) # the color maps work for [0, 1]

        #Colours' definitions (status)
        # Available: Green 
        x_i = 0
        color_i = my_cmap(norm(x_i)) # returns an rgba value
    
        # Burnt: Orange
        x_i2 = 1
        color_i2 = my_cmap(norm(x_i2)) # returns an rgba value
        
        # Burning: Red and different levels depending on the period (decay factor)
        x_i3 = 2
        color_i3 = my_cmap(norm(x_i3)) # returns an rgba value
        x_i32 = 1.8
        color_i32 = my_cmap(norm(x_i32)) # returns an rgba value
        x_i33 = 1.6
        color_i33 = my_cmap(norm(x_i33)) # returns an rgba value
        x_i34 = 1.4
        color_i34 = my_cmap(norm(x_i34)) # returns an rgba value
        x_i35 = 1.2
        color_i35 = my_cmap(norm(x_i35)) # returns an rgba value
        
        # Harvested: green/orange
        x_i4 = 0.6
        color_i4 = my_cmap(norm(x_i4)) #(228, 191, 164, 0.8) # # returns an rgba value
        
        #Determining cells' colors
        # If cell has been initialized (o/w, keep original colors)
        for c in Cells_Obj.keys():
            # if cell is burning, depending on the number of periods, red tends to be orange
            #print("Cell:", c, "Status:", Cells_Obj[c].Status, "FireStart:", Cells_Obj[c].Firestarts, "period:", period)	
            if Cells_Obj[c].Status == 1:
                #First burning period
                if Cells_Obj[c].Firestarts == period:
                    Cells_Obj[c].Color = color_i3
                    
                #Second burning period
                if Cells_Obj[c].Firestarts == (period-1):
                    Cells_Obj[c].Color = color_i32
                    
                #Third burning period
                if Cells_Obj[c].Firestarts == (period-2):
                    Cells_Obj[c].Color = color_i33
                    
                #Fourth burning period
                if Cells_Obj[c].Firestarts == (period-3):
                    Cells_Obj[c].Color = color_i34
                    
                #Fifth burning period
                if Cells_Obj[c].Firestarts == (period-4):
                    Cells_Obj[c].Color = color_i35
                
                #More burning periods
                if Cells_Obj[c].Firestarts < (period-4):
                    Cells_Obj[c].Color = color_i2
                    
            # if cell is burnt (but not burning), orange (be careful with number, harvested)
            elif Cells_Obj[c].Status == 2:
                Cells_Obj[c].Color = color_i2
            
            # if cell is harvested, different green
            elif Cells_Obj[c].Status == 3:
                Cells_Obj[c].Color = color_i4
            
        cmmapable = cm.ScalarMappable(norm, my_cmap)
        cmmapable.set_array(range(min_val, max_val))

        #Scatter data
        c = col
        x = np.linspace(0, c, c+1)
        y = np.linspace(0, r, r+1)
        pts = itertools.product(x, y)

        #Initializing figures
        figure()
        ax = gca()

        #Markers
        #ax.scatter(*zip(*pts), marker='o', s=30, color='red', zorder=2)

        #Rectangle
        fillcolor=color_i
        edgecolor="None"#'k' if black borders are wanted
        lwidth=1.0
        
        rectangle = []
        rectangle.append(plt.Rectangle((0, r-1), 1, 1, fc=(1.0,1.0,1.0,0.0),ec=edgecolor,linewidth=lwidth))
        rectangle.append(plt.Rectangle((0, 0), 1, 1, fc=(1.0,1.0,1.0,0.0),ec=edgecolor,linewidth=lwidth))
        rectangle.append(plt.Rectangle((c-1, r-1), 1, 1, fc=(1.0,1.0,1.0,0.0),ec=edgecolor,linewidth=lwidth))
        rectangle.append(plt.Rectangle((c-1, 0), 1, 1, fc=(1.0,1.0,1.0,0.0),ec=edgecolor,linewidth=lwidth))
        
        # For burning cells
        for c in Cells_Obj.keys():
            if Cells_Obj[c].Status != "Available":
                rectangle.append(plt.Rectangle((Cells_Obj[c].Coord[0], Cells_Obj[c].Coord[1]), 1, 1, 
                                               fc=Cells_Obj[c].Color,ec=edgecolor,linewidth=lwidth))
        
            
        for i in range(0,len(rectangle)):
            ax.add_patch(rectangle[i])
            
        #Grid
        #plt.grid()

        #Title
        plt.title('Fire simulation Year '+str(Year) +' period '+str(period))
        plt.axis('scaled')

        #Arrows
        #plt.quiver(x, y , size, angle, color='r', units='x',linewidths=(2,), edgecolors=('k'), headaxislength=5,zorder=3)
        #QP = plt.quiver(2.0,1 ,5, 0, color='r', units='x',linewidths=(2,), edgecolors=('k'), headaxislength=5,zorder=0)
        
        XCoord = None
        YCoord = None
        
        # Plot messages arrows
        for cell in msg_list.keys():
            for adj in msg_list[cell]:
                    XCoord = Cells_Obj[adj-1].Coord[0] - Cells_Obj[cell-1].Coord[0]
                    YCoord = Cells_Obj[adj-1].Coord[1] - Cells_Obj[cell-1].Coord[1]
        
                    u = XCoord
                    v = YCoord
        
                    # Plot arrows
                    plt.quiver(Cells_Obj[cell-1].Coord[0] + 0.5 + 0.4 * u,
                               Cells_Obj[cell-1].Coord[1] + 0.5 + 0.4 * v,
                               u, v, color='r', units='x', linewidths=(2,), 
                               edgecolors=('k'), headaxislength=5, zorder=3)

        # Save
        Folder = os.path.join(Folder, "Plots"+str(Sim))
        if not os.path.exists(Folder):
            os.makedirs(Folder)
        fstr = str(counter).zfill(4)
        PathFile = os.path.join(Folder,"forest"+fstr+".png")
        
        #Save the file
        plt.savefig(PathFile, dpi=200, figsize=(200, 200), bbox_inches='tight', transparent=True)
        plt.close("all")
        
        if showtrue == True:
            show()
    
    
    
    '''
    Returns      void
    
    Inputs:
    Cells_Obj    objects array (cells objects)
    msg_list     array of integer arrays (multidimensional)
    counter      int
    period       int
    Year         int
    showtrue     boolean
    r            int
    col          int
    Folder       string
    Sim          int
    Coords       array of integers
    Positions    array of integers
    '''
    def forest_plotV3_Operational(self, Cells_Obj, msg_list, counter, period,Year,
                                  showtrue, r, col, Folder, Sim, Coords, Positions):
        #Max and min status values
        min_val = 0
        max_val = 2

        #Colorbar dictionary
        cdict1 = {'red':   ((0.0, 0.0, 0.0),(0.0, 0.0, 0.1),(1.0, 1.0, 1.0)),
                  'green':  ((0.0, 0.0, 0.6),(1.0, 0.0, 0.0),(1.0, 0.0, 0.0)),
                  'blue':   ((0.0, 0.0, 0.0),(1.0, 0.1, 0.0),(1.0, 0.0, 0.0))
                 }
                
        green_red = LinearSegmentedColormap('GreenRed', cdict1)
        plt.register_cmap(cmap=green_red)

        my_cmap = cm.get_cmap(green_red) # or any other one
        norm = matplotlib.colors.Normalize(min_val, max_val) # the color maps work for [0, 1]

        #Colours' definitions (status)
        # Available: Green 
        x_i = 0
        color_i = my_cmap(norm(x_i)) # returns an rgba value
    
        # Burnt: Orange
        x_i2 = 1
        color_i2 = my_cmap(norm(x_i2)) # returns an rgba value
        
        # Burning: Red and different levels depending on the period (decay factor)
        x_i3 = 2
        color_i3 = my_cmap(norm(x_i3)) # returns an rgba value
        x_i32 = 1.8
        color_i32 = my_cmap(norm(x_i32)) # returns an rgba value
        x_i33 = 1.6
        color_i33 = my_cmap(norm(x_i33)) # returns an rgba value
        x_i34 = 1.4
        color_i34 = my_cmap(norm(x_i34)) # returns an rgba value
        x_i35 = 1.2
        color_i35 = my_cmap(norm(x_i35)) # returns an rgba value
        
        # Harvested: green/orange
        x_i4 = 0.6
        color_i4 = my_cmap(norm(x_i4)) #(228, 191, 164, 0.8) # # returns an rgba value
        
        #Determining cells' colors
        # If cell has been initialized (o/w, keep original colors)
        for c in Cells_Obj.keys():
            # if cell is burning, depending on the number of periods, red tends to be orange
            #print("Cell:", c, "Status:", Cells_Obj[c].Status, "FireStart:", Cells_Obj[c].Firestarts, "period:", period)	
            if Cells_Obj[c].Status == 1:
                #First burning period
                if Cells_Obj[c].Firestarts == period:
                    Cells_Obj[c].Color = color_i3
                    
                #Second burning period
                if Cells_Obj[c].Firestarts == (period-1):
                    Cells_Obj[c].Color = color_i32
                    
                #Third burning period
                if Cells_Obj[c].Firestarts == (period-2):
                    Cells_Obj[c].Color = color_i33
                    
                #Fourth burning period
                if Cells_Obj[c].Firestarts == (period-3):
                    Cells_Obj[c].Color = color_i34
                    
                #Fifth burning period
                if Cells_Obj[c].Firestarts == (period-4):
                    Cells_Obj[c].Color = color_i35
                
                #More burning periods
                if Cells_Obj[c].Firestarts < (period-4):
                    Cells_Obj[c].Color = color_i2
                    
            # if cell is burnt (but not burning), orange (be careful with number, harvested)
            elif Cells_Obj[c].Status == 2:
                Cells_Obj[c].Color = color_i2
            
            # if cell is harvested, different green
            elif Cells_Obj[c].Status == 3:
                Cells_Obj[c].Color = color_i4
            
        cmmapable = cm.ScalarMappable(norm, my_cmap)
        cmmapable.set_array(range(min_val, max_val))

        #Scatter data
        c = col
        x = np.linspace(0, c, c+1)
        y = np.linspace(0, r, r+1)
        pts = itertools.product(x, y)

        #Initializing figures
        figure()
        ax = gca()

        #Markers
        #ax.scatter(*zip(*pts), marker='o', s=30, color='red', zorder=2)

        #Rectangle
        fillcolor=color_i
        edgecolor="None"#'k' if black borders are wanted
        lwidth=1.0
        
        rectangle = []
        rectangle.append(plt.Rectangle((0, r-1), 1, 1, fc=(1.0,1.0,1.0,0.0),ec=edgecolor,linewidth=lwidth))
        rectangle.append(plt.Rectangle((0, 0), 1, 1, fc=(1.0,1.0,1.0,0.0),ec=edgecolor,linewidth=lwidth))
        rectangle.append(plt.Rectangle((c-1, r-1), 1, 1, fc=(1.0,1.0,1.0,0.0),ec=edgecolor,linewidth=lwidth))
        rectangle.append(plt.Rectangle((c-1, 0), 1, 1, fc=(1.0,1.0,1.0,0.0),ec=edgecolor,linewidth=lwidth))
        
        # For burning cells
        for c in Cells_Obj.keys():
            if Cells_Obj[c].Status != "Available":
                rectangle.append(plt.Rectangle((Cells_Obj[c].Coord[0], Cells_Obj[c].Coord[1]), 1, 1, 
                                               fc=Cells_Obj[c].Color,ec=edgecolor,linewidth=lwidth))
        
        # Team positions
        for c in Positions:
            if c != -1:
                rectangle.append(plt.Rectangle((Coords[c-1][0], Coords[c-1][1]), 1, 1, 
                                               fc="yellow", ec=edgecolor, linewidth=lwidth))
        
        # Add rectangles
        for i in range(0,len(rectangle)):
            ax.add_patch(rectangle[i])
            
        #Grid
        #plt.grid()

        #Title
        plt.title('Fire simulation Year '+str(Year) +' period '+str(period))
        plt.axis('scaled')

        #Arrows
        #plt.quiver(x, y , size, angle, color='r', units='x',linewidths=(2,), edgecolors=('k'), headaxislength=5,zorder=3)
        #QP = plt.quiver(2.0,1 ,5, 0, color='r', units='x',linewidths=(2,), edgecolors=('k'), headaxislength=5,zorder=0)
        
        XCoord = None
        YCoord = None
        
        # Plot messages arrows
        for cell in msg_list.keys():
            for adj in msg_list[cell]:
                    XCoord = Cells_Obj[adj-1].Coord[0] - Cells_Obj[cell-1].Coord[0]
                    YCoord = Cells_Obj[adj-1].Coord[1] - Cells_Obj[cell-1].Coord[1]
        
                    u = XCoord
                    v = YCoord
        
                    # Plot arrows
                    plt.quiver(Cells_Obj[cell-1].Coord[0] + 0.5 + 0.4 * u,
                               Cells_Obj[cell-1].Coord[1] + 0.5 + 0.4 * v,
                               u, v, color='r', units='x', linewidths=(2,), 
                               edgecolors=('k'), headaxislength=5, zorder=3)

        # Save
        Folder = os.path.join(Folder, "Plots"+str(Sim))
        if not os.path.exists(Folder):
            os.makedirs(Folder)
        fstr = str(counter).zfill(4)
        PathFile = os.path.join(Folder,"forest"+fstr+".png")
        
        #Save the file
        plt.savefig(PathFile, dpi=200, figsize=(200, 200), bbox_inches='tight', transparent=True)
        plt.close("all")
        
        if showtrue == True:
            show()
    
    
    '''
    Returns      void
    
    Inputs:
    Cells_Obj    objects array|dictionary (cells objects)
    msg_list     array of integer arrays (multidimensional)
    counter      int
    period       int
    Year         int
    showtrue     boolean
    r            int
    col          int
    Folder       string
    Coords       array of 2D int arrays
    BurntCells   int set
    Sim          int
    '''
    def forest_plotV3_FreeMem(self, Cells_Obj, msg_list, counter, period, Year, showtrue,
                              r, col, Folder, Coords, BurntCells, Sim):
        #Max and min status values
        min_val = 0
        max_val = 2

        #Colorbar dictionary
        cdict1 = {'red':   ((0.0, 0.0, 0.0),(0.0, 0.0, 0.1),(1.0, 1.0, 1.0)),
                  'green':  ((0.0, 0.0, 0.6),(1.0, 0.0, 0.0),(1.0, 0.0, 0.0)),
                  'blue':   ((0.0, 0.0, 0.0),(1.0, 0.1, 0.0),(1.0, 0.0, 0.0))
                 }
                
        green_red = LinearSegmentedColormap('GreenRed', cdict1)
        plt.register_cmap(cmap=green_red)

        my_cmap = cm.get_cmap(green_red) # or any other one
        norm = matplotlib.colors.Normalize(min_val, max_val) # the color maps work for [0, 1]

        #Colours' definitions (status)
        # Available: Green 
        x_i = 0
        color_i = my_cmap(norm(x_i)) # returns an rgba value
    
        # Burnt: Orange
        x_i2 = 1
        color_i2 = my_cmap(norm(x_i2)) # returns an rgba value
            
        # Burning: Red and different levels depending on the period (decay factor)
        x_i3 = 2
        color_i3 = my_cmap(norm(x_i3)) # returns an rgba value
        x_i32 = 1.8
        color_i32 = my_cmap(norm(x_i32)) # returns an rgba value
        x_i33 = 1.6
        color_i33 = my_cmap(norm(x_i33)) # returns an rgba value
        x_i34 = 1.4
        color_i34 = my_cmap(norm(x_i34)) # returns an rgba value
        x_i35 = 1.2
        color_i35 = my_cmap(norm(x_i35)) # returns an rgba value
        
        # Harvested: green/orange
        x_i4 = 0.6
        color_i4 = my_cmap(norm(x_i4)) # returns an rgba value
        
        #Determining cells' colors
        for c in Cells_Obj.keys():
            # if cell is burning, depending on the number of periods, red tends to be orange
            if Cells_Obj[c].Status == 1:
                #First burning period
                if Cells_Obj[c].Firestarts == period:
                    Cells_Obj[c].Color = color_i3
                
                #Second burning period
                if Cells_Obj[c].Firestarts == (period-1):
                    Cells_Obj[c].Color = color_i32
                
                #Third burning period
                if Cells_Obj[c].Firestarts == (period-2):
                    Cells_Obj[c].Color = color_i33
                
                #Fourth burning period
                if Cells_Obj[c].Firestarts == (period-3):
                    Cells_Obj[c].Color = color_i34
                
                #Fifth burning period
                if Cells_Obj[c].Firestarts == (period-4):
                    Cells_Obj[c].Color = color_i35
                
                #More burning periods
                if Cells_Obj[c].Firestarts < (period-4):
                    Cells_Obj[c].Color = color_i2
                    
            # if cell is burnt (but not burning), orange 
            elif Cells_Obj[c].Status == 2:
                Cells_Obj[c].Color = color_i2
            
            # if cell is harvested, different green
            elif Cells_Obj[c].Status == 3:
                Cells_Obj[c].Color = color_i4
        
        cmmapable = cm.ScalarMappable(norm, my_cmap)
        cmmapable.set_array(range(min_val, max_val))

        #Scatter data
        c = col
        x = np.linspace(0, c, c+1)
        y = np.linspace(0, r, r+1)
        pts = itertools.product(x, y)

        #Initializing figures
        figure()
        ax = gca()

        #Markers
        #ax.scatter(*zip(*pts), marker='o', s=30, color='red', zorder=2)

        #Rectangle
        fillcolor=color_i
        edgecolor="None"#'k'
        lwidth=1.0
        
        rectangle = []
        rectangle.append(plt.Rectangle((0, r-1), 1, 1, fc=(1.0,1.0,1.0,0.0),ec=edgecolor,linewidth=lwidth))
        rectangle.append(plt.Rectangle((0, 0), 1, 1, fc=(1.0,1.0,1.0,0.0),ec=edgecolor,linewidth=lwidth))
        rectangle.append(plt.Rectangle((c-1, r-1), 1, 1, fc=(1.0,1.0,1.0,0.0),ec=edgecolor,linewidth=lwidth))
        rectangle.append(plt.Rectangle((c-1, 0), 1, 1, fc=(1.0,1.0,1.0,0.0),ec=edgecolor,linewidth=lwidth))
        
        # for active cells
        for c in Cells_Obj.keys():
            if Cells_Obj[c].Status != "Available":
                rectangle.append(plt.Rectangle((Cells_Obj[c].Coord[0], Cells_Obj[c].Coord[1]), 1, 1, 
                                               fc=Cells_Obj[c].Color,ec=edgecolor,linewidth=lwidth))
        
        # for burnt cells
        for c in BurntCells:
            if (c-1) not in Cells_Obj.keys():
                rectangle.append(plt.Rectangle((Coords[c-1][0], Coords[c-1][1]), 1, 1, 
                                               fc=color_i2,ec=edgecolor,linewidth=lwidth))
        
        # Add rectangles to plot
        for i in range(0,len(rectangle)):
            ax.add_patch(rectangle[i])

        #Grid
        #plt.grid()
    
        #Title
        plt.title('Fire simulation Year '+str(Year) +' period '+str(period))
        plt.axis('scaled')

        #Arrows
        #plt.quiver(x, y , size, angle, color='r', units='x',linewidths=(2,), edgecolors=('k'), headaxislength=5,zorder=3)
        #QP = plt.quiver(2.0,1 ,5, 0, color='r', units='x',linewidths=(2,), edgecolors=('k'), headaxislength=5,zorder=0)
        
        XCoord = None
        YCoord = None
        
        # for active cells
        for cell in msg_list.keys():
            for adj in msg_list[cell]:
                    XCoord = Cells_Obj[adj-1].Coord[0] - Cells_Obj[cell-1].Coord[0]
                    YCoord = Cells_Obj[adj-1].Coord[1] - Cells_Obj[cell-1].Coord[1]
        
                    u = XCoord
                    v = YCoord
    
                    # Plot arrows
                    plt.quiver(Cells_Obj[cell-1].Coord[0] + 0.5 + 0.4 * u,
                               Cells_Obj[cell-1].Coord[1] + 0.5 + 0.4 * v,
                               u,v, color='r', units='x', linewidths=(2,), 
                               edgecolors=('k'), headaxislength=5, zorder=3)
        
        #Put a colorbar
        #colorbar(cmmapable)
        Folder = os.path.join(Folder, "Plots"+str(Sim))
        if not os.path.exists(Folder):
            os.makedirs(Folder)
        fstr = str(counter).zfill(4)
        PathFile = os.path.join(Folder,"forest"+fstr+".png")
               
        #Save the file
        plt.savefig(PathFile, dpi=200, figsize=(200, 200), bbox_inches='tight', transparent=True)
        plt.close("all")
        
        if showtrue == True:
            show()
    
    '''
    Returns      void
    
    Inputs:
    Folder       string
    filen        int
    Sim          int
    '''
    # Mixes the evolution plots with the base forest (initial state for saving memory/time)
    def Mix(self,Folder,filen,Sim):
        img = imread(os.path.join(Folder, "ForestInitial.png"))
        fstr = str(filen).zfill(4)
        
        #Path and name of the file
        PathFile = os.path.join(Folder, "Plots", "Plots"+str(Sim), "forest" + fstr + ".png")
        
        # Reads the basic forest
        img2 = imread(PathFile)
        
        # Over plot
        gca().set_axis_off()
        subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                        hspace = 0, wspace = 0)
        margins(0,0)
        gca().xaxis.set_major_locator(NullLocator())
        gca().yaxis.set_major_locator(NullLocator())
        
        plt.imshow(img,zorder=0)
        plt.imshow(img2,zorder=1)
        plt.savefig(PathFile, dpi=200, bbox_inches='tight', pad_inches=0)
        plt.close("all")
    
    def MultiFireMix(self,Folder,nSims,mode="Scale",probs=[]):
            # Read initial forest status
            imgForest = imread(os.path.join(Folder, "ForestInitial.png"))
            #fstr = str(filen).zfill(4)
            
            # If no probs provided, alpha = 0.25 by default (otherwise, transparency is proportional to the fire probability)
            if len(probs) == 0:
                probs = np.full(nSims, 1/nSims)
            
            #Path and name of the file
            PathFile = []
            for i in range(1, nSims+1):
                #PathFile.append(os.path.join(Folder, "Plots", "Plots"+str(i), "forest" + fstr + ".png"))
                ScarPath = os.path.join(Folder, "Plots", "Plots"+str(i))
                ScarFiles = os.listdir(ScarPath)
                PathFile.append(ScarPath +"/"+ScarFiles[-1])
                #print(ScarFiles[-1])
            
            # Reads the basic forest
            imgArray = []
        
            for i in range(nSims):
                imgArray.append(imread(PathFile[i]))
                #print(imgArray[i].shape)
            
            # Summation mode: sum the pixels values for highlighting the intersections of fires (more intense than Scale)
            if mode == "Sum":
                SumPixels = np.zeros([imgArray[0].shape[0], imgArray[0].shape[1], imgArray[0].shape[2]])
                for i in range(nSims):
                    SumPixels[:,:,] += imgArray[i][:,:,]
                
                # Trick for seeing less likely scar
                SumPixels[:,:,] += 1

                # Divide by the total number of simulations 
                SumPixels /= (nSims+1)
            
            # Over plot
            gca().set_axis_off()
            subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                            hspace = 0, wspace = 0)
            margins(0,0)
            gca().xaxis.set_major_locator(NullLocator())
            gca().yaxis.set_major_locator(NullLocator())
            
            # Plot the initial forest state
            plt.imshow(imgForest,zorder=0)
            
            # Sum or Scale
            if mode == "Sum":
                plt.imshow(SumPixels, zorder=0, alpha=1, vmin=0, vmax=255)
            
            # Plot each fire
            else:
                 for i in range(nSims):
                    plt.imshow(imgArray[i], zorder=i, alpha=probs[i], vmin=0, vmax=255)

            # Save the combined picture
            plt.savefig(os.path.join(Folder, "Plots", "MultiFire_Plot"+mode+".png"), dpi=200, bbox_inches='tight', pad_inches=0)
            plt.close("all")	