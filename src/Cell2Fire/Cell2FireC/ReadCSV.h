#ifndef READCSV
#define READCSV

#include "FBP5.0.h"

#include <iostream>
#include <fstream>
#include <vector>
#include <iterator>
#include <string>
#include <algorithm>
#include <boost/algorithm/string.hpp>
#include <unordered_map>
#include <unordered_set>

 
/*
*   Weather structure
*/
typedef struct
   { std::string scenario, datetime;
      float apcp, tmp, rh, ws, ffmc, dmc, dc, isi, bui, fwi;
      int waz;
   } weatherDF;
   
 /*
*   Forest structure
*/
typedef struct
   { int cellside, rows, cols; 
      std::vector<std::unordered_map<std::string, int>> adjCells;
	  std::vector<std::vector<int>> coordCells;
   } forestDF;

 
/*
 * A class to read data from a csv file.
 */
class CSVReader{ 
public:
	// inmutable 
	std::string fileName;
	std::string delimeter;
	
	// Constructor
	CSVReader(std::string filename, std::string delm = ",");
 
	// Function to fetch data from a CSV File
	std::vector<std::vector<std::string>> getData();
	
	//Print data to console (Debug)
	void printData(std::vector<std::vector<std::string>> & DF);
	
	//Populate DF 
	void parseDF(inputs * df_ptr, std::vector<std::vector<std::string>> & DF, int NCells);
	
	// Populate NFtypes
	void parseNDF(std::vector<int> & NFTypes, std::vector<std::vector<std::string>> & DF, int NCells);
	
	//Populate Weather DF
	void parseWeatherDF(weatherDF * wt_ptr, std::vector<std::vector<std::string>> & DF, int WPeriods);
	
	// Populate Ignition Points
	void parseIgnitionDF(std::vector<int> & ig, std::vector<std::vector<std::string>> & DF, int IgPeriods);
	
	// Populates ForestDF
	void parseForestDF(forestDF * frt_ptr, std::vector<std::vector<std::string>> & DF);
	
	// Populate Harvested Cells 
	void parseHarvestedDF(std::unordered_map<int, std::vector<int>> & hc, std::vector<std::vector<std::string>> & DF, int HPeriods);
	
	// Populate BBO Factors
	void parseBBODF(std::unordered_map<int, std::vector<float>> & bbo, std::vector<std::vector<std::string>> & DF, int NFTypes);
	
	// Prints individual cell info
	void printDF(inputs df);
	
	// Prints individual weather row info
	void printWeatherDF(weatherDF wdf);
};
 
#endif
