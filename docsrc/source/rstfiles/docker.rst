.. _docker-section:

Using Docker
============


If you have a lot of trouble installing the software on your
computer, you can try running it under a docker image. If you are
not familiar with docker, you may find it a little confusing,
but the installation of Cell2Fire is much simpler (once you have docker
installed and running). You also need to install ``git``.


Note that in these instructions some command arguments have a single dash,
while others have a double-dash.

Install Docker
^^^^^^^^^^^^^^

Install docker and start the docker daemon: https://docs.docker.com/get-docker/


Install Cell2Fire in the Docker Image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On a Unix host machine, run this sequence of terminal commands. If any command fails,
the subsequent commands will fail:

* git clone https://github.com/cell2fire/Cell2Fire

* cd Cell2Fire

* ``docker run -it --mount source=$(pwd),destination=/Cell2Fire,type=bind dlwoodruff/c2fcondatest:latest``

* cd Cell2Fire
  
* python setup.py develop

* cd cell2fire

* cd Cell2FireC

* make

* cd ..

To test your installation, try

``python main.py --help``

When you are done using the docker image, give the command ``exit`` to
the hashtag prompt.

You don't have repeat the installation steps every time you run. In subsequent
sessions you can cd to the Cell2Fire directory that you installed and
start with the ``docker run`` command.

Running on Windows
^^^^^^^^^^^^^^^^^^

On Windows machines, terminal commands are given to the ``DOS`` command prompt. These instructions
assume you are running in DOS terminal and not some other shell.

Replace the ``docker run`` command with this:

* ``docker run --rm -it -v %cd%:/Cell2Fire dlwoodruff/c2fcondatest:latest``

Note that it might take docker a minute or two to start the image.
The commands you give to the docker image (with the `#` prompt) are
unix commands, even if the docker image is running on a Windows
machine.

File access
^^^^^^^^^^^

The ``-v`` argument (or ``--mount`` on Unix) gives the image
(and programs running it) access to the entire Cell2Fire directory
structure on your computer, but it will not have access to any other
files or directories on your computer. But you want to specify
subdirectories, you use the forward slash as in Unix rather than the
backslash even if your host computer is a  Windows machine.

The commands in the documentation assume you are running on Unix, and
if you are running inside the docker image, then you are running
on Unix. The docker image has its own Python and it cannot
access any other Python.
