Heuristics
==========

Cell2Fire includes built-in heristics to use as benchmarks.


A Simple Example
----------------

First, move to the directory where "main.py" is located. From the root directory of Cell2Fire, you can cd into "cell2fire":

::

    cd cell2fire


Then, run the following command:

::

    python main.py --input-instance-folder ../data/Sub20x20/ --output-folder ../results/Sub20x20/Sub20_RW_RI_N10 --sim-years 1 --nsims 10 --finalGrid --weather random --nweathers 100 --Fire-Period-Length 1.0 --ROS-CV 0.0 --seed 123 --IgnitionRad 0 --stats --output-messages --ROS-Threshold 0 --HFI-Threshold 0 --heuristic 1

Output:

::

    cell2fire_path ~/workspace/Cell2Fire/Cell2Fire/cell2fire
    End of Cell2FireC execution...
    ------ Generating Statistics --------
    General stats...
    ------ Generating outputs for heuristics --------
    Reading data...
    Using custom value function ( from file ../data/Sub40x40/values40x40.csv )
    ------ Running Heuristic: Max_Utility ------
    Total Available cells: 1444
    Running the AS-IS forest (no heuristic applied)
    End of Cell2FireC execution...

    Treat Fraction 0.05...
    Adjacent Constraint: False
    Demand satisfied: True
    Total fitness (FPV): 92733.0
    Running the instance with the heuristic...
    End of Cell2FireC with Harvesting Plan execution...
    Generating stats from heuristic...
    General stats...

    Treat Fraction 0.1...
    Adjacent Constraint: False
    Demand satisfied: True
    Total fitness (FPV): 177698.0
    Running the instance with the heuristic...
    End of Cell2FireC with Harvesting Plan execution...
    Generating stats from heuristic...
    General stats...

    ....

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

The output directory, specified by the user when executing the command, will have the base case without any heuristics. Some heuristics use that (e.g., bp maps bases heurs) to calculate protection metrics.

Then, the heuristic(s) are applied and generates a directory per heuristic in the user-specified output folder.

To access the heuristic results, move to the Heuristic folder. Inside, there is a folder that has the name of the heuristic applied (refer to the list of heuristics in the previous section). For example, if you apply heuristic 2, the name of that directory will be "Max_Utility". Inside that directory, you can find directories that contain the results created by the heuristic - named as FractionX, where X is the treatment/harvesting intensity.

For instance, if you run the following command:

::

  python main.py --input-instance-folder ../data/Sub40x40/ --output-folder ../results/Sub40x40_H2 --sim-years 2 --nsims 10 --finalGrid --weather random --nweathers 100 --Fire-Period-Length 1.0 --ROS-CV 0.0 --seed 123 --IgnitionRad 0 --stats --output-messages --ROS-Threshold 0 --HFI-Threshold 0 --heuristic 2 --customValue="../data/Sub40x40/values40x40.csv"

The results of Heuristic 2 is stored in "results/Sub40x40_H2/Heuristic/Max_Utility".
