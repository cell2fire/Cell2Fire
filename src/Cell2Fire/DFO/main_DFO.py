# coding: utf-8
__version__ = "1.0"
__author__ = "Cristobal Pais"

# Importations
import time
import numpy as np
import nlopt
from argparse import ArgumentParser
from Cell2Fire_DFO import Cell2Fire_Norm

# Main
if __name__ == "__main__":
    # Read args
    parser = ArgumentParser()
    parser.add_argument("--PathC",
                        help="Path to the main exe file (Cell2Fire Sim)",
                        dest="PathC",
                        type=str,
                        default=None)
    parser.add_argument("--OutFolder",
                        help="Path to the output folder (Cell2Fire Sim)",
                        dest="OutFolder",
                        type=str,
                        default=None)
    parser.add_argument("--PathScars",
                        help="Path to the original scar folder (Farsite/Real fire)",
                        dest="PathScars",
                        type=str,
                        default=None)
    parser.add_argument("--input-instance-folder",
                        help="Path to the instance folder (Cell2Fire Sim)",
                        dest="PathInstance",
                        type=str,
                        default=None)
    parser.add_argument('--BBOEllipticalFactors', nargs='+', 
                        help="Black box optimization SROS factors for Elliptical KitralSP (Surface Basal ROSs)",
                        type=float, 
                        dest="BBOEllipticalFactors",
                        default=np.ones(4))
    parser.add_argument("--ROS_Threshold",
                        help="SROS critical threshold (m/s) default 0.1.",
                        dest="ROS_Threshold",
                        type=float,
                        default=0.1)      
    parser.add_argument("--norm",
                        help="Norm for the fire scar function (Cell2Fire Sim)",
                        dest="normF",
                        type=str,
                        default="fro")
      
    parser.add_argument('--muWeights', nargs='+', 
                        help="Hour weights (per hour fire scar weight)",
                        type=float, 
                        dest="muWeights",
                        default=np.ones(10))
    parser.add_argument('--toTune', nargs='+', 
                        help="Components to tune, combination of: SROS, CriticalSROS, CROS, CriticalCROS, RTime, EllipticalROS",
                        type=str, 
                        dest="toTune",
                        default="")
      
    
    # Parse arguments
    args = parser.parse_args()
    
    # Flags (inside dictionary)
    TuningParams = {}
    LengthParams = np.zeros(6).astype(np.int32)
    
    # Filter adjustement parameters
    if len(args.toTune) > 0:
        # Sort toTune
        sortedTune = []
        if "CriticalSROS" in args.toTune:
            sortedTune.append("CriticalSROS")
        if "EllipticalROS" in args.toTune:
            sortedTune.append("EllipticalROS")
            
        # Initialize x
        x_0 = np.array([])
        for i in sortedTune:
            if i == "CriticalSROS":
                x_0 = np.concatenate((x_0, [args.ROS_Threshold]))
                TuningParams[i] = True
                LengthParams[0] = 1
                LengthParams[1] = LengthParams[0].copy()
            if i == "EllipticalROS":
                x_0 = np.concatenate((x_0, args.BBOEllipticalFactors))
                TuningParams[i] = True
                LengthParams[2] += 4            
    
    # Information
    print("TuningParams:", TuningParams)
    print("LengthParams:", LengthParams)
        
    # NLOPT package
    # Info
    print("Total parameters: 1 Critical SROS, 4 EllipticalROS")
    print("Tuning:", [k for k in TuningParams.keys()])
    print("X0:", x_0, "\nN:", len(x_0))
    time.sleep(2)

    # BOBYQA
    print("\n\n********* Function Cell2Fire  ********")
    alg = "BOBYQA"
    print("Algorithm:", alg)

    # Dimension
    n = len(x_0)                           
    opt = nlopt.opt(nlopt.LN_BOBYQA, n)

    # Bounds
    opt.set_lower_bounds(np.zeros(n))
    opt.set_upper_bounds(np.full(n, 10))

    # Objective
    opt.set_min_objective(lambda x, grad: Cell2Fire_Norm(x, grad, args.OutFolder, args.PathC, 
                                                           args.PathScars, args.PathInstance,
                                                           args.muWeights, args.normF,
                                                           TuningParams, LengthParams,
                                                           args.ROS_Threshold,
                                                           args.BBOEllipticalFactors))
    
    # Tolerance
    opt.set_xtol_abs(1e-10)
    #opt.set_xtol_rel(1e-26)
    
    # Time and optimization
    t1= time.time()
    x = opt.optimize(x_0)
    t2 = time.time()
    
    # Minimum fobj
    minf = opt.last_optimum_value()

    # Final results
    print ("\n")
    print ("---------- Results from BOBYQA -----------------")
    print("Optimum at:\t", x)
    print("Minimum obj. value:\t", minf)
    print("Number of evaluations:\t", opt.get_numevals())
    print("Total Runtime [s]:\t", t2-t1)
