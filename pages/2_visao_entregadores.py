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

st.set_page_config( page_title='Visão Entregadores', page_icon='📈', layout='wide' )
#-------------
# Funções
#-------------
def top_delivers ( df1, top_asc ):
    df2 = ( df1.loc[: , ['Delivery_person_ID' , 'City' , 'Time_taken(min)']]
               .groupby( ['City', 'Delivery_person_ID'])
               .mean()
               .sort_values( ['City', 'Time_taken(min)'], ascending=top_asc ).reset_index() )
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)                
    df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index( drop=True )
    return df3

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


#==============
#Barra Lateral
#==============

#image_path = 'logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image , width=120 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual valor?', value=pd.datetime( 2022, 3, 13 ), 
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

st.header('Marketplace - Visão Entregadores')

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.title ('Overall Metrics' )

        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        with col1:
            maior_idade = df1.loc[: , 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade )

        with col2:
            menor_idade = df1.loc[: , 'Delivery_person_Age'].min()
            col2.metric('Menor idade' , menor_idade )
            
        with col3:
            melhor_condicao = df1.loc[: , 'Vehicle_condition'].max()
            col3.metric('Melhor condição' , melhor_condicao )
            
        with col4:
            pior_condicao = df1.loc[: , 'Vehicle_condition'].min()
            col4.metric('Pior condição' , pior_condicao )

    with st.container():
        st.markdown("""---""")
        st.title( 'Avaliações' )
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Avaliação média por Entregador' )
            df_avg_ratings_per_deliver = ( df1.loc[: , ['Delivery_person_ID' , 'Delivery_person_Ratings']]
                                              .groupby( 'Delivery_person_ID')
                                              .mean()
                                              .reset_index() )
            st.dataframe( df_avg_ratings_per_deliver )
        with col2:
            st.markdown( '##### Avaliação média por trânsito' )
            df_avg_rating_traffic = ( df1.loc[: , ['Delivery_person_Ratings' , 'Road_traffic_density']]
                                         .groupby('Road_traffic_density')
                                         .agg( {'Delivery_person_Ratings': ['mean', 'std']} ) )
            df_avg_rating_traffic.columns = ['delivery_mean' , 'delivery_std']
            df_avg_rating_traffic.reset_index()
            st.dataframe( df_avg_rating_traffic )
            
            st.markdown( '##### Avaliação média por clima' )
            df_avg_rating_climate = ( (df1.loc[: , ['Delivery_person_Ratings' , 'Weatherconditions']]
                                          .groupby('Weatherconditions')
                                          .agg( {'Delivery_person_Ratings': ['mean', 'std']} ) ) )
            df_avg_rating_climate.columns = ['delivery_mean' , 'delivery_std']
            df_avg_rating_climate.reset_index()
            st.dataframe( df_avg_rating_climate )

    with st.container():
        st.markdown("""---""")
        st.title( 'Velocidade de entrega' )
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Entregadores mais rápidos' )
            df3 = top_delivers( df1, top_asc=True )                        
            st.dataframe( df3 )
            
        with col2:
            st.markdown( '##### Entregadores mais lentos' )
            df3 = top_delivers( df1, top_asc=False )                        
            st.dataframe( df3 )
            
    