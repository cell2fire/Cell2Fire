What are HCELLS (Harvested Cells):
==================================

The different types of cells in our model are:

* NCells denote the total number of cells in our grid.
* HCells are the harvested cells that have either burned due to fire or have been harvested.

Hcells denote the harvested cells in our grid which can not catch fire and act as breaks to wildfires. These cells could have been harvested either by earlier fires or can strategically be cut to reduce the spread of fire and arrest the spread of fires so that large contiguous areas don't catch fire. 

To simulate the program with harvested cells, we need to run the program and set-up our Cell2Fire folder from GIT hub. Then we run the program and once the file structure is created in our Cell2Fire document, we could open the Data folder and create a new .csv file to provide input for --HarvestedCells command. 

How to create a new CSV file
----------------------------

After setting up Cell2fire and running the program we need to create a .csv file to provide input for --HarvestedCells to simulate a real-life fire situation. Comma Separated Values or .csv file should just have numerical values as their inputs. The .csv file should contain the number of years and the cell number as inputs e.g. 1, 1, 2, 3, 5, 8. Once we have created the CSV file we could save it as harvestedCells.csv in the following path ../data/Harvest40x40. 

Now to simulate the program we would need to provide the inputs required by each function. For --HarvestedCells we would have to provide the location of the harvestedCells.csv file as aninput. 


Illustrations
-------------

**input command:**

.. code-block:: html
   :linenos:
   
    python main.py --input-instance-folder ../data/Harvest40x40/ --output-folder ../Harvest40x40 --ignitions --sim-years 1 --nsims 100        --grids --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.8 --seed 123 --stats               --allPlots --IgnitionRad 1 --grids --combine --heuristic 1 --GASelection --HarvestedCells ../data/Harvest40x40/harvestedCells.csv

Using the above command we could run our program to create plots that will depict the spread of fire and the effect of providing input cells that are already burnt or harvested. 


**Output:**

The output of the program would be stored in Cell2Fire document. We can access the new folder that would be created after running the program and access the various Plots, Stats, Grids, and messages.

By running multiple simulations we could reach an optimal solution which would enhance our chance to utilize our model to effectively manage the spread of forest fires.

