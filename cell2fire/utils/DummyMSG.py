import re
import glob
import os
import numpy as np
from argparse import ArgumentParser

def DummyMessages(OutFolder):
	os.chdir(OutFolder + 'Messages')
	MessagesFiles = glob.glob('*')
	existingIDs = [int(re.match('MessagesFile(\d+)', MessagesFiles[i]).groups()[0]) for i in range(0, len(MessagesFiles))]
	for i in range(1, np.max(existingIDs)):
		if i not in existingIDs:
			np.savetxt(os.path.join(os.getcwd(), "MessagesFile" + str(i) + ".csv"), np.asarray([]))
			
if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument("--input-instance-folder",
							help="The path to the folder contains all the files for the simulation",
							dest="input_folder",
							type=str,
							default=None)                
	args = parser.parse_args()
	DummyMessages(args.input_folder)
