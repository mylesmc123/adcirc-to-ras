#!/usr/bin/env python3

def getColdStart(adcirc_fort63_file):
# Get cold start from adcirc fort.63 file:
    import xarray as xr
    from datetime import datetime
    # ds = xr.open_dataset(adcirc_fort63_file, drop_variables=['neta','nvel'], chunks={"node": 1000})
    ds = xr.open_dataset(adcirc_fort63_file, drop_variables=['neta','nvel'])
    coldstart = ds.time.base_date
    coldstart = datetime.fromisoformat(coldstart)
    return coldstart

def getPointFilesFromDir(dir):
    import glob, os
    pointFilesList = glob.glob(rf'{dir}/*.txt')
    return pointFilesList

def main():
    import argparse
    from datetime import datetime, timedelta, timezone    
    import os.path
    from utils.extract import Extract

    p = argparse.ArgumentParser(description="File to use for extraction of ADCIRC time series")
    p.add_argument(
        "--file", help="The ADCIRC file to extract timeseries data from.", 
        required=True, 
        type=str
    )

    p.add_argument(
        "--ras_hdf", help="The filename for the HEC-RAS temp plan HDF file (p##.tmp.hdf) to update boundary condition timeseries data to.", 
        required=False, 
        type=str
    )
    
    p.add_argument(
        "--dir",
        help="Name of the directory containing the point files to extract coordinates from. The directory should only contain .txt files that are point files.",
        required=True,
        type=str,
    )
    p.add_argument(
        "--coldstart",
        help="Cold start time for ADCIRC simulation",
        required=False,
        type=datetime.fromisoformat,
    )

    p.add_argument(
        "--ras_start", help="RAS simulation start time. Will be used to update RAS pertinent data and HDF files. (Format Ex: 19Sep2022 0600)", 
        required=False, type=str
    )

    p.add_argument(
        "--ras_end", help="RAS simulation start time. Will be used to update RAS pertinent data and HDF files. (Format Ex: 19Sep2022 0600)", 
        required=False, type=str
    )
    
    p.add_argument(
        "--outdir", help="Name of output directory to place output files", required=True, type=str
    )
    p.add_argument(
        "--format",
        help="Format to use. Either netcdf, csv, dss, ras, json",
        required=False,
        default="netcdf",
        type=str,
    )
    p.add_argument(
        "--event",
        help="Event name to use for A-part of output DSS files",
        required=False,
        default="",
        type=str,
    )
    p.add_argument(
        "--json_start",
        help="Specified start time to use for outputting synced Json files. If not specified, the start time will be the cold start time. Format: YYYY-MM-DD HH:MM:SS",
        required=False,
        default=None,
        type=str,
    )

    args = p.parse_args()

    # ...The user is sending UTC, so make python do the same
    if args.coldstart is None:
        coldstart = getColdStart(args.file)
    else: coldstart = args.coldstart
        
    coldstart_utc = datetime(
        coldstart.year,
        coldstart.month,
        coldstart.day,
        coldstart.hour,
        coldstart.minute,
        0,
        tzinfo=timezone.utc,
    )

    outputFileExtensions = {
        "netcdf": ".nc",
        "csv": ".csv",
        "dss": ".dss",
        "ras": ".hdf",
        "json": ".json",
    }

    

    # get the output file extension based on the format
    outputExtension = outputFileExtensions[args.format]

    pointFilesList = getPointFilesFromDir(args.dir)
    for pointFile in pointFilesList:
        head, tail = os.path.split(pointFile)
        # // defaults to a .nc extension but it is replaced later if using a different format.
        outputFile = os.path.join(args.outdir, tail.split(".")[0] + outputExtension)
        print("\nOutput file: ", outputFile)
        print (f'Extracting {tail.split(".")[0]}')

        # if ras output validate and extract using additional required arguments.
        if args.format == 'ras':

            if (args.ras_start is None) or (args.ras_end is None) or (args.ras_hdf is None):
                p.error("--output = ras --> Requires the arguments: --ras_hdf, --ras_start, and --ras_end.")

            try:
                datetime.strptime(args.ras_start, '%d%b%Y %H%M')  
            except:
                print (f'\nERROR: --ras_start {args.ras_start} not the correct format required (Format Ex: 19Sep2022 0600).\n')
                exit()

            try:
                datetime.strptime(args.ras_end, '%d%b%Y %H%M')
            except:
                print (f'\nERROR: --ras_end {args.ras_end} not the correct format required (Format Ex: 19Sep2022 0600).\n')
                exit()

            # extract using additional required arguments for RAS HDF output.
            extractor = Extract(args.file, pointFile, coldstart_utc)
            extractor.extract(outputFile, args.format, hdf_fn=args.ras_hdf, ras_startTime=args.ras_start, ras_endTime=args.ras_end)
        
        elif args.format == 'json':
            if (args.json_start is None):
                args.json_start = coldstart_utc.strftime('%Y-%m-%d %H:%M:%S')
            try:
                datetime.strptime(args.json_start, '%Y-%m-%d %H:%M:%S')
            except:
                print (f'\nERROR: --start {args.json_start} not the correct format required (Format Ex: 2022-09-19 06:00:00).\n')
                exit()
            # extract using additional required argument for JSON output.
            extractor = Extract(args.file, pointFile, coldstart_utc)
            extractor.extract(outputFile, args.format, event=args.event, json_start=args.json_start)

        # else if not ras or json output, extract using less arguments.
        else:
            extractor = Extract(args.file, pointFile, coldstart_utc)
            extractor.extract(outputFile, args.format, args.event)


if __name__ == "__main__":
    main()