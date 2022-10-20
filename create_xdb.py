####
# create_xdb.py

#Author: Prateek

#Note: This code is modified from the original version of  Lydia Rill


import streamlit as st
import os
import sys
from datetime import datetime, timedelta
import math
import xml
import pandas as pd
import numpy as np
from misc_func import average_bd
#
def read_soil(sdb_file):
    st.write("Reading in soil data")
    tree = xml.etree.ElementTree.parse(sdb_file)
    root = tree.getroot()
    return root,tree

def create_xdb(
        xdb_file,
        sdb_file,
        wdb_file,
        cdb_file,
        wx_id,
        cultivar,
        soilID_list,
        N_rate_list,
        SALUS_start,
        SALUS_end,
        Main_datframe,
        **kwargs):
    # for key,value in kwargs.items:
    #     if (key == start_doy):
    #         start_doy=value
    #     elif (key == Irrigation):
    #         Irrigation=value
    #     elif (key == Planting):
    #         Planting=value
    #     elif (key == split_fertapp):
    #         split_fertapp=value
    #     elif (key == Tillage):
    #         Tillage=value
    #     elif (key == Harvest):
    #         Harvest=value

    start_doy=kwargs['start_doy']
    Irrigation=kwargs['Irrigation']
    Planting=kwargs['Planting']
    split_fertapp=kwargs['split_fertapp']
    Tillage=kwargs['Tillage']
    Harvest=kwargs['Harvest']
    # Keep track of the experiment numbers.
    expID = 0
    #Total number of run years for salus
    nyrs = SALUS_end - SALUS_start + 1
    root,tree=read_soil(sdb_file)
    with open(xdb_file, 'w') as out:
            out.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
            out.write("<XDB>\n")

            # Loop through the SoilIDs.
            for i,soil_id in enumerate(soilID_list):
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
                    comp=0
                    for i,yearp in enumerate(Main_datframe['yearp']):
                        #st.write(i,yearp)
                        comp += 1
                        out.write("      <Component OrderNum=\"" + str(comp) + "\" Title=\"" + Main_datframe['crop_name'][i]
                            + "\" IPltI=\"R\" IIrrI=\"" +  Main_datframe['irrFlag'][i] + "\" IferI=\"R\" IResI=\"R\" ITilI=\"R\" IHarI=\"R\" IEnvI=\"N\">\n")
                        
                        if Irrigation:
                            out.write("        <Mgt_Irrigation_Auto DSoil=\"" + str(Main_datframe['dsoil'][i]) + "\" IAMe=\"" + Main_datframe['irr_method'][i]
                                + "\" ThetaC=\"" + str(Main_datframe['thetaC'][i]) + "\" IEPt=\"" + str(Main_datframe['endPt'][i]) + "\" />\n")
                        if Planting:
                            #st.write(Main_datframe['crop_name'][i])
                            out.write("        <Mgt_Planting CropMod=\"" + Main_datframe['crop_mode'][i] + "\" SpeciesID=\"" + Main_datframe['speciesID'][i] + "\" CultivarID=\"" +  Main_datframe['cultivar'][i]
                                + "\" Year=\"" + str(yearp) + "\" DOY=\"" + str(Main_datframe['pdoy'][i])
                                + "\" Ppop=\"" + str(Main_datframe['ppop'][i]) + "\" Ppoe=\"" + str(Main_datframe['ppop'][i])
                                + "\" PlMe=\"S\" PlDs=\"R\" RowSpc=\"" + str(Main_datframe['rowspc'][i])
                                + "\" SDepth=\"" + str(Main_datframe['plant_depth'][i]) + "\" />\n")
                        if split_fertapp:
                            for j in range(Main_datframe['Num_fert_event'][i]):
                                fert_amt_kg = "{0:.2f}".format((float(N_rate) * Main_datframe['fert_amt_frac_list'][i][j]))
                                out.write("        <Mgt_Fertilizer_App Year=\"" + str(Main_datframe['yearf_list'][i][j]) + "\" DOY=\"" + str(Main_datframe['fdoy_list'][i][j])
                                + "\" IFType=\"" + Main_datframe['fert_type_list'][i][j] + "\" FerCode=\"" + Main_datframe['fert_code_list'][i][j]
                                + "\" FInP=\"100\" DFert=\"" + Main_datframe['fert_depth_list'][i][j] + "\" ACrbFer=\"0\" ANFer=\"" + fert_amt_kg
                                + "\" APFer=\"0\" AKFer=\"0\" ACFer=\"0\" AOFer=\"0\" FerDecRt=\"0\" VolN=\"0\" VolNRate=\"0\" />\n")

                        if Tillage:
                            #Tillgae_comp_list=[len(tdoy_list),len(tillage_tool_list),len(tillage_depth_list)]
                            for j in range(Main_datframe['Num_till_event'][i]):
                                out.write("        <Mgt_Tillage_App Year=\"" + str(Main_datframe['yeart_list'][i][j]) + "\" DOY=\"" + str(Main_datframe['tdoy_list'][i][j])
                                        + "\" TImpl=\"" + str(Main_datframe['tillage_tool_list'][i][j]) + "\" TDep=\"" + str(Main_datframe['tillage_depth_list'][i][j]) + "\" />\n")
                        
                        if Harvest:
                            out.write("        <Mgt_Harvest_App Year=\"" + str(Main_datframe['yearh'][i]) + "\" DOY=\"" + str(Main_datframe['hdoy'][i])
                            + "\" HCom=\"" + Main_datframe['hcom'][i] + "\" HPc=\"" + Main_datframe['hpc'][i]
                            + "\" HBmin=\"" + Main_datframe['hbpc'][i] + "\" HBPc=\"0\" HKnDnPc=\"" +  Main_datframe['knock_down'][i] + "\" />\n")
                    
                        out.write("      </Component>\n")
                    out.write("    </Rotation_Components>\n")

                    out.write("  </Experiment>\n")
            out.write("</XDB>\n")
    return()