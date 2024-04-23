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
output_dir = "output/ds_parallel"
output_format = "dss" 

def extract(surge_fn, coldstart_utc, output_dir, output_format, event, pointFile):
    head, tail = os.path.split(pointFile)
    outputFile = os.path.join(output_dir, tail.split(".")[0] + ".nc")
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




# batch loop - for each row in df.


for i in tqdm(range(len(df))):
    adcirc_dir = df["ADCIRC Data on Rougarou"][i]
    # reformat to WSL path
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
    # Convert to pandas timestamp
    # coldstart_utc = pd.Timestamp(coldstart_utc)

    pointFilesList = adcirc2hec_surge.getPointFilesFromDir(points_dir)
    # print (pointFilesList)
    pool = multiprocessing.Pool(processes=16)
    pool.starmap( extract, [[surge_fn, coldstart_utc, output_dir, output_format, event, x] for x in pointFilesList] )
    # pool.starmap( extract, [[surge_fn, coldstart_utc, output_dir, output_format, event, pointFilesList, x] for x in range(1,len(pointFilesList)+1)] )
    # for pointFile in tqdm(pointFilesList):
        # head, tail = os.path.split(pointFile)
        # outputFile = os.path.join(output_dir, tail.split(".")[0] + ".nc")
        # extract(surge_fn, pointFile, coldstart_utc, outputFile, output_format, event)
        # print("Outut file: ", outputFile)
        # print (f'\nExtracting {tail.split(".")[0]}')

        

# %%
