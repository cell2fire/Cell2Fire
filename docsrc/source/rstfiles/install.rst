============
Installation 
============

To be able to run the file will first need to download the zip file and extract
it in a folder in your preferred directory (I used Desktop). Or clone
the githup repository (these instructions assume you cloned in Desktop)

Give a terminal command to cd to the directory, e.g.,

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
