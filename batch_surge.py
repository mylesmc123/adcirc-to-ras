# Produce wind netcdf and downstream surge timeseries for each cal/val event in an excel sheet
# %%
from datetime import datetime, timezone
import os
import pandas as pd
import adcirc2hec_surge
from tqdm import tqdm
from utils.extract import Extract

# %%
# open excel sheet
sheet = "Combined_No_Duplicates"
excel_file = "Validation_Calibration_Storm_Selection.xlsx"
df = pd.read_excel(excel_file, sheet_name=sheet)
df

# %%
# drop any rows with Nan in column: df["ADCIRC Data on Rougarou"]
df = df.dropna(subset=["ADCIRC Data on Rougarou"])
# reindex
df = df.reset_index(drop=True)
df["ADCIRC Data on Rougarou"]
# %%
df
# %%
# a couple events require multiple ADCIRC files. lets skip those for now.
# drop any rows with multiple ADCIRC files
df = df[~df["ADCIRC Data on Rougarou"].str.contains(",")]
df = df.reset_index(drop=True)
df["ADCIRC Data on Rougarou"]
# %%
# protoype: get the ADCIRC file's for wind (74) and surge (63) for the first event
# event = df["Name"][0]
# # get the first event's ADCIRC directory
# adcirc_dir = df["ADCIRC Data on Rougarou"][0]
# # reformat to WSL path
# adcirc_dir = adcirc_dir.replace("/twi/work", "/mnt/w")
# # get filenames for wind and surge

points_dir = "/mnt/v/projects/p00832_ocd_2023_latz_hr/01_processing/GIS/Coastal_Segments/v20240412/textfiles"
output_dir = "output/ds"
output_format = "dss" 

# batch loop - for each row in df.
for i in tqdm(range(len(df))):
    adcirc_dir = df["ADCIRC Data on Rougarou"][i]
    # reformat to WSL path
    adcirc_dir = adcirc_dir.replace("/twi/work", "/mnt/w")
    adcirc_wind_fn = f"{adcirc_dir}/storm/fort.74.nc"
    event = df["Name"][i]
    print(f'\n{event}')
    surge_fn = f"{adcirc_dir}/storm/fort.63.nc"
    coldstart = adcirc2hec_surge.getColdStart(surge_fn)
    coldstart_utc = datetime(
        coldstart.year,
        coldstart.month,
        coldstart.day,
        coldstart.hour,
        coldstart.minute,
        0,
        tzinfo=timezone.utc,
    )

    pointFilesList = adcirc2hec_surge.getPointFilesFromDir(points_dir)
    # print (pointFilesList)
    for pointFile in tqdm(pointFilesList):
        head, tail = os.path.split(pointFile)
        outputFile = os.path.join(output_dir, tail.split(".")[0] + ".nc")
        # print("Outut file: ", outputFile)
        # print (f'\nExtracting {tail.split(".")[0]}')

        adcirc2hec_surge.extractor = Extract(surge_fn, pointFile, coldstart_utc)
        adcirc2hec_surge.extractor.extract(outputFile, output_format, event)

# %%
