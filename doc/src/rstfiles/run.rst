====================
How to Run Simulator  
====================

In able to run the file you will have to cd to Cell2Fire/cell2fire

then the following command can be used in this directory:

.. code-block:: html
   :linenos:
   
    python main.py --input-instance-folder ../data/Sub40x40/ --output-folder ../results/Sub40x40 --ignitions --sim-years 1 --nsims 5 --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.0 --seed 123 --stats --allPlots --IgnitionRad 5 --grids --combine

This command sends output to the directory specified by ``--output-folder``, namely ``../results/Sub40x40``.
    
For the full list of arguments and their explanations use the following command in the same directory:

.. code-block:: html
   :linenos:
   
   python main.py -h
