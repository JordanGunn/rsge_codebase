# Witten by: Harald Steiner, Harald.steiner@gov.bc.ca
# Copyright: Provincial Government of BC , July 2022
# Argument: Data input is lidar LAS file
# Data output is the UTM ZONE and ZONE_ID out of las data
# Note: If nop UTM projection is present, the ZONE & ID is set to -1 -1
# usage at your own risk

import struct
from numpy import str_


def check_UTM(filename, verb):

    # set default variables for UTM projection in the VLRS decsription
    Vert_datum_flag = ""
    VERT_CS = ""
    COMP_SY = ""

    #rep_ZONE= ""
    ZONE=-1
    ZONE_ID = -1

    # convert text to lowercase and search for UTM lowercase characters to avoid ambiguities
    list_ = (str(list(parse_header(filename, verb).items())[-1])).lower()
    rep_UTM = list_.find('utm')  # search for UTM string in VLRS #1

    # Vert_datum_flag_CGVD=list_.find('CGVD') # search for UTM string in VLRS #4
    VERT_CS = list_.find('vert_cs[')  # search for UTM string in VLRS #4
    COMP_SY = list_.find('compd_cs')  # search for WKT version 1.0 compound CS entry 

    if VERT_CS>0 or COMP_SY>0:
        Vert_datum_flag="ORTHOMETRIC"

    # search fotr ZONE and Zone ID if TM is found 
    if rep_UTM > 0:
        str_UTM = list_[rep_UTM:rep_UTM +30]
        rep_ZONE = str_UTM.replace('zone',"")
        rep_ZONE = rep_ZONE.replace('_',"")
        rep_ZONE = rep_ZONE.replace(' ',"")
        pos_ZONE_ID = rep_ZONE.find('n')
        
        if pos_ZONE_ID < 1:
            pos_ZONE_ID = rep_ZONE.find('s')
            ZONE_ID="S"
            ZONE= rep_ZONE[3:pos_ZONE_ID]
        else:
            ZONE_ID="N"
            ZONE= rep_ZONE[3:pos_ZONE_ID]             

    else:
        # If no UTM< projection is present, -1 -1 will be used
        ZONE_ID = -1
        ZONE = -1
    
    return ZONE, ZONE_ID, VERT_CS


def parse_header(filename, ver):
    """Parse a las/laz file's header into a workable struct format."""

    headerstruct = (
        ('filesig', 4, 'c', 4),
        ('filesourceid', 2, 'H', 1),
        ('global enc', 2, 'H', 1),
        ('guid1', 4, 'L', 1),
        ('guid2', 2, 'H', 1),
        ('guid3', 2, 'H', 1),
        ('guid4', 8, 'B', 8),
        ('vermajor', 1, 'B', 1),
        ('verminor', 1, 'B', 1),
        ('sysid', 32, 'c', 32),
        ('gensoftware', 32, 'c', 32),
        ('fileday', 2, 'H', 1),
        ('fileyear', 2, 'H', 1),
        ('headersize', 2, 'H', 1),
        ('offset', 4, 'L', 1),
        ('numvlrecords', 4, 'L', 1),
        ('pointformat', 1, 'B', 1),
        ('pointreclen', 2, 'H', 1),
        ('numptrecords', 4, 'L', 1),
        ('numptbyreturn', 20, 'L', 5),
        ('xscale', 8, 'd', 1),
        ('yscale', 8, 'd', 1),
        ('zscale', 8, 'd', 1),
        ('xoffset', 8, 'd', 1),
        ('yoffset', 8, 'd', 1),
        ('zoffset', 8, 'd', 1),
        ('xmax', 8, 'd', 1),
        ('xmin', 8, 'd', 1),
        ('ymax', 8, 'd', 1),
        ('ymin', 8, 'd', 1),
        ('zmax', 8, 'd', 1),
        ('zmin', 8, 'd', 1),
        ('waveform', 8, 'Q', 1),
        ('firstEVLR', 8, 'Q', 1),
        ('numEVLR', 4, 'L', 1),
        ('exnumbptrec', 8, 'Q', 1),
        ('exnumbyreturn', 120, 'Q', 15),
        ('reserved',      2, 'H', 1),
        ('User id',      16, 'c', 16),
        ('Record id',     2, 'H', 1),
        ('Record Length After Header',  2, 'H', 1),
        ('Description', 2048, 'c', 54)  # parsing through all possible VLRs
    )

    header = {'infile': filename}

    if ver == 1:
        verbose = True
    else:
        verbose = False

    with open(filename, 'rb') as fh:
        for i in headerstruct:
            if i[2] == 'c':
                value = fh.read(i[1])
            elif i[3] > 1:
                value = struct.unpack('=' + str(i[3]) + i[2], fh.read(i[1]))
            else:
                value = struct.unpack('=' + i[2], fh.read(i[1]))[0]
            if verbose:
                print(i[0] + '\t', value)

            header[i[0]] = value

    # if laz file, subtract 128 from the point data format
    # (laz compression adds 128 to the point format)
    if header['infile'].endswith('.laz'):
        header['pointformat'] = header['pointformat']-128
    return header


