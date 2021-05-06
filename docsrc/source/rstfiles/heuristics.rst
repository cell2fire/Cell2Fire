Heuristics
==========

Cell2Fire includes built-in heristics to use as benchmarks.


A Simple Example
----------------


Input Command:

::

    python ${C2LOC}/main.py --input-instance-folder ${C2LOC}/../data/Sub20x20/ --output-folder ${THISLOC}/results/Sub20x20/Sub20_RW_RI_N10 --sim-years 1 --nsims 10 --finalGrid --weather random --nweathers 100 --Fire-Period-Length 1.0 --ROS-CV 0.0 --seed 123 --IgnitionRad 0 --stats --output-messages --ROS-Threshold 0 --HFI-Threshold 0 --heuristic 1

Output:

A List of Heuristics
--------------------

Currently, the heuristics (greedy based) are executed for a hard-coded interval of treatment fraction, i.e., varying the total number of nodes to be treated by 5%, starting from 0% (no treatment) to 90% of the available cells. If a valid argument is provided, Cell2Fire simulates nsim fires, gathers statistics and useful information for the metrics, simulates nsim fires with the treatment plan provided by the heuristic, and finally, provides an evaluation of the treatment plan’s performance.
In parenthesis the number of the heuristic associated with the --heuristic argument (--heuristic -1 indicates that no heuristic is applied).


*	Random (0): Selects available cells at random until the treatment fraction threshold is hit (e.g., 10% of the available cells)
*	Random_Adj (1): Idem as above but satisfying adjacency constraints by selecting cells at random connected to the previous ones.
*	Max_Utility (2): Given a utility map with a value for each cell (.csv file, see customValue argument), it selects those cells that maximize the total utility.
*	Max_Utility_Adj (3): Idem but satisfying adjacency constraints (greedy)
*	Burnt_Probability (4): Selects those cells with higher burn probability based on the previous simulations.
*	Burnt_Probability_Adj (5): Idem but satisfying adjacency constraints (greedy)
*	FPV_Palma (6): Calculates the fire protection value from Palma et. al and selects those cells that maximize the total sum of the selection (slow, not recommended)
*	FPV_Palma_Adj (7): Idem but satisfying adjacency constraints (greedy)
*	DPV_VaR_Volume (8): Calculates the downstream protection value metric using the volume/provided utility per cell as the VaR to protect. Selects the cells of the forest that maximize the total summation of the metric.
*	DPV_VaR_Volume_Adj (9): Idem but satisfying adjacency constraints (greedy)
*	DPV_VaR_Volume_Degree (10): Idem as (8) but weighting the metric by the degree of the node.
*	DPV_VaR_Volume_Degree_Adj (11): Idem but satisfying adjacency constraints (greedy)
*	DPV_VaR_Volume_Degree_Time (12): Experimental. Adds a time factor weighting the metric by the ROS of the fire.
*	DPV_VaR_Volume_Degree_Time_Adj (13): Idem but satisfying adjacency constraints (greedy)
*	DPV_VaR_Volume_Degree_Time_Layer_decay (14): Experimental. Adds a decay factor associated with how deep the node is to the ignition point. The farther, the smaller importance of the cell.
*	DPV_VaR_Volume_Degree_Time_Layer_decay_Adj (15): Idem but satisfying adjacency constraints (greedy)
*	BCentrality (18): Calculates the betweenness centrality value for each node, selecting those that maximize the total summation.
*	BCentrality_Adj (19): Idem but satisfying adjacency constraints (greedy)

Output Folders
--------------

The output folder specified by the user will have the base case without any heuristics. Some heuristics use that info (e.g., bp maps bases heurs) to calculate protection metrics.

Then, the heuristic(s) are applied generating folders per heuristic (inside the Heuristic folder in the aforementioned output folder).

Inside the individual heuristic folders, you get the outputs of simulations using the heuristic for different treatment/harvesting intensities.

A Simple Experiment
-------------------

We have two bash scripts - one with heuristic 2 and another with heuristic 3. We are going to see which one produces fewer burned cells in FinalStats.csv.

To use this heuristics, a values file is needed. This file gives a value for each cell of the forest. It is space-delimited and specified using the --customValue option.

An example can be found in `data/Sub40x40/values40x40.csv` Note: this file is space-delimited even though the file name extension is .csv. 

This is a sample command to run heuristitic 2 with a custom file that has 40x40 cells.

::

  python main.py --input-instance-folder ../data/Sub40x40/ --output-folder ../results/Sub40x40 --sim-years 2 --nsims 10 --finalGrid --weather random --nweathers 100 --Fire-Period-Length 1.0 --ROS-CV 0.0 --seed 123 --IgnitionRad 0 --stats --output-messages --ROS-Threshold 0 --HFI-Threshold 0 --heuristic 2 --customValue="../data/Sub40x40/values40x40.csv"

Another sample command to run heuristic 3 with a custom file that has 40x40 cells.

::

  python main.py --input-instance-folder ../data/Sub40x40/ --output-folder ../results/Sub40x40 --sim-years 2 --nsims 10 --finalGrid --weather random --nweathers 100 --Fire-Period-Length 1.0 --ROS-CV 0.0 --seed 123 --IgnitionRad 0 --stats --output-messages --ROS-Threshold 0 --HFI-Threshold 0 --heuristic 3 --customValue="../data/Sub40x40/values40x40.csv"
