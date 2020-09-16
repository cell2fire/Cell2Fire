# test_dogrib
"""
Before you run this, run

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
import os
from PIL import Image, ImageChops
import collections


p = str(cell2fire.__path__)
l = p.find("'")
r = p.find("'", l+1)
cell2fire_path = p[l+1:r]
data_path = os.path.join(cell2fire_path, "..","data")

# Those files are checked in the test
result_Forest01 = os.path.join(cell2fire_path, "..", "results", "harvested40x40_Illustrations_1", "Grids", "Grids1", "ForestGrid01.csv")
baseline_Forest01 = os.path.join(cell2fire_path, "..", "tests", "baseline", "harvested40x40_Illustrations_1", "ForestGrid01.csv")
result_Fire01 = os.path.join(cell2fire_path, "..", "results", "harvested40x40_Illustrations_1", "Plots", "Plots1", "Fire01.png")
baseline_Fire01 = os.path.join(cell2fire_path, "..", "tests", "baseline", "harvested40x40_Illustrations_1", "Fire01.png")
result_Propagation = os.path.join(cell2fire_path, "..", "results", "harvested40x40_Illustrations_1","Plots", "Plots1", "PropagationTree1.png")
baseline_Propagation = os.path.join(cell2fire_path, "..", "tests", "baseline", "harvested40x40_Illustrations_1", "PropagationTree1.png")

def _cmd_list():
    datadir = os.path.abspath(os.path.join(data_path, "Harvest40x40"))
    resultsdir = os.path.abspath(os.path.join(data_path, "..", "results", "harvested40x40_Illustrations_1"))
    ### python3 main.py --input-instance-folder ../data/Harvest40x40/ --output-folder ../results/harvested40x40_Illustrations_1 --ignitions --sim-years 1 --nsims 5 --grids --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.8 --seed 123 --stats --allPlots --IgnitionRad 1 --grids --combine --heuristic 1 --GASelection --HarvestedCells ../data/Harvest40x40/harvestedCells.csv
    baselist = ["--input-instance-folder", datadir,
                "--output-folder", resultsdir,
                "--ignitions",
                "--sim-years", "1",
                "--nsims",  "5",
	"--grids",
                "--finalGrid",
                "--weather", "rows",
                "--nweathers", "1",
                "--Fire-Period-Length", "1.0",
                "--output-messages",
                "--ROS-CV", "0.8",
                "--seed", "123",
                "--stats",
                "--allPlots",
                "--IgnitionRad", "1",
                "--grids",
                "--combine",
	"--heuristic", "1",
	"--GASelection",
	"--HarvestedCells", "../data/Harvest40x40/harvestedCells.csv"]
    return baselist
    

class TestMain(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

    def test_readme_cmd(self):
        print("Running ", str(self.id()).split('.')[2])
        parser = make_parser()
        cmdlist = _cmd_list()
        cmdlist.append("--onlyProcessing")
        # only-processing means something else has to make the data!!! (no call to C++)

        args = parser.parse_args(cmdlist)
        env = Cell2FireC(args)  # see main.py
        env.stats()
        
        # Check if the result generated by the run matches the baseline files
        equal = True
        with open(result_Forest01) as result_file:
                with open(baseline_Forest01) as baseline_file:
                        for line1, line2 in zip(result_file, baseline_file):
                                                if not line1 == line2:
                                                        equal = False
                                                        print("In File Grids1/ForestGrid01.csv the result is wrong")

        imgfire1 = Image.open(result_Fire01)
        imgfire2 = Image.open(baseline_Fire01)
        imgprop1 = Image.open(result_Propagation)
        imgprop2 = Image.open(baseline_Propagation)
        diffFire = ImageChops.difference(imgfire1, imgfire2)
        diffProp = ImageChops.difference(imgprop1, imgprop2)
        if diffFire.getbbox():
                equal = False 
                print("The image Fire01.png doesn't match the baseline file")                                                
        
        if diffProp.getbbox():
                equal = False 
                print("The image PropagationTree1.png doesn't match the baseline file")  
        
        self.assertTrue(equal)

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