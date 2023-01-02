import streamlit as st
import os
import snowflake.connector
import warnings
warnings.filterwarnings("ignore")
from PIL import Image

user = os.environ.get('user')
password = os.environ.get('password')
account = os.environ.get('account')

st.set_page_config(
    page_title="Snowflake Client",
    initial_sidebar_state="collapsed",)
########Footer
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


####Image 
image = Image.open('Infosys_logo.JPG')
image1 = image.resize((100, 60))
st.image(image1)
st.title("Sign In To Snowflake")



def switch_page(page_name: str):
    from streamlit.runtime.scriptrunner import RerunData, RerunException
    from streamlit.source_util import get_pages

    def standardize_name(name: str) -> str:
        return name.lower().replace("_", " ")

    page_name = standardize_name(page_name)

    pages = get_pages("app.py")  # OR whatever your main page is called

    for page_hash, config in pages.items():
        if standardize_name(config["page_name"]) == page_name:
            raise RerunException(
                RerunData(
                    page_script_hash=page_hash,
                    page_name=page_name,
                )
            )

    page_names = [standardize_name(config["page_name"]) for config in pages.values()]

    raise ValueError(f"Could not find page {page_name}. Must be one of {page_names}")
    
def intro():
    
    #st.header("Sign in to Snowflake ❄️", anchor=None)
    account_name = st.text_input('Account Name',label_visibility="visible")
    user_name1 = st.text_input('User Name',label_visibility="visible")

    password1 = st.text_input('Password',label_visibility="visible",type='password')
        
    #agree = st.button('Submit')
    if st.button("Sign In"):
        
        if 'account_name' not in st.session_state:
            st.session_state['account_name'] = account_name
        
        if 'user_name1' not in st.session_state:
            st.session_state['user_name1'] = user_name1

        if 'password1' not in st.session_state:
            st.session_state['password1'] = password1        
    
        if user == user_name1 and password == password1 and account == account_name:
            
            st.write('Logged in Successfully')
            switch_page("Streamlit")

        else:
            st.write('Invalid Username or Password')

page_names_to_funcs = {
    "Log in to snowflake": intro,
}
demo_name = st.sidebar.selectbox("Choose a action", page_names_to_funcs.keys())

page_names_to_funcs[demo_name]()
       
                
