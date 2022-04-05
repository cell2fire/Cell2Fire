EIGENDIR     = /usr/include/eigen3/
# EIGENDIR     = /usr/local/include/eigen3/ # For Mac only.
CC = g++
MPCC = g++
OPENMP = -openmp
CFLAGS = -std=c++11 -O3 -I$(EIGENDIR)
LIBS = -m64 -fPIC -fno-strict-aliasing -fexceptions -DNDEBUG -DIL_STD -lm -lpthread -ldl

TARGETS = Cell2Fire
all:	$(TARGETS)

# if not Ubuntu, then OSX is assumed.
OS = Ubuntu

# Mode is Parallel if it is not Serial
MODE=Serial
PARALLEL_DIR = parallel_code/Cell2FireParallel/Cell2FireC_Parallel

Cell2Fire: Cell2Fire.o CellsFBP.o FBPfunc5_NoDebug.o SpottingFBP.o ReadCSV.o ReadArgs.o Lightning.o WriteCSV.o Ellipse.o

# This will cause 'Extraneous text after `ifneq' directive'
ifneq ($(OS), Ubuntu) && ($(OS), OSX))
$(info OS must be either Ubuntu or OSX)
endif

ifneq ($(MODE), Serial) && ($(MODE), Parallel))
$(info MODE must be either Serial or Parallel)
endif

ifeq ($(MODE), Serial)
		$(CC) -o $@ $(LIBS) Cell2Fire.o CellsFBP.o FBPfunc5_NoDebug.o SpottingFBP.o ReadCSV.o ReadArgs.o Lightning.o WriteCSV.o Ellipse.o
else
ifeq ($(OS), Ubuntu)
	$(CC) -o $@ $(LIBS) -fopenmp Cell2Fire.o CellsFBP.o FBPfunc5_NoDebug.o SpottingFBP.o ReadCSV.o ReadArgs.o Lightning.o WriteCSV.o Ellipse.o
else
	$(CC) -o $@ $(LIBS) -Xclang -fopenmp -lomp Cell2Fire.o CellsFBP.o FBPfunc5_NoDebug.o SpottingFBP.o ReadCSV.o ReadArgs.o Lightning.o WriteCSV.o Ellipse.o
endif
endif

Cell2Fire.o: Cell2Fire.cpp CellsFBP.o FBPfunc5_NoDebug.o SpottingFBP.o ReadCSV.o ReadArgs.o WriteCSV.o
ifeq ($(MODE), Serial)
	$(CC) -c $(CFLAGS) Cell2Fire.cpp
else
ifeq ($(OS), Ubuntu)
	$(CC) -c $(CFLAGS) -fopenmp Cell2Fire.cpp
else
	$(CC) -c $(CFLAGS) -Xclang -fopenmp -lomp Cell2Fire.cpp
endif
endif

SpottingFBP.o: SpottingFBP.cpp SpottingFBP.h CellsFBP.h
	$(CC) -c $(CFLAGS) SpottingFBP.cpp CellsFBP.h

CellsFBP.o: CellsFBP.cpp CellsFBP.h FBPfunc5_NoDebug.o
	$(CC) -c $(CFLAGS) CellsFBP.cpp

FBPfunc5_NoDebug.o: FBPfunc5_NoDebug.c FBP5.0.h
	$(CC) -c $(CFLAGS) FBPfunc5_NoDebug.c

ReadCSV.o: ReadCSV.cpp ReadCSV.h FBPfunc5_NoDebug.o
	$(CC) -c $(CFLAGS) ReadCSV.cpp

READARGS = ReadArgs
ifneq ($(MODE), Serial)
	READARGS = $(PARALLEL_DIR)/ReadArgs
endif

ReadArgs.o: $(READARGS).cpp $(READARGS).h
	$(CC) -c $(CFLAGS) $(READARGS).cpp

Lightning.o: Lightning.cpp Lightning.h
	$(CC) -c $(CFLAGS) Lightning.cpp

Forest.o: Forest.cpp Forest.h
	$(CC) -c $(CFLAGS) Forest.cpp

WriteCSV.o: WriteCSV.cpp WriteCSV.h
	$(CC) -c $(CFLAGS) WriteCSV.cpp

Ellipse.o: Ellipse.cpp Ellipse.h 
	$(CC) -c $(LIBS) $(CFLAGS) Ellipse.cpp 


clean:
	rm Lightning.o ReadArgs.o ReadCSV.o FBPfunc5_NoDebug.o Cell2Fire.o CellsFBP.o Cell2Fire SpottingFBP.o Forest.o WriteCSV.o Ellipse.o *.gch
