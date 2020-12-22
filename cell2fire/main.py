# coding: utf-8
__version__ = "1.0"
__author__ = "Cristobal Pais"

# Importations
#from tqdm import tqdm

# No Warnings
import warnings
warnings.filterwarnings("ignore")

# Inputs and environment generator
from utils.ParseInputs import ParseInputs
from Cell2FireC_class import *
from utils.Stats import *
from utils.Heuristics import *

def main():
    # Parse inputs (args)
    args = ParseInputs()

    # C++ init and run
    env = Cell2FireC(args)
    
    # Postprocessing: Plots Stats
    if args.stats:
        print("------ Generating Statistics --------")
        env.stats()
        
    if args.heuristic != -1:
        print("------ Generating outputs for heuristics --------")
        env.heur() 

if __name__ == "__main__":
    main()    