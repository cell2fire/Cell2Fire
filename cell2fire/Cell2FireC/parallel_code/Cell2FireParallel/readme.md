### Readme
Cell2Fire parallel version modified files. It requires OpenMP:
- MACOSX: brew install libomp
- UBUNTU: sudo apt install libomp-dev


#### C++
- Cell2Fire.cpp: Parallel version ready of Cell2Fire. New argument --nthreads INT indicates the total number of threads used for parallel replications
- Cell2Fire.h: Modified to include new function arguments to avoid threads collisions (e.g., avoiding saving the grid files with the same name)
- ReadArgs.cpp: Added nthreads 
- ReadArgs.h: Added nthreads
- Makefile_MACOSX: Added specific compiler instructions to compile Cell2Fire Parallel version in MACOSX. 
- Makefile_UBUNTU: Added specific compiler instructions to compile Cell2Fire Parallel version in UBUNTU. 

#### Python
- Cell2FireC_class.py: Added args.nthreads as part of the inputs when calling the C++ code
- ParseInputs.py: nthreads was already part of the existing arguments, but included as a reference. 