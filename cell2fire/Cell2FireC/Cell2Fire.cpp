/* coding: utf-8
__version__ = "2.0"
__author__ = "Cristobal Pais"
__maintainer__ = "Jaime Carrasco, Cristobal Pais, David Woodruff"
*/

// Include classes
#include "Cell2Fire.h"
#include "CellsFBP.h"
#include "SpottingFBP.h"
#include "FBP5.0.h"
#include "ReadCSV.h"
#include "WriteCSV.h"
#include "ReadArgs.h"
#include "Lightning.h"

// Include libraries
#include <omp.h>
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
#include <chrono>

using namespace std;

// Global Variables (DFs with cells and weather info)
inputs * df_ptr;
weatherDF * wdf_ptr;
weatherDF wdf[150];
inputs df [1560000];
std::unordered_map<int, std::vector<float>> BBOFactors;
std::unordered_map<int, std::vector<int>> HarvestedCells;   
std::vector<int> NFTypesCells;

/******************************************************************************
																Utils
*******************************************************************************/
void printSets(std::unordered_set<int> availCells, std::unordered_set<int> nonBurnableCells, 	
					 std::unordered_set<int> burningCells, std::unordered_set<int> burntCells, std::unordered_set<int> harvestCells)
{
	std::cout << "\nSet information period" << std::endl;
	std::cout << "Available Cells:";
	for (auto & ac : availCells){
			std::cout << " " << ac;
	}
	std::cout << std::endl;
	
	std::cout << "nonBurnable Cells:";
	for (auto & nbc : nonBurnableCells){
			std::cout << " " << nbc;
	}
	std::cout << std::endl;
	
	std::cout << "Burning Cells:";
	for (auto & bc : burningCells){
			std::cout << " " << bc;
	}
	std::cout << std::endl;
	
	std::cout << "Burnt Cells:";
	for (auto & bc : burntCells){
			std::cout << " " << bc;
	}
	std::cout << std::endl;
	
	
	std::cout << "Harvested Cells:";
	for (auto & hc : harvestCells){
			std::cout << " " << hc;
	}
	std::cout << std::endl;
}

// Output grids
void CSVGrid(int rows, int cols, int gridNumber, std::string gridFolder, std::vector<int> & statusCellsCSV, bool verbose){
	std::string gridName;
	if (gridNumber < 10){
			gridName = gridFolder+ "ForestGrid0" + std::to_string(gridNumber) + ".csv";
	}
	
	else {
			gridName = gridFolder+ "ForestGrid" + std::to_string(gridNumber) + ".csv";
	}
	
	if(verbose){
		std::cout  << "We are plotting the current forest to a csv file " << gridName << std::endl;
	}
	CSVWriter CSVPloter(gridName, ",");
	CSVPloter.printCSV_V2(rows, cols, statusCellsCSV);
}


/******************************************************************************
															Constructor 
*******************************************************************************/
Cell2Fire::Cell2Fire(arguments _args) : CSVWeather(_args.InFolder + "Weather.csv", ","), 
														  CSVForest(_args.InFolder + "Forest.asc", " ")
														  {
	// Aux
	int i;
		
    // Populate arguments from command line into the Cell2Fire object
	this->args = _args;
	this->args_ptr = &this->args;
	
	/********************************************************************
	*
	*															Initialization steps
	*
	********************************************************************/
	//DEBUGstd::cout << "------------------ Simulator C++ Beta version ----------------------\n" << std::endl;
	/*
		      Command line arguments (all of them inside args structure)
	*/
	//DEBUGstd::cout << "------ Command line values ------\n";
	//DEBUGprintArgs(this->args);
	
	/********************************************************************
										Initialize fuel coefficients for FBP
	********************************************************************/
	// fuel_coefs coefs[18];	
	this->coef_ptr = &this->coefs[0];
	setup_const(this->coef_ptr);
	
	/********************************************************************
					Global Values (Forest) and Instance (in memory for the moment)
	********************************************************************/
	//DEBUGstd::cout << "\n------ Instance from file initialization ------\n";	
	this->sim = 1;
	/********************************************************************
											Read Instance from csv files...
	********************************************************************/
	// Create forest structure 
	forestDF frdf;
	//DEBUGstd::cout << "------------------Forest Data ----------------------\n" << std::endl;
	std::vector<std::vector<std::string>> FDF = this->CSVForest.getData();
	//DEBUGthis->CSVForest.printData(FDF);
	this->CSVForest.parseForestDF(&frdf, FDF);
		
	//DEBUGstd::cout << "------------------Detailed Data ----------------------\n" << std::endl;
	this->rows = frdf.rows;
	this->cols = frdf.cols;
	this->nCells = rows * cols; 
	this->cellSide = frdf.cellside;
	this->areaCells= cellSide * cellSide;
	this->perimeterCells = 4 * cellSide;
	
	this->coordCells = frdf.coordCells;
	this->adjCells = frdf.adjCells;
		
	/********************************************************************
							Dataframes initialization: Forest and Weather
	********************************************************************/
	//DEBUGstd::cout << "\n------ Read DataFrames: Forest and Weather ------\n";
	
	/* Forest DataFrame */
	std::string filename = this->args.InFolder + "Data.csv";
	std::string sep = ",";
	CSVReader CSVParser(filename, sep);
	
	// Populate DF 
	std::vector<std::vector<std::string>> DF = CSVParser.getData();
	std::cout << "Forest DataFrame from instance " << filename << std::endl;
	//DEBUGCSVParser.printData(DF);
	std::cout << "Number of cells: " <<  this->nCells  << std::endl;
	
	// Create empty df with size of NCells
	df_ptr = & df[0];
	
	// Populate the df [nCells] objects
	CSVParser.parseDF(df_ptr, DF, this->nCells);
	
	// Initialize and populate relevant vectors 
	this->fTypeCells = std::vector<int> (this->nCells, 1); 
	this->fTypeCells2 = std::vector<string> (this->nCells, "Burnable"); 
    this->statusCells = std::vector<int> (this->nCells, 0);
	
	// Non burnable types: populate relevant fields such as status and ftype
	std::string NoFuel = "NF ";
	std::string NoData = "ND ";
	std::string Empty = "";
	const char * NF = NoFuel.c_str();
	const char * ND = NoData.c_str();
	const char * EM = Empty.c_str();
	
	for(int l=0; l< this->nCells; l++){
		if (strcmp(df[l].fueltype,NF) == 0 || strcmp(df[l].fueltype, ND) == 0) {
			this->fTypeCells[l] = 0;
			this->fTypeCells2[l] = "NonBurnable";
			this->statusCells[l] = 4;
		}
	}
	
	// Harvested cells
	if(strcmp(this->args.HarvestPlan.c_str(), EM) != 0){
		std::string sep = ",";
		CSVReader CSVHPlan(this->args.HarvestPlan, sep);
						
		// Populate Ignitions vector 
		std::vector<std::vector<std::string>> HarvestedDF  = CSVHPlan.getData();
		//CSVHPlan.printData(HarvestedDF);
		
		// Cells
		int HCellsP = HarvestedDF.size() - 1;
		CSVHPlan.parseHarvestedDF(HarvestedCells, HarvestedDF, HCellsP);
		
		// Print-out
		std::cout << "\nTo Harvest Cells :" << std::endl;
		for (auto it = HarvestedCells.begin(); it != HarvestedCells.end(); it++ ){
			std::cout << " " << it->first << ": ";
				for (auto & it2 : it->second){
					std::cout << it2 <<  " ";
					this->fTypeCells[it2-1] = 0;
					this->fTypeCells2[it2-1] = "NonBurnable";
					this->statusCells[it2-1] = 3;
				}  
		}
		std::cout << std::endl;
	}
	
	// Relevant sets: Initialization
	this->availCells.clear();
	this->nonBurnableCells.clear();
	this->burningCells.clear();
	this->burntCells.clear();
	this->harvestCells.clear();
	for (i=0; i < this->statusCells.size(); i++){
		if(this->statusCells[i] < 3) this->availCells.insert (i+1);
		else if (this->statusCells[i] == 4)  this->nonBurnableCells.insert(i+1);
		else if (this->statusCells[i] == 3)  this->harvestCells.insert(i+1);
	}	
	
	/* Weather DataFrame */
	this->WeatherDF = this->CSVWeather.getData();
	std::cout << "\nWeather DataFrame from instance " << this->CSVWeather.fileName << std::endl;
	
	// Populate WDF 
	int WPeriods = WeatherDF.size() - 1;  // -1 due to header
	wdf_ptr = &wdf[0];
	
	// Populate the wdf objects
	this->CSVWeather.parseWeatherDF(wdf_ptr, this->WeatherDF, WPeriods);
	//DEBUGthis->CSVWeather.printData(this->WeatherDF);
	
	/*  Ignitions */
	int IgnitionYears;
	std::vector<int> IgnitionPoints;   
	
	if(this->args.Ignitions){
		//DEBUGstd::cout << "\nWe have specific ignition points:" << std::endl;
		
		/* Ignition points */
		std::string ignitionFile = args.InFolder + "Ignitions.csv";
		std::string sep = ",";
		CSVReader CSVIgnitions(ignitionFile, sep);
						
		// Populate Ignitions vector 
		std::vector<std::vector<std::string>> IgnitionsDF = CSVIgnitions.getData();
		//DEBUGstd::cout << "Ignition points from file " << ignitionFile << std::endl;
		//DEBUGCSVIgnitions.printData(IgnitionsDF);
		
		// Total Years
		IgnitionYears = IgnitionsDF.size() - 1;
		//DEBUGstd::cout << "Ignition Years: " << IgnitionYears  << std::endl;
		//DEBUGstd::cout << "Total Years: " << this->args.TotalYears  << std::endl;
		args.TotalYears = std::min(args.TotalYears, IgnitionYears);
		//DEBUGstd::cout << "Setting TotalYears to " << args.TotalYears << " for consistency with Ignitions file" << std::endl;
		
		// Ignition points 
		this->IgnitionPoints = std::vector<int>(IgnitionYears, 0);
		CSVIgnitions.parseIgnitionDF(this->IgnitionPoints, IgnitionsDF, IgnitionYears);
		//this->IgnitionSets = std::vector<unordered_set<int>>(this->IgnitionPoints.size());
		this->IgnitionSets = std::vector<std::vector<int>>(this->args.TotalYears);
		
		
		// Ignition radius
		if (this->args.IgnitionRadius > 0){
			// Aux
			int i, a, igVal;
			//std::unordered_set<int> auxSet;
			std::vector<int> auxSet;
			int auxIg = 0;

			// Debug
			//for (i=0; i<this->args.TotalYears; i++)
			//	std::cout << this->IgnitionPoints[i] <<	std::endl;
			
			// Loop
			for (i=0; i<this->args.TotalYears; i++){
				auxSet.clear();
				igVal = this->IgnitionPoints[i];
				
				if (this->args.IgnitionRadius == 1){
					for (auto & nb : adjCells[igVal-1]) {
						if (nb.second != -1) {
								//this->IgnitionSets[auxIg].insert(nb.second);
								this->IgnitionSets[auxIg].push_back(nb.second);
						}
					}
					//this->IgnitionSets[auxIg].insert(igVal);
					this->IgnitionSets[auxIg].push_back(igVal);
				}
				
				if (this->args.IgnitionRadius > 1){
					// Initial ignition set (first year for 1 degree)
					for (auto & nb : adjCells[igVal-1]) {
						if (nb.second != -1) {
								//this->IgnitionSets[auxIg].insert(nb.second);
								this->IgnitionSets[auxIg].push_back(nb.second);
						}
					}
					int auxR = 1;
					//auxSet.insert(igVal);
					auxSet.push_back(igVal);

					// loop over radius of adjacents
					while (auxR < args.IgnitionRadius){
						//unordered_set<int> IgnitionSetsAux = this->IgnitionSets[auxIg];
						std::vector<int> IgnitionSetsAux = this->IgnitionSets[auxIg];
						
						for (auto & c : IgnitionSetsAux) {
							// Populate Aux Set
							for (auto & na : adjCells[c - 1]) {
								if (na.second != -1) {
										//auxSet.insert(na.second);
										auxSet.push_back(na.second);
								}
							}
						}
						// Save aux set as Ignition Set
						this->IgnitionSets[auxIg] = auxSet;
						auxR += 1;
					}
				}
				// Next iteration (year)
				auxIg++;
			}
		}
		
		// Clean vectors 
		for (auto & v : this->IgnitionSets){
			std::sort(v.begin(), v.end());
			v.erase(std::unique(v.begin(), v.end()), v.end());
		}
		
		// IgRadius Information 
		if (this->args.verbose){
			for (auto & nb : this->IgnitionSets[0]){
				std::cout  << "Ignition sets[0] example:" <<  nb <<  std::endl;
			}
		}
	}
	
	/* BBO Tuning factors (only the ones present in the instances*/
	if(this->args.BBOTuning){
		// Get fuel types numbers
		CSVParser.parseNDF(NFTypesCells, DF, this->nCells);
		
		// BBO File
		std::string BBOFile = args.InFolder + "BBOFuels.csv";
		std::string sep = ",";
		CSVReader CSVBBO(BBOFile, sep);
		
		// Populate BBO vector 
		std::vector<std::vector<std::string>> BBODF = CSVBBO.getData();
		int BBONTypes = BBODF.size() - 1;
		CSVBBO.parseBBODF(BBOFactors, BBODF, BBONTypes);
		
		// Print-out
		std::cout << "BBO Factors:" << std::endl;
		for (auto it = BBOFactors.begin(); it != BBOFactors.end(); it++ ){
			std::cout << " " << it->first << ": ";
				for (auto & it2 : it->second){
					std::cout << it2 <<  " ";
				}  
		}
		std::cout << std::endl;
			
	}
	/********************************************************************
	*
	*											Global Parameters for loop 
	*
	*********************************************************************/
	// Global parameters for the loop
	this->year = 1;
	this->weatherPeriod = 0;
	this->noIgnition = true;  		//  None = -1
	this->gridNumber = 0;
	this->fire_period = vector<int>(this->args.TotalYears, 0);
	
	// Check maxFirePeriods and Weather File consistency
	if(this->args.WeatherOpt.compare("rows") == 0 || this->args.WeatherOpt.compare("random") == 0) {
		int maxFP = this->args.MinutesPerWP / this->args.FirePeriodLen * WPeriods;
		if (this->args.MaxFirePeriods > maxFP) {
			this->args.MaxFirePeriods = maxFP ;
            if (this->args.verbose){
				std::cout << "Maximum fire periods are set to: " << this->args.MaxFirePeriods << " based on the weather file, Fire Period Length, and Minutes per WP" << std::endl;
			}
         }
     }
}



/******************************************************************************
																Methods
*******************************************************************************/
// Init Cells
void Cell2Fire::InitCell(int id){
	// Declare an iterator to unordered_map
	std::unordered_map<int, CellsFBP>::iterator it2;
	
	// Initialize cell, insert it inside the unordered map
	CellsFBP Cell(id-1, this->areaCells,  this->coordCells[id-1],  this->fTypeCells[id-1],  this->fTypeCells2[id-1], 
						this->perimeterCells, this->statusCells[id-1], this->adjCells[id-1], id);
	this->Cells_Obj.insert(std::make_pair(id, Cell));							 
									
	// Get object from unordered map
	it2 = this->Cells_Obj.find(id);
	
	// Initialize the fire fields for the selected cel
	it2->second.initializeFireFields(this->coordCells, this->availCells);
	
	// Print info for debugging
	if (this->args.verbose) it2->second.print_info();
}


// Resets the instance/object
void Cell2Fire::reset(int rnumber, double rnumber2){
	// Reset info
	//DEBUGstd::cout  << "--------------------- Reseting environment -----------------------" << std::endl;
	
	// Aux
	int i;
	
	// Reset global parameters for the simulation
	this->year = 1;
	this->weatherPeriod = 0;
	this->noIgnition = true;  		//  None = -1
	this->nIgnitions = 0;
	this->gridNumber = 0;
	this->done = false;
	this->fire_period = vector<int>(this->args.TotalYears, 0);
	
	// Initial status grid folder
	if(this->args.OutputGrids){
		CSVWriter CSVFolder("","");
		this->gridFolder = "mkdir -p " + this->args.OutFolder + "/Grids/Grids" + std::to_string(this->sim);
		CSVFolder.MakeDir(this->gridFolder);
		this->gridFolder = this->args.OutFolder + "/Grids/Grids" + std::to_string(this->sim) + "/";
		//DEBUGstd::cout << "\nInitial Grid folder was generated in " << this->gridFolder << std::endl;
	}
	
	// Messages Folder
	if(this->args.OutMessages){
		CSVWriter CSVFolder("","");
		this->messagesFolder = "mkdir -p " + this->args.OutFolder + "/Messages/";
		CSVFolder.MakeDir(this->messagesFolder);
		this->messagesFolder = this->args.OutFolder + "/Messages/";
	}
		
	// Random Weather 
	/*std::cout << "Weather Option:" << this->args.WeatherOpt << std::endl;
	std::cout << "Weather Option random check:" << (this->args.WeatherOpt.compare("random") == 0) << std::endl;
	std::cout << "Weather Option rows check:" << (this->args.WeatherOpt.compare("rows") == 0) << std::endl;
	*/
	
	if(this->args.WeatherOpt.compare("random") == 0){
		// Random Weather 	
		CSVWeather.fileName = this->args.InFolder + "Weathers/Weather" + std::to_string(rnumber) + ".csv" ;
		std::cout  << "Weather file selected: " <<  CSVWeather.fileName  << std::endl;

		/* Weather DataFrame */
		this->WeatherDF = this->CSVWeather.getData();
		
		// Populate WDF 
		int WPeriods = this->WeatherDF.size() - 1;  // -1 due to header
		wdf_ptr = &wdf[0];
		
		// Populate the wdf objects
		this->CSVWeather.parseWeatherDF(wdf_ptr, this->WeatherDF, WPeriods);
	}
	
	// Random ROS-CV
	this->ROSRV = std::abs(rnumber2);
	//std::cout << "ROSRV: " << this->ROSRV << std::endl;
	
	// Cells dictionary
	this->Cells_Obj.clear(); 
	
	// Declare an iterator to unordered_map
	std::unordered_map<int, CellsFBP>::iterator it;
	   
	// Reset status 
	this->fTypeCells = std::vector<int> (this->nCells, 1); 
	this->fTypeCells2 = std::vector<string> (this->nCells, "Burnable"); 
	this->statusCells = std::vector<int> (this->nCells, 0);
	this->FSCell.clear();
	
	// Non burnable types: populate relevant fields such as status and ftype
	std::string NoFuel = "NF ";
	std::string NoData = "ND ";
	const char * NF = NoFuel.c_str();
	const char * ND = NoData.c_str();	
	
	for(i=0; i < this->nCells; i++){
		if (strcmp(df[i].fueltype, NF) == 0 || strcmp(df[i].fueltype, ND) == 0) {
			this->fTypeCells[i] = 0;
			this->fTypeCells2[i] = "NonBurnable";
			this->statusCells[i] = 4;
		}
	}
	   
	// Relevant sets: Initialization
	this->availCells.clear();
	this->nonBurnableCells.clear();
	this->burningCells.clear();
	this->burntCells.clear();
	this->harvestCells.clear();
	
	// Harvest Cells
	for (auto it = HarvestedCells.begin(); it != HarvestedCells.end(); it++ ){
		for (auto & it2 : it->second){
				this->fTypeCells[it2-1] = 0;
				this->fTypeCells2[it2-1] = "NonBurnable";
				this->statusCells[it2-1] = 3;
		}  
	}	
	
	for (i=0; i < this->statusCells.size(); i++){
		if(this->statusCells[i] < 3) this->availCells.insert (i+1);
		else if (this->statusCells[i] == 4)  this->nonBurnableCells.insert(i+1);
		else if (this->statusCells[i] == 3)  this->harvestCells.insert(i+1);
	}
	
	// Print-out sets information
	if (this->args.verbose){
		printSets(this->availCells, this->nonBurnableCells, this->burningCells, this->burntCells, this->harvestCells);
	}
}


//Ignition method (False then ignition)
bool Cell2Fire::RunIgnition(std::default_random_engine generator){
	if (this->args.verbose) {
		printf("\n----------------------------- Simulating Year %d -----------------------------\n", this->year);
		printf("---------------------- Step 1: Ignition ----------------------\n");
	}
	/*******************************************************************
	*
	*												Step 1: Ignition 
	*
	*******************************************************************/
	// Ignitions 
	int aux = 0;
	int loops = 0;
	this->noIgnition = false;
	std::unordered_map<int, CellsFBP>::iterator it;
	std::uniform_int_distribution<int> distribution(1, this->nCells);
	
	// No Ignitions provided
	if (this->args.Ignitions == 0) { 
		while (true) {
			// Pick any cell (uniform distribution [a,b])
			aux = distribution(generator);
			
			// Check information (Debugging)
			if (this->args.verbose){
				std::cout << "aux: " << aux << std::endl;
			}
			
			// If cell is available and not initialized, initialize it 
			if (this->statusCells[aux - 1] < 3 && this->burntCells.find(aux) == this->burntCells.end()) {
				if (this->Cells_Obj.find(aux) == this->Cells_Obj.end()) {
					InitCell(aux);
					it = this->Cells_Obj.find(aux);
				}
				
				if (it->second.getStatus() == "Available" && it->second.fType != 0) {
					std::cout << "\nSelected (Random) ignition point for Year " << this->year <<  ", sim " <<  this->sim << ": "<< aux;
					std::vector<int> ignPts = {aux};
					if (it->second.ignition(this->fire_period[year - 1], this->year, ignPts, & df[aux - 1], this->coef_ptr, this->args_ptr, & wdf[this->weatherPeriod])) {
															
						//Printing info about ignitions        
						if (this->args.verbose){
							std::cout << "Cell " <<  it->second.realId <<  " Ignites" << std::endl;
							std::cout << "Cell " <<  it->second.realId << " Status: "<< it->second.getStatus() << std::endl;
						}
						
						// Status 
						this->statusCells[it->second.realId - 1] = 1;
						
						// Plotter placeholder
						if (this->args.OutputGrids){
							this->outputGrid();
						}
						
						break;  
					}
				}
			}
			
			loops++;
			if (loops > this->nCells * 100) {
				this->noIgnition = true;
				break;
			}
			

		}
	} 

	// Ignitions with provided points from CSV
	else {
		int temp = IgnitionPoints[this->year-1];
		
		// If ignition Radius != 0, sample from the Radius set
		if (this->args.IgnitionRadius > 0){
			// Pick any at random and set temp with that cell
			std::uniform_int_distribution<int> udistribution(0, this->IgnitionSets[this->year - 1].size()-1);
            temp = this->IgnitionSets[this->year - 1][udistribution(generator)];          
		}
		
		std::cout << "\nSelected ignition point for Year " << this->year <<  ", sim " <<  this->sim << ": "<< temp;
	
		// If cell is available 
		if (this->burntCells.find(temp) == this->burntCells.end() && this->statusCells[temp - 1] < 3) {
			if (this->Cells_Obj.find(temp) == this->Cells_Obj.end()) {
				// Initialize cell, insert it inside the unordered map
				InitCell(temp);
			}
			
			// Iterator
			it = this->Cells_Obj.find(temp);
			
			// Not available or non burnable: no ignition
			if (it->second.getStatus() != "Available" || it->second.fType == 0) {
				this->noIgnition = true;
			}
			
			// Available and Burnable: ignition
			if (it->second.getStatus() == "Available" && it->second.fType != 0) {
				std::vector<int> ignPts = {temp};
				if (it->second.ignition(this->fire_period[year - 1], this->year, ignPts, & df[temp-1], this->coef_ptr, this->args_ptr, &wdf[this->weatherPeriod])) {
						
						//Printing info about ignitions        
						if (this->args.verbose){
							std::cout << "Cell " <<  it->second.realId <<  " Ignites" << std::endl;
							std::cout << "Cell " <<  it->second.realId << " Status: "<< it->second.getStatus() << std::endl;
						}
						
						// Status 
						this->statusCells[it->second.realId-1] = 1;
						
				}
				
			}

		} else {
			this->noIgnition = true;
			std::cout  <<"Next year..." << std::endl;
			if (this->args.verbose){
				std::cout << "No ignition during year " << this->year << ", Cell " << this->IgnitionPoints[this->year-1] << " is already burnt or non-burnable type" << std::endl;
			}
			this->year++;
			this->weatherPeriod = 0;
		}
	}
	
	
	
	
	// If ignition occurs, we update the forest status
	if (!this->noIgnition) {
		int newId = it->second.realId;
		if (this->args.verbose) std:cout << "New ID for burning cell: " << newId << std::endl;
		
		this->nIgnitions++;
		this->burningCells.insert(newId);
		this->burntCells.insert(newId);
		this->availCells.erase(newId);
		
		// Print sets information
		if (this->args.verbose){
			printSets(this->availCells, this->nonBurnableCells, this->burningCells, this->burntCells, this->harvestCells);
		}
	}
		
	// Plotter placeholder
	if (this->args.OutputGrids){
		//DEBUGstd::cout << "Grid post ignition" << std::endl;
		this->outputGrid();
	}
	
	
	// Next period
	//this->fire_period[year - 1] += 1;   // DEBUGGING!!!
	if (this->args.verbose){
		std::cout << "Fire period updated to " << this->fire_period[year - 1] << std::endl; 
	}
	
	// Check weather period consistency
	updateWeather();
	
	// Print-out information regarding the weather and fire period
	if (this->args.verbose){
		std::cout << "Fire Period Starts: " <<  this->fire_period[year-1] << std::endl;
		std::cout << "\nCurrent weather conditions:" << std::endl;
		this->CSVWeather.printWeatherDF(wdf[this->weatherPeriod]);
		
		if (this->args.WeatherOpt.compare("constant") == 0)
			std::cout << "(NOTE: current weather is not used for ROS with constant option)" << std::endl;
					
		// End of the ignition step
		std::cout << "\nNext Fire Period: " << this->fire_period[year-1] << std::endl;
	}
	
	// If no ignition occurs, go to next year (no multiple ignitions per year, only one)
	if(this->noIgnition){
		if (this->args.verbose){
			std::cout << "No ignition in year " << this->year << std::endl;
			std::cout << "-------------------------------------------------------------------------\n" << std::endl;
			std::cout << "                           End of the fire year " << this->year << "               "  << std::endl;
			std::cout << "-------------------------------------------------------------------------" << std::endl;
		}
		
		// Next year
		this->year+=1;  
	}
	
	return this->noIgnition;
}


// Send messages 
std::unordered_map<int, std::vector<int>> Cell2Fire::SendMessages(){
	// Iterator
	std::unordered_map<int, CellsFBP>::iterator it;
	
	// Clean list 
	this->burnedOutList.clear();
	
	// Check ending
	if (fire_period[year - 1] == args.MaxFirePeriods - 1 && this->args.verbose) {
		std::cout << "*** WARNING!!! About to hit MaxFirePeriods: " << this->args.MaxFirePeriods << std::endl;
	}
	
	/// Send messages logic
	this->messagesSent = false;
	std::unordered_map<int, vector<int>> sendMessageList;
	
	// Repeat fire flag 
	this->repeatFire = false;
	
	// Printing info before sending messages
	if (this->args.verbose){
		std::cout << "\n---------------------- Step 2: Sending Messages from Ignition ----------------------" << std::endl;
		std::cout << "Current Fire Period:" << this->fire_period[this->year - 1] << std::endl;
		printSets(this->availCells, this->nonBurnableCells, this->burningCells, 
					  this->burntCells, this->harvestCells);
		
	}
	
	/*
			Potential parallel zone: Send messages
			Burning cells loop: sending messages (Embarrasingly parallel?: CP: should be)
			Each burning cell updates its fire progress and (if needed) populates their message
	*/
	for (int cell : this->burningCells) {
		std::vector<int> aux_list;
		// Get object from unordered map
		it = this->Cells_Obj.find(cell);
		
		// Cell's info 
		if (this->args.verbose) {
			it->second.print_info();
		}
				
		/*
				Manage Fire method main step
		*/
		if (it->second.ROSAngleDir.size() > 0) {
			//std::cout << "Entra a Manage Fire" << std::endl;
			if (!this->args.BBOTuning){
				aux_list = it->second.manageFire(this->fire_period[this->year-1], this->availCells,  & df[cell-1], this->coef_ptr, 
															   this->coordCells, this->Cells_Obj, this->args_ptr, &wdf[this->weatherPeriod],
															   &this->FSCell, this->ROSRV);								
			}
												
			
			else{
				auto factors = BBOFactors.find(NFTypesCells[cell-1]);
				aux_list = it->second.manageFireBBO(this->fire_period[this->year-1], this->availCells,  & df[cell-1], this->coef_ptr, 
																		this->coordCells, this->Cells_Obj, this->args_ptr, &wdf[this->weatherPeriod],
																		&this->FSCell, this->ROSRV, factors->second);								
			}
			//std::cout << "Sale de Manage Fire" << std::endl;
		} 

		else{
			if(this->args.verbose) std::cout << "\nCell " << cell <<  " does not have any neighbor available for receiving messages" << std::endl;
		}
		
		// If message and not a true flag 
		if (aux_list.size() > 0 && aux_list[0] != -100) {
			if (this->args.verbose) std::cout <<"\nList is not empty" << std::endl;
			this->messagesSent = true;
			sendMessageList[it->second.realId] = aux_list; 
			if (this->args.verbose){
				std::cout << "Message list content" << std::endl;
				for (auto & msg : sendMessageList[it->second.realId]){
					std::cout << "  Fire reaches the center of the cell " << msg << "  Distance to cell (in meters) was 100.0" << " " << std::endl;
				}
			}
			
		}

		// Repeat fire conditions if true flag
		if (aux_list.size() > 0 && aux_list[0] == -100) {
			this->repeatFire = true;
		}

		// Burnt out inactive burning cells
		if (aux_list.size() == 0) {
			// not parallel here
			this->burnedOutList.push_back(it->second.realId);
			if (this->args.verbose){
				std::cout  << "\nMessage and Aux Lists are empty; adding to BurnedOutList" << std::endl;
			}
		}

	}
	/* End sending messages loop */
	
	
	// Check for burnt out updates via sets' difference
	for(auto &bc : this->burnedOutList){
		auto lt = this->burningCells.find(bc);
		if (lt != this->burningCells.end()) { 
			this->burningCells.erase(bc);
		}
	}
	if (this->args.verbose) printSets(this->availCells, this->nonBurnableCells, 
													 this->burningCells, this->burntCells, 
													 this->harvestCells);
	
	return sendMessageList;
}


// Get messages
void Cell2Fire::GetMessages(std::unordered_map<int, std::vector<int>> sendMessageList){
	// Iterator 
	std::unordered_map<int, CellsFBP>::iterator it;
	
	// Information of the current step 
	if (this->args.verbose){
		std::cout << "\n---------------------- Step 3: Receiving and processing messages from Ignition ----------------------" << std::endl;
		std::cout << "Current Fire Period: " <<  this->fire_period[this->year-1] << std::endl;
		printSets(this->availCells, this->nonBurnableCells, this->burningCells, this->burntCells, this->harvestCells);
	}	
	
	// Conditions depending on number of messages and repeatFire flag 
	// No messages but repetition
	if (this->repeatFire && !this->messagesSent) {
		if(this->args.verbose){
			std::cout << "Fires are still alive, no message generated" << std::endl;
			std::cout <<  "Current fire period: " << this->fire_period[this->year - 1] << std::endl;
		}
		this->fire_period[this->year - 1] += 1;

		// Check if we need to update the weather
		this->updateWeather();
	}

	// Messages and repetition
	if (this->repeatFire && this->messagesSent) {
		if (this->args.verbose) std::cout << "Messages have been sent, next step. Current period: " << this->fire_period[this->year - 1] << std::endl;
		this->repeatFire = false;
	}
	
	// No messages, no repeat (break and next year)
	if (!this->messagesSent && !this->repeatFire) {
		if (this->args.verbose){
			std::cout << "\nNo messages during the fire period, end of year "<< this->year << std::endl;
		}
		
		// Next year, reset weeks, weather period, and update burnt cells from burning cells
		this->year += 1;
		this->weatherPeriod = 0;
		this->noMessages = true;
			
		// Update sets
		for(auto &bc : this->burningCells){
			this->burntCells.insert(bc);
		}
		this->burningCells.clear();
		
		if (this->args.verbose) printSets(this->availCells, this->nonBurnableCells, this->burningCells, this->burntCells, this->harvestCells);
	}

	/*
	*
	*					Receiving messages
	*
	*/
	// Mesages and no repeat 
	 if (this->messagesSent && !this->repeatFire) {
	
		// frequency array
		std::unordered_map<int, int> globalMessagesList;
		for (auto & sublist : sendMessageList) {
			for (int val : sublist.second) {
				if (globalMessagesList.find(val) == globalMessagesList.end()){
					globalMessagesList[val] = 1;
				} else {
					globalMessagesList[val] = globalMessagesList[val] + 1;
				}
			}
		}
		
		// Initialize cells if needed (getting messages)
		for (auto & _bc : globalMessagesList) {
			int bc = _bc.first;
			if (this->Cells_Obj.find(bc) == this->Cells_Obj.end() && this->burntCells.find(bc) == this->burntCells.end()) {			
				// Initialize cell, insert it inside the unordered map
				InitCell(bc);
				it = this->Cells_Obj.find(bc);
			}
		}
		
			
			
		
		// Get burnt loop
		if(this->args.verbose){
			for (auto & _bc : globalMessagesList) {
				printf("CELL %d inside global message list \n", _bc.first);
			}
		}
		
		
		std::unordered_set<int> burntList;
		bool checkBurnt;
		for (auto & _bc : globalMessagesList) {
			//printf("\n\nWE ARE DEBUGGING!!!! CELL TO BE ANALYZED GET BURNT IS %d\n", _bc.first);
			int bc = _bc.first;
			if (this->burntCells.find(bc) == this->burntCells.end()) {
				if (this->Cells_Obj.find(bc) == this->Cells_Obj.end()) {
					
					// Initialize cell, insert it inside the unordered map
					InitCell(bc);
					it = this->Cells_Obj.find(bc);
				}
				else  it = this->Cells_Obj.find(bc);
					
				// Check if burnable, then check potential ignition
				if (it->second.fType != 0) {
					checkBurnt = it->second.get_burned(this->fire_period[this->year-1], 1, this->year, df, 
																			this->coef_ptr, this->args_ptr, &wdf[this->weatherPeriod]);

				} else {
					checkBurnt = false;
				}
				
				// Print-out regarding the burnt cell
				if(this->args.verbose){
					std::cout << "\nCell " << it->second.realId << " got burnt (1 true, 0 false): " << checkBurnt << std::endl;
				}
				
				// Update the burntlist
				if (checkBurnt) {
					burntList.insert(it->second.realId);
					
					// Cleaning step
					int cellNum = it->second.realId - 1;
					for (auto & angle : it->second.angleToNb) {
						int origToNew = angle.first;
						int newToOrig = (origToNew + 180) % 360;
						int adjCellNum = angle.second;  // Check
						auto adjIt = Cells_Obj.find(adjCellNum);
						if (adjIt != Cells_Obj.end()) {
							adjIt->second.ROSAngleDir.erase(newToOrig);
						} 
					}
				}

			}
		}
		
	
		// Update sets
		for(auto &bc : burntList) {
			this->burntCells.insert(bc);
		}

		for(auto &bc : this->burnedOutList) {
			this->burntCells.insert(bc);
		}
		
		for(auto &bc : burntList) {
			this->burningCells.insert(bc);
		}

		for(auto &bc : burningCells){
			auto lt = this->availCells.find(bc);
			if (lt != this->availCells.end()) {
				this->availCells.erase(bc);
			}
		}
		
		// Display info for debugging
		if(this->args.verbose){
			printSets(this->availCells, this->nonBurnableCells, this->burningCells, this->burntCells, this->harvestCells);
		}

		/*  
		*					Next Period
		*/
		this->fire_period[this->year - 1] += 1;
		
		// If weather is not constant (random weather to be supported in next commit...)
		this->updateWeather();
		
		// Message for constant weather
		if (this->args.WeatherOpt.compare("constant") == 0 && this->args.verbose){
			std::cout << "(NOTE: current weather is not used for ROS with constant option)" << std::endl;
		}
	}
}


// Display results
void Cell2Fire::Results(){
	/*****************************************************************************
	*
	*												Steps 4: Results and outputs 
	*
	******************************************************************************/
	// Iterator
	// Declare an iterator to unordered_map
	std::unordered_map<int, CellsFBP>::iterator it; 
	int i;
	
	for (auto & br : this->burntCells) {
		if (this->Cells_Obj.find(br) != this->Cells_Obj.end()) {
			// Get object from unordered map
			it = this->Cells_Obj.find(br);
			
			// Initialize the fire fields for the selected cel
			it->second.status = 2;
		}
	}

	for (auto & br : this->burningCells) {
		if (this->Cells_Obj.find(br) != this->Cells_Obj.end()) {
			// Get object from unordered map
			it = this->Cells_Obj.find(br);
			
			// Initialize the fire fields for the selected cel
			it->second.status = 2;
		}
	}
	
	// Final results for comparison with Python
	//DEBUGstd::cout  << "\n ------------------------ Final results for comparison with Python ------------------------";
	
	// Final report
	float ACells = this->availCells.size();
	float BCells = this->burntCells.size();
	float NBCells = this->nonBurnableCells.size();
	float HCells = this->harvestCells.size();
	
	std::cout <<"\n----------------------------- Results -----------------------------" << std::endl;
	std::cout << "Total Available Cells:    " << ACells << " - % of the Forest: " <<  ACells/nCells*100.0 << "%" << std::endl;
	std::cout << "Total Burnt Cells:        " << BCells << " - % of the Forest: " <<  BCells/nCells*100.0 <<"%" << std::endl;
	std::cout << "Total Non-Burnable Cells: " << NBCells << " - % of the Forest: " <<  NBCells/nCells*100.0 <<"%"<< std::endl;
	std::cout << "Total Harvested Cells: " << HCells << " - % of the Forest: " <<  HCells/nCells*100.0 <<"%"<< std::endl;

	// Final Grid 
	if(this->args.FinalGrid){
		CSVWriter CSVFolder("","");
		if (this->args.OutFolder.empty())
			this->gridFolder = "mkdir -p " + this->args.InFolder + "simOuts/Grids/Grids" + std::to_string(this->sim);
		else
			this->gridFolder = "mkdir -p " + this->args.OutFolder + "/Grids/Grids" + std::to_string(this->sim);
		CSVFolder.MakeDir(this->gridFolder);
		
		if (this->args.OutFolder.empty())
			this->gridFolder = this->args.InFolder + "simOuts/Grids/Grids" + std::to_string(this->sim) + "/";
		else
			this->gridFolder = this->args.OutFolder + "/Grids/Grids" + std::to_string(this->sim) + "/";
		//std::string gridName = this->gridFolder + "FinalStatus_" + std::to_string(this->sim) + ".csv";
		outputGrid();
		
		/*if(this->args.verbose){
			std::cout  << "We are plotting the final forest status to a csv file " << gridName << std::endl;
		}
		CSVWriter CSVPloter(gridName, ",");
		
		for (auto & cell: this->Cells_Obj){
			if(cell.second.getStatus() == "Burning" || cell.second.getStatus() == "Burnt"){
				this->statusCells[cell.second.id] = 1;
				//std::cout  << "We are including cell " << cell.second.realId << " in the plot" << std::endl;
			}
		}
		
		
		std::vector<int> statusCellsCSV (this->nCells);
		for (i=0; i < this->statusCells.size(); i++){		
			if(this->statusCells[i] == 1) statusCellsCSV[i] = 1;
		}
		CSVPloter.printCSV(this->rows, this->cols, statusCellsCSV);
		*/
	}
	
	
	// Messages
	if(this->args.OutMessages){
		this->messagesFolder = this->args.OutFolder + "/Messages/";
		std::string messagesName;
		
		if (this->sim < 10){
			messagesName = this->messagesFolder + "MessagesFile0" + std::to_string(this->sim) + ".csv";
		}
		
		else{
			messagesName = this->messagesFolder + "MessagesFile" + std::to_string(this->sim) + ".csv";
		}
		
		if(this->args.verbose){
			std::cout  << "We are generating the network messages to a csv file " << messagesName << std::endl;
		}
		CSVWriter CSVPloter(messagesName, ",");
		CSVPloter.printCSVDouble_V2(this->burntCells.size() - this->nIgnitions, 4, this->FSCell);
	}

	
	
}


// Generate the binary grids
void Cell2Fire::outputGrid(){
	// FileName
	std::string gridName;
	std::vector<int> statusCells2(this->nCells, 0); //(long int, int);
	
	// Update status 
	for (auto & bc : this->burningCells){
			statusCells2[bc-1] = 1;
	}
	for (auto & ac : this->burntCells){
			statusCells2[ac-1] = 1;
	}
	for (auto & hc : this->harvestCells){
			statusCells2[hc-1] = -1;
	}
		
	if (this->gridNumber < 10){
			gridName = this->gridFolder+ "ForestGrid0" + std::to_string(this->gridNumber) + ".csv";
	}
	
	else {
			gridName = this->gridFolder+ "ForestGrid" + std::to_string(this->gridNumber) + ".csv";
	}
	
	if(this->args.verbose){
		std::cout  << "We are plotting the current forest to a csv file " << gridName << std::endl;
	}
	
	CSVWriter CSVPloter(gridName, ",");
	CSVPloter.printCSV_V2(this->rows, this->cols, statusCells2);
	this->gridNumber++;
}


// Update hourly weather (and grid)
void Cell2Fire::updateWeather(){
	if (this->args.WeatherOpt != "constant" && this->fire_period[this->year - 1] * this->args.FirePeriodLen / this->args.MinutesPerWP > this->weatherPeriod + 1) {
			this->weatherPeriod++;
			
			if (this->args.OutputGrids){
				this->outputGrid();
			}
			
			if (this->args.verbose){
				std::cout  << "\nWeather has been updated" << std::endl;
				this->CSVWeather.printWeatherDF(wdf[this->weatherPeriod]);
			}
	}
}


// Advance one Time-step 
void Cell2Fire::Step(std::default_random_engine generator){
	// Iterator
	// Declare an iterator to unordered_map
	std::unordered_map<int, CellsFBP>::iterator it;	
	bool auxC = false;
	this->noMessages = false;
	
	// Conditions entering the step
	if (this->args.verbose){
		std::cout << "********************************************" << std::endl;
		std::cout << "Year: " << this->year << std::endl;
		std::cout << "Total years:" <<  this->args.TotalYears << std::endl;
		std::cout << "Fire Period: " <<  this->fire_period[this->year-1]  << std::endl;
		std::cout << "WeatherPeriod: " <<  this->weatherPeriod << std::endl;
		std::cout << "MaxFirePeriods: " <<  this->args.MaxFirePeriods << std::endl;
		printSets(this->availCells, this->nonBurnableCells, this->burningCells, this->burntCells, this->harvestCells);
		std::cout << "********************************************" << std::endl;
	}
	
	 // One step (one fire period, ignition - if needed -, sending messages and receiving them - if needed)
	 // For completeness: just in case user runs it longer than the horizon (should not happen)
	if (this->year > this->args.TotalYears){
		if (this->args.verbose){
			printf("\nYear is greater than the Horizon, no more steps");
		}
		this->done = true;
				
		// Print-out results to folder
		if (this->args.verbose) this->Results();        
		
		//Next Sim
		this->sim += 1;	
	}
	
	// Info
	if (this->args.verbose){	
		std::cout << "\nSimulating year" << this->year << "\nOut of totalYears:" << this->args.TotalYears;
	}
	
	// New operational step (ONE fire period)
	if (this->fire_period[this->year - 1] > 0 && !this->done){
		// Fire Spread (one time step of RL - Operational)
		// Send messages after ignition (does not advance time!)
		std::unordered_map<int, std::vector<int>> SendMessageList = this->SendMessages();
		
		// Get Message
		this->GetMessages(SendMessageList);
	}
	
	// Operational dynamic
	// Ignition if we are in the first period (added workaround for no Messages)
	if (this->fire_period[this->year - 1] == 0 && !this->done && !this->noMessages){
		//std::cout << "Entra a Ignition step 0" << std::endl;
		// Continue only if ignition  - No ignition (True): done
		if(this->RunIgnition(generator)){
			// Next year
			this->weatherPeriod = 0;
			
			// If more than planning horizon, next sim
			if (this->year > this->args.TotalYears){
				// Print-out results to folder
				this->Results();

				// Next Sim if max year
				this->done = true;
			}
		}
		else {
			// Start sending messages
			std::unordered_map<int, std::vector<int>> SendMessageList = this->SendMessages();
			
			// Get Message
			this->GetMessages(SendMessageList);
			
			// Check if no burning cells to stop
			if(this->burningCells.size() == 0){
				// Next Sim if max year
				this->done = true;
			}

			
			
		}
	}


	// Ending conditions 
	//if (this->year - 1 >= this->fire_period.size()){
	//	this->year = this->fire_period.size();
	//}
	
	if (this->fire_period[std::min(this->year , int(fire_period.size())) - 1] >= this->args.MaxFirePeriods){
		// Extra breaking condition: Max fire periods then go to next year
		if (this->args.verbose){
			printf("\nNext year due to max periods...\n");
		}

		// Next Year/Season update
		//if(this->year < this->year += 1;
		this->year += 1; // EXTRA
		this->weatherPeriod = 0;
		auxC = true;
		
		for(auto &bc : burningCells){
			auto lt = this->availCells.find(bc);
			if (lt != this->availCells.end()) {
				this->availCells.erase(bc);
			}
			this->burntCells.insert(bc);
		}
		this->burningCells.clear();
	}
	
	// If more than planning horizon, next sim
	if (this->year > this->args.TotalYears){
		//printf("\n\nEntra a year mayor al total...\n\n");
		// Print-out results to folder
		this->Results();

		// Next Sim if max year
		this->sim += 1;
		this->done = true;
	}
	
	// Done flag (extra condition: no available cells or death of the team)
	if ((this->availCells.size() == 0) || (this->burningCells.size() == 0 && !this->noMessages) && !this->done && !auxC){
		// Done
		this->done = true;
		
		// Print-out results to folder
		this->Results();        
		
		// Next Sim if max year
		this->sim += 1;
	}
		
	// Print current status
	if (!this->done && this->args.verbose){
		printf("\nFire Period: %d", this->fire_period[this->year - 1]);
		printf("\nYear: %d \n\n", this->year);
	}
}


// Populate initial harvested cells
void Cell2Fire::InitHarvested(){
	std::cout  << "OK";
}


// Get Hitting ROS matrix 
std::vector<float> Cell2Fire::getROSMatrix(){
	std::vector<float> ROSMatrix (this->nCells, 0);
	
	
	return ROSMatrix;
}


// Get Fire Progress matrix 
std::vector<float> Cell2Fire::getFireProgressMatrix(){
	std::vector<float> ProgressMatrix (this->nCells, 0);
	
	return ProgressMatrix;
}








/******************************************************************************

																Main Program	

*******************************************************************************/
int main(int argc, char * argv[]){
	// Read Arguments
	std::cout << "------ Command line values ------\n";
	arguments args;
	arguments * args_ptr = &args;
	parseArgs(argc, argv, args_ptr);
	//printArgs(args);
	
	// Random generator and distributions
	std::default_random_engine generator (args.seed);
	std::uniform_int_distribution<int> udistribution(1, args.NWeatherFiles);		// Get random weather
	std::normal_distribution<double> ndistribution(0.0,1.0);  							// ROSRV
	
	// Random numbers (weather file and ROS-CV)
	int rnumber;
	double rnumber2;
	
	// Initialize Instance
	Cell2Fire Forest(args);
	
	// Random ignition 
	std::uniform_int_distribution<int> udistributionIgnition(1, Forest.nCells);		// Get random ignition point
	
	// Episodes
	int ep = 0;
	int tstep = 0;
		
	// Episodes loop (episode = replication)
	// CP: Modified to account the case when no ignition occurs and no grids are generated (currently we are not generating grid when no ignition happened, TODO)
	for(ep = 1; ep <= args.TotalSims * 10; ep++){
		// Reset environment (passing new random numbers)
		rnumber = udistribution(generator);
		rnumber2 = ndistribution(generator);
		
		// Reset
		Forest.reset(rnumber, rnumber2);
	
		// Time steps during horizon (or until we break it)
		for (tstep = 0; tstep <= Forest.args.MaxFirePeriods * Forest.args.TotalYears ; tstep++){   
			//DEBUGprintf("\n ---- tstep %d \n", tstep);
			Forest.Step(generator);
			//DEBUGprintf("\nDone: %d", Forest.done);
			
			if (Forest.done){
				//DEBUGprintf("\n Done = True!, break \n");
				break;
			}
		
		}
		// Enforces to satisfy the total number of simulations (if no ignition, find another cell until we obtain the TotalSim asked)
		if (Forest.sim > args.TotalSims){
			break;
		}
		
	}
	
	return 0;
}