#ifndef LIGHTNING
#define LIGHTNING

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

class Lightning {
    public:
		// Constructor & Methods
		Lightning();
        int Lambda_Simple_Test(int period);
        bool Lambda_NH(int period, bool verbose);
        bool Lambda_H(int period, bool verbose);
};

#endif
