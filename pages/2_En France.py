
#----------------------------------------------------------------------------------------------------------------------------------------------- #
#                                                               Librairies                                                                       #
#----------------------------------------------------------------------------------------------------------------------------------------------- #

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import re
import ast
import base64
import folium
import time
from typing import Optional
from folium.plugins import MarkerCluster
import streamlit as st
import streamlit.components.v1 as components
import requests_cache
from retry_requests import retry
import openmeteo_requests

st.set_page_config(page_title="Outil de visualisation", layout="wide")

# --- Chargement du CSS via le fichier style.css ---
with open('style.css') as c:
    css = c.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

st.markdown(
    "<h1 style='text-align: center;'>Nos Voies Vertes Françaises</h1>",
    unsafe_allow_html=True
)
st.write("---")
# ------------------------------------------------------------------------------------------------------------------------ #
#                                                       CONTENU                                                            #
# ------------------------------------------------------------------------------------------------------------------------ #


        # ------------------------------------------------ #
        #                     WEBSCRAPING                  #
        # ------------------------------------------------ #

# URL de base
url = "https://www.af3v.org/resultats-des-recherches/?stv%5B1%5D=on&sact%5B9%5D=on&sact%5B6%5D=on&ssort=dista"
# Tri : voie verte lisse, vélo de route et roller

@st.cache_resource
def get_session():
    return requests_cache.CachedSession('.http_cache', expire_after=86400)  # 24h

@st.cache_data
def get_basic_fiches():
    session = get_session()
   
    # Récupération des noms des fiches VV et les liens sur les différentes pages de résultats 

    data = {}
    index = 0

    for i in range(0,325,10):
        link = f"https://www.af3v.org/resultats-des-recherches/?stv%5B1%5D=on&sact%5B9%5D=on&sact%5B6%5D=on&ssort=dista&searchoffs={i}&blockOrLine=0"

        html = session.get(link)

        # récupérer le nom, les villes de début et fin et le lien de la fiche
        if html.status_code == 200:
            soup = BeautifulSoup(html.text, 'html.parser')
            cards = [div for div in soup.find_all("div", class_="openSansReg temCom198")] # Pour chaque élément div trouvé dans soup.find_all(...), il est gardé dans une liste.
            cards_town = [div for div in soup.find_all("div", class_="openSansReg s12w400 coc7c7c7")]
        

            for card, cardt in zip(cards, cards_town):      # si le nombre de résultats change surtout pour dernière page)
                var_1 = card.find('a')
                if var_1:
                    name = var_1.get_text(strip=True)
                    link_end = var_1['href']
                    link_full = "https://www.af3v.org" + link_end
                    trajet = cardt.get_text(strip=True)
                    words = re.search(r'De (.+?) à (.+)', trajet)
                    

                    if words:
                        start = words.group(1)
                        end = words.group(2)

                        data[index] = { 'Nom': name,
                                        'Lien': link_full,
                                        'Début': start,
                                        'Fin': end}
                        index += 1
    return data

@st.cache_data
def get_fiches_characteristics(basic_data):
        # récupérer les autres infos caractéristiques en rentrant dans la fiche
    session = get_session()

    data = basic_data.copy()

    for i in data:
        link_fiche = data[i]['Lien']
        html_fiche = session.get(link_fiche)

        if html_fiche.status_code == 200:
            soup_fiche = BeautifulSoup(html_fiche.text, 'html.parser')
            caracteristics_dist = [div for div in soup_fiche.find_all("div", class_="co767676 openSansMed s14w400")]
            if len(caracteristics_dist) >= 4:
                distance = caracteristics_dist[0].get_text(strip=True)
                type_voie = caracteristics_dist[1].get_text(strip=True)
                nature = caracteristics_dist[2].get_text(strip=True)
                revetement = caracteristics_dist[3].get_text(strip=True)
                data[i].update({ 'Distance': distance,
                            'Type voie': type_voie,
                            'Nature voie': nature,
                            'Revêtement': revetement})
    return data

@st.cache_data
def get_fiches_coordinates(data_with_chars):    

    #print("🗺️  Récupération des coordonnées...")

    session = get_session()

    data = data_with_chars.copy()

    for i in data:
        link_fiche = data[i]['Lien']
        html_fiche = session.get(link_fiche)

        if html_fiche.status_code == 200:
            soup_fiche = BeautifulSoup(html_fiche.text, 'html.parser')
            car_map = [div for div in soup_fiche.find_all("iframe", id="carte_voies")]
            for map in car_map:
                carte = map["data-url"]
                coords_all = re.search(r'(?<=bbox=)[^&]*', carte) # cherche tout ce qui est après = et avant &
                if coords_all:
                    coords_str = coords_all.group() # récupérer la str extraite
                    coords = coords_str.split(',') # séparer par ,
                    coord_start = (coords[0], coords[1])
                    coord_end = (coords[2], coords[3])
                    data[i].update({ 'Carte': carte,
                                    'Coordonnées de début': coord_start,
                                    'Coordonnées de fin': coord_end})                        

    return data

@st.cache_data                   
def scraping():
    
    # Étape 1
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Récupération des fiches de base...")
    basic_data = get_basic_fiches()
    progress_bar.progress(33)
    
    # Étape 2
    status_text.text("Ajout des caractéristiques...")
    data_with_chars = get_fiches_characteristics(basic_data)
    progress_bar.progress(66)
    
    # Étape 3
    status_text.text("Ajout des coordonnées...")
    final_data = get_fiches_coordinates(data_with_chars)
    progress_bar.progress(100)
    
    status_text.text(f"L'attente est finie : {len(final_data)} fiches viennent d'être récupérées sur le site de l'Association Française pour le développement des Véloroutes et Voies Vertes.")
    return final_data

data = scraping()

@st.cache_data()
def convert_en_df(data):
    df = pd.DataFrame.from_dict(data, orient='index')

    def midpoint(lat1, lon1, lat2, lon2):
        mid_lat = (lat1 + lat2) / 2
        mid_lon = (lon1 + lon2) / 2
        return mid_lat, mid_lon

    def calculate_midpoint_voie_verte(row):
        try:
            coord_debut = row['Coordonnées de début']
            coord_fin = row['Coordonnées de fin']
            
            # Convertir selon le type
            if isinstance(coord_debut, str):
                coord_debut = coord_debut.strip('()')
                lat_debut, lon_debut = map(float, coord_debut.split(','))
            else:
                lat_debut, lon_debut = float(coord_debut[0]), float(coord_debut[1])
            
            if isinstance(coord_fin, str):
                coord_fin = coord_fin.strip('()')
                lat_fin, lon_fin = map(float, coord_fin.split(','))
            else:
                lat_fin, lon_fin = float(coord_fin[0]), float(coord_fin[1])
            
            return midpoint(lat_debut, lon_debut, lat_fin, lon_fin)
        except Exception as e:
            print(f"Erreur: {e}")
            return None
    
    df['Coordonnées milieu'] = df.apply(calculate_midpoint_voie_verte, axis=1)

    def safe_literal_eval(val):
        if isinstance(val, str):
            try:
                return ast.literal_eval(val)
            except Exception as e:
                print(f"Erreur pour la valeur {val}: {e}")
                return None
        else:
            return val  # déjà un tuple ou autre type valide
    
    df["Coordonnées milieu"] = df["Coordonnées milieu"].apply(safe_literal_eval)
    df["Coordonnées de début"] = df["Coordonnées de début"].apply(safe_literal_eval)
    df["Coordonnées de fin"] = df["Coordonnées de fin"].apply(safe_literal_eval)
    df['Distance'] = df['Distance'].str.replace('km', '', regex=False).str.replace(',', '.').astype(float)
    df['Début'] = df['Début'].str.capitalize()
    df['Fin'] = df['Fin'].str.capitalize()
    df['% Couverture correspondant (200m)'] = round((200 / (df['Distance'] * 1000) * 100),2)

    return df

df = convert_en_df(data)

@st.cache_data()
def categorize_nature(voie) -> str :
    voie = str(voie).lower()
    if 'rivière' in voie or 'canal' in voie or 'chemin de halage' in voie:
        return 'Bord de rivière ou canal'
    elif 'sentier' in voie or 'chemin' in voie:
        return 'Bord de sentier'
    elif 'route' in voie:
        return 'Bord de route'
    elif 'piste' in voie:
        return 'Piste cyclable'
    elif 'chemin de halage' in voie:
        return 'Chemin de halage'
    elif 'ancienne' in voie:
        return 'Ancienne ligne ferrovière'
    elif 'verte' in voie:
        return 'Voie verte'
    elif 'ferrée'in voie:
        return 'Bord de voie ferrée'
    else:
        return 'Voie verte'
    
df['Groupes nature voie'] = df['Nature voie'].apply(categorize_nature)





        # --------------------------------------------------------------- #
        #                    COMPLETION DONNEES SOLAIRES                  #
        # --------------------------------------------------------------- #

@st.cache_data
def solar_info_annuel(coord_tuple):
    coord_string = str(coord_tuple)
    coord_string = coord_string.strip('()')  # Retire les parenthèses si présentes
    lon, lat = map(float, coord_string.split(','))

    # Délai de 1-2 secondes entre chaque requête
    time.sleep(1.5)
    
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Paramètres à renseigner
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": f"2024-01-01",
        "end_date": f"2024-12-31",
        "daily": ["sunshine_duration", "temperature_2m_mean"],
        "hourly": "shortwave_radiation",
        "timezone": "Europe/Berlin"
    }
    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]
    

    # Process hourly data
    hourly = response.Hourly()
    hourly_shortwave_radiation = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data["shortwave_radiation"] = hourly_shortwave_radiation

    hourly_dataframe = pd.DataFrame(data = hourly_data)


    # Nettoyage pour exploitation des données du df Hourly
    hourly_dataframe['month'] = hourly_dataframe['date'].dt.month_name(locale='English')
    hourly_dataframe['month_num'] = hourly_dataframe['date'].dt.month

    hourly_dataframe = hourly_dataframe.iloc[2:]

    df_ghi = hourly_dataframe.groupby(['month', 'month_num']).agg(
        ghi_mean_W_m2=('shortwave_radiation', 'mean')
    )

    df_ghi = df_ghi.sort_values(by='month_num')


    # Process daily data
    daily = response.Daily()
    daily_sunshine_duration = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_mean = daily.Variables(1).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}

    daily_data["sunshine_duration"] = daily_sunshine_duration
    daily_data["temperature_2m_mean"] = daily_temperature_2m_mean

    daily_dataframe = pd.DataFrame(data = daily_data)


    # Nettoyage pour exploitation des données du df daily
    daily_dataframe['sunshine_duration_hours'] = daily_dataframe['sunshine_duration'] / 3600
    daily_dataframe.drop(columns='sunshine_duration', inplace=True)

    daily_dataframe = daily_dataframe.iloc[1:]

    daily_dataframe['month'] = daily_dataframe['date'].dt.month_name(locale='English')
    daily_dataframe['month_num'] = daily_dataframe['date'].dt.month
    daily_dataframe['days_in_month'] = daily_dataframe['date'].dt.daysinmonth



    df_weather = daily_dataframe.groupby(['month', 'month_num']).agg(
        temp_mean_c=('temperature_2m_mean', 'mean'),
        sunshine_duration_mean_hour=('sunshine_duration_hours', 'mean'),
        days_in_month=('days_in_month', 'first')  
    )


    df_weather = df_weather.sort_values(by='month_num')

    # Concaténation des dfs

    df = pd.merge(df_weather, df_ghi, on='month')
    

    # ==================#
    #     Panneau       #
    #  Photovoltaïques  #
    # ==================#

    # --- Paramètres spécifiques à l'installation ---
    # Ajout de paramètres types, servant d'exemples, 
    EFFICIENCY_PANEL = 0.20  # Exemple : rendement de 20 % (par ex. pour un panneau de 400W, diviser par sa surface en m²)

    ANGLE_ORIENTATION_FACTOR = 1.00 # paramètre crucial pour estimer le rendement énergétique réel d’un système photovoltaïque, car il prend en compte l’impact de l’alignement physique de l’installation par rapport au soleil.

    TEMP_COEFFICIENT_PMAX = 0.004  # Typique : 0.004 soit 0,4 % de perte de puissance par °C 

    SYSTEM_LOSS_FACTOR = 0.85      # Tient compte des pertes du système : onduleur, câblage, saleté, ombrage, etc. (typiquement entre 0.75 et 0.90)

    DELTA_TEMP_PANEL = 20          # Écart estimé entre la température du panneau et la température ambiante (en °C)

    # =================#
    #     Formules     #
    # =================#

    # 1. Calcul de l’irradiance journalière en kWh/m²/jour
    # Ce calcul suppose que ghi_mean_W_m2 et sunshine_duration_mean_hour représentent des moyennes journalières pour le mois.
    df['ghi_journalier_kWh_m2_jour'] = (df['ghi_mean_W_m2'] * df['sunshine_duration_mean_hour']) / 1000

    # 2. Estimation de la température de fonctionnement des panneaux
    # La température du panneau est généralement supérieure à la température ambiante
    df['panel_temp_c'] = df['temp_mean_c'] + DELTA_TEMP_PANEL

    # 3. Calcul du facteur de correction de température
    # Les performances diminuent lorsque la température dépasse 25°C
    df['correction_temp'] = 1 - (df['panel_temp_c'] - 25) * TEMP_COEFFICIENT_PMAX

    # On s’assure que correction_temp reste dans des bornes raisonnables (évite des gains irréalistes ou pertes trop fortes)
    df['correction_temp'] = df['correction_temp'].clip(lower=0.95, upper=1.05)

    # 4. Calcul de la production d’énergie journalière par m² (kWh/jour/m²)
    # On combine tous les facteurs :
    # GHI_journalier * Rendement * Facteur d’orientation * Correction température * Pertes système
    df['energie_jour_kWh/j/m2'] = df['ghi_journalier_kWh_m2_jour'] * \
                                EFFICIENCY_PANEL * \
                                ANGLE_ORIENTATION_FACTOR * \
                                df['correction_temp'] * \
                                SYSTEM_LOSS_FACTOR

    # Arrondi à 2 décimales pour l’affichage
    df['energie_jour_kWh/j/m2'] = round(df['energie_jour_kWh/j/m2'], 2)

    # 5. Calcul de la production mensuelle d’énergie par m² (kWh/mois/m²)
    # On multiplie la production journalière par le nombre de jours dans le mois
    df['energie_mois_kWh/mois/m2'] = round(df['energie_jour_kWh/j/m2'] * df['days_in_month'], 2)

    return round(df['energie_mois_kWh/mois/m2'].sum(), 2)
    
df['Energie produite annuelle (kWh)'] = df['Coordonnées milieu'].apply(solar_info_annuel)
df['Énergie produite annuelle (kWh / 860m2 de panneau)'] = df['Energie produite annuelle (kWh)']. apply(lambda x: x*860)


        # --------------------------------------------------------------- #
        #                         AJOUT SOLAR SCORE                       #
        # --------------------------------------------------------------- #


@st.cache_data()
def load_data():
    df_solarscore = pd.read_csv("datasets/df_solarscore.csv")
    return df_solarscore

df_solarscore = load_data()

dF = pd.merge(df, df_solarscore, on='Nom')



        # --------------------------------------------------------------- #
        #                         AFFICHAGE CARTE                         #
        # --------------------------------------------------------------- #

url_map = 'http://api-adresse.data.gouv.fr/search/'


def get_lat_lon(address : str):

    session = get_session()
    params = {
        'q': address,

        'limit': 1
    }
    response = session.get(url_map, params=params)
    j = response.json()
    if len(j.get('features')) > 0:
        first_result = j.get('features')[0]
        lon, lat = first_result.get('geometry').get('coordinates')
        return(lat, lon)
    else:
        return('No result')

@st.cache_data
def create_map(dF):
    """Créer la carte Folium avec les marqueurs"""

    #Récupérer les coordonnées de France à l'aide de la fonction get_lat_lon
    france_coord = get_lat_lon("France")

    #Centrer la carte folium sur ces coordonnées
    my_map = folium.Map(location=france_coord, zoom_start=6)

    # Ajouter un cluster de marqueurs pour de meilleures performances
    marker_cluster = MarkerCluster().add_to(my_map)

    # Ajouter des couleurs pour le SolarScore
    colors_score = {"A":"darkgreen",
                    "B":"green", 
                    "C":"lightgreen",
                    "D":"orange",
                    "E":"red"}

    #Fonction pour placer les marqueurs sur la carte
    def add_markers(row, my_map=my_map):
        location = row["Nom"]
        lon, lat = row["Coordonnées milieu"]
        score = row.get("SolarScore")
        color = colors_score.get(score)

        # Créer un popup avec plus d'informations
        popup_text = f"""
        <b><span style='color:green'>{location}</span></b><br>
        <br>
        <b>De 📍 : </b>{row.get('Début', 'N/A')}<br>
        <b>À 📍 : </b>{row.get('Fin', 'N/A')}<br>
        <b>Distance: </b>{row.get('Distance', 'N/A')} km<br>
        <b>Nature: </b>{row.get('Groupes nature voie', 'N/A')}<br>
        <b>Lien de la fiche : </b><a href="{row.get('Lien', '#')}" target="_blank">ouvrir la fiche dans une autre fenêtre</a><br>
        <b>Couverture de la piste : </b>{row.get('% Couverture correspondant (200m)', 'N/A')} %<br>
        <b>Energie produite : </b>{row.get('Énergie produite annuelle (kWh / 860m2 de panneau)')} kWh (moyenne anuelle)<br>
        <b>SolarScore 🔆 : </b><span style='color:{color}; font-weight:bold'>{row.get('SolarScore')}</span><br>
        """

        folium.Marker(location=(lat, lon), 
                      popup=folium.Popup(popup_text, max_width=300), 
                      icon=folium.Icon(icon="leaf", color=color)
                      ).add_to(marker_cluster)
        

    #Ajouter les marqueurs sur la carte
    dF.apply(add_markers, axis=1)

    #Afficher la carte folium
    return my_map


# Affichage de la carte

st.write("""Avec la carte ci-dessous, nous cherchons à identifier les voies vertes référencées sur le site de l'AF3V
         qui pourraient se prêter à une duplication du projet Solar Horizon.""")
st.write("""Pour ceci, nous leur avons attribué un score nommé SolarScore 
         basé sur le ratio entre :\n
         - l'énergie produite annuellement (en kWh par 860m2 de panneau) sur un point au milieu de la voie verte\n
         - et l'énergie produite annuellement à Satigny, commune du projet Solar Horizon.""")      
st.write("""Ce SolarScore va de A à E, avec A les voies avec un potentiel solaire nettement supérieur à celui de Solar Horizon, 
         et E un potentiel solaire nettement inférieur.""")

if not df.empty:
    # Créer et afficher la carte
    my_map = create_map(dF)
        
    # Utiliser st.components.v1.html
    map_html = my_map._repr_html_()
    components.html(map_html, height=600, scrolling=True)

    # Afficher la légende
    st.markdown("""
    <div style="line-height: 1.8">
        <b>Légende SolarScore :</b><br>
        <span style='display:inline-block; width:12px; height:12px; background-color:darkgreen; border-radius:50%; margin-right:6px'></span> A : Excellent potentiel solaire (entre 137% et 127% de l'énerge produite avec Solar Horizon)<br>
        <span style='display:inline-block; width:12px; height:12px; background-color:green; border-radius:50%; margin-right:6px'></span> B : Très bon potentiel solaire (entre 125% et 111%)<br>
        <span style='display:inline-block; width:12px; height:12px; background-color:lightgreen; border-radius:50%; margin-right:6px'></span> C : Potentiel solaire plus ou moins similaire (entre 104% et 92%)<br>
        <span style='display:inline-block; width:12px; height:12px; background-color:orange; border-radius:50%; margin-right:6px'></span> D : Potentiel solaire inférieur (entre 91% et 80%)<br>
        <span style='display:inline-block; width:12px; height:12px; background-color:red; border-radius:50%; margin-right:6px'></span> E : Potentiel solaire nettement inférieur (entre 79% et 70%)
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("Aucune donnée à afficher")
        
# Bouton de téléchargement
#csv = dF.to_csv(index=False)
#st.download_button(
            #label="📥 Télécharger les données CSV",
            #data=csv,
            #file_name="voies_vertes.csv",
            #mime="text/csv")


# Informations supplémentaires
def get_base64_image(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

info_icon = get_base64_image("images/icones/icone_info.png")

st.markdown("---")
st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 40px;">
        <div> <img src="data:image/png;base64,{info_icon}" width="48"><span style="font-size:20px; font-weight: bold;">Informations</span><br><br>
            - <b>Source pour les voies vertes :</b> <a href="https://www.af3v.org/" target="_blank">AF3V - Association Française pour le développement des Véloroutes et Voies Vertes</a><br>
            - <b>Source pour les données météorologiques / solaires :</b> <a href="https://open-meteo.com/en/docs" target="_blank">Open-Meteo - Weather Forecast API</a><br>
            - <b>Critères :</b> Voies vertes lisses, adaptées au vélo de route et roller<br>
            - <b>Mise à jour :</b> Données récupérées automatiquement
</div>""",
        unsafe_allow_html=True
    )