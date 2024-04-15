#####################################################
# Interpolates ADCIRC netcdf output (wind) on an
# unstructured triangular mesh to a CF-compliant
# netcdf format which can be used within HEC-RAS
#
####################################################

import logging
from datetime import datetime
from typing import Tuple

import matplotlib.tri as mpl_tri
import numpy as np


class Interpolator:
    """
    Wrapper class for matplotlib's LinearTriInterpolator
    """

    def __init__(self, tri_interp: mpl_tri.LinearTriInterpolator):
        """
        Constructor

        Args:
            tri_interp: LinearTriInterpolator
        """
        self.__interpolator = tri_interp

    def interpolator(self) -> mpl_tri.LinearTriInterpolator:
        """
        Returns the LinearTriInterpolator object

        Returns:
            LinearTriInterpolator

        """
        return self.__interpolator


class AdcircMesh:
    """
    Class to read and store ADCIRC mesh data
    """

    def __init__(self, filename: str):
        """
        Constructor

        Args:
            filename: Path to ADCIRC netcdf file
        """
        self.__filename = filename
        self.__node_x = None
        self.__node_y = None
        self.__elements = None
        self.__elevation = None
        self.__triangulation = None
        self.__read_mesh()
        self.__compute_triangulation()

    def __read_mesh(self) -> None:
        """
        Reads mesh data from ADCIRC netcdf file

        Returns:
            None

        """
        if self.__filename[-3:] == ".nc":
            self.__read_mesh_netcdf()
        else:
            self.__read_mesh_ascii()

    def __read_mesh_netcdf(self) -> None:
        """
        Reads mesh data from ADCIRC netcdf file

        Returns:
            None
        """
        from netCDF4 import Dataset

        ds = Dataset(self.__filename)
        self.__node_x = ds["x"][:]
        self.__node_y = ds["y"][:]
        self.__elements = ds["element"][:] - 1
        self.__elevation = ds["depth"][:]

    def __read_mesh_ascii(self) -> None:
        """
        Read the ADCIRC mesh from an ASCII file

        Returns:
            None
        """

        with open(self.__filename) as f:
            _ = f.readline()
            metadata_string = f.readline()
            n_nodes = int(metadata_string.split()[1])
            n_elements = int(metadata_string.split()[0])
            self.__node_x = np.zeros(n_nodes)
            self.__node_y = np.zeros(n_nodes)
            self.__elements = np.zeros((n_elements, 3), dtype=int)
            self.__elevation = np.zeros(n_nodes)
            for i in range(n_nodes):
                line = f.readline().split()
                self.__node_x[i] = float(line[1])
                self.__node_y[i] = float(line[2])
                self.__elevation[i] = float(line[3])
            for i in range(n_elements):
                line = f.readline().split()
                self.__elements[i, 0] = int(line[2]) - 1
                self.__elements[i, 1] = int(line[3]) - 1
                self.__elements[i, 2] = int(line[4]) - 1

    def __compute_triangulation(self) -> None:
        """
        Computes the triangulation of the mesh

        Returns:
            None

        """
        self.__triangulation = mpl_tri.Triangulation(
            self.__node_x, self.__node_y, self.__elements
        )

    def nnode(self) -> int:
        """
        Returns the number of nodes in the mesh

        Returns:
            int - Number of nodes

        """
        return self.__node_x.shape[0]

    def nele(self) -> int:
        """
        Returns the number of elements in the mesh

        Returns:
            int - Number of elements

        """
        return self.__elements.shape[0]

    def x(self) -> np.array:
        """
        Returns the x coordinates of the nodes

        Returns:
            np.array - x coordinates of the nodes

        """
        return self.__node_x

    def y(self) -> np.array:
        """
        Returns the y coordinates of the nodes

        Returns:
            np.array - y coordinates of the nodes

        """
        return self.__node_y

    def elements(self) -> np.array:
        """
        Returns the elements of the mesh

        Returns:
            np.array - Elements of the mesh

        """
        return self.__elements

    def elevation(self) -> np.array:
        """
        Returns the elevation of the mesh

        Returns:
            np.array - Elevation of the mesh

        """
        return self.__elevation

    def bounds(self) -> Tuple[float, float, float, float]:
        """
        Returns the bounds of the mesh

        Returns:
            tuple - (x_min, y_min, x_max, y_max)

        """
        x_min = np.min(self.__node_x)
        x_max = np.max(self.__node_x)
        y_min = np.min(self.__node_y)
        y_max = np.max(self.__node_y)
        return x_min, y_min, x_max, y_max

    def get_interpolator(self, dataset: np.array) -> Interpolator:
        """
        Returns an Interpolator object for the given dataset

        Args:
            dataset: np.array - Dataset to interpolate

        Returns:
            Interpolator - Interpolator object

        """
        # TODO: These interpolators are slow because of the trifinder
        # construction at each step. Consider moving to our own
        # triangulation object which can be cached
        return Interpolator(
            mpl_tri.LinearTriInterpolator(self.__triangulation, dataset)
        )


class AdcircResult:
    """
    Class to read and store ADCIRC result data
    """

    def __init__(self, filename: str):
        """
        Constructor

        Args:
            filename: Path to ADCIRC netcdf file
        """
        self.__VARIABLE_NAMES = [
            "zeta",
            "zeta_max",
            "windx",
            "windy",
        ]  # ...TODO: Incomplete list
        self.__filename = filename
        self.__n_datasets = 0
        self.__n_time_steps = 0
        self.__dataset = None
        self.__ascii_file = None
        self.__dt = None
        self.__n_nodes = None
        self.__variables = []
        self.__file_format = self.__check_file_format()
        self.__initialize()

    def __del__(self):
        """
        Destructor

        Returns:
            None

        """
        if self.__file_format == "ascii" and self.__ascii_file is not None:
            self.__ascii_file.close()

    def __check_file_format(self) -> str:
        """
        Checks the file format of the ADCIRC netcdf file

        Returns:
            str - File format

        """
        if self.__filename[-3:] == ".nc":
            return "netcdf"
        else:
            return "ascii"

    def __initialize(self) -> None:
        """
        Reads the initial information in the ADCIRC file

        Returns:
            None
        """
        if self.__file_format == "netcdf":
            self.__initialize_netcdf()
        elif self.__file_format == "ascii":
            self.__initialize_ascii()
        else:
            msg = "Unknown file format"
            raise ValueError(msg)

    def __initialize_ascii(self) -> None:
        """
        Initializes the information for an ASCII ADCIRC file

        Returns:
            None
        """
        self.__ascii_file = open(self.__filename)  # noqa: SIM115
        _ = self.__ascii_file.readline()
        metadata_string = self.__ascii_file.readline()
        header_pos = self.__ascii_file.tell()
        first_record_header = self.__ascii_file.readline()
        self.__ascii_file.seek(header_pos)

        self.__n_time_steps = int(metadata_string.split()[0])
        self.__n_datasets = int(metadata_string.split()[4])
        n_step_per_output = float(metadata_string.split()[3])
        self.__n_nodes = int(metadata_string.split()[1])

        output_time_0 = float(first_record_header.split()[0])
        output_step_0 = float(first_record_header.split()[1])
        time_step = output_time_0 / output_step_0

        self.__dt = n_step_per_output * time_step

    def __initialize_netcdf(self) -> None:
        """
        Initializes the information for a netcdf ADCIRC file

        Returns:
            None
        """
        from netCDF4 import Dataset

        self.__dataset = Dataset(self.__filename)

        for vv in self.__VARIABLE_NAMES:
            if vv in list(self.__dataset.variables.keys()):
                self.__variables.append(vv)

        self.__n_datasets = len(self.__variables)
        self.__n_time_steps = self.__dataset.dimensions["time"].size
        self.__n_nodes = self.__dataset.dimensions["node"].size
        self.__ref_time = self.__dataset["time"].units

    def variable(self, index: int) -> str:
        """
        Returns the variable name at the given index

        Args:
            index (int): Index of the variable

        Returns:
            str - Variable name

        """
        if self.__file_format == "netcdf":
            return self.__variables[index]
        else:
            msg = "ASCII files do not have variable names"
            raise ValueError(msg)

    def n_datasets(self) -> int:
        """
        Returns the number of datasets in the file

        Returns:
            int - Number of datasets

        """
        return self.__n_datasets

    def n_time_steps(self) -> int:
        """
        Returns the number of time steps in the file

        Returns:
            int - Number of time steps

        """
        return self.__n_time_steps

    def get_time(self, index: int) -> float:
        """
        Returns the time at the given index

        Args:
            index: Index of the time step

        Returns:
            float - Time at the given index

        """
        if self.__file_format == "netcdf":
            return self.__dataset["time"][index]
        else:
            return index * self.__dt

    def get(self, index: int) -> np.array:
        """
        Returns the data at the given index

        Args:
            index: Index of the time step

        Note: If reading ascii, no index is needed and the data is read sequentially

        Returns:
            np.array - Data at the given index

        """
        if self.__file_format == "netcdf":
            return self.__get_netcdf(index)
        else:
            return self.__get_ascii()

    def __get_ascii(self) -> np.array:
        """
        Returns the data at the next time step for an ASCII file

        Note:
            You must read the ascii sequentially, so no index is needed

        Returns:
            np.array - Data at the next time step
        """

        header = self.__ascii_file.readline().split()
        if len(header) == 2:
            n_nodes = self.__n_nodes
            default_value = 0.0
        elif len(header) == 4:
            n_nodes = int(header[2])
            default_value = float(header[3])
        else:
            msg = "Unknown header format"
            raise ValueError(msg)

        data = np.full((self.__n_datasets, n_nodes), default_value, dtype=float)
        for i in range(n_nodes):
            line = self.__ascii_file.readline().split()
            for j in range(self.__n_datasets):
                data[j, i] = float(line[j+1])
                
        return data

    def __get_netcdf(self, index: int) -> np.array:
        """
        Returns the data at the given index for a netcdf file
        Args:
            index: Index of the time step

        Returns:
            np.array - Data at the given index
        """

        arr = np.zeros((self.__n_datasets, self.__n_nodes), dtype=float)

        for i in range(self.__n_datasets):
            v = self.__variables[i]
            if self.__n_time_steps > 1:
                a = self.__dataset[v][index][:]
            else:
                a = self.__dataset[v][:]
            arr[i, :] = a[:]

        return arr


class HecWindFile:
    """
    Class to generate HEC wind files
    """

    def __init__(self, input_file: str, mesh_file: str, output_file: str):
        """
        Constructor

        Args:
            input_file: ADCIRC netcdf file
            mesh_file: ADCIRC mesh file if input is not netCDF
            output_file: HEC wind file in netcdf format
        """
        self.__input_file = input_file
        self.__mesh_file = mesh_file
        self.__output_file = output_file

    def write(
        self,
        resolution: float,
        x_min: float,
        y_min: float,
        x_max: float,
        y_max: float,
        # reference_time: datetime,
    ) -> None:
        """
        Writes the HEC wind file

        Args:
            resolution: Resolution of the output raster in decimal degrees
            x_min: bounding box minimum x coordinate
            y_min: bounding box minimum y coordinate
            x_max: bounding box maximum x coordinate
            y_max: bounding box maximum y coordinate
            reference_time: Reference time of the output file

        Returns:
            None

        """
        from datetime import datetime

        import netCDF4
        from netCDF4 import Dataset
        from tqdm import tqdm

        log = logging.getLogger(__name__)
        log.info("Beginning HEC netcdf wind file generation")

        x_resolution = resolution
        y_resolution = resolution

        # ...ADCIRC Data
        dataset = AdcircResult(self.__input_file)
        if self.__mesh_file is None:
            mesh = AdcircMesh(self.__input_file)
        else:
            mesh = AdcircMesh(self.__mesh_file)

        n_steps = dataset.n_time_steps()
        reference_time = dataset._AdcircResult__ref_time.split(" ")[-2:]
        reference_time = " ".join(reference_time)
        reference_time = datetime.strptime(reference_time, "%Y-%m-%d %H:%M:%S")

        # ...Generate blocks of the output raster
        xx = np.linspace(x_min, x_max, num=int((x_max - x_min) / x_resolution + 1))
        yy = np.linspace(y_min, y_max, num=int((y_max - y_min) / y_resolution + 1))
        xg, yg = np.meshgrid(xx, yy)

        ds = Dataset(self.__output_file, mode="w", format="NETCDF4_CLASSIC")
        ds.createDimension("lon", len(xx))
        ds.createDimension("lat", len(yy))
        ds.createDimension("time", n_steps)

        lon_var = ds.createVariable("lon", np.float64, ("lon",))
        lat_var = ds.createVariable("lat", np.float64, ("lat",))
        z_var = ds.createVariable("z", np.float64, ("lat", "lon"))
        crs_var = ds.createVariable("crs", np.int32)
        time_var = ds.createVariable("time", np.float64, ("time",))

        wind_u_var = ds.createVariable(
            "wind_u",
            np.float32,
            ("time", "lat", "lon"),
            fill_value=netCDF4.default_fillvals["f8"],
            compression="zlib",
            complevel=2,
            chunksizes=(1, len(yy), len(xx)),
        )
        wind_v_var = ds.createVariable(
            "wind_v",
            np.float32,
            ("time", "lat", "lon"),
            fill_value=netCDF4.default_fillvals["f8"],
            compression="zlib",
            complevel=2,
            chunksizes=(1, len(yy), len(xx)),
        )
        # wind_mag_var = ds.createVariable(
        #    "wind_speed",
        #    np.float32,
        #    ("time", "lat", "lon"),
        #    fill_value=-99999.0,
        #    chunksizes=(1, len(yy), len(xx)),
        #    compression='zlib', complevel=2,
        # )

        # ...Metadata
        lon_var.long_name = "Longitude"
        lon_var.units = "degrees_east"
        lon_var.axis = "X"
        lat_var.long_name = "Latitude"
        lat_var.units = "degrees_north"
        lat_var.axis = "Y"
        z_var.long_name = "height above mean sea level"
        z_var.units = "meters"
        time_var.long_name = "time"
        time_var.units = "minutes since {:s}".format(
            reference_time.strftime("%Y-%m-%d %H:%M:%S")
        )
        time_var.axis = "T"
        wind_u_var.units = "m/s"
        wind_u_var.long_name = "e/w wind velocity"
        wind_u_var.grid_mapping = "crs"
        wind_v_var.units = "m/s"
        wind_v_var.long_name = "n/s wind velocity"
        wind_v_var.grid_mapping = "crs"
        crs_var.long_name = "coordinate reference system"
        crs_var.grid_mapping_name = "latitude_longitude"
        crs_var.longituce_of_prime_meridian = 0.0
        crs_var.semi_major_axis = 6378137.0
        crs_var.inverse_flattening = 298.257223563
        crs_var.crs_wkt = (
            'GEOGCS["WGS 84",DATUM["WGS_1984",'
            'SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],'
            'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],'
            'UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
        )
        ds.Conventions = "CF-1.6,UGRID-0.9"
        ds.title = f"Conversion to HEC-RAS CF format from {self.__input_file:s}"
        ds.institution = "The Water Institute of the Gulf"
        ds.source = "https://github.com/mylesmc123/adcirc-to-ras"
        ds.history = "Created {:s}".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M"))
        ds.metadata_conventions = "Data generated by adcirc2hec_wind.py for HEC-RAS"
        ds.date_created = "{:s}".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M"))

        # ... Grid
        lon_var[:] = xx
        lat_var[:] = yy
 
        for i in tqdm(range(n_steps)):
            wind_data = dataset.get(i)
            wind_u_raw = wind_data[0]
            wind_v_raw = wind_data[1]
            # get timestep in seconds from reference time.
            timestep_now = dataset.get_time(i)

            wind_u_interp = mesh.get_interpolator(wind_u_raw)
            wind_v_interp = mesh.get_interpolator(wind_v_raw)

            wind_u_result = wind_u_interp.interpolator()(xg, yg)
            wind_v_result = wind_v_interp.interpolator()(xg, yg)

            # ...Force the ADCIRC NAN data to zero
            wind_u_result[wind_u_result <= -100] = 0.0
            wind_v_result[wind_v_result <= -100] = 0.0
            np.nan_to_num(wind_u_result, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
            np.nan_to_num(wind_v_result, copy=False, nan=0.0, posinf=0.0, neginf=0.0)

            # convert seconds to minutes
            time_var[i] = timestep_now / 60.0
            wind_u_var[i, :, :] = wind_u_result.data
            wind_v_var[i, :, :] = wind_v_result.data

            # print(wind_u_var[i, 6, :])
            # wind_mag_var[i, :, :] = np.sqrt(
            #    wind_u_result * wind_u_result + wind_v_result * wind_v_result
            # )
        
        ds.close()

def adcirc2hec_wind_main():
    """
    Main function for the adcirc2hec_wind.py script

    Returns:
        None

    """

    import argparse

    parser = argparse.ArgumentParser(
        description="Conversion of ADCIRC data into netCDF format"
    )
    parser.add_argument(
        "--input", help="Name of ADCIRC netCDF input file", type=str, required=True
    )
    parser.add_argument(
        "--output", help="Name of output netCDF file", type=str, required=True
    )
    parser.add_argument(
        "--resolution", help="Resolution in decimal degrees", type=float, required=True
    )
    parser.add_argument(
        "--bounds",
        help="Bounding box [x0,y0,x1,y1]",
        nargs=4,
        required=True,
        type=float,
    )
    parser.add_argument(
        "--mesh",
        help="Name of ADCIRC mesh if input is not netCDF",
        type=str,
        required=False,
        default=None,
    )

    args = parser.parse_args()

    x0 = args.bounds[0]
    y0 = args.bounds[1]
    x1 = args.bounds[2]
    y1 = args.bounds[3]

    x_min = min(x0, x1)
    x_max = max(x0, x1)
    y_min = min(y0, y1)
    y_max = max(y0, y1)

    r = HecWindFile(args.input, args.mesh, args.output)
    r.write(args.resolution, x_min, y_min, x_max, y_max)


if __name__ == "__main__":
    adcirc2hec_wind_main()
