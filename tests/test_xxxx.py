# demonstrate how to write a test
import pyutilib.th as unittest
import os.path
import datetime
from Cell2Fire.Cell2Fire.ParseInputs import make_parser
import Cell2Fire
from Cell2Fire.Cell2FireC import *
p = str(Cell2Fire.__path__)
l = p.find("'")
r = p.find("'", l+1)
cell2fire_path = p[l+1:r]
data_path = os.path.join(cell2fire_path, "..", "..","data")


class TestMain(unittest.TestCase):

    def _readme_list(self):
        # arguments list that matches the readme
        datadir = os.path.join(data_path, "Sub40x40")
        baselist = ["--input-instance-folder", datadir,
                    "--output-folder", " .",
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

if __name__ == "__main__":
    unittest.main()