#include "ReadCSV.h"
#include "FBP5.0.h"

#include <stdexcept>
#include <iostream>
#include <fstream>
#include <vector>
#include <iterator>
#include <string>
#include <algorithm>
#include <unordered_map>
#include <unordered_set>
#include <boost/algorithm/string.hpp>
 
/*
 * Constructur
 */
CSVReader::CSVReader(std::string filename, std::string delm){
	this->fileName = filename;
	this->delimeter = delm;		
}
 
 
/*
* Parses through csv file line by line and returns the data
* in vector of vector of strings.
*/
std::vector<std::vector<std::string>> CSVReader::getData(){
	std::ifstream file(this->fileName);
  if (!file.good()) {
    std::string error_message = this->fileName + " doesn't exist!";
    throw std::invalid_argument(error_message); 
  }

	std::vector<std::vector<std::string> > dataList;
	std::string line = "";
	
	// Iterate through each line and split the content using delimeter
	while (getline(file, line))
	{
		std::vector<std::string> vec;
		boost::algorithm::split(vec, line, boost::is_any_of(this->delimeter));
		dataList.push_back(vec);
	}
	// Close the File
	file.close();
 
	return dataList;
}


/*
* Prints data to screen inside the DF obtained from the CSV file
*/
void CSVReader::printData(std::vector<std::vector<std::string>> & DF){
	// Print the content of row by row on screen
	for(std::vector<std::string> vec : DF)
	{
		for(std::string data : vec)
		{
			if(data.length() >0) std::cout << " " << data << " ";
			else std::cout << " " <<  "NaN" << " ";
		}
		std::cout<<std::endl;
	}
}


/*
* Populates the df input objects based on the DF csv file for each row/cell
*/
void CSVReader::parseDF(inputs * df_ptr, std::vector<std::vector<std::string>> & DF, int NCells){
	int i;
	
	// Floats 
	float pdf, cur, elev, lat, lon, ffmc, ws, bui, gfl;
	
	// Ints 
	int mon, jd, jd_min, waz, ps, saz, pc, time, pattern, hour,hourly; //std::stoi (DF[i][1] ,&sz);
	
	// CChar
	const char * faux;
	std::string::size_type sz;   // alias of size_t
	
	// Loop over cells (populating per row)
	for (i=1; i <= NCells; i++){
		//printf("Populating DF for cell %d\n", i);
		faux = DF[i][0].append(" ").c_str();
		
		if (DF[i][2].compare("") == 0) jd = 0;
		else jd = std::stoi (DF[i][2] ,&sz);
		
		if (DF[i][4].compare("") == 0) jd_min = 0;
		else jd_min = std::stoi (DF[i][4] ,&sz);
		
		if (DF[i][10].compare("") == 0) waz = 0;
		else waz = std::stoi (DF[i][10] ,&sz) + 180.;// + 2*90;  // CHECK!!!!
		if (waz >= 360) waz = waz - 360;
		
		if (DF[i][12].compare("") == 0) ps = 0;
		else ps = std::stoi (DF[i][12] ,&sz);
		
		if (DF[i][13].compare("") == 0) saz = 0;
		else saz = std::stoi (DF[i][13] ,&sz);
		
		if (DF[i][14].compare("") == 0) pc = 0;
		else pc = std::stoi (DF[i][14] ,&sz);
		
		if (DF[i][15].compare("") == 0) pdf = 0;
		else pdf = std::stoi (DF[i][15] ,&sz);
		
		if (DF[i][17].compare("") == 0) cur = 0;
		else cur = std::stoi (DF[i][17] ,&sz);
		
		if (DF[i][7].compare("") == 0) elev = 0;
		else elev = std::stoi (DF[i][7] ,&sz);
		
		if (DF[i][18].compare("") == 0) time = 0;
		else time = std::stoi (DF[i][18] ,&sz); 
		
		if (DF[i][5].compare("") == 0) lat = 0;
		else lat = std::stof (DF[i][5], &sz);
		
		if (DF[i][6].compare("") == 0) lon = 0;
		else lon = std::stof (DF[i][6], &sz);
		
		if (DF[i][8].compare("") == 0) ffmc = 0;
		else ffmc = std::stof (DF[i][8], &sz);
		
		if (DF[i][9].compare("") == 0) ws = 0;
		else ws = std::stof (DF[i][9], &sz);
		
		if (DF[i][11].compare("") == 0) bui = 0;
		else bui = std::stof (DF[i][11], &sz);
		
		if (DF[i][16].compare("") == 0) gfl = 0;
		else gfl = std::stof (DF[i][16], &sz);
		
		if (DF[i][18].compare("") == 0) pattern = 0;
		else pattern = 1;// std::stoi (DF[i][18], &sz);
		
		
			
		// Set values
		strncpy(df_ptr->fueltype, faux, 4);
		df_ptr->mon=mon; df_ptr->jd=jd; /*df_ptr->m=DF[i][3];*/ df_ptr->jd_min=jd_min;
		df_ptr->lat=lat; df_ptr->lon=lon; df_ptr->elev=elev; df_ptr->ffmc=ffmc;
		df_ptr->ws=ws; df_ptr->waz=waz; df_ptr->bui=bui; df_ptr->ps=ps;
		df_ptr->saz=saz; df_ptr->pc=pc; df_ptr->pdf=pdf; df_ptr->gfl=gfl; 
		df_ptr->cur=cur; df_ptr->time=time;df_ptr->pattern=pattern;
		df_ptr->hourly=0;df_ptr->hour=0;
			
		// Next pointer
		df_ptr++;
	}
}


/*
* Populates vector of size NCells with type number based on lookup table 
*/
void CSVReader::parseNDF(std::vector<int> &NFTypes, std::vector<std::vector<std::string>> & DF, int NCells){
	int i;
	
	// Ints 
	int FType;
	
	// CChar
	const char * faux;
	std::string::size_type sz;   // alias of size_t
	
	// Loop over cells (populating per row)
	for (i=1; i <= NCells; i++){
		//printf("Populating DF for cell %d\n", i);
		if (DF[i][20].compare("") == 0) FType = 0;
		else FType = std::stoi (DF[i][20], &sz);
			
		// Set values
		NFTypes.push_back(FType);
		
	}
}



/*
* Populate Weather DF
*/
void CSVReader::parseWeatherDF(weatherDF * wdf_ptr, std::vector<std::vector<std::string>> & DF, int WPeriods){
	int i;
	
	//Strings
	std::string scenario, datetime;
	std::string::size_type sz;   // alias of size_t
	
	//Floats 
	float apcp, tmp, rh, ws, ffmc, dmc, dc, isi, bui, fwi;
	
	//Ints 
	int waz;
	
	// Loop over cells (populating per row)
	for (i=1; i <= WPeriods; i++){
		//printf("Populating Weather DF period %d\n", i);
		scenario = DF[i][0];
		
		scenario = DF[i][0];
		datetime = DF[i][1];
		
		if (DF[i][6].compare("") == 0) waz = 0;
		else {waz = std::stoi (DF[i][6] ,&sz); //+ 180/2;   // DEBUGGING THE ANGLE 
			if (waz >= 360){
				waz = waz - 360;
			}
		}
		
		if (DF[i][2].compare("") == 0) apcp = 0;
		else apcp = std::stof (DF[i][2], &sz);
		
		if (DF[i][3].compare("") == 0) tmp = 0;
		else tmp = std::stof (DF[i][3], &sz);
		
		if (DF[i][4].compare("") == 0) rh = 0;
		else rh = std::stof (DF[i][4], &sz);
		
		if (DF[i][5].compare("") == 0) ws = 0;
		else ws = std::stof (DF[i][5], &sz);
		
		if (DF[i][7].compare("") == 0) ffmc = 0;
		else ffmc = std::stof (DF[i][7], &sz);
		
		if (DF[i][8].compare("") == 0) dmc = 0;
		else dmc = std::stof (DF[i][8], &sz);
		
		if (DF[i][9].compare("") == 0) dc = 0;
		else dc = std::stof (DF[i][9], &sz);
				
		if (DF[i][10].compare("") == 0) isi = 0;
		else isi = std::stof (DF[i][10], &sz);
		
		if (DF[i][11].compare("") == 0) bui = 0;
		else bui = std::stof (DF[i][11], &sz);
		
		if (DF[i][12].compare("") == 0) fwi = 0;
		else fwi = std::stof (DF[i][12], &sz);
		
		// Set values
		wdf_ptr->scenario = scenario;
		wdf_ptr->datetime = datetime;
		wdf_ptr->apcp=apcp; wdf_ptr->tmp=tmp; wdf_ptr->rh=rh;
		wdf_ptr->ws=ws; wdf_ptr->waz=waz; wdf_ptr->ffmc=ffmc; wdf_ptr->dmc=dmc;
		wdf_ptr->dc=dc; wdf_ptr->isi=isi; wdf_ptr->bui=bui; wdf_ptr->fwi=fwi;
			
		// Next pointer
		wdf_ptr++;
	}
	
}


/*
* Populate IgnitionDF
*/
void CSVReader::parseIgnitionDF(std::vector<int> & ig, std::vector<std::vector<std::string>> & DF, int IgPeriods){
	// Integers
	int i, igcell;
	std::string::size_type sz;   // alias of size_t
	
	// Loop over cells (populating per row)
	for (i=1; i <= IgPeriods; i++){
		//DEBUGprintf("Populating Ignition points: %d\n", i);
		igcell = std::stoi(DF[i][1], &sz);
		
		// Set values
		ig[i-1]= igcell;
			
		// Next pointer
		//ig_ptr++;
	}
	
	
}

/*
* Populate HarvestedDF
*/
void CSVReader::parseHarvestedDF(std::unordered_map<int, std::vector<int>> & hc, std::vector<std::vector<std::string>> & DF, int HPeriods){
	// Integers
	int i, j, hcell;
	std::vector<int> toHarvestCells;
	std::string::size_type sz;   // alias of size_t
	
	// Loop over cells (populating per row)
	for (i=1; i <= HPeriods; i++){
		// Clean the vector before the new year 
		toHarvestCells.clear();
		
		// Loop over years of the simulation
		for(j=1; j < DF[i].size(); j++){
			hcell = std::stoi(DF[i][j], &sz);
		
			// Set values
			toHarvestCells.push_back(hcell);
		}
		
		// Populate unordered set 
		hc.insert(std::make_pair(i, toHarvestCells));	
		
	}
	
	
}

/*
* Populate BBO Tuning factors
*/
void CSVReader::parseBBODF(std::unordered_map<int, std::vector<float>> & bbo, std::vector<std::vector<std::string>> & DF, int NFTypes){
	// Integers
	int i, j, ftype;
	int ffactors = 4;
	std::vector<float> bboFactors;
	std::string::size_type sz;   // alias of size_t
	
	// Loop over cells (populating per row)
	for (i=1; i <= NFTypes; i++){
		// Clean the vector before the fuels
		bboFactors.clear();
		
		//DEBUGprintf("Populating Ignition points: %d\n", i);
		ftype = std::stoi(DF[i][0], &sz);
		
		for (j=1; j <= ffactors; j++){
			bboFactors.push_back(std::stof(DF[i][j], &sz));
		}

		//Set values							 
		bbo.insert(std::make_pair(ftype, bboFactors));	
	}
	
	
}

void CSVReader::parseForestDF(forestDF * frt_ptr, std::vector<std::vector<std::string>> & DF){
	// Ints 
	int cellside, rows, cols;
	int i, j;
	
	// Others 
	std::vector<std::unordered_map<std::string, int>> adjCells;
 	std::string::size_type sz;   // alias of size_t
	std::vector<std::vector<int>> coordCells;
	std::unordered_map<std::string, int> Aux;
	std::vector<int> Aux2;
	
	std::string North = "N";
    std::string South = "S";
    std::string East = "E";
    std::string West = "W";
    std::string NorthEast = "NE";
    std::string NorthWest = "NW";
    std::string SouthEast = "SE";
    std::string SouthWest = "SW";
	
	// Filling DF
	//DEBUGprintf("Populating Forest DF\n");
	
	cols = std::stoi (DF[0][1], &sz);
	rows = std::stoi (DF[1][1], &sz);
	cellside = std::stoi (DF[4][1], &sz);
	
	//DEBUGprintf("cols: %d,  rows:  %d,   cellside:  %d\n", cols, rows, cellside);
	
	// CoordCells and Adjacents
	int n = 1; 
	int r, c;
	//std::cout  << "CoordCells Debug" << std::endl;
	for (r=0; r<rows; r++){
		for (c=0; c < cols; c++){
			
			/*   CoordCells  */
			Aux2 = std::vector<int>();
			Aux2.push_back(c); 
            Aux2.push_back(rows-r-1);   
			coordCells.push_back(Aux2);                    
			//printf("i,j = %d,%d\n", r,c);
			//std::cout << "x: " << coordCells[c + r*(cols)][0] <<  "  y: " << coordCells[c + r*(cols)][1]  <<   std::endl;
					
			/*   Adjacents  */
			// if we have rows (not a forest = line)
			if (rows>1){
				
				// Initial row
				if(r == 0){
					
					if (c == 0){
                        Aux = {{North,-1},{NorthEast,-1},{NorthWest,-1},{South,n+cols},{SouthEast,n+cols+1}, 
							        {SouthWest,-1}, {East,n+1},{West,-1}};
                        adjCells.push_back(Aux);
						n++;
					}
                    if (c == cols - 1){
                        Aux = {{North,-1},{NorthEast,-1},{NorthWest,-1},{South, n+cols},{SouthEast,-1},
										{SouthWest, n+cols-1,}, {East,-1}, {West,n-1}};
						adjCells.push_back(Aux);
                        n++;
					}
                    if (c > 0 && c < cols-1){    
                        Aux = {{North, -1},{NorthEast,-1},{NorthWest,-1},{South,n+cols},{SouthEast,n+cols+1}, 
									{SouthWest, n+cols-1}, {East, n+1},{West,n-1}};
						adjCells.push_back(Aux);
						n++;
					}
				}
				
				// In between
				if (r > 0 && r < rows - 1){
                    if (c == 0){
                        Aux = {{North, n-cols} , {NorthEast, n-cols+1 }, {NorthWest,-1}, {South, n+cols}, 
									{SouthEast, n+cols+1} , {SouthWest,-1}, {East, n+1} ,{West,-1}};
						adjCells.push_back(Aux);
                        n++;
					}
                    if (c == cols-1){
                        Aux = {{North, n-cols}, {NorthEast,-1}, {NorthWest, n-cols-1},{South, n+cols}, 
									{SouthEast,-1}, {SouthWest, n+cols-1}, {East,-1}, {West, n-1}};
                        adjCells.push_back(Aux);
						n++;
					}
                    if (c>0 && c<cols-1){    
                        Aux = {{North, n-cols}, {NorthEast, n-cols+1} , {NorthWest, n-cols-1}, {South, n+cols}, 
									{SouthEast, n+cols+1} , {SouthWest, n+cols-1}, {East, n+1}, {West, n-1}};
						adjCells.push_back(Aux);
                        n++;    
					}
				}
				
				// Final row
				if (r == rows-1){
                    if (c == 0){
                        Aux = {{North,n-cols}, {NorthEast,n-cols+1}, {NorthWest,-1}, {South,-1}, {SouthEast,-1}, 
									{SouthWest,-1,}, {East,n+1}, {West,-1}};
						adjCells.push_back(Aux);				 
                        n++;    
					}
                        
                    if (c == cols-1){
                        Aux = {{North,n-cols}, {NorthEast,-1}, {NorthWest,n-cols-1}, {South,-1}, {SouthEast,-1}, 
									{SouthWest,-1}, {East,-1}, {West,n-1}};
						adjCells.push_back(Aux);
                        n++;    
					}
                    if (c>0 and c<cols-1){    
                        Aux = {{North,n-cols}, {NorthEast, n-cols+1}, {NorthWest,n-cols-1}, {South,-1}, 
									{SouthEast,-1} , {SouthWest,-1}, {East,n+1}, {West,n-1}};
						adjCells.push_back(Aux);
						n++;    
					}
				
				}
			}	
				
			// One line
			if (rows == 1){
				if (c == 0){
					Aux = {{North,-1}, {NorthEast,-1}, {NorthWest,-1}, {South,-1}, {SouthEast,-1}, 
								{SouthWest,-1}, {East,n+1}, {West,-1}};
					adjCells.push_back(Aux);
					n++;    
				}
				if (c == cols-1){
					Aux = {{North,-1}, {NorthEast,-1}, {NorthWest,-1}, {South,-1}, {SouthEast,-1}, 
								{SouthWest,-1}, {East,-1},{West,n-1}};
					adjCells.push_back(Aux);
					n++;    
				}
				if (c>0 && c<cols-1){						
					Aux = {{North,-1}, {NorthEast,-1}, {NorthWest,-1}, {South,-1}, {SouthEast,-1}, 
								{SouthWest,-1}, {East,n+1}, {West,n-1}};
					adjCells.push_back(Aux);
					n++;    
				}
			}
		}
	}
	
	
	
	// Adjacents cells
	//std::cout  << "Adjacents Debug" << std::endl;
	/*for (i=0; i<adjCells.size();i++){
		std::cout << "Cell "<< i+1 << " =  "; 
		for (auto & nb : adjCells[i]){
			std::cout << " " << nb.first << " : " << nb.second;
		}
		std::cout << std::endl;
	}
	*/
	
	
	// Set values
	frt_ptr->cellside = cellside;
	frt_ptr->rows = rows;
	frt_ptr->cols = cols;
	frt_ptr->coordCells = coordCells;
	frt_ptr->adjCells = adjCells;
		
		
	
}



void CSVReader::printDF(inputs df){
	std::cout << df.fueltype; std::cout << " " << df.mon; std::cout << " " << df.jd;
	std::cout << " " << df.jd_min; std::cout << " " << df.lat; std::cout << " " << df.lon;
	std::cout << " " << df.elev; std::cout << " " << df.ffmc; std::cout << " " << df.ws;
	std::cout << " " << df.waz; std::cout << " " << df.bui; std::cout << " " << df.ps;
	std::cout << " " << df.saz; std::cout << " " << df.pc; std::cout << " " << df.pdf;
	std::cout << " " << df.gfl; std::cout << " " << df.cur; std::cout << " " << df.time;
	std::cout << " " << df.pattern << std::endl;
}

void CSVReader::printWeatherDF(weatherDF wdf){
	std::cout << wdf.scenario; std::cout << " " << wdf.datetime; std::cout << " " << wdf.apcp;
	std::cout << " " << wdf.tmp; std::cout << " " << wdf.rh; std::cout << " " << wdf.ws;
	std::cout << " " << wdf.waz; std::cout << " " << wdf.ffmc; std::cout << " " << wdf.dmc;
	std::cout << " " << wdf.dc; std::cout << " " << wdf.isi; std::cout << " " << wdf.bui;
	std::cout << " " << wdf.fwi << std::endl;
}

/*
int main() {
	// Creating an object of CSVWriter
	CSVReader reader("/home/kotaro/workspace/Cell2Fire/Cell2Fire/data/Harvest40x40/Weathers/Weather947.csv");
 
	// Get the data from CSV File
  std::vector<std::vector<std::string> > dataList = reader.getData();

 	// Print the content of row by row on screen
	for(std::vector<std::string> vec : dataList)
	{
		for(std::string data : vec)
		{
			std::cout<<data<< " ";
		}
		std::cout<<std::endl;
	}
	return 0;
}
*/
