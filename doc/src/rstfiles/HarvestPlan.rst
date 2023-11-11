Evaluating a Harvest Plan
=========================

Harvest plans are entered in csv file that has one row for each year with the year number followed by the cells
harvested at the beginning of that year. The ``--HarvestedCells`` option gives the name 


Band first year: 
----------------

This is very articial harvest plan to illustrate how the inputs work.
For the first have take the year number and cell numbers as
1,20,60,100,140..,1580. The second year we plan to harvest a cell
next to the cell harvest the previous year (alternating sides), so the input for the
second year is 2, 19,61,99,141 ...

Input Command:

::
   
    python main.py --input-instance-folder ../data/Harvest40x40/ --output-folder ../Harvest40x40 --ignitions --sim-years 2 --nsims 1 --grids --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.0 --seed 123 --stats --allPlots --IgnitionRad 1 --grids --combine --HarvestedCells ../data/Harvest40x40/band1_2.csv
	

Output:

Once we run the program we create a series of outputs in the Harvest40x40 folder. The Harvest40x40 folder will have the output in the form of Grids, Plots and Stats. 

As we have harvested enough cells the fire does not propogate. We have
strategically harvested cells in a staight line starting from cell
20,60,100..1580. This results in stopping fire spread even though
there is more forest cover which would be burned if we did not stop
its propogation via harvesting. So there should be some
 cells harvested in the second year.


Stochastics?
------------

ROS CV
^^^^^^

In the next command we allow variation in the rate of spread by giving it a CV of 0.8 so we run
5 simulations to get statistics (which won't vary much).

::

    python main.py --input-instance-folder ../data/Harvest40x40/ --output-folder ../Harvest40x40 --ignitions --sim-years 2 --nsims 5 --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.8 --seed 123 --stats --allPlots --IgnitionRad 1 --grids --combine --HarvestedCells ../data/Harvest40x40/band1_2.csv


Random Ignitions
^^^^^^^^^^^^^^^^

In the next command, we add uniform random ignitions (but dropping the ``--ignitions`` option).

::
   
    python main.py --input-instance-folder ../data/Harvest40x40/ --output-folder ../Harvest40x40 --sim-years 2 --nsims 5 --grids --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.8 --seed 123 --stats --allPlots --IgnitionRad 1 --combine --HarvestedCells ../data/Harvest40x40/band1_2.csv


Random Weather
^^^^^^^^^^^^^^

Random weather is supported by providing multiple weather files in the ``Weathers`` sub-directory
of the input directory. Each weather file has the name WeatherX.csv, where is X is replaced by an integer.
There should be one file per integer (0..--nweathers) and use ``--weather random`` to trigger
randomly selecting one for each run (note whether random ignitions is on or off).

::
   
    python main.py --input-instance-folder ../data/Harvest40x40/ --output-folder ../Harvest40x40 --ignitions --sim-years 2 --nsims 5 --grids --finalGrid --weather random --nweathers 200 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.8 --seed 123 --stats --allPlots --IgnitionRad 1 --combine --HarvestedCells ../data/Harvest40x40/band1_2.csv

The value of ``--nweathers`` should be less than or equal to the number of the weather files in the ``Weathers`` subdirectory.
