import os
import signal
import subprocess
import sys

execArray=['/mnt/c/Users/Lenovo/Documents/GitHub/Cell2Fire/src/C++b/Cell2Fire', 
'--input-instance-folder', '/mnt/c/Users/Lenovo/Documents/GitHub/Cell2Fire/data/9cells/',
'--output-folder', '/mnt/c/Users/Lenovo/Desktop/9cellsCfromPy/',
'--ignitions',
'--sim-years', '1',
'--nsims', '10',
'--grids', '--final-grid',
'--Fire-Period-Length', '1.0',
'--output-messages',
'--weather', 'random',
'--nweathers', '2']

with open('/mnt/c/Users/Lenovo/Desktop/9cells_April15_FastfromPY.txt', 'w') as output:
    proc = subprocess.Popen(execArray, stdout=output)
    proc.communicate()
proc.wait()
print("Simulator finished...")