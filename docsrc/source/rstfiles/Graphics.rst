=====================================
Create Graphics for Forest Fire Model
=====================================

Once we have run our Cell2Fire using docker image we create various outputs in
the form of **.png** which are saved in the contributed folder.
As the outputs are based on same geographical location with change in time being
the only difference, therefore we can easily showcase these images in the form of clips.
This would make it simpler to analyze the spread of fire and the magnitude of
its extent.

To convert the images in the form of **.gif** files we have to follow these steps:
----------------------------------------------------------------------------------

* We need to download **Pillow** to convert .png files to .gif.
Open the bash window and download using the command

.. code-block:: html
   :linenos:

   pip install Pillow


* Once we have installed the pillow package we could open our code block gif.py
in the following file location.

.. code-block:: html
   :linenos:

   mydirectory/Cell2Fire/docsrc/source/gif.py

* In the python program we need to specify the location of the images which would
be converted to gif. Once we mention the **.png** files that need to be converted
we run the **gif.py** file to get a gif formed by the **.png** files we just choose. 
The output will be shown as **gen_output.gif** and can be accessed through the following path: 
.. code-block:: html
   :linenos:

   Cell2Fire/results/Sub40x40/Plots/Plots1
 

This gif.py file can also be used to convert other outputs to the **.gif** format.



