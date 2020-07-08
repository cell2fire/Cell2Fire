import  unittest
import os.path
import datetime
import warnings
warnings.filterwarnings("ignore")
from cell2fire.utils.ParseInputs import ParseInputs
import cell2fire.utils.DataGeneratorC as DataGenerator
from cell2fire.utils.ParseInputs import make_parser
from cell2fire.Cell2FireC_class import *
from cell2fire.utils.Stats import *


class TestMain(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

    def test_readme_cmd(self):
        baselist = ["--input-instance-folder", "../data/Sub40x40/",
            "--output-folder", "../results/Sub40x40",
            "--ignitions",
            "--sim-years", "1",
            "--nsims",  "5",
            "--finalGrid",
            "--weather", "rows",
            "--nweathers", "1",
            "--Fire-Period-Length", "1.0",
            "--output-messages",
            "--ROS-CV", "0.0",
            "--seed", "123",
            "--stats",
            "--allPlots",
            "--IgnitionRad", "5",
            "--grids",
            "--combine"]
        parser = make_parser()
        args = parser.parse_args(baselist)
        env = Cell2FireC(args)
        env.stats()
        # Postprocessing: Plots Stats
        if args.stats:
            print("------ Generating Statistics --------")
            env.stats()

        DataGenerator.GenDataFile(env.args.InFolder)
    

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
 
