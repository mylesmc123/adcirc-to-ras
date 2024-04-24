# ADCIRC netCDF to RAS Compliant data

## All data locations are related to The Water Institute for use with LWI Coastwide Model Development.

ADCIRC Data locations on Rougarou can be found in Column O of the spreadsheet: https://thewaterinstitute.sharepoint.com/:x:/r/sites/P-00832_OCD_2023_LATZ_HR/_layouts/15/Doc.aspx?sourcedoc=%7B4502DA51-0C48-4775-A056-DE6ECCC6193B%7D&file=Validation_Calibration_Storm_Selection.xlsx&action=default&mobileredirect=true&DefaultItemOpen=1&login_hint=mmcmanus%40thewaterinstitute.org&ct=1712941796553&wdOrigin=OFFICECOM-WEB.MAIN.EDGEWORTH&cid=d2a2ce0f-4cd4-4d05-8647-a9bc74b78730&wdPreviousSessionSrc=HarmonyWeb&wdPreviousSession=eb6711cb-331c-4f44-b146-06e98f9d9279

For example, Hurricane Laura Winds: /twi/work/projects/p00542_cpra_2020_lwi_t01/adcirc_simulations/v1/2020-laura/storm/fort.74.nc
### Wind

The ADCIRC output netCDF for wind needs to be processed to be read into RAS. RAS can read both netCDF and DSS. However, on occasion we have seen issues with netCDF, so both formats are processed.
#### ADCIRC Wind to RAS netCDF

The following script was used: https://github.com/mylesmc123/adcirc-to-ras/blob/lwi-coastwide-cal/batch_wind.py
output data located at: V:\projects\p00832_ocd_2023_latz_hr\01_processing\ADCIRC2RAS\wind\nc
#### RAS Wind netCDF to DSS

This script was run on windows just to avoid installing a linux version of HMS/Vortex in WSL and Rougarou was busy at the time: 
https://github.com/mylesmc123/adcirc-to-ras/blob/lwi-coastwide-cal/nc_to_dss_wind.jy

output data: V:\projects\p00832_ocd_2023_latz_hr\01_processing\ADCIRC2RAS\wind\dss
## Surge ADCIRC WSE to DSS Timeseries

Example Laura ADCIRC Surge Data: /twi/work/projects/p00542_cpra_2020_lwi_t01/adcirc_simulations/v1/2020-laura/storm/fort.63.nc

Coordinates list used for RAS downstream boundary segment centroid are in 4326 projection: "V:\projects\p00832_ocd_2023_latz_hr\01_processing\GIS\Coastal_Segments\v20240312\coastal_segments_centroid_v20240312_xy_EPSG4326.csv" 

The coordinates list was then run through a script to create a text file for each segment: https://github.com/mylesmc123/adcirc-to-ras/blob/lwi-coastwide-cal/utils/stationpoints_to_textFiles.py
Then, the following script was used to create the DSS files: https://github.com/mylesmc123/adcirc-to-ras/blob/lwi-coastwide-cal/batch_surge_parallel.py. This script makes use of multithreaded processing, it is currently set to use 16 CPU cores. so adjust as needed.

The output dss files are created as one dss file per downstream Segment. Each Segment dss file contains each storm event.
output dss timeseries: V:\projects\p00832_ocd_2023_latz_hr\01_processing\ADCIRC2RAS\downstream_boundary
## QAQC

Output wind data needs to be compared temporally to the precip data (AORC).
AORC netcdf data: V:\projects\p00832_ocd_2023_latz_hr\01_processing\Precipitation_AORC\nc_files\AORC_APCP_4KM_LMRFC_202008-09
AORC dss data (processed previously, likely by the Vortex Jython API): "V:\projects\p00832_ocd_2023_latz_hr\01_processing\Precipitation_AORC\Laura_AORC_LWI_Coastwide.dss"

QAQC script will produce animations for a surge timeseries location, wind, and precip: https://github.com/mylesmc123/RAS-Data-Temporal-QAQC
These videos can then be put together to compare the temporal relationship between the variables. 

Example Hurricane Laura video is here: "V:\projects\p00832_ocd_2023_latz_hr\01_processing\ADCIRC2RAS\Example\Laura\QAQC\LWI Laura.mp4"

Enjoy!


 ███▄ ▄███▓▓██   ██▓ ██▓    ▓█████   ██████     ███▄ ▄███▓ ▄████▄  
▓██▒▀█▀ ██▒ ▒██  ██▒▓██▒    ▓█   ▀ ▒██    ▒    ▓██▒▀█▀ ██▒▒██▀ ▀█  
▓██    ▓██░  ▒██ ██░▒██░    ▒███   ░ ▓██▄      ▓██    ▓██░▒▓█    ▄ 
▒██    ▒██   ░ ▐██▓░▒██░    ▒▓█  ▄   ▒   ██▒   ▒██    ▒██ ▒▓▓▄ ▄██▒
▒██▒   ░██▒  ░ ██▒▓░░██████▒░▒████▒▒██████▒▒   ▒██▒   ░██▒▒ ▓███▀ ░
░ ▒░   ░  ░   ██▒▒▒ ░ ▒░▓  ░░░ ▒░ ░▒ ▒▓▒ ▒ ░   ░ ▒░   ░  ░░ ░▒ ▒  ░
░  ░      ░ ▓██ ░▒░ ░ ░ ▒  ░ ░ ░  ░░ ░▒  ░ ░   ░  ░      ░  ░  ▒   
░      ░    ▒ ▒ ░░    ░ ░      ░   ░  ░  ░     ░      ░   ░        
       ░    ░ ░         ░  ░   ░  ░      ░            ░   ░ ░      
            ░ ░                                           ░        
