# demonstrate how to write a test
import pyutilib.th as unittest
import os.path
import datetime
from Cell2Fire.ParseInputs import make_parser
from Cell2FireC_class import *
import Cell2Fire
p = str(Cell2Fire.__path__)
l = p.find("'")
r = p.find("'", l+1)
cell2fire_path = p[l+1:r]
data_path = os.path.join(cell2fire_path, "..", "..","..","data")


class TestMain(unittest.TestCase):

    def _readme_list(self):
        # arguments list that matches the readme
        #python main.py --input-instance-folder ../../data/Sub40x40/ --output-folder ../../results/Sub40x40 --ignitions --sim-years 1 --nsims 5 --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.0 --seed 123 --stats --allPlots --IgnitionRad 5 --grids --combine
        datadir = os.path.join(data_path, "Sub40x40")
        resultsdir = os.path.join(data_path, "..", "results", "Sub40x40")
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

    @classmethod
    def setUpClass(self):
        pass

    def test_readme_cmd(self):
        print("Running ", str(self.id()).split('.')[2])
        parser = make_parser()
        args = parser.parse_args(self._readme_list())
        env = Cell2FireC(args)  # see main.py
        env.stats()

if __name__ == "__main__":
    unittest.main()
