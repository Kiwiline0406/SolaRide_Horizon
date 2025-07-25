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
                <p class="custom-paragraph">Dans le cadre de notre formation de Data Analyst à la Wild Code School, nous avons l'opportunité de réaliser un projet avec un sujet libre. Découvrez ci-dessous l'histoire de ce projet.</p>
            """, unsafe_allow_html=True)
               

# ------------------------------------------------------------------------------------------------------------------------ #
#                                                       CONTENU                                                            #
# ------------------------------------------------------------------------------------------------------------------------ #

# Création de 5 onglets
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Inspirations", "Livrables", "Sources des données", "L'équipe", "Liens utiles"])

            # ---------------------- #
            #         ONGLET 1 
            # ---------------------- #


with tab1:
   
    st.markdown("""
        <div class="hero-title">L'histoire</div>
""", unsafe_allow_html=True)


    st.markdown(""" 
                    <p class="custom-paragraph">TEXTE A AJOUTER</p>
    """, unsafe_allow_html=True)


            # ---------------------- #
            #         ONGLET 2 
            # ---------------------- #

with tab2:
    st.markdown("""
        <div class="hero-title">Les livrables</div>
""", unsafe_allow_html=True)
    
    st.markdown(""" 
                <p class="custom-paragraph">TEXTE A AJOUTER</p>
""", unsafe_allow_html=True)
            # ---------------------- #
            #         ONGLET 3
            # ---------------------- #

with tab3:
    st.markdown("""
        <div class="hero-title">Les sources</div>
""", unsafe_allow_html=True)

    st.markdown(""" 
                    <p class="custom-paragraph">TEXTE A AJOUTER</p>
    """, unsafe_allow_html=True)
    
            # ---------------------- #
            #         ONGLET 4
            # ---------------------- #

with tab4:
    st.markdown("""
        <div class="hero-title">L'équipe</div>
""", unsafe_allow_html=True)

    st.markdown(""" 
                    <p class="custom-paragraph">TEXTE A AJOUTER</p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.image("images/illu_ange2.png", width=300)
        st.write("Angéline")
        st.write("Something...")
        # Ajouter description rapide

    with col2:
        st.image("images/illu_aurelie.png", width=300)
        st.write("Aurélie")
        st.write("Dynamique, elle voit la vie comme un sport : faut que ça bouge ! Toujours prête à donner de son temps pour les autres, elle est la partenaire idéale pour partir à l'aventure.")
        # Ajouter description rapide    

    with col3:
        st.image("images/illu_yanis.png", width=300)
        st.write("Yanis")
        st.write("Efficace, Yanis met les mains au clavier plus vite que son ombre. Complètement geek, il peut tenir n'importe quelle conversation, surtout s'il s'agit d'IT ou d'e-sport.")
        # Ajouter description rapide    


    
            # ---------------------- #
            #         ONGLET 5
            # ---------------------- #

with tab5:
    st.markdown("""
        <div class="hero-title">Les liens utiles</div>
""", unsafe_allow_html = True)
    
    st.markdown("[Potentiel s(c)olaire] (https://dataforgood.fr/projects/potentielscolaire)", unsafe_allow_html=True)

    st.markdown("[Article de presse du projet Solar Horizon] (https://ww2.sig-ge.ch/actualites/sig-et-letat-de-geneve-devoilent-la-premiere-piste-cyclable-solaire-de-suisse)", unsafe_allow_html=True)
   