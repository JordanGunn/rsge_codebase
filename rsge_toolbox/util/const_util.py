
class EpsgCode:

    """
    EPSG code constants.

    @param MIN: 1024
    @param MAX: 32767
    @param WGS_84: 4326
    @param NAD_83_CSRS_UTM_Z11: 2955
    @param NAD_83_CSRS_UTM_Z10: 3157
    @param NAD_83_CSRS_UTM_Z09: 3156
    @param NAD_83_CSRS_UTM_Z08: 3155
    @param NAD_83_CSRS_UTM_Z07: 3154
    @param NAD_83_CSRS_BC_ALBERS: 3005
    @param EPSG_DICT_CODE_TO_TUPLE_WKT_PROJ: Epsg codes mapped to a tuple containing WKT [0] and proj [1] CRS strings.

    """

    MIN = 1024
    MAX = 32767
    WGS_84 = 4326
    NAD_83_CSRS_UTM_Z11 = 2955
    NAD_83_CSRS_UTM_Z10 = 3157
    NAD_83_CSRS_UTM_Z09 = 3156
    NAD_83_CSRS_UTM_Z08 = 3155
    NAD_83_CSRS_UTM_Z07 = 3154
    NAD_83_CSRS_BC_ALBERS = 3005
    EPSG_DICT_CODE_TO_TUPLE_WKT_PROJ = {
        NAD_83_CSRS_UTM_Z11: ("EPSG 2955: NAD83(CSRS) / UTM zone 11 N", "nad83csrs_utm11n"),
        NAD_83_CSRS_UTM_Z10: ("EPSG 3157: NAD83(CSRS) / UTM zone 10 N", "nad83csrs_utm10n"),
        NAD_83_CSRS_UTM_Z09: ("EPSG 3156: NAD83(CSRS) / UTM zone 9 N", "nad83csrs_utm09n"),
        NAD_83_CSRS_UTM_Z08: ("EPSG 3155: NAD83(CSRS) / UTM zone 8 N", "nad83csrs_utm08n"),
        NAD_83_CSRS_UTM_Z07: ("EPSG 3154: NAD83(CSRS) / UTM zone 7 N", "nad83csrs_utm07n"),
        NAD_83_CSRS_BC_ALBERS: ("EPSG 3005: NAD83 / BC Albers", "nad83_bc_albers")
    }