

####
# misc_func.py

#Author: Prateek
#Note: This code is directly taken from Lydia's version
#Taken from: 
# Lydia Rill
# 
# Python 3.6
#
# This script contains a python function used in creating xdbfile
#
####

import os
import sys
from datetime import datetime, timedelta
import math
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from io import StringIO


# Check if a file or directory exists.
# If it does not exist, exit the script!
# You must set fileflag=True for a file.
# Read in the weather file (wdb.xml file).
def read_wx(wdb_file,wx_id):
    # Get the StationID (XML attribute) from the filename.
    #wx_id = os.path.basename(wdb_file).replace(".wdb.xml", "")
    print("Wxid ", wx_id)
    # Read in the file using XML library.
    tree = ET.parse(wdb_file)
    root = tree.getroot()
    # Find the "Weather" tag for the specific StationID.
    wx = root.find("Stations[@StationID='" + wx_id + "']/Weather")
    # Get the text from the "Weather" element.
    wx_text = wx.text
    # Convert the text to a pandas dataframe by reading it as a CSV.
    # You must define the column names ["Year,DOY,SRAD,Tmax,Tmin,Rain,DewP,Wind,PAR"]
    #wx_df = pd.read_csv(StringIO(wx_text), names=["Year","DOY","SRAD","Tmax","Tmin","Rain","DewP","Wind","PAR"])
    wx_df = pd.read_csv(StringIO(wx_text), names=["Year","DOY","SRAD","Tmax","Tmin","Rain","WindSp","SH", "Rmax", "Rmin"])
    # Check the dataframe.
    print("Checking dataframe")
    print(wx_df)
    return(wx_df)
def check_exists_error(tmp_location, **kwargs):
    fileflag = False
    if 'fileflag' in kwargs:
        fileflag = kwargs['fileflag']
    if fileflag:
        if not os.path.isfile(tmp_location):  # Check if the file exists.
            st.write("## ERROR: cannot find the file", tmp_location)
            #sys.exit()
    else:
        if not os.path.isdir(tmp_location):  # Check if the directory exists.
            st.write("ERROR: cannot find the directory", tmp_location)
            #sys.exit()

# Calculate the average Bulk Density for 2 layers (top and bottom with defined threshold).
def average_bd(soil_id, root, thresh_depth):
    soil_layer = root.find('Soils/Soil[@SoilID="' + soil_id + '"]')
    if soil_layer is None:
        print("Error: soil layer does not exist in root", soil_id)
        return(np.nan, np.nan, np.nan, np.nan)
    else:
        # Loop through each layer in the soil.
        bd_dict = {}
        top_bd_list = []
        bottom_bd_list = []
        for lyr in soil_layer.findall('Layer'):
            depth = float(lyr.attrib['ZLYR'])  # Depth in cm.
            bd = float(lyr.attrib['BD'])  # Bulk density.
            bd_dict[depth] = bd
            if depth <= thresh_depth:
                top_bd_list.append(bd)  # Add the bulk density value to the top layer list.
            else:
                bottom_bd_list.append(bd)  # Add the bulk density value to the bottom layer list.

        # Determine the min and max depth of the soil.
        min_depth = min(bd_dict.keys())
        max_depth = max(bd_dict.keys())

        # Calculate the average bulk density using layers above the provided threshold.
        if top_bd_list:
            avg_bd_top = sum(top_bd_list) / len(top_bd_list)
        else:
            # If no layer began before 30 cm, use the BD of the first layer.
            avg_bd_top = bd_dict[min_depth]
        # Calculate the average bulk density using layers below the provided threshold.
        if bottom_bd_list:
            avg_bd_bottom = sum(bottom_bd_list) / len(bottom_bd_list)
        else:
            # No layers deeper than 30cm.
            avg_bd_bottom = None

        # Check to make sure the means values are ok.
        if avg_bd_top < 1 or avg_bd_top > 2:
            print("WARNING: unreasonable bulk density for top layer", soil_id)
        if avg_bd_bottom is not None:
            if avg_bd_bottom < 1 or avg_bd_bottom > 2:
                print("WARNING: unreasonable bulk density for bottom layer", soil_id)

        # Calculate the top depth and bottom depth for the initial conditions, converting the threshold from cm to m.
        top_depth = thresh_depth / 100.
        bottom_depth = (max_depth - thresh_depth) / 100.
        return (avg_bd_top, avg_bd_bottom, top_depth, bottom_depth, max_depth)
