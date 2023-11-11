Notes Concerning Installation
=============================

As noted in the top level `README.md` file, installation
is presently best done by someone with some knowledge
of C++, make, and Python. Although the software
can be run on a Windows machine, we are presently giving
installation instructions only for Unix. In the future, we plan
to make the installation a little easier.

Overview
--------

* Install dependencies for C++
* `make`
* Install dependencies for Python
* `python setup.py develop`
* Test the installation and perhaps discover the need for more Python packages

Install dependencies for C++
----------------------------

The packages `boost` and `eigen` must be installed. You can probably
install `boost` using a command like

::

   sudo apt-get install libboost-all-dev

You can install `eigen` using a command like

::
   
   sudo apt install libeigen3-dev

You need to find out where it is installed on your machine
(perhaps `/usr/include/eigen3/`)

make
----

cd to `Cell2Fire/src/Cell2Fire/Cell2FireC` then edit the file named
`Makefile` and change the first line to have the correct path to
`eigen` so it might look something like:

::
   
   EIGENDIR = /usr/include/eigen3/

then give the command

::

   make

Python dependencies
-------------------

There is a list of Python dependencies in the top level `README.md` file.
Some of them may already be installed. You can google how to install
python packages on your machine and for your Python (e.g., we recommend
Anaconda Python and conda package manager).

setup.py
--------

cd to `Cell2Fire/src` and give the command

::

   python setup.py develop

Test the installation
---------------------

cd to `Cell2Fire/src/Cell2Fire` and give the command

::

   python main.py --help

.. note::

   There are two dashes before ``help``.

You should see a long list of command line options, but you might see
a message that an import failed, which would mean that you need to
install the Python package named in the error message.

Once that works, you can try

::

   python main.py --input-instance-folder ../../data/Sub40x40/ --output-folder ../../results/Sub40x40 --ignitions --sim-years 1 --nsims 5 --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.0 --seed 123 --stats --allPlots --IgnitionRad 5 --grids --combine

.. note::

   Depending on how up-to-date your Python packages are, you might see deprecation warnings
   from some Python packages.

There should be newly created outputs in the directory `Cell2Fire/results/Sub40x40`.  In particular, the directory `Cell2Fire/results/Sub40x40/Plots/Plots1' should have a series of `png` files that show the evolution of the fire. If
you have ``ffmpeg` installed, you make a movie of the fire using a
command like

::
   
   ffmpeg -i Fire%2d.png firemovie.gif

or

::

   ffmpeg -i Fire%2d.png -filter:v "setpts=15.0*PTS"  firemovie.gif

to slow down the movie. In either case, the file
`firemovie.gif' then contains the movie.

(Or on Windows use software such as ImageMagick)
