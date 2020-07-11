==============
Ignition Point
==============

To change the initiation cell of fire we need to edit the file Ignitions.csv which is located in the following location:

.. code-block:: html
   :linenos:

   Cell2Fire/contributed/delme63/9cellsC1


We can edit this file using either Excel or Numbers(Mac). Cells are numbered as shown below:

.. image:: /image/Ignitions/Cellnumbering.png
   :width: 50%

This gives us the options to edit in which cell the fire would start.
Where the fire starts along with the wind direction provides important information on its spread.


Tests
-----

The test will have the following values:

* Wind speed: 25 km/h
* Wind Direction: 45 degrees (NE winds)
* All other values are kept the same.

The only changes we would make is in the initiation cell of the fire and then map the spread of the fire.

**For test 1 we will keep the Ignition point in cell 7:**

.. image:: /image/Fire01.jpg
   :width: 23%
.. image:: /image/Ignitions/7hr6.png
   :width: 23%
.. image:: /image/Ignitions/7hr8.png
   :width: 23%
.. image:: /image/Ignitions/7hr9.png
   :width: 23%

In test 1 we notice that due to wind direction and starting point it is harder for the fire to spread. Hence fire is not able to spread to all of the cells.

**For Test 2 we will keep the Ignition point in cell 3:**

.. image:: /image/Ignitions/Cell31.png
   :width: 30%
.. image:: /image/Ignitions/Cell32.png
   :width: 30%
.. image:: /image/Ignitions/Cell33.png
   :width: 30%

In test 2 we notice that it takes only three hours for the fire to cover all the cells.
As we can notice fire starting from cell 3 spreads faster as it is in the direction of the wind.
