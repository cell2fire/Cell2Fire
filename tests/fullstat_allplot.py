"""
Before you run this, run:

python main.py --input-instance-folder ../data/dogrib/ --output-folder ../results/dogrib_n100cv05 --ignitions --sim-years 1 --nsims 3 --grids --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.5 --seed 123 --IgnitionRad 0 --stats --allPlots

That will create the input files. Then we run basically the same command under the tester, but
with --onlyProcessing to avoid calling the compiled C++ code.
# TBD: this test module should take the command line as an arg, so it does not have to
#      be pasted into the github action yml file and here. It should just be in the action
#      yml file and read here, with --onlyProcessing appended here.

"""
import unittest
import os.path
import datetime
from cell2fire.utils.ParseInputs import make_parser
from cell2fire.Cell2FireC_class import *
import cell2fire  # for path finding
import pandas as pd


p = str(cell2fire.__path__)
l = p.find("'")
r = p.find("'", l+1)
cell2fire_path = p[l+1:r]
data_path = os.path.join(cell2fire_path, "..","data")

def _readme_list():
    datadir = os.path.abspath(os.path.join(data_path, "dogrib"))
    resultsdir = os.path.abspath(os.path.join("..", "results", "dogrib_n100cv05"))
    baselist = ["--input-instance-folder", datadir,
                "--output-folder", resultsdir,
                "--ignitions",
                "--sim-years", "1",
                "--nsims",  "3",
                "--grids",
                "--finalGrid",
                "--weather", "rows",
                "--nweathers", "1",
                "--Fire-Period-Length", "1.0",
                "--output-messages",
                "--ROS-CV", "0.5",
                "--seed", "123",
                "--IgnitionRad", "0",
                "--stats",
                "--allPlots",
                ]
    return baselist


class TestMain(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

    def test_readme_cmd(self):
        print("Running ", str(self.id()).split('.')[2])
        parser = make_parser()
        cmdlist = _readme_list()
        cmdlist.append("--onlyProcessing")
        # only-processing means something else has to make the data!!! (no call to C++)

        args = parser.parse_args(cmdlist)
        env = Cell2FireC(args)  # see main.py
        env.stats()

        csv_path = os.path.join(data_path, "..", "results", "dogrib_n100cv05", "Stats", "HourlySummaryAVG.csv")
        df = pd.read_csv(csv_path)
        self.assertAlmostEqual(df['AVGNonBurned'][6], 78091.0), "TEST ERROR"
        self.assertAlmostEqual(df['AVGNonBurned'][7], 77533.333), "TEST ERROR"


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
