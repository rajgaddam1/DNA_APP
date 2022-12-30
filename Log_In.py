import streamlit as st
import os
import snowflake.connector
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
from snowflake.connector.connection import SnowflakeConnection
from PIL import Image
import altair as alt

######Load color and scale

scale = alt.Scale(
    domain=["Warehouse", "Database", "Role", "User"],
    range=["#e7ba52", "#a7a7a7", "#aec7e8", "#1f77b4"],
)
color = alt.Color("weather:N", scale=scale)

# We create two selections:
# - a brush that is active on the top panel
# - a multi-click that is active on the bottom panel
brush = alt.selection_interval(encodings=["x"])
click = alt.selection_multi(encodings=["color"])

##############Snowflake Credentials

user = os.environ.get('user')
password = os.environ.get('password')
account = os.environ.get('account')

st.set_page_config(
    page_title="Snowflake Client",)

##########Header and Footer
hide_footer_style='''
<style>
reportview-container .main footer (visibility: hidden;)
'''
st.markdown(hide_footer_style, unsafe_allow_html=True)

hide_menu_style= '''
<style>
#MainMenu (visibility: hidden;}
</style>
'''
st.markdown(hide_menu_style, unsafe_allow_html=True)

#html_code = '<div class="markdown-text-container stText" style="width: 698px;"> <footer><p></p></footer><div style="font-size: 12px;">Snowflake Client v 0.1</div> <div style="font-size: 12px;">Infosys Technologies Limited</div></div>'
#with st.sidebar:
    #st.markdown(html_code,unsafe_allow_html=True)

footer="""<style>
a:link , a:visited{
color: blue;
background-color: #f2f4f5;
}
a:hover,  a:active {
color: red;
background-color: #f2f4f5;
}
.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: #f2f4f5;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Snowflake Client v 0.1 <a style='display: block; text-align: center;' href="https://www.infosys.com/" target="_blank">Infosys Technologies Limited</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)


############Check Log in

#try:
    #account_name_fin = st.session_state['account_name']
    #user_name1_fin = st.session_state['user_name1']
    #password1_fin = st.session_state['password1']
    #if user != user_name1_fin and password != password1_fin and account != account_name_fin:
        #st.warning("You must log-in to see the content of this sensitive page! Head over to the log-in page.")
        #st.stop()  # App won't run anything after this line
#except:
     #st.warning("Please Login")
     #st.stop()
    
        
##To manage bug in sreamlit(Intialize button click)
if 'key' not in st.session_state:
    st.session_state.key = False

def callback():
    st.session_state.key = True

##############Sidebar Logo
with st.sidebar:
    image = Image.open('Infosys_logo.JPG')
    new_image = image.resize((60, 40))
    st.image(new_image)


###Function to convert data to csv

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')



###Snow connection

con = snowflake.connector.connect(
                    user = user,
                    password = password,
                    account='MD93775.ap-southeast-1')

####Snowflake connection
def get_connector() -> SnowflakeConnection:
    """Create a connector to SnowFlake using credentials filled in Streamlit secrets"""
    con = snowflake.connector.connect(
    user = user,
    password = password,
    account = account,
    warehouse='DNAHACK')
    return con

snowflake_connector = get_connector()

######Snowflake connection for SQL Window and Function

def get_connector_sqlwindow(role_sql, ware_sql) -> SnowflakeConnection:
    """Create a connector to SnowFlake using credentials filled in Streamlit secrets"""
    con = snowflake.connector.connect(
    user = user,
    password = password,
    account = account,
    warehouse =ware_sql,
    role = role_sql)
    return con

def con_window(ware_sql,role_sql):
    con_fun = snowflake.connector.connect(
                    user = user,
                    password = password,
                    account = account,
                    warehouse =ware_sql,
                    role = role_sql)
    return con_fun

#####Show warehouses
def get_wareshouse(_connector) -> pd.DataFrame:
    return pd.read_sql("SHOW WAREHOUSES;", _connector)

wareshouse = get_wareshouse(snowflake_connector)

list_ware = wareshouse['name'].to_list()
list_up = ['-------------------', 'Create a Warehouse']
list_ware_up = list_up + list_ware

##Snowflake Waarehouse dataframe to csv

ware_csv = convert_df(wareshouse)

#################Function to create Warehouse

def create_ware(con):
    ware_name = st.text_input('Enter Warehouse Name')
    ware_size = st.select_slider('Select size', ['XSMALL', 'SMALL', 'MEDIUM', 'LARGE', 'XLARGE', 'XXLARGE', 'XXXLARGE', 'X4LARGE', 'X5LARGE', 'X6LARGE'])
    sql_cmd = 'CREATE OR REPLACE WAREHOUSE  ' + str(ware_name) + ' ' +'WAREHOUSE_SIZE = '+ str(ware_size) +';'
    if st.button('Create Warehouse'):
        try:
            cur = con.cursor()
            cur.execute(sql_cmd)
            st.success(str(ware_name) + ' Warehouse has been created')
        except Exception as e:
            print(e)
            st.error(e)
            st.write('An error has occured please check logs')
        finally:
            cur.close()
        con.close()
        
#Function to Drop Warehouse
def drop_ware(con, ware_name_del):
    #ware_name_del = st.radio("Select Warehouse to Drop",list_ware)
    sql_cmd = 'DROP WAREHOUSE IF EXISTS ' + str(ware_name_del) + ';'

    try:
        cur = con.cursor()
        cur.execute(sql_cmd)
        st.success(str(ware_name_del) + ' Warehouse has been dropped')
    except Exception as e:
        print(e)
        #st.exception(e)
        st.error(e)
        st.write('An error has occured please check logs')
    finally:
        cur.close()
    con.close()




#################Function to create Databsase
def create_data(con):
    database_name = st.text_input('Enter Database Name')
    database_type = st.radio('Select Database Type', ['PERMANENT', 'TRANSIENT'])
    if database_type == 'PERMANENT':
        sql_cmd = 'CREATE OR REPLACE DATABASE  ' + str(database_name) + ';'
    else:
        sql_cmd = 'CREATE OR REPLACE TRANSIENT DATABASE  ' + str(database_name) + ';'
        
    if st.button('Create Database'):
        try:
            cur = con.cursor()
            cur.execute(sql_cmd)
            st.success(str(database_name) + ' Database has been created')
        except Exception as e:
            print(e)
            st.error(e)
            #st.exception(e)
            st.write('An error has occured please check logs')
        finally:
            cur.close()
        con.close()
##############################
def clone_data(con):
    database_name1 = st.text_input('Enter Database Name')
    source_name = st.text_input('Enter Source Database Name')
    sql_cmd = 'CREATE OR REPLACE DATABASE ' + str(database_name1) + ' CLONE '+ str(source_name)  +';'
    if st.button('Done'):
        try:
            cur = con.cursor()
            cur.execute(sql_cmd)
            st.success(str(database_name1) + ' Database has been Cloned')
        except Exception as e:
            print(e)
            st.error(e)
            #st.exception(e)
            st.write('An error has occured please check logs')
        finally:
            cur.close()
        con.close()


       
#####Function to create Schema
def create_schema(con, dbname):
    schema_name = st.text_input('Enter Schema Name')
    schema_type = st.radio('Select Schema Type', ['PERMANENT', 'TRANSIENT'])
    if schema_type == 'PERMANENT':
        sql_cmd3 = 'CREATE OR REPLACE SCHEMA ' + str(dbname) + '.'  +str(schema_name) + ';'
    else:
        sql_cmd3 = 'CREATE OR REPLACE TRANSIENT SCHEMA '+ str(dbname) + '.'  +str(schema_name) + ';'
        
    if st.button('Create Schema'):
        try:
            cur = con.cursor()
            cur.execute(sql_cmd3)
            st.success(str(schema_name) + ' Schema has been created')
        except Exception as e:
            print(e)
            st.error(e)
            #st.exception(e)
            st.write('An error has occured please check logs')
        finally:
            cur.close()
        con.close()
        
#####Create Function        
def create_function(con, dbname):
    sql_query1 = st.text_area('Enter SQL', height= 250)
    if st.button('Create '):
        try:
            cur = con.cursor()
            cur.execute(sql_query1)
            st.success('Function has been created')
        except Exception as e:
            print(e)
            st.error(e)
            #st.exception(e)
            st.write('Please enter valid inputs')
        finally:
            cur.close()
        con.close()
###########Drop Function
def drop_function(con, fun_name_del):
    #ware_name_del = st.radio("Select Warehouse to Drop",list_ware)
    sql_cmd = 'DROP FUNCTION IF EXISTS ' + str(fun_name_del) + ';'
    try:
        cur = con.cursor()
        cur.execute(sql_cmd)
        st.success(str(fun_name_del) + ' Function has been dropped')
    except Exception as e:
        print(e)
        st.error(e)
        #st.exception(e)
        st.write('An error has occured please check logs')
    finally:
        cur.close()
    con.close()


##########  Function to DROP Schema

def drop_schema(con, dbname, schema_name_del):
    #ware_name_del = st.radio("Select Warehouse to Drop",list_ware)
    sql_cmd = 'DROP SCHEMA IF EXISTS ' + str(dbname)+ '.'  + str(schema_name_del) + ';'
    try:
        cur = con.cursor()
        cur.execute(sql_cmd)
        st.success(str(schema_name_del) + ' Schema has been dropped')
    except Exception as e:
        print(e)
        st.error(e)
        #st.exception(e)
        st.write('An error has occured please check logs')
    finally:
        cur.close()
    con.close()
###Function to DROP table
def drop_table(con, dbname, scname, table_name_del):
    #ware_name_del = st.radio("Select Warehouse to Drop",list_ware)
    sql_cmd = 'DROP TABLE IF EXISTS ' + str(dbname)+ '.'  + str(scname) + '.' + str(table_name_del)  +';'
    try:
        cur = con.cursor()
        cur.execute(sql_cmd)
        st.success(str(table_name_del) + ' Table has been dropped')
    except Exception as e:
        print(e)
        st.error(e)
        #st.exception(e)
        st.write('An error has occured please check logs')
    finally:
        cur.close()
    con.close()
    
    
###Function to DROP View
def drop_view(con, dbname, scname, view_name_del):
    #ware_name_del = st.radio("Select Warehouse to Drop",list_ware)
    sql_cmd = 'DROP VIEW IF EXISTS ' + str(dbname)+ '.'  + str(scname) + '.' + str(view_name_del)  +';'
    try:
        cur = con.cursor()
        cur.execute(sql_cmd)
        st.success(str(view_name_del) + ' View has been dropped')
    except Exception as e:
        print(e)
        st.error(e)
        #st.exception(e)
        st.write('An error has occured please check logs')
    finally:
        cur.close()
    con.close()


#################Function to DROP Databsase       
def drop_database(con, database_name_del):
    #ware_name_del = st.radio("Select Warehouse to Drop",list_ware)
    sql_cmd = 'DROP DATABASE IF EXISTS ' + str(database_name_del) + ';'

    try:
        cur = con.cursor()
        cur.execute(sql_cmd)
        st.success(str(database_name_del) + ' Database has been dropped')
    except Exception as e:
        print(e)
        st.error(e)
        #st.exception(e)
        st.write('An error has occured please check logs')
    finally:
        cur.close()
    con.close()
    
############################Create Table/View  

def create_table(con,dbname,scname):
    str1 = "create table "+ str(dbname)+ "." + str(scname)+ "." + "<table_name>" + " (<col1_name> <col1_type>);"
    sql_cmd4 = st.text_area('Enter SQL Query', str1, height = 250)
    if st.button('Create'):
        try:
            cur = con.cursor()
            cur.execute(sql_cmd4)
            st.success('Created')
        except Exception as e:
            print(e)
            st.error(e)
            #st.exception(e)
            st.write('Please Enter Valid Inputs')
        finally:
            cur.close()
        con.close()
        
        
########Alter table
def alter_table(con,dbname,scname,tbname):
    str1 = "alter table "+ str(dbname)+ "." + str(scname) + "." + str(tbname) +" <command>;"
    sql_cmd4 = st.text_area('Enter SQL Query', str1, height = 250)
    if st.button('Submit'):
        try:
            cur = con.cursor()
            cur.execute(sql_cmd4)
            st.success('Done')
        except Exception as e:
            print(e)
            st.error(e)
            #st.exception(e)
            st.write('Please Enter Valid Inputs')
        finally:
            cur.close()
        con.close()

###########Create View
def create_view(con,dbname,scname):
    str2 = "create view "+ str(dbname)+ "." + str(scname)+ "." + "<view_name>" + " as <select_statement>;"
    #sql_cmd5 = st.text_input('Enter SQL Query', 'create view <view_name> as <select_statement>;')
    sql_cmd5 = st.text_area('Enter SQL Query', str2, height = 250)
    if st.button('Create'):
        try:
            cur = con.cursor()
            cur.execute(sql_cmd5)
            st.success('Created')
        except Exception as e:
            print(e)
            st.error(e)
            #st.exception(e)
            st.write('Please Enter Valid Inputs')
        finally:
            cur.close()
        con.close()

#####Alter View
def alter_view(con,dbname,scname,vname):
    str2 = "alter view "+ str(dbname)+ "." + str(scname) + "." + str(vname) +" <command>;"
    #sql_cmd5 = st.text_input('Enter SQL Query', 'create view <view_name> as <select_statement>;') 
    sql_cmd5 = st.text_area('Enter SQL Query', str2, height = 250)
    if st.button('Submit'):
        try:
            cur = con.cursor()
            cur.execute(sql_cmd5)
            st.success('Done')
        except Exception as e:
            print(e)
            st.error(e)
            #st.exception(e)
            st.write('Please Enter Valid Inputs')
        finally:
            cur.close()
        con.close()


################ SIDEBAR_1(WAREHOUSE)###########################
with st.sidebar:
    sel_ware = st.selectbox("**Warehouse**",list_ware_up)

###Action after selecting Warehouse
if sel_ware != 'Create a Warehouse' and sel_ware !=  '-------------------':
    st.subheader('Click the below button to drop '+ str(sel_ware) +' Warehouse')
    if st.button('Drop Warehouse'):
        
        drop_ware(con, sel_ware)

        #pass
    st.subheader('Warehouse Information')

    st.dataframe(wareshouse[['name', 'size']].loc[wareshouse['name'] == sel_ware])
   
    #st.markdown("Click on below button to Download full Information about Warehouse")
    #st.download_button(
    #label = "Download data as CSV",
    #data = ware_csv,
    #file_name = 'Warehouse_info.csv',
    #mime = 'text/csv',)

#### Homepage Create Warehouse
if sel_ware == 'Create a Warehouse':
    st.title('Snowflake Hackathon')
    st.subheader("Click the below button to create a new Warehouse in Snowflake")
    
    if st.button('Create Warehouse', on_click = callback) or st.session_state.key:
        create_ware(con)
    st.subheader("Click the below to Download full Information about Warehouses available")
    st.download_button(
    label = "Download",
    data = ware_csv,
    file_name = 'Warehouse_info.csv',
    mime = 'text/csv',
)
    


####ShowDatabases
def get_databases(_connector) -> pd.DataFrame:
    return pd.read_sql("SHOW DATABASES;", _connector)

databases = get_databases(snowflake_connector)

##Snowflake Waarehouse dataframe to csv

database_csv = convert_df(databases)

##Adding Database type by creating copy of dataframe
databases_up = databases.copy()
databases_up.rename(columns={'options': 'type'}, inplace=True)
#databases_up['type'] = databases_up['type'].replace(np.nan, 'PERMANENT')
databases_up.type.fillna("PERMANENT",inplace = True)


list_data = databases['name'].to_list()
list_up = ['-------------------', 'Create a Database']
list_data_up = list_up + list_data

####SHOW SCHEMAS
def get_schema(_connector, dbname) -> pd.DataFrame:
    sql_cmd2 = 'SHOW SCHEMAS IN DATABASE ' + str(dbname) + ';'
    return pd.read_sql(sql_cmd2, _connector)

####SHOW FUNCTIONS
def get_function(_connector, dbname) -> pd.DataFrame:
    sql_cmd2 = 'SHOW USER FUNCTIONS IN DATABASE ' + str(dbname) + ';'
    return pd.read_sql(sql_cmd2, _connector)


####SHOW TABLES
def get_table(_connector, dbname, scname) -> pd.DataFrame:
    sql_cmd3 = 'SHOW TABLES IN '+ str(dbname) + '.' + str(scname) + ';'
    return pd.read_sql(sql_cmd3, _connector)

####SHOW VIEWS
def get_views(_connector, dbname, scname) -> pd.DataFrame:
    sql_cmd4 = 'SHOW VIEWS IN '+ str(dbname) + '.' + str(scname) + ';'
    return pd.read_sql(sql_cmd4, _connector)


######SHOW ROLES
def get_role(_connector) -> pd.DataFrame:
    return pd.read_sql("SHOW ROLES", _connector)

roles_df = get_role(snowflake_connector)

list_role = roles_df['name'].to_list()
list_up2 = ['-------------------', 'Create a Role']
list_role_up = list_up2 + list_role

role_csv = convert_df(roles_df)

#######SHOW USERS
def get_user(_connector) -> pd.DataFrame:
    return pd.read_sql("SHOW USERS", _connector)

users_df = get_user(snowflake_connector)

list_user = users_df['name'].to_list()
list_up3 = ['-------------------', 'Create a User']
list_user_up = list_up3 + list_user

user_csv = convert_df(users_df)




###################Function to display Query for copy

def show_query(_connector) -> pd.DataFrame:
    #sel_table3 = st.radio("Table Available 1", tables_df_query.name)
    #str1 = str(dbname)+ "." + str(scname) + "." + str(sel_table3)
    #cmd1 = "select get_ddl('table'," + f" '{str1}' " + ",True) As Query"
    str1 = st.text_input('Enter Table Name')
    if st.button('Show Query'):
        cmd1 = "SELECT * FROM TABLE(DB1.PUBLIC.get_object_ddl1('table'," + f" '{str1}' "  +",true));"
    #st.write(cmd1)
    #cmd1 =  "select * from get_ddl('table'," + f" '{str1}' " + ",True) As Query"
    #cmd1 = "select * from get_ddl('table'," + f" '{str1}' " + ",True) As Query"
        return pd.read_sql(cmd1, _connector)
    

######FUNCTION TO DISPLAY OUTPUT AS DATAFRAME
def display_output(role_sql, ware_sql, query_sql) -> pd.DataFrame:
    
    connector1 = get_connector_sqlwindow(role_sql, ware_sql)
    try:
    
        return pd.read_sql(query_sql, connector1)
    
    except:
        st.error('Database does not exist or not Authorized')
        

######FUNCTION Creation in Snowflake
def function_create(role_sql, ware_sql, query_sql):
    con = con_window(ware_sql, role_sql)
    if st.button('Create '):
        try:
            cur = con.cursor()
            cur.execute(query_sql)
            st.success('Created')
        except Exception as e:
            print(e)
            st.error(e)
            #st.exception(e)
            st.write('Please Enter Valid Inputs')
        finally:
            cur.close()
        con.close()




#############SHOW table Query
def show_table_query(_connector, dbname, scname, tbname) -> pd.DataFrame:
    str1 = str(dbname) + '.' + str(scname) + '.' + str(tbname)
    cmd1 = "SELECT * FROM TABLE(DB1.PUBLIC.get_object_ddl1('table'," + f" '{str1}' "  +",true));"
    return pd.read_sql(cmd1, _connector)

############SHOW VIEW QUERY
def show_view_query(_connector, dbname, scname, vname) -> pd.DataFrame:
    str1 = str(dbname) + '.' + str(scname) + '.' + str(vname)
    cmd1 = "SELECT * FROM TABLE(DB1.PUBLIC.get_object_ddl1('view'," + f" '{str1}' "  +",true));"
    return pd.read_sql(cmd1, _connector)



########Publish Report 1
def get_report1(_connector) -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM TABLE(DB1.PUBLIC.GET_PUBLISH_REPORT(-1));", _connector)

def get_report2(_connector) -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM TABLE(DB1.PUBLIC.GET_PUBLISH_REPORT(-7));", _connector)

def get_report3(_connector) -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM TABLE(DB1.PUBLIC.GET_PUBLISH_REPORT(-14));", _connector)



##### Function to create Role CREATE ROLE
def create_role(con):
    role_name = st.text_input('Enter Role Name')
    sql_cmd5 = 'CREATE OR REPLACE ROLE  ' + str(role_name) + ';'
    if st.button('Create Role'):
        try:
            cur = con.cursor()
            cur.execute(sql_cmd5)
            st.success(str(role_name) + ' Role has been created')
        except Exception as e:
            print(e)
            #st.exception(e)
            st.error(e)
            st.write('An error has occured please check logs')
        finally:
            cur.close()
        con.close()

###Function to DROP ROLE
def drop_role(con, sel_role):
    #role_name = st.text_input('Enter Role Name')
    sql_cmd5 = 'DROP ROLE ' + str(sel_role) + ';'
    try:
        cur = con.cursor()
        cur.execute(sql_cmd5)
        st.success(str(sel_role) + ' Role has been dropped')
    except Exception as e:
        print(e)
        #st.exception(e)
        st.error(e)
        st.write('An error has occured please check logs')
    finally:
        cur.close()
    con.close()

###### Function to create Role CREATE ROLE
def create_user(con):
    role_name = st.text_input('Enter User Name')
    #role_email = st.text_input('Enter Email Address')
    sql_cmd6 = "CREATE OR REPLACE USER " + str(role_name) + " PASSWORD = 'welcome' default_role = PUBLIC must_change_password = true" + ';'
    if st.button('Create User'):
        try:
            cur = con.cursor()
            cur.execute(sql_cmd6)
            st.success('User has been created. Plese note the default password is welcome and user must change password on first time login')
        except Exception as e:
            print(e)
            #st.exception(e)
            st.error(e)
            st.write('An error has occured please check logs')
        finally:
            cur.close()
        con.close()
###Function to DROP USER
def drop_user(con, sel_user):
    #role_name = st.text_input('Enter Role Name')
    sql_cmd5 = 'DROP USER ' + str(sel_user) + ';'
    try:
        cur = con.cursor()
        cur.execute(sql_cmd5)
        st.success(str(sel_user) + ' User has been dropped')
    except Exception as e:
        print(e)
        #st.exception(e)
        st.error(e)
        st.write('An error has occured please check logs')
    finally:
        cur.close()
    con.close()


#############SIDEBAR_2(DATABASES)
with st.sidebar:
    global sel_data
    sel_data = st.selectbox("**Databases**", list_data_up)
    
###Create Databse Page
if sel_data == 'Create a Database':
    st.subheader("Click the below button to create a new Database in Snowflake")
    
    if st.button('Create Database', on_click = callback) or st.session_state.key:
        create_data(con)
    
    st.subheader('Click the below checkbox to Clone Existing Database')
    agree1 = st.checkbox('Clone Database')
    if agree1:
        clone_data(con)
    st.subheader("Click the below button to download full information about Databases available")
    st.download_button(
    label = "Download",
    data = database_csv,
    file_name = 'Database_info.csv',
    mime = 'text/csv',)
    
    #st.subheader("👇 Do you want to Copy Query from existing objects")
    #agree3 = st.checkbox('Copy query from existing Table')
    #if agree3:
        #query_df = show_query(snowflake_connector)
        #st.dataframe(query_df)


###Action after selecting Database    
if sel_data != 'Create a Database' and sel_data !=  '-------------------':
    global sel_schema
    #global table_df
    st.subheader('Click the below button to drop '+ str(sel_data) +' Database')
    if st.button('Drop Database'):
        
        drop_database(con, sel_data)
        #pass
    #st.subheader('👇 Do you want to Clone Existing Database? 🗑️')
    #if st.button('Clone Databse'):
        #clone_data(con,sel_data)
    
    st.subheader('Database Information')

    st.dataframe(databases_up[['name', 'type']].loc[databases_up['name'] == sel_data])
    
    #st.markdown("Click on below button to Download full Information about Database")
    #st.download_button(label = "Download data as CSV",data = database_csv,file_name = 'Database_info.csv',mime = 'text/csv',)
    schemas_df = get_schema(snowflake_connector, sel_data)
    sc_list_data = schemas_df['name'].to_list()
    sc_list_up = ['-------------------', 'Create a Schema']
    sc_list_data_up = sc_list_up + sc_list_data
    
    ########### Schema Sidebar#########
    
    with st.sidebar:
        global sel_schema
        sel_schema = st.selectbox("**Schemas**", sc_list_data_up)
        ################## Select Create Schema
    if sel_schema == 'Create a Schema':
            st.subheader("Click the below button to create a new Schema in Snowflake")
            if st.button('Create Schema', on_click = callback) or st.session_state.key:
                create_schema(con, sel_data)
   
##################Table sidebar

    if sel_schema != 'Create a Schema' and sel_schema != '-------------------':
        st.subheader('Click the below button to drop '+ str(sel_schema) +' Schema')
        if st.button('Drop Schema'):
            drop_schema(con, sel_data, sel_schema)
        
        tables_df = get_table(snowflake_connector, sel_data, sel_schema)
        list_table = tables_df['name'].to_list()
        list_up1 = ['-------------------', 'Create a Table']
        list_table_up = list_up1 + list_table
    
        with st.sidebar:
            global sel_table
            sel_table = st.selectbox("**Tables**", list_table_up)
        #### Select Create Table ####
        if sel_table == 'Create a Table':
            st.subheader("Click the below button to create a new Table in Snowflake")
            if st.button('Create Table', on_click = callback) or st.session_state.key:
                create_table(con, sel_data, sel_schema) 
        if sel_table != 'Create a Table' and sel_table != '-------------------':
            
            st.subheader('Click the below button to Drop '+ str(sel_table) +' Table')
            if st.button('Drop Table'):
                drop_table(con, sel_data, sel_schema,sel_table)
            st.subheader("Click the below Checkbox to Copy Query")
            agree3 = st.checkbox('Copy query of Table')
            if agree3:
                table_query_df = show_table_query(snowflake_connector, sel_data, sel_schema, sel_table)
                st.dataframe(table_query_df)
            st.subheader('Click the below button Alter '+ str(sel_table) +' Table')
            if st.button('Alter Table', on_click = callback) or st.session_state.key:
                alter_table(con, sel_data, sel_schema,sel_table)
                
                
            
##################VIEWS sidebar   
        view_df = get_views(snowflake_connector, sel_data, sel_schema)
        list_view = view_df['name'].to_list()
        list_up2 = ['-------------------', 'Create a View']
        list_view_up = list_up2 + list_view

        with st.sidebar:
            global sel_view
            sel_view = st.selectbox("**Views**", list_view_up)
            
                #### Select Create View #######
                
        if sel_view == 'Create a View':
            st.subheader("Click the below button to create a new View in Snowflake")
            if st.button('Create View', on_click = callback) or st.session_state.key:
                create_view(con, sel_data, sel_schema)
        if sel_view != 'Create a View' and sel_view != '-------------------' :
            
            st.subheader('Click the below button to drop '+ str(sel_view) +' View?')
            if st.button('Drop View'):
                drop_view(con, sel_data, sel_schema,sel_view)            
            
            st.subheader("Click the Checkvox to Copy Query?")
            agree4 = st.checkbox('Copy query of View')
            if agree4:
                view_query_df = show_view_query(snowflake_connector, sel_data, sel_schema, sel_view)
                st.dataframe(view_query_df)
            st.subheader('Click the below button to Alter '+ str(sel_view) +' View?')
            if st.button('Alter View', on_click = callback) or st.session_state.key:
                alter_view(con, sel_data, sel_schema,sel_view)



###############SIDEBAR_3(Functions)

if sel_data != 'Create a Database' and sel_data !=  '-------------------':
    function_df = get_function(snowflake_connector, sel_data)
    fn_list_data = function_df['name'].to_list()
    fn_list_up = ['-------------------', 'Create a Function']
    fn_list_data_up = fn_list_up + fn_list_data
    
    ########### Functions Sidebar#########
    
    with st.sidebar:
        global sel_fun
        sel_fun = st.selectbox("**Functions**", fn_list_data_up)
        ################## Select Create Function
    if sel_fun == 'Create a Function':
            st.subheader("Click the below button to create a new Function in Snowflake")
            if st.button('Create Function', on_click = callback) or st.session_state.key:
                create_function(con, sel_data)
    if sel_fun != 'Create a Function' and sel_fun != '-------------------':
        st.subheader('Click the below button to drop '+ str(sel_fun) +' Function?')
        if st.button('Drop Function'):
            drop_function(con, sel_fun)



#############SIDEBAR_4(Roles)
with st.sidebar:
    global sel_role
    sel_role = st.selectbox("**Role**", list_role_up)
    
if sel_role == 'Create a Role':
    
    st.subheader("Click the below button to create a new Role in Snowflake")
    if st.button('Create Role', on_click = callback) or st.session_state.key:
        create_role(con)
        
    st.subheader("Click the below button to download full information about Roles available")
    st.download_button(
    label = "Download",
    data = role_csv,
    file_name = 'Roles_info.csv',
    mime = 'text/csv',)

if sel_role != 'Create a Role' and sel_role != '-------------------':
    st.subheader('Click the below button to drop '+ str(sel_role) +' Role')
    if st.button('Drop Role'):
        drop_role(con, sel_role)
        
    st.subheader('Role Information')

    st.dataframe(roles_df[['name', 'comment']].loc[roles_df['name'] == sel_role])
    

#######SIDEBAR_5(USERS)
with st.sidebar:
    global sel_user
    sel_user = st.selectbox("**User**", list_user_up)
    
if sel_user == 'Create a User':
    
    st.subheader("Click the below button to create a new User in Snowflake")
    if st.button('Create User', on_click = callback) or st.session_state.key:
        create_user(con)
        
    st.subheader("Click the below button to download full information about Users available")
    st.download_button(
    label = "Download",
    data = user_csv,
    file_name = 'User_info.csv',
    mime = 'text/csv',)

if sel_user != 'Create a User' and sel_user != '-------------------' :
    
    st.subheader('Click the below button to drop '+ str(sel_user) + 'User')
    if st.button('Drop User'):
        drop_user(con, sel_user)
        
    st.subheader('User Information')

    st.dataframe(users_df[['name', 'has_password']].loc[users_df['name'] == sel_user])

#######SIDEBAR_6(Report)
with st.sidebar:
    global sel_report
    sel_report = st.selectbox('**Reports**', ['-------------------', 'Get Publish Report'])

if sel_report == 'Get Publish Report':
    st.subheader('Publish Report')
    sel_days = st.radio("Get Objects Created or Modified", ['None','Last Day', 'Last 7 Days', 'Last 14 days'])
    if sel_days == 'Last Day':
        report1_df = get_report1(snowflake_connector)
        st.dataframe(report1_df)
    if sel_days == 'Last 7 Days':
        report2_df = get_report2(snowflake_connector)
        st.dataframe(report2_df)
    if sel_days == 'Last 14 days':
        report3_df = get_report3(snowflake_connector)
        st.dataframe(report3_df)    
    
########SQL Window
with st.sidebar:
    global sql_window
    sql_window = st.checkbox('**SQL Window** ')
if sql_window:
    #st.set_page_config(layout = "wide",)
    col1, col2, col3 = st.columns([3, 2, 2])
    col1.title('Snowflake Client ')
    #col1, col2 = st.columns([3, 3])
    sel_role2 = col2.selectbox("Role ", roles_df.name)
    sel_ware2 = col3.selectbox("Warehouse ", wareshouse.name)
    #buff, col, buff2 = st.columns([1,3,1])
    #sql_query1 = col.text_input('Enter SQL')
    sql_query1 = st.text_area('Enter SQL', height= 250)
    #sql_final_cmd = 'USE ' + str(sel_role2) + ';' + 'USE ' + str(sel_ware2) + ';' + str(sql_query1)
    if st.button('Submit SQL'):
        display_output_df = display_output(sel_role2, sel_ware2, sql_query1)
        st.dataframe(display_output_df)
        





    
#######HOME PAGE
if sel_ware == '-------------------' and sel_data == '-------------------' and sel_role == '-------------------'  and sel_user == '-------------------' and sel_report == '-------------------' and not sql_window :
    st.title('Snowflake Client')
    sel_role1 = st.selectbox("Role", roles_df.name)
    sel_ware1 = st.selectbox("Warehouse", wareshouse.name)
    #st.subheader("Number of Objects in Snowflake")
    a = [len(list_ware), "Warehouse"]
    b = [len(list_data), "Database"]
    c = [len(list_role), "Role"]
    d = [len(list_user), "User"]


    chart_data = pd.DataFrame([a, b, c, d],columns=["Count", "Object"])
    bar_chart = alt.Chart(chart_data).mark_bar().encode(
        y = 'Count',
        x = 'Object:N',
        color=alt.Color("Object:N", scale=scale),
        )
    #st.altair_chart(bar_chart, theme=None, use_container_width=True)
    #st.bar_chart(chart_data["Object"], x = [len(list_ware), len(list_data), len(list_role), len(list_user)])
    
