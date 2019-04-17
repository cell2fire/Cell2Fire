# Cell2Fire: A Cell Based Forest Fire Growth Model  C++/Python
## Cristobal Pais, Jaime Carrasco, David Martell, David L. Woodruff, Andres Weintraub
Cell2Fire is a new cell-based forest and wildland landscape fire spread simulator.
The fire environment is characterized by partitioning the landscape into a large number of homogeneous cells and specifying the fuel, weather, fuel moisture and topography attributes of each cell.
Fire spread within each cell is assumed to be elliptical and governed by spread rates predicted by any independent fire spread model (e.g. the Canadian Forest Fire Behavior Prediction System).
Cell2Fire exploits parallel computation methods which allows users to run large-scale simulations in short periods of time.
It includes powerful statistical, graphical output, and spatial analysis features to facilitate the display and analysis of projected fire growth.

# Requirements
- Boost
- Eigen
- Python 3.6
- numpy
- pandas
- matplotlib
- seaborn
- tqdm
- networkx (for stats module)

# Usage
In order to run the simulator and process the results, the following command can be used:
```
$ python main.py --input-instance-folder ../data/Sub40x40/ --output-folder ../Sub40x40 --ignitions --sim-years 1 --nsims 100 --grids --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.8 --seed 123 --stats --allPlots --IgnitionRad 1
```
For the full list of arguments and their explanation use:
```
$ python main.py -h
```

In addition, both the C++ core and Python scripts can be used separately:
## C ++
Only simulation and generate evolution grids (no stats or plots).
```
$ ./Cell2Fire --input-instance-folder ../data/Sub40x40/ --output-folder ../results/Sub40x40 --ignitions --sim-years 1 --nsims 1 --grids --final-grid --Fire-Period-Length 1.0 --weather rows --nweathers 1 --output-messages --ROS-CV 0.0 --seed 123 --IgnitionRad 0 --HFactor 1.0 --FFactor 1.0 --BFactor 1.0 --EFactor 1.0
```


## Python 
Only processing (reads a previously simulated instance and computes stats/plots).
Important: provide the number of sims --nsims to be processed
```
$ python main.py --input-instance-folder /mnt/c/Users/Lenovo/documents/GitHub/Cell2Fire/data/9cells/ --output-folder /mnt/c/Users/Lenovo/Desktop/9cells --nsims 10 --stats --allPlots --onlyProcessing
```

# Output examples
![Dogrib Fire Propagation and ROS map](outputs/Example1.png)
![Dogrib Fire Propagation map](outputs/Example2.png)
![Dogrib BP map](outputs/Example3.png)
