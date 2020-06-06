====================
How to Run Simulator  
====================

In able to run the file you will have to be cd into src/Cell2Fire

.. code-block:: html
   :linenos:
   
    cd Desktop/FolderName/src/Cell2Fire
    
then the following command can be used in this directory:

.. code-block:: html
   :linenos:
   
    $ python main.py --input-instance-folder ../../data/Sub40x40/ --output-folder ../../results/Sub40x40 --ignitions --sim-years 1 --nsims 5 --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.0 --seed 123 --stats --allPlots --IgnitionRad 5 --grids --combine
    
For the full list of arguments and their explanations use the following command in the same directory:

.. code-block:: html
   :linenos:
   
   $ python main.py -h