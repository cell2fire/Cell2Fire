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
   
from here you are able to change how many years you want to simulate up to 4 years. This is use full as in your ignition point file you are able to edit
where the fire starts for each of those 4 years.