==========================
Editing Weather Conditions
==========================

Cell2Fire provides us the flexibility to modify for the various weather conditions (inputs) which cause wildfires.
By modifying the weather conditions we can create different environments to run our simulator and obtain results required for a particular test case.
To modify weather conditions we need to first find our delme63 directory, the path for the directory is as below:

.. code-block:: html
   :linenos:

   Cell2Fire/contributed/delme63/9cellsC1

Once we are in the 9cellsC1 directory we need to open Weather.csv file. To edit Weather.csv we need to open it with Excel.

**In Weather.csv the following inputs are editable.**

* Temperature [TMP] (Celcius)
* Relative Humidity [RH]
* Wind Speed [WS] (km/hr)
* Wind Direction [WD] (degrees)
* Fine Fuel moisture Code [FFMC]
* Duff Moisture Code [DMC]
* Drought code [DC]
* Initial Spread Index [ISI]
* Buildup Index [BUI]
* Fire Weather Index [FWI]

The Initial SpreadIndex [ISI], Buildup Index [BUI], and Fire Weather Index [FWI] are dependent on the values of the other inputs to determine their respective scores.
We can use **Equations for the Canadian Forest Fire Weather Index System (Van Wagner)** to clearly determine how to generate values for these three dependent attributes using the independent variables.


Temperature and Humidity
------------------------

We can manipulate either temperature or humidity or both of them to predict the different outcomes based on the heat and humidity conditions of the various climatic region.
This provides us the flexibility to predict how fire would propagate in in hot and humid area (Norther California, USA) as well as in areas that is generally colder and with higher amounts of precipitation(Calgary, Canada).
Temperature plays a key role in ignition of wildfires. As we all know, warmer temperatures with low relative humidity are the major factors for the spread of wildfires and even affects its rate of spread.
**We would measure temperature in Celsius and relative humidity as percentage of water vapor in air.**

Wind Speed and Direction
------------------------

Winds have a significant influence on the spread of fire. It is evident that stronger winds increase the intensity of the fire and speeds up its spread through the forest.
As per our default settings, fire starts from the bottom left cell of the grid. After which to monitor its spread we need to determine the wind direction.
The direction of wind flow can be determined based on where it starts from and to which direction it flows.
For example, if the movement of the wind is from East to West, we would take the input as 0 degrees whereas if its from West to East we would take the input as 180 degrees. 
The input for wind coming from North West direction would lie between 90 and 180 degrees whereas the wind coming from North East would lie between 0 and 90 degrees.


Illustration
------------

To show how modifying Temperature, Wind Speed and Wind Direction affects the simulation, we will take two different environments to show how the fire will spread in these different scenarios.

**The first simulation is based on an area with cooler and drier climate having low Humidity with typically high wind speeds. We used the following inputs for this simulation:**

* **Temperature:** from 1pm-5pm was 25 Celsius and from 6pm-8pm was 20 Celsius. Humidity was constant at 48%.
* **Wind Speed:** from 1pm-5pm was 23 km/h and from 6pm-9pm was 6 km/h.
* **Wind Direction:** Constant at 135 degrees (North Western winds).

**The second simulation is based on an area with higher temperatures and humidity with little to no wind. We used the following inputs for this simulation:**

* **Temperature:** from 1pm-5pm was 33 Celsius and from 6pm-8pm was 27 Celsius. Humidity was constant at 90%.
* **Wind Speed:** from 1pm-5pm was 5.9 km/h and from 6pm-9pm was 4 km/h.
* **Wind Direction:** from 1pm-5pm winds were directed at 30 degrees, but from 6pm-8pm wind were directed from 290 degrees.


Our observation from the first simulation is that the fire has spread to all of the cells by the 8th hour. This could be attributed to the higher windspeed which influences how fast and effectively fires spread.

.. image:: /image/Chicohr1.png
   :width: 20%

   1st hour

.. image:: /image/Chicohr4.png
   :width: 20%

   4th hour

.. image:: /image/Chicohr8.png
   :width: 20%

   8th hour

whereas, Our observations from the second simulation shows that the fire is not able to spread to all of the cells even by the end of the 9th hour.  This is mostly due to the high humidity and the low wind speed.

.. figure:: /image/Manaushr1.png
   :width: 40%

   1st hour

.. figure:: /image/Manaushr6.png
   :width: 40%

   6th hour

.. figure:: /image/Manaushr9.png
   :width: 40%

   9th hour


Build Up Index
--------------

The Buildup Index [BUI] is a weighted combination of the Duff Moisture Code [DMC] and Drought code [DC]. It indicates the total amount of fuel available for combustion by a moving flame front.
The Duff Moisture Code [DMC] indicates the moisture content of loosely-compacted organic layer at a moderate depth while the Drought Code(DC) indicates moisture content at higher depths with compact organic layers.
**The Buildup Index [BUI] scale starts from zero, a rating above 34 is deemed high and one above 77 it is considered extreme.**

Editing Buildup Index [BUI] determines the change in fuel content which determines the spread of fire from the initial cell to the subsequent cells.

**Test 1 has a low BUI score:**

.. image:: /image/Fire01.jpg
   :width: 25%
.. image:: /image/Fire01.jpg
   :width: 25%

In test 1, the fire would remain in the same cell for a few hours.  The fire will not spread to the subsequent cells as there is no fuel for its spread.


**Test 2 has an extreme BUI score set at 99:**

.. image:: /image/Fire01.jpg
  :width: 23%
.. image:: /image/Fire02.png
  :width: 23%
.. image:: /image/Fire03.png
   :width: 23%
.. image:: /image/Fire04.png
   :width: 23%

In Test 2, the fire has enough fuel which enables it to burn all 9 cells in 4 hours.
We should always keep in consideration the Duff Moisture Code [DMC] value while calculating the Buildup Index [BUI] as it considerably affects it.
When Duff Moisture Code [DMC] value is zero the value for Buildup Index [BUI] is also zero.

Initial spread Index
--------------------

The Initial Spread Index [ISI] combines the Fine Fuel moisture Code [FFMC] and Wind speed [WS] to indicate the expected rate of fire spread.
Generally, a 13 km/h increase in wind speed will double the Initial Spread Index [ISI] value.
The Initial Spread Index [ISI] is accepted as a good indicator for spread of fire for open light fuel with wind speeds up to 40 km/h.

To explain how it works we will have to tests the two scenarios, one with low Wind speed [WS] and the other with high Wind speed [WS].

**For Test 1:**

* Wind speed [WS] 4 km/h
* Fine Fuel moisture Code [FFMC] 95
* Initial Spread Index [ISI] is calculated as 35.9

**These inputs resulted in the following graphs :**

.. image:: /image/ISI1.png
  :width: 23%
.. image:: /image/ISI2.png
  :width: 23%
.. image:: /image/ISI4.png
   :width: 23%

with these values it will take 4 hour to burn all of the cells.

**For test 2 (we increase wind speed by 13 km/h as we know it doubles Initial Spread Index [ISI]):**

* Wind speed [WS] 17 km/h
* Fine Fuel moisture Code [FFMC] 95
* Initial Spread Index [ISI] is calculated as 71.8

**These inputs resulted in the following graphs :**

.. image:: /image/ISI5.png
  :width: 23%
.. image:: /image/ISI6.png
  :width: 23%
.. image:: /image/ISI4.png
   :width: 23%

The first image is at the end of the 1st hour and the final image is at the end of the 3rd hour.
This shows that increasing the Initial Spread Index [ISI] increases the spread of fire.
