

class CrsType:
    PROJECTION = "PROJECTION"
    VERT_DATUM = "VERT_DATUM"
    COMPD_CS = "COMPD_CS"
    SPHEROID = "SPHEROID"
    VERT_CS = "VERT_CS"
    PROJCRS = "PROJCRS"
    HZ_DATUM = "DATUM"
    PROJCS = "PROJCS"
    GEOGCS = "GEOGCS"
    TYPES = [
        PROJECTION,
        VERT_DATUM,
        COMPD_CS,
        SPHEROID,
        VERT_CS,
        HZ_DATUM,
        PROJCS,
        GEOGCS
    ]


class WktCrsInfo:

    def __init__(self, wkt_crs: str):

        """
        Initialize a WktCrsInfo object.

        Initializes a WktCrsInfo object. When wkt_crs is passed as an argument,
        the constructor will call self.parse(wkt_crs) by default, and attempt to
        assign all the object properties.

        Note that the user may pass any string (e.g. 'Hi, I like cheese') to WktCrsInfo.
        In this event, WktCrsInfo will only make an attempt to parse out WKT information,
        leaving all object properties empty on failure.

        :param wkt_crs: A raw wkt string.
        """

        self.string = wkt_crs
        self.projection = ""
        self.vert_datum = ""
        self.compd_cs = ""
        self.spheroid = ""
        self.hz_datum = ""
        self.vert_cs = ""
        self.proj_cs = ""
        self.geog_cs = ""

        if wkt_crs:
            self.parse(wkt_crs)

    def get_compound_crs(self, wkt_crs: str = None) -> str:

        """
        :return:String from WKT projection indicating compound coordinate system.
        :return:Empty string if no information is found.
        """

        if not bool(wkt_crs):
            return self.compd_cs

        if not bool(self.compd_cs) and (CrsType.COMPD_CS in wkt_crs):
            data = wkt_crs[wkt_crs.index(CrsType.COMPD_CS):]
            self.compd_cs = data.split("\"", maxsplit=3)[1]

        return self.compd_cs

    def get_vert_crs(self, wkt_crs: str = None) -> str:

        """
        :return:String from WKT projection indicating compound coordinate system.
        :return:Empty string if no information is found.
        """

        if not bool(wkt_crs):
            return self.vert_cs

        if not bool(self.vert_cs) and (CrsType.VERT_CS in wkt_crs):
            data = wkt_crs[wkt_crs.index(CrsType.VERT_CS):]
            self.vert_cs = data.split("\"", maxsplit=3)[1]

        return self.vert_cs

    def get_hz_crs(self, wkt_crs: str = None) -> str:

        """
        :return:String from WKT projection indicating compound coordinate system.
        :return:Empty string if no information is found.
        """

        if not bool(wkt_crs):
            return self.proj_cs

        projcs_str = ""
        if CrsType.PROJCRS in wkt_crs:
            projcs_str = CrsType.PROJCRS
        elif CrsType.PROJCS in wkt_crs:
            projcs_str = CrsType.PROJCS

        if not bool(self.proj_cs) and bool(projcs_str):
            data = wkt_crs[wkt_crs.index(projcs_str):]
            self.proj_cs = data.split("\"", maxsplit=3)[1]

        return self.proj_cs

    def get_projection(self, wkt_crs: str = None) -> str:

        """
        :return:String from WKT projection indicating compound coordinate system.
        :return:Empty string if no information is found.
        """

        if not bool(wkt_crs):
            return self.projection

        if not bool(self.projection) and (CrsType.PROJECTION in wkt_crs):
            data = wkt_crs[wkt_crs.index(CrsType.PROJECTION):]
            self.projection = data.split("\"", maxsplit=3)[1]

        return self.projection

    def get_vert_datum(self, wkt_crs: str = None) -> str:

        """
        :return:String from WKT projection indicating compound coordinate system.
        :return:Empty string if no information is found.
        """

        if not bool(wkt_crs):
            return self.vert_datum

        if not bool(self.vert_datum) and (CrsType.VERT_DATUM in wkt_crs):
            data = wkt_crs[wkt_crs.index(CrsType.VERT_DATUM):]
            self.vert_datum = data.split("\"", maxsplit=3)[1]

        return self.vert_datum

    def get_spheroid(self, wkt_crs: str = None) -> str:

        """
        :return:String from WKT projection indicating compound coordinate system.
        :return:Empty string if no information is found.
        """

        if not bool(wkt_crs):
            return self.spheroid

        if not bool(self.spheroid) and (CrsType.SPHEROID in wkt_crs):
            data = wkt_crs[wkt_crs.index(CrsType.SPHEROID):]
            self.spheroid = data.split("\"", maxsplit=3)[1]

        return self.spheroid

    def get_hz_datum(self, wkt_crs: str = None) -> str:

        """
        :return:String from WKT projection indicating compound coordinate system.
        :return:Empty string if no information is found.
        """

        if not bool(wkt_crs):
            return self.hz_datum

        if not bool(self.hz_datum) and (CrsType.HZ_DATUM in wkt_crs):
            data = wkt_crs[wkt_crs.index(CrsType.HZ_DATUM):]
            self.hz_datum = data.split("\"", maxsplit=3)[1]

        return self.hz_datum

    def get_geog_crs(self, wkt_crs: str = None) -> str:

        """
        :return:String from WKT projection indicating compound coordinate system.
        :return:Empty string if no information is found.
        """

        if not bool(wkt_crs):
            return self.geog_cs

        if not bool(self.geog_cs) and (CrsType.GEOGCS in wkt_crs):
            data = wkt_crs[wkt_crs.index(CrsType.GEOGCS):]
            self.geog_cs = data.split("\"", maxsplit=3)[1]

        return self.geog_cs

    def parse(self, wkt_crs):

        """
        Parse a raw WKT string.

        Parses the input argument and attempts to fill all object properties
        with appropriate CRS elements.

        If called on an existing WktCrsInfo object, existing object properties
        will be overwritten.

        :param wkt_crs: A raw WKT CRS string.
        """

        if self.is_wkt_crs(wkt_crs):
            self.get_hz_crs(wkt_crs)
            self.get_vert_crs(wkt_crs)
            self.get_geog_crs(wkt_crs)
            self.get_spheroid(wkt_crs)
            self.get_hz_datum(wkt_crs)
            self.get_compound_crs(wkt_crs)
            self.get_projection(wkt_crs)
            self.get_vert_datum(wkt_crs)

    def to_string(self):

        """
        Dump CRS object to a string.

        Dumps the object properties in 'key: value \n'
        format for representation or debugging purposes.
        """

        crsinfo_str = ""

        for key, value in self.__dict__.items():
            crsinfo_str += (key + ":\t" + value + "\n")

        return crsinfo_str

    def get_proj_epsg(self) -> int:

        """
        Get the epsg from the projected crs.

        Retrieves the epsg code from the projected (hz) coordinate
        system within a wkt.

        :return: EPSG code if successful, else, -1
        """

        wkt = self.string
        if not (CrsType.PROJCS in wkt):
            return -1

        hz_start = wkt.index(CrsType.PROJCS)
        data = wkt[hz_start:]

        # use the classic stack-based approach to validating parenthesis counts
        # to navigate our way to the desired EPSG code.
        brackets = ["["]
        i = data.index("[") + 1
        while len(brackets) > 0:
            if data[i] == "]":
                brackets.pop()
            if data[i] == "[":
                brackets.append("[")
            i += 1
        hz_data = data[:i]

        try:
            epsg_start = hz_data.rindex("EPSG")
        except ValueError:
            return -1

        epsg_data = hz_data[epsg_start: i]
        epsg_str = epsg_data.split(",")[1]

        epsg = ""
        for char in epsg_str:
            if char.isnumeric():
                epsg += char

        if bool(epsg):
            return int(epsg)
        else:
            return -1

    def get_vert_epsg(self) -> int:

        """
        Get the epsg from the projected crs.

        Retrieves the epsg code from the projected (hz) coordinate
        system within a wkt.

        :return: EPSG code if successful, else, -1
        """

        wkt = self.string
        if not (CrsType.PROJCS in wkt):
            return -1

        hz_start = wkt.index(CrsType.VERT_CS)
        data = wkt[hz_start:]

        # use the classic stack-based approach to validating parenthesis counts
        # to navigate our way to the desired EPSG code.
        brackets = ["["]
        i = data.index("[") + 1
        while len(brackets) > 0:
            if data[i] == "]":
                brackets.pop()
            if data[i] == "[":
                brackets.append("[")
            i += 1
        hz_data = data[:i]

        try:
            epsg_start = hz_data.rindex("EPSG")
        except ValueError:
            return -1

        epsg_data = hz_data[epsg_start: i]
        epsg_str = epsg_data.split(",")[1]

        epsg = ""
        for char in epsg_str:
            if char.isnumeric():
                epsg += char

        if bool(epsg):
            return int(epsg)
        else:
            return -1

    def get_epsg(self, crs_type: str):

        """
        Get epsg based on crs type.

        All input string constants are stored in CrsType enum object.
            >> from WktCrsInfo import CrsType
        Constants may be used via CrsType object:
            >> CrsType.VERT_DATUM
        Or passed via string literal:
            >> "VERT_DATUM"

        Valid input values for crs_type:
            CrsType.VERT_DATUM: "VERT_DATUM"
            CrsType.SPHEROID: "SPHEROID"
            CrsType.VERT_CS: "VERT_CS"
            CrsType.HZ_DATUM: "DATUM"
            CrsType.PROJCS: "PROJCS"
            CrsType.GEOGCS: "GEOGCS"

        Invalid input values for crs_type:
            CrsType.COMPD_CS: "COMPD_CS"
            CrsType.PROJECTION: "PROJECTION"

        :param crs_type: Any string contained within object CrsType
        :return: Epsg code as integer if successful, -1 if failure.
        """

        wkt = self.string
        has_epsg = [
            CrsType.SPHEROID, CrsType.VERT_CS, CrsType.HZ_DATUM,
            CrsType.PROJCS, CrsType.GEOGCS, CrsType.VERT_DATUM
        ]

        if crs_type not in has_epsg:
            return -1  # invalid crs string passed

        if not (crs_type in wkt):
            return -1  # crs type not present in wkt string

        hz_start = wkt.index(crs_type)
        data = wkt[hz_start:]

        # use the classic stack-based approach to validating parenthesis counts
        # to navigate our way to the desired EPSG code.
        brackets = ["["]
        i = data.index("[") + 1
        while len(brackets) > 0:
            if data[i] == "]":
                brackets.pop()
            if data[i] == "[":
                brackets.append("[")
            i += 1
        hz_data = data[:i]

        try:
            epsg_start = hz_data.rindex("EPSG")
        except ValueError:
            return -1

        epsg_data = hz_data[epsg_start: i]
        epsg_str = epsg_data.split(",")[1]

        epsg = ""
        for char in epsg_str:
            if char.isnumeric():
                epsg += char

        if bool(epsg):
            return int(epsg)
        else:
            return -1

    @staticmethod
    def is_wkt_crs(wkt_crs: str) -> bool:
        """
        :param wkt_crs:
        :return: True or False
        """

        for cs in CrsType.TYPES:
            if cs in wkt_crs:
                return True

        return False


def main():

    wkt_crs = r'COMPD_CS["NAD83(CSRS) / UTM zone 10N + CGVD2013 height - CGG2013 (meters)",PROJCS["NAD83(CSRS) / UTM ' \
              r'zone 10N",GEOGCS["NAD83(CSRS)",DATUM["NAD83_Canadian_Spatial_Reference_System",SPHEROID["GRS 1980",' \
              r'6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6140"]],' \
              r'PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY' \
              r'["EPSG","9122"]],AUTHORITY["EPSG","4617"]],PROJECTION["Transverse_Mercator"],PARAMETER' \
              r'["latitude_of_origin",0],PARAMETER["central_meridian",-123],PARAMETER["scale_factor",0.9996],' \
              r'PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["meter",1,AUTHORITY' \
              r'["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],AUTHORITY["EPSG","3157"]],VERT_CS' \
              r'["CGVD2013 height - CGG2013 (meters)",VERT_DATUM["Canadian Geodetic Vertical Datum of 2013",2005,' \
              r'AUTHORITY["EPSG","1127"]],UNIT["meter",1,AUTHORITY["EPSG","9001"]],AXIS["Up",UP],' \
              r'AUTHORITY["EPSG","6647"]]]'

    info = WktCrsInfo(wkt_crs)


if __name__ == "__main__":
    main()

# COMPD_CS["NAD83(CSRS) / UTM zone 10N + CGVD2013",
#     PROJCS["NAD83(CSRS) / UTM zone 10N",
#         GEOGCS["NAD83(CSRS)",
#             DATUM["NAD83_Canadian_Spatial_Reference_System",
#                 SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],
#                 AUTHORITY["EPSG","6140"]
#             ],
#             PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],
#             UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],
#             AUTHORITY["EPSG","4617"]
#         ],
#         PROJECTION["Transverse_Mercator"],
#         PARAMETER["latitude_of_origin",0],
#         PARAMETER["central_meridian",-123],
#         PARAMETER["scale_factor",0.9996],
#         PARAMETER["false_easting",500000],
#         PARAMETER["false_northing",0],
#         UNIT["metre",
#             1,
#             AUTHORITY["EPSG","9001"]
#         ],
#         AXIS["Easting",EAST],
#         AXIS["Northing",NORTH],
#         AUTHORITY["EPSG","3157"]
#     ],
#     VERT_CS["CGVD2013",
#         VERT_DATUM["Canadian Geodetic Vertical Datum of 2013",2005,AUTHORITY["EPSG","1127"]],
#         UNIT["metre",1.0,AUTHORITY["EPSG","9001"]],
#         AXIS["Gravity-related height",UP],
#         AUTHORITY["EPSG","6647"]
#     ]
# ]
