#bibliotecas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
#!pip install haversine
from haversine import haversine
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

# from utils import clean_code - seria um arquivo python chamado utils com nossas funções

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide' )

#-------------
# Funções
#-------------
def country_maps( df1 ):
    columns = [
          'City',
          'Road_traffic_density',
          'Delivery_location_latitude',
          'Delivery_location_longitude'
        ]
    columns_groupby = ['City', 'Road_traffic_density']
    data_plot = df1.loc[:, columns].groupby( columns_groupby ).median().reset_index()
   
    # Desenhar o mapa
    map = folium.Map()
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
    folium_static(map, width=1024, height=600)
        
def order_share_by_week (df1):
    df_aux1 = df1.loc[:, [ 'ID' , 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux2 = ( df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                   .groupby( 'week_of_year')
                   .nunique()
                   .reset_index() )
    df_aux = pd.merge( df_aux1 , df_aux2 , how='inner')
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux , x='week_of_year' , y='order_by_delivery')
    return fig

def order_by_week( df1 ):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%u' )
    df_aux = df1.loc[: , ['ID' , 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line( df_aux , x='week_of_year' , y='ID')
    return fig

def traffic_order_city( df1 ):
    df_aux = ( df1.loc[:,['ID','City','Road_traffic_density']]
                  .groupby(['City','Road_traffic_density'])
                  .count()
                  .reset_index() )
    fig = px.scatter( df_aux , x='City' , y='Road_traffic_density' , size='ID' , color='City')
    return fig
    
def traffic_order_share( df1 ):
    #3 Distribuição dos pedidos por tipo de tráfego            
    df_aux = ( df1.loc[: , ['ID' , 'Road_traffic_density']]
                  .groupby('Road_traffic_density')
                  .count()
                  .reset_index() )
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    fig = px.pie(df_aux , values='perc_ID' , names = 'Road_traffic_density')
    return fig

def order_metric( df1 ):
    cols = ['ID' , 'Order_Date']
    df_aux = df1.loc[: , cols].groupby('Order_Date').count().reset_index()
    fig = px.bar( df_aux , x='Order_Date' , y='ID')
    return fig

def clean_code( df1 ):
    """ Esta função tem responsabilidade de limpar o dataframe
        Tipos de limpeza:
        
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espços das variáveis do texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável nunérica )

        Input: Dataframe
        Output: Dataframe    
    """
    # Excluir as linhas vazias
    # ( Conceitos de seleção condicional )
    linhas_selecionadas0 = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas0, :]
    
    # Excluir as linhas com tráfego vazio
    df1 = df1.loc[df1 ['Road_traffic_density'] != "NaN ", :]
    df1 = df1.loc[df1 ['City'] !='NaN ', :]
    df1 = df1.loc[df1 ['Festival'] !='NaN ', :]
    
    # Conversao de texto/categoria/string para numeros inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    
    # Conversao de texto/categoria/strings para numeros decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
    
    # Conversao de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )
    
    # Remove as linhas da culuna multiple_deliveries que tenham o
    # conteudo igual a 'NaN '
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias , :]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
    
    # Comando para remover o texto de números
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    
    # Tirar o min do time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
    return df1
#------------------------------------ Início da estrutura lógica --------------------------
#--------------------------
#import dataset
#--------------------------
df = pd.read_csv('train.csv')

#--------------------------
#Limpando os dados
#--------------------------
df1 = clean_code( df )

#==========================
#Barra Lateral
#==========================
#image_path = 'logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image , width=120 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?', 
    value=pd.datetime(2022, 4, 13), 
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY' )
st.sidebar.markdown("""---""")
traffic_options = st.sidebar.multiselect( 'Quais as condições do trânsito', ['Low', 'Medium', 'High' , 'Jam'], 
                       default=['Low', 'Medium', 'High' , 'Jam'] )
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

#Filtros de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de Trânsito

linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

#===========================
#Layout no Streamlit
#===========================
st.header('Marketplace - Visão Cliente')

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container():
        #Order Metric
        fig = order_metric( df1 )
        st.header ('Orders per day')
        st.plotly_chart ( fig , use_container_width=True )
        
    with st.container():
        col1, col2 = st.columns ( 2 )

        with col1:
            st.header ('Traffic Order Share')
            fig = traffic_order_share( df1 )
            st.plotly_chart ( fig , use_container_width=True )
            
        with col2:
            st.header ('Traffic Order City')
            fig = traffic_order_city ( df1 )
            st.plotly_chart ( fig , use_container_width=True )
            
with tab2:
    with st.container():
        st.markdown( "Weekly Orders" )
        fig = order_by_week( df1 )        
        st.plotly_chart (fig, use_container_width=True)
    
    with st.container():
        st.markdown( "Order Share by Week" )
        fig = order_share_by_week(df1)               
        st.plotly_chart (fig, use_container_width=True)
    
with tab3:
    st.markdown( "Map View" )
    country_maps( df1 )
    
    
