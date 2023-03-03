import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🏡",
    layout="wide")

image_path = "order.png"
image = Image.open(image_path)
st.sidebar.image(image,width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown( """___""")

st.write("# Curry Company Growth Report")

st.markdown(
    """
    ### Welcome to my report!
    The purpose of this report is to provide growth patterns in Cury Company, a delivery company located in India. To such an extent, the report is divided in 3 major frames:
    ### 1. Company View:
        - General tracking metrics;
        - Weekly Growth KPIs;
        - Geolocation Insights;
    ### 2. Deliver View:
        - Monitoring weekly growth indicators of employees;
    ### 3. Restaurant View:
        - Restaurant weekly growth indicators
        
    You can access all these frames by clicking on the arrow in the upper left corner and by selecting the name of frames you would like to see.
    
    ### Contact Me
    Please don't hesitate to reach out if you have any questions or feedback:
    
    ✉️ [View my linkedin](https://www.linkedin.com/in/danielsibraga/?locale=en_US)
""")