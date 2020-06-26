Using Docker
============


If you have a lot of trouble installing the software on your
computer, you can try running it under a docker image. If you are
not familiar with docker, you may find it a little confusing,
but the installation of Cell2Fire is much simpler (once you have docker
installed and running).

Install
^^^^^^^

Install docker and start the docker daemon: https://docs.docker.com/get-docker/

Then run this sequence of terminal commands. If any command fails, the subsequent commands will fail:

* git clone https://github.com/cell2fire/Cell2Fire

  * cd Cell2Fire

  * docker run -it --mount source=$(pwd),destination=/Cell2Fire,type=bind c2fcondatest:latest

  * cd Cell2Fire
  
  * python setup.py develop

  * cd cell2fire

  * cd Cell2FireC

  * make

  * cd ..

To test your installation, try
python main.py --help

When you are done using the docker image, give the command ``exit`` to
the hashtag prompt.

You don't have repeat the installation steps every time you run. In subsequent
sessions you can cd to the Cell2Fire directory that you installed and
start with the ``docker run`` command.

