# Witten by: Harald Steiner, Harald.steiner@gov.bc.ca
# Copyright: Provincial Government of BC , November 2022
# Data input is aa lidar LAS file
# Data output is the UTM ZONE and ZONE_ID out of las data  
# Note: If nop UTM projection is present, the ZONE & ID is set to -1 -1
# usage at your own risk

import struct

def check_UTM (filename,verb):

    #search for UTM projection entry in the VLRS decsription 
    Vert_datum_flag=""
    list_ =str(list(parse_header(filename,verb).items())[-1])

    
    rep_WKT = list_.find('UTM ') # search for UTM string in VLRS #1
    rep_PCS = list_.find('UTM zone') # search for UTM string in VLRS #4
    rep_PCS2 = list_.find('UTM_zone_') # search for UTM string in VLRS #4
    
    Vert_datum_flag_CGVD=list_.find('CGVD') # search for UTM string in VLRS #4

    return list_

def parse_header(filename,ver):

    """Parse a las/laz file's header into a workable struct format."""

    headerstruct = (
        ('filesig', 4,'c',4) ,
        ('filesourceid' , 2,'H',1) ,
        ('global enc'     , 2,'H',1) ,
        ('guid1'        , 4,'L',1) ,
        ('guid2'        , 2,'H',1) ,
        ('guid3'        , 2,'H',1) ,
        ('guid4'        , 8,'B',8) ,
        ('vermajor'     , 1,'B',1) ,
        ('verminor'     , 1,'B',1) ,
        ('sysid'        , 32,'c',32) ,
        ('gensoftware'  , 32,'c',32) ,
        ('fileday'      , 2,'H',1) ,
        ('fileyear'     , 2,'H',1) ,
        ('headersize'   , 2,'H',1) ,
        ('offset'       , 4,'L',1) ,
        ('numvlrecords' , 4,'L',1) ,
        ('pointformat'  , 1,'B',1) ,
        ('pointreclen'  , 2,'H',1) ,
        ('numptrecords' , 4,'L',1) ,
        ('numptbyreturn', 20,'L',5) ,
        ('xscale'       , 8,'d',1) ,
        ('yscale'       , 8,'d',1) ,
        ('zscale'       , 8,'d',1) ,
        ('xoffset'      , 8,'d',1) ,
        ('yoffset'      , 8,'d',1) ,
        ('zoffset'      , 8,'d',1) ,
        ('xmax'         , 8,'d',1) ,
        ('xmin'         , 8,'d',1) ,
        ('ymax'         , 8,'d',1) ,
        ('ymin'         , 8,'d',1) ,
        ('zmax'         , 8,'d',1) ,
        ('zmin'         , 8,'d',1) ,
        ('waveform'     , 8,'Q',1) ,
        ('firstEVLR'    , 8,'Q',1) ,
        ('numEVLR'      , 4,'L',1) ,
        ('exnumbptrec'  , 8,'Q',1) ,
        ('exnumbyreturn',120,'Q',15),
        ('reserved',      2,'H',1),
        ('User id [ID]',      16,'c',16) ,
        ('Record id',     2,'H',1) ,
        ('Record Length After Header',  2,'H',1) ,
        ('Description',32,'c',32),  # parsing through all possible VLRs
        ('Version',      2,'H',1),
        ('Major Rev',      2,'H',1),
        ('Minor Rev',      2,'H',1),
        ('Number of Keys [count]',2,'H',1),
        ('GTModelTypeGeoKey',      2,'H',1),
        ('e2',      2,'H',1),
        ('e2',      2,'H',1),
        ('e4',      2,'H',1),
        ('GTCitationGeoKey:',      2,'H',1),
        ('GTCitationGeoKey ID:',      2,'H',1),
        ('GTCitationGeoKey Count:',      2,'H',1),
        ('e8',      2,'H',1),
        ('e9',      2,'H',1),
        ('e10',      2,'H',1),
        ('e11',      2,'H',1),
        ('e12',      2,'H',1),
        ('e13',      2,'H',1),
        ('e14',      2,'H',1),
        ('e15',      2,'H',1),
        ('e16',      2,'H',1),
        ('e17',      2,'H',1),
        ('e18',      2,'H',1),
        ('e19',      2,'H',1),
        ('e20',      2,'H',1),
        ('e21',      2,'H',1),
        ('e22',      2,'H',1)
        )
        #OGC standards section 7: coordinate systems in WKT format
        #https://repository.oceanbestpractices.org/bitstream/handle/11329/1141/01-009_OpenGIS_Implementation_
        #
        #GeoTiff:Specification_Coordinate_Transformation_Services_Revision_1.00.pdf?sequence=1&isAllowed=y
        #GeoKeyDirectoryTag version 1.1.0 
        #https://docs.opengeospatial.org/is/19-008r4/19-008r4.html

    header = {'infile':filename}

    if ver==1:
     verbose=True
    else:
     verbose=False

    with open(filename, 'rb') as fh:
        for i in headerstruct:
            print ("                                                                     i=",i[1])
            if i[2] == 'c':
                value = fh.read(i[1]) #start reading when c encountered
                print("\n ============= First Value c ====================================================================", i[0] )

            elif i[3] > 1:
                value = struct.unpack( '=' + str(i[3]) + i[2] , fh.read(i[1]) )
                print("\n ========== Second Value", i[3] )
            else:
                value = struct.unpack( '=' + i[2] , fh.read(i[1]) )[0]
                print("\n ========== Third Value", value )
            if verbose:
                print(i[0] + '\t', value)

            header[i[0]] = value

    # if laz file, subtract 128 from the point data format
    # (laz compression adds 128 to the point format)
    if header['infile'].endswith('.laz'):
        header['pointformat'] = header['pointformat']-128
    return header


list_=check_UTM("utm09_las-clip.las",1)

print (list_)


