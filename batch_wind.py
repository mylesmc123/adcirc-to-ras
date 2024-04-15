# Produce wind netcdf and downstream surge timeseries for each cal/val event in an excel sheet
# %%
import pandas as pd
import adcirc2hec_wind
from tqdm import tqdm

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
# input parameters
mesh = None
resolution = 0.1
x_min = -95
y_min = 28.5
x_max = -87.9
y_max = 33 

# batch loop - for each row in df.
for i in tqdm(range(len(df))):

    adcirc_dir = df["ADCIRC Data on Rougarou"][i]
    print(adcirc_dir)
    # reformat to WSL path
    adcirc_dir = adcirc_dir.replace("/twi/work", "/mnt/w")
    adcirc_wind_fn = f"{adcirc_dir}/storm/fort.74.nc"
    event = df["Name"][i+plus]
    print(event)
    ras_wind_output = f'output/wind/{event}_wind_ras.nc'
    r = adcirc2hec_wind.HecWindFile(adcirc_wind_fn, mesh, ras_wind_output)
    r.write(resolution, x_min, y_min, x_max, y_max)

# %%