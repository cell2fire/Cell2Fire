// Include classes
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
#include <Eigen/Dense>

#define no_argument 0
#define required_argument 1 
#define optional_argument 2

using namespace Eigen;
using namespace std;


/*
	Constructor   
*/
Ellipse::Ellipse(std::vector<double> _x, std::vector<double> _y)
{
	// Aux integers
	int i,j;
	int N =  _x.size();
	
	// Initialize Arrays and Matrices 
	ArrayXXd X(1,N);
	ArrayXXd Y(1,N);
	ArrayXXd D1(N,3);
	ArrayXXd D2(N,3);
	ArrayXXd S1(3,3);
	ArrayXXd S2(3,3);
	ArrayXXd S3(3,3);
	ArrayXXd C1 = ArrayXXd::Zero(3,3);
	ArrayXXd M(3,3);
	VectorXd Eval(3,1);
	MatrixXd Evec(3,3);
	ArrayXXd cond(3,1);
	ArrayXXd Coef(1,N);
	
	// Print input vectors (debug)
	for (i = 0; i < N; i++){
		X(i) = _x[i];
		Y(i) = _y[i];
	}	
	//std::cout << "X:" << X << //std::endl;
	//std::cout << "Y:" << Y << //std::endl;
	
	//Quadratic part of design matrix [eqn. 15] from (*)
    D1.col(0) = X.pow(2).transpose();
	D1.col(1) = (X * Y).transpose();
	D1.col(2) = Y.pow(2).transpose();
    //std::cout << "D1:" << D1 << //std::endl;
    
	// Linear part of design matrix [eqn. 16] from (*)
    D2.col(0) = X.transpose(); 
	D2.col(1) = Y.transpose();
	D2.col(2) = ArrayXXd::Constant(N,1,1);
    //std::cout << "D2:" << D2 << //std::endl;
	
    // Forming scatter matrix [eqn. 17] from (*)
	S1 = D1.matrix().transpose() * D1.matrix();
	S2 = D1.matrix().transpose() * D2.matrix();
	S3 = D2.matrix().transpose() * D2.matrix();
	
	//std::cout << "S1:" << S1 << //std::endl;
	//std::cout << "S2:" << S2 << //std::endl;
	//std::cout << "S3:" << S3 << //std::endl;

    // Constraint matrix [eqn. 18]
    C1(0,2) = 2;
	C1(1,1) = -1;
	C1(2,0) = 2;
    //std::cout << "C1:" << C1 << //std::endl;
        
    //Reduced scatter matrix [eqn. 29]
	M = C1.matrix().inverse()*(S1.matrix() - S2.matrix() * S3.matrix().inverse() * S2.matrix().transpose());
	EigenSolver<MatrixXd> M2(M.matrix());
	
	//M*|a b c >=l|a b c >. Find eigenvalues and eigenvectors from this equation [eqn. 28]
    Eval = M2.eigenvalues().real();
	Evec = M2.eigenvectors().real();
	
	//std::cout << "Eval:" << Eval << //std::endl;
	//std::cout << "Evec:" << Evec << //std::endl;
        
    // Eigenvector must meet constraint 4ac - b^2 to be valid.
	cond = 4 * Evec.row(0).array() * Evec.row(2).array()  - Evec.row(1).array().pow(2);
	//std::cout << "cond:" << cond << //std::endl;
	//std::cout << "Check condition:" << (cond > 0) << //std::endl;
	
	int TotalCols = 0;
	int auxCol = 0;
	for (i=0; i < cond.size(); i++){
		if (cond(i) > 0){
			TotalCols++;
		}
	}
	//std::cout << "Total Cols:" << TotalCols << //std::endl;
	
	ArrayXXd a1(3, TotalCols);
	for (i=0; i < cond.size(); i++){
		if (cond(i) > 0){
			a1.col(auxCol) = Evec.col(i);
			auxCol++;
			//std::cout << "Adde column:" << i+1 << //std::endl;
		}
	}
	
	//std::cout << "a1:" << a1 << //std::endl;
	
	//|d f g> = -S3^(-1)*S2^(T)*|a b c> [eqn. 24]
	MatrixXd a2 = -S3.matrix().inverse() *S2.matrix().transpose() * a1.matrix();
    //std::cout << "a2:" << a2 << //std::endl;
    
	// eigenvectors |a b c d f g> 	
	for (i=0; i<6; i++){	
		if (i<3) Coef(i) = a1(i);
		else Coef(i) = a2(i-3);
	}
	
	//std::cout << "Coef:" << Coef << //std::endl;
	this->_Coef = Coef; 
}

std::vector<double> Ellipse::get_parameters(){
	std::vector<double> params;
	 double a,b,c,d,f,g;
	 
	 a = this->_Coef(0);
 	 b = this->_Coef(1) / 2;
	 c = this->_Coef(2);
	 d = this->_Coef(3) / 2;
	 f = this->_Coef(4) / 2;
	 g = this->_Coef(5);
        
    // finding center of ellipse [eqn.19 and 20] from (**)
    double x0 = (c*d - b*f) / (std::pow(b,2) - a*c);
    double y0 = (a*f - b*d) / (std::pow(b,2) - a*c);
        
    //Find the semi-axes lengths [eqn. 21 and 22] from (**)
	double numerator = 2*(a*f*f+c*d*d+g*b*b-2*b*d*f-a*c*g);
	double denominator1 = (b*b-a*c)*( (c-a)*std::sqrt(1+4*b*b/((a-c)*(a-c)))-(c+a));
	double denominator2 = (b*b-a*c)*( (a-c)*std::sqrt(1+4*b*b/((a-c)*(a-c)))-(c+a));
	double width = std::sqrt(numerator / denominator1);
	double height = std::sqrt(numerator / denominator2);
	
	// angle of counterclockwise rotation of major-axis of ellipse to x-axis [eqn. 23] from (**) or [eqn. 26] from (***).
    this->_a = width;
	this->_b = height;
	params.push_back(width);
	params.push_back(height);
	return params;
}