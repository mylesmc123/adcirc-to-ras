# Produce wind netcdf and downstream surge timeseries for each cal/val event in an excel sheet
# %%
from datetime import datetime, timezone
import os
import pandas as pd
import adcirc2hec_surge
from tqdm import tqdm
from utils.extract import Extract
import multiprocessing

# inputs
excel_file = "Validation_Calibration_Storm_Selection.xlsx"
sheet = "Combined_No_Duplicates"
points_dir = "/mnt/v/projects/p00832_ocd_2023_latz_hr/01_processing/GIS/Coastal_Segments/v20240412/textfiles"
output_dir = "output/ds_json"
output_format = "json" 

def extract(surge_fn, coldstart_utc, output_dir, output_format, event, pointFile):
    head, tail = os.path.split(pointFile)
    outputFile = os.path.join(output_dir, tail.split(".")[0] + "." + output_format)
    adcirc2hec_surge.extractor = Extract(surge_fn, pointFile, coldstart_utc)
    adcirc2hec_surge.extractor.extract(outputFile, output_format, event)

# %%
# open excel sheet
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

for i in tqdm(range(len(df))):
    # skipping first 2 events for debugging
    # if i < 2:
    #     continue
    adcirc_dir = df["ADCIRC Data on Rougarou"][i+2]
    # reformatting to my WSL path instead of the rougarou path used in spreadsheet
    adcirc_dir = adcirc_dir.replace("/twi/work", "/mnt/w")
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
    pool = multiprocessing.Pool(processes=16)
    pool.starmap( extract, [[surge_fn, coldstart_utc, output_dir, output_format, event, x] for x in pointFilesList] )

# %%
