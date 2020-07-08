import  unittest
import os.path
import datetime
from cell2fire.utils.ReadDataPrometheus import ReadDataPrometheus
filename = "spot_file_complex.json"
nonoutput = False

if __name__ == "__main__":
    try:    
        SpottingParams = ReadDataPrometheus.ReadSpotting(filename, nonoutput)
    except:
        print("Bug occur")
