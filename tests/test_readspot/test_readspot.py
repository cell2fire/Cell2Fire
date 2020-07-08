import  unittest
import os.path
import datetime
from cell2fire.utils.ReadDataPrometheus import ReadData
filename = "spot_file_complex.json"
nonoutput = False

if __name__ == "__main__":
    try:    
        SpottingParams = ReadData.ReadSpotting(filename, nonoutput)
    except:
        print("Bug occur")
