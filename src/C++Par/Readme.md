# Cell2Fire: A Cell Based Forest Fire Growth Model  C++/Python
## Cristobal Pais, Jaime Carrasco, David Martell, David L. Woodruff, Andres Weintraub
This project includes the Parallel C++ core implementation of Cell2Fire simulator.

# Version: Beta OpenMP ready
Experimental parallel version after the adaptation to new sim structure. 
Known bug: new manageFire() function (CellsFBP.cpp) modifies df_ptr (solved) and FSCell (not solved) values. Thus, although very unlikely, we can have memory access problems when having a large number of threads.
Potential solution: local copy of FSCell, return it, and then update the global variable in the main.
Current solution: run it AS-IS and "normally" it will not have an error. If needed, uncomment the omp critical section (Cell2Fire line 721) or run the serial version.

# Requirements (libraries)
- Boost
- Eigen

# Usage
To run a simulation:
```
$ ./Cell2Fire --nthreads 1 --input-instance-folder ../data/Sub40x40/ --output-folder ../results/Sub40x40 --ignitions --sim-years 1 --nsims 1 --grids --final-grid --Fire-Period-Length 1.0 --weather rows --nweathers 1 --output-messages --ROS-CV 0.0 --seed 123 --IgnitionRad 0 --HFactor 1.0 --FFactor 1.0 --BFactor 1.0 --EFactor 1.0
```
The main output of this code consists of a series of binary .csv files (matrices) where 1s represent burned cells and 0s available ones. 
These grids will be processed by the Python code in order to generate all relevant statistics and visualizations.

