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

def _readme_list_nweather_1():
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

def _readme_list_nweather_2():
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

    def test_readme_cmd1(self):
        print("Running ", str(self.id()).split('.')[2])
        parser = make_parser()
        cmdlist = _readme_list_nweather_1()
        cmdlist.append("--onlyProcessing")
        # only-processing means something else has to make the data!!! (no call to C++)

        args = parser.parse_args(cmdlist)
        env = Cell2FireC(args)  # see main.py
        env.stats()

        csv_path = os.path.join(data_path, "..", "results", "Sub40x40", "Stats", "HourlySummaryAVG.csv")
        df = pd.read_csv(csv_path)
        self.assertAlmostEqual(df['AVGNonBurned'][6], 1264.6, 0), "TEST ERROR"
        self.assertAlmostEqual(df['AVGNonBurned'][7], 1192.8, 0), "TEST ERROR"

    def test_readme_cmd2(self):
        print("Running ", str(self.id()).split('.')[2])
        parser = make_parser()
        cmdlist = _readme_list_nweather_2()
        cmdlist.append("--onlyProcessing")
        # only-processing means something else has to make the data!!! (no call to C++)

        args = parser.parse_args(cmdlist)
        env = Cell2FireC(args)  # see main.py
        env.stats()

        csv_path = os.path.join(data_path, "..", "results", "Sub40x40", "Stats", "HourlySummaryAVG.csv")
        df = pd.read_csv(csv_path)
        self.assertAlmostEqual(df['AVGNonBurned'][6], 1306.0, 0), "TEST ERROR"
        self.assertAlmostEqual(df['AVGNonBurned'][7], 1242.8, 0), "TEST ERROR"

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