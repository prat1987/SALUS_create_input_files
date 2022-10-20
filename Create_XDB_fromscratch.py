from ast import Num
from curses.ascii import SP
#from msilib.schema import CheckBox
import streamlit as st
from streamlit_tags import st_tags
#import xml.etree.ElementTree as ET
import xml
import pandas as pd
import numpy as np
from create_xdb import create_xdb
from misc_func import check_exists_error
st.write("""
# Create Experimental file (*xdb.xml) for SALUS
""")

st.write('Author: Prateek Sharma, Graduate Student in the Basso Lab at MSU'
)

st.write('Note: This app will create a customized experimental file for running SALUS\
     based on user input.\
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


@st.cache(allow_output_mutation=True)
#@st.cache()
def get_data():
    return []

@st.cache(allow_output_mutation=True)
#@st.cache()
def exp_data():
    return []
#st.write('Soil file:', sdb_file)

#Weather file 
wdb_file= st.sidebar.text_input('Weather file name','sample.wdb.xml')


#Crop file 
cdb_file= st.sidebar.text_input('Crop file name','sample.cdb.xml')

st.sidebar.markdown('## Step 2: Provide names for output file')
# Experimental file 
xdb_file=st.sidebar.text_input('Experimental file name','sample.xdb.xml')

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
            "Experiment",
            "Regular Runs", #First option in menu
        
        ]
    )
    
    if (selection=="Experiment"):
        st.markdown('## Select different options for run type')
        with st.form(key='Initial'):
            SALUS_start = st.slider(label='SALUS start year', key='Year start',value=int(1980),\
                min_value=1850, max_value=2022, step=1)
            SALUS_end = st.slider(label='SALUS end year', key='Year end',value=int(1982),\
                min_value=1850, max_value=2022, step=1)
            #Checking if end year is later than start year 
            if (SALUS_end <= SALUS_start):
                st.markdown('## ERROR:Start year cannot be later than end year')
            #Total number of run years for salus
            nyrs = SALUS_end - SALUS_start + 1
            #Start DOY 
            start_doy = 1
            
            wx_id = st.text_input('### Weather Station ID','39.7333N_89.9333W')
            soilID_list = st_tags(
            label='### Enter Soil IDs:',
            text='Press enter to add more',
            value=[199353, 199290, 199312],
            suggestions=[],
            maxtags=20,
            key="soilid")
            
            
                
            N_rate_list = st_tags(
            label='### Enter N fert rate (Kg/ha):',
            text='Press enter to add more',
            value=[0., 150., 200.],
            suggestions=[],
            maxtags=20,
            key="aljnf")

            N_init_list = st_tags(
            label='### Enter Initail N for each soil type (Kg/ha):',
            text='Press enter to add more',
            value=[0.,0.,0.],
            suggestions=[],
            maxtags=20,
            key="N init")
            
            N_init_list = convert_float(N_init_list )
            N_rate_list = convert_int(N_rate_list )
            

            CropDetails=st.checkbox('Crop Information')
            Planting=st.checkbox('Planting')
            Irrigation=st.checkbox('Irrigation')
            split_fertapp=st.checkbox('Split N fert')
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
                plant_depth = st.number_input('Planting depth in cm',30)  # 
                ppop = st.text_input('Planting population in seeds/m2',"8")   # seeds/m2.
                rowspc = st.text_input('Row spacing in cm',"76")   # cm
                pdoy = st.text_input('Planting DOY',"121")   # DOY 121 = May 1  
            else:
                yearp = ''
                plant_depth = '' # 
                ppop = ''
                rowspc = ''
                pdoy = ''
            
            #get_data().append({"crop_name":crop_name, "crop_mode ": crop_mode, "speciesID":speciesID,\
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
                label='Enter split fraction of total N applied:',
                text='Press enter to add more',
                value=["0.33"],
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
        
            if (len(soilID_list )!=len(N_init_list)):
                st.markdown('## ERROR: Soil initial N value are not same as number of soil type')
                Error_enter=True
                #st.write("### Results:")
                #st.write(type(N_rate_list))
                #N_rate_list.append(Nrate)
            else:
                st.write("Start year SALUS:",SALUS_start)
                st.write("End year SALUS:",SALUS_end)
                st.write("Final list of soils",soilID_list)
                st.write("Final list N fert rate (Kg/ha)",N_rate_list)
            if Tillage:
                if any(t!=Num_till_event for t in Tillgae_comp_list ):
                    st.markdown('## ERROR: Number of tillage entries should be same as the number of tillage events')
                    Error_enter=True
                    
                else:
                    st.write("Total number of tillage events",Num_till_event)
                    st.write("Tillage events DOY",tdoy_list)
                    st.write("Tillage types",tillage_tool_list)
                    st.write("Tillage depths (cm)",tillage_depth_list)
            
            if split_fertapp:
                if any(t!=Num_fert_event for t in fertilizer_comp_list ):
                    st.markdown('## ERROR: Number of fetilizer entries should be same as the number of application events')
                    Error_enter=True
                    
                else:
                    st.write("Total number of fertilizer events",Num_fert_event)
                    st.write("Fertilizer events DOY",fdoy_list)
                    st.write("Fertilizer types",fert_type_list)
                    st.write("Fertilizer codes",fert_code_list)
                    st.write("Fertilizer depths (cm)",fert_depth_list)
                    st.write("Fertilizer split fractions (0-1)",fert_amt_frac_list)

    row1,row2=st.columns([1,1])
    with row1:
        M_data=st.checkbox('Management details')
    with row2:
        E_data=st.checkbox('Experiment details')          
    
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
    if show_data:
        if E_data:
            st.write("## Experimental dataset")
            st.write(pd.DataFrame(exp_data()))
        if M_data:  
            st.write("## Management dataset")
            st.write(pd.DataFrame(get_data()))
    if remove_last:
        get_data().pop() 
        st.write("## Management dataset")
        st.write(pd.DataFrame(get_data())) 
    if (reset_data):
        if M_data:
            st.write("## Management dataset")
            get_data().clear() 
            st.write(pd.DataFrame(get_data()))
        if E_data:  
            exp_data().clear() 
            st.write("## Experimental dataset")
            st.write(pd.DataFrame(exp_data()))

    if (add_data):
        if (Error_enter==False):
            if E_data:
            
                exp_data().append({"SALUS_start":SALUS_start,"SALUS_end":SALUS_end, "start_doy":start_doy,\
                "wx_id":wx_id, "soilID_list":soilID_list,"N_rate_list":N_rate_list})

            if M_data: 
                get_data().append({"crop_name":crop_name, "crop_mode": crop_mode, "speciesID":speciesID,\
                   "cultivar": cultivar,"plant_depth":plant_depth,"yearp":yearp,"ppop":ppop ,"rowspc":rowspc,\
                    "pdoy":pdoy,"irrFlag":irrFlag,"irr_method":irr_method,"dsoil":dsoil,"thetaC":thetaC,"endPt":endPt,\
                    "Num_fert_event":Num_fert_event,"fert_amt_frac_list":fert_amt_frac_list,"fdoy_list":fdoy_list,"yearf_list":yearf_list,\
                     "fert_type_list":fert_type_list,"fert_depth_list":fert_depth_list,"fert_code_list":fert_code_list,"Nfert":N_rate_list,\
                    "Num_till_event":Num_till_event,"tdoy_list":tdoy_list,"yeart_list":yeart_list,"tillage_tool_list":tillage_tool_list,"tillage_depth_list":tillage_depth_list,\
                       "yearh":yearh, "hdoy":hdoy,"hcom":hcom,"hpc":hpc,"knock_down":knock_down,"hbpc":hbpc})
        else:
            st.write('First check all the error msg for the data input')
        #Main_datframe=pd.DataFrame(get_data())
        st.write("## Experimental dataset")
        st.write(pd.DataFrame(exp_data()))
        st.write("## Management dataset")
        st.write(pd.DataFrame(get_data()))
        


            
            #     st.write("N fertilizer rates done")
         # Read in the soil file data.

    
    
    
    #load = st.checkbox('Load soil data')
    #if load:
    
    # Open the xdb file for writing.
    if st.button('Create file'):
        Main_datframe=pd.DataFrame(get_data())
        Exp_dataframe=pd.DataFrame(exp_data())
        st.write(len(Main_datframe.index))
        st.write(len(Exp_dataframe.index))
        if (not Main_datframe.empty and not Exp_dataframe.empty):
        #
            
            #root,tree=read_soil(sdb_file)
            st.write("Start writing")
            create_xdb(
            xdb_file,
            sdb_file,
            wdb_file,
            cdb_file,
            str(wx_id),
            cultivar,
            soilID_list,
            N_rate_list,
            SALUS_start,
            SALUS_end,
            Main_datframe,
            start_doy=start_doy,
            Irrigation=Irrigation,
            Planting=Planting,
            split_fertapp=split_fertapp,
            Tillage=Tillage,
            Harvest=Harvest)
            st.write("Done writing")
        else:
            st.write("##Opps! File will not be created, Please check both the data boxes and add data to both dataframes")


        
        
    


            
        
        


