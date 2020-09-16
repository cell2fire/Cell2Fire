# coding: utf-8
__version__ = "1.0"
__author__ = "Cristobal Pais"

# Importations
#from tqdm import tqdm

# No Warnings
import warnings
warnings.filterwarnings("ignore")
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
import sys
sys.path.append(dir_path+'/..')
	
# Inputs and environment generator
from cell2fire.utils.ParseInputs import ParseInputs
#from Cell2Fire.ParseInputs import ParseInputs
from cell2fire.Cell2FireC_class import *
from cell2fire.utils.Stats import *
print("here")
def main():
    # Parse inputs (args)
    args = ParseInputs()
    print("part1")
    # C++ init and run
    env = Cell2FireC(args)
    print("part2")
    # Postprocessing: Plots Stats
    if args.stats:
        print("------ Generating Statistics --------")
        env.stats()

if __name__ == "__main__":
    main()    
