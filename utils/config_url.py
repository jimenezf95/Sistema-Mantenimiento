
# CAMBIAR LA URL DEPENDIENDO DE LA RED 

# Claro-3899 
#BASE_URL = "http://192.168.1.14:8501"

ACA_BOGOTA = "http://192.168.1.17:8501"

# CASA
# BASE_URL = "http://192.168.1.10:8501" 


# App desplegada Online (Render)
#BASE_URL = "https://sistema-mantenimiento-fpt8bvtkyaarj6c6q68jyo.streamlit.app/"

import streamlit as st

BASE_URL = st.secrets.get(
    "BASE_URL",
    ACA_BOGOTA
)