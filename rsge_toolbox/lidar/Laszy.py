import os
import re
import io
import sys
import glob
import uuid
import math
import json
import tqdm
import laspy
import datetime
import numpy as np
import pandas as pd
from typing import Union
from lazrs import LazrsError
from collections import namedtuple

from rsge_toolbox.util import WktCrsInfo
from rsge_toolbox.util import time_tools
from rsge_toolbox.util.WktCrsInfo import WktCrsInfo
from rsge_toolbox.lidar.lidar_const import ASPRS, RegexLidar


# ------------------------------------
# -- Type Definitions
# ------------------------------------
PointFilterType = namedtuple("PointFilterType", "LAST_RETURN IGNORE_CLASS IGNORE_RETURN")



# ------------------------------------
# -- Misc. Constants
# ------------------------------------
ACQUISITON = False  # !!! Temporary constant - will be removed in the future. Being used to switch off some new features.
GPS_WEEK_TIME_LENGTH = 6
GPS_WEEK_TIME_ERR_STR = "GpsDateConversionError"
CORRUPT_FILE_MSG = "POSSIBLE CORRUPT FILE (Failed to decompress)"

# ------------------------------------
# -- Encoding Constants
# ------------------------------------
UTF_8 = "utf-8"
UNICODE_DECODE_ERROR = "UnicodeDecodeError"


# ------------------------------------
# -- LAS/LAZ related constants
# ------------------------------------
POINT_FILTER_TYPE = PointFilterType(
    LAST_RETURN=0, IGNORE_RETURN=-1, IGNORE_CLASS=-1
)


# ------------------------------------
# -- LaszyReport constants
# ------------------------------------
LASZY_REPORT_DROP_COLUMNS = [  # drop all columns that don't need to be checked for issues
    "x_min", "x_max", "y_min", "y_max", "z_min", "z_max", "guid_hex", "generating_software", "point_count",
    'waveform_internal_packets', 'waveform_external_packets', 'projection', 'spheroid', "wkt_bbox",
    'vert_cs', 'proj_cs', 'geog_cs', 'vlr_count', 'vlr_has_geotiff_crs', 'date_start',
    'has_keypoint', 'has_withheld', 'has_overlap', 'evlr_count', 'evlr_has_geotiff_crs', "rgb_encoding"
]


# =========================================================
# --- Laszy class
# =========================================================
class Laszy:

    """
    Class for reading, parsing, and interpreting LAS/LAZ data.

    Attributes:
        - public_header_block: PublicHeaderBlock object.
        - vlrs: List of VariableLengthRecord objects.
        - points: Laspy.LasData object (optional) (initialized to None).
        - evlrs: List of VariableLengthRecord objects.

    """

    def __init__(self, file: str, read_points=True):

        if not self.__is_lidar_file(file):
            raise NotLidarFileError

        self.file_basename = os.path.basename(file) if bool(file) else ""
        self.file_absolute = file if bool(file) else ""
        reader = laspy.read if read_points else laspy.open

        try:
            self._lasdata = reader(file, laz_backend=laspy.LazBackend.LazrsParallel)
            self.public_header_block = self._lasdata.header
            self.vlrs = self._lasdata.header.vlrs
            self.points = self._lasdata.points if read_points else None
            self.evlrs = self._lasdata.evlrs
        except LazrsError:
            self._lasdata = None
            self.public_header_block = None
            self.vlrs = None
            self.points = None
            self.evlrs = None

    def read_points(self):

        """
        Call laspy.read() to get point record data.
        """

        file = self.file_absolute

        if bool(file):
            self._lasdata.seek(0, io.SEEK_SET)
            self.points = self._lasdata.read_points(self.public_header_block.point_count)

    def set_lasdata(self, lasdata: Union[laspy.LasReader, laspy.LasData]):

        """
        Set self._lasdata using Laspy object.

        Sets the _lasdata property, initializing all related properties that
        depend on _lasdata. This method is particularly useful when a user
        wishes to utilize the functionality of laszy using an already
        initialized laspy object.

        Note that:
            If calling set_lasdata with a LasReader object, (with laspy.open()),
            the points attribute will not be assigned.

            If calling set_lasdata with a LasData object, (with laspy.read()),
            the points attribute will be assigned.

        :param lasdata: LasReader or LasData object.
        """

        has_points = isinstance(lasdata, laspy.LasData)

        self.file_basename = ""
        self.file_absolute = ""
        self._lasdata = lasdata
        self.public_header_block = self._lasdata.header
        self.vlrs = self._lasdata.header.vlrs
        self.points = self._lasdata.points if has_points else None
        self.evlrs = self._lasdata.evlrs

    def get_classes(self) -> list[int]:

        """
        Get point classes present in data.

        :return: List of classes present in all point records.
        """

        classes = list(np.unique(self._lasdata.classification))
        classes = [int(val) for val in classes]

        return classes

    def filter_points(self, class_num: int = POINT_FILTER_TYPE.IGNORE_CLASS, return_num: int = POINT_FILTER_TYPE.IGNORE_RETURN) -> Union[laspy.ScaleAwarePointRecord, None]:

        """
        Filter point cloud by return number or class number.

        Returns a numpy ndarray object containing points filtered by input params.
        By default, both class_num and return_num are set to IGNORE.

        NOTE: return_num=0 indicates LAST_RETURN
        NOTE: return_num=-1 indicates IGNORE
        NOTE: class_num=-1 indicates IGNORE

        :param return_num: Integer value indicating return number.
        :param class_num: Integer value indicating class number.

        :return: Filtered np.ndarray of points.
        """

        filtered = None
        las = self._lasdata

        if not bool(las):
            return filtered

        return_filter = return_num

        should_filter_return = return_num > POINT_FILTER_TYPE.IGNORE_RETURN
        should_filter_class = class_num > POINT_FILTER_TYPE.IGNORE_CLASS

        if should_filter_return:
            return_filter = self.points.num_returns if return_num == POINT_FILTER_TYPE.LAST_RETURN else return_num

        if should_filter_class and should_filter_return:
            filtered = las.points[return_filter == las.return_num & las.classification == class_num]

        elif should_filter_return:
            filtered = las.points[return_filter == las.return_num]

        elif should_filter_class:
            filtered = las.points[las.classification == class_num]

        return filtered

    def get_density(self, class_num: int = POINT_FILTER_TYPE.IGNORE_CLASS, return_num: int = POINT_FILTER_TYPE.IGNORE_RETURN) -> float:

        """
        Calculate density of the LAS/LAZ data.

        Computes point density based on X/Y geographic bounds of the data.
        User may filter by return or class number.

        By default, both class_num and return_num are set to -1. When
        either of these arguments are set to a value LESS THAN 0, these
        filters are ignored.

        Additionally, a 'return_num' of 0 indicates LAST_RETURN, and will
        hence filter the point by last return. Moreover, LAST_RETURN is also
        provided as a constant equal to the value 0.

        :param class_num: Return number to filter points by. (0 = LAST_RETURN; N < 0 = IGNORE)
        :param return_num: Return number to filter points by. (0 = LAST_RETURN; N < 0 = IGNORE)
        :return: Point density for entire point cloud as float or -1 if failure.
        """

        density = -1  # return invalid density if failure as a signal something went wrong

        min_x, max_x = self.get_x_minmax()
        min_y, max_y = self.get_y_minmax()
        dim_x, dim_y = max_x - min_x, max_y - min_y

        filtered = self.filter_points(class_num, return_num)
        if bool(filtered):
            density = filtered.array.size/(dim_x * dim_y)

        return density

    def get_global_encoding(self, value_only: bool = False) -> Union[dict, int]:

        """
        Interpret the Global Encoding value in the LAS/LAZ data.

        Reads the Global Encoding and performs bitwise checks for flags:
            - gps time type
            - internal waveform packets
            - external waveform packets
            - has synthetic returns.
            - CRS info type

        Note that a value of False in the resulting dictionary means
        that the bit associated with the dictionary key is set to 0.

        :return: Dictionary containing the point flag name, and a boolean indicating the status of the bit field.
        :return: Integer value of global encoding (if value_only=True).
        :return: None if failure.
        """

        ge = self.public_header_block.global_encoding

        if value_only:
            return ge.value

        ged = {
            "global_encoding": ge.value,
            "gps_standard_time": bool(ge.gps_time_type),
            "waveform_internal_packets": ge.waveform_data_packets_internal,
            "waveform_external_packets": ge.waveform_data_packets_external,
            "synthetic_returns": ge.synthetic_return_numbers,
            "wkt_crs": ge.wkt
        }

        return ged

    def get_crs_info(self) -> str:

        """
        Get CRS info in VLRs or EVLRs (if present).

        Returns the CRS info of the LAS/LAZ data as a single string.

        :return: Entire CRS string from VLRs if present
        :return: Empty string if no info present.
        """

        # check the VLRs
        vlr = self.vlrs.get("WktCoordinateSystemVlr") if bool(self.vlrs) else None
        if bool(vlr):
            return vlr[0].string

        # check the VLRs
        evlr = self.evlrs.get("WktCoordinateSystemVlr") if bool(self.evlrs) else None
        if bool(evlr):
            return evlr[0].string

        return ""  # will return an empty string if no WKT CRS in VLRs

    def get_x_minmax(self):

        """
        Get LasHeader min/max values.

        :return: Tuple (min, max) on success.
        :return: Tuple (None, None) on failure.
        """

        pub_hdr = self.public_header_block

        return pub_hdr.x_min, pub_hdr.x_max

    def get_y_minmax(self):

        """
        Get LasHeader min/max values.

        :return: Tuple (min, max) on success.
        :return: Tuple (None, None) on failure.
        """

        pub_hdr = self.public_header_block

        return pub_hdr.y_min, pub_hdr.y_max

    def get_z_minmax(self):

        """
        Get LasHeader min/max values.

        :return: Tuple (min, max) on success.
        :return: Tuple (None, None) on failure.
        """

        return self.public_header_block.z_min, self.public_header_block.z_max

    def get_guid_hex(self) -> str:

        """
        Combine guids 1-4 into a single hexadecimal string.

        :return: string representing guids 1-4 in hexadecimal encoding.
        """

        pub_hdr = self.public_header_block

        first = pub_hdr.uuid.hex[0:8]
        second = pub_hdr.uuid.hex[8:12]
        third = pub_hdr.uuid.hex[12:16]
        fourth = pub_hdr.uuid.hex[16:20]
        fifth = pub_hdr.uuid.hex[20:32]

        fourth, fifth = self.__swap_guid_chars(fourth, fifth)

        return "-".join([first, second, third, fourth, fifth])

    def get_gps_time_minmax(self) -> tuple:

        """
        Get the minimum and maximum GPS times for the LAS/LAZ data.

        :return: tuple -> (min_time, max_time)
        """

        gps_times = self.points.gps_time
        gps_min = np.min(gps_times)
        gps_max = np.max(gps_times)

        return float(gps_min), float(gps_max)

    def get_point_source_id_minmax(self) -> tuple:

        """
        Get the minimum and maximum point source IDs for the LAS/LAZ data.

        :return: tuple -> (min_psid, max_psid)
        """

        pt_src_ids = self.points.pt_src_id
        psid_min = np.min(pt_src_ids)
        psid_max = np.max(pt_src_ids)

        return int(psid_min), int(psid_max)

    def get_classification_flags(self) -> Union[dict, None]:

        """
        Get classification flags present in point records (if any).

        Reads the point records and performs bitwise checks for flags:
            - synthetic
            - withheld
            - keypoint
            - overlap

        Note that this utility will only report if these flags are present
        IN ANY of the point records.

        :return: Dictionary containing the point flag name, and a boolean indicating the status of the bit field.
        :return: None if failure.
        """

        point_flags = None

        # classification flags only exist for point formats 6-10
        pdr = self._lasdata.point_format.id
        class_flags_exist = (6 <= pdr <= 10)
        if bool(pdr) and not class_flags_exist:
            return point_flags

        class_flags = np.sort(self.points.classification_flags)
        check_synthetic = np.bitwise_and(class_flags, ASPRS.ClassFlag.SYNTHETIC)
        check_withheld = np.bitwise_and(class_flags, ASPRS.ClassFlag.WITHHELD)
        check_keypoint = np.bitwise_and(class_flags, ASPRS.ClassFlag.KEYPOINT)
        check_overlap = np.bitwise_and(class_flags, ASPRS.ClassFlag.OVERLAP)

        point_flags = {  # check if a flagged point exists after bitwise-and
            "has_synthetic": ASPRS.ClassFlag.SYNTHETIC in check_synthetic,
            "has_keypoint": ASPRS.ClassFlag.KEYPOINT in check_keypoint,
            "has_withheld": ASPRS.ClassFlag.WITHHELD in check_withheld,
            "has_overlap": ASPRS.ClassFlag.OVERLAP in check_overlap
        }

        return point_flags

    def is_rgb_encoded(self) -> bool:

        """
        Check if point record format ID contains rgb encoding fields.

        :return: True or False
        """

        rgb_record_ids = [2, 3, 5, 7, 8, 10]
        pid = self.public_header_block.point_format.id

        return pid in rgb_record_ids

    def get_version(self) -> str:

        """
        Get the Major and Minor version of the inpuit LAS/LAZ data.

        :return: string of the LAS/LAZ version (e.g '1.4')
        """

        version = ""
        if not bool(self.file_basename):
            return version

        pub_hdr = self.public_header_block
        version = f"{pub_hdr.major_version}.{pub_hdr.minor_version}"

        return version

    def get_wkt_boundingbox(self) -> str:

        """
        Get bounding box of input LAS/LAZ data as WKT POLYGON string.

        :return: WKT POLYGON string.
        """

        x_min, x_max = self.get_x_minmax()
        y_min, y_max = self.get_y_minmax()

        p_ll = f"{x_min} {y_min}"
        p_ul = f"{x_min} {y_max}"
        p_ur = f"{x_max} {y_max}"
        p_lr = f"{x_max} {y_min}"

        wkt_str = f"POLYGON(({p_ll}, {p_ul}, {p_ur}, {p_lr}, {p_ll}))"

        return wkt_str

    def vlrs_have_wkt_crs(self, evlr: bool = False) -> bool:

        """
        Check if VLRs has crs info in them.

        :return: bool
        """

        records = self.evlrs if evlr else self.vlrs
        vlr = records.get("WktCoordinateSystemVlr") if bool(records) else None

        if bool(vlr):
            return True

        return False

    def vlrs_have_geotiff_crs(self, evlr: bool = False) -> bool:

        """
        Check if VLRs has crs info in them.

        :return: bool
        """

        records = self.evlrs if evlr else self.vlrs
        if bool(records):
            has_geo_double = bool(records.get("GeoDoubleParamsVlr"))
            has_geo_ascii = bool(records.get("GeoAsciiParamsVlr"))
            has_geo_key = bool(records.get("GeoKeyDirectoryVlr"))
            if has_geo_key or has_geo_ascii or has_geo_double:
                return True

        return False

    def summarize(self, header_only=False, outdir="") -> Union[dict, None]:

        """
        Summarize the input LAS/LAZ data into a dictionary.

        User may optionally pass header_only=True (False by default).
        When header_only is set to True, this utility will omit the
        point data. This is considerably faster, however certain data
        that can only be derived from the point records will not be
        present in the result.

        If 'outdir' is NOT an empty string, function will write results to
        file in JSON format. Note that even if the 'outdir' is not valid,
        function will create a directory to write hte results to.

        :param outdir: Out directory. If provided, results will also be writting to a file ({self._file}.json)
        :param header_only: boolean value. Determines whether to read the point data.
        :return:
        """

        point_record_summary = None
        pub_hdr = self.public_header_block
        if not header_only and pub_hdr.point_count > 0:
            point_record_summary = self.__point_record_summary()

        summary = {
            "filename": self.file_basename,
            "public_header_block": self.__public_header_summary(),
            "crs": self.__crs_info_summary(),
            "vlrs": {
                "vlr_count": len(pub_hdr.vlrs),
                "vlr_has_wkt_crs": self.vlrs_have_wkt_crs(),
                "vlr_has_geotiff_crs": self.vlrs_have_geotiff_crs(),
                "records": self.__vlr_summary()
            },
            "point_records": point_record_summary,
            "evlrs": {
                "evlr_count": pub_hdr.number_of_evlrs,
                "evlr_has_wkt_crs": self.vlrs_have_wkt_crs(evlr=True),
                "evlr_has_geotiff_crs": self.vlrs_have_geotiff_crs(evlr=True),
                "records": self.__vlr_summary(evlr=True)
            },
            "rgb_encoding": self.is_rgb_encoded(),
            "wkt_bbox": self.get_wkt_boundingbox()
        }

        if bool(outdir):
            self.__summary_to_json(outdir, summary)

        return summary

    def __public_header_summary(self) -> dict:

        """
        Summarize the input LAS/LAZ public header block data into a dictionary.

        :return:
        """

        pub_hdr = self.public_header_block
        x_min, x_max = self.get_x_minmax()
        y_min, y_max = self.get_y_minmax()
        z_min, z_max = self.get_z_minmax()
        x_dec_places = str(pub_hdr.x_scale)[::-1].find('.')
        y_dec_places = str(pub_hdr.y_scale)[::-1].find('.')
        z_dec_places = str(pub_hdr.z_scale)[::-1].find('.')

        pub_hdr_summary = {
            "global_encoding": self.get_global_encoding(),
            "guid_asc": self.get_guid_asc(),
            "guid_hex": self.get_guid_hex(),
            "file_source_id": pub_hdr.file_source_id,
            "system_id": pub_hdr.system_identifier,
            "generating_software": pub_hdr.generating_software,
            "creation_date": self.__format_creation_date(pub_hdr),
            "version": self.get_version(),
            "point_data_format": pub_hdr.point_format.id,
            "point_count": pub_hdr.point_count,
            "x_min": round(x_min, x_dec_places),
            "x_max": round(x_max, x_dec_places),
            "y_min": round(y_min, y_dec_places),
            "y_max": round(y_max, y_dec_places),
            "z_min": round(z_min, z_dec_places),
            "z_max": round(z_max, z_dec_places),
            "x_scale": pub_hdr.x_scale,
            "y_scale": pub_hdr.y_scale,
            "z_scale": pub_hdr.z_scale,
            "x_offset": round(pub_hdr.x_offset, x_dec_places),
            "y_offset": round(pub_hdr.y_offset, y_dec_places),
            "z_offset": round(pub_hdr.z_offset, z_dec_places),
        }

        return pub_hdr_summary

    def __point_record_summary(self) -> dict:

        """
        Summarize the input LAS/LAZ point data into a dictionary.

        :return:
        """

        gps_min, gps_max = self.get_gps_time_minmax()
        fl_min, fl_max = self.get_point_source_id_minmax()
        gps_min_week_time = self.__is_gps_week_time(gps_min)
        gps_max_week_time = self.__is_gps_week_time(gps_max)
        point_records_summary = {
            "classes": self.get_classes(),
            "gps_time_min": gps_min,
            "gps_time_max": gps_max,
            "date_start": time_tools.gps2unix(gps_min) if not gps_min_week_time else GPS_WEEK_TIME_ERR_STR,
            "date_end": time_tools.gps2unix(gps_max) if not gps_max_week_time else GPS_WEEK_TIME_ERR_STR,
            "flightline_start": fl_min,
            "flightline_end": fl_max,
            "class_flags": self.get_classification_flags()
        }

        return point_records_summary

    def __crs_info_summary(self) -> dict:

        """
        Summarize the input LAS/LAZ CRS information into a dictionary.

        :return:
        """

        crsinfo = WktCrsInfo(self.get_crs_info())

        return crsinfo.__dict__

    def __vlr_summary(self, evlr=False) -> Union[list[dict], None]:

        """
        Summarize the input LAS/LAZ VLRs or EVLRs into a list of dictionary objects.

        :param evlr: Boolean that controls whether to summarize EVLRs or VLRs.
        :return: list of dictionaries where each list element is a single VLR/EVLR summary.
        """

        records = self.evlrs if evlr else self.vlrs
        if not records:
            return None

        record_summaries = []
        for record in records:

            vlr_num = len(record_summaries) + 1
            vlr_keys = record.__dict__.keys()
            is_copc_info = self.__is_copc_info_vlr(record)
            is_copc_hierarchy = self.__is_copc_hierarchy_vlr(record)
            # laspy names the variable length portion of the VLR differently for each type of VLR.
            # Due to this distasteful decision, we must dynamically assign the variable record data
            # based on each VLR type.
            record_data = ""
            if "record_data" in vlr_keys:
                record_data = record.record_data

            elif is_copc_info:
                record_data = b""  # COPC VLRs are a special case (annoying). Ignore them.

            elif is_copc_hierarchy:
                record_data = record.bytes  # COPC VLRs are a special case (annoying). Ignore them.

            else:
                for key in vlr_keys:
                    if (not key.startswith("_")) and (key not in ["description", "record_id", "user_id"]):
                        record_data = record.__dict__[key]
                        break

            summary = {
                f"vlr{vlr_num}_user_id": record.user_id if not is_copc_hierarchy else None,
                f"vlr{vlr_num}_record_id": record.record_id if not is_copc_hierarchy else None,
                f"vlr{vlr_num}_record_length": sys.getsizeof(record_data) if not is_copc_hierarchy else None,
                f"vlr{vlr_num}_description": record.description,
                f"vlr{vlr_num}_record_data": str(record_data) if not isinstance(record_data, bytes) else None
            }

            record_summaries.append(summary)

        return record_summaries

    def get_guid_asc(self) -> str:

        try:
            guid = uuid.UUID(self.get_guid_hex())
            guid_asc = guid.bytes.decode(UTF_8).replace("\x00", "")
        except UnicodeDecodeError:
            guid_asc = UNICODE_DECODE_ERROR

        return guid_asc

    def __summary_to_json(self, outdir, summary):

        """
        Private method to encapsulate writing summary dict to json file.

        :param outdir: Out directory.
        :param summary: Summary dictionary.
        """

        os.makedirs(outdir, exist_ok=True)
        file_no_ext = os.path.splitext(self.file_basename)[0]
        out_json = os.path.join(outdir, file_no_ext + ".json")
        if not os.path.exists(out_json):
            with open(out_json, "w") as outfile:
                json.dump(summary, outfile, indent=4)

    @staticmethod
    def __format_creation_date(pub_hdr: laspy.LasHeader) -> str:

        """
        Format the creation date attribute for presentation.

        :param pub_hdr: Public header block attribute.
        :return: Date as string.
        """

        creation_date_fmt = ""
        creation_date = pub_hdr.creation_date
        if creation_date:
            creation_month = f"{creation_date.month}" if len(str(creation_date.month)) > 1 else f"0{creation_date.month}"
            creation_day = f"{creation_date.day}" if len(str(creation_date.day)) > 1 else f"0{creation_date.day}"
            creation_date_fmt = f"{creation_date.year}-{creation_month}-{creation_day}"
        return creation_date_fmt

    @staticmethod
    def __is_gps_week_time(gps_time: float) -> bool:

        """
        Check if gps time is gps week time.

        :param gps_time: GPS time (float value)
        :return: True or False
        """

        gpst_no_dec = str(gps_time).split(".")[0]
        return len(gpst_no_dec) <= GPS_WEEK_TIME_LENGTH

    @staticmethod
    def __is_lidar_file(file):

        """
        Determine if filename is LAS/LAZ file.
        """

        return file.endswith("las") or file.endswith("laz")

    @staticmethod
    def __swap_guid_chars(fourth: str, fifth: str):

        strings = ["", ""]
        for i, string in enumerate([fourth, fifth]):
            strings[i] += (string[2:4] + string[0:2])
        strings[1] += fifth[4:]

        return strings[0], strings[1]

    @staticmethod
    def __is_copc_vlr(record):
        return isinstance(record, laspy.copc.CopcHierarchyVlr) or isinstance(record, laspy.copc.CopcInfoVlr)

    @staticmethod
    def __is_copc_info_vlr(record):
        return isinstance(record, laspy.copc.CopcInfoVlr)

    @staticmethod
    def __is_copc_hierarchy_vlr(record):
        return isinstance(record, laspy.copc.CopcHierarchyVlr)


# =========================================================
# --- LaszyReport class
# =========================================================
class _LaszyReportColumns:

    """
    'enum' class containing constant lists for LaszyReport columns.
    """

    FILENAME = "filename"

    PUB_HDR = [
        "guid_asc", "guid_hex", "file_source_id", "system_id",  "generating_software", "creation_date",
        "version", "point_data_format", "point_count",  "x_min",  "x_max",  "y_min", "y_max", "z_min",
        "z_max", "x_scale", "y_scale", "z_scale", "x_offset", "y_offset", "z_offset"
    ]
    GLOBAL_ENCODING = [
        'global_encoding', 'gps_standard_time', 'waveform_internal_packets',
        'waveform_external_packets', 'synthetic_returns', 'wkt_crs'
    ]
    CRS = [
        'projection', 'vert_datum', 'compd_cs', 'spheroid', 'hz_datum',
        'vert_cs', 'proj_cs', 'geog_cs'
    ]
    VLR_HDR = [
        'vlr_count', 'vlr_has_wkt_crs', 'vlr_has_geotiff_crs'
    ]
    POINT_RECORDS = [
        'classes', 'gps_time_min', 'gps_time_max', 'date_start', 'date_end',
        'flightline_start', 'flightline_end'
    ]
    CLASS_FLAGS = [
        'has_synthetic', 'has_keypoint', 'has_withheld', 'has_overlap'
    ]
    EVLR_HDR = [
        'evlr_count', 'evlr_has_wkt_crs', 'evlr_has_geotiff_crs'
    ]
    RGB_ENCODING = "rgb_encoding"
    WKT_BBOX = "wkt_bbox"

    COLUMNS = [
        FILENAME, *PUB_HDR, *GLOBAL_ENCODING, *CRS, *VLR_HDR,
        *POINT_RECORDS, *CLASS_FLAGS, *EVLR_HDR, RGB_ENCODING, WKT_BBOX
    ]


class LaszyReport:

    def __init__(self, file_list: list[str] = None, outdir: str = ".", las_to_json: bool = False, verbose: bool = False):

        """
        Initialize LaszyReport object.

        The argument flist may contain:
            - LAS/LAZ files
            - JSON files holding a Laszy summary (generated from Laszy.summary())
            - Both LAS/LAZ files and JSON files.

        Note that an 'flist' containing both json and las/laz files will be partitioned
        into self.json_list, and self.lidar_list.

        :param file_list: A list containing input files.
        :param outdir: Out directory for tabular dataset (default=".")
        :param las_to_json: When 'True', will write a json summary file for input LAS/LAZ files.
        :param verbose: When 'True', display information about progress to the user.
        """

        self._path = ""
        self._errors = []
        self.outdir = outdir
        self.verbose = verbose
        self._json_completed = []
        self._lidar_completed = []
        self.file_list = file_list
        self.las_to_json = las_to_json
        self._DEFAULT_NAME = "laszy_report.csv"
        self._JSON_LOG_NAME = "json_completed.log"
        self._LIDAR_LOG_NAME = "lidar_completed.log"
        self.json_list = [f for f in file_list if f.endswith('json')]
        self.lidar_list = [f for f in file_list if (f.endswith("laz") or f.endswith("las"))]
        self.__remove_processed_lidar()

    def __remove_processed_lidar(self):
        laszy_json = os.path.join(self.outdir, "laszy_json")
        if os.path.exists(laszy_json):
            self.json_list.extend(
                glob.glob(os.path.join(laszy_json, "*.json"))
            )

        laszy_json_bases = [os.path.basename(json_file) for json_file in self.json_list]
        for lidar_file in self.lidar_list.copy():
            lidar_base = os.path.basename(lidar_file)
            lidar_json = lidar_base.split(".")[0] + ".json"
            if lidar_json in laszy_json_bases:
                self.lidar_list.remove(lidar_file)

    def write(self, name: str = "", validate=False, check_logs: bool = True):

        """
        Write list of LAS/LAZ file summaries to a csv file.

        Static method that accepts a list of LAS/LAZ files and writes
        their respective summaries to rows in a csv file.

        :param validate: When True, function will call validate_report() to output lidar error reports.
        :param check_logs: Check for existing completed logs to ignore previously processed files.
        :param name: Output filename (default='laszy_report.csv')
        """

        existing_data = ""
        if not bool(name):
            name = self._DEFAULT_NAME

        if not name.endswith(".csv"):
            name += ".csv"

        self._path = os.path.join(self.outdir, name)
        if check_logs:
            existing_data = self.__check_logs(existing_data, self._path)

        with open(self._path, "w") as csv:
            self.__write_report(csv, existing_data)

        if validate:
            self.validate_report()

        for is_lidar in [True, False]:
            self.__log_completed(lidar=is_lidar)

        self.__write_err(self._path)

    def validate_report(self, path: str = "", outdir=""):

        if not bool(path):
            path = self._path

        if os.path.exists(path):
            issues = {}
            df = pd.read_csv(path)

            df = df.drop(LASZY_REPORT_DROP_COLUMNS, axis=1)

            df = self.__public_header_check(df, issues)
            df = self.__xyx_scale_check(df, issues)
            df = self.__xyz_offset_check(df, issues)
            df = self.__global_encoding_check(df, issues)
            df = self.__crs_check(df, issues)
            df = self.__point_records_check(df, issues)

            if bool(issues):
                issues = {key: int(issues[key]) for key, value in issues.items()}
                _outdir = os.path.dirname(path) if not bool(outdir) else outdir
                name = os.path.basename(path)
                name_no_ext = name.split(".")[0]

                # write the json summary
                out_summary_name = name_no_ext + "_errors_summary.json"
                with open(os.path.join(_outdir, out_summary_name), "w") as json_summary:
                    json.dump(issues, json_summary, indent=4)

                # write the errors file
                out_csv_name = os.path.join(_outdir, name_no_ext + "_errors.csv")
                df.to_csv(out_csv_name)

    def __write_report(self, csv, existing_data):

        """
        Write final CSV report.

        Private helper method.

        :param csv: Open csv file-like object.
        :param existing_data: Previous CSV data.
        """

        if bool(existing_data):
            csv.write(existing_data)
        else:
            csv.write(",".join(_LaszyReportColumns.COLUMNS) + "\n")
        self.__from_lidar_list(csv)
        self.__from_json_list(csv)

    def __check_logs(self, existing_data, out):

        """
        Check existing log files and inherit data from previous reports (if possible).

        :param existing_data: existing data from previous csv file.
        :param out: out directory.
        """

        for is_lidar in [False, True]:
            self.__check_for_completed(lidar=is_lidar)
        if os.path.exists(out):
            with open(out, "r") as f:
                existing_data = f.read()
        return existing_data

    def __log_completed(self, lidar: bool = False):

        """
        Write a list of processed files to a log file.

        :param lidar: When True, will write LiDAR log, otherwise, will write JSON log.
        """

        completed = self._lidar_completed if lidar else self._json_completed
        out_name = self._LIDAR_LOG_NAME if lidar else self._JSON_LOG_NAME

        if bool(completed):
            with open(os.path.join(self.outdir, out_name), "w") as f:
                for file in completed:
                    f.write(file + "\n")

    def __write_err(self, out):

        """
        Write any errors encountered to log file.

        :param out: Output report name.
        """

        if bool(self._errors):
            with open(f"{out}_exceptions.log", "w") as err_log:
                for err in self._errors:
                    fname = err[0]
                    exception = err[1]
                    err_log.write(fname + f"\n\t{exception}\n")

    def __from_lidar_list(self, csv):

        """
        Write rows ro open CSV file from list of lidar files (LAS/LAZ).

        :param csv: Open file pointer to CSV file object.
        """

        if bool(self.lidar_list):
            json_outdir = os.path.join(self.outdir, "laszy_json") if self.las_to_json else ""
            files = tqdm.tqdm(self.lidar_list, desc="Processing LAS/LAZ files...") if self.verbose else self.lidar_list
            for file in files:
                las = Laszy(file)
                try:
                    s = las.summarize(outdir=json_outdir)
                    row = self.__get_row(s)
                    csv.write(",".join(row) + "\n")
                    self._lidar_completed.append(file)

                except Exception as e:
                    is_possibly_corrupt = (not bool(las.public_header_block))
                    self._errors.append(
                        (file, (CORRUPT_FILE_MSG if is_possibly_corrupt else e) + "\n")
                    )

    def __from_json_list(self, csv):

        """
        Write rows to CSV file from list of json files.

        :param csv: Open file pointer to CSV file object.
        """

        if bool(self.json_list):
            files = tqdm.tqdm(self.json_list, desc="Processing JSON files...") if self.verbose else self.json_list
            for file in files:
                try:
                    with open(file, "r") as f:
                        summary = json.load(f)
                        row = self.__get_row(summary)
                        csv.write(",".join(row) + "\n")
                    self._json_completed.append(file)

                except Exception as e:
                    self._errors.append((file, e))

    def __check_for_completed(self, lidar: bool = False):

        """
        Check for existing logs to see if files should be skipped.

        Checks in self.outdir directory for 'lidar_completed.log' or
        'json_completed.log'. If either of these files exist, the contents
        will be compared with 'self.las_list' and 'self.json_list'.

        If filenames are present in both the log files and the completed logs,
        these files will be removed from processing.

        This feature is implemented in an effort to keep the utility from
        executing files that have already been processed.

        :param lidar: When True, will check lidar logs, otherwise, will check json logs.
        """

        file_list = self.lidar_list if lidar else self.json_list
        log_name = self._LIDAR_LOG_NAME if lidar else self._JSON_LOG_NAME

        log = os.path.join(self.outdir, log_name)
        if os.path.exists(log):
            with open(log, "r") as f:
                contents = f.read()
                ignore_list = contents.split("\n")

            set_ignore = set(ignore_list)
            set_file_list = set(file_list)
            file_list_ = list(set_file_list.difference(set_ignore))

            if lidar:
                self.lidar_list = file_list_
            else:
                self.json_list = file_list_

    @staticmethod
    def __get_row(summary: dict) -> list[str]:

        """
        Get a single row for output csv.

        Uses the keys stored in enum class '_LaszyReportColumns' to
        retrieve the values stored in a json dictionary that represents
        a Laszy summary and casts all values to a string.

        :param summary: Dictionary object containing laszy summary data.
        :return: List of strings containing each values in laszy summary.
        """

        pr = summary["point_records"]
        phb = summary["public_header_block"]
        pub_hdr_vals = [str(phb[key]) for key in _LaszyReportColumns.PUB_HDR]
        ge_vals = [str(phb["global_encoding"][key]) for key in _LaszyReportColumns.GLOBAL_ENCODING]
        crs_vals = [str(summary["crs"][key]) for key in _LaszyReportColumns.CRS]
        vlr_vals = [str(summary["vlrs"][key]) for key in _LaszyReportColumns.VLR_HDR]
        point_vals = [str(pr[key]) for key in _LaszyReportColumns.POINT_RECORDS]
        evlr_vals = [str(summary["evlrs"][key]) for key in _LaszyReportColumns.EVLR_HDR]

        flag_vals = [
            (str(pr["class_flags"][key]) if bool(pr["class_flags"]) else "N/A")
            for key in _LaszyReportColumns.CLASS_FLAGS
        ]

        row = [
            summary["filename"], *pub_hdr_vals, *ge_vals, *crs_vals,
            *vlr_vals, *point_vals, *flag_vals, *evlr_vals, str(summary["rgb_encoding"]), summary["wkt_bbox"]
        ]

        # make sure to wrap each row item in quotes
        # if the item contains a csv seperator in it
        for i in range(len(row)):
            if row[i].find(",") >= 0:
                row[i] = f"\"{row[i]}\""

        return row

    @staticmethod
    def __global_encoding_check(df, issues):

        """Check global encoding value for issues"""

        df['global_encoding'] = df['global_encoding'].apply(LaszyReport.__is_globalencoding_invalid)
        col = df["global_encoding"] != ""
        if col.sum() > 0:
            issues.update({"global_encoding_value": col.sum()})
        else:
            df = df.drop("global_encoding", axis=1)

        df['wkt_crs'] = df['wkt_crs'].apply(LaszyReport.__is_wktflag_invalid)
        col = df["wkt_crs"] != ""
        if col.sum() > 0:
            issues.update({"wkt_crs_flag": col.sum()})
        else:
            df = df.drop("wkt_crs", axis=1)

        df['gps_standard_time'] = df['gps_standard_time'].apply(LaszyReport.__is_gpstimeflag_invalid)
        col = df["gps_standard_time"] != ""
        if col.sum() > 0:
            issues.update({"gps_time_flag": col.sum()})
        else:
            df = df.drop("gps_standard_time", axis=1)
        # guid contract number check
        df['synthetic_returns'] = df['synthetic_returns'].apply(LaszyReport.__is_syntheticflag_invalid)
        col = df["synthetic_returns"] != ""
        if col.sum() > 0:
            issues.update({"synthetic_returns_flag": col.sum()})
        else:
            df = df.drop("synthetic_returns", axis=1)

        return df

    @staticmethod
    def __xyz_offset_check(df, issues):

        """Check XYZ offset for issues."""

        df['x_offset'] = df['x_offset'].apply(LaszyReport.__is_xoffset_invalid)
        col = df["x_offset"] != ""
        if col.sum() > 0:
            issues.update({"x_offset": col.sum()})
        else:
            df = df.drop("x_offset", axis=1)

        df['y_offset'] = df['y_offset'].apply(LaszyReport.__is_yoffset_invalid)
        col = df["y_offset"] != ""
        if col.sum() > 0:
            issues.update({"y_offset": col.sum()})
        else:
            df = df.drop("y_offset", axis=1)

        df['z_offset'] = df['z_offset'].apply(LaszyReport.__is_zoffset_invalid)
        col = df["z_offset"] != ""
        if col.sum() > 0:
            issues.update({"z_offset": col.sum()})
        else:
            df = df.drop("z_offset", axis=1)

        return df

    @staticmethod
    def __xyx_scale_check(df, issues):

        """Check XYZ scaling for issues."""

        # guid contract number check
        df['x_scale'] = df['x_scale'].apply(LaszyReport.__is_xscale_invalid)
        col = df["x_scale"] != ""
        if col.sum() > 0:
            issues.update({"x_scale": col.sum()})
        else:
            df = df.drop("x_scale", axis=1)

        # guid contract number check
        df['y_scale'] = df['y_scale'].apply(LaszyReport.__is_yscale_invalid)
        col = df["y_scale"] != ""
        if col.sum() > 0:
            issues.update({"y_scale": col.sum()})
        else:
            df = df.drop("y_scale", axis=1)

        # guid contract number check
        df['z_scale'] = df['z_scale'].apply(LaszyReport.__is_zscale_invalid)
        col = df["z_scale"] != ""
        if col.sum() > 0:
            issues.update({"z_scale": col.sum()})
        else:
            df = df.drop("z_scale", axis=1)

        return df

    @staticmethod
    def __point_records_check(df, issues):

        """Check point record fields for any issues with data."""

        # check for class code 0
        df['classes'] = df['classes'].apply(LaszyReport.__is_neverclassified_points)
        col = df["classes"] != ""
        if col.sum() > 0:
            issues.update({"points_in_never_classified": col.sum()})
        else:
            df = df.drop("classes", axis=1)

        # check for invalid flightline numbers
        df['flightline_start'] = df['flightline_start'].apply(LaszyReport.__is_flightlines_invalid)
        col = df["flightline_start"] != ""
        if col.sum() > 0:
            issues.update({"invalid_flightline_numbers": col.sum()})
        else:
            df = df.drop(["flightline_start", "flightline_end"], axis=1)

        # check for invalid gps times
        df['gps_time_min'] = df['gps_time_min'].apply(LaszyReport.__is_gpsweektime_present)
        col = df["gps_time_min"] != ""
        if col.sum() > 0:
            df = df.drop("gps_time_max", axis=1)
            issues.update({"gps_week_time_found": col.sum()})
        else:
            df = df.drop(["gps_time_min", "gps_time_max"], axis=1)

        # check for synthetic flags
        df['has_synthetic'] = df['has_synthetic'].apply(LaszyReport.__is_syntheticclassflag_invalid)
        col = df["has_synthetic"] != ""
        if col.sum() > 0:
            issues.update({"synthetic_class_flags": col.sum()})
        else:
            df = df.drop("has_synthetic", axis=1)

        # check if no wkt crs is present at all
        df['date_end'] = df['date_end'].apply(LaszyReport.__is_date_from_future)
        col = df["date_end"] != ""
        if col.sum() > 0:
            df["invalid_dates"] = col
            issues.update({"invalid_dates_found": col.sum()})
        df = df.drop('date_end', axis=1)

        return df

    @staticmethod
    def __crs_check(df, issues):

        """Check CRS for any issues."""

        # check for existence of compound crs
        df['compd_cs'] = df['compd_cs'].apply(LaszyReport.__is_compdcs_invalid)
        col = df["compd_cs"] != ""
        if col.sum() > 0:
            issues.update({"compd_cs": col.sum()})
        else:
            df = df.drop('compd_cs', axis=1)

        # check the vertical datum
        df['vert_datum'] = df['vert_datum'].apply(LaszyReport.__is_vertdatum_invalid)
        col = df["vert_datum"] != ""
        if col.sum() > 0:
            issues.update({"vert_datum": col.sum()})
        else:
            df = df.drop('vert_datum', axis=1)

        # check the horizontal datum
        df['hz_datum'] = df['hz_datum'].apply(LaszyReport.__is_hzdatum_invalid)
        col = df["hz_datum"] != ""
        if col.sum() > 0:
            issues.update({"hz_datum": col.sum()})
        else:
            df = df.drop('hz_datum', axis=1)

        # check if no wkt crs is present at all
        df['vlr_has_wkt_crs'] = df['vlr_has_wkt_crs'].apply(LaszyReport.__is_vlrwkt_empty)
        df['evlr_has_wkt_crs'] = df['evlr_has_wkt_crs'].apply(LaszyReport.__is_vlrwkt_empty)
        col_vlr = df["vlr_has_wkt_crs"] != ""
        col_evlr = df["evlr_has_wkt_crs"] != ""
        col = col_vlr & col_evlr
        if ~col.sum() > 0:
            df["no_wkt_found"] = col
            issues.update({"vlr_has_wkt_crs": col.sum()})
        df = df.drop(['vlr_has_wkt_crs', 'evlr_has_wkt_crs'], axis=1)

        return df

    @staticmethod
    def __public_header_check(df, issues):

        # guid contract number check
        df['guid_asc'] = df['guid_asc'].apply(LaszyReport.__is_contract_invalid)
        col = df["guid_asc"] != ""
        if col.sum() > 0:
            issues.update({"guid_contract_number": col.sum()})
        else:
            df = df.drop("guid_asc", axis=1)

        # System ID format check
        df['system_id'] = df['system_id'].apply(LaszyReport.__is_systemid_invalid)
        col = df["system_id"] != ""
        if col.sum() > 0:
            issues.update({"system_id_format": col.sum()})
        else:
            df = df.drop("system_id", axis=1)

        # version check
        df['version'] = df['version'].apply(LaszyReport.__is_lasversion_invalid)
        col = df["version"] != ""
        if col.sum() > 0:
            issues.update({"version": col.sum()})
        else:
            df = df.drop("version", axis=1)

        # Point data record format check
        df['point_data_format'] = df['point_data_format'].apply(LaszyReport.__is_pointformat_invalid)
        col = df["point_data_format"] != ""
        if col.sum() > 0:
            issues.update({"point_data_format": col.sum()})
        else:
            df = df.drop("point_data_format", axis=1)

        if ACQUISITON:
            # File source id vs filename number check
            df['filename_has_correct_source_id'] = df.apply(LaszyReport.__is_sourceid_valid, axis=1)
            col = df['filename_has_correct_source_id'] != ""
            if col.sum() > 0:
                issues.update({"filename_has_correct_source_id": col.sum()})
            else:
                df = df.drop("filename_has_correct_source_id", axis=1)

        return df

    @staticmethod
    def __is_sourceid_valid(row):
        numb5 = str(row["filename"]).split("_")[0]
        fsid = str(row["file_source_id"])
        return "Correct" if fsid == numb5 else "Filename does not contain File Source ID"

    @staticmethod
    def __is_syntheticclassflag_invalid(synthetic_class_flag: bool):
        expected = False
        if not math.isnan(synthetic_class_flag) and synthetic_class_flag != expected:
            return synthetic_class_flag
        else:
            return ""

    @staticmethod
    def __is_gpsweektime_present(gps_min_time: int):
        max_gps_week_time = 604800
        if max_gps_week_time >= gps_min_time:
            return str(gps_min_time)
        else:
            return ""

    @staticmethod
    def __is_flightlines_invalid(point_source_id: int):
        min_valid_fl = 1
        if point_source_id < min_valid_fl:
            return str(point_source_id)
        else:
            return ""

    @staticmethod
    def __is_neverclassified_points(classes: str):
        expected = 0
        classes = classes.replace("[", "").replace("]", "")
        classes = [int(val) for val in classes.split(",")]
        if expected in classes:
            return str(classes)
        else:
            return ""

    @staticmethod
    def __is_vlrwkt_empty(vlr_has_wkt: bool):
        expected = True
        if vlr_has_wkt != expected:
            return vlr_has_wkt
        else:
            return ""

    @staticmethod
    def __is_hzdatum_invalid(hz_datum: str):
        expected = "NAD83_Canadian_Spatial_Reference_System"
        if hz_datum != expected:
            return hz_datum
        else:
            return ""

    @staticmethod
    def __is_vertdatum_invalid(vert_datum: str):
        expected = "Canadian Geodetic Vertical Datum of 2013"
        if vert_datum != expected:
            return vert_datum
        else:
            return ""

    @staticmethod
    def __is_compdcs_invalid(compdcs: str):
        expected = bool(compdcs)
        if not expected:
            return "No compound projection"
        else:
            return ""

    @staticmethod
    def __is_contract_invalid(guid: str):
        expected = re.compile(RegexLidar.CONTRACT_NUMBER)
        if bool(guid):
            if (not isinstance(guid, str)) and (not isinstance(guid, bytes)):
                return "unknown format"
            elif not bool(expected.search(guid)):
                return guid
            else:
                return ""
        return "No GUID found"

    @staticmethod
    def __is_systemid_invalid(system_id: str):
        expected = re.compile(RegexLidar.SYSTEM_ID_PRODUCTION)
        if bool(system_id):
            if (not isinstance(system_id, str)) and (not isinstance(system_id, bytes)):
                return "unknown format"
            elif not bool(expected.search(system_id)):
                return system_id
            else:
                return ""
        return "No System ID found"

    @staticmethod
    def __is_lasversion_invalid(lasversion: float):
        expected = 1.4
        if lasversion != expected:
            return str(lasversion)
        else:
            return ""

    @staticmethod
    def __is_pointformat_invalid(pointformat: int):
        expected = 6
        if pointformat != expected:
            return str(pointformat)
        else:
            return ""

    @staticmethod
    def __is_xscale_invalid(xscale: float):
        expected = 0.01
        if xscale != expected:
            return str(xscale)
        else:
            return ""

    @staticmethod
    def __is_yscale_invalid(yscale: float):
        expected = 0.01
        if yscale != expected:
            return str(yscale)
        else:
            return ""

    @staticmethod
    def __is_zscale_invalid(zscale: float):
        expected = 0.01
        if zscale != expected:
            return str(zscale)
        else:
            return ""

    @staticmethod
    def __is_xoffset_invalid(xoffset: float):
        expected = 0
        modulo = float(xoffset) % 1
        if modulo != expected:
            return str(xoffset)
        else:
            return ""

    @staticmethod
    def __is_yoffset_invalid(yoffset: float):
        expected = 0
        modulo = float(yoffset) % 1
        if modulo != expected:
            return str(yoffset)
        else:
            return ""

    @staticmethod
    def __is_zoffset_invalid(zoffset: float):
        expected = 0
        modulo = float(zoffset) % 1
        if modulo != expected:
            return str(zoffset)
        else:
            return ""

    @staticmethod
    def __is_globalencoding_invalid(value: int):
        expected = 17
        if value != expected:
            return str(value)
        else:
            return ""

    @staticmethod
    def __is_wktflag_invalid(flag: bool):
        expected = True
        if flag != expected:
            return flag
        else:
            return ""

    @staticmethod
    def __is_gpstimeflag_invalid(flag: bool):
        expected = True
        if flag != expected:
            return flag
        else:
            return ""

    @staticmethod
    def __is_syntheticflag_invalid(flag: bool):
        expected = False
        if flag != expected:
            return flag
        else:
            return ""

    @staticmethod
    def __is_date_from_future(date: str):
        today = datetime.datetime.today()
        in_date = date.split(" ")[0]
        ymd = in_date.split("-")

        # first check if GpsWeekTimeError string is present
        is_invalid_date = date == GPS_WEEK_TIME_ERR_STR
        if not is_invalid_date:  # now check the actual date
            year, month, day = int(ymd[0]), int(ymd[1]), int(ymd[2])
            invalid_year = today.year < year
            invalid_month = (today.year == year) and (today.month < month)
            invalid_day = (today.year == year) and (today.month == month) and (today.day < day)
            is_invalid_date = invalid_day or invalid_month or invalid_year
        if is_invalid_date:
            return date
        else:
            return ""


class NotLidarFileError(Exception):
    """
    Exception raised for non LAS/LAZ file input.
    """

    def __init__(self, message="File is not a LAS/LAZ file"):
        self.message = message
        super().__init__(self.message)


def main():

    wackadoo_list = glob.glob("/home/jordan/work/geobc/test_data/wackadoo/*.laz")
    wackadoo_list.extend(
        glob.glob("/home/jordan/work/geobc/test_data/wackadoo/*.las")
    )

    # file = "/media/jordan/EMBC_SKUPPA/problem_files/bcts_092l062_4_2_3_xc_31_12_2012.laz"
    # las = Laszy(file)

    report = LaszyReport(wackadoo_list, las_to_json=True, verbose=True)
    report.write("wacky", validate=True, check_logs=True)


if __name__ == "__main__":
    main()
