Editing Code Line
=================

Another are where you can make changes to the Fire simulator is in going into

.. code-block:: html
   :linenos:
   
   mydirectory/contributed/delme63/go.bash
   
this will work with any of the other projects that you would like to work on as well not just delme63.
You will need to open go.bash with your favorite text editing app (I used Xcode) and get the following code


.. image:: /image/codeline.png
  :width: 99%
  
if you are working on a different folder that is not delme63 make your directory is correctly pathed to file you are working with.
It is only recommended to edit the following inputs

* Number of years (Up to 4)
* Number of simulations


Changing # of years
-------------------

In the command line of your go.bash file you will have a section that looks like 

.. code-block:: html
   :linenos:
   
   --sim-years 1
   
from here this will let you chose how many years per simulation you can have. This would give you more data as you could start the ignition point and see how it happen 
if it started at different locations.

Number of simulations
---------------------
To change the number of simulations which will output multiple stats depending on the number of simulations. This can be edited in the command line at

.. code-block:: html
  :linenos:
  
  --nsmis #
  
This will give you multiple outputs depending on your # of simulations.

For example when the command line had 

.. code-block:: html
  :linenos:
  
  --nsmis 10
  
which resulted in 10 graphs (i don't recommend)

.. image:: /image/plots.png
  :width: 30%

