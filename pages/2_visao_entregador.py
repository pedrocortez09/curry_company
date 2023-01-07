# Libraries
import re
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

import plotly.express as px
import folium

from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static


st.set_page_config(page_title='Visão Entregador', layout='wide')

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


def mean_deliver_ratings(df1):
    mean_deliver_ratings = (df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                            .groupby('Delivery_person_ID')
                            .mean()
                            .reset_index()
                            .sort_values('Delivery_person_Ratings', ascending=False))

    return mean_deliver_ratings


def mean_ratings(df1, col):
    mean_weather_ratings = (df1.loc[:, [col, 'Delivery_person_Ratings']].groupby(
        col).agg({'Delivery_person_Ratings': ['mean', 'std']}))
    mean_weather_ratings.columns = ['mean_rating', 'std_rating']
    mean_weather_ratings.reset_index()
    mean_weather_ratings = mean_weather_ratings.sort_values(
        'mean_rating', ascending=False)

    return mean_weather_ratings


def top_delivers(df1, top_asc):
    aux = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(
        ['City', 'Delivery_person_ID']).mean().reset_index().sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
    aux_metropolitian = aux.loc[aux['City'] == 'Metropolitian', :].head(10)
    aux_urban = aux.loc[aux['City'] == 'Urban', :].head(10)
    aux_semi = aux.loc[aux['City'] == 'Semi-Urban', :].head(10)
    faster_deliver = pd.concat([aux_metropolitian, aux_urban, aux_semi],
                               axis=0).reset_index(drop=True)
    return faster_deliver


def calculate_key_numbers(col, operation):
    if operation == 'max':
        result = df1.loc[:, col].max()
    elif operation == 'min':
        result = df1.loc[:, col].min()

    return result

# ------------------INICIO DA ESTRUTURA LOGICA DO CODIGO------------------------------


# ------- Import Dataset ----------
df = pd.read_csv('dataset/train.csv')

# ------- Transformation Dataset ------------
df1 = clean_code(df)

df2 = feature_engineering(df1)

# =============================
# SIDEBAR
# =============================
st.header('Marketplace - Visão Entregadores')

# image_path = '/home/pedro/Documentos/repos/ftc/img/logo.jpg'
image = Image.open('logo.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in town')
st.sidebar.markdown("""___""")

data_slider = st.sidebar.slider('Selecione a data limite',
                                value=pd.datetime(2022, 6, 4),
                                min_value=pd.datetime(2022, 2, 11),
                                max_value=pd.datetime(2022, 6, 4),
                                format='DD-MM-YYYY')
st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect('Quais as condições de trânsito?',
                                         ['Low', 'Medium', 'High', 'Jam'],
                                         default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""___""")


wheater_options = st.sidebar.multiselect('Selecione as condições climaticas',
                                         ['conditions Sunny', 'conditions Fog', 'conditions Cloudy', 'conditions Windy',
                                          'conditions Stormy', 'conditions Sandstorms'],
                                         default=['conditions Sunny', 'conditions Fog', 'conditions Cloudy', 'conditions Windy',
                                                  'conditions Stormy', 'conditions Sandstorms'])

st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Pedro Cortez')

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Clima
linhas_selecionadas = df1['Weatherconditions'].isin(wheater_options)
df1 = df1.loc[linhas_selecionadas, :]


# =============================
# LAYOUT NO STREAMLIT
# =============================

tab1, tab2, tab3 = st.tabs(
    ['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')

        with col1:
            # Maior idade dos entregadores
            maior_idade = calculate_key_numbers(
                col='Delivery_person_Age', operation='max')
            col1.metric('Maior idade', maior_idade)

        with col2:
            # Menor idade dos entregadores
            menor_idade = calculate_key_numbers(
                col='Delivery_person_Age', operation='min')
            col2.metric('Menor idade', menor_idade)

        with col3:
            # Melhor Condição de veiculo
            melhor_condicao = calculate_key_numbers(
                col='Vehicle_condition', operation='max')
            col3.metric('Melhor condição', melhor_condicao)

        with col4:
            # Pior Condição de veiculo
            pior_condicao = calculate_key_numbers(
                col='Vehicle_condition', operation='min')
            col4.metric('Pior condição', pior_condicao)

    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Avaliações médias por entregador')
            mean_deliver_ratings = mean_deliver_ratings(df1)
            st.dataframe(mean_deliver_ratings, use_container_width=False)

        with col2:
            st.markdown('##### Avaliação média por trânsito')
            mean_traffic_ratings = mean_ratings(
                df1, col='Road_traffic_density')
            st.dataframe(mean_traffic_ratings)

            st.markdown('##### Avaliação média por clima')
            mean_weather_ratings = mean_ratings(df1, col='Weatherconditions')
            st.dataframe(mean_weather_ratings)

    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de entrega')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            faster_deliver = top_delivers(df1, top_asc=True)
            st.dataframe(faster_deliver, use_container_width=True)

        with col2:
            st.markdown('##### Top entregadores mais lentos')
            slowest_deliver = top_delivers(df1, top_asc=False)
            st.dataframe(slowest_deliver, use_container_width=True)
