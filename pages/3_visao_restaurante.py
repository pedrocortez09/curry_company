# Libraries
import re
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import datetime

import plotly.express as px
import folium

from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static


st.set_page_config(page_title='Visão Restaurante', layout='wide')

# ====================== FUNÇÕES ================================


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

    # Criando coluna Week of Year
    df1['order_week'] = df1['Order_Date'].dt.isocalendar().week

    return df1


def avg_time_taken(df1, festival):
    df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                 .groupby('Festival')
                 .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(
        df_aux.loc[df_aux['Festival'] == festival, 'avg_time'], 2)

    return df_aux


def delivery_time_by_city(df1):
    aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby(
        'City').agg({'Time_taken(min)': ['mean', 'std']})
    aux.columns = ['avg_time', 'std_time']
    aux = aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=aux['City'], y=aux['avg_time'], error_y=dict(
        type='data', array=aux['std_time'])))
    fig.update_layout(barmode='group')

    return fig


def sunburst_chart(df1):
    aux = df1.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']].groupby(
        ['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})

    aux.columns = ['avg_time', 'std_time']
    aux = aux.reset_index()

    fig = px.sunburst(aux, path=['City', 'Road_traffic_density'],
                      values='avg_time',
                      color='std_time',
                      color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(aux['std_time']))
    return fig


# ------------------INICIO DA ESTRUTURA LOGICA DO CODIGO------------------------------


# ------- Import Dataset ----------
df = pd.read_csv('dataset/train.csv')

# ------- Transformation Dataset ------------
df1 = clean_code(df)
df2 = feature_engineering(df1)


# =============================
# SIDEBAR
# =============================
st.header('Marketplace - Visão Restaurante')

# image_path = '/home/pedro/Documentos/repos/ftc/img/logo.jpg'
image = Image.open('logo.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in town')
st.sidebar.markdown("""___""")

data_slider = st.sidebar.slider('Selecione uma data limite',
                                value=datetime.datetime(2022, 6, 4),
                                min_value=datetime.datetime(2022, 2, 11),
                                max_value=datetime.datetime(2022, 6, 4),
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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:

    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            deliver_num = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores', deliver_num)

        with col2:
            avg_distance = np.round(df1['distance'].mean(), 2)
            col2.metric('Distancia média', avg_distance)

        with col3:

            df_aux = avg_time_taken(df1, festival='Yes')
            col3.metric('Tempo médio com Festival', df_aux)

        with col4:
            df_aux = avg_time_taken(df1, festival='No')
            col4.metric('Tempo médio sem Festival', df_aux)

    with st.container():
        st.markdown("""___""")

        tab1, tab2 = st.tabs(['Bar Chart', 'Dataframe'])

        with tab1:
            st.title('Tempo médio de entrega por cidade')
            fig = delivery_time_by_city(df1)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.title('Distribuição da distancia')
            aux = df1.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']].groupby(
                ['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
            aux.columns = ['avg_time', 'std_time']
            aux = aux.reset_index()

            st.dataframe(aux, use_container_width=True)

    with st.container():

        st.markdown("""___""")
        st.title('Distribuição do tempo')
        col1, col2 = st.columns(2)

        with col1:

            avg_distance = df1.loc[:, ['City', 'distance']].groupby(
                'City').mean().reset_index()
            fig = go.Figure(data=[go.Pie(labels=avg_distance['City'],
                            values=avg_distance['distance'], pull=[0, 0.1, 0])])
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = sunburst_chart(df1)
            st.plotly_chart(fig, use_container_width=True)
