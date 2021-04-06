#include "WriteCSV.h"

#include <cmath>
#include <iostream>
#include <fstream>
#include <vector>
#include <iterator>
#include <string>
#include <algorithm>
#include <unordered_map>
#include <unordered_set>
#include <boost/algorithm/string.hpp>
#include <set>
 
/*
 * Constructur
 */
CSVWriter::CSVWriter(std::string filename, std::string delm){
	this->fileName = filename;
	this->delimeter = delm;		
	this->linesCount = 0;
}
 
 
/*
* Prints iterator into a row of a csv file 
*/
template<typename T>
void CSVWriter::addDatainRow(T first, T last){
	std::fstream file;
	// Open the file in truncate mode if first line else in Append Mode
	file.open(this->fileName, std::ios::out | (this->linesCount ? std::ios::app : std::ios::trunc));
 
	// Iterate over the range and add each element to file seperated by delimeter.
	for (; first != last; )
	{
		file << *first;
		if (++first != last)
			file << this->delimeter;
	}
	file << "\n";
	this->linesCount++;
 
	// Close the file
	file.close();
}

/*
*     Creates CSV
*/
void CSVWriter::printCSV(int rows, int cols, std::vector<int> statusCells)
{
	// Create a rowVector for printing
	std::vector<int> rowVector;
 
	// Adding vector to CSV File
	int r, c;
	
	// Printing rows (output)
	for (r=0; r<rows; r++){
		for (c=0; c < cols; c++){
			
			std::vector<int>::const_iterator first = statusCells.begin() + c+r*cols;
			std::vector<int>::const_iterator last = statusCells.begin() + c+r*cols +cols;
			std::vector<int> rowVector(first, last);
						
			this->addDatainRow(rowVector.begin(), rowVector.end());
			c+=cols;
		}
	}
	
}

void CSVWriter::printCSV_V2(int rows, int cols, std::vector<int> statusCells)
{
	std::ofstream ofs(this->fileName, std::ofstream::out);
	std::string toOut;
	int r,c,i;
	
	for (r = 0; r < rows; r++)
	{
		for (c = 0; c < cols; c++)
		{
			std::string toOut;
			for (i = 0; i < cols; i ++){
				if (i == cols - 1){
					toOut += std::to_string(statusCells[c+r*cols + i]);
				}
				else{
					toOut += std::to_string(statusCells[c+r*cols + i])  + this->delimeter;
				}
			}
			ofs << toOut << "\n";
			c+=cols;
		}
	}
	// Close file 
	ofs.close();
}


/*
*     Creates CSVDouble
*/
void CSVWriter::printCSVDouble(int rows, int cols, std::vector<double> network)
{
	// Create a rowVector for printing
	std::vector<double> rowVector;
 
	// Adding vector to CSV File
	int r, c;
	
	// Printing rows (output)
	for (r=0; r < rows; r++){
		for (c=0; c < cols; c++){
			
			std::vector<double>::const_iterator first = network.begin() + c+r*cols;
			std::vector<double>::const_iterator last = network.begin() + c+r*cols +cols;
			std::vector<double> rowVector(first, last);
						
			this->addDatainRow(rowVector.begin(), rowVector.end());
			c+=cols;
		}
	}
	
}

// Ofstream version to save faster
void CSVWriter::printCSVDouble_V2(int rows, int cols, std::vector<double> network){
	
	bool outs = false;
	std::ofstream ofs(this->fileName, std::ofstream::out);

	for (int r = 0; r < rows; r++)
	{
		for (int c = 0; c < cols; c++)
		{
			if (network[c+r*cols] < 1 || network[c+r*cols + 1] < 1 || std::ceil(network[c+r*cols]) != network[c+r*cols]){
				outs = true;
				break;
			}

			ofs << (int)network[c+r*cols]  << this->delimeter << (int)network[c+r*cols + 1]  << this->delimeter << (int)network[c+r*cols + 2]  << this->delimeter << network[c+r*cols + 3]  << "\n";
			c+=cols;
		}
		
		if (outs) {
			break;
		}
	}
	// Close file 
	ofs.close();
	
}


void CSVWriter::MakeDir(std::string pathPlot) {
	// Default folder simOuts
	const char * Dir;
	Dir = pathPlot.c_str();
	system(Dir);
}