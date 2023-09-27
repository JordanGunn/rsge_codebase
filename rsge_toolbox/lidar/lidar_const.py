# ===============================================================
# -- Valid lidar class numbers
# ===============================================================
class _LidarClass:

    """
    Child LidarClass Object.

    :param name: Name of lidar Class. (e.g. "ground")
    :param number: Integer value assigned to lidar class. (e.g. 2)
    """

    def __init__(self, number, name):
        self.name = name
        self.number = number


class LidarClass:

    """
    Constant class containing valid ASPRS lidar classifications.
    Composed of _LidarClass objects.

    :param DEFAULT: (1, "default")
    :param GROUND: (2, 'ground')
    :param HIGH_VEGETATION: (5, 'high_vegetation')
    :param OUTLIERS: (7, 'outliers')
    :param WATER: (9, 'water')
    :param HIGH_NOISE: (18, 'high_noise')
    :param IGNORED_GROUND: (20, 'ignored_ground')
    :param DICT: Dictionary mapping all class numbers to names.
    """

    DEFAULT = _LidarClass(1, "default")
    GROUND = _LidarClass(2, 'ground')
    HIGH_VEGETATION = _LidarClass(5, 'high_vegetation')
    OUTLIERS = _LidarClass(7, 'outliers')
    WATER = _LidarClass(9, 'water')
    HIGH_NOISE = _LidarClass(18, 'high_noise')
    IGNORED_GROUND = _LidarClass(20, 'ignored_ground')
    DICT = {
        1: "default",
        2: 'ground',
        5: 'high_vegetation',
        7: 'outliers',
        9: 'water',
        18: 'high_noise',
        20: 'ignored_ground'
    }


class _VlrRecordId:

    def __init__(self, user_id, record_id):
        self.user_id = user_id
        self.record_id = record_id


class ASPRS:

    class VlrRecordType:

        MATH_TRANSFORM_WKT = _VlrRecordId("LASF_Projection", 2111)
        CRS_WKT = _VlrRecordId("LASF_Projection", 2112)
        CRS_GEOTIFF_KEY_DIR = _VlrRecordId("LASF_Projection", 34735)
        CRS_GEOTIFF_DOUBLE_PARAMS = _VlrRecordId("LASF_Projection", 34736)
        CRS_GEOTIFF_ASCII_PARAMS = _VlrRecordId("LASF_Projection", 34737)
        CLASSIFICATION_LOOKUP = _VlrRecordId("LASF_Spec", 0)
        TEXT_AREA_DESCRIPTION = _VlrRecordId("LASF_Spec", 3)
        EXTRA_BYTES = _VlrRecordId("LASF_Spec", 4)
        SUPERSEDED = _VlrRecordId("LASF_Spec", 7)
        USER_ID_LASF_PROJ = "LASF_Projection"
        USER_ID_LASF_Spec = "LASF_Spec"
        RECORDS_IDS = [2111, 2112, 34735, 34736, 34737, 0, 3, 4, 7]
        USER_IDS = ["LASF_Projection", "LASF_Spec"]

    class GlobalEncodingFlag:
        """
        'enum' Class containing named global encoding bit-field flags.
        """

        HAS_GPS_STANDARD_TIME = 1
        HAS_WAVEFORM_PACKETS_INTERNAL = 2
        HAS_WAVEFORM_PACKETS_EXTERNAL = 4
        HAS_SYNTHETIC_RETURN_NUMBERS = 8
        HAS_WKT_CRS = 16

    class ClassFlag:

        """
        Constant enum class containing base10 values for classification bit field flags.
        """

        SYNTHETIC = 1
        KEYPOINT = 2
        WITHHELD = 4
        OVERLAP = 8


class RegexLidar:

    """
    Constant enum class containing useful regex patterns
    """

    FILENAME_LIDAR_PRODUCTION = r'bc_\d{3}[a-z]\\d{3}_(\\d_){3}x(yes|no)' \
                                r'_(\d{1,2}|\dp\d[1-9])_(bcalb|utm09|utm' \
                                r'9|utm10|utm11)_2\d{3}\.la(s|z)'

    FILENAME_LIDAR_RAW = r'[0-9]{1,5}_[0-9]{3}_[0-9]{4}_([a-z0-9]?)+([A-' \
                         r'Z0-9\-?]).*\.la(s|z)'

    GUID = R'\s+([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})'

    CONTRACT_NUMBER = R"OP\d\dBMRS\d\d\d"

    SYSTEM_ID_PRODUCTION = "^[\\w.]( .)?[\\w.]"

    SYSTEM_ID_ACQUISITION = "^[\\w+;]( .)?[\\w+]"
