    #----------------------------------------------------------------------------------------------------------------------------------------------- #
    #                                                               Librairies                                                                       #
    #----------------------------------------------------------------------------------------------------------------------------------------------- #

import pandas as pd
import streamlit as st
import datetime
import time


st.set_page_config(page_title="Projet", layout="wide")


# --- Chargement du CSS via le fichier style.css ---
with open('style.css') as c:
    css = c.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)



# --- Logo centré ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("images/logo_3.png", width=500)
st.write("---")

# --- Accueil ---

st.markdown(""" </br>
                <p class="custom-paragraph"></br>
                <p class="custom-paragraph">Dans le cadre de notre formation de Data Analyst à la Wild Code School, nous avons eu l'opportunité de mener un projet sur un sujet libre.
Ce projet nous a permis d’explorer une problématique de notre choix, de collecter et d’analyser des données pertinentes, et de mettre en pratique les compétences acquises tout au long de notre formation.
Découvrez ci-dessous l’histoire et les objectifs de ce projet.</p>
            """, unsafe_allow_html=True)
               

# ------------------------------------------------------------------------------------------------------------------------ #
#                                                       CONTENU                                                            #
# ------------------------------------------------------------------------------------------------------------------------ #

# Création de 5 onglets
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Contexte", "Livrables", "Technologies", "L'équipe", "Liens utiles"])

            # ---------------------- #
            #         ONGLET 1 
            # ---------------------- #


with tab1:


   st.markdown("""
        ## 🧭 Contexte

        SolaRide Horizon est une application de data analyse développée pour estimer le potentiel photovoltaïque des pistes cyclables (voies vertes) en France. En nous appuyant sur des initiatives pionnières comme celle de Genève, notre projet vise à :

        - Réduire la dépendance énergétique aux sources non renouvelables  
        - Révéler le potentiel énergétique des infrastructures existantes et inexploitées

        ## 🧪 Objectifs du projet

        | Aspect | Description |
        |--------|-------------|
        | 🎯 **Sujet initial** | Potentiel bio-solaire des surfaces cyclables pour produire de l'énergie |
        | 🔄 **Révision du sujet** | Estimation du rendement solaire basé sur les données AF3V + météo |
        | 🧠 **Inspiration** | Projet suisse à Genève + projet "Potentiel Scolaire" de Data For Good |
        | 🛠️ **Objectif technique** | Créer une application de A à Z avec données, visualisations et ChatBot IA |
        """, unsafe_allow_html=True)


            # ---------------------- #
            #         ONGLET 2 
            # ---------------------- #

with tab2:
    st.markdown("""
        ##Les livrables
""", unsafe_allow_html=True)
    
    st.markdown(""" 
                <p class="custom-paragraph">TEXTE A AJOUTER</p>
""", unsafe_allow_html=True)
            # ---------------------- #
            #         ONGLET 3
            # ---------------------- #

with tab3:
    st.markdown("""
        ##Les Technologies
""", unsafe_allow_html=True)

    st.markdown(""" 
                | Technologie       | Usage                                         |
|-------------------|-----------------------------------------------|
| **Python**        | Web scraping, transformation, API, GeoPandas  |
| **Pandas**        | Traitement et agrégation des données          |
| **Plotly.express**| Visualisations                                |
| **Streamlit**     | Application interactive et visualisation      |
| **Open-Meteo API**| Données météo historiques                     |
| **Folium**        | Cartographie interactive                      |
| **Scikit-learn**  | Prémices d'intégration IA (prédictions)       |
| **OpenAI**        | Intégration d'un LLM pour le ChatBot          |
                """)
    
            # ---------------------- #
            #         ONGLET 4
            # ---------------------- #

with tab4:
    st.markdown("""
        ##L'équipe
""", unsafe_allow_html=True)

    st.markdown(""" 
                    <p class="custom-paragraph">TEXTE A AJOUTER</p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.image("images/illu_ange2.png", width=300)
        st.write("**Angéline**")
        st.write("Méticuleuse et jusqu'au boutiste, elle n'hésitera pas à creuser le sujet jusqu'à la moëlle... Mais seulement si la rigolade est de mise.")
        # Ajouter description rapide

    with col2:
        st.image("images/illu_aurelie.png", width=300)
        st.write("**Aurélie**")
        st.write("Dynamique, elle voit la vie comme une aventure : faut que ça bouge ! Toujours prête à donner de son temps pour les autres, et relever de nouveaux défis !")
        # Ajouter description rapide    

    with col3:
        st.image("images/illu_yanis.png", width=300)
        st.write("**Yanis**")
        st.write("Efficace, Yanis met les mains au clavier plus vite que son ombre. Complètement geek, il peut tenir n'importe quelle conversation, surtout s'il s'agit d'IT ou d'e-sport.")
        # Ajouter description rapide    


    
            # ---------------------- #
            #         ONGLET 5
            # ---------------------- #

with tab5:
    st.markdown("""
        ##Les liens utiles
""", unsafe_allow_html = True)
    
    st.markdown("[Potentiel s(c)olaire] (https://dataforgood.fr/projects/potentielscolaire)", unsafe_allow_html=True)

    st.markdown("[Article de presse du projet Solar Horizon] (https://ww2.sig-ge.ch/actualites/sig-et-letat-de-geneve-devoilent-la-premiere-piste-cyclable-solaire-de-suisse)", unsafe_allow_html=True)
   