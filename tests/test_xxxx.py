# demonstrate how to write a test
import pyutilib.th as unittest
import os.path
import datetime
import mape_maker
import Cell2Fire
from Cell2Fire import main
p = str(Cell2Fire.__path__)
l = p.find("'")
r = p.find("'", l+1)
cell2fire_path = p[l+1:r]
data_path = os.path.join(cell2fire_path, "..", "..","data")


class TestMain(unittest.TestCase):


    def _readme_list(self):
        # arguments list that matches the readme
        datadir = os.join(data_path, "Sub40x40")
        baselist = ["--input-instance-folder {}".format(datadir),
                    "--output-folder .",
                    "--ignitions",
                    "--sim-years 1",
                    "--nsims 5",
                    "--finalGrid",
                    "--weather rows",
                    "--nweathers 1",
                    "--Fire-Period-Length 1.0",
                    "--output-messages",
                    "--ROS-CV 0.0",
                    "--seed 123",
                    "--stats",
                    "--allPlots",
                    "--IgnitionRad 5",
                    "--grids",
                    "--combine"]
        return baselist

    @classmethod
    def setUpClass(self):
        pass

    def test_readme_cmd(self):
        print("Running ", str(self.id()).split('.')[2])


if __name__ == "__main__":
    unittest.main()
