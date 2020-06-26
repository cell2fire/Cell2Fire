============
Installation 
============

If you are not a programmer, these instructions may be difficult. If
you get frustrated, jump to the section on using docker.

First, be sure that boost, eigen and gcc are installed on your computer. 

Download the zip file and extract
it in a folder in your preferred directory (I used Desktop). Or clone
the githup repository (these instructions assume you cloned in Desktop)

.. code-block:: html
   git clone https://github.com/cell2fire/Cell2Fire.git

Give a terminal command to cd to the C++ directory, e.g.,

.. code-block:: html
   :linenos:
   
    cd Desktop/Cell2Fire/cell2fire/Cell2FireC
    
then edit Makefile to have the correct path to Eigen. Then,

.. code-block:: html
   :linenos:
   
      make
      cd ../..   # (the working directory should now be Cell2Fire)
      pip install -r requirements.txt
      python setup.py develop

