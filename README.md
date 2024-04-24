# ADCIRC netCDF to RAS Compliant data
A set of scripts using command-line interface arguments to convert ADCIRC netCDF data to RAS compliant data. This includes 2D wind and 1D downstream boundary surge timeseries data.

## The specific model branches will have more in-depth Readme information and project-specific scripting and data locations.
Often this data processing is project specific so check the branches for specific projects.
For example: [LWI calibration/validation](https://github.com/mylesmc123/adcirc-to-ras/tree/lwi-coastwide-cal)

### Wind

The ADCIRC output netCDF for wind needs to be processed to be read into RAS. RAS can read both netCDF and DSS. However, on occasion we have seen issues with netCDF, so both formats are processed. Requires a fort.73 ADCIRC file.

![image](https://github.com/mylesmc123/adcirc-to-ras/assets/64209352/65128269-c1a6-4ce5-9b22-50ebbb9d6a1b)

## Surge ADCIRC WSE to DSS Timeseries

Surge data requires a fort.63 ADCIRC file.

A coordinates list is used for RAS downstream boundary segment centroids and are in 4326 projection. Example CSV: 

|X                |Y               |Segment_ID|
|-----------------|----------------|----------|
|-88.0717228360401|30.3137148153158|1         |
|-88.1728856276438|30.2994324331548|2         |
|-88.2721814976089|30.3210838516696|3         |
|-88.3547022998999|30.3634054544617|4         |
|-88.4401807155804|30.3142621790549|5         |
|-88.5435897702386|30.3170900213712|6         |
|-88.6402053094564|30.3430328817197|7         |
|-88.7413020453639|30.334800028443 |8         |
|-88.8327137323075|30.3772355695856|9         |
|-88.9356720052649|30.3852921851168|10        |

The output dss files are created as one dss file per downstream Segment. Each Segment dss file contains each storm event.

![image](https://github.com/mylesmc123/adcirc-to-ras/assets/64209352/3b69be25-a579-49bd-8eb6-4aa1f4f3d8c7)

## QAQC

Output wind data needs to be compared temporally to the precip data (AORC).

QAQC script will produce animations for a surge timeseries location, wind, and precip: https://github.com/mylesmc123/RAS-Data-Temporal-QAQC
These videos can then be put together to compare the temporal relationship between the variables. 

![image](https://github.com/mylesmc123/adcirc-to-ras/assets/64209352/f791c450-763a-4a0d-ae72-d3295eb47a67)
