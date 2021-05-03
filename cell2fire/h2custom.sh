#!/bin/bash
python main.py --input-instance-folder ../data/Sub20x20/ --output-folder ../results/Sub20x20/Sub20_RW_RI_N10 --sim-years 2 --nsims 10 --finalGrid --weather random --nweathers 100 --Fire-Period-Length 1.0 --ROS-CV 0.0 --seed 123 --IgnitionRad 0 --stats --output-messages --ROS-Threshold 0 --HFI-Threshold 0 --heuristic 2 --customValue="../data/Sub40x40/values40x40.csv"
