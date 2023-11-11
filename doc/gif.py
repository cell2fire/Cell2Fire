import glob
from PIL import Image

# filepaths
imageInput = "/Users/vaibhav/Documents/Cell2Fire_latest/Cell2Fire/contributed/16cell/results/Plots/Plots1/Fire??.png"
gifOutput = "/Users/vaibhav/Documents/Cell2Fire_latest/Cell2Fire/contributed/16cell/results/Plots/gen_output.gif"

# https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
img, *imgs = [Image.open(f) for f in sorted(glob.glob(imageInput))]
img.save(fp=gifOutput, format='GIF', append_images=imgs,
         save_all=True, duration=200, loop=0)