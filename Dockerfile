# to build: docker build -t c2fcondatest:latest .
# local test: docker run -it --mount source=$(pwd),destination=/src,type=bind c2fcondatest:latest
# docker push dlwoodruff/c2fcondatest:latest
FROM continuumio/anaconda3
RUN conda update conda
RUN conda install -c anaconda numpy
RUN pip install imread
#RUN conda install -c conda-forge imread
RUN conda install -c anaconda pandas
RUN conda install -c anaconda matplotlib
RUN conda install -c anaconda seaborn
RUN conda install -c conda-forge tqdm
#RUN conda install -c conda-forge opencv
RUN pip install opencv-python
RUN apt update
RUN apt install -y build-essential
# we will assume that eign3 goes to /usr/include
RUN apt-get install -y libeigen3-dev
RUN apt install -y libboost-dev
RUN apt install -y libboost-all-dev
RUN apt install -y curl
