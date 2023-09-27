
class RegexRaster:

    """
    'enum' Class containing useful regex pattern constants.
    """

    FILENAME_ORTHO = '^bc_\\d{3}[a-z]\\d{3}(_\\d_\\d_\\d_|_)xc\\d{3}mm_(bcalb|utm08|utm8|utm09|utm9|utm10|utm11)_2\\' \
                     'd{3}(.tif|.tiff|.jpg|.jpeg|.sid)$'

    FILENAME_DSM = '^bc_\\d{3}[a-z]\\d{3}(_\\d_\\d_\\d_|_)x(li|r|rgb)([1-9]m|\\d[1-9]m)_(bcalb|utm08|utm8|utm09|utm9' \
                   '|utm10|utm11)_2\\d{3}_dsm.(tif|tiff|asc)$'

    FILENAME_DEM = '^bc_\\d{3}[a-z]\\d{3}(_\\d_\\d_\\d_|_)x(li|r|rgb)([1-9]m|\\d[1-9]m)_(bcalb|utm08|utm8|utm09|utm9' \
                   '|utm10|utm11)_2\\d{3}.(tif|tiff|asc)$'

    FILENAME_RAW_IMAGERY = '^(\\d[1-9]|[1-9]\\d)bcd([1-9]\\d|\\d[1-9])([1-9]\\d{2}|\\d[1-9]\\d|\\d{2}[1-9])_([1-9]\\' \
                           'd{2}|\\d[1-9]\\d|\\d{2}[1-9])_([1-9]\\d|\\d[1-9])_([1-9]\\d|[1-9])bit_(rgb|rgbir).(tif|' \
                           'tiff|sid|jpg|jpeg)$'


class ImageFormats:

    """
    Class of valid image format constants.

    :param ESRI_ASCII: "asc"
    :param ASCII: "asc"
    :param ASC: "asc"
    :param GEOTIFF: "tiff"
    :param GEOTIF: "tif"
    :param TIFF: "tiff"
    :param TIF: "tif"
    :param SID: "sid"
    :param JPG: "jpg"
    :param JPEG: "jpeg"
    """

    SID = "sid"
    JPG = "jpg"
    JPEG = "jpeg"
    TIF = GEOTIF = "tif"
    TIFF = GEOTIFF = "tiff"
    ASC = ASCII = ESRI_ASCII = "asc"
