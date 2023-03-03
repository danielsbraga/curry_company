# Bibliotecas necessarias
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Restaurant View",page_icon="👨‍🍳",layout="wide")

# =================================
# Functions
# =================================
def average_distance(df1):
    col =['Restaurant_latitude',
          'Restaurant_longitude',
          'Delivery_location_latitude',
          'Delivery_location_longitude']

    df1['distance'] = (df1.loc[:,col]
                        .apply(lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),
                                                   (x['Delivery_location_latitude'],x['Delivery_location_longitude'])
                                                  ),
                        axis=1)
                      )
    avg_distance = np.round(df1['distance'].mean(),2)
    return avg_distance

def time_efficiency(df1,metric,festival):
    if metric == "avg":
        if festival == "Yes":
            col = ['Festival','Time_taken(min)']
            df_aux = df1.loc[:,col].groupby(['Festival']).mean()
            df_aux = df_aux.reset_index()
            linhas_selecionadas = df_aux['Festival'] == "Yes "
            df_aux = (np.round(df_aux
                                .loc[linhas_selecionadas,'Time_taken(min)']
                               ,2)
                     )
        else:
            col = ['Festival','Time_taken(min)']
            df_aux = df1.loc[:,col].groupby(['Festival']).mean()
            df_aux = df_aux.reset_index()
            linhas_selecionadas = df_aux['Festival'] == "No "
            df_aux = (np.round(df_aux
                                .loc[linhas_selecionadas,'Time_taken(min)']
                               ,2)
                     )
    else:
        if festival == "Yes":
            col = ['Festival','Time_taken(min)']
            df_aux = df1.loc[:,col].groupby(['Festival']).std()
            df_aux = df_aux.reset_index()
            linhas_selecionadas = df_aux['Festival'] == "Yes "
            df_aux = (np.round(df_aux
                                .loc[linhas_selecionadas,'Time_taken(min)']
                               ,2)
                     )
        else:
            col = ['Festival','Time_taken(min)']
            df_aux = df1.loc[:,col].groupby(['Festival']).std()
            df_aux = df_aux.reset_index()
            linhas_selecionadas = df_aux['Festival'] == "No "
            df_aux = (np.round(df_aux
                                .loc[linhas_selecionadas,'Time_taken(min)']
                               ,2)
                     )
    return df_aux

def Time_taken_city(df1):
    col = ["City",'Time_taken(min)']
    df_aux = df1.loc[:,col].groupby("City").agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                         x=df_aux["City"],
                         y=df_aux['avg_time'],
                         error_y=dict(type="data",array=df_aux['std_time'])))
    fig.update_layout(barmode="group")
    return fig

def Type_of_order_city(df1):
    col = ["City",'Type_of_order','Time_taken(min)']
    df_aux = df1.loc[:,col].groupby(["City",'Type_of_order']).agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg','std']
    return df_aux

def Road_traffic_density_city(df1):
    col = ["City",'Road_traffic_density','Time_taken(min)']
    df_aux = (df1.loc[:,col]
              .groupby(["City",'Road_traffic_density'])
              .agg({'Time_taken(min)':['mean','std']})
             )
    df_aux.columns = ['avg time','std time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=["City",'Road_traffic_density'],
                      values="avg time", color="std time",
                      color_continuous_scale="RdBu",
                      color_continuous_midpoint=np.average(df_aux["std time"]))
    return fig

def clean_code(df1):
    '''
    This function is responsible for cleaning the data:
    1. Remove NaN statements
    2. Change column types
    3. Remove spaces
    4. Remove unnecessary strings
    
    Input: DataFrame
    Output: DataFrame
    
    '''
    df1 = df.copy()
    
    # Remove NaN statements 
    selecao = df1['Delivery_person_Age'] != "NaN "
    df1 = df1.loc[selecao, :].copy()
    selecao = df1['Road_traffic_density'] != "NaN "
    df1 = df1.loc[selecao, :].copy()
    selecao = df1['City'] != "NaN "
    df1 = df1.loc[selecao, :].copy()
    selecao = df1['Festival'] != "NaN "
    df1 = df1.loc[selecao, :].copy()

    # Change column types to int
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    selecao2 = df1['multiple_deliveries'] != "NaN "
    df1 = df1.loc[selecao2, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # Change column types to float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # Change column types to Datetime
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # Remove spaces
    df1.loc[:,"ID"] = df1.loc[:,"ID"].str.strip()
    df1.loc[:,"Road_traffic_density"] = df1.loc[:,"Road_traffic_density"].str.strip()
    df1.loc[:,"Type_of_order"] = df1.loc[:,"Type_of_order"].str.strip()
    df1.loc[:,"Type_of_vehicle"] = df1.loc[:,"Type_of_vehicle"].str.strip()
    df1.loc[:,"City"] = df1.loc[:,"City"].str.strip()

    # Remove unnecessary strings
    df1["Time_taken(min)"] = df1["Time_taken(min)"].apply(lambda x: x.split('(min) ')[1])
    df1["Time_taken(min)"] = df1["Time_taken(min)"].astype(int)
    
    return df1

# =================================
# Data Extraction and Cleaning
# =================================

# Import dataset
df = pd.read_csv("dataset/train.csv")

# Cleaning Data
df1 = clean_code(df)

# =================================
# Side Bar
# =================================

image_path = "order.png"
image = Image.open(image_path)
st.sidebar.image(image,width=70)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown( """___""")

st.sidebar.markdown('### Filter your Analysis')
date_slider = st.sidebar.slider(
                "When is it due?",
                value=pd.datetime(2022,4,13),
                min_value=pd.datetime(2022,2,11),
                max_value=pd.datetime(2022,4,6),
                format='DD-MM-YYYY')
st.sidebar.markdown( """___""")

traffic_options = st.sidebar.multiselect(
                    "What are the traffic conditions?",
                    ["Low","Medium","High","Jam"],
                    default=["Low","Medium","High","Jam"])
st.sidebar.markdown( """___""")

cities = st.sidebar.multiselect(
                    "What types of cities?",
                    ["Urban","Semi-Urban","Metropolitian"],
                    default=["Urban","Semi-Urban","Metropolitian"])
st.sidebar.markdown( """___""")

# Filtros de Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]

# Filtros de Road Trafic
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]

# Filtros de Cidades
linhas_selecionadas = df1['City'].isin(cities)
df1 = df1.loc[linhas_selecionadas,:]

# =================================
# Layout in Streamlit
# =================================

st.header('Marketplace - Restaurant View')

tab1,tab2,tab3 = st.tabs(["Visão Gerencial",' ',' '])

with tab1:
    with st.container():
        st.title('Deliver Status')
        
        col1, col2 = st.columns(2, gap='large')
        with col1:
            # Entregadores únicos
            entregador_unico = len(df1['Delivery_person_ID'].unique())
            col1.metric(label='Nº of Deliver Employees',value=entregador_unico)
            
        with col2:
            # Distância Média
            col2.metric(label='Average Distance traveled (Km)',value=average_distance(df1))
            
        st.markdown( """___""")
        
        st.title('Time Efficiency')
        
        # Description of big Numbers
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.markdown('#### During Festivals (min)')
        with col2:
            st.markdown('#### Without Festivals (min)')
            
        # Big Number (avg and std - During Festivals and Without Festivals)
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # Tempo Médio de Entrega c/ Festival
            df_time = time_efficiency(df1,"avg","Yes")
            col1.metric(label='Average Time',value=df_time)
            
        with col2:
            # Tempo Médio de Entrega c/ Festival
            df_time = time_efficiency(df1,"std","Yes")
            col2.metric(label='Standard Deviation',value=df_time)
            
        with col3:
            # Tempo Médio de Entrega s/ Festival
            df_time = time_efficiency(df1,"avg","No")
            col3.metric(label='Average Time',value=df_time)
            
        with col4:
            # Tempo Médio de Entrega s/ Festival
            df_time = time_efficiency(df1,"std","No")
            col4.metric(label='Standard Deviation',value=df_time)
    
    with st.container():
        st.markdown( """___""")
        st.title('Time Efficiency in each City')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(Time_taken_city(df1), use_container_width=True)
                
        with col2:
            st.dataframe(Type_of_order_city(df1))
        
    with st.container():
        st.markdown( """___""")
        st.title('Time taken in each City per Road Traffic Density')
        
        st.plotly_chart(Road_traffic_density_city(df1), use_container_width=True)
        
        with st.expander("How to read the graph"):
            st.write("The size of each pie slice corresponds to the average time taken, while the colors indicate the standard deviation observed among the slices. This allows for a visual representation of both the central tendency and the variability of the data.")