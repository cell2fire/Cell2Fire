#ifndef SPOTTINGFBP
#define SPOTTINGFBP

#include "CellsFBP.h" 

// Include libraries
#include <stdio.h>
#include <string>
#include <vector>
#include <math.h>
#include <cmath>
#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <string>

using namespace std;

std::vector<int> SpottingFBP(std::unordered_map<int, CellsFBP> & Cells_Obj, 
											std::vector<std::vector<int>> & coordCells, 
											std::unordered_set<int> & AvailSet, double WSD, double WSC, 
											std::unordered_map<std::string, double> spottingParams, bool verbose);

#endif
