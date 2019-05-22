#ifndef CELLSFBP
#define CELLSFBP

// include stuff
#include "FBP5.0.h"
#include "ReadCSV.h"
#include "ReadArgs.h"
#include "Ellipse.h"

#include <stdio.h>
#include <math.h>
#include <unordered_map>
#include <unordered_set>
#include <string>
#include <vector>

using namespace std;

class CellsFBP {
    // TODO: find where to put the enums
    public:
        // immutable
        int id;
        int fType;
		int realId;
		double _ctr2ctrdist;							
		double area;
        double perimeter;
		
        std::string fType2;
        std::vector<int> coord; //maybe change this into a tuple or class	CP: 2-tuple (int)
		std::unordered_map<std::string, int> adjacents; // CP: dictionary {string: [int array]}
		
		string FTypeD[3];
        string StatusD[5];
		
		// mutable
        int status;
        int hPeriod;
        int fireStarts;
        int harvestStarts;
        int fireStartsSeason;
        int burntP;
        int tYears;	
		
        std::unordered_map<int, std::vector<int>> gMsgList; // {40 -> [1, 2, 3] }
		std::unordered_map<int, std::vector<int>> gMsgListSeason;
        std::unordered_map<int, double> fireProgress;	// CP: dictionary {int: double}
        std::unordered_map<int, double> angleDict;				// CP: dictionary {int: double}
        std::unordered_map<int, double> ROSAngleDir;       // CP: dictionary {int: double|None}   Instead of None we can use a determined number like -9999 = None  TODO: maybe int : double
        std::unordered_map<int, double> distToCenter;   	// CP: dictionary {int: double}
        std::unordered_map<int, int> angleToNb;			// CP: dictionary {double: int}

        // TODO: reference to shared object

        // constructor and methods here
        CellsFBP(int _id, double _area, std::vector<int> _coord, 
					 int _fType, std::string _fType2, double _perimeter, 
					 int _status, std::unordered_map<std::string, int> & _adjacents, 
					 int _realId);
        
		void initializeFireFields(std::vector<std::vector<int>> & coordCells, std::unordered_set<int> & availSet); // TODO: need TYPE
       
	    void ros_distr_old(double thetafire, double forward, double flank, double back);
		double rhoTheta(double theta, double a, double b);
		void ros_distr(double thetafire, double forward, double flank, double back, double EFactor);
		
        std::vector<int> manageFire(int period, std::unordered_set<int> & AvailSet,      
                                                          inputs * df, fuel_coefs * coef, 
														  std::vector<std::vector<int>> & coordCells, std::unordered_map<int, CellsFBP> & Cells_Obj, 
														  arguments * args, weatherDF * wdf_ptr, std::vector<double> * FSCell,
														  double randomROS);
		
		std::vector<int> manageFireBBO(int period, std::unordered_set<int> & AvailSet,      
															inputs * df_ptr, fuel_coefs * coef, 
															std::vector<std::vector<int>> & coordCells, std::unordered_map<int, CellsFBP> & Cells_Obj, 
															arguments * args, weatherDF * wdf_ptr, std::vector<double> * FSCell,
															double randomROS, std::vector<float> & EllipseFactors);
		
		bool get_burned(int period, int season, int NMsg, inputs df[],  fuel_coefs * coef, arguments * args, weatherDF * wdf_ptr) ;
								
		void set_Adj(std::unordered_map<std::string, int> & adjacentCells);
		
		void setStatus(int status_int);
		
		std::string getStatus();
		
		bool ignition(int period, int year, std::vector<int> & ignitionPoints, inputs * df_ptr,   // WORKING CHECK OK
						   fuel_coefs * coef, arguments *args, weatherDF * wdf_ptr);
						  
		void harvested(int id, int period);
		
		void print_info();
		
		
		
		
	private:
		double allocate(double offset, double base, double ros1, double ros2);
};

#endif
