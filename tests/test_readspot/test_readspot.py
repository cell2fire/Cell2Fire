import  unittest
import os.path
import datetime
from cell2fire.utils.ParseInputs import make_parser
from cell2fire.utils.ReadDataPrometheus import ReadSpotting
from cell2fire.Cell2FireC_class import *


class TestMain(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

    def test_readme_cmd(self):
        filename = "spot_file_complex.json"
        nonoutput = False

        try:    
            SpottingParams = ReadSpotting(filename, nonoutput)
        except:
            print("Bug occur")

        # TBD: add an assert

if __name__ == "__main__":

    """
    # first: full run to create data files for testing  
    Unfortunately, we can run't under os.system because the call to compiled code fails....
    cmdstr = "python main.py "
    for es in _readme_list():
        cmdstr += es+' '
    print("cmdstr=",cmdstr)
    os.system(cmdstr)
    """
    # something else needs to create the files
    # second: do the tests
    unittest.main()
 
