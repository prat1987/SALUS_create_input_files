from ast import Num
from ast import literal_eval
from curses.ascii import SP
#from msilib.schema import CheckBox
import streamlit as st
from streamlit_tags import st_tags
#import xml.etree.ElementTree as ET
import xml
import pandas as pd
import numpy as np
from create_xdb import create_xdb
from misc_func import check_exists_error,read_wx
import hiplot as hip
import base64
import time
st.write("""
# SALUS utility app
""")

st.write('Author: Prateek Sharma, Graduate Student in the Basso Lab at MSU'
)

st.write('Note: This app will create a customized experimental file for running SALUS\
     based on user input.Also, the user can visualize the weather input data using Hiplot\
     However, before using this app make sure that you have the following files in the same folder as *.py: **soil file (sdb.xml)**,\
        **weather file (wbd.xml)**,\
        **crop file (cbd.xml)**')
# st.write('soil file (*.sdb.xml),\
#         weather file (*wbd.xml),\
#         crop file (*.cbd.xml)')

#st.markdown('**HELP**')
st.markdown('**HELP: Please click on the following link for more information about the files (weather, soil, and experiment) structure in SALUS**')
link = '[SALUS Data Structure](https://basso.ees.msu.edu/salus/tools/data-structure.php)'
st.markdown(link, unsafe_allow_html=True)

#Enter by the user the name of the weather, soil, crop file
#Soil file 
st.sidebar.markdown('## Step 1: Provide names for input files')
sdb_file= st.sidebar.text_input('Soil file name','CONUS.sdb.xml')
#@st.cache(hash_funcs={ET: lambda _: None})
#@st.cache(hash_funcs={xml.etree.ElementTree.parse: lambda _: None},suppress_st_warning=True)

def add_values_in_dict(sample_dict, key, list_of_values):
    ''' Append multiple values to a key in 
        the given dictionary '''
    if key not in sample_dict:
        sample_dict[key] = list()
    sample_dict[key].extend(list_of_values)
    return sample_dict

def convert_int(dlist):
    dlist=[int(item) for item in dlist]
    return dlist
def convert_float(dlist):
    dlist=[float(item) for item in dlist]
    return dlist
def convert_str(dlist):
    dlist=[str(item) for item in dlist]
    return dlist
def download_button(object_to_download, download_filename, button_text):
    # Generate the download link for the XML content
    b64 = base64.b64encode(object_to_download.encode()).decode()
    href = f'<a href="data:file/xml;base64,{b64}" download="{download_filename}">{button_text}</a>'
    st.markdown(href, unsafe_allow_html=True)
import streamlit as st

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')



#@st.cache(allow_output_mutation=True)
if 'get_data' not in st.session_state:
    st.session_state['get_data'] = []

#@st.cache(allow_output_mutation=True)
@st.cache_data()
def rot_data():
    return []

#@st.cache(allow_output_mutation=True)
if 'exp_data' not in st.session_state:
    st.session_state['exp_data'] = []
#st.write('Soil file:', sdb_file)

#Weather file 
wdb_file= st.sidebar.text_input('Weather file name','BC.wdb.xml')


#Crop file 
cdb_file= st.sidebar.text_input('Crop file name','crops_kbs.cdb.xml')

st.sidebar.markdown('## Step 2: Provide names for output file')
# Experimental file 
xdb_file=st.sidebar.text_input('Experimental file name','resource_grad.xdb.xml')
# Path to save the file
path_file=st.sidebar.text_input('Path to save the file','/Users/prateeksharma/SALUS_experiment_files')


#st.write(cdb_file.endswith('xml'))
end_with_xml=[cdb_file.endswith('xml'),wdb_file.endswith('xml'),sdb_file.endswith('xml'),\
    xdb_file.endswith('xml')]
#Condition to check if all files ended with
if  any(t == False for t in end_with_xml):
        st.write('WARNING: All XML file should end with .xml')


else:
    # check if file exist in the directory
    # check_exists_error(sdb_file, fileflag=True)
    # check_exists_error(wdb_file, fileflag=True)
    # check_exists_error(cdb_file, fileflag=True)

    st.sidebar.markdown('## Step 3: Select run type')
    selection=st.sidebar.selectbox(
        "Please select one option", #Drop Down Menu Name

        [
            "Create a experiment file",
            "Create a weather file",
            "Create a soil file",
            "Plot weather",
            "Output analysis" #First option in menu
        
        ]
    )
    
    if (selection=="Create a experiment file"):
        st.markdown('## Select different options for run type')
        uploadfile_m=st.sidebar.checkbox('Upload management file')
        uploadfile_e=st.sidebar.checkbox('Upload experimental file')
        with st.form(key='Initial'):
            if uploadfile_e:
                uploaded_file_e = st.file_uploader("Choose a experiment file")
                if uploaded_file_e is not None:  
                    # Can be used wherever a "file-like" object is accepted:
                    dataframe_e = pd.read_csv(uploaded_file_e)
                    st.write(dataframe_e)
            else:
                Experiment= int(st.number_input('Experiment number', 1))
                Experiment_name= st.text_input('Experiment name', "")
                SALUS_start = int(st.slider(label='SALUS start year', key='Year start',value=int(1980),\
                    min_value=int(1850), max_value=int(2022), step=1))
                SALUS_end = int(st.slider(label='SALUS end year', key='Year end',value=int(1982),\
                    min_value=int(1850), max_value=int(2022), step=1))
                spinup = st.radio(
                "Wants to add Spinup with repeated management?",
                ('Yes', 'No'))
                rotation=st.radio(
                "Wants to add rotation crop management?",
                ('Yes', 'No'))

                if spinup == 'Yes':
                    Years_spinup=st.slider(label='Please selet no. of spin up years', key='Year spin',value=int(10),\
                    min_value=0, max_value=1000, step=1)
                if rotation == 'Yes':
                    crop_rotation=st.slider(label='Please selet no. of crops to rotate', key='Rotation',value=int(2),\
                    min_value=0, max_value=5, step=1)
                
                nyrs = SALUS_end - SALUS_start + 1
            #
                
                #Start DOY 
                start_doy = 1
                
                wx_id = str(st.text_input('### Weather Station ID','KBSS'))
                
                
                soilID_list =st.number_input('SoilID',187069)

                N_init_list=st.number_input('Enter Initail N for each soil type (Kg/ha):', 30)
               
                N_init_list = float(N_init_list)
                
            #N_init_list = convert_float(N_init_list)
           # N_rate_list = convert_int(N_rate_list )
            
            if uploadfile_m:
                uploaded_file_m = st.file_uploader("Choose a management file")
                if uploaded_file_m is not None:  
                    # Can be used wherever a "file-like" object is accepted:
                   
                    convert_dict={'fert_amt_frac_list': literal_eval,'yearf_list':literal_eval,'fdoy_list':literal_eval,'fert_type_list':literal_eval,\
                        'fert_depth_list':literal_eval,'fert_code_list':literal_eval,'yeart_list':literal_eval,'tdoy_list':literal_eval,'tillage_tool_list':literal_eval,\
                            'tillage_depth_list':literal_eval}
                        
                    dataframe_m = pd.read_csv(uploaded_file_m,converters=convert_dict)
                    #st.write(dataframe_m)
                CropDetails=st.checkbox('Crop Information')
                Planting=st.checkbox('Planting')
                Irrigation=st.checkbox('Irrigation')
                split_fertapp=st.checkbox('N fertilizer application')
                Tillage=st.checkbox('Tillage')
                Harvest=st.checkbox('Harvesting')
            else:

                CropDetails=st.checkbox('Crop Information')
                Planting=st.checkbox('Planting')
                Irrigation=st.checkbox('Irrigation')
                split_fertapp=st.checkbox('N fertilizer application')
                Tillage=st.checkbox('Tillage')
                Harvest=st.checkbox('Harvesting')
        
            #if (Planting):
        #Crop Information

                if CropDetails:
                    st.markdown("### Crop detail information")
                    st.write("Enter crop information:")
                    st.write("Please be careful with crop detail make\
                    sure it is correct,otherwise SALUS will throw error")
                    st.write("Hint:Cross check wth crop file(*.cdb.xml)")
                    crop_name = st.text_input('Crop name','Maize')
                    crop_mode = st.text_input('Crop mode','C')
                    speciesID = st.text_input('Crop ID','MZ')
                    cultivar = st.text_input('Crop cultivar','17167')
                else:
                    crop_name = ''
                    crop_mode = ''
                    speciesID = ''
                    cultivar = ''
                    
                # PLANTING
                if Planting:
                    st.markdown("### Planting details")
                    yearp = int(st.number_input('Planting year', SALUS_start))
                    plant_depth = st.number_input('Planting depth in cm',0.)  # 
                    ppop = st.text_input('Planting population in seeds/m2',"8")   # seeds/m2.
                    rowspc = st.text_input('Row spacing in cm',"76")   # cm
                    pdoy = st.text_input('Planting DOY',"121")   # DOY 121 = May 1  
                else:
                    yearp = ''
                    plant_depth = '' # 
                    ppop = ''
                    rowspc = ''
                    pdoy = ''
                
                #st.session_state['get_data'].append({"crop_name":crop_name, "crop_mode ": crop_mode, "speciesID":speciesID,\
                #        "cultivar": cultivar,"plant_depth":plant_depth,"yearp":yearp,"ppop ":ppop ,"rowspc":rowspc,\
                #            "pdoy":pdoy})
                if Irrigation:
                    st.markdown("### Irrigation information")
                    irrFlag = 'A'  # Auto
                    irr_method = st.text_input('Irrigation method','IR004')  # Sprinkler
                    dsoil = st.number_input('Management depth of soil to look at for irrigation',30)  # Management depth of soil to look at for irrig (cm)
                    thetaC = st.number_input(' Threshold for automatic application (% of max avail. water)',70)   # Threshold for automatic application (% of max avail. water)
                    endPt = st.number_input(' End point for automatic application (% of max avail. water)',90)  # End point for automatic application (% of max avail. water)
                else:
                    irrFlag = 'N'
                    irr_method =''
                    dsoil = ''
                    thetaC = ''
                    endPt = ''

            
                

                # FERTILIZE
                if split_fertapp:
                    st.markdown("### Split N fertilizer details")
                    
                    Num_fert_event = st.slider(label='Total number of fertilizer splits', key='fert',value=int(1),\
                        min_value=1, max_value=10, step=1)
                    
                    yearf_list= st_tags(
                    label='Enter fertilizer application year:',
                    text='Press enter to add more',
                    value=[1980],
                    suggestions=[],
                    maxtags=20,
                    key="yearf")

                    fdoy_list = st_tags(
                    label='Enter fertilizer application DOY:',
                    text='Press enter to add more',
                    value=["121"],
                    suggestions=[],
                    maxtags=20,
                    key="fdoy")

                    
                    fert_code_list = st_tags(
                    label='Enter fertilizer code:',
                    text='Press enter to add more',
                    value=["AP001"],
                    suggestions=[],
                    maxtags=20,
                    key="fcode")

                    fert_amt_frac_list = st_tags(
                    label='Amount of N applied in Kg/ha:',
                    text='Press enter to add more',
                    value=["150"],
                    suggestions=[],
                    maxtags=20,
                    key="frac_fert")

                    fert_type_list = st_tags(
                    label=' Enter Fertilizer types:',
                    text='Press enter to add more',
                    value=["FE001"],
                    suggestions=[],
                    maxtags=20,
                    key="ferttype")

                    fert_depth_list = st_tags(
                    label='Enter fertilizer application depths(cm):',
                    text='Press enter to add more',
                    value=["0"],
                    suggestions=[],
                    maxtags=20,
                    key="fdepth")
                    fert_amt_frac_list =convert_float(fert_amt_frac_list)
                    fdoy_list = convert_int(fdoy_list)
                    yearf_list = convert_int(yearf_list)
                    
                        #st.write("N fertilizer rates list for experiments",N_rate_list_int)
                    fertilizer_comp_list=[len(fdoy_list),len(fert_amt_frac_list),len(fert_type_list),len(fert_depth_list),len(fert_code_list)]
                else:
                    Num_fert_event=0
                    yearf_list=[]
                    fdoy_list=[]
                    fert_amt_frac_list=[]
                    fert_type_list=[]
                    fert_depth_list=[]
                    fert_code_list=[]
                    
                    
                        
                    
                    
        
                
            #Num_split = st.slider(label='Total number of splits', key='split',value=int(2),\
            #        min_value=1, max_value=10, step=1

        
                if Tillage:
                    st.markdown("### Tilllag events details")
                    Num_till_event = st.slider(label='Total number of tillage events', key='till',value=int(1),\
                        min_value=1, max_value=10, step=1)
                    
                    yeart_list= st_tags(
                    label='Enter tillage application year:',
                    text='Press enter to add more',
                    value=[SALUS_start],
                    suggestions=[],
                    maxtags=20,
                    key="yearT")


                    tdoy_list = st_tags(
                    label='Enter Tilling DOY:',
                    text='Press enter to add more',
                    value=["119"],
                    suggestions=[],
                    maxtags=20,
                    key="tdoy")

                    tillage_tool_list = st_tags(
                    label=' Enter Tilling types:',
                    text='Press enter to add more',
                    value=["TI002"],
                    suggestions=[],
                    maxtags=20,
                    key="tilltype")

                    tillage_depth_list = st_tags(
                    label='Enter Tilling depths(cm):',
                    text='Press enter to add more',
                    value=["10"],
                    suggestions=[],
                    maxtags=20,
                    key="tdepth")
                    tdoy_list = convert_int(tdoy_list)
                    yeart_list = convert_int(yeart_list)
                    #add = st.form_submit_button(label='add')
                            
                        #st.write("N fertilizer rates list for experiments",N_rate_list_int)
                    Tillgae_comp_list=[len(tdoy_list),len(tillage_tool_list),len(tillage_depth_list)]
                else:
                    Num_till_event=0
                    yeart_list=[]
                    tdoy_list=[]
                    tillage_tool_list=[]
                    tillage_depth_list=[]
                    
                        
                    
                    #N_init_list_float =[float(item) for item in N_init_list]
                
                    
                    
                if Harvest:
                    st.markdown("### Harvest details")
                    # HARVEST
                    yearh = int(st.number_input('Harvest year', SALUS_start))
                    hdoy = st.text_input('Harvest DOY',"334")  # DOY 334 = Nov 30
                    hcom = st.text_input('Hcom',"H")
                    hpc = st.text_input('Harvest percentage',"100")
                    knock_down = st.text_input('Knock down percent',"100")
                    hbpc = st.text_input('Harvest byproducts percent',"0")
                else:
                    yearh = ''
                    hdoy = ''
                    hcom = ''
                    hpc = ''
                    knock_down = ''
                    hbpc = ''

            submit_button = st.form_submit_button(label='Submit')        
                    #st.write("N fertilizer rates list for experiments",N_rate_list_int)
        Error_enter=False
        if submit_button:
        
            # if (len(soilID_list )!=len(N_init_list)):
            #     st.markdown('## ERROR: Soil initial N value are not same as number of soil type')
            #     Error_enter=True
                #st.write("### Results:")
                #st.write(type(N_rate_list))
                #N_rate_list.append(Nrate)
            #else:
            if uploadfile_e:
                st.write(dataframe_e)
            else:
                #Checking if end year is later than start year 
                if (int(SALUS_end) <= int(SALUS_start)):
                    st.markdown('## ERROR!!!!!: Start year cannot be later than end year')
                    Error_enter=True
                #Total number of run years for salus
                
                # if (spinup == 'Yes') & (Years_spinup>=nyrs):
                #     st.markdown('## ERROR!!!: Spin up years > Simulation years')
                #     Error_enter=True
                if (Error_enter==False):
                    st.write("Start year SALUS:",SALUS_start)
                    st.write("End year SALUS:",SALUS_end)
                    st.write("Final list of soils",soilID_list)
            if uploadfile_m:
                st.write(dataframe_m)
                #st.write(dataframe_m[['yearf_list','yeart_list']].dtypes)
            else:
                #st.write("Final list N fert rate (Kg/ha)",N_rate_list)
                if Tillage:
                    if any(t!=Num_till_event for t in Tillgae_comp_list ):
                        st.markdown('## ERROR!!!!!!: Number of tillage entries should be same as the number of tillage events')
                        Error_enter=True
                        
                    else:
                        if (Error_enter==False):
                            st.write("Total number of tillage events",Num_till_event)
                            st.write("Tillage events DOY",tdoy_list)
                            st.write("Tillage types",tillage_tool_list)
                            st.write("Tillage depths (cm)",tillage_depth_list)
                    
                if split_fertapp:
                    if any(t!=Num_fert_event for t in fertilizer_comp_list ):
                        st.markdown('## ERROR!!!!!!: Number of fetilizer entries should be same as the number of application events')
                        Error_enter=True
                        
                    else:
                        if (Error_enter==False):
                            st.write("Total number of fertilizer events",Num_fert_event)
                            st.write("Fertilizer events DOY",fdoy_list)
                            st.write("Fertilizer types",fert_type_list)
                            st.write("Fertilizer codes",fert_code_list)
                            st.write("Fertilizer depths (cm)",fert_depth_list)
                            st.write("Fertilizer split fractions (0-1)",fert_amt_frac_list)

        row1,row2,row3=st.columns([1,1,1])
        with row1:
            M_data=st.checkbox('Management details')
        with row2:
            E_data=st.checkbox('Experiment details')    
        with  row3:
            write_data= st.checkbox('Export data as CSV')   
          
        
        col1, col2, col3,col4 = st.columns([1,1,1,1])

        with col1:
            add_data=st.button('Add entry')
            
        with col2:
            remove_last=st.button('Delete last entry')
        with col3:
            reset_data=st.button('Reset')
            
        with col4:
            show_data=st.button('Show')

        
        # add_data=st.button('Add entry to DataFrame')
        # remove_last=st.button('Delete last entry to DataFrame')
        # reset_data=st.button('Reset DataFrame')
        
        

        if (add_data):
            if (Error_enter==False):
                if E_data:

                    if uploadfile_e:
                        st.write("##Error: Already in the dataframe format read from experimental file")
                        if write_data:
                            dataframe_e.to_csv('Experiment_file_createdfromfile.csv')
                    else:
                        st.write("##Error: Added the data to Experiment file")
                        st.session_state['exp_data'].append({"Experiment_number":Experiment,"Experiment_name":Experiment_name,"SALUS_start":SALUS_start,"SALUS_end":SALUS_end, "start_doy":start_doy,\
                        "wx_id":wx_id, "soilID_list":soilID_list})
                        if write_data:
                            pd.DataFrame(st.session_state['exp_data']).to_csv('Experiment_file.csv')


                if M_data: 
                    if uploadfile_m:
                        st.write("##Error: Already in the dataframe format; read from management file")
                        if write_data:
                            dataframe_m.to_csv('Management_file_createdfromfile.csv')
                    else:
                        if (rotation=='Yes'):
                            
                        
                            st.session_state['get_data'].append({"Experiment_number":Experiment,"crop_name":crop_name, "crop_mode": crop_mode, "speciesID":speciesID,\
                                    "cultivar": cultivar,"plant_depth":plant_depth,"yearp":yearp,"ppop":ppop ,"rowspc":rowspc,\
                                        "pdoy":pdoy,"irrFlag":irrFlag,"irr_method":irr_method,"dsoil":dsoil,"thetaC":thetaC,"endPt":endPt,\
                                        "Num_fert_event":Num_fert_event,"fert_amt_frac_list":fert_amt_frac_list,"fdoy_list":fdoy_list,"yearf_list":yearf_list,\
                                        "fert_type_list":fert_type_list,"fert_depth_list":fert_depth_list,"fert_code_list":fert_code_list,\
                                        "Num_till_event":Num_till_event,"tdoy_list":tdoy_list,"yeart_list":yeart_list,"tillage_tool_list":tillage_tool_list,"tillage_depth_list":tillage_depth_list,\
                                        "yearh":yearh, "hdoy":hdoy,"hcom":hcom,"hpc":hpc,"knock_down":knock_down,"hbpc":hbpc})
                            st.write(len(pd.DataFrame(st.session_state['get_data']).index))
                            #dataframe_m=get_dataframe(pd.DataFrame(st.session_state['get_data']).columns)
                            st.write("outside",len(pd.DataFrame(st.session_state['get_data']).index),crop_rotation)
                            if (len(pd.DataFrame(st.session_state['get_data']).index)==crop_rotation):
                                q=nyrs//crop_rotation
                                z=-1
                                for l in range(q):
                                    st.write(q)

                                    for crop in range(crop_rotation):
                                        z+=1
                                        year_p=SALUS_start + z
                                        year_h=SALUS_start + z
                                        #st.session_state['get_data'][crop]["yearp"]=year_p
                                        #st.session_state['get_data'][crop]["yearh"]=year_h
                                        st.write(pd.DataFrame(st.session_state['get_data']))
                                        #if z==0:
                                        rot_data().append(st.session_state['get_data'][crop])
                                        rot_data()[z]["yearp"]=year_p
                                        rot_data()[z]["yearh"]=year_h
                                        #else:
                                        #rot_data().append(st.session_state['get_data'][crop])
                                        #st.write(pd.DataFrame(rot_data()))
                                        st.write(z,rot_data()[z])

                                # st.write("Inside",len(pd.DataFrame(st.session_state['get_data']).index),crop_rotation)
                                # if spinup =='Yes':
                                #     for i in range(Years_spinup):
                                        
                                #         yearp=SALUS_start + i
                                #         yearh=SALUS_start + i 
                                #         if split_fertapp:
                                #             start_listf = [SALUS_start] * Num_fert_event
                                #             yearf_list = list(map(lambda x : x + i, start_listf))
                                #         if Tillage:
                                #             start_listt = [SALUS_start] * Num_till_event
                                #             yeart_list = list(map(lambda x : x + i, start_listt))
                                        
                                        #dataframe_m=pd.concat([dataframe_m,pd.DataFrame(st.session_state['get_data'])],ignore_index=True)
                                        
                                st.write(pd.DataFrame(rot_data()))
                                        


                        else:


                            if spinup =='Yes':
                                for i in range(Years_spinup):
                                    
                                    yearp=SALUS_start + i
                                    yearh=SALUS_start + i 
                                    if split_fertapp:
                                        start_listf = [SALUS_start] * Num_fert_event
                                        yearf_list = list(map(lambda x : x + i, start_listf))
                                    if Tillage:
                                        start_listt = [SALUS_start] * Num_till_event
                                        yeart_list = list(map(lambda x : x + i, start_listt))
                                    


                                    st.session_state['get_data'].append({"Experiment_number":Experiment,"crop_name":crop_name, "crop_mode": crop_mode, "speciesID":speciesID,\
                                    "cultivar": cultivar,"plant_depth":plant_depth,"yearp":yearp,"ppop":ppop ,"rowspc":rowspc,\
                                        "pdoy":pdoy,"irrFlag":irrFlag,"irr_method":irr_method,"dsoil":dsoil,"thetaC":thetaC,"endPt":endPt,\
                                        "Num_fert_event":Num_fert_event,"fert_amt_frac_list":fert_amt_frac_list,"fdoy_list":fdoy_list,"yearf_list":yearf_list,\
                                        "fert_type_list":fert_type_list,"fert_depth_list":fert_depth_list,"fert_code_list":fert_code_list,\
                                        "Num_till_event":Num_till_event,"tdoy_list":tdoy_list,"yeart_list":yeart_list,"tillage_tool_list":tillage_tool_list,"tillage_depth_list":tillage_depth_list,\
                                        "yearh":yearh, "hdoy":hdoy,"hcom":hcom,"hpc":hpc,"knock_down":knock_down,"hbpc":hbpc})
                            else:
                                st.session_state['get_data'].append({"Experiment_number":Experiment,"crop_name":crop_name, "crop_mode": crop_mode, "speciesID":speciesID,\
                                    "cultivar": cultivar,"plant_depth":plant_depth,"yearp":yearp,"ppop":ppop ,"rowspc":rowspc,\
                                        "pdoy":pdoy,"irrFlag":irrFlag,"irr_method":irr_method,"dsoil":dsoil,"thetaC":thetaC,"endPt":endPt,\
                                        "Num_fert_event":Num_fert_event,"fert_amt_frac_list":fert_amt_frac_list,"fdoy_list":fdoy_list,"yearf_list":yearf_list,\
                                        "fert_type_list":fert_type_list,"fert_depth_list":fert_depth_list,"fert_code_list":fert_code_list,\
                                        "Num_till_event":Num_till_event,"tdoy_list":tdoy_list,"yeart_list":yeart_list,"tillage_tool_list":tillage_tool_list,"tillage_depth_list":tillage_depth_list,\
                                        "yearh":yearh, "hdoy":hdoy,"hcom":hcom,"hpc":hpc,"knock_down":knock_down,"hbpc":hbpc})
                        if write_data:
                            if rotation == 'yes':
                                dataframe_m.to_csv('Management_file_createdfromfile.csv') 
                            else:
                                pd.DataFrame(st.session_state['get_data']).to_csv('Management_file.csv')
            else:
                st.write('First check all the error msg for the data input')
            #Main_datframe=pd.DataFrame(st.session_state['get_data'])
            st.write("## Experimental dataset")
            st.write(st.session_state['exp_data'])
            st.write(pd.DataFrame(st.session_state['exp_data']))
            st.write("## Management dataset")
            st.write(pd.DataFrame(st.session_state['get_data']))
            

        if show_data:
            if E_data:
                st.write("## Experimental dataset")
                if uploadfile_e:

                     st.write(dataframe_e)
                else:
                    st.write(pd.DataFrame(st.session_state['exp_data']))
            if M_data:  
                
                if uploadfile_m:
                    st.write("## Management dataset")
                    st.write(dataframe_m)
                else:
                    if (rotation=='Yes'):
                        st.write("## Rotational dataset")
                        st.write(pd.DataFrame(rot_data()))
                    st.write("## Management dataset")
                    st.write(pd.DataFrame(st.session_state['get_data']))
        if remove_last:
            if M_data:
                if uploadfile_m:
                    dataframe_m=dataframe_m[:-1]
                    st.write("## Management dataset")
                    st.write(dataframe_m)
                else:
                    # if (rotation):
                    #     rot_data().pop()
                    #     st.write("## Management dataset")
                    #     st.write(pd.DataFrame(st.session_state['get_data']))
                    # else:
                    st.session_state['get_data'].pop() 
                    st.write("## Management dataset")
                    st.write(pd.DataFrame(st.session_state['get_data']))

               
            if E_data:  
                if uploadfile_e:
                    dataframe_e=dataframe_e[:-1]
                    st.write("## Experimental dataset")
                    st.write(dataframe_e)
                else:
                    st.session_state['exp_data'].pop() 
                    st.write("## Experimental dataset")
                    st.write(pd.DataFrame(st.session_state['exp_data']))
        if (reset_data):
            if M_data:

                
                st.session_state['get_data'].clear() 
                rot_data().clear()
                st.write("## Management dataset")
                st.write(pd.DataFrame(st.session_state['get_data']))
                if (rotation=='Yes'):
                    st.write("## Rotational dataset")
                    st.write(pd.DataFrame(rot_data()))
            if E_data:  
                st.session_state['exp_data'].clear() 
                st.write("## Experimental dataset")
                st.write(pd.DataFrame(st.session_state['exp_data']))
            
            #     st.write("N fertilizer rates done")
         # Read in the soil file data.

    
    
    
    #load = st.checkbox('Load soil data')
    #if load:
    
        # Open the xdb file for writing.
        if st.button('Create file'):
            status_text = st.empty()
            progress_bar = st.progress(0)

            for i in range(100):
                # Update progress bar with some fancy text
                status_text.text(f"Processing... {i+1}% 🚀")
                progress_bar.progress(i + 1)
                time.sleep(0.05)  # Simulate some work being done

            
            # progress_bar = st.progress(0)
            # for i in range(100):
            #     # Update progress bar
            #     progress_bar.progress(i + 1)
            #     time.sleep(0.1) 
            if uploadfile_m:
                Main_datframe=dataframe_m
            else:
                if (rotation=='Yes'):
                    st.write("No Rotation")
                    Main_datframe=pd.DataFrame(rot_data())
                else:
                    
                    Main_datframe=pd.DataFrame(st.session_state['get_data'])
            if uploadfile_e:
                Exp_dataframe=dataframe_e
            else:
                Exp_dataframe=pd.DataFrame(st.session_state['exp_data'])
            # st.write("get_data contents:", pd.DataFrame(st.session_state['get_data']))
            # st.write("exp_data contents:", pd.DataFrame(st.session_state['exp_data']))
            # #Main_datframe=pd.DataFrame(st.session_state['get_data'])
            # st.write(len(Main_datframe.index))
            # st.write(Main_datframe)
            # st.write(len(Exp_dataframe.index))
            #if (not Main_datframe.empty and not Exp_dataframe.empty):
            if (len(Main_datframe.index)>0 and len(Exp_dataframe.index)>0):
            #
                #root,tree=read_soil(sdb_file)
                #st.write("Start writing",rotation)
                
                xml_content=create_xdb(
                    path_file,
                    xdb_file,
                    sdb_file,
                    wdb_file,
                    cdb_file,
                    Exp_dataframe,
                    Main_datframe,
                    Irrigation=Irrigation,
                    Planting=Planting,
                    split_fertapp=split_fertapp,
                    Tillage=Tillage,
                    Harvest=Harvest,
                    uploadfile_e=uploadfile_e,
                    uploadfile_m=uploadfile_m,
                    )
                status_text.text("Done! ✨🎉✨")

        # Resetting the progress bar and status text
                time.sleep(2)
                progress_bar.empty()
                status_text.empty() 
                st.text("XML Generated! Click the link below to download.")
                download_button(xml_content, "experiment_data.xml", "Download XML File")
                
                    

            else:
                st.write("##Opps! File will not be created, Please check both the data boxes and add data to both dataframes")
    elif (selection=="Plot weather"):
        wx_id = st.text_input('### Weather Station ID','39.720420N_89.920985W')
        label=["SRAD","Tmax","Tmin","Rain","WindSp","SH", "Rmax", "Rmin"]
        df_wx=read_wx(wdb_file,wx_id)
        xp=hip.Experiment.from_dataframe(df_wx[label])
        ret_val = xp.to_streamlit( key="hip").display()
    elif (selection=="Output analysis"):
        st.markdown("## This section will be avaiable soon......")
    elif (selection=="Create a weather file"):
        st.markdown('## Please click on the following link for directing to the site for creating weather file')
        link_n = '[SALUS  GRIDMET](https://salusmodel.ees.msu.edu/GRIDMET/)'
        st.markdown(link_n, unsafe_allow_html=True)
    elif (selection=="Create a soil file"):
        st.markdown("## This section will be avaiable soon......")
        
    # if st.button("Generate XML"):
    #                 st.text("XML Generated! Click the link below to download.")
    #                 download_button(xml_content, "experiment_data.xml", "Download XML File")


            
        
        


