import streamlit as st
import pandas as pd 
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt
import json
import geopandas as gpd


    ##########################
    # AFFICHAGE du DATAFRAME #   
    ##########################

st.set_page_config(page_title="Data", page_icon="📊",layout="wide")
st.title("Analyses descriptives des données collectées")

st.markdown("<br><br>", unsafe_allow_html=True)  # espace vertical

df = pd.read_csv("C:/Users/pujad/OneDrive - APS Consult/Documents/FORMATION/Wild Code School/Projet 3/df_analysesFinal.csv", sep=',')
df.rename(columns = {'Nom_x':'Dénomination AF3V'},inplace=True)
df.rename(columns = {'Eclairage urbain en Nbre lapamdaires alimentés/an':'Eclairage urbain en Nbre lampadaires alimentés/an'},inplace=True)

st.markdown(" ### :one: Aperçu dynamique de la base de données")
st.markdown("<br><br>", unsafe_allow_html=True)  # espace vertical
st.markdown(" Sélection de 321 voies vertes dôtées d'un revêtement lisse pour cycles et rollers.")

# Colonnes à supprimer ? 
df1 = df.drop(columns=['Voie_ID',])
#rennomage sur la région Ile de France des erreurs de saisie

df1['Région'] = df1['Région'].replace({'Ile-de-France': 'Île-de-France', 'Ile-de-Frane': 'Île-de-France'})
df1['Région'] = df1['Région'].replace({'Pays basque autonome': 'Nouvelle-Aquitaine'})

st.data_editor(df1)

st.markdown("<br><br>", unsafe_allow_html=True)  # espace vertical

    #############################
    # Statistiques descriptives #
    #############################

#voies par régions
st.markdown(" ### :two: Distribution des voies vertes sélectionnées pour l'étude")

st.markdown("<br><br>", unsafe_allow_html=True)  # espace vertical

# Metrics sur les voies vertes de l'échantillon 
# Mise en forme

def format_number(n):
    return f"{int(n):,}".replace(",", " ")

a,b,c,d = st.columns(4)
distance_totale_voies = df1['Distance (km)'].sum()
distance_totale_equipee = len(df1)*0.2 # 200m par voie verte
pourcentage_equipe = df1['% Couverture correspondant (200m)'].mean()

a.metric(" ℹ️ Nombre de voies vertes", f"{format_number(len(df1))}",border=True)

b.metric(" ℹ️ Total de la distance des voies référencées", f"{format_number(distance_totale_voies)} km",border=True)

c.metric(" ℹ️ Total de la distance équipée", f"{format_number(distance_totale_equipee)} km",border = True)

d.metric(" ℹ️ Pourcentage de la distance équipée",f"{format_number(pourcentage_equipe)} %",border = True)

st.markdown("<br><br>", unsafe_allow_html=True)  # espace vertical

col1, col2 = st.columns(2)
with col1:
    df_region = df1.groupby(['Région'])['Distance (km)'].sum().round().reset_index(name='km de voies vertes')
    df_region = df_region.sort_values(by='km de voies vertes', ascending=False)    
    fig_region = px.bar(
    df_region,
    y='Région',
    x='km de voies vertes',
    color='Région',
    orientation='h',
    title="km de voies vertes par régions",
    )

# --- Mise en forme ---
    fig_region = px.bar(
    df_region.sort_values("km de voies vertes", ascending=False),
    y='Région',
    x='km de voies vertes',
    color='Région',
    orientation='h',
    title="km de voies vertes par régions"
    )

# --- Supprimer la légende ---
    fig_region.update_layout(
    showlegend=False,  # 👈 cache la légende
    height=600,
    width=800,
    margin=dict(l=60, r=20, t=60, b=60),
    font=dict(family="Helvetica", size=14),
    
    )
# --- Affichage ---
    st.plotly_chart(fig_region, use_container_width=False)

        

#voies par départements
with col2:
    df_departement = df1.groupby(['Département'])['Distance (km)'].sum().round().reset_index(name='km de voies vertes')
    df_departement = df_departement.sort_values(by='km de voies vertes', ascending=False)
    fig = px.bar(
        df_departement,
        x='Département',
        y='km de voies vertes',
        color='Département',
        title="km de voies vertes par départements",
    )

    fig.update_layout(
        xaxis_title="Département",
        yaxis_title='km de voies vertes',
        height=600,
        width=1200,  # Largeur suffisante pour forcer le scroll horizontal
        margin=dict(l=20, r=20, t=60, b=100),
        xaxis=dict(tickangle=-90),
        font=dict(family="Helvetica", size=14),
        showlegend=False,
    )

# Afficher dans Streamlit avec scroll horizontal
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)  # espace vertical



    ###################################################
    # Energie solaire produite et équivalents d'usage #
    ###################################################

# ----------------Agrégation nationale -------------------------------------------------------------------------------------------------------------

prod_total = df1['Production pour 860m2 de panneau (kWh)'].sum()
heures_eclairage = df1['Eclairage urbain en Nbre lampadaires alimentés/an'].sum()
km_bus = df1['nbre annuel km/BlueBus _12m'].sum()
charges_velo = df1['nbre annuel de charges velos'].sum()

# Affichage stylisé
st.markdown(" ### :three: Synthèse du potentiel solaire annuel estimé pour l'ensemble des voies vertes équipées")
st.markdown("<br><br>", unsafe_allow_html=True)  # espace vertical
st.markdown(" ##### ⚡️ Production solaire pour la France avec équivalents d’usage")

e,f= st.columns(2)
g,h = st.columns(2)
e.metric("🔋  Production totale ", format_number(prod_total) + " kWh"," Conso annuelle moyenne de 9 786 Français en 2024",border=True)
f.metric("💡  Éclairage public LED ", format_number(heures_eclairage) + " lampadaires","3% du parc Français LED (3.6 M) en 2024",border=True,)
g.metric("🚎 Km en BlueBus de 12m ", format_number(km_bus) + " km", "390 501 kg CO2e ou baisse de 81% des émissions par rapport à un bus thermique",border=True)
h.metric("🚲  Charges de VAE ", format_number(charges_velo) + " charges"," Equivalent 2.8M € en prix revente (production totale à un taux Enedis de 0.13 en 2024)",border=True )

st.markdown("<br><br>", unsafe_allow_html=True)  # espace vertical

#---------------------Visualisation par régions ----------------------------------------------------------------------------------------------------

# ------------------------ Nettoyage & fusion identique ------------------------
df_prod_regions = df1.groupby("Région")[[
    "Production pour 860m2 de panneau (kWh)",
    "Eclairage urbain en Nbre lampadaires alimentés/an",
    "nbre annuel km/BlueBus _12m",
    "nbre annuel de charges velos"
]].sum().reset_index().rename(columns={
    "Production pour 860m2 de panneau (kWh)": "🔋Production kWh",
    "Eclairage urbain en Nbre lampadaires alimentés/an": "💡Lampadaires alimentés",
    "nbre annuel km/BlueBus _12m": "🚎 km en BlueBus",
    "nbre annuel de charges velos": "🚲 nbre charge VAE"
})

# Charger et fusionner le GeoJSON
geojson_url = "https://france-geojson.gregoiredavid.fr/repo/regions.geojson"
regions_geo = gpd.read_file(geojson_url)
regions_geo["nom"] = regions_geo["nom"].str.strip()
df_prod_regions["Région"] = df_prod_regions["Région"].str.strip()

merged = regions_geo.merge(df_prod_regions, left_on="nom", right_on="Région")
merged = merged.to_crs(epsg=4326)

regions_to_exclude = ["Corse", "Guyane", "Guadeloupe", "Martinique", "La Réunion", "Mayotte"]
filtered = merged[~merged["nom"].isin(regions_to_exclude)].copy()

geojson_dict = json.loads(filtered.to_json())

# ------------------------ Construction de la carte ------------------------
fig = px.choropleth(
    filtered,
    geojson=geojson_dict,
    featureidkey="properties.nom",
    locations="nom",
    color="🔋Production kWh",
    color_continuous_scale=["#e8f166", "#12c7be", "#0a8d50"],
)

# Ajout du hover customisé
fig.update_traces(
    hovertemplate=
        "<b>%{location}</b><br><br>" +
        "🔋 Production : %{z:,} kWh<br>" +
        "💡 Lampadaires : %{customdata[0]:,}<br>" +
        "🚎 BlueBus : %{customdata[1]:,} km<br>" +
        "🚲 Charges VAE : %{customdata[2]:,}<extra></extra>",
    customdata=filtered[[
        "💡Lampadaires alimentés",
        "🚎 km en BlueBus",
        "🚲 nbre charge VAE"
    ]].values
)

# Mise en forme
fig.update_geos(
    showland=True,
    landcolor="#f0f0f0",
    showocean=True,
    oceancolor="#e6f7ff",
    showlakes=False,
    showrivers=False,
    showcoastlines=False,
    showframe=False,
    fitbounds="locations",
    projection_type="mercator",
    center={"lat": 46.5, "lon": 2.5},
    lataxis_range=[41, 52],
    lonaxis_range=[-5, 9]
)

fig.update_layout(
    font=dict(family="Helvetica, sans-serif", size=14, color="#333"),
    title=dict(
        text="⚡️ Production solaire par région avec équivalents d’usage",
        font=dict(size=20, color="#222"),
        x=0.0,
        xanchor="left"
    ),
    height=900,
    width=600,
    margin=dict(l=20, r=20, t=60, b=20),
    coloraxis_showscale=True,
)

# ---- Affichage dans Streamlit ----
st.plotly_chart(fig, use_container_width=True, key="solar_map_chart")


    ##############################
    # Productivité et paramètres #
    ##############################

#-------------------------Distrib en boxplot ---------------------------------------------------------------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)  # espace vertical

fig = px.box(
    df1,
    x="Énergie produite annuelle (kWh / m2 de panneau)",
    orientation="h",
    points="all",
    color_discrete_sequence=["#12c7be"]
)

fig.update_traces(
    marker=dict(color="#0a8d50", opacity=0.5, size=6),
    line=dict(color="#e8f166")
)

fig.update_layout(
    height=500,
    margin=dict(l=60, r=40, t=60, b=40),
    font=dict(family="Helvetica", size=14),
    xaxis_title="kWh / m² de panneau /an",
    title=dict(
        text="  ⚡️   Distribution du rendement  annuel",
        font=dict(size=20),
        x=0.0,
        xanchor="left"
    ),
    showlegend=False
      
)

st.plotly_chart(fig, use_container_width=True,key="boxplot_energie")


#-----------------------Top 20 des voies vertes les plus productives ------------------------------------------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)  # espace vertical
st.markdown(" ###  👍 20 voies vertes les plus productives 🔋")

df_top_prod=df.nlargest(20,'Énergie produite annuelle (kWh / m2 de panneau)').copy()
df_top_prod = df_top_prod.sort_values('Énergie produite annuelle (kWh / m2 de panneau)', ascending=True)
# Ajouter les colonnes nécessaires dans customdata
df_top_prod['🔋Production kWh/an'] = df_top_prod["Production pour 860m2 de panneau (kWh)"]
df_top_prod['💡Lampadaires alimentés'] = df_top_prod["Eclairage urbain en Nbre lampadaires alimentés/an"]
df_top_prod['🚎 km en BlueBus '] = df_top_prod["nbre annuel km/BlueBus _12m"]
df_top_prod['🚲 nbre charge VAE'] = df_top_prod["nbre annuel de charges velos"]

# Création du graphique
fig = px.bar(
    df_top_prod,
    x='Énergie produite annuelle (kWh / m2 de panneau)',
    y='Dénomination AF3V',
    orientation='h',
    color='Énergie produite annuelle (kWh / m2 de panneau)',
    color_continuous_scale=["#e8f166", "#12c7be", "#0a8d50"],
    labels={
        'Énergie produite annuelle (kWh / m2 de panneau)': 'Production (kWh/m²/an)',
        'Dénomination AF3V' :'Dénomination  AF3V'
    },
    
)

# Injecter les données personnalisées pour le hover uniquement
fig.update_traces(
    customdata=df_top_prod[['Voie_ID', 'Région','🔋Production kWh/an','💡Lampadaires alimentés', '🚎 km en BlueBus ', '🚲 nbre charge VAE']],
    hovertemplate=
        "<b>ID :</b> %{customdata[0]}<br>" +
        "<b>Région :</b> %{customdata[1]}<br>" +
        "🔋 Production kWh/an: %{customdata[2]}<br>" +
        "💡 Lampadaires alimentés : %{customdata[3]}<br>" +
        "🚎 km en BlueBus : %{customdata[4]}<br>" +
        "🚲 nbre charge VAE : %{customdata[5]}<br><extra></extra>"
)
      
# Optionnel : Affichage du texte sur les barres
fig.update_traces(
    text=df_top_prod['Énergie produite annuelle (kWh / m2 de panneau)'].round(2),
    textposition='outside'
)

fig.update_layout(
    height=750,
    margin=dict(l=120, r=50, t=70, b=40),
    font=dict(family="Helvetica", size=14),
    coloraxis_showscale=False
)

st.plotly_chart(fig, use_container_width=True)


#-----------------------BOTTOM 20 des voies vertes les moins productives ------------------------------------------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)  # espace vertical
st.markdown(" ### 👎 20 voies vertes les moins productives 🪫")

df_bott_prod=df.nsmallest(20,'Énergie produite annuelle (kWh / m2 de panneau)').copy()
df_bott_prod = df_bott_prod.sort_values('Énergie produite annuelle (kWh / m2 de panneau)', ascending=True)
# Ajouter les colonnes nécessaires dans customdata
df_bott_prod['🪫Production kWh/an'] = df_bott_prod["Production pour 860m2 de panneau (kWh)"]
df_bott_prod['💡Lampadaires alimentés'] = df_bott_prod["Eclairage urbain en Nbre lampadaires alimentés/an"]
df_bott_prod['🚎 km en BlueBus '] = df_bott_prod["nbre annuel km/BlueBus _12m"]
df_bott_prod['🚲 nbre charge VAE'] = df_bott_prod["nbre annuel de charges velos"]

# Création du graphique
fig = px.bar(
    df_bott_prod,
    x='Énergie produite annuelle (kWh / m2 de panneau)',
    y='Dénomination AF3V',
    orientation='h',
    color='Énergie produite annuelle (kWh / m2 de panneau)',
    color_continuous_scale=["#e7630b","#c78812","#e8f166"],
    labels={
        'Énergie produite annuelle (kWh / m2 de panneau)': 'Production (kWh/m²/an)',
        'Dénomination AF3V' :'Dénomination  AF3V'
    },
    
)

# Injecter les données personnalisées pour le hover uniquement
fig.update_traces(
    customdata=df_bott_prod[['Voie_ID', 'Région','🪫Production kWh/an','💡Lampadaires alimentés', '🚎 km en BlueBus ', '🚲 nbre charge VAE']],
    hovertemplate=
        "<b>ID :</b> %{customdata[0]}<br>" +
        "<b>Région :</b> %{customdata[1]}<br>" +
        "🪫Production kWh/an: %{customdata[2]}<br>" +
        "💡 Lampadaires alimentés : %{customdata[3]}<br>" +
        "🚎 km en BlueBus : %{customdata[4]}<br>" +
        "🚲 nbre charge VAE : %{customdata[5]}<br><extra></extra>"
    
)
      
# Optionnel : Affichage du texte sur les barres
fig.update_traces(
    text=df_bott_prod['Énergie produite annuelle (kWh / m2 de panneau)'].round(2),
    textposition='outside'
)

fig.update_layout(
    height=750,
    margin=dict(l=120, r=50, t=70, b=40),
    font=dict(family="Helvetica", size=14),
    coloraxis_showscale=False
)

st.plotly_chart(fig, use_container_width=True)



    ##############
    # SolarScore #
    ##############

    
st.markdown("<br><br>", unsafe_allow_html=True)  # espace vertical
st.markdown(" ### :four: Répartition du SolarScore des voies vertes par région")
col1,col2,col3,col4 = st.columns(4)
with col4:
    st.image("C:/Users/pujad/OneDrive - APS Consult/Documents/FORMATION/Wild Code School/Projet 3/SolaRide Horizon/data_viz/Échelle de notation SolarScore.png", width=140)

# Assurons-nous que la colonne Score est bien catégorique et ordonnée
df1["SolarScore"] = pd.Categorical(df1["SolarScore"], categories=["A", "B", "C", "D", "E"], ordered=True)

# Grouper le nombre de voies vertes par Région et Score
df_score_region = df1.groupby(['Région', 'SolarScore'], observed=True).size().reset_index(name='Nombre de voies')

# Palette personnalisée
custom_colors = {
    "A": "#0a8d50",   
    "B": "#12bb5e",   
    "C": "#f3db52",   
    "D": "#f7b12f",   
    "E": "#f87f2f"    
}

fig = px.bar(
    df_score_region,
    x="Région",
    y="Nombre de voies",
    color="SolarScore",
    category_orders={"SolarScore": ["A", "B", "C", "D", "E"]},
    color_discrete_map=custom_colors,
    labels={"Nombre de voies": "Nombre de voies vertes"},
    
)

# Mise en forme du layout
fig.update_layout(
    barmode="stack",
    height=600,
    margin=dict(l=60, r=40, t=60, b=100),
    font=dict(family="Helvetica", size=14),
    xaxis_tickangle=-45,
    legend_title_text="SolarScore",
    showlegend=False,
)

st.plotly_chart(fig, use_container_width=True, key="barres_empilées_scores")



st.markdown("<br><br>", unsafe_allow_html=True)  # espace vertical
st.markdown(" #### :question: Quelles autres analyses ou visualisations souhaiteriez-vous voir ?")









