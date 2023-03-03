# Bibliotecas necessarias
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Company View",page_icon="🏫",layout="wide")

# =================================
# Functions
# =================================
def world_map(df1):
    df_aux = (df1.loc[:,
                ["City","Road_traffic_density",
                "Delivery_location_latitude","Delivery_location_longitude"]]
                .groupby(["City","Road_traffic_density"]).median().reset_index()
             )
    df_aux =(df_aux.loc[(df_aux["City"] != "NaN") & 
            (df_aux["Road_traffic_density"] != "NaN"),:]
            )
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
      folium.Marker([location_info["Delivery_location_latitude"],
                    location_info["Delivery_location_longitude"]]).add_to(map)
    return map

def order_share_by_week(df1):
    df_aux01 = df1.loc[:,["ID","week_of_year"]].groupby("week_of_year").count().reset_index()
    df_aux02 = (df1.loc[:,["Delivery_person_ID","week_of_year"]]
    .groupby("week_of_year").nunique().reset_index()
               )
    df_aux = pd.merge(df_aux01,df_aux02,how="inner")
    df_aux["Order_by_delivery"] = df_aux["ID"] / df_aux["Delivery_person_ID"]
    df_aux = df_aux[["week_of_year","Order_by_delivery"]]

    fig = px.line(df_aux, x="week_of_year", y="Order_by_delivery")
    return fig

def order_by_week(df1):
    df1["week_of_year"] = df1["Order_Date"].dt.strftime("%U")
    df_aux = df1.loc[:,["ID","week_of_year"]].groupby(["week_of_year"]).count().reset_index()
    fig = px.line(df_aux,x="week_of_year",y="ID")
    return fig

def traffic_order_city(df1):
    df_aux = (df1.loc[:,["ID","City","Road_traffic_density"]]
    .groupby(["City","Road_traffic_density"]).count().reset_index()
             )
    df_aux = (df_aux.loc[(df_aux["City"] != "NaN") & 
                        (df_aux["Road_traffic_density"] != "NaN"),:]
             )
    fig = (px.scatter(df_aux,x="City",
                     y="Road_traffic_density",size="ID")
          )
    return fig

def traffic_order_share(df1):
    df_aux = (df1.loc[:,['ID','Road_traffic_density']]
    .groupby(["Road_traffic_density"]).count().reset_index()
             )
    df_aux = df_aux.loc[df_aux["Road_traffic_density"] != "NaN",:]
    df_aux["entregas_perc"] = df_aux["ID"] / df_aux["ID"].sum()
    fig = px.pie(df_aux, values = "entregas_perc", 
           names="Road_traffic_density")
    return fig

def order_by_day(df1):
    col = ["ID","Order_Date"]
    df_aux = df1.loc[:,col].groupby("Order_Date").count().reset_index()
    fig = px.bar(df_aux,x="Order_Date",y="ID")
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

# Filtros de Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]

# Filtros de Road Trafic
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]


# =================================
# Layout in Streamlit
# =================================

st.header('Marketplace - Company View')

tab1,tab2,tab3 = st.tabs(["Visão Gerencial","Visão Tática","Visão Geográfica"])

with tab1:
    #Quantidade de pedidos por Dia
    with st.container():
        st.markdown("# Orders by Day")
        st.markdown("###### Number of orders requested daily by customers")
        fig = order_by_day(df1)
        st.plotly_chart(fig,use_container_width=True)
    
    #Analise de Trafico
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            #grafico de pixa para tipos de transito
            st.header('Traffic Order Share')
            st.markdown("###### Trafficking classes detected in the period")
            fig = traffic_order_share(df1)
            st.plotly_chart(fig,use_container_width=True)
            
        with col2:
            #grafico de bolha para tipos de transito por cidade
            st.header('Traffic Order City')
            st.markdown("###### Trafficking classes detected in each city format")
            fig = traffic_order_city(df1)
            st.plotly_chart(fig,use_container_width=True)
    
with tab2:
    with st.container():
        #pedidos por entregador por semana
        st.markdown("# Order by Week")
        st.markdown("##### All orders accounted for per week")
        fig = order_by_week(df1)
        st.plotly_chart(fig,use_container_width=True)
        
    with st.container():
        #media de pedidos por entregador por semana
        st.markdown("# Order Share by Week")
        st.markdown("##### Average of orders delivered by each deliver per week")
        fig = order_share_by_week(df1)
        st.plotly_chart(fig,use_container_width=True)

with tab3:
    #Mapa de cidades por tipo de grafico
    with st.container():
        st.markdown("# Country Maps")
        st.markdown("##### The central location of each city by type of traffic - See where you can find the best and worst kinds of traffics")
        map = world_map(df1)
        folium_static(map,width=800,height=600)