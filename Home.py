import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home")

#image_path = '/home/pedro/Documentos/repos/ftc/img/'
image = Image.open('logo.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in town')
st.sidebar.markdown("""___""")

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar o Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for help
    - Time de Data Science discord
        - @Pedro Cortez
    """
)
