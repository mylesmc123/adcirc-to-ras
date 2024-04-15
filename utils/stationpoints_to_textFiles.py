# %%
import pandas as pd

# %%
# Open the csv file (in 4326 coordinates) and for each row in the file, write a csv file with just the single row of data.
# The text file should be named with the name of the station.
# The text file should have the following format: id,y,x
# stationFile = r"V:\projects\p00832_ocd_2023_latz_hr\01_processing\GIS\Coastal_Segments\v20240412\coastal_segments_centroid_v20240412_xy_EPSG4326.csv"
# WSL formatting
stationFile = "/mnt/v/projects/p00832_ocd_2023_latz_hr/01_processing/GIS/Coastal_Segments/v20240412/coastal_segments_centroid_v20240412_xy_EPSG4326.csv"

df = pd.read_csv(stationFile)
# remaove the last column
df = df.iloc[:, :-1]
df.head()
# %%
# for each row in the dataframe, write a text file to the output_dir with the name of the segment_id
# output_dir = r"V:\projects\p00832_ocd_2023_latz_hr\01_processing\GIS\Coastal_Segments\v20240412\textfiles"
# WSL formatting
output_dir = "/mnt/v/projects/p00832_ocd_2023_latz_hr/01_processing/GIS/Coastal_Segments/v20240412/textfiles"
for index, row in df.iterrows():
    segment_id = str(int(row['Segment_ID']))
    x = row['X']
    y = row['Y']
    with open(f"{output_dir}/Segment_{segment_id}.txt", "w") as f:
        # write the header
        f.write("id,y,x\n")
        f.write(f"{segment_id},{y},{x}")
# %%