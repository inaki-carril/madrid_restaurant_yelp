#!/usr/bin/env python
# coding: utf-8

# ### Breve explicacion de los datos y como se obtuvieron.
# Los datos empleados provienen de la API gratuita de Yelp, una API que nos permite obtener informacion de empresas
# en una determinada ubicacion (dirreccion, rango de precios, ratings, numero se resenas). En este caso informacion sobre restaurantes en los distintos distritos de Madrid.
# El primer problema que se ha encontrado es que la API de Yelp devuelve un maximo de 1000 observaciones por llamada, y
# al utilizar como ubicacion la ciudad de madrid, la mayoria de esos mil datos son restaurantes del distrito Centro. Para
# poder obtener mas de 1000 observaciones y obtener datos de todos los distritos se creara una funcion que reciba como 
# parametros las coordenadas del centroide de cada distrito y un radio especifico para cada distrito para tratar de maximizar
# los datos por distrito. Luego con un bucle haremos 21 llamadas a la API con esta funcion, variando los parametros mencionados.
# Evidentemente los distritos no son circulares y el radio se excedera en muchas ocasiones, dando lugar a datos duplicados.
# Tambien, claramente la API no puede recibir como parametro el nombre de un distrito o el poligono para solo devolver datos
# de ese distrito.
# 
# Por la descripcion mencionada anteriormente podemos ver que un claro porblema (y esto se reflejara mas adelante) es que hay distritos (aproximadamente 3-4) que tendran muy pocas observaciones y probabalemente las conclusiones en estos no sean reales. Para mejorar este trabajo se puediese recabar la informacion con la API de Google Places, esto no se hizo porque dicha API es paga.

# In[3]:


# Paquetes adicionales necesarios.
# !pip install shapely
# !pip install folium


# In[4]:


import pandas as pd
import folium
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


# In[5]:


datos = pd.read_csv("C:/Users/inaki/OneDrive/Escritorio/yelp/yelp_data.csv")


# In[6]:


# Importamos los datos de los poligonos de los 21 distritos de la Comunidad de Madrid.
import json

with open('C:/Users/inaki/OneDrive/Escritorio/yelp/madrid-districts.geojson.json', 'r', encoding = 'utf-8') as file:
    datos_mapa = json.load(file)


# In[7]:


datos.head()


# In[8]:


datos.drop(["Unnamed: 0"], inplace = True, axis = 1)


# In[9]:


len(datos)


# In[10]:


# Crear una columna con las coordenadas a partir de la latitud y la longitud.
columna = dict()
for i in range(len(datos)):
    lista = []
    lista.extend([datos["coordinates.longitude"][i], datos["coordinates.latitude"][i]])
    columna[i] = lista

datos["coordinates"] = pd.Series(columna)


# In[11]:


datos.head()


# In[12]:


# Creamos una columna vacia para los Distritos de cada observacion
datos['Distrito'] = np.nan


# In[14]:


# Utilizando los datos GeoJson de poligonos de los distritos vemos a que distrito pertenece cada observacion y agregamos esta
# informacion a la columna distrito del dataframe.
for punto in range(len(datos)):
    for distrito in range(21):
        if Polygon(datos_mapa["features"][distrito]["geometry"]["coordinates"][0][0]).contains(Point(datos['coordinates'][punto])):
            datos["Distrito"][punto] = datos_mapa['features'][distrito]['properties']['name']


# In[15]:


datos.head()


# In[16]:


# Cuatos datos de los totales no son duplicados.
len(datos["id"].unique())


# In[17]:


# Eliminamos los duplicados
datos = datos.drop_duplicates(subset = ["id"])
len(datos)


# In[18]:


# Datos por distrito. Como mencionamos en la introduccion para algunos distritos tenemos muy pocos datos.
datos.Distrito.value_counts()


# In[19]:


# Cambiar la variable de categorias de precios por un rango de numeros.
datos.loc[datos.price == '€', 'price'] = 1
datos.loc[datos.price == '€€', 'price'] = 2
datos.loc[datos.price == '€€€', 'price'] = 3
datos.loc[datos.price == '€€€€', 'price'] = 4


# In[21]:


# Creamos las variables que nos van a permitir agregar al Geojson los datos de yelp a cada distrito que utilizaremos mas
# adelante para las vizualizaciones en el mapa.


# In[22]:


avg_rating = datos.groupby(['Distrito']).mean().reset_index()[['Distrito', 'rating']]
dist_avg_rating = dict(zip(list(avg_rating['Distrito']), list(round(avg_rating['rating'], 1))))


# In[23]:


mean_reviews = datos.groupby(['Distrito']).mean().reset_index()[['Distrito', 'review_count']]
dist_avg_review_count = dict(zip(list(mean_reviews['Distrito']), list(round((mean_reviews['review_count']), 0))))


# In[24]:


precios = datos.groupby(['Distrito', 'price']).count().reset_index()[['Distrito', 'price', 'id']]
d = datos.groupby(['Distrito', 'price']).count().reset_index(['Distrito']).groupby(['Distrito']).max('id')['id']


# In[25]:


precios_modales = pd.merge(d, precios, on = ['Distrito', 'id']).rename(columns = {'id' : 'More frequent price'})
dist_prices = dict(zip(list(precios_modales['Distrito']), list(precios_modales['price'])))


# In[26]:


# Agrgeamos a los datos del GeoJson el rating medio, numero medio de reviews y precio mas frecuente de cada distrito.
for distrito in range(21):
    datos_mapa['features'][distrito]['properties']['yelp_rating'] = dist_avg_rating[datos_mapa['features'][distrito]['properties']['name']]
    datos_mapa['features'][distrito]['properties']['yelp_reviews'] = dist_avg_review_count[datos_mapa['features'][distrito]['properties']['name']]
    datos_mapa['features'][distrito]['properties']['yelp_price'] = dist_prices[datos_mapa['features'][distrito]['properties']['name']]


# In[27]:


datos_mapa


# In[28]:


datos.head()


# In[51]:


# Escribimos un nuevo archivo Json con los nuevos datos.
json_yelp = json.dumps(datos_mapa)
with open('C:/Users/inaki/OneDrive/Escritorio/yelp/json_data_yelp.json', 'w') as outfile:
    outfile.write(json_yelp)


# In[52]:


# Escribimos un archivo csv con el nuevo dataframe de los datos de yelp y sus correspondientes distritos.
datos.to_csv("C:/Users/inaki/OneDrive/Escritorio/yelp/yelp_distritos.csv", sep = ",")


# In[29]:


# A partir de esta celda de codigo se pueden ver algunos mapas de la app de streamlit, la razon por la que los agrego aca es
# porque los mapas me funcionaban perfectammente en la App hasta, pero de la nada ciertas característicaa dejaron de apareccer
# especificamente el degradado de colores mapeado a los ratings promedio por distrito y el numero medio de reviews.
# La razon por la que agrego esto es porque me gustaria saber que ha pasado, puesto que es exactamente el mismo codigo que
# muesto mas abajo el que esta en la app de Streamlit.


# In[35]:


import branca.colormap as cmp

colores = cmp.LinearColormap(
    ['red','lightblue', 'steelblue', 'blue'],
    vmin = min(list(avg_rating['rating'])), vmax = max(list(avg_rating['rating'])),
    caption = 'Average rating'
)

def estilo_provincias (feature):

    return{ 'radius': 7,
        'fillColor': colores(feature['properties']['yelp_rating']), 
        'color': colores(feature['properties']['yelp_rating']), 
        'weight': 1,
        'opacity' : 1,
        'fillOpacity' : 0.8}


# In[36]:


m = folium.Map(location=[40.4309, -3.6878], zoom_start = 10)

folium.GeoJson(datos_mapa, style_function = estilo_provincias,
               tooltip = folium.GeoJsonTooltip(fields = ['name', 'yelp_rating'],
                                                    aliases=['Distrito: ', 'Avg Rating: '],
                                                    style = ("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"),
                                                    sticky = True
                    )).add_to(m)

colores.add_to(m)
m


# In[40]:


colores = cmp.LinearColormap(
    ['red','lightblue', 'steelblue', 'blue'],
    vmin = min(list(mean_reviews['review_count'])), vmax = max(list(mean_reviews['review_count'])),
    caption = 'Number of reviews'
)

def estilo_provincias (feature):

    return{ 'radius': 7,
        'fillColor': colores(feature['properties']['yelp_reviews']), 
        'color': colores(feature['properties']['yelp_reviews']), 
        'weight': 1,
        'opacity' : 1,
        'fillOpacity' : 0.8}


# In[41]:


m = folium.Map(location=[40.4309, -3.6878], zoom_start = 10)

folium.GeoJson(datos_mapa, style_function = estilo_provincias,
               tooltip = folium.GeoJsonTooltip(fields = ['name', 'yelp_reviews'],
                                                    aliases=['Distrito: ', 'Avg reviews: '],
                                                    style = ("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"),
                                                    sticky = True
                    )).add_to(m)

colores.add_to(m)
m


# In[39]:


colores = cmp.LinearColormap(
    ['red','lightblue', 'steelblue', 'blue'],
    vmin = min(list(precios_modales['price'])), vmax = max(list(precios_modales['price'])),
    caption = 'Modal Price Category'
)

def estilo_provincias (feature):

    return{ 'radius': 7,
        'fillColor': colores(feature['properties']['yelp_price']), 
        'color': colores(feature['properties']['yelp_price']), 
        'weight': 1,
        'opacity' : 1,
        'fillOpacity' : 0.8}

m = folium.Map(location=[40.4309, -3.6878], zoom_start = 10)

folium.GeoJson(datos_mapa, style_function = estilo_provincias,
               tooltip = folium.GeoJsonTooltip(fields = ['name', 'yelp_price'],
                                                    aliases=['Distrito: ', 'Price category: '],
                                                    style = ("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"),
                                                    sticky = True
                    )).add_to(m)

colores.add_to(m)
m


# In[76]:


datos2 = pd.read_csv("C:/Users/inaki/OneDrive/Escritorio/yelp/yelp_distritos.csv")
datos2.head()


# In[ ]:




