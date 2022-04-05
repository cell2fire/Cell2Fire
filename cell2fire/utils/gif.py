import glob
from PIL import Image
import sys
import os
 
 
# filepaths
#print("test2")
#print(sys.argv[1],sys.argv[2])

if len(sys.argv) != 3:
   print("location of pictures is needed, type the commandline in the form of: python -m cell2fire.utils.gif.py 'locationpath' 'outputpath'")
   quit()
	
imageInput = sys.argv[1]+"/Fire??.png"
#print('test')
#print(imageInput)
if not os.path.exists(sys.argv[1]):
    print("the input path does not exist.")
    quit()
if not os.path.isdir(sys.argv[1]):
    print("the input location of png files'location should be a directory")
    quit()
if os.path.isfile(imageInput):
    print(f"the input location of png files'location is a file, ought to be a directory: {imageInput}")
    quit()

# filepaths
#imageInput = "sys.argv[1]/Fire??.png"
gifOutput = sys.argv[2]
#print(gifOutput)
#if not os.path.exists(sys.argv[2]):
 #   print("the input location of gif path does not exist.")
  #  quit()
#if not os.path.isdir(sys.argv[2]):
 #  print('the input location of gif should be a directory')
  # quit()
#if os.path.isfile(gifOutput):
 #  print(f"the input location of gif is a file, ought to be a directory: {gifOutput}")
  # quit()


# https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif

img, *imgs = [Image.open(f) for f in sorted(glob.glob(imageInput))]
img.save(fp=gifOutput, format='GIF', append_images=imgs,
         save_all=True, duration=200, loop=0)
print(f"gif saved to {gifOutput}")
         
         
