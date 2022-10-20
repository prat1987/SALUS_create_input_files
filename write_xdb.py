#! /usr/bin/env python

####
# write_xdb.py
# Lydia Rill
# Updated 03/11/2020
#
# Python 3.6
#
# This script contains a python function that writes the xdb.xml file.
#
####
import streamlit as st 
import os
import sys
from datetime import datetime, timedelta
import math
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

# Check if a file or directory exists.
# If it does not exist, exit the script!
# You must set fileflag=True for a file.
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


def write_xdb(
        xdb_file,
        sdb_file,
        wdb_file,
        cdb_file,
        irrigation_flag,
        wx_id,
        cultivar,
        soilID_list,
        N_rate_list,
        **kwargs):

    if not xdb_file.endswith('xml'):
        print('WARNING: Output XML file should end with .xml', out_xdb)

    # Define years you want to simulate.
    SALUS_start = 1980
    SALUS_end = 2099
    nyrs = SALUS_end - SALUS_start + 1
    start_doy = 1

    # Read in the soil file data.
    print("Reading in soil data")
    tree = ET.parse(sdb_file)
    root = tree.getroot()

    # Keep track of the experiment numbers.
    expID = 0
    # Open the xdb file for writing.
    with open(xdb_file, 'w') as out:
        out.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        out.write("<XDB>\n")

        # Loop through the SoilIDs.
        for soil_id in soilID_list:
            print("-Writing soil", soil_id)
            # Convert soilID to a string
            soil_id = str(soil_id)

            # Get soil parameters for initial conditions.
            # Calculate the average Bulk Density for layers 0-30cm and 30cm-bottom.
            avg_bd_top, avg_bd_bottom, depth_top, depth_bottom, max_depth = average_bd(soil_id, root, 30)

            # Loop through the N rates.
            for N_rate in N_rate_list:
                print("---Writing N rate", N_rate)

                expID += 1

                # Experiment title to distinguish the differences in each experiment.
                title = (
                        str(N_rate)
                        + "|" + str(soil_id)
                )
                out.write("  <Experiment ExpID=\"" + str(expID) + "\" Title=\"" + title
                          + "\" NYrs=\"" + str(nyrs) + "\" SYear=\"" + str(SALUS_start)
                          + "\" SDOY=\"" + str(start_doy) + "\" ISwWat=\"Y\" ISwNit=\"Y\" ISwPho=\"N\" Frop=\"1\" Soilfp=\"" + sdb_file
                          + "\" SoilID=\"" + str(soil_id)
                          + "\" Weatherfp=\"" + wdb_file + "\" StationID=\"" + wx_id
                          + "\" Cropfp=\"" + cdb_file
                          + "\" NRrepSq=\"0\" MeEvp=\"R\" MeInf=\"R\" kResOrg=\"3.914E-5\" kSloOrg=\"0.00013699\" >\n")

                # Calculate Initial N Values for this SoilID
                # Note that it doesn't matter what year or doy you set in the Mgt_InitialCond, it sets the values on the SYear and SDOY of the experiment.
                # Need to convert 30 kg N/ha to ppm for each soil, using bulk density.
                # N (ppm) = N(kg/ha) / (thickenss of layer(m) * bulk density(Mg/m3) * 10000(m2/ha)) * 1000(g/kg)
                n_kg = 30
                n1_kg = n_kg * 0.4  # Top 30 cm get 40% of the N (value from Bruno a while ago)
                n2_kg = n_kg * 0.6
                n1_ppm = '%.2f' % (n1_kg / (depth_top * avg_bd_top * 10000) * 1000)
                out.write("    <Mgt_InitialCond Year=\"" + str(SALUS_start) + "\" DOY=\"" + str(start_doy) + "\" >\n")
                out.write("      <Layer DLayrI=\"30\" INinorg=\"" + str(n1_ppm) + "\" />\n")
                # Always write out an additional layer below 30cm, even for LS otherwise the initalized N will not work.
                if pd.isnull(avg_bd_bottom):
                    max_depth = 200
                    n2_ppm = 0
                else:
                    n2_ppm = '%.2f' % (n2_kg / (depth_bottom * avg_bd_bottom * 10000) * 1000)
                out.write("      <Layer DLayrI=\"" + str(max_depth) + "\" INinorg=\"" + str(n2_ppm) + "\" />\n")
                out.write("    </Mgt_InitialCond>\n")

                # Component Parameters.
                out.write("    <Rotation_Components>\n")
                crop_name = "Maize"
                crop_mode = "C"
                speciesID = "MZ"

                # Keep track of the component numbers.
                comp = 1

                # Component Flags
                # IHarI = R for reported date, M for harvest at maturity.
                # Irrigation flag
                if irrigation_flag:
                    irrFlag = 'A'  # Auto
                else:
                    irrFlag = 'N'
                out.write("      <Component OrderNum=\"" + str(comp) + "\" Title=\"" + crop_name
                          + "\" IPltI=\"R\" IIrrI=\"" + irrFlag + "\" IferI=\"R\" IResI=\"R\" ITilI=\"R\" IHarI=\"R\" IEnvI=\"N\">\n")

                # IRRIGATION
                if irrigation_flag:
                    irr_method = 'IR004'  # Sprinkler
                    dsoil = 30  # Management depth of soil to look at for irrig (cm)
                    thetaC = 70  # Threshold for automatic application (% of max avail. water)
                    endPt = 90  # End point for automatic application (% of max avail. water)
                    out.write("        <Mgt_Irrigation_Auto DSoil=\"" + str(dsoil) + "\" IAMe=\"" + irr_method
                              + "\" ThetaC=\"" + str(thetaC) + "\" IEPt=\"" + str(endPt) + "\" />\n")

                # PLANTING
                
                year = SALUS_start
                plant_depth = 5   # cm
                ppop = "8"  # seeds/m2.
                rowspc = "76"  # cm
                pdoy = "121"  # DOY 121 = May 1

                out.write(
                    "        <Mgt_Planting CropMod=\"" + crop_mode + "\" SpeciesID=\"" + speciesID + "\" CultivarID=\"" + cultivar
                    + "\" Year=\"" + str(year) + "\" DOY=\"" + str(pdoy)
                    + "\" Ppop=\"" + str(ppop) + "\" Ppoe=\"" + str(ppop)
                    + "\" PlMe=\"S\" PlDs=\"R\" RowSpc=\"" + str(rowspc)
                    + "\" SDepth=\"" + str(plant_depth) + "\" />\n")

                # FERTILIZE
                # Fertilize at Planting
                # Use 1/3 of the total N at planting.
                fert_amt_kg = "{0:.2f}".format((float(N_rate) * 1./3.))
                fert_type = "FE001"
                fert_code = "AP001"
                fert_depth = "0"  # On the surface application (cm)
                out.write("        <Mgt_Fertilizer_App Year=\"" + str(year) + "\" DOY=\"" + str(pdoy)
                          + "\" IFType=\"" + fert_type + "\" FerCode=\"" + fert_code
                          + "\" FInP=\"100\" DFert=\"" + fert_depth + "\" ACrbFer=\"0\" ANFer=\"" + fert_amt_kg
                          + "\" APFer=\"0\" AKFer=\"0\" ACFer=\"0\" AOFer=\"0\" FerDecRt=\"0\" VolN=\"0\" VolNRate=\"0\" />\n")

                # Fertilize at side-dress
                # Use 2/3 of the total N at side-dress, 45 days after planting.
                fert_amt_kg = "{0:.2f}".format((float(N_rate) * 2./3.))
                sidedress_doy = str(int(pdoy) + 45)
                fert_type = "FE010"
                fert_code = "AP001"
                fert_depth = "0"  # On the surface application (cm)
                out.write("        <Mgt_Fertilizer_App Year=\"" + str(year) + "\" DOY=\"" + str(sidedress_doy)
                          + "\" IFType=\"" + fert_type + "\" FerCode=\"" + fert_code
                          + "\" FInP=\"100\" DFert=\"" + fert_depth + "\" ACrbFer=\"0\" ANFer=\"" + fert_amt_kg
                          + "\" APFer=\"0\" AKFer=\"0\" ACFer=\"0\" AOFer=\"0\" FerDecRt=\"0\" VolN=\"0\" VolNRate=\"0\" />\n")

                

                # SPRING Tillage
                tdoy = int(pdoy) - 2   # 2 days prior to planting
                tillage_tool = "TI002"
                tillage_depth = "10"  # cm
                out.write("        <Mgt_Tillage_App Year=\"" + str(year) + "\" DOY=\"" + str(tdoy)
                          + "\" TImpl=\"" + str(tillage_tool) + "\" TDep=\"" + str(tillage_depth) + "\" />\n")

                # HARVEST
                hdoy = "334"  # DOY 334 = Nov 30
                hcom = "H"
                hpc = "100"
                knock_down = "100"
                hbpc = "0"
                out.write("        <Mgt_Harvest_App Year=\"" + str(year) + "\" DOY=\"" + str(hdoy)
                          + "\" HCom=\"" + hcom + "\" HPc=\"" + hpc
                          + "\" HBmin=\"" + hbpc + "\" HBPc=\"0\" HKnDnPc=\"" + knock_down + "\" />\n")

                #TILLAGE
                #FALL  Tillage
                tdoy = int(hdoy) + 7   # 1 week after harvest
                tillage_tool = "TI008"  # Subsoiler
                tillage_depth = 16  # inches
                tillage_depth = "{0:.2f}".format(tillage_depth * 2.54)  # Convert inches to cm.
                out.write("        <Mgt_Tillage_App Year=\"" + str(int(year) - 1) + "\" DOY=\"" + str(tdoy)
                          + "\" TImpl=\"" + str(tillage_tool) + "\" TDep=\"" + str(tillage_depth) + "\" />\n")

                out.write("      </Component>\n")
                out.write("    </Rotation_Components>\n")
                out.write("  </Experiment>\n")
        out.write("</XDB>\n")
    return()