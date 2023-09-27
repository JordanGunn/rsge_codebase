import os
import sys

# set environment parameters for installing GDAL data base using pyinstaller
# Look for 
# C:\Users\hsteiner\AppData\Local\Programs\Python\Python39\Lib\site-packages\osgeo\data\proj\proj.db

os.environ['PROJ_LIB'] = sys._MEIPASS
# os.environ['GDAL_DATA'] ='C:\\Users\\hsteiner\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\osgeo\\data\\gdal'
