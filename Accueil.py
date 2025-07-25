import streamlit as st
import time
st.set_page_config(page_title="🔎 Projet", layout="wide")

# --- Chargement du CSS via le fichier style.css ---
with open('style.css') as c:
    css = c.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

with st.spinner("Chargement en cours de l'application..."):
    time.sleep(2)  # Simule un traitement long
    # --- Logo ou bannière ---
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("images/logo_3.png",  width=600)

    # --- Titre principal ---
    st.markdown("<h1 style='text-align: center; color: #0d2c03; margin-top: -20px;'>Bienvenue sur SolaRide Horizon</h1>", unsafe_allow_html=True)

    # --- Séparateur ---
    st.markdown("<hr style='border: 1px solid #444;'>", unsafe_allow_html=True)

    # --- Texte de bienvenue ---
    st.markdown("""
    <div style='color: #0d2c03; font-size: 18px; text-align: center; line-height: 1.6; max-width: 1000px; margin: auto;'>
        Votre vélo à l’ombre, la planète au soleil ☀️<br>
         Apprenez-en plus sur les abris solaires pour cyclistes<br>
        <b>Parcourez le menu à gauche</b> pour débuter
    </div>
    """, unsafe_allow_html=True)

    # --- Footer ou note ---
    st.markdown("<br><p style='text-align: center; color: #0d2c03;'>Application conçue avec 💚 par Angéline, Aurélie & Yanis</p>", unsafe_allow_html=True)