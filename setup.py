#!/bin/usr/env python3
import glob
import sys
import os

# We raise an error if trying to install with python2
if sys.version[0] == '2':
    print("Error: This package must be installed with python3")
    sys.exit(1)

from setuptools import find_packages
from distutils.core import setup

packages = find_packages()

setup(name='Cell2Fire',
      version='0.2',
      description="Fire Simulator for Harvest and Fuel Management Planning",
      url='https://github.com/cell2Fire/Cell2Fire',
      author='Cristobal Pais, Jaime Carrasco, David Martell, David L. Woodruff, Andres Weintraub',
      author_email='dlwoodruff@ucdavis.edu',
      packages=packages,
      install_requires=['numpy', 'pandas', 'matplotlib', 'seaborn', 'tqdm', 'opencv-python', 'networkx', 'deap'],
      extras_require={
        'doc': [
            'sphinx_rtd_theme',
            'sphinx',
        ]
    },
      
)
# opencv or cv2?
