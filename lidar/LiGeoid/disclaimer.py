# Disclaimer of program usage 

def get_disclaimer(geoid_model):
    title = "LiGeoid: Ellipsoidal to orthometric Height transformation \
    for lidar point cloud files Version: 1.0 "
    message= "INPUT REQUIREMENTS:\n========================\nlidar Las file V1.4\nHOR-DATUM: NAD83CSRS\nV-DATUM: ELLIPSOIDAL \
    HEIGHTS\nGEOID MODEL: "+str(geoid_model)+" (NrCan)\n\nThis Program transforms ellipsoidal heights (n) into orthometric heights (H) according to:\n\n\
        H=h-N\n\nwhere (N) represents the height above the geoid.\
    The Provincial Government of BC, Canada, assumes no responsibillities for the\
    correctness or maintenance of the program. Use at your own risk. For questions, please\
    contact Lidar@gov.bc.ca .July 2022"    
    return message,title