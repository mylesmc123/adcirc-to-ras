# Produce wind netcdf and downstream surge timeseries for each cal/val event in an excel sheet
# %%
import pandas as pd

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
# get the first event's ADCIRC directory
adcirc_dir = df["ADCIRC Data on Rougarou"][0]
# reformat to WSL path
adcirc_dir = adcirc_dir.replace("/twi/work", "/mnt/w")
# get filenames for wind and surge
wind_fn = f"{adcirc_dir}/storm/fort.74.nc"
surge_fn = f"{adcirc_dir}/storm/fort.63.nc"
# %%
# call adcirc2hec_wind.py and adcirc2hec_surge.py