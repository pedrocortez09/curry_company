# Libraries
import re
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import datetime


import plotly.express as px
import folium

from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', layout='wide')

# --------- FUNÇÕES ------------


def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe

        Tipos de limpeza:
        1. Retirar os valores NaN das colunas
        2. Converter os tipos dos dados das colunas
        3. Remoção dos espaços vazios
        4. Formatação da coluna de data
        5. Limpeza da coluna 'Time_taken(min)'
    """
    # Change Data Types
    # 1. Convertendo a coluna 'Age' de texto para número
    df1 = df1.loc[df1['Delivery_person_Age'] != 'NaN ', :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # 2. Convertendo a coluna ratings de texto para número decimal
    df1 = df1.loc[df1['Delivery_person_Ratings'] != 'NaN ', :].copy()
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(
        float)

    # 3. Convertendo a coluna order date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # 4. Convertendo Multiple Deliveries de texto para numero
    df1 = df1.loc[df1['multiple_deliveries'] != 'NaN ', :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # 5. Convertendo Multiple Deliveries de texto para numero
    df1 = df1.loc[df1['Festival'] != 'NaN ', :].copy()

    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN ', :].copy()

    df1 = df1.loc[df1['City'] != 'NaN ', :].copy()

    # 6. Coluna Time Taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(
        lambda x: re.search('[0-9]+', x).group(0))
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    # 7. Removendo os espaços dentro de strings/texto/object
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:,
                                                 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    return df1


def feature_engineering(df1):
    """ Esta função tem a responsabilidade de criar novas colunas:

        As colunas criadas são:
        1. 'distance' - Distancia em quilometros.
        2. 'order_week' - Semana do ano em que o pedido foi realizado.
    """
    col = ['Restaurant_latitude', 'Restaurant_longitude',
           'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:, col].apply(lambda x: haversine(
        (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

    df1['order_week'] = df1['Order_Date'].dt.isocalendar().week
    print('Estou na visão empresa')

    aux = df1[['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    px.bar(aux, x='Order_Date', y='ID')

    return df1

# Gráfico de Barras


def order_metric(df1):
    aux = df1[['ID', 'Order_Date']].groupby(
        'Order_Date').count().reset_index()
    fig = px.bar(aux, x='Order_Date', y='ID')

    return fig

# Gráfico de pizza densidade trânsito


def traffic_order_share(df1):
    aux = df1[['ID', 'Road_traffic_density']].groupby(
        'Road_traffic_density').count().reset_index()
    aux['perc'] = round(aux['ID'] / aux['ID'].sum() * 100, 2)
    fig = px.pie(aux, values='perc', names='Road_traffic_density')

    return fig


# Grafico de bolha
def traffic_order_city(df1):
    aux = df1[['ID', 'City', 'Road_traffic_density']].groupby(
        ['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(aux, x='City', y='Road_traffic_density',
                     size='ID', color='City')

    return fig

# Gráfico de linha pedidos por semana


def order_by_week(df1):
    aux = df1[['ID', 'order_week']].groupby('order_week').count().reset_index()
    fig = px.line(aux, x='order_week', y='ID')

    return fig


def order_share_by_week(df1):
    aux1 = df1[['ID', 'order_week']].groupby(
        'order_week').count().reset_index()
    aux2 = df1[['Delivery_person_ID', 'order_week']].groupby(
        'order_week').nunique().reset_index()
    df_aux = pd.merge(aux1, aux2, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='order_week', y='order_by_deliver')

    return fig


def country_maps(df1):

    cols = ['City', 'Road_traffic_density',
            'Delivery_location_latitude', 'Delivery_location_longitude']
    aux = df1.loc[:, cols].groupby(
        ['City', 'Road_traffic_density']).median().reset_index()
    map = folium.Map()

    for index, location in aux.iterrows():
        folium.Marker([location['Delivery_location_latitude'],
                      location['Delivery_location_longitude']]).add_to(map)
    folium_static(map, width=1024, height=600)

    return None

# ------------------INICIO DA ESTRUTURA LOGICA DO CODIGO------------------------------


# ------- Import Dataset ----------
df = pd.read_csv('dataset/train.csv')

# ------- Transformation Dataset ------------
df1 = clean_code(df)

df2 = feature_engineering(df1)


# =============================
# SIDEBAR
# =============================
st.header('Marketplace - Visão Empresa')

# image_path = '/home/pedro/Documentos/repos/ftc/img/logo.jpg'
image = Image.open('logo.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in town')
st.sidebar.markdown("""___""")

data_slider = st.sidebar.slider('Selecione uma data limite',
                                value=datetime.datetime(2022, 4, 13),
                                min_value=datetime.datetime(2022, 2, 11),
                                max_value=datetime.datetime(2022, 4, 6),
                                format='DD-MM-YYYY')
st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect('Quais as condições de trânsito?',
                                         ['Low', 'Medium', 'High', 'Jam'],
                                         default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""___""")

city_options = st.sidebar.multiselect('Quais tipos de cidades?',
                                      ['Metropolitian', 'Urban', 'Semi-Urban'],
                                      default=['Metropolitian', 'Urban', 'Semi-Urban'])

st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Pedro Cortez')

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Cidade
linhas_selecionadas = df1['City'].isin(city_options)
df1 = df1.loc[linhas_selecionadas, :]

# =============================
# LAYOUT NO STREAMLIT
# =============================

tab1, tab2, tab3 = st.tabs(
    ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:

    with st.container():
        st.markdown('# Orders by day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('# Traffic Order Share ')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('# Traffic Order City ')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)


with tab2:

    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)
