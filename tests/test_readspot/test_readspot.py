import  unittest
import os.path
import datetime
from cell2fire.utils.ParseInputs import make_parser
from cell2fire.utils.ReadDataPrometheus import ReadSpotting
filename = "spot_file_complex.json"
nonoutput = False

if __name__ == "__main__":
    try:    
        SpottingParams = ReadSpotting(filename, nonoutput)
    except:
        print("Bug occur")
