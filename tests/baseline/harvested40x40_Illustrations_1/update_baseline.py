# test_dogrib
"""
Before you run this, run
python main.py --input-instance-folder ../data/dogrib/ --output-folder ../results/dogrib --ignitions --sim-years 1 --nsims 1 --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.0 --seed 123 --stats --allPlots --IgnitionRad 5 --grids --combine
Or any argument you want.
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
result_Forest01 = os.path.join(cell2fire_path, "..", "results", "dogrib", "Grids", "Grids1", "ForestGrid01.csv")
baseline_Forest01 = os.path.join(cell2fire_path, "..", "tests", "baseline", "dogrib", "ForestGrid01.csv")
result_Fire01 = os.path.join(cell2fire_path, "..", "results", "dogrib", "Plots", "Plots1", "Fire01.png")
baseline_Fire01 = os.path.join(cell2fire_path, "..", "tests", "baseline", "dogrib", "Fire01.png")
result_Propagation = os.path.join(cell2fire_path, "..", "results", "dogrib", "Plots", "Plots1", "PropagationTree1.png")
baseline_Propagation = os.path.join(cell2fire_path, "..", "tests", "baseline", "dogrib", "PropagationTree1.png")

def copy_and_overwrite():
	
	shutil.move(result_Forest01, baseline_Forest01)
	shutil.move(result_Fire01, baseline_Fire01)
	shutil.move(result_Propagation, baseline_Propagation)

if __name__ == "__main__":
	copy_and_overwrite()
