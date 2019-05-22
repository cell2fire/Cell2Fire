// Include classes
#include "CellsFBP.h"
#include "SpottingFBP.h"
#include "FBP5.0.h"
#include "ReadCSV.h"
#include "ReadArgs.h"
#include "Ellipse.h"

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
//#define RAND_MAX 0.5

using namespace std;


/*
	Constructor   // WORKING CHECK OK
*/
CellsFBP::CellsFBP(int _id, double _area, std::vector<int> _coord,  
							int _fType, std::string _fType2, double _perimeter, 
							int _status, std::unordered_map<std::string, int> & _adjacents, 
							int _realId)
{
	// Global "dictionaries" (vectors) for status and types
	// Status: 0: "Available", 1: "Burning", 2: "Burnt", 3: "Harvested", 4:"Non Fuel"
	this->StatusD[0] = "Available";
	this->StatusD[1] = "Burning";
	this->StatusD[2] = "Burnt";
	this->StatusD[3] = "Harvested";
	this->StatusD[4] = "Non Fuel";
	
	// FTypeD: 0: "NonBurnable", 1: "Normal", 2: "Burnable
	this->FTypeD[0] = "NonBurnable";
	this->FTypeD[1] = "Normal";
	this->FTypeD[2] = "Burnable";
	
	// Initialize fields of the Cell object 
    this->id = _id;
    this->area = _area;
    this->coord = _coord;
    this->fType = _fType;
    this->fType2 = _fType2;
    this->perimeter = _perimeter;
    this->status = _status;
    this->adjacents = _adjacents;
    this->realId = _realId;
    this->_ctr2ctrdist = std::sqrt(this->area);

    if (std::abs(4 * this->_ctr2ctrdist - this->perimeter) > 0.01 * this->perimeter) {
        std::cerr << "Cell ID=" << this->id << "Area=" <<  this->area <<  "Perimeter=" <<  this->perimeter << std::endl;
        // maybe raise runtime error
    }
	
	// Inner fields
    this->gMsgList = std::unordered_map<int, std::vector<int>>();
    this->hPeriod = 0;

    this->fireStarts = 0;
    this->harvestStarts = 0;
    this->fireStartsSeason = 0;
    this->tYears = 4;
	
    this->gMsgListSeason = std::unordered_map<int, std::vector<int>>();
    this->fireProgress = std::unordered_map<int, double>();
    this->angleDict = std::unordered_map<int, double>();
    this->ROSAngleDir = std::unordered_map<int, double>();
    this->distToCenter = std::unordered_map<int, double>();
    this->angleToNb = std::unordered_map<int, int>();
}


/*
    Populates angles, distances, and initialize ROS per axis
    Modified by dlw to use cell area to compute distances in meters.
    ASSUME square fire cells.
    
    Returns        void
    
    Inputs:
    CoorCells      array of 2D int arrays
    AvailSet       int set
*/
void CellsFBP::initializeFireFields(std::vector<std::vector<int>> & coordCells,    // TODO: should probably make a coordinate type
												std::unordered_set<int> & availSet) 				// WORKING CHECK OK
{  
    for (auto & nb : this->adjacents) {
        // CP Default value is replaced: None = -1
		//std::cout << "DEBUG1: adjacent: " << nb.second << std::endl;
        if (nb.second != -1) {
            int a = -1 * coordCells[nb.second - 1][0] + coordCells[this->id][0];
            int b = -1 * coordCells[nb.second - 1][1] + coordCells[this->id][1];
            
            int angle = -1;
            if (a == 0) {
                if (b >= 0) 
                    angle = 270; 
                else 
                    angle = 90;
            }
            else if (b == 0) {
                if (a >= 0)
                    angle = 180;
                else
                    angle = 0;
            }
            else {
                // TODO: check this logi
                double radToDeg = 180 / M_PI;
                // TODO: i think all the negatives and abs cancel out
                double temp = std::atan(b * 1.0 / a) * radToDeg;
                if (a > 0)
                    temp += 180;
                if (a < 0 && b > 0) 
                    temp += 360;
                angle = temp;
            }

            this->angleDict[nb.second] = angle;
            if (availSet.find(nb.second) != availSet.end()) {
                // TODO: cannot be None, replaced None = -1   and ROSAngleDir has a double inside 
                this->ROSAngleDir[angle] = -1;
            }
            this->angleToNb[angle] = nb.second;
            this->fireProgress[nb.second] = 0.0;
            this->distToCenter[nb.second] = std::sqrt(a * a + b * b) * this->_ctr2ctrdist;
        }
    }
}

        
		
/*
    New functions for calculating the ROS based on the fire angles
	Distribute the rate of spread (ROS,ros) to the axes given in the AngleList.
    All angles are w.t.r. E-W with East positive and in non-negative degrees.
    Inputs:
            thetafire: direction of "forward"
            forward : forward ROS
            flank: ROS normal to forward (on both sides)
            back: ROS in the opposide direction of forward
            AngleList: List of angles for the axes connecting centers
                       of interest (might have less than 8 angles)
    Effect:
            Populate the ROSAngleDir, whose indexes are the angles,
            with ROS values.
        
	Returns       void
 */		
void CellsFBP::ros_distr_old(double thetafire, double forward, double flank, double back) {   // WORKING CHECK OK
    for (auto & angle : this->ROSAngleDir) {
        double offset = std::abs(angle.first - thetafire);
        
        double base = ((int)(offset)) / 90 * 90;
        double result;
		
		// Distribute ROS
		if (offset >= 0 && offset <= 90) {
            result = this->allocate(offset, 0, forward, flank);
        } else if (offset > 90 && offset < 180) {
            result = this->allocate(offset, 90, flank, back);
        } else if (offset >= 180 && offset <= 270) {
            result = this->allocate(offset, 180, back, flank);
        } else if (offset > 270 && offset < 360) {
            result = this->allocate(offset, 270, flank, forward);
        }
        this->ROSAngleDir[angle.first] = result;
    }	
}	


double CellsFBP::rhoTheta(double theta, double a, double b){
	const double pi = 3.141592653589793;
	
	double c2, e, r1, r2, r;
	
	c2 = std::pow(a, 2) - std::pow(b, 2);
	e = std::sqrt(c2) / a;
	
	r1 = a * (1 - std::pow(e, 2));
	r2 = 1 - e * std::cos(theta * pi / 180.0);
	r = r1 / r2;
	return r;
}

void CellsFBP::ros_distr(double thetafire, double forward, double flank, double back, double EFactor) {   // WORKING CHECK OK
    
	// Ellipse points 
	//std::cout << "Dentro de ROS dist" << std::endl;
	//std::cout << "thetafire:" << thetafire << std::endl;
	//std::cout << "forward:" << forward << std::endl;
	//std::cout << "flank:" << flank << std::endl;
	//std::cout << "back:" << back << std::endl;
	//std::cout << "EFactor:" << EFactor << std::endl;
	
	
	
	//std::cout << "Previo Data" << std::endl;
	double a = (forward + back) / 2;
	double b;
	std::vector<double> _x = {0.0, back, back, (forward + back) / 2., (forward + back) / 2., (forward + back)};
	std::vector<double> _y = {0.0, std::pow(flank, 2) / a, - (std::pow(flank, 2) / a), flank, -flank, 0.0};
	//std::cout << "Post data" << std::endl;
	
	// Fit the Ellipse
	//std::cout << "Previo Ellipse" << std::endl;
	Ellipse SqlEllipse(_x, _y);     // DEBUGGING
	//std::cout << "Inicializo" << std::endl;
	std::vector<double> params = SqlEllipse.get_parameters();
	a = params[0];
	b = params[1];
	
	//std::cout << "a:" << a << std::endl; 
	//std::cout << "b:" << b << std::endl; 
	
	// Ros allocation for each angle inside the dictionary
	for (auto & angle : this->ROSAngleDir) {
        double offset = angle.first - thetafire;
		
		if (offset < 0) {
            offset += 360;
        }
		if (offset > 360) {
            offset -= 360;
        }
        this->ROSAngleDir[angle.first] = rhoTheta(offset, a, b) * EFactor;
    }	
}			
		

/*
	Returns      double
	
	Inputs:
	offset       double
	base         double
	ros1         double
	ros2         double
*/	
double CellsFBP::allocate(double offset, double base, double ros1, double ros2) {   // WORKING CHECK OK
    double d = (offset - base) / 90;
    return (1 - d) * ros1 + d * ros2;
}


/*
    Returns           vect[integers]   Important: we are sending a True sometimes, pick a special value -x for replacing it
    
    Inputs:
    period            int
    AvailSet          int set
    verbose           boolean
    df                Data frame
    coef              pointer
    spotting          boolean
    SpottingParams    Data frame
    CoordCells        array of 2D doubles arrays
    Cells_Obj         dictionary of cells objects
*/
        
std::vector<int> CellsFBP::manageFire(int period, std::unordered_set<int> & AvailSet,      
                                                          inputs * df_ptr, fuel_coefs * coef, 
														  std::vector<std::vector<int>> & coordCells, std::unordered_map<int, CellsFBP> & Cells_Obj, 
														  arguments * args, weatherDF * wdf_ptr, std::vector<double> * FSCell,
														  double randomROS) 
	{
	// Special flag for repetition (False = -99 for the record)
	int repeat = -99;
	
    // msg lists contains integers (True = -100)
    std::vector<int> msg_list_aux;
	msg_list_aux.push_back(0);
    std::vector<int> msg_list;

	df_ptr->waz = wdf_ptr->waz;
	df_ptr->ws = wdf_ptr->ws;
	df_ptr->ffmc = wdf_ptr->ffmc;
	df_ptr->bui = wdf_ptr->bui;	
	
	// Compute main angle and ROSs: forward, flanks and back
    main_outs mainstruct;
    snd_outs sndstruct;
    fire_struc headstruct, backstruct, flankstruct;

	// Calculate parameters
	calculate(df_ptr, coef, &mainstruct, &sndstruct, &headstruct, &flankstruct, &backstruct);
	
	/*  ROSs DEBUG!   */
	if(args->verbose){
		std::cout << "*********** ROSs debug ************" << std::endl;
		std::cout <<  "-------Input Structure--------" << std::endl;
		std::cout <<  "fueltype: " << df_ptr->fueltype << std::endl;
		std::cout <<  "ffmc: " << df_ptr->ffmc << std::endl;
		std::cout <<  "ws: " << df_ptr->ws << std::endl;
		std::cout <<  "gfl: " << df_ptr->gfl << std::endl;
		std::cout <<  "bui: " << df_ptr->bui << std::endl;
		std::cout <<  "lat: " << df_ptr->lat << std::endl;
		std::cout <<  "lon: " << df_ptr->lon << std::endl;
		std::cout <<  "time: " << df_ptr->time << std::endl;
		std::cout <<  "pattern: " << df_ptr->pattern << std::endl;
		std::cout <<  "mon: " << df_ptr->mon << std::endl;
		std::cout <<  "jd: " << df_ptr->jd << std::endl;
		std::cout <<  "jd_min: " << df_ptr->jd_min << std::endl;
		std::cout <<  "waz: " << df_ptr->waz << std::endl;
		std::cout <<  "ps: " << df_ptr->ps << std::endl;
		std::cout <<  "saz: " << df_ptr->saz << std::endl;
		std::cout <<  "pc: " << df_ptr->pc << std::endl;
		std::cout <<  "pdf: " << df_ptr->pdf << std::endl;
		std::cout <<  "cur: " << df_ptr->cur << std::endl;
		std::cout <<  "elev: " << df_ptr->elev << std::endl;
		std::cout <<  "hour: " << df_ptr->hour << std::endl;
		std::cout <<  "hourly: " << df_ptr->hourly << std::endl;
		std::cout <<  "\n-------Mainout Structure--------" << std::endl;
		std::cout << "hffmc: " << mainstruct.hffmc << std::endl;
		std::cout << "sfc: " << mainstruct.sfc << std::endl;
		std::cout << "csi: " << mainstruct.csi << std::endl;
		std::cout << "rso: " << mainstruct.rso << std::endl;
		std::cout << "fmc: " << mainstruct.fmc << std::endl;
		std::cout << "sfi: " << mainstruct.sfi << std::endl;
		std::cout << "rss: " << mainstruct.rss << std::endl;
		std::cout << "isi:" << mainstruct.isi << std::endl;
		std::cout << "be:" << mainstruct.be << std::endl;
		std::cout << "sf:" << mainstruct.sf << std::endl;
		std::cout << "raz: " << mainstruct.raz << std::endl;
		std::cout << "wsv:" << mainstruct.wsv << std::endl;
		std::cout << "ff: " << mainstruct.ff << std::endl;
		std::cout << "jd_min:" << mainstruct.jd_min << std::endl;
		std::cout << "jd:" << mainstruct.jd << std::endl;
		std::cout << "covertype: " << mainstruct.covertype << std::endl;
		std::cout <<  "\n-------Headout Structure--------" << std::endl;
		std::cout <<  "ros: " << headstruct.ros * args->HFactor << std::endl;
		std::cout <<  "dist: " << headstruct.dist << std::endl;
		std::cout <<  "rost: " << headstruct.rost << std::endl;
		std::cout <<  "cfb: " << headstruct.cfb << std::endl;
		std::cout <<  "fc: " << headstruct.fc << std::endl;
		std::cout <<  "cfc: "<< headstruct.cfc << std::endl;
		std::cout <<  "time: " << headstruct.time << std::endl;
		std::cout <<  "rss: " << headstruct.rss << std::endl;
		std::cout <<  "isi: " << headstruct.isi << std::endl;
		std::cout <<  "fd: " << headstruct.fd << std::endl;
		std::cout <<  "fi: " << headstruct.fi << std::endl;
		std::cout <<  "\n------- Flank Structure--------" << std::endl;
		std::cout <<  "ros: " << flankstruct.ros * args->FFactor<< std::endl;
		std::cout <<  "dist: " << flankstruct.dist << std::endl;
		std::cout <<  "rost: " << flankstruct.rost << std::endl;
		std::cout <<  "cfb: " << flankstruct.cfb << std::endl;
		std::cout <<  "fc: " << flankstruct.fc << std::endl;
		std::cout <<  "cfc: "<< flankstruct.cfc << std::endl;
		std::cout <<  "time: " << flankstruct.time << std::endl;
		std::cout <<  "rss: " << flankstruct.rss << std::endl;
		std::cout <<  "isi: " << flankstruct.isi << std::endl;
		std::cout <<  "fd: " << flankstruct.fd << std::endl;
		std::cout <<  "fi: " << flankstruct.fi << std::endl;
		std::cout <<  "\n------- Back Structure--------" << std::endl;
		std::cout <<  "ros: " << backstruct.ros * args->BFactor << std::endl;
		std::cout <<  "dist: " << backstruct.dist << std::endl;
		std::cout <<  "rost: " << backstruct.rost << std::endl;
		std::cout <<  "cfb: " << backstruct.cfb << std::endl;
		std::cout <<  "fc: " << backstruct.fc << std::endl;
		std::cout <<  "cfc: "<< backstruct.cfc << std::endl;
		std::cout <<  "time: " << backstruct.time << std::endl;
		std::cout <<  "rss: " << backstruct.rss << std::endl;
		std::cout <<  "isi: " << backstruct.isi << std::endl;
		std::cout <<  "fd: " << backstruct.fd << std::endl;
		std::cout <<  "fi: " << backstruct.fi << std::endl;
		std::cout << "*********** ROSs debug ************" << std::endl;
	}
	/*                         */
	
    double cartesianAngle = 270 - mainstruct.raz; //                 - 90;   // CHECK!!!!!
	if (cartesianAngle < 0){
		cartesianAngle += 360;
	} 
	 
    double ROSRV = 0;
    if (args->ROSCV > 0) {
	    //std::srand(args->seed);
		//std::default_random_engine generator(args->seed);
		//std::normal_distribution<double> distribution(0.0,1.0);
		ROSRV = randomROS;
	}
	

	// Display if verbose True (FBP ROSs, Main angle, and ROS std (if included))
    if (args->verbose) {
        std::cout << "Main Angle (raz): " << mainstruct.raz  << " Cartesian: " << cartesianAngle << std::endl;
        std::cout << "FBP Front ROS Value: " << headstruct.ros * args->HFactor << std::endl; 
        std::cout << "FBP Flanks ROS Value: " << flankstruct.ros * args->FFactor << std::endl;
        std::cout <<  "FBP Rear ROS Value: " << backstruct.ros * args->BFactor << std::endl;
        std::cout << "Std Normal RV for Stochastic ROS CV: " << ROSRV << std::endl;
    }

	// If cell cannot send (thresholds), then it will be burned out in the main loop
    double HROS = (1 + args->ROSCV * ROSRV) * headstruct.ros * args->HFactor;
    	
	// Extra debug step for sanity checks
	if (args->verbose){
            std::cout << "\nSending message conditions" << std::endl;
            std::cout << "HROS: " << HROS << " Threshold: "<<  args->ROSThreshold << std::endl;
            std::cout << "HeadStruct FI: " << headstruct.fi << " Threshold: " << args->HFIThreshold << std::endl;
	}
	
    // Check thresholds for sending messages	
    if (HROS > args->ROSThreshold && headstruct.fi > args->HFIThreshold) {
        // True = -100
		repeat = -100;	
		
		if (args->verbose) {
            std::cout << "\nRepeat condition: " << repeat << std::endl;
            std::cout << "Cell can send messages" << std::endl;
        }
        
		// ROS distribution method
        //ros_distr(mainstruct.raz,  headstruct.ros, flankstruct.ros, backstruct.ros);
		//std::cout << "Entra a Ros Dist" << std::endl;
		ros_distr(cartesianAngle,  
					  headstruct.ros * args->HFactor, 
					  flankstruct.ros * args->FFactor, 
					  backstruct.ros * args->BFactor,
					  args->EFactor);
        //std::cout << "Sale de Ros Dist" << std::endl;		
		
		// Fire progress using ROS from burning cell, not the neighbors //
       // vector<double> toPop = vector<double>();
        
		// this is a iterator through the keyset of a dictionary
        for (auto&  _angle : this->ROSAngleDir) {
            double angle = _angle.first;
            int nb = angleToNb[angle];
            double ros = (1 + args->ROSCV * ROSRV) * _angle.second;
			
			if(std::isnan(ros)){
				ros = 1e-4;
			}
			
            if (args->verbose) {
                std::cout << "     (angle, realized ros in m/min): (" << angle << ", " << ros << ")" << std::endl;
            }
			            
			// Workaround PeriodLen in 60 minutes
            this->fireProgress[nb] += ros * args->FirePeriodLen;   // Updates fire progress
		
		    // If the message arrives to the adjacent cell's center, send a message
            if (this->fireProgress[nb] >= this->distToCenter[nb]) {
                msg_list.push_back(nb);
				FSCell->push_back(double(this->realId));
				FSCell->push_back(double(nb));
				FSCell->push_back(double(period));
				FSCell->push_back(ros);
                // cannot mutate ROSangleDir during iteration.. we do it like 10 lines down
               // toPop.push_back(angle);
                /*if (verbose) {
                    //fill out this verbose section
                    std::cout << "MSG list" << msg_list << std::endl;
                }*/
            }    
        
			// Info for debugging status of the cell and fire evolution			
			if (this->fireProgress[nb] < this->distToCenter[nb] && repeat == -100 && -100  != msg_list_aux[0]){
                    if (args->verbose){
                        std::cout << "A Repeat = TRUE flag is sent in order to continue with the current fire....." << std::endl;
                        std::cout << "Main workaround of the new sim logic....." << std::endl;
					}
                    msg_list_aux[0] = repeat;
			}
						
		}
		
		if (args->verbose){
			printf("fireProgress Dict: ");
			for (auto & nb : this->fireProgress){
				std::cout << " " << nb.first << " : " << nb.second;
			}
			std::cout << std::endl;
		}
    }
	
	
	// If original is empty (no messages but fire is alive if aux_list is not empty)
	if  (msg_list.size() == 0){
		if (msg_list_aux[0] == -100){
			msg_list = msg_list_aux;
		}
	
		else{
			this->status = 2;   // we are done sending messages, call us burned
		}
	}
				
    if (args->verbose){
		std::cout << " ----------------- End of new manageFire function -----------------" << std::endl;
	}
    return msg_list;
}
    
		

/*

	Manage fire for BBO tuning version 
	
*/

std::vector<int> CellsFBP::manageFireBBO(int period, std::unordered_set<int> & AvailSet,      
																  inputs * df_ptr, fuel_coefs * coef, 
																  std::vector<std::vector<int>> & coordCells, std::unordered_map<int, CellsFBP> & Cells_Obj, 
																  arguments * args, weatherDF * wdf_ptr, std::vector<double> * FSCell,
																  double randomROS, std::vector<float> & EllipseFactors) 
	{
	// Special flag for repetition (False = -99 for the record)
	int repeat = -99;
	
    // msg lists contains integers (True = -100)
    std::vector<int> msg_list_aux;
	msg_list_aux.push_back(0);
    std::vector<int> msg_list;

	df_ptr->waz = wdf_ptr->waz;
	df_ptr->ws = wdf_ptr->ws;
	df_ptr->ffmc = wdf_ptr->ffmc;
	df_ptr->bui = wdf_ptr->bui;	
	
	// Compute main angle and ROSs: forward, flanks and back
    main_outs mainstruct;
    snd_outs sndstruct;
    fire_struc headstruct, backstruct, flankstruct;

	// Calculate parameters
	calculate(df_ptr, coef, &mainstruct, &sndstruct, &headstruct, &flankstruct, &backstruct);
	
	/*  ROSs DEBUG!   */
	if(args->verbose){
		std::cout << "*********** ROSs debug ************" << std::endl;
		std::cout <<  "-------Input Structure--------" << std::endl;
		std::cout <<  "fueltype: " << df_ptr->fueltype << std::endl;
		std::cout <<  "ffmc: " << df_ptr->ffmc << std::endl;
		std::cout <<  "ws: " << df_ptr->ws << std::endl;
		std::cout <<  "gfl: " << df_ptr->gfl << std::endl;
		std::cout <<  "bui: " << df_ptr->bui << std::endl;
		std::cout <<  "lat: " << df_ptr->lat << std::endl;
		std::cout <<  "lon: " << df_ptr->lon << std::endl;
		std::cout <<  "time: " << df_ptr->time << std::endl;
		std::cout <<  "pattern: " << df_ptr->pattern << std::endl;
		std::cout <<  "mon: " << df_ptr->mon << std::endl;
		std::cout <<  "jd: " << df_ptr->jd << std::endl;
		std::cout <<  "jd_min: " << df_ptr->jd_min << std::endl;
		std::cout <<  "waz: " << df_ptr->waz << std::endl;
		std::cout <<  "ps: " << df_ptr->ps << std::endl;
		std::cout <<  "saz: " << df_ptr->saz << std::endl;
		std::cout <<  "pc: " << df_ptr->pc << std::endl;
		std::cout <<  "pdf: " << df_ptr->pdf << std::endl;
		std::cout <<  "cur: " << df_ptr->cur << std::endl;
		std::cout <<  "elev: " << df_ptr->elev << std::endl;
		std::cout <<  "hour: " << df_ptr->hour << std::endl;
		std::cout <<  "hourly: " << df_ptr->hourly << std::endl;
		std::cout <<  "\n-------Mainout Structure--------" << std::endl;
		std::cout << "hffmc: " << mainstruct.hffmc << std::endl;
		std::cout << "sfc: " << mainstruct.sfc << std::endl;
		std::cout << "csi: " << mainstruct.csi << std::endl;
		std::cout << "rso: " << mainstruct.rso << std::endl;
		std::cout << "fmc: " << mainstruct.fmc << std::endl;
		std::cout << "sfi: " << mainstruct.sfi << std::endl;
		std::cout << "rss: " << mainstruct.rss << std::endl;
		std::cout << "isi:" << mainstruct.isi << std::endl;
		std::cout << "be:" << mainstruct.be << std::endl;
		std::cout << "sf:" << mainstruct.sf << std::endl;
		std::cout << "raz: " << mainstruct.raz << std::endl;
		std::cout << "wsv:" << mainstruct.wsv << std::endl;
		std::cout << "ff: " << mainstruct.ff << std::endl;
		std::cout << "jd_min:" << mainstruct.jd_min << std::endl;
		std::cout << "jd:" << mainstruct.jd << std::endl;
		std::cout << "covertype: " << mainstruct.covertype << std::endl;
		std::cout <<  "\n-------Headout Structure--------" << std::endl;
		std::cout <<  "ros: " << headstruct.ros * args->HFactor << std::endl;
		std::cout <<  "dist: " << headstruct.dist << std::endl;
		std::cout <<  "rost: " << headstruct.rost << std::endl;
		std::cout <<  "cfb: " << headstruct.cfb << std::endl;
		std::cout <<  "fc: " << headstruct.fc << std::endl;
		std::cout <<  "cfc: "<< headstruct.cfc << std::endl;
		std::cout <<  "time: " << headstruct.time << std::endl;
		std::cout <<  "rss: " << headstruct.rss << std::endl;
		std::cout <<  "isi: " << headstruct.isi << std::endl;
		std::cout <<  "fd: " << headstruct.fd << std::endl;
		std::cout <<  "fi: " << headstruct.fi << std::endl;
		std::cout <<  "\n------- Flank Structure--------" << std::endl;
		std::cout <<  "ros: " << flankstruct.ros * args->FFactor<< std::endl;
		std::cout <<  "dist: " << flankstruct.dist << std::endl;
		std::cout <<  "rost: " << flankstruct.rost << std::endl;
		std::cout <<  "cfb: " << flankstruct.cfb << std::endl;
		std::cout <<  "fc: " << flankstruct.fc << std::endl;
		std::cout <<  "cfc: "<< flankstruct.cfc << std::endl;
		std::cout <<  "time: " << flankstruct.time << std::endl;
		std::cout <<  "rss: " << flankstruct.rss << std::endl;
		std::cout <<  "isi: " << flankstruct.isi << std::endl;
		std::cout <<  "fd: " << flankstruct.fd << std::endl;
		std::cout <<  "fi: " << flankstruct.fi << std::endl;
		std::cout <<  "\n------- Back Structure--------" << std::endl;
		std::cout <<  "ros: " << backstruct.ros * args->BFactor << std::endl;
		std::cout <<  "dist: " << backstruct.dist << std::endl;
		std::cout <<  "rost: " << backstruct.rost << std::endl;
		std::cout <<  "cfb: " << backstruct.cfb << std::endl;
		std::cout <<  "fc: " << backstruct.fc << std::endl;
		std::cout <<  "cfc: "<< backstruct.cfc << std::endl;
		std::cout <<  "time: " << backstruct.time << std::endl;
		std::cout <<  "rss: " << backstruct.rss << std::endl;
		std::cout <<  "isi: " << backstruct.isi << std::endl;
		std::cout <<  "fd: " << backstruct.fd << std::endl;
		std::cout <<  "fi: " << backstruct.fi << std::endl;
		std::cout << "*********** ROSs debug ************" << std::endl;
	}
	/*                         */
	
    double cartesianAngle = 270 - mainstruct.raz; //                 - 90;   // CHECK!!!!!
	if (cartesianAngle < 0){
		cartesianAngle += 360;
	} 
	 
    double ROSRV = 0;
    if (args->ROSCV > 0) {
	    //std::srand(args->seed);
		//std::default_random_engine generator(args->seed);
		//std::normal_distribution<double> distribution(0.0,1.0);
		ROSRV = randomROS;
	}
	

	// Display if verbose True (FBP ROSs, Main angle, and ROS std (if included))
    if (args->verbose) {
        std::cout << "Main Angle (raz): " << mainstruct.raz  << " Cartesian: " << cartesianAngle << std::endl;
        std::cout << "FBP Front ROS Value: " << headstruct.ros * EllipseFactors[0] << std::endl; 
        std::cout << "FBP Flanks ROS Value: " << flankstruct.ros * EllipseFactors[1] << std::endl;
        std::cout <<  "FBP Rear ROS Value: " << backstruct.ros * EllipseFactors[2] << std::endl;
        std::cout << "Std Normal RV for Stochastic ROS CV: " << ROSRV << std::endl;
    }

	// If cell cannot send (thresholds), then it will be burned out in the main loop
    double HROS = (1 + args->ROSCV * ROSRV) * headstruct.ros * EllipseFactors[0];
    	
	// Extra debug step for sanity checks
	if (args->verbose){
            std::cout << "\nSending message conditions" << std::endl;
            std::cout << "HROS: " << HROS << " Threshold: "<<  args->ROSThreshold << std::endl;
            std::cout << "HeadStruct FI: " << headstruct.fi << " Threshold: " << args->HFIThreshold << std::endl;
	}
	
    // Check thresholds for sending messages	
    if (HROS > args->ROSThreshold && headstruct.fi > args->HFIThreshold) {
        // True = -100
		repeat = -100;	
		
		if (args->verbose) {
            std::cout << "\nRepeat condition: " << repeat << std::endl;
            std::cout << "Cell can send messages" << std::endl;
        }
        
		// ROS distribution method
        //ros_distr(mainstruct.raz,  headstruct.ros, flankstruct.ros, backstruct.ros);
		//std::cout << "Entra a Ros Dist" << std::endl;
		ros_distr(cartesianAngle,  
					  headstruct.ros * EllipseFactors[0], 
					  flankstruct.ros * EllipseFactors[1], 
					  backstruct.ros * EllipseFactors[2],
					  EllipseFactors[3]);
        //std::cout << "Sale de Ros Dist" << std::endl;		
		
		// Fire progress using ROS from burning cell, not the neighbors //
       // vector<double> toPop = vector<double>();
        
		// this is a iterator through the keyset of a dictionary
        for (auto&  _angle : this->ROSAngleDir) {
            double angle = _angle.first;
            int nb = angleToNb[angle];
            double ros = (1 + args->ROSCV * ROSRV) * _angle.second;
			
            if (args->verbose) {
                std::cout << "     (angle, realized ros in m/min): (" << angle << ", " << ros << ")" << std::endl;
            }
			            
			// Workaround PeriodLen in 60 minutes
            this->fireProgress[nb] += ros * args->FirePeriodLen;   // Updates fire progress
		
		    // If the message arrives to the adjacent cell's center, send a message
            if (this->fireProgress[nb] >= this->distToCenter[nb]) {
                msg_list.push_back(nb);
				FSCell->push_back(double(this->realId));
				FSCell->push_back(double(nb));
				FSCell->push_back(double(period));
				FSCell->push_back(ros);
                // cannot mutate ROSangleDir during iteration.. we do it like 10 lines down
               // toPop.push_back(angle);
                /*if (verbose) {
                    //fill out this verbose section
                    std::cout << "MSG list" << msg_list << std::endl;
                }*/
            }    
        
			// Info for debugging status of the cell and fire evolution			
			if (this->fireProgress[nb] < this->distToCenter[nb] && repeat == -100 && -100  != msg_list_aux[0]){
                    if (args->verbose){
                        std::cout << "A Repeat = TRUE flag is sent in order to continue with the current fire....." << std::endl;
                        std::cout << "Main workaround of the new sim logic....." << std::endl;
					}
                    msg_list_aux[0] = repeat;
			}
						
		}
		
		if (args->verbose){
			printf("fireProgress Dict: ");
			for (auto & nb : this->fireProgress){
				std::cout << " " << nb.first << " : " << nb.second;
			}
			std::cout << std::endl;
		}
    }
	
	
	// If original is empty (no messages but fire is alive if aux_list is not empty)
	if  (msg_list.size() == 0){
		if (msg_list_aux[0] == -100){
			msg_list = msg_list_aux;
		}
	
		else{
			this->status = 2;   // we are done sending messages, call us burned
		}
	}
				
    if (args->verbose){
		std::cout << " ----------------- End of new manageFire function -----------------" << std::endl;
	}
    return msg_list;
}
    


		
/*
    Get burned new logic: Checks if the ROS on its side is above a threshold for burning
	
	Returns     boolean  
    
    Inputs:
    period      int
    NMsg        int
    Season      int
    verbose     boolean
    df          Data frame
    coef        pointer
    ROSThresh   double
 */
	
bool CellsFBP::get_burned(int period, int season, int NMsg, inputs df[],  fuel_coefs * coef, arguments * args, weatherDF * wdf_ptr) {
    if (args->verbose) { 
        std::cout << "ROS Threshold get_burned method" << std::endl;
		std::cout << "ROSThreshold: " << args->ROSThreshold << std::endl;
    }

	// Structures
    main_outs mainstruct;
    snd_outs sndstruct;
    fire_struc headstruct, backstruct, flankstruct;

	// Compute main angle and ROSs: forward, flanks and back
	df[this->id].waz = wdf_ptr->waz;
	df[this->id].ws = wdf_ptr->ws;
	df[this->id].ffmc = wdf_ptr->ffmc;
	df[this->id].bui = wdf_ptr->bui;	
    calculate(&(df[this->id]), coef, &mainstruct, &sndstruct, &headstruct, &flankstruct, &backstruct);

    if (args->verbose) { 
		std::cout << "\nMain Angle :" << mainstruct.raz << std::endl;
		std::cout << "Front ROS Value :" << headstruct.ros * args->HFactor << std::endl;
		std::cout << "Flanks ROS Value :" << flankstruct.ros * args->FFactor << std::endl;
		std::cout << "Rear ROS Value :" << backstruct.ros * args->BFactor << std::endl;
	}
    
	// Check a threshold for the ROS
    if (headstruct.ros  * args->HFactor > args->ROSThreshold) {
        this->status = 1;
        this->fireStarts = period;
        this->fireStartsSeason = season;
        this->burntP = period;
        return true;
    }
    // Not burned
    return false; 
}


		
/* Old functions
    Returns            void
    
    Inputs:  
    AdjacentCells      dictionary{string:[array integers]}
*/
void CellsFBP::set_Adj(std::unordered_map<std::string, int> & adjacentCells) {   // WORKING CHECK OK
    // TODO: in python, these are pointers, maybe make these pointers too :P
    this->adjacents = adjacentCells;
}


/* 
    Returns            void
    
    Inputs:  
    Status_int         int
*/
void CellsFBP::setStatus(int status_int) {   // WORKING CHECK OK
    this->status = status_int;
}


/*
    Returns            string
    
    Inputs:  
*/
std::string CellsFBP::getStatus() {		// WORKING CHECK OK
    // Return cell's status
    return this->StatusD[this->status];
}

		
/*
    Returns           boolean
    
    Inputs:
    period            int
    Season            int
    IgnitionPoints    array of int
    df                Data frame
    coef              pointer
    ROSThresh         double
    HFIThreshold      double
 */
bool CellsFBP::ignition(int period, int year, std::vector<int> & ignitionPoints, inputs * df_ptr,   // WORKING CHECK OK
								 fuel_coefs * coef, arguments *args, weatherDF * wdf_ptr) {
    
	// If we have ignition points, update
    if (ignitionPoints.size() > 0) {
        this->status = 1;
        this->fireStarts = period;
        this->fireStartsSeason = year;
        this->burntP = period;

		// An ignition has happened
        return true;
    } else {
        // Ignites if implied head ros andfire intensity are high enough
        main_outs mainstruct;
        snd_outs sndstruct;
        fire_struc headstruct, backstruct, flankstruct;

		//printf("\nWeather inside ignition:\n");
		//std::cout << "waz: " << wdf_ptr->waz << "  ffmc: " <<    wdf_ptr->ffmc << "  bui: " <<   wdf_ptr->bui << std::endl;
		
		df_ptr->waz = wdf_ptr->waz;
		df_ptr->ws = wdf_ptr->ws;
		df_ptr->ffmc = wdf_ptr->ffmc;
		df_ptr->bui = wdf_ptr->bui;	
			
        calculate(df_ptr, coef, &mainstruct, &sndstruct, &headstruct, &flankstruct, &backstruct);

        if (args->verbose) {
			std::cout << "\nIn ignition function" << std::endl;
			std::cout << "Main Angle: " << mainstruct.raz << std::endl;
			std::cout << "Front ROS Value: " << headstruct.ros * args->HFactor << std::endl;
			std::cout << "Flanks ROS Value: " << flankstruct.ros * args->FFactor << std::endl;
			std::cout << "Rear ROS Value: " << backstruct.ros * args->BFactor << std::endl;
        }
		
		// Check a threshold for the ROS
        if (headstruct.ros * args->HFactor > args->ROSThreshold && headstruct.fi > args->HFIThreshold) {
            if (args->verbose) {
                std::cout << "Head (ROS, FI) values of: (" << headstruct.ros * args->HFactor<< ", " << headstruct.fi  <<  ") are enough for ignition" << std::endl;
            }

            this->status = 1;
            this->fireStarts = period;
            this->fireStartsSeason = year;
            this->burntP = period;

            return true;
        }
        return false;
    }
}		
		
		
		
/*
    Returns      void
    Inputs
    ID           int
    period       int
*/
void CellsFBP::harvested(int id, int period) {     // WORKING CHECK OK
    // TODO: unused param
    this->status = 3;
    this->harvestStarts = period;
}



/*
    Returns      void
*/
void CellsFBP::print_info() {    // WORKING CHECK OK
	std::cout << "Cell Information" << std::endl;
	std::cout << "ID = "  << this->id<< std::endl;
	std::cout << "In Forest ID = "  << this->realId<< std::endl;
    std::cout << "Status = " << this->StatusD[this->status] << std::endl;
    std::cout << "Coordinates: ";
	std::cout << this->coord[0] <<  " " << this->coord[1]  << std::endl;
	
	std::cout << "Area = "<<  this->area << std::endl;
    std::cout << "FTypes = "<< this->FTypeD[this->fType] << std::endl;
    std::cout << "AdjacentCells:";
	for (auto & nb : this->adjacents){
		std::cout << " " << nb.first << ":" << nb.second;
	}
	std::cout << std::endl;
	
	printf("Angle Dict: ");
	for (auto & nb : this->angleDict){
		std::cout << " " << nb.first << " : " << nb.second;
	}
	std::cout << std::endl;
	
	printf("Ros Angle Dict: ");
	for (auto & nb : this->ROSAngleDir){
		std::cout << " " << nb.first << " : " << nb.second;
	}
	std::cout << std::endl;
	
	
	printf("angleToNb Dict: ");
	for (auto & nb : this->angleToNb){
		std::cout << " " << nb.first << " : " << nb.second;
	}
	std::cout << std::endl;
	
	
	printf("fireProgress Dict: ");
	for (auto & nb : this->fireProgress){
		std::cout << " " << nb.first << " : " << nb.second;
	}
	std::cout << std::endl;
	
	
	printf("distToCenter Dict: ");
	for (auto & nb : this->distToCenter){
		std::cout << " " << nb.first << " : " << nb.second;
	}
	std::cout << std::endl;
}


