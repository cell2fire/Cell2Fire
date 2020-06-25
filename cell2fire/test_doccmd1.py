# demonstrate how to hack together a test
"""
Before you run this, run
python main.py --input-instance-folder ../../data/Sub40x40/ --output-folder ../../results/Sub40x40 --ignitions --sim-years 1 --nsims 5 --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.0 --seed 123 --stats --allPlots --IgnitionRad 5 --grids --combine

That will create the input files. Then we run basically the same command under the tester, but
with --onlyProcessing to avoid calling the compiled C++ code.

# TBD: this test module should take the command line as an arg, so it does not have to
#      be pasted into the github action yml file and here. It should just be in the action
#      yml file and read here, with --onlyProcessing appended here.

"""
import  unittest
import os.path
import datetime
from cell2fire.utils.ParseInputs import make_parser
from cell2fire.Cell2FireC_class import *
import cell2fire  # for path finding
p = str(cell2fire.__path__)
l = p.find("'")
r = p.find("'", l+1)
cell2fire_path = p[l+1:r]
data_path = os.path.join(cell2fire_path, "..","data")

def _readme_list():
    # arguments list that matches the first example in the readme file
    #python main.py --input-instance-folder ../../data/Sub40x40/ --output-folder ../../results/Sub40x40 --ignitions --sim-years 1 --nsims 5 --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.0 --seed 123 --stats --allPlots --IgnitionRad 5 --grids --combine
    datadir = os.path.abspath(os.path.join(data_path, "Sub40x40"))
    resultsdir = os.path.abspath(os.path.join(data_path, "..", "results", "Sub40x40"))
    baselist = ["--input-instance-folder", datadir,
                "--output-folder", resultsdir,
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
