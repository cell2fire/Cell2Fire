====================
How to Run Simulator
====================

**To run the simulator you will have to be in the following path:**

.. code-block:: html
   :linenos:

    cd Desktop/FolderName/src/Cell2Fire

**Once we are in the above directory we could run the following command:**

.. code-block:: html
   :linenos:

    $ python main.py --input-instance-folder ../../data/Sub40x40/ --output-folder ../../results/Sub40x40 --ignitions --sim-years 1 --nsims 5 --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.0 --seed 123 --stats --allPlots --IgnitionRad 5 --grids --combine

**To get the full list of arguments and their explanations we can use the following command:**

.. code-block:: html
   :linenos:

   $ python main.py -h
