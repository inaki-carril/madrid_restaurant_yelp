
#%%
# Paquetes necesarios para manipular informacion geo espacial.
# !pip install shapely
# !pip install pyproj
#%%

#%%
import requests
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import matplotlib.path as mplPath
import numpy as np
from shapely import wkt
from shapely.geometry import Point, shape
from pyproj import Proj, transform
#%%

#%%
# En este programa de python haremos llamadas a la API de Yelp, una API que nos permite obtener informacion de empresas
# en una determinada ubicacion. En este caso informacion sobre restaurantes en los distintos distritos de Madrid.
# El primer problema que se ha encontrado es que la API de Yelp devuelve un maximo de 1000 observaciones por llamada, y
# al utilizar como ubicacion la ciudad de madrid, la mayoria de esos mil datos son restaurantes del distrito centro. Para
# poder obtener mas de 1000 observaciones y obtener datos de todos los distritos se creara una funcion que reciba como 
# parametros las coordenadas del centroide de cada distrito y un radio especifico para cada distrito para tratar de maximizar
# los datos por distrito. Luego con un bucle haremos 21 llamadas a la API con esta funcion, variando los parametros mencionados.
# Evidentemente los distritos no son circulares y el radio se excedera en muchas ocasiones, dando lugar a datos duplicados.
# Tambien, claramente la API no puede recibir como parametro el nombre de un distrito o el poligono para solo devolver datos
# de ese distrito.
#%%

#%%
# Datos para afilar la busqueda en la API de Yelp. Estos datos incluyen los poligonos de los 21 distritos de la comunidad de
# Madrid.
import json

with open('data/madrid-districts.geojson.json', 'r', encoding = 'utf-8') as file:
    datos_mapa = json.load(file)

#%%

#%%
# Crear un diccionario con cada distrito y su centroide, estas coordenadas las usaremos en los parametros de la funcion de
# la API.
centroide_distritos = dict()
for distrito in range(21):
    centroide = list(Polygon(datos_mapa["features"][distrito]["geometry"]["coordinates"][0][0]).centroid.coords)
    centroide_distritos[datos_mapa["features"][distrito]["properties"]["name"]] = centroide
#%%

#%%
print(centroide_distritos)
#%%

#%%
# Crear un diccionario con los distritos y la distancia media del centroide a cada punto del poligono (frontera), esto
# nos ayudara a utilizar un radio mas preciso para cada distrito ya que estos varian en tamano.
distancias_medias = dict() 
for key in centroide_distritos:
    distancias = []
    for i in range(len(datos_mapa["features"][0]["geometry"]["coordinates"][0][0])):
        dist = Point(transform(Proj(init='EPSG:4326'), Proj(init='EPSG:3857'), 
                datos_mapa["features"][0]["geometry"]["coordinates"][0][0][0][0], 
                datos_mapa["features"][0]["geometry"]["coordinates"][0][0][0][1])).distance(Point(transform(Proj(init='EPSG:4326'),Proj(init='EPSG:3857'), 
                                                                                                            centroide_distritos[key][0][0], centroide_distritos[key][0][1])))
        distancias.append(dist)
    media = sum(distancias) / len(distancias)
    distancias_medias[key] = media

#%%

#%%
print(distancias_medias)
#%%

#%%
# Redondear las distancias a enteros y reducir las que sean muy grandes, esto para conseguir la maxima cantidad de datos por
# cada distrito, se probaron varias combinaciones y esta es la que recolecto mas datos por distrito.
for key in distancias_medias:
    if distancias_medias[key] > 5000:
        distancias_medias[key] = 5000
    else:
        distancias_medias[key] = int(distancias_medias[key])
distancias_medias

#%%

#%%
radios = []
for key in distancias_medias:
    radio = distancias_medias[key]
    radios.append(radio)

#%%

#%%
latitudes = []
longitudes = []
for key in centroide_distritos:
    latitud = centroide_distritos[key][0][1] 
    longitud = centroide_distritos[key][0][0]
    latitudes.append(latitud)
    longitudes.append(longitud) 
#%%

#%%
# Lista de distritos
distritos = []
for key in distancias_medias:
    distritos.append(key)
#%%

#%%
# Parametros a pasar al llamar a la API
key = "5s6jdk9aIjxDIlslHiGps6D9k4XbYgZPxSevE6SPiXtgxuNsuoJR2l2YVXzC4Qxt9Zhlkr1egArx_IsNHjC8-DmWtSyFml-c4aMXxCxy2_ja6xNRd47frV_iEsH_YXYx"
end_point = "https://api.yelp.com/v3/businesses/search"
#%%

#%%
# Funcion que utliza las coordenadas y el radio como parametros de busqueda. La parte del offset es porque la API solo 
# devuelve por default los primeras 50 resultados de los 1000 posibles.
def get_businesses(api_key, end_point, latitude, longitude, radius):
    headers = {'Authorization': 'Bearer %s' % api_key}
    url = end_point

    data = []
    for offset in range(0, 1000, 50):
        parameters = {"term" : "restaurant", "radius" : radius, "latitude" : latitude, "longitude" : longitude, 
              "limit" : 50, 'offset': offset
        }

        response = requests.get(url, headers = headers, params = parameters)
        if response.status_code == 200:
            data += response.json()['businesses']
        elif response.status_code == 400:
            print('400 Bad Request')
            break

    return data 

#%%

#%%
# Cada una de las 21 (21 distritos) llamadas a la API con sus respectivos datos se alamcenaran en un diccionario.
# Con un bucle hacemos 21 llamadas a la API de yelp con los parametros de cada distrito.
data = dict()
for i in range(21):
    data[distritos[i]] = get_businesses(key, end_point, latitudes[i], longitudes[i], radios[i])

#%%

#%%
# Almacenar en una lista los datos de cada llamada (los datos para cada distrito)
all_data = []
for key in data:
    all_data.append(data[key]) 
#%%

#%%
# Guardar los datos de cada distrito en un dataframe (trate de hacerlo con un bucle pero no obtenia el resultado deseado)
datos_df_0 = pd.json_normalize(all_data[0])
datos_df_1 = pd.json_normalize(all_data[1])
datos_df_2 = pd.json_normalize(all_data[2])
datos_df_3 = pd.json_normalize(all_data[3])
datos_df_4 = pd.json_normalize(all_data[5])
datos_df_5 = pd.json_normalize(all_data[5])
datos_df_6 = pd.json_normalize(all_data[6])
datos_df_7 = pd.json_normalize(all_data[7]) 
datos_df_8 = pd.json_normalize(all_data[8])
datos_df_9 = pd.json_normalize(all_data[9])
datos_df_10 = pd.json_normalize(all_data[10])
datos_df_11 = pd.json_normalize(all_data[11])
datos_df_12 = pd.json_normalize(all_data[12])
datos_df_13 = pd.json_normalize(all_data[13]) 
datos_df_14 = pd.json_normalize(all_data[14]) 
datos_df_15 = pd.json_normalize(all_data[15]) 
datos_df_16 = pd.json_normalize(all_data[16]) 
datos_df_17 = pd.json_normalize(all_data[17]) 
datos_df_18 = pd.json_normalize(all_data[18]) 
datos_df_19 = pd.json_normalize(all_data[19])
datos_df_20 = pd.json_normalize(all_data[20])

#%%

#%%
# Juntar los 21 dataframes anteriores en uno solo con toda la informacion recolectada.
todos = pd.concat([datos_df_0, datos_df_1, datos_df_2, datos_df_3, datos_df_4, datos_df_5, datos_df_6, datos_df_7, datos_df_8, 
          datos_df_9, datos_df_10, datos_df_11, datos_df_12, datos_df_13, datos_df_14, datos_df_15, datos_df_16, 
          datos_df_17, datos_df_18, datos_df_19, datos_df_20])

#%%

#%%
print(len(todos))
#%%

#%%
print(todos.head())
#%%

#%%
# Eliminar columnas irrelevantes.
todos.drop(["image_url", "location.address2", "location.address3", "location.display_address"], 
                     inplace = True, axis = 1)
#%%

#%%
# Guardar los datos en un archivo csv.
# todos.to_csv("C:/Users/inaki/OneDrive/Escritorio/practica_inaki_carril/data/yelp_data.csv", sep = ",")
#%%
