#ifndef CELL2FIRE
#define CELL2FIRE

// Headers
#include "CellsFBP.h"
#include "SpottingFBP.h"
#include "FBP5.0.h"
#include "ReadCSV.h"
#include "WriteCSV.h"
#include "ReadArgs.h"
#include "Lightning.h"

// Include libraries
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <vector>
#include <math.h>
#include <cmath>
#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <string>
#include <string.h>
#include <random>
#include <algorithm> 

using namespace std;

class Cell2Fire {
	// DFs 
	private:
		CSVReader CSVWeather;
		CSVReader CSVForest;
			
    public: 
		 // Main inputs
		 arguments args;
		 arguments* args_ptr;
		 fuel_coefs* coef_ptr;
		 fuel_coefs coefs[18];	
		 
		 // Integers
		 int sim;
		 int rows;
		 int cols;
		 int weatherPeriod = 0;
		 int year = 1;
		 int gridNumber = 0;
		 int weatherperiod = 0;
		 long int nCells;
		 int nIgnitions = 0;
		 
		 // Booleans
		 bool noIgnition = true;  		//  None = -1
		 bool messagesSent = false;
		 bool repeatFire = false;
		 bool done = false;
		 bool noMessages = false;
		 
		 // Doubles
		 double cellSide;
		 double areaCells;
		 double perimeterCells;
		 double ROSRV;
			
		// Strings	
		 string gridFolder;
		 string messagesFolder;
	
		 // Vectors
		 std::vector<int> fire_period;
		 std::vector<std::vector<int>> coordCells;
		 std::vector<std::unordered_map<std::string, int>> adjCells;
		 std::vector<std::vector<std::string>> DF;
		 std::vector<int> statusCells; //(long int, int);
		 std::vector<int> fTypeCells; // (long int&, int); 
		 std::vector<string> fTypeCells2; // (long int&, const char [9]);
		 std::vector<std::vector<std::string>> WeatherDF;
		 std::vector<int> IgnitionPoints;
		 vector<int> burnedOutList;
		 std::vector<double> FSCell;
		 //std::vector<unordered_set<int>> IgnitionSets;
		 std::vector<std::vector<int>> IgnitionSets;
		 
		 // Sets
		 std::unordered_set<int> availCells;				
		 std::unordered_set<int> nonBurnableCells; 	
		 std::unordered_set<int> burningCells;
		 std::unordered_set<int> burntCells;
		 std::unordered_set<int> harvestCells;
		 
		 // Cells Dictionary
		 std::unordered_map<int, CellsFBP> Cells_Obj;
		 
		 // Constructor
        Cell2Fire(arguments args);
		
		// Methods
		void InitCell(int id);
        void reset(int rnumber, double rnumber2, int simExt);
		bool RunIgnition(std::default_random_engine generator, int rnumber3);
		std::unordered_map<int, std::vector<int>> SendMessages();
		void GetMessages(std::unordered_map<int, std::vector<int>> sendMessageList);
		void Results();
		void outputGrid();
		void updateWeather();
		void Step(std::default_random_engine generator, int rnumber, double rnumber2, int rnumber3);
		void InitHarvested();
		
		// Utils
		std::vector<float> getROSMatrix();
		std::vector<float> getFireProgressMatrix();
};

#endif
