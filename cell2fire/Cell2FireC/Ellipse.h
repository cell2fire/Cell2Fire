#ifndef ELLIPSE
#define ELLIPSE

// include stuff
#include <stdio.h>
#include <math.h>
#include <unordered_map>
#include <unordered_set>
#include <string>
#include <vector>
#include <Eigen/Dense>

using namespace Eigen;
using namespace std;

class Ellipse {
    public:
        // mutable
        double _a;
        double _b;
		ArrayXXd _Coef;
		
        // constructor and methods here
        Ellipse(std::vector<double> _x, std::vector<double> _y);
		std::vector<double> get_parameters();
};

#endif
