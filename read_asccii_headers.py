
# %%
from astropy.io import ascii

# %%
dat = ascii.read(
    '/mnt/v/projects/p00659_dec_glo_phase3/01_processing/ADCIRC_for_RAS/wind/Rita/CTXCS_TP_0007_HIS_Tides_1_SLC_0_RFC_0_WAV_1_GCP_S2G03BE01_fort.74/CTXCS_TP_0007_HIS_Tides_1_SLC_0_RFC_0_WAV_1_GCP_S2G03BE01_fort.74')

# %%
dat.head()

# %%
