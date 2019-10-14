Changing the grid
=================

The Cell2Fire simulator is by default set to run on a 9x9 grid. Recently there has been added a 16 cell and a 12 cell example that is available to use. The other option
would be creating your own which could be done by the following steps:

* You will need to find your contributed folder and create a duplicate of delme63.
* From there you will need to edit your go bash to have the right directory to your file (Look at editing Code Line section for help)

From here you have a couple files you will need find in your current 9cellsC1 that will allow you to edit the grid size.
First you will need find both Data.csv and Data.dat. To open these files it recommended to have Microsoft Excell and a text editing program.
After opening both files you will see they will have the same amount of Data lines 9 each. From here,depending on what grid size you would like, copy one of the lines and 
paste the line in an empty section. The following is an example of the 16 cell:

.. image:: /image/data.png
   :width: 25%
.. image:: /image/excell.png
   :width: 50%
   
You will need the same amount of entries equaling to size of grid you want to create of n columns and m rows.

From here find another file the 9cellsC1 folder named Forest.asc and will have to add a couple parts. To change cell size you will need to input the amount of rows and columns 
wanted for the grid. In the 16 cell example the input has 4 columns and 4 rows here is an example of the code:

.. image:: /image/Forest.png
   :width: 40%
   
Notice in the bottom of the code there is grid which you must create to resemble the desired cell grid. Using 1 to edit this sections create the desired grid, save, and exit the inputs.
From here run the code the same way you would the original code from here the results should be different resulting in a different size grid:

.. image:: /image/16cell1.png
  :width: 25% 
.. image:: /image/16cell2.png
  :width: 25%   