# test sub20x20
"""
Before you run this, run
python main.py --input-instance-folder ../data/Sub20x20/ --output-folder ../results/Sub20x20 --ignitions --sim-years 1 --nsims 5 --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.0 --seed 123 --stats --allPlots --IgnitionRad 5 --grids --combine

This will create the output files that we will update as the new baseline
"""

import os.path
import datetime
import cell2fire  # for path finding
import shutil


p = str(cell2fire.__path__)
l = p.find("'")
r = p.find("'", l+1)
cell2fire_path = p[l+1:r]
result_path = os.path.join(cell2fire_path, "..", "results", "Sub20x20", "Grids", "Grids1", "ForestGrid08.csv")
baseline_path = os.path.join(cell2fire_path, "..", "tests", "baseline", "Sub20x20", "ForestGrid08.csv")


def copy_and_overwrite():
	
	shutil.move(result_path, baseline_path)

if __name__ == "__main__":
	copy_and_overwrite()
	
