// include classes
#include "Forest.h"

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

/* 
	Constructor 
*/
Forest::Forest(int _id, std::string _location, std::vector<int> _coord, int _nCells, double _area, double _vol, 
					  double _age, double _perimeter, std::unordered_map<std::string, int> & _fTypes) {
    
	// Populate fields
	this->id = _id;
    this->location = _location;
    this->coord = _coord;
    this->nCells = _nCells;
    this->area = _area;
    this->vol = _vol;
    this->age = _age;
    this->fTypes = _fTypes;
    this->availCells = std::vector<int>();
    for (int i = 0; i <= this->nCells; i++) {
        this->availCells.push_back(i);
    }
    this->burntCells = std::vector<int>();

}

/*
	Prints-out information from the forest
*/
void Forest::print_info() {
	std::cout << "Forest Information" << std::endl;
    std::cout <<  "ID = " << this->id << std::endl; 
	std::cout <<  "Location = " << this->location << std::endl;
	//std::cout << "Coordinates = " << this->coord << std::endl; 
	std::cout << "NCells = " << this->nCells << std::endl;
	std::cout << "Area = " << this->area << std::endl;
	std::cout << "Vol = " << this->vol << std::endl; 
	std::cout << "Age = " << this->age << std::endl;
	//std::cout << "FTypes = " << this->fTypes << std::endl;
}


// Main for debugging
int main(){
	std::cout << "Forest has been compiled!" << std::endl;
	return 0;
}