DASHLINE = f"\n{'-' * 80}\n"

HELP_TEXT = (
    "Usage:\n\n"
    "1. Select directory of image files as input (jpg, jpeg, tif, sid)\n"
    "   (or xlsx if using Metadata test only).\n\n"
    "2. Select which test(s) to perform on the input.\n\n"
    "3. Select an output directory. If left blank an output folder\n"
    "   (oriqcs_results) will be created in the input directory.\n\n"
    "4. Click \"Add To Queue\", which saves the information from\n"
    "   steps 1-3 and prompts for additional information if certain\n"
    "   tests are selected. A queue item is created that can be\n"
    "   viewed in the \"Queue\" frame.\n\n"
    "5. Repeat steps 1-4 until all needed tests are added to the\n"
    "   queue.\n\n"
    "6. Click \"Process Queue\" and wait for all queue items to\n"
    "   process."
)

ABOUT_TEXT = (
    "Ortho Raster Imagery Quality Control Suite (ORIQCS) © GeoBC"
    "\n\nPronunciation: 'orks', 'oh-rix'"
    "\n\nORIQCS will run on any folders containing ortho, raster, or "
    "raw image files, with the exception of the metadata test which "
    "requires xlsx files.\n\n"
    "Tests:\n\n"
    "1. Image Summary: creates a csv spreadsheet with metadata\n"
    "   from each file.\n"
    "Output: Output path\\image_summary.csv\n\n"
    "2. Image Corruption: Checks each image file for corruption.\n"
    "Output: Output path\\corrupt_files.txt\n\n"
    "3. File Naming: Checks naming of ortho, raster, and raw image\n"
    "   files based on GeoBC naming conventions.\n"
    "Output: Output path\\filename_check.txt\n\n"
    "4. Histogram RGB: Creates a pdf of histograms and a\n"
    "   spreadsheet detailing red, green, and blue values for\n"
    "   each file.\n"
    "Output: Output path\\Histogram_RGB\\ \n\n"
    "5. Tile Index: Computes the bounding box of the images\n"
    "   in the input directory and writes it to a shapefile.\n"
    "   Requires an EPSG code.\n"
    "Output: Output path\\Coverage_Index\\ \n\n"
    "6. Metadata: Takes in metadata xlsx file(s) containing\n"
    "   requisition data and checks if it meets GeoBC\n"
    "   specifications. Requires a minimum\n"
    "   solar angle.\n"
    "Output(1): Output path\\Metadata\\Formatted_Metadata\\Metadata_Error_Overview.csv\n"
    "Output(2): Output path\\Metadata\\Metadata_Error_Overview.csv\n\n"
    "7. Valid Image Area: Outputs a shapefile that delineates\n"
    "   the actual image area of an ortho image. It assumes\n"
    "   the nodata area of the ortho image is black (0,0,0).\n"
    "   It currently works with only geotiff images.\n"
    "Output: Output path\\Valid_Image_Area\\ \n\n"
    "8. Ortho QC Prep: Grabs a user specified percentage and\n"
    "   copies ortho files in the input directory to the output\n"
    "   directory. The copied ortho files are compressed, internally\n"
    "   tiled, and overviews are created. (Optional) If a lidar\n"
    "   directory is specified ORIQCS matches the lidar tiles that\n"
    "   overlap with the sample orthos and creates a lidar intensity\n"
    "   raster from the overlapping data.\n"
    "Output: Output path\\Ortho_QC_Prep\\\n\n"
    "9. Create COG: Takes in a directory of ortho files and creates\n"
    "   Cloud Optimized Geotiffs (COG) for each file in the input\n"
    "   directory.\n"
    "Output: Output path\\COG\\\n\n"
    "10. Validate COG: Checks if each Cloud Optimized Geotiff\n"
    "   in the input directory is valid. If the Create_COG test is\n"
    "   selected \'output path\\COG\\\' is used as input directory.\n"
    "Output: Output path\Validate_COG.txt\n\n"
    "11. Check Thumbnails: *Input directory must contain (subdirectories included) both original TIF and thumbnail images*\n"
    "   Checks if each thumbnail is 1/16th the size of\n"
    "   its parent TIF image. Checks if each TIF has a\n"
    "   child thumbnail. Checks rows in all thumbnails that are all\n"
    "   one colour (clearly an error)\n"
    "Output: Output path\\thumbnail_report.txt\n\n"
)

# Base64 encoding of the icon for the Province of BC
BC_LOGO_B64 = (
"""
AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAD/////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
/////////////////////////fz8/+ri3f/x7Or/8Ozp//Tw7v/x7er/8+/s//Pu7P/6+Pf/
593Y//Xy7//v6uf/8ezp/+7n4//18vD/9fLw//Xy8P/18e///f38/+jf2v/6+Pj/6eDb//Hs
6f/y7ev/8u7r//Dq5//y7er/+ff2//f08v/r49///v7+//7+/f/Tw7v/zLmv/+Tc1//g1c//
ybes/9HBuP/p4t7/zbuw/+jh3f+ohnT/7eXh/9rNxP/DraH/39TM/+LY0//Yy8P/6OHd/8ay
pv/p4d3/qYd1//Xy8P+vkID/39XO/829sv/CrJ//zbmv/9zRyf/j2tT/yLOn/8m3rP/+/f3/
/Pv7/596Zv/////////////////DraH/3c/I///////NvLD/3dLL/7KVhf//////9/Px/76m
mP//////7efj/+DVzv/l3Nf/wqyf/9fKwv+vjn3//////7ecjP/g19D/wqyf/8+8s//Wxr7/
/f39/+HX0P+oiHb/8e3q///////8+/v/o35q/////////////////9TFvP/YysL/+fj2/7id
j//k3df/pYNy///////w6+n/tJmK///////h19D/39XO/7WZiv/f0sz/8+/t/5dvWf/5+Pj/
rIx6/9fJwf+xlYX/28/I/8ezqP//////1se+/8Ovov/6+fj///////7+/v/c0Mn/zLuw/9/V
zv/Uxb3/5dzX//Pv7f/p4t7/6eHc//j39f/f0sv///////b08//l3Nb//f38//Dr6P/v6ub/
5NnT//v5+P//////3tLL//n39v/bzsf/6eLd/+zm4f/w6+f/6uPe///////w6+j/9PHv//7+
/v////////////39/f/08e//+ff2/+vj3//azMP/28/I//Xx8P/w7Or/4dXN//n5+P/k2tX/
6+bh/+LX0f/29fL/7OTg/+bf2f/7+/r/5t3Z/+rk4P/n4Nr/39bO//Lv7f/r5uH/5t3Y//f2
9f/l3db/7+nn////////////////////////////////////////////7OXg/8aypv/s5uP/
uZ6Q/+/r5/+3nI3/6ODc/7+mmf/39PL/vKSW///////azMT/2szE///////CrJ//7Ofk/9vO
x///////uJ2N//bz8f/DraD//////9bGvv/cz8j/////////////////////////////////
///////////s5eD/y7qv/+ji3v+nhnX/7+rl/62Me/+qinn/9PTw//Xx7/+9pJX//////9vN
xf/bzcX//////8KqnP/r5+T/+fj2/7OYh//Cq5//9PDu/6uKef/e0cj/waib/97Ryv//////
/////////////////////////////////////+3m4v/CrJ7/tZuL/825rv/59/X/tJiJ//z6
+v+ujn3/+ff1/7uhk///////2szE/9vNxf//////wKea/+/r6f+3no7/5+Db//j39v/y7ev/
xK2g///////Vxr3/3M/H////////////////////////////////////////////6uPe/8y7
sP/Xy8L/xK6i/+Pb1f/Nuq//287G/+be2f/u7On/yLWp/9/Vz//Qwbj/2MrC/9zQyf/Muq//
5t7a/+vl4f/i2NL/1sjA/+vm4v/Tw7r/+/z7/9jLw//l3Nj/////////////////////////
///////////////////08e//4tfR/+Pa1P/8+/v/////////////////////////////////
///////////39PP/7+nm/+ri3v/k2dP/49jS/+Tb1f/r49//7+nm//r5+P//////////////
////////////////////////////////////////////////////////////////////////
///////////6+fj/7+nl/+LX0f/UxLv/v6ea/6aDcP+PYkv/fEku/3E5G/9vNxj/dD4g/4JQ
Nv+TalL/ro99/868sf/t5uL/////////////////////////////////////////////////
5NrU/8axpP/Twrr/2MjA/9fGvv/OvLH/wquc/7GTgv+dd2L/iFlA/3U+IP9uNBX/cTkZ/3M8
Hf91PiD/dj8h/3ZAIf91PyH/dD0f/3I7HP9wNxj/dD0e/5ZtVv/d0Mn/////////////////
//////////////////////39/f+4nY3/bzYX/39NMv+DUzj/g1E2/3pGKf9wOBn/cDcY/3I6
G/90PR7/dj8h/3ZAIv92QCL/dkAi/3ZAIv92QCL/dkAi/3ZAIv92QCL/dkAi/3ZAIv92PyH/
bDER/7KVhf/7+vn/////////////////////////////////+vj3/7OWhv9vNhb/dD4g/3Q+
H/90Ph//dT8g/3ZAIv91PyD/cDcX/3I7HP92QCL/dkAi/3ZAIv92QCL/dj8h/3E5Gv91PiD/
dkAi/3ZAIv92QCL/dkAi/3ZAIv9wOBj/ro99//f18///////////////////////////////
///7+vn/tpqK/283F/92QCL/dkAi/3ZAIv92QCL/dD0f/3lEJ/+6opT/mHBb/241Ff91PiD/
dT8h/3A4GP9yOhz/pIFu/3pGKv9yOxz/dkAi/3ZAIv92QCL/dkAi/3A3GP+wk4H/+ff1////
///////////////////////////////////CqJr/cDMS/3ZAIv92QCL/dT4f/3Q9Hv+GVzz/
4NfQ//z7+v/z7+z/w66h/3tILP93QiX/s5WF/+LX0P/39PL/6OHb/512YP9wNRf/czgZ/3Y8
HP92QCL/bzQU/7yikv/+//7//////////////////////////////////////8HW3/9iZmf/
dD4i/3c/IP+HZFD/il1E/9zh5f////7////////////+/v7/5NrU/+LY0f/9/Pv/////////
////////4u7z/8O9uv+gtL3/coeQ/3Q9H/9uSDT/x8TC////////////////////////////
////////////////1+/6/1q97P9bka7/lrDB/6nV7/+b0O//zun2/+j0+v//////////////
//////////////////////////////D5/P/U6vj/kc7v/5HO8P+bzuz/cqbE/2enxP/R7/z/
///////////////////////////////////////////9/v7/ltLw/1W26P9Vt+j/Vrjo/5jT
7/+k1PD/5/X8/+j0+v/+///////////////////////////////u9/z/6fX7/6zY8f+X0u//
YL3p/z6v5P9Jseb/kNHy//n8/v//////////////////////////////////////////////
///N6vf/R7Tm/zet5P9Vuef/Zb3q/7/h9P+v2vL/zej2/9zu+f/u9/v/+Pz9//f7/v/s9vv/
6fX7/9Hp9v+n1fH/vuH0/3vE7P9Rtuj/QLDm/0Oy5v/F5/f/////////////////////////
//////////////////////////////////+Z1fD/M6vk/0Ov5f+Sy+z/esbr/4nL7f+g0+//
0en4/7Tc8//V6/j/zef3/7je9P/U6/f/otTx/5bS7/9nvun/kcvt/1e25/8xqeT/k9Pw////
//////////////////////////////////////////////////////////////b7/f+EzO7/
Wbbn/1q25v9Fseb/acDp/4jK7f+s2fL/i8zu/6nX8f+q1/H/mdHw/5jR7/+g1PD/Y73o/061
5/9FsOX/WLXm/4XM7f/x+fz/////////////////////////////////////////////////
//////////////////////P6/f+W0/D/Marj/zuv5f8+ruT/i8jr/2zA6v9kvur/esTr/4vL
7P9vwuv/Vrfn/4/K7P9Qs+b/PK7l/y2p5P+Lz+//7/n8////////////////////////////
//////////////////////////////////////////////////////f8/f+x3/P/W7zq/zir
4/9dt+b/Oa3l/0Kx5/9euOj/cL7o/0215/8yq+T/ULLm/0ev5f9Vuuj/rN3y//T7/f//////
////////////////////////////////////////////////////////////////////////
///////////////////f8vv/uOL0/3/J7P9Cseb/J6bi/zWp5P8/rOP/LKjj/0Gx5v91xuv/
tuD0/93x+v//////////////////////////////////////////////////////////////
///////////////////////////////////////////////////+////7vj9/+Lz+//Y7/r/
0uz6/9Ps+v/Y7/r/4PP7/+34/P/9/v//////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAA=
"""
)
