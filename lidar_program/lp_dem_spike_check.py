import os
import glob
from typing import Optional, List, Dict
from osgeo import ogr, osr, gdal, gdalconst


def create_in_memory_copy(dataset: gdal.Dataset) -> Optional[gdal.Dataset]:
    """
    Create an in-memory copy of a GDAL dataset.

    :param dataset: The input dataset to copy.
    :type dataset: gdal.Dataset

    :return: The in-memory copy of the dataset, or None if creation failed.
    :rtype: Optional[gdal.Dataset]
    """
    driver = gdal.GetDriverByName('MEM')
    return driver.CreateCopy('', dataset, 0)


def resample_dataset(dataset: gdal.Dataset, x_res: float, y_res: float) -> Optional[gdal.Dataset]:
    """
    Resample a GDAL dataset to a new resolution using cubic interpolation.

    :param dataset: The input dataset to resample.
    :type dataset: gdal.Dataset
    :param x_res: The new x-resolution.
    :type x_res: float
    :param y_res: The new y-resolution.
    :type y_res: float

    :return: The resampled dataset, or None if resampling failed.
    :rtype: Optional[gdal.Dataset]
    """
    return gdal.Warp('', dataset,
                     format='MEM',
                     xRes=x_res,
                     yRes=y_res,
                     resampleAlg=gdalconst.GRIORA_Cubic)


def align_datasets(src_dataset: gdal.Dataset, ref_dataset: gdal.Dataset) -> Optional[gdal.Dataset]:
    """
    Align a source dataset to match the grid and dimensions of a reference dataset.

    :param src_dataset: The source dataset to align.
    :type src_dataset: gdal.Dataset
    :param ref_dataset: The reference dataset to align to.
    :type ref_dataset: gdal.Dataset

    :return: The aligned dataset, or None if alignment failed.
    :rtype: Optional[gdal.Dataset]
    """
    return gdal.Warp('', src_dataset,
                     format='MEM',
                     outputBounds=ref_dataset.GetGeoTransform(),
                     width=ref_dataset.RasterXSize,
                     height=ref_dataset.RasterYSize,
                     resampleAlg=gdalconst.GRIORA_NearestNeighbour)


def subtract_datasets(dataset1: gdal.Dataset, dataset2: gdal.Dataset) -> Optional[gdal.Dataset]:
    """
    Subtract one GDAL dataset from another.

    :param dataset1: The first dataset.
    :type dataset1: gdal.Dataset
    :param dataset2: The second dataset to subtract from the first.
    :type dataset2: gdal.Dataset

    :return: The dataset containing the subtraction result, or None if subtraction failed.
    :rtype: Optional[gdal.Dataset]
    """
    band1 = dataset1.GetRasterBand(1).ReadAsArray()
    band2 = dataset2.GetRasterBand(1).ReadAsArray()
    result_array = band1 - band2

    driver = gdal.GetDriverByName('MEM')
    result_dataset = driver.Create('', dataset1.RasterXSize, dataset1.RasterYSize, 1, gdal.GDT_Float32)
    result_dataset.SetGeoTransform(dataset1.GetGeoTransform())
    result_dataset.SetProjection(dataset1.GetProjection())
    result_dataset.GetRasterBand(1).WriteArray(result_array)

    return result_dataset


def identify_spikes(dataset: gdal.Dataset, threshold: float) -> List[Dict[str, float]]:
    """
    Identify spikes in a GDAL dataset based on a threshold.

    :param dataset: The input dataset to inspect.
    :type dataset: gdal.Dataset
    :param threshold: The value threshold for flagging spikes.
    :type threshold: float

    :return: List of dictionaries containing flagged spike information.
    :rtype: List[Dict[str, float]]
    """
    spikes = []
    band = dataset.GetRasterBand(1).ReadAsArray()
    geo_transform = dataset.GetGeoTransform()

    for row in range(band.shape[0]):
        for col in range(band.shape[1]):
            value = band[row, col]

            if abs(value) > threshold:
                x_coord = geo_transform[0] + col * geo_transform[1]
                y_coord = geo_transform[3] + row * geo_transform[5]

                spike_info = {
                    "row": row,
                    "col": col,
                    "x_coord": x_coord,
                    "y_coord": y_coord,
                    "value": value
                }

                spikes.append(spike_info)

    return spikes


def write_spikes_to_shapefile(spikes: List[Dict[str, float]], input_file: str, epsg_code: int) -> None:
    """
    Write identified spikes to a shapefile.

    :param spikes: List of dictionaries containing flagged spike information.
    :type spikes: List[Dict[str, float]]
    :param input_file: Path to the input GeoTIFF file for naming the shapefile.
    :type input_file: str
    :param epsg_code: EPSG code for output CRS of shapefile.
    :type epsg_code: int
    """
    # Create directory if it does not exist
    output_folder = 'dem_spikes'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create shapefile
    driver = ogr.GetDriverByName('ESRI Shapefile')
    output_name = os.path.splitext(os.path.basename(input_file))[0] + '_spikes.shp'
    output_path = os.path.join(output_folder, output_name)
    data_source = driver.CreateDataSource(output_path)

    # Set spatial reference
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg_code)  # Replace with the EPSG code that matches your data

    # Create layer and fields
    layer = data_source.CreateLayer("spikes", srs, ogr.wkbPoint)
    field_value = ogr.FieldDefn("Value", ogr.OFTReal)
    layer.CreateField(field_value)

    # Write points
    for spike in spikes:
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(spike['x_coord'], spike['y_coord'])

        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetGeometry(point)
        feature.SetField("Value", spike['value'])

        layer.CreateFeature(feature)
        feature = None

    # Clean up
    data_source = None


def batch_process_dems(input_folder: str, output_folder: str, threshold: float, epsg_code: int) -> None:
    """
    Batch process a folder of DEM files to identify spikes and write them to shapefiles.

    :param input_folder: Path to the folder containing the input GeoTIFF files.
    :type input_folder: str
    :param output_folder: Path to the folder for storing output GeoTIFF files.
    :type output_folder: str
    :param threshold: The value threshold for flagging spikes.
    :type threshold: float
    :param epsg_code: EPSG code for output CRS of shapefile.
    :type epsg_code: int
    """
    summary_data = {}

    for input_file in glob.glob(os.path.join(input_folder, '*.tif')):
        print(f"Processing {input_file}...")

        input_dem = gdal.Open(input_file)
        if input_dem is None:
            print(f"Could not open {input_file}. Skipping...")
            continue

        mem_copy = create_in_memory_copy(input_dem)
        resampled_dem = resample_dataset(mem_copy, 5, 5)
        aligned_resampled_dem = align_datasets(resampled_dem, input_dem)
        diff_dem = subtract_datasets(input_dem, aligned_resampled_dem)

        output_file_name = os.path.basename(input_file)
        output_file = os.path.join(output_folder, output_file_name)
        driver = gdal.GetDriverByName('GTiff')
        output_dataset = driver.CreateCopy(output_file, diff_dem)
        output_dataset = None  # Close and save the file

        spikes = identify_spikes(diff_dem, threshold)

        if spikes:
            print(f"Found {len(spikes)} spikes that exceed the threshold.")
            write_spikes_to_shapefile(spikes, input_file, epsg_code)
            summary_data[input_file] = len(spikes)
        else:
            print("No spikes found that exceed the threshold.")

    # Write summary to text file
    summary_file = os.path.join(output_folder, 'summary.txt')
    with open(summary_file, 'w') as f:
        for file, count in summary_data.items():
            f.write(f"{file}: {count} spikes\n")


def process_single_dem(input_file: str, output_folder: str, threshold: float, epsg_code: int) -> None:
    """
    Process a single DEM file to identify spikes and write them to a shapefile.

    :param input_file: Path to the input GeoTIFF file.
    :type input_file: str
    :param output_folder: Path to the folder for storing output shapefile and summary.
    :type output_folder: str
    :param threshold: The value threshold for flagging spikes.
    :type threshold: float
    :param epsg_code: EPSG code for output CRS of shapefile.
    :type epsg_code: int
    """
    print(f"Processing {input_file}...")

    input_dem = gdal.Open(input_file)
    if input_dem is None:
        print(f"Could not open {input_file}. Exiting...")
        return

    mem_copy = create_in_memory_copy(input_dem)
    resampled_dem = resample_dataset(mem_copy, 5, 5)
    aligned_resampled_dem = align_datasets(resampled_dem, input_dem)
    diff_dem = subtract_datasets(input_dem, aligned_resampled_dem)

    spikes = identify_spikes(diff_dem, threshold)
    summary_data = {}

    if spikes:
        print(f"Found {len(spikes)} spikes that exceed the threshold.")
        write_spikes_to_shapefile(spikes, input_file, epsg_code)
        summary_data[input_file] = len(spikes)
    else:
        print("No spikes found that exceed the threshold.")

    # Write summary to text file
    summary_file = os.path.join(output_folder, 'single_file_summary.txt')
    with open(summary_file, 'w') as f:
        for file, count in summary_data.items():
            f.write(f"{file}: {count} spikes\n")


if __name__ == "__main__":
    # For batch processing
    # input_folder = "path/to/your/input_folder"
    # output_folder = "path/to/your/output_folder"
    # threshold = 0.5
    # batch_process_dems(input_folder, output_folder, threshold)

    # For single file processing
    epsg = 3157
    infile = "path/to/your/input_dem.tif"
    outfolder = "path/to/your/output_folder_single_file"
    _threshold = 0.5  # Replace with the threshold you want to use

    # Create output folder if it does not exist
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    process_single_dem(infile, outfolder, _threshold, epsg)
