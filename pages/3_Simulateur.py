
import streamlit as st
import numpy as np
import requests
import folium
import calendar
import base64
import streamlit.components.v1 as components
from streamlit_folium import st_folium
import pandas as pd
import time
import openmeteo_requests
import requests_cache
from retry_requests import retry
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

# ------------------------------------------------------------------------------------------------------------------------ #
#                                                       CONTENU 
# ------------------------------------------------------------------------------------------------------------------------ #


            # ---------------------------- #
            #        Simulation carte      #
            # ---------------------------- #

# Titre
st.markdown(
    "<h1 style='text-align: center;'>Simulateur</h1>",
    unsafe_allow_html=True
)
st.write("---")
st.write("Vous voulez vérifier pour une voie verte près de chez vous mais qui n'est pas encore renseignée sur notre outil de visualisation ?")

st.write("Cette carte ci-dessous est interactive : zoomez et localisez la/les voie(s) que vous cherchez, les coordonnées GPS seront conservées dans un tableau en dessous, prêt à exporter.")

url_map = 'http://api-adresse.data.gouv.fr/search/'

@st.cache_resource
def get_session():
    return requests_cache.CachedSession('.http_cache', expire_after=86400)  # 24h

# Récupérer les coordonnées depuis une adresse
@st.cache_data
def get_lat_lon(address : str):
    params = {
        'q': address,
        'limit': 1
    }
    response = requests.get(url_map, params=params)
    j = response.json()
    if len(j.get('features')) > 0:
        first_result = j.get('features')[0]
        lon, lat = first_result.get('geometry').get('coordinates')
        return(lat, lon)
    else:
        return('No result')

# Récupérer le nom de la ville depuis des coordonnées
@st.cache_data
def get_ville(lat, lon):
    url = 'https://api-adresse.data.gouv.fr/reverse/'
    params = {'lon': lon, 'lat': lat}
    response = requests.get(url, params=params)
    j = response.json()
    if j.get('features'):
        return j['features'][0]['properties'].get('city', 'Inconnue')
    return 'Inconnue'

# Initialisation de l'historique des datas de clics
if "last_click" not in st.session_state:
    st.session_state["last_click"] = None
    
# Récupérer les coordonnées de France à l'aide de la fonction get_lat_lon
france_coord = get_lat_lon("France")
m = folium.Map(location=france_coord, zoom_start=6)

# Ajout des marqueurs existants
if st.session_state["last_click"]:
    lat = st.session_state["last_click"]["Latitude"]
    lon = st.session_state["last_click"]["Longitude"]
    ville = st.session_state["last_click"]["Ville"]
    folium.Marker([lat, lon], popup=ville).add_to(m)

# Affichage dans Streamlit avec interaction activée
output = st_folium(m, width=1200, height=600)

if output and output.get("last_clicked"):
    lat = output["last_clicked"]["lat"]
    lon = output["last_clicked"]["lng"]
    ville = get_ville(lat, lon)
    st.session_state["last_click"] = {"Latitude": lat, "Longitude": lon, "Ville": ville}
    st.success(f"Clic enregistré : {lat:.4f}, {lon:.4f} — {ville}")

# Bouton pour réinitialiser les clics
if st.button("🔄️ Réinitialiser le clic pour sélectionner une autre localisation"):
    st.session_state["last_click"] = None
    st.experimental_rerun()

df = pd.DataFrame()
# Affichage de l'historique
if st.session_state["last_click"]:
    df_click = pd.DataFrame([st.session_state["last_click"]])
st.write("---")

            # --------------------------------------------- #
            #        Simulation données météorologiques     #
            # --------------------------------------------- #

@st.cache_data
def solar_info_mensuel_popup(coords):
    lat = coords[0]
    lon = coords[1]

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

    ANGLE_ORIENTATION_FACTOR = 1.00 

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


    # Calcul de la production annuelle pour chaque surface
    
    df_annuel = pd.DataFrame({
        "Surface du panneau (m2)": [1],
        "Énergie produite annuelle (kWh)":
            round(df['energie_mois_kWh/mois/m2'].sum(), 2),
        
    })

    df.drop(columns=['days_in_month', 'ghi_journalier_kWh_m2_jour', 'panel_temp_c', 'correction_temp', 'energie_jour_kWh/j/m2'], inplace=True)
    df.rename(columns= {
        'temp_mean_c' : 'Température moyenne (°c)',
        'sunshine_duration_mean_hour' : "Durée d'ensoleillement moyenne (heure)",
        'ghi_mean_W_m2' : 'GHI moyen (W/m²)',
        'energie_mois_kWh/mois/m2' : 'Énergie produite (kWh/m²)',
        'month' : 'Mois'
    }, inplace=True)

    df['Énergie produite (kWh/860m²)'] = df['Énergie produite (kWh/m²)']*860
    df = df.drop(columns=["Énergie produite (kWh/m²)"])

    #return df_annuel
    return df
    
results = []

st.write("""Le tableau ci-dessous vous permet d'avoir un aperçu des données météorologiques et solaires pour l'année 2024 complète.
         Pour chaque mois, vous obtenez la température moyenne journalière par mois, la durée d'ensoleillement moyenne journalière par mois,
         le GHI moyen mensuel et enfin la quantité d'énergie produite pour 860m² de panneaux photovoltaïques bifaciaux en kWh.
         Le calcul de l'énergie produite est directement lié aux trois autres mesures indiquées.""")

if "last_click" in st.session_state and st.session_state["last_click"]:
    lat, lon = df_click.iloc[-1]["Latitude"], df_click.iloc[-1]["Longitude"]
    df_simu = solar_info_mensuel_popup((lat, lon))
    df_simu.reset_index(inplace=True)
    st.dataframe(df_simu)
else:
    st.info("Ajoutez un point sur la carte pour calculer la production solaire.")


            # --------------------------------------------- #
            #             Simulation cas concrets           #
            # --------------------------------------------- #

if "last_click" in st.session_state and st.session_state["last_click"]:

    total_energie = df_simu["Énergie produite (kWh/860m²)"].sum()
    #création de la variable Nbre de charges vélos électriques/an
    val_bike = int(round(total_energie.sum() / 0.5))

    #création de la variable alimentation annuelle moy éclairage urbain en nuités (8h/jour)pour 40 lampadaires
    val_bus = int(round(total_energie.sum() / 200))

    #création de la variable nbre de km annuels pour un BlueBus de 12m
    val_lamp = round((total_energie.sum() * 225) / 272)

    #création de la variable revenus de revente Enedis
    val_enedis = round(total_energie.sum()  * 0.13)

    #création de la variable conso annuelle de x nbr de personnes
    def calcul_equivalent(energie):
        if energie < 2223:
            return "Insuffisant pour 1 personne"
        else:
            return int(round(energie / 2223))
    val_perso = calcul_equivalent(total_energie)


   

    def get_base64_image(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    panneau_icon = get_base64_image("images/icones/icone_panneau.png")
    bike_icon = get_base64_image("images/icones/icone_bike.png")
    bus_icon = get_base64_image("images/icones/icone_bus.png")
    lamp_icon = get_base64_image("images/icones/icone_lamp.png")
    coin_icon = get_base64_image("images/icones/icone_coin.png")
    perso_icon = get_base64_image("images/icones/icone_perso.png")

    st.write("---")

    st.write("""Les nombres ci dessous représentent des valeurs annuelles, respectivement la quantité d'énergie produite, 
             le nombre de charges vélos, le nombre de kilomètres pour un bluebue de 12m, le nombre de lampadaires (allumés 8h/nuit), 
             la somme issue de la revente de l'énergie produite, et enfin la consommation annuelle en électricité pour X persones.
             """)

    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])

    with col1 : 
        st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 40px;">
            <div><img src="data:image/png;base64,{panneau_icon}" width="48"><br><span>{total_energie:.2f} kWh</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with col2 : 
        st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 40px;">
            <div><img src="data:image/png;base64,{bike_icon}" width="48"><br><span>{val_bike} vélos</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )
        
    with col3:
        st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 40px;">
            <div><img src="data:image/png;base64,{bus_icon}" width="48"><br><span>{val_bus} km</span></div>

        """,
        unsafe_allow_html=True
    )
        
    with col4:
        st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 40px;">
            <div><img src="data:image/png;base64,{lamp_icon}" width="48"><br><span>{val_lamp} lampadaires</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )   
        
    with col5:
        st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 40px;">
            <div><img src="data:image/png;base64,{coin_icon}" width="48"><br><span>{val_enedis}€ de revente</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )   
        
    with col6:
        st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 40px;">
            <div><img src="data:image/png;base64,{perso_icon}" width="48"><br><span>{val_perso} personnes</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )  

    st.write("---")

            # --------------------------------------------- #
            #             Simulation prédiction             #
            # --------------------------------------------- #

@st.cache_resource   
def predict_solar_weather_m12(lat, lon):
    """
    Fonction intégrée qui :
    1. Récupère les données météo historiques à partir de coordonnées géographiques
    2. Entraîne un modèle de ML sur ces données
    3. Retourne les prédictions météo sur les 12 prochains mois (M+12)
    
    Args:
        lat (float): Latitude du point géographique
        lon (float): Longitude du point géographique
    
    Returns:
        pd.DataFrame: Prédictions météo pour les 12 prochains mois avec colonnes :
                     - Date
                     - Température moyenne (°c)
                     - Durée d'ensoleillement moyenne (heure)
                     - GHI moyen (W/m²)
                     - Énergie solaire produite (kWh/860m²)
    """
    
    # === ÉTAPE 1: Récupération des données historiques === #

    # Initialisation du client Open-Meteo avec un cache pour ne pas refaire les mêmes requêtes et une logique de retry
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Liste pour stocker les DataFrames de chaque année
    all_dataframes = []

    # Boucle sur les années de 2015 à 2025 pour récupérer les données
    for year in range(2015, 2026):
        # Préparation de la requête API Open-Meteo pour l’année en cours
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": f"{year}-01-01", 
            "end_date": f"{year}-12-31" if year < 2025 else "2025-07-23",
            "daily": ["sunshine_duration", "temperature_2m_mean"],
            "hourly": "shortwave_radiation",
            "timezone": "Europe/Berlin"
        }

        try:
            # Appel API
            responses = openmeteo.weather_api(url, params=params)
            response = responses[0]

            # --- Traitement des données horaires (irradiance solaire) --- #
            hourly = response.Hourly()
            hourly_shortwave_radiation = hourly.Variables(0).ValuesAsNumpy()

            # Construction du DataFrame horaire
            hourly_data = {"date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )}
            hourly_data["shortwave_radiation"] = hourly_shortwave_radiation
            hourly_dataframe = pd.DataFrame(data=hourly_data)

            # Ajout des colonnes temporelles
            hourly_dataframe['month'] = hourly_dataframe['date'].dt.month_name(locale='English')
            hourly_dataframe['month_num'] = hourly_dataframe['date'].dt.month
            hourly_dataframe['year'] = hourly_dataframe['date'].dt.year
            hourly_dataframe = hourly_dataframe.iloc[2:]  # Supprimer les 2 premières valeurs erratiques

            # Agrégation mensuelle de l’irradiance (GHI)
            df_ghi = hourly_dataframe.groupby(['year', 'month', 'month_num']).agg(
                ghi_mean_W_m2=('shortwave_radiation', 'mean')
            ).sort_values(by=['year', 'month_num'])

            # --- Traitement des données journalières (température & ensoleillement) --- #
            daily = response.Daily()
            daily_sunshine_duration = daily.Variables(0).ValuesAsNumpy()
            daily_temperature_2m_mean = daily.Variables(1).ValuesAsNumpy()

            # Construction du DataFrame journalier
            daily_data = {"date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            )}
            daily_data["sunshine_duration"] = daily_sunshine_duration
            daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
            daily_dataframe = pd.DataFrame(data=daily_data)

            # Conversion de l’ensoleillement en heures et nettoyage
            daily_dataframe['sunshine_duration_hours'] = daily_dataframe['sunshine_duration'] / 3600
            daily_dataframe.drop(columns='sunshine_duration', inplace=True)
            daily_dataframe = daily_dataframe.iloc[1:]

            # Ajout des colonnes temporelles
            daily_dataframe['month'] = daily_dataframe['date'].dt.month_name(locale='English')
            daily_dataframe['month_num'] = daily_dataframe['date'].dt.month
            daily_dataframe['year'] = daily_dataframe['date'].dt.year
            daily_dataframe['days_in_month'] = daily_dataframe['date'].dt.daysinmonth

            # Agrégation mensuelle de la température et de la durée d’ensoleillement
            df_weather = daily_dataframe.groupby(['year', 'month', 'month_num']).agg(
                temp_mean_c=('temperature_2m_mean', 'mean'),
                sunshine_duration_mean_hour=('sunshine_duration_hours', 'mean'),
                days_in_month=('days_in_month', 'first')
            ).sort_values(by=['year', 'month_num'])

            # Fusion des deux sources (journalier & horaire) pour l’année en cours
            df_year = pd.merge(df_weather, df_ghi, on=['year', 'month', 'month_num'])
            all_dataframes.append(df_year)

        except Exception as e:
            print(f"Erreur lors de la récupération des données pour {year}: {e}")
            continue

    # Vérification si on a bien récupéré des données
    if not all_dataframes:
        print("Aucune donnée récupérée")
        return pd.DataFrame()

    # Concaténation de toutes les années
    df = pd.concat(all_dataframes, ignore_index=False).sort_values(by=['year', 'month_num'])
    df = df.reset_index()

    # === Calcul de la production photovoltaïque historique === #

    # Définition des constantes physiques et techniques du panneau
    EFFICIENCY_PANEL = 0.20
    ANGLE_ORIENTATION_FACTOR = 1.00
    TEMP_COEFFICIENT_PMAX = 0.004
    SYSTEM_LOSS_FACTOR = 0.85
    DELTA_TEMP_PANEL = 20

    # Calcul de l’énergie journalière en kWh/m²/jour
    df['ghi_journalier_kWh_m2_jour'] = (df['ghi_mean_W_m2'] * df['sunshine_duration_mean_hour']) / 1000

    # Température estimée du panneau
    df['panel_temp_c'] = df['temp_mean_c'] + DELTA_TEMP_PANEL

    # Correction de performance selon la température
    df['correction_temp'] = 1 - (df['panel_temp_c'] - 25) * TEMP_COEFFICIENT_PMAX
    df['correction_temp'] = df['correction_temp'].clip(lower=0.95, upper=1.05)

    # Calcul de la production d'énergie journalière
    df['energie_jour_kWh/j/m2'] = (
        df['ghi_journalier_kWh_m2_jour'] *
        EFFICIENCY_PANEL *
        ANGLE_ORIENTATION_FACTOR *
        df['correction_temp'] *
        SYSTEM_LOSS_FACTOR
    ).round(2)

    # Multiplication par le nombre de jours pour avoir la production mensuelle
    df['energie_mois_kWh/mois/m2'] = (df['energie_jour_kWh/j/m2'] * df['days_in_month']).round(2)

    # === ÉTAPE 2: Entraînement du modèle de Machine Learning === #

    # Suppression des colonnes qui introduiraient une fuite de données
    cols_to_drop = ['panel_temp_c', 'correction_temp', 'energie_jour_kWh/j/m2', 'energie_mois_kWh/mois/m2']
    df_ml = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

    # Création de la colonne datetime pour le suivi temporel
    df_ml['date'] = pd.to_datetime(df_ml[['year', 'month_num']].rename(columns={'month_num': 'month'}).assign(day=1))

    # Création des features cycliques (saisonnalité mensuelle)
    df_ml['month_sin'] = np.sin(2 * np.pi * df_ml['month_num'] / 12)
    df_ml['month_cos'] = np.cos(2 * np.pi * df_ml['month_num'] / 12)

    # Définition des features (X) et des cibles (y)
    features = ['year', 'days_in_month', 'month_sin', 'month_cos']
    targets = ['temp_mean_c', 'sunshine_duration_mean_hour', 'ghi_mean_W_m2']

    X = df_ml[features]
    y = df_ml[targets]

    # Séparation temporelle train/test
    train_mask = df_ml['year'] <= 2021
    test_mask = df_ml['year'] > 2021
    X_train, X_test = X[train_mask], X[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]

    # Standardisation des features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Définition du modèle multi-sortie
    base_model = RandomForestRegressor(random_state=42)
    multi_output_model = MultiOutputRegressor(base_model)

    # Définition de la grille de recherche d’hyperparamètres
    param_grid = {
        "estimator__n_estimators": [50, 100, 200],
        "estimator__max_depth": [5, 10, None],
        "estimator__min_samples_split": [2, 5],
    }

    # Utilisation de TimeSeriesSplit pour validation temporelle
    tscv = TimeSeriesSplit(n_splits=5)

    # Recherche des meilleurs hyperparamètres
    grid_search = GridSearchCV(
        estimator=multi_output_model,
        param_grid=param_grid,
        cv=tscv,
        scoring='neg_mean_squared_error',
        n_jobs=-1,
        verbose=0,
    )
    grid_search.fit(X_train_scaled, y_train)

    # Création du modèle final avec les meilleurs paramètres
    best_params = grid_search.best_params_
    final_model = MultiOutputRegressor(
        RandomForestRegressor(
            n_estimators=best_params['estimator__n_estimators'],
            max_depth=best_params['estimator__max_depth'],
            min_samples_split=best_params['estimator__min_samples_split'],
            random_state=42
        )
    )
    final_model.fit(X_train_scaled, y_train)

    # === ÉTAPE 3: Génération des prédictions sur les 12 mois futurs === #

    # Création d’un calendrier des 12 mois futurs (de août 2025 à juillet 2026)
    future_dates = pd.date_range(start='2025-08-01', periods=12, freq='MS')
    
    # Préparation des features pour prédiction
    future_df = pd.DataFrame({
        'year': future_dates.year,
        'month_num': future_dates.month,
    })
    future_df['days_in_month'] = future_df.apply(
        lambda row: calendar.monthrange(row['year'], row['month_num'])[1], 
        axis=1
    )
    future_df['month_sin'] = np.sin(2 * np.pi * future_df['month_num'] / 12)
    future_df['month_cos'] = np.cos(2 * np.pi * future_df['month_num'] / 12)

    # Standardisation des données futures
    X_future = future_df[features]
    X_future_scaled = scaler.transform(X_future)

    # Prédictions avec le modèle
    y_future_pred = final_model.predict(X_future_scaled)

    # Construction du DataFrame final des prédictions
    predictions_future = pd.DataFrame(y_future_pred, columns=targets)
    predictions_future['date'] = future_dates
    predictions_future['days_in_month'] = future_df['days_in_month'].values

    # === ÉTAPE 4: Estimation de la production solaire future === #

    # Calculs identiques à l’historique pour estimer la production d'énergie
    predictions_future['ghi_journalier_kWh_m2_jour'] = (
        predictions_future['ghi_mean_W_m2'] * predictions_future['sunshine_duration_mean_hour']
    ) / 1000
    predictions_future['panel_temp_c'] = predictions_future['temp_mean_c'] + DELTA_TEMP_PANEL
    predictions_future['correction_temp'] = 1 - (predictions_future['panel_temp_c'] - 25) * TEMP_COEFFICIENT_PMAX
    predictions_future['correction_temp'] = predictions_future['correction_temp'].clip(lower=0.95, upper=1.05)
    predictions_future['energie_jour_kWh/j/m2'] = (
        predictions_future['ghi_journalier_kWh_m2_jour'] *
        EFFICIENCY_PANEL *
        ANGLE_ORIENTATION_FACTOR *
        predictions_future['correction_temp'] *
        SYSTEM_LOSS_FACTOR
    ).round(2)
    predictions_future['energie_mois_kWh/mois/m2'] = (
        predictions_future['energie_jour_kWh/j/m2'] * predictions_future['days_in_month']
    ).round(2)

    # Renommage des colonnes pour un rendu final clair
    predictions_future.rename(columns={
        'date' : 'Date',
        'temp_mean_c': 'Température moyenne (°c)',
        'sunshine_duration_mean_hour': "Durée d'ensoleillement moyenne (heure)",
        'ghi_mean_W_m2': 'GHI moyen (W/m²)',
        'energie_mois_kWh/mois/m2': 'Énergie solaire produite (kWh/m²)'
    }, inplace=True)
    predictions_future['Énergie solaire produite (kWh/860m²)'] = predictions_future['Énergie solaire produite (kWh/m²)']*860
    predictions_future['Date'] = predictions_future['Date'].dt.to_period('M')

    # Réorganisation des colonnes pour affichage
    final_columns = [
        'Date', 
        'Température moyenne (°c)', 
        "Durée d'ensoleillement moyenne (heure)", 
        'GHI moyen (W/m²)',
        'Énergie solaire produite (kWh/860m²)'
    ]
    predictions_future = predictions_future[final_columns]

    return predictions_future

st.write("""Dans le tableau ci-dessous vous obtenez des prédictions sur les 12 mois à venir concernant la température journalière moyenne ,
         la durée d'ensoleillement journalière moyenne, le GHI moyen et l'énergie moyenne produite pour 860 m² de panneau.""")

if "last_click" in st.session_state and st.session_state["last_click"]:
    predictions = predict_solar_weather_m12(lat, lon)

    st.dataframe(predictions)