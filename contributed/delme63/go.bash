#!/bin/bash
# run from main dir Cell2Fire/src/Cell2Fire for now
# bash ../../contributed/delme63/go.bash for now 
mydir=../../contributed/delme63
python main.py --input-instance-folder $mydir/9cellsC1/ --output-folder $mydir/results --ignitions --sim-years 1 --nsims 1 --finalGrid --weather rows --nweathers 1 --Fire-Period-Length 1.0 --output-messages --ROS-CV 0.0 --seed 1134 --stats --allPlots --IgnitionRad 0 --grids --combine --verbose
