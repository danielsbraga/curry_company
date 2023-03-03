# Bibliotecas necessarias
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Deliver View",page_icon="🛵",layout="wide")

# =================================
# Functions
# =================================
def avg_ratings_per_deliver(df1):
    df_avg_ratings_per_deliver = (df1.loc[:,["Delivery_person_ID","Delivery_person_Ratings"]]
                                  .groupby(["Delivery_person_ID"])
                                  .mean()
                                  .reset_index()
                                 ).rename_axis('Rank')
    df_avg_ratings_per_deliver['Delivery_person_Ratings'] = df_avg_ratings_per_deliver['Delivery_person_Ratings'].round(2)
    df_avg_ratings_per_deliver.columns = ['Person ID','Average Rating']
    return df_avg_ratings_per_deliver

def avg_ratings_per_traffic(df1):
    df_avg_ratings_per_traffic = ( df1.loc[:,["Road_traffic_density","Delivery_person_Ratings"]]
                                  .groupby(["Road_traffic_density"])
                                  .agg({'Delivery_person_Ratings': ['mean','std']})
                                 ).rename_axis('Road Traffic Density')
    # OBS:formato como esta fica com nomes ruins para as colunas
    df_avg_ratings_per_traffic.columns = ['raitng mean','raitng std']
    df_avg_ratings_per_traffic[['raitng mean','raitng std']] = df_avg_ratings_per_traffic[['raitng mean','raitng std']].round(2)
    
    return df_avg_ratings_per_traffic
    
def avg_ratings_per_weather(df1):
    # removing the word 'conditions' from dataframe
    df2 = df1.copy()
    df2["Weatherconditions"] = df2["Weatherconditions"].apply(lambda x: x.split('conditions')[1])
    
    df_avg_ratings_per_weather = ( df2.loc[:,["Weatherconditions","Delivery_person_Ratings"]]
                                  .groupby(["Weatherconditions"])
                                  .agg({'Delivery_person_Ratings': ['mean','std']})
                                 ).rename_axis('Weather Conditions')
    # OBS:formato como esta fica com nomes ruins para as colunas
    df_avg_ratings_per_weather.columns = ['raitng mean','raitng std']
    df_avg_ratings_per_weather[['raitng mean','raitng std']] = df_avg_ratings_per_weather[['raitng mean','raitng std']].round(2)

    return df_avg_ratings_per_weather

def top_best_delivers(df1):
    df2 = (df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
            .groupby(['City','Delivery_person_ID'])
            .min()
            .sort_values(['City','Time_taken(min)'])
            .reset_index()
          )
    df_aux01 = df2.loc[df2["City"] == "Metropolitian",:].head(10)
    df_aux02 = df2.loc[df2["City"] == "Urban",:].head(10)
    df_aux03 = df2.loc[df2["City"] == "Semi-Urban",:].head(10)

    df_top_faster = pd.concat([df_aux01,df_aux02,df_aux03]).reset_index(drop=True).rename_axis('Rank')
    df_top_faster.columns = ["City","Person ID","Time taken (min)"]
    return df_top_faster

def top_worst_delivers(df1):
    df2 = (df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
            .groupby(['City','Delivery_person_ID'])
            .max()
            .sort_values(['City','Time_taken(min)'],ascending=False)
            .reset_index()
          )
    df_aux01 = df2.loc[df2["City"] == "Metropolitian",:].head(10)
    df_aux02 = df2.loc[df2["City"] == "Urban",:].head(10)
    df_aux03 = df2.loc[df2["City"] == "Semi-Urban",:].head(10)

    df_top_slower = pd.concat([df_aux01,df_aux02,df_aux03]).reset_index(drop=True).rename_axis('Rank')
    df_top_slower.columns = ["City","Person ID","Time taken (min)"]
    return df_top_slower

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

st.header('Marketplace - Deliver View')

tab1,tab2,tab3 = st.tabs(["Visão Gerencial",' ',' '])

with tab1:
    with st.container():
        st.title('Big Numbers')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # Entregador mais velho
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric(label='Eldest Deliverer',value=str(maior_idade)+" years")
            
        with col2:
            # Entregador mais novo
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric(label='Youngest Deliverer',value=str(menor_idade)+" years")
            
        with col3:
            # Veiculo na pior condição
            pior_veiculo = df1.loc[:,'Vehicle_condition'].max()
            col3.metric(label='Oldest vehicle age',value=str(pior_veiculo)+" years")
            
        with col4:
            # Veiculo na melhor condição
            melhor_veiculo = df1.loc[:,'Vehicle_condition'].min()
            col4.metric(label='Youngest vehicle age',value=str(melhor_veiculo)+" year")
    
    with st.container():
        st.markdown( """___""")
        st.title('Avarege Rating per')
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Deliver')
            st.dataframe(avg_ratings_per_deliver(df1),height=506,width=500)
            
        with col2:
            # Avaliação média por transito
            st.subheader('Type of Traffic')  
            st.dataframe(avg_ratings_per_traffic(df1))
            
            # Avaliação média por clima
            st.subheader('Weather')
            st.dataframe(avg_ratings_per_weather(df1))
            
    with st.container():
        st.markdown( """___""")
        st.title('Delivery Efficiency')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top Fast Employees')
            st.dataframe(top_best_delivers(df1))
            
        with col2:
            st.markdown('##### Top Slow Employees')
            st.dataframe(top_worst_delivers(df1))