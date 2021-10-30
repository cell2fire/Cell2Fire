=====================================
Create GIF image for Forest Fire Model
=====================================

We can create a short movie of files plots and observe the trends of the images. 
After running the simulator of the Cell2Fire project, we obtain several plots as outputs
in the **Plots** directory. We can cd to the following location to verify that:
.. code-block:: html
   :linenos:

   cd Cell2Fire/results/Sub40x40/Plots

or we can just check that in the folder locally.


Here are the specific steps about how to generate a **gif** file from the outputs. 


Steps to convert images to the form of **.gif** files:
----------------------------------------------------------------------------------

The gif file can be created when we run the **gif.py** file, which combines several .png files into a short "movie".

Here are the specific steps to create the gif file:

1. cd to a plot dirctory that contains the png files that we want to use to create the gif file.
Take Plots1 as an example:
.. code-block:: html
   :linenos:

   cd Cell2Fire/results/Sub40x40/Plots/Plots1

2. run  **gif.py** file for the plot set we choose.
run the command like:
.. code-block:: html
   :linenos:

   python gif.py

3. The output will be shown as **gen_output.gif** and can be accessed through the following path:
.. code-block:: html
   :linenos:

   Cell2Fire/results/Sub40x40/Plots/Plots1

We can check that in the folder and open it.

.. image:: ../image/gifgenerate/gifpicture.png
   :width: 40%

The **gif** file can be opened to see the animation.


