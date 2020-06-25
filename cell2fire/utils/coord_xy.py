# coding: utf-8
__version__ = "2.0"
__author__ = "Jaime Carrasco"
__maintainer__ = "Jaime Carrasco, Cristobal Pais, David Woodruff"
__status__ = "Alpha Operational"

import numpy as np

def coord_xy(i, m, n, cellsize):
	centro = np.array([1,1]) * cellsize/2
	q = i / n
	r = i % n
	if r == 0:
		return np.array([n - 1, m - q]) + centro
	else:
		return np.array([r - 1, m - q - 1]) + centro