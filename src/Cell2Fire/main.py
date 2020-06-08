# coding: utf-8
__version__ = "1.0"
__author__ = "Cristobal Pais"

# Importations
#from tqdm import tqdm

# No Warnings
import warnings
warnings.filterwarnings("ignore")

# Inputs and environment generator
from Cell2Fire.ParseInputs import ParseInputs
#from Cell2Fire.ParseInputs import ParseInputs
from Cell2FireC import *
from Cell2Fire.Stats import *

def main():
    # Parse inputs (args)
    args = ParseInputs()

    # C++ init and run
    env = Cell2FireC(args)
    
    # Postprocessing: Plots Stats
    if args.stats:
        print("------ Generating Statistics --------")
        env.stats()

if __name__ == "__main__":
    main()    
