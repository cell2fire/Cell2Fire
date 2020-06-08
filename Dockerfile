# to build: docker build -t c2fcondatest .
# local test: docker run -it --mount source=$(pwd),destination=/src,type=bind c2fcondatest:latest
FROM continuumio/anaconda3
RUN conda install -c anaconda numpy
RUN conda install -c anaconda pandas
RUN conda install -c anaconda matplotlib
RUN conda install -c anaconda seaborn
RUN conda install -c conda-forge tqdm
RUN conda install -c conda-forge imread
