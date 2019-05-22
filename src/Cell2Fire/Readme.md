# Cell2Fire: A Cell Based Forest Fire Growth Model  C++/Python
## Cristobal Pais, Jaime Carrasco, David Martell, David L. Woodruff, Andres Weintraub
Main program 

# Requirements
- Boost (C++)
- Eigen (C++)
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


# Post-Processing  
Only processing (reads a previously simulated instance and computes stats/plots).
Important: provide the number of sims --nsims to be processed
```
$ python main.py --input-instance-folder /mnt/c/Users/Lenovo/documents/GitHub/Cell2Fire/data/9cells/ --output-folder /mnt/c/Users/Lenovo/Desktop/9cells --nsims 10 --stats --allPlots --onlyProcessing
```
