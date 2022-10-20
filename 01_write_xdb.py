####
# 01_write_xdb.py
# Lydia Price
# 05/03/2022
#
# Python 3.10
#
# This python script write the experiment file and associated shell script for an example field.
# The field's management in hard-coded.
# The
####

import os
import sys
import shutil
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

# Import Lydia's python functions.
from write_xdb import write_xdb


# Check if a file or directory exists.
# If it does not exist, exit the script!
# You must set fileflag=True for a file.
def check_exists_error(tmp_location, **kwargs):
    fileflag = False
    if 'fileflag' in kwargs:
        fileflag = kwargs['fileflag']
    if fileflag:
        if not os.path.isfile(tmp_location):  # Check if the file exists.
            print("ERROR: cannot find the file", tmp_location)
            sys.exit()
    else:
        if not os.path.isdir(tmp_location):  # Check if the directory exists.
            print("ERROR: cannot find the directory", tmp_location)
            sys.exit()


# Function to delete an entire directory and remake it.
# This is used to delete old files.
def delete_old_files(tmp_dir):
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)



if __name__ == "__main__":

    # root directory for this project
    # rootdir = r'C:\Users\rilllydi\Michigan State University\EESBassoLab - Lydia_Project_Progress\SALUS_Simulation_Example\Hasenick_222_Main_Farm'  # Too slow to run in on the synced folder!
    #rootdir = r'D:\Older_Projects\Share_with_others\Mukta\Example_Field'
    rootdir = r'D:\MSU Work\Lydia\SALUS_Simulation_Example\SALUS_Simulation_Example\IL_Smith_Farms_Horn_South'

    ###
    # Specific field management information. Hard coded due to lack of time before project deadline.
    # corn_cultivar = county GEOID or FIPS code (5 digits usually, but no leading zero is ok). If this county cultivarID does not exist in the crop file, use the state abbreviation instead (e.g. MI).
    # soilID_list = list of soilIDs to simulate. These should exist in the SDB XML file.
    # wx_id = StationID in the WDB file
    # total_N_list = list of total N fertilizer amounts to apply. Units in kg of N/ha.
    ###

    #corn_cultivar = "26075"  # Hasenick 222 Main Farm
    # soilID_list = [188754, 188756, 188757, 188769, 188770, 188772, 188780, 188781]
    #wx_id = "42.3583N_84.6833W"

    #corn_cultivar = "18131"  # Hasenick 210 Well
    #soilID_list = [188754, 188755, 188756, 188757, 188760, 188769, 188770, 188777, 188779, 188780, 188781, 188782]
    #wx_id = "42.3583N_84.7250W" 

    corn_cultivar = "17167"   #IL Smith_Farms Horn_South    
    soilID_list = [199353, 199290, 199312]    
    wx_id = "39.7333N_89.9333W"
    total_N_list = [0, 50, 100, 150, 200, 250, 300]

    # This key_name distinguishes the scenario you are running.
    key_name = "test_20220929"

    # Irrigation flag
    irrigation_flag = False

    # Output directory
    # Erase previous result so we know the results are updated.
    outdir = os.path.join(rootdir, key_name)
    delete_old_files(outdir)

    # Experiment file you will create
    xdb_file = os.path.join(outdir, "nrate_experiment.xdb.xml")

    # Crop file
    cdb_file = os.path.join(rootdir, 'crops_20181213_olderParams_byCounty_withStateParams.cdb.xml')
    check_exists_error(cdb_file, fileflag=True)

    # Weather file
    wdb_file = os.path.join(rootdir, wx_id + '.wdb.xml') #encoding="utf-8"
    check_exists_error(wdb_file, fileflag=True)

    # Soil file
    sdb_file = os.path.join(rootdir, "CONUS.sdb.xml")
    check_exists_error(sdb_file, fileflag=True)

    # SALUS Version
    # salus_version = r"D:\SALUS_Desktop_Version\SalusWin64-2022-04-08\SalusC_64.exe"
    salus_version = r"D:\MSU Work\Brian\SalusWorkingWin\SalusC_64.exe"

    if not os.path.isfile(salus_version):
        print("ERROR: cannot find SALUS", salus_version)

    # Global file
    # Use the default that comes with the version of SALUS.
    gdb_file = os.path.join(os.path.dirname(salus_version), 'salus.gdb.xml')
    check_exists_error(gdb_file, fileflag=True)

    #### SALUS Result Variables ####
    # Specify the SALUS variables you need in the output.
    # You should always include SpeciesID.
    # Make sure you do NOT have any spaces!
    daily_vars = ('ExpID,Title,SpeciesID,RcID,GWAD,CWAD,'
                  + 'LAI,gPhase,'
                  + 'TMNA,TMXA,Rain,'
                  + 'KRPP,OWAD,N_Plants,NLCC,'
                  + 'layer:12:NIADL,layer:12:BD,layer:12:LL,layer:12:DUL,layer:12:SW,layer:12:SWCN,layer:12:SAT,'
                  + 'ROFC,DRNC,SWXD,'
                  + 'LeafEq,LeafEqEar,LeafEqFinal,'
                  + 'DrghtStressDays,NitroStressDays,NitroFac,DrghtFac,'  # Stress factors
                  + 'NIAD,NLCC,DRNC,ROFC,N_NitrateBl,'  # N output
                  + 'C_AtmoCO2,C_CO2,C_Net,C_Out,'  # C Output
                  + 'C_ActOrgBl,C_SloOrgBl,C_ResOrgBl,'  # SOC
                  + 'layer:12:C_ResOrg,layer:12:C_ActOrg,layer:12:C_SloOrg,'  # SOC by layer
                  + 'EOAC,EOAD,ETAC,ETAD,'  # PET
                  + 'IRRC'  # Irrigation
                  )
    seas_vars = daily_vars

    # Call the write_xdb function to write the experiment file.
    write_xdb(
        xdb_file,
        sdb_file,
        wdb_file,
        cdb_file,
        irrigation_flag,
        wx_id,
        corn_cultivar,
        soilID_list,
        total_N_list,
    )

    # Write the shell file to easily run SALUS.
    daily_file = os.path.join(outdir, "daily.csv")
    seas_file = os.path.join(outdir, "seasonal.csv")
    log_file = os.path.join(outdir, "salus.log")
    shell_file = os.path.join(outdir, "run_salus.sh")
    with open(shell_file, 'w') as out:
        out.write("# run salus.\n")
        # Include the -npoolseparate flag to get N_Nitrate variable to write out!
        # Include the n20diffusion flag as well. These are important flags for the model to be the most accurate!
        salus_line = ('"' + salus_version + '"' + " -wn -npoolseparate -n2odiffusion -frozensoil gdb=\"" + gdb_file
                  + "\" xdb=\"" + xdb_file + "\"")
        if daily_vars:
            salus_line += (" file1=\"" + daily_file + "\" freq1=\"1\" vars1=\"" + daily_vars + "\"")
        if seas_vars:
            salus_line += (" file2=\"" + seas_file + "\" freq2=\"season\" vars2=\"" + seas_vars + "\"")

        salus_line += (" msglevel=\"status\" > \"" + log_file + "\"\n")
        out.write(salus_line)