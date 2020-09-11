Evaluating a Harvest Plan
=========================

Harvest plans are entered in csv file that has one row for each year with the year number followed by the cells
harvested at the beginning of that year.


Band first year: 
----------------

This is very articial harvest plan to illustrate how the inputs work.
For the first have take the year number and cell numbers as
1,20,60,100,140..,1580. The second year we plan to harvest two cells
year each of the cells harvest in the first year, so the input for the
second year is 2, 19,21, 59,61, 99, 101, ..., 1579, 1581.

Input Command:

::
   
    python main.py --input-instance-folder ../data/Harvest40x40/ --output-folder ../Harvest40x40 --ignitions --sim-years 2 --nsims 5 --grids --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.8 --seed 123 --stats --allPlots --IgnitionRad 1 --grids --combine --heuristic 1 --GASelection --HarvestedCells ../data/Harvest40x40/harvestedCells.csv
	

Output:

Once we run the program we create a series of outputs in Harvest40x40 folder which would be saved in the Cell2Fire directory. The Harvest40x40 folder will have the output in the form of Grids, Plots and Stats. 

We could show how the fire has spread through the BP_HeatMap.png saved in our Stats Directory. 

.. image:: /image/BP_HeatMap2.png
   :width: 50%

As we have harvested enough cells the fire does not propogate. We have strategically harvested cells in a staight line starting from cell 20,60,100..1580. This results in stopping fire spread even though there is more forest cover which would be burned if we did not stop its propogation via harvesting.


