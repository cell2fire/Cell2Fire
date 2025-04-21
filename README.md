# Cell2Fire: A Cell Based Forest Fire Growth Model  C++/Python
## Cristobal Pais, Jaime Carrasco, David Martell, David L. Woodruff, Andres Weintraub

# Disclaimer

This software is for research use only. There is no warranty of any kind;
there is not even the implied warranty of fitness for use.

![](https://github.com/cell2fire/Cell2Fire/workflows/TestExamples/badge.svg)

# Introduction

Cell2Fire is a new cell-based forest and wildland landscape fire spread simulator.
The fire environment is characterized by partitioning the landscape into a large number of homogeneous cells and specifying the fuel, weather, fuel moisture and topography attributes of each cell.
Fire spread within each cell is assumed to be elliptical and governed by spread rates predicted by any independent fire spread model (e.g. the Canadian Forest Fire Behavior Prediction System).
Cell2Fire exploits parallel computation methods which allows users to run large-scale simulations in short periods of time.
It includes powerful statistical, graphical output, and spatial analysis features to facilitate the display and analysis of projected fire growth.

Work in progress documentation is available at
[readthedocs](https://cell2fire.readthedocs.io/) and there is an
original draft of a paper on
[arXiv](https://arxiv.org/abs/1905.09317v1).

# Citation

@ARTICLE{Cell2Fire,
AUTHOR={Pais, Cristobal and Carrasco, Jaime and Martell, David L. and Weintraub, Andres and Woodruff, David L.},
TITLE={Cell2Fire: A Cell-Based Forest Fire Growth Model to Support Strategic Landscape Management Planning},  
JOURNAL={Frontiers in Forests and Global Change},
VOLUME={4},
YEAR={2021},
URL={https://www.frontiersin.org/articles/10.3389/ffgc.2021.692706},
DOI={10.3389/ffgc.2021.692706},
ISSN={2624-893X}
}
   
# Requirements
- g++
- Boost (C++)
- Eigen (C++)
- Python >3.6; you might need 3.12
- numpy
- pandas
- matplotlib
- seaborn
- tqdm
- opencv
- imageio (replaced imread, April 2026)
- networkx (for stats module)

# Installation

Installation may require some familiarity with C++, make, and Python. 
- cd Cell2Fire/cell2fire/Cell2FireC
- (edit Makefile to have the correct path to Eigen)
- make
- cd ../..
- pip install -r requirements.txt  # might not do anything
- pip install -e .

# Usage
In order to run the simulator (after installation and cd to  Cell2Fire/cell2fire), the following command can be used:
```
$ python main.py --input-instance-folder ../data/Sub40x40/ --output-folder ../results/Sub40x40 --ignitions --sim-years 1 --nsims 5 --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.0 --seed 123 --stats --allPlots --IgnitionRad 5 --grids --combine
```
For the full list of arguments and their explanation use:
```
$ python main.py -h
```

In addition, both the C++ core and Python scripts can be used separately:
## C ++
Only simulation and generate evolution grids (no stats or plots).
Parallel-ready version will be uploaded soon.
```
$ ./Cell2Fire --input-instance-folder ../data/Sub40x40/ --output-folder ../results/Sub40x40 --ignitions --sim-years 1 --nsims 1 --grids --final-grid --Fire-Period-Length 1.0 --weather rows --nweathers 1 --output-messages --ROS-CV 0.0 --seed 123 --IgnitionRad 0 --HFactor 1.0 --FFactor 1.0 --BFactor 1.0 --EFactor 1.0
```


## Python 
Only processing option (reads a previously simulated instance and computes stats/plots).
Important: provide the number of sims --nsims to be processed
```
$ python main.py --input-instance-folder ../data/Sub40x40/ --output-folder ../results/Sub40x40_Previous_simulation --nsims 10 --stats --allPlots --onlyProcessing
```

# Output examples
## Dogrib forest (Canadian instance)
![Dogrib Instance](outputs/Example4.png)

## Visualize shortest paths propagation (10 scens)
![Dogrib Fire Propagation and ROS map](outputs/Example1.png)

## Shortest paths propagation and ROS intensity (10 scens)
![Dogrib Fire Propagation map](outputs/Example2.png)

## Burn-Probability maps (10 scens)
![Dogrib BP map](outputs/Example3.png)
