# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 18:39:59 2022

@author: Inaki Carril
"""

#%%
# Paquetes necesarios
# !pip install streamlit_folium
# !pip install branca.colormap
#%%

#%%
# IMPORTANTE, en dos mapas que funcinaban perfectamente (average ratings y number of reviews)
# el mapeo de una variable para mostrar colores dependiendo de estas variables dejaron de funcionar
# y no se la razon. En el notebook de yelp_processing esta el mismo codigo y los mapas se ven bien
# me gustaria saber la razon, si me la puedes comentar cuando subas la correccion lo agradeceria.
#%%

#%%
import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium
import json
import branca.colormap as cmp
from ast import literal_eval
#%%

#%%
with open('data/json_data_yelp.json', 'r', encoding = 'utf-8') as file:
    datos_mapa = json.load(file)
    
datos = pd.read_csv("data/yelp_distritos.csv")
datos.drop(["Unnamed: 0"], inplace = True, axis = 1)
#%%

#%%
avg_rating = datos.groupby(['Distrito']).mean().reset_index()[['Distrito', 'rating']]

colores_1 = cmp.LinearColormap(
    ['red','lightblue', 'steelblue', 'blue'],
    vmin = min(list(avg_rating['rating'])), vmax = max(list(avg_rating['rating'])),
    caption = 'Average rating'
)

def estilo_provincias (feature):

    return{ 'radius': 7,
        'fillColor': colores_1(feature['properties']['yelp_rating']), 
        'color': colores_1(feature['properties']['yelp_rating']), 
        'weight': 1,
        'opacity' : 1,
        'fillOpacity' : 0.8}


m = folium.Map(location=[40.4309, -3.6878], zoom_start = 10)

folium.GeoJson(datos_mapa, style_function = estilo_provincias,
               tooltip = folium.GeoJsonTooltip(fields = ['name', 'yelp_rating'],
                                                    aliases=['District: ', 'Avg Rating: '],
                                                    sticky = True
                    )).add_to(m)

colores_1.add_to(m)
#%%

#%%
mean_reviews = datos.groupby(['Distrito']).mean().reset_index()[['Distrito', 'review_count']]
colores_2 = cmp.LinearColormap(
    ['red','lightblue', 'steelblue', 'blue'],
    vmin = min(list(mean_reviews['review_count'])), vmax = max(list(mean_reviews['review_count'])),
    caption = 'Average number of reviews'
)

def estilo_provincias_2 (feature):

    return{'radius': 7,
        'fillColor': colores_2(feature['properties']['yelp_reviews']), 
        'color': colores_2(feature['properties']['yelp_reviews']), 
        'weight': 1,
        'opacity' : 1,
        'fillOpacity' : 0.8}

m1 = folium.Map(location=[40.4309, -3.6878], zoom_start = 10)

folium.GeoJson(datos_mapa, style_function = estilo_provincias_2,
               tooltip = folium.GeoJsonTooltip(fields = ['name', 'yelp_reviews'],
                                                    aliases=['District: ', 'Avg reviews: '],
                                                    sticky = True
                    )).add_to(m1)

colores_2.add_to(m1)
#%%

#%%
precios = datos.groupby(['Distrito', 'price']).count().reset_index()[['Distrito', 'price', 'id']]
d = datos.groupby(['Distrito', 'price']).count().reset_index(['Distrito']).groupby(['Distrito']).max('id')['id']
precios_modales = pd.merge(d, precios, on = ['Distrito', 'id']).rename(columns = {'id' : 'More frequent price'})

colores_3 = cmp.LinearColormap(
    ['red','lightblue', 'steelblue', 'blue'],
    vmin = min(list(precios_modales['price'])), vmax = max(list(precios_modales['price'])),
    caption = 'Modal Price Category'
)

def estilo_provincias_3 (feature):

    return{ 'radius': 7,
        'fillColor': colores_3(feature['properties']['yelp_price']), 
        'color': colores_3(feature['properties']['yelp_price']), 
        'weight': 1,
        'opacity' : 1,
        'fillOpacity' : 0.8}

m3 = folium.Map(location=[40.4309, -3.6878], zoom_start = 10)

folium.GeoJson(datos_mapa, style_function = estilo_provincias_3,
               tooltip = folium.GeoJsonTooltip(fields = ['name', 'yelp_price'],
                                                    aliases=['District: ', 'Price category: '],
                                                    sticky = True
                    )).add_to(m3)

colores_3.add_to(m3)
#%%

#%%
st.set_page_config(page_title = 'Dashboard')

st.sidebar.header('Yelp restaurant data of Madrid districts.')
st.sidebar.write('Select a section to visualize')

menu = st.sidebar.selectbox(
    "",
    ("Average rating", "Average number of reviews", "Most frequent price category", 
     "Top 5 restaurants by district", "Expensive restaurants"),
)


if menu == 'Average rating':
    st.title("Average rating of restaurant businesses by District.")
    folium_static(m)
    
if menu == 'Average number of reviews':
    st.title("Average number of reviews of restaurant businesses by District.")
    folium_static(m1)
    
if menu == 'Most frequent price category':
    st.title("Most frequent price category by district.")
    st.write("Range goes from 1 to 4, 1 being cheaper and 4 more expensive.")
    folium_static(m3)
    
if menu == 'Top 5 restaurants by district':
    st.title("Top 5 Rated restaurants in selected district.")
    st.header('Select a district')
    seleccion = st.selectbox(
            'Select a district to display the top 5 rated restuarants in it.',
             datos.Distrito.unique())

    top = datos[(datos.Distrito == seleccion)].sort_values(by = ['rating'], axis = 0, ascending = False).head()
    coor1 = list(reversed(literal_eval(top['coordinates'].iloc[[0]].values[0])))
    coor2 = list(reversed(literal_eval(top['coordinates'].iloc[[1]].values[0])))
    coor3 = list(reversed(literal_eval(top['coordinates'].iloc[[2]].values[0])))
    coor4 = list(reversed(literal_eval(top['coordinates'].iloc[[3]].values[0])))
    coor5 = list(reversed(literal_eval(top['coordinates'].iloc[[4]].values[0])))
    
    m4 = folium.Map(location=[40.4309, -3.6878], zoom_start = 10)

    folium.GeoJson(datos_mapa, tooltip = folium.GeoJsonTooltip(fields = ['name'],
                                        aliases=['Distrito: '],
                                        sticky = True
                        )).add_to(m4)
    folium.Marker(location = coor1, 
                  popup = "Name: " + top['name'].iloc[[0]].values[0] + "\n" + "Rating: " + str(top['rating'].iloc[[0]].values[0]), 
                  tooltip = 'Click for additional info').add_to(m4)
    folium.Marker(location = coor2, 
                  popup = "Name: " + top['name'].iloc[[1]].values[0] + "\n" + "Rating: " + str(top['rating'].iloc[[1]].values[0]), 
                  tooltip = 'Click for additional info').add_to(m4)
    folium.Marker(location = coor3, 
                  popup = "Name: " + top['name'].iloc[[2]].values[0] + "\n" + "Rating: " + str(top['rating'].iloc[[2]].values[0]), 
                  tooltip = 'Click for additional info').add_to(m4)
    folium.Marker(location = coor4, 
                  popup = "Name: " + top['name'].iloc[[3]].values[0] + "\n" + "Rating: " + str(top['rating'].iloc[[3]].values[0]), 
                  tooltip = 'Click for additional info').add_to(m4)
    folium.Marker(location = coor5, 
                  popup = "Name: " + top['name'].iloc[[4]].values[0] + "\n" + "Rating: " + str(top['rating'].iloc[[4]].values[0]), 
                  tooltip = 'Click for additional info').add_to(m4)
    folium_static(m4)
    
if menu == "Expensive restaurants":
    st.title("Expensive restaurants by district.")
    st.header('Select a district')
    seleccion = st.selectbox(
            'Select a district to display expensive restaurants in district.',
             datos.Distrito.unique())
    
    m5 = folium.Map(location=[40.4309, -3.6878], zoom_start = 10)
    folium.GeoJson(datos_mapa, tooltip = folium.GeoJsonTooltip(fields = ['name'],
               aliases=['Distrito: '],
                sticky = True
                        )).add_to(m5)
    try:
       expensive = datos[(datos.Distrito == seleccion) & (datos.price == 4)]
       coor = list(reversed(expensive['coordinates'].iloc[[0]].values[0]))
       for i in range(len(expensive)):
            coor = list(reversed(literal_eval(expensive['coordinates'].iloc[[i]].values[0])))
            folium.Marker(location = coor, 
                  popup = "Name: " + expensive['name'].iloc[[i]].values[0] + "\n" + "Rating: " + str(expensive['rating'].iloc[[i]].values[0]), 
                  tooltip = 'Click for additional info').add_to(m5)
       folium_static(m5)
        
    except:
        st.write('There are no restaurants with the highest price level.')
#%%

