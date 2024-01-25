####
# create_xdb.py

#Author: Prateek

#Note: This code is modified from the original version of  Lydia Rill


#from tkinter import E
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
        path,
        xdb_file,
        sdb_file,
        wdb_file,
        cdb_file,
        Exp_dataframe,
        Main_datframe_all,
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

    
    Irrigation=kwargs['Irrigation']
    Planting=kwargs['Planting']
    split_fertapp=kwargs['split_fertapp']
    Tillage=kwargs['Tillage']
    Harvest=kwargs['Harvest']
    expfile=kwargs['uploadfile_e']
    mngfile=kwargs['uploadfile_m']
    #path =kwargs['Path_file']
    # if mngfile:
    #     Main_datframe_all['fert_amt_frac_list']=Main_datframe_all['fert_amt_frac_list'].astype(object)
    #     #st.write(Main_datframe_all.dtypes)
    # Keep track of the experiment numbers.
    expID = 0
    #Total number of run years for salus
    
    root,tree=read_soil(sdb_file)
    #with open(path + '/'+ xdb_file, 'w+') as out:
    with open(xdb_file, 'w') as out:
            out.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
            out.write("<XDB>\n")

            
            st.write("-Writing soil", Exp_dataframe['soilID_list'])
            # # Convert soilID to a string
            # soil_id = str(soil_id)

            # # Get soil parameters for initial conditions.
            # # Calculate the average Bulk Density for layers 0-30cm and 30cm-bottom.
            # avg_bd_top, avg_bd_bottom, depth_top, depth_bottom, max_depth = average_bd(soil_id, root, 30)

                # Loop through the N rates.
                
            #st.write("---Writing N rate", N_rate)

            expID += 1
            for j,enum in enumerate(Exp_dataframe['Experiment_number']):
                Main_datframe=Main_datframe_all[Main_datframe_all['Experiment_number']==enum]
                Main_datframe=Main_datframe.reset_index(drop=True)
                st.write("---Writing for Experiment number:", enum )
                # Experiment title to distinguish the differences in each experiment.
                nyrs = Exp_dataframe['SALUS_end'][j] - Exp_dataframe['SALUS_start'][j] + 1
                out.write("  <Experiment ExpID=\"" + str(enum) + "\" Title=\"" + Exp_dataframe["Experiment_name"][j]
                        + "\" NYrs=\"" + str(nyrs) + "\" SYear=\"" + str(Exp_dataframe['SALUS_start'][j])
                        + "\" SDOY=\"" + str(Exp_dataframe['start_doy'][j]) + "\" ISwWat=\"Y\" ISwNit=\"Y\" ISwPho=\"N\" Frop=\"1\" Soilfp=\"" + sdb_file
                        + "\" SoilID=\"" + str(Exp_dataframe['soilID_list'][j])
                        + "\" Weatherfp=\"" + wdb_file + "\" StationID=\"" +str(Exp_dataframe['wx_id'][j])
                        + "\" Cropfp=\"" + cdb_file
                        + "\" NRrepSq=\"0\" MeEvp=\"R\" MeInf=\"R\" kResOrg=\"3.914E-5\" kSloOrg=\"0.00013699\" >\n")
                
                
                
                    # Get soil parameters for initial conditions.
                # Calculate the average Bulk Density for layers 0-30cm and 30cm-bottom.
                avg_bd_top, avg_bd_bottom, depth_top, depth_bottom, max_depth = average_bd( str(Exp_dataframe['soilID_list'][j]), root, 30)
                n_kg = 30
                n1_kg = n_kg * 0.4  # Top 30 cm get 40% of the N (value from Bruno a while ago)
                n2_kg = n_kg * 0.6
                n1_ppm = '%.2f' % (n1_kg / (depth_top * avg_bd_top * 10000) * 1000)
                out.write("    <Mgt_InitialCond Year=\"" + str(Exp_dataframe['SALUS_start'][j]) + "\" DOY=\"" +  str(Exp_dataframe['start_doy'][j]) + "\" >\n")
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
                        out.write("        <Mgt_Planting CropMod=\"" + str(Main_datframe['crop_mode'][i]) + "\" SpeciesID=\"" + str(Main_datframe['speciesID'][i]) 
                            + "\" CultivarID=\"" +  str(Main_datframe['cultivar'][i])
                            + "\" Year=\"" + str(yearp) + "\" DOY=\"" + str(Main_datframe['pdoy'][i])
                            + "\" Ppop=\"" + str(Main_datframe['ppop'][i]) + "\" Ppoe=\"" + str(Main_datframe['ppop'][i])
                            + "\" PlMe=\"S\" PlDs=\"R\" RowSpc=\"" + str(Main_datframe['rowspc'][i])
                            + "\" SDepth=\"" + str(Main_datframe['plant_depth'][i]) + "\" />\n")
                    if split_fertapp:
                        for j in range(Main_datframe['Num_fert_event'][i]):
                            st.write(Main_datframe['fert_amt_frac_list'][i][j])
                            fert_amt_kg = "{0:.2f}".format(Main_datframe['fert_amt_frac_list'][i][j])
                            out.write("        <Mgt_Fertilizer_App Year=\"" + str(Main_datframe['yearf_list'][i][j]).strip() + "\" DOY=\"" + str(Main_datframe['fdoy_list'][i][j]).strip()
                            + "\" IFType=\"" + str(Main_datframe['fert_type_list'][i][j]).strip() + "\" FerCode=\"" + str(Main_datframe['fert_code_list'][i][j]).strip()
                            + "\" FInP=\"100\" DFert=\"" + str(Main_datframe['fert_depth_list'][i][j]).strip() + "\" ACrbFer=\"0\" ANFer=\"" + fert_amt_kg
                            + "\" APFer=\"0\" AKFer=\"0\" ACFer=\"0\" AOFer=\"0\" FerDecRt=\"0\" VolN=\"0\" VolNRate=\"0\" />\n")

                    if Tillage:
                        #Tillgae_comp_list=[len(tdoy_list),len(tillage_tool_list),len(tillage_depth_list)]
                        for j in range(Main_datframe['Num_till_event'][i]):
                            out.write("        <Mgt_Tillage_App Year=\"" + str(Main_datframe['yeart_list'][i][j]).strip() + "\" DOY=\"" + str(Main_datframe['tdoy_list'][i][j]).strip()
                                    + "\" TImpl=\"" + str(Main_datframe['tillage_tool_list'][i][j]).strip() + "\" TDep=\"" + str(Main_datframe['tillage_depth_list'][i][j]).strip() + "\" />\n")
                    
                    if Harvest:
                        st.write(Main_datframe['yearh'][i])
                        st.write(str(Main_datframe['yearh'][i])+"Hello")
                        #Main_datframe['yearh'][i]
                        out.write("        <Mgt_Harvest_App Year=\"" + str(Main_datframe['yearh'][i])
                        + "\" DOY=\"" + str(Main_datframe['hdoy'][i])
                        + "\" HCom=\"" + str(Main_datframe['hcom'][i]) 
                        + "\" HPc=\"" + str(Main_datframe['hpc'][i])
                        + "\" HBmin=\"" + str(Main_datframe['hbpc'][i])
                        + "\" HBPc=\"0\" HKnDnPc=\"" +  str(Main_datframe['knock_down'][i])
                        + "\" />\n")
                    out.write("      </Component>\n")
                out.write("    </Rotation_Components>\n")

                out.write("  </Experiment>\n")
            out.write("</XDB>\n")
            # out.seek(0)
            # xml_content=out.read()
    return ()#xml_content
