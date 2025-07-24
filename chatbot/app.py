import streamlit as st
import requests
import pandas as pd


# 📌 Configuration Streamlit
st.set_page_config(page_title="Chatbot Énergie & Mobilité Douce", page_icon="🌞")
st.title("♻️ Expert Photovoltaïque et Pistes Cyclables")

# 🧠 Initialisation mémoire (avant toute utilisation)
if "qa_data" not in st.session_state:
    st.session_state.qa_data = []

# Bouton pour réinitialiser l'historique
if st.button("🗑️ Réinitialiser l'historique"):
    st.session_state.qa_data = []
    st.experimental_rerun()

# 👤 Avatar expert
st.image("C:/Users/pujad/OneDrive - APS Consult/Documents/FORMATION/Wild Code School/Projet 3/SolaRide Horizon/chatbot/ChatGPT Image 3 juil. 2025, 17_03_12.png", width=120)

# 📘 Introduction
with st.container():
    st.markdown("""
### 🤖 Pose une question à notre expert

Ce bot est spécialisé en :

- 🔋**Énergie photovoltaïque** : panneaux bifaciaux, ombrières solaires  
- 🚴‍♂️ **Mobilité douce** : pistes cyclables et voies vertes en France

**Exemples de questions :**
- "Quels sont les avantages des panneaux bifaciaux ?"
- "Comment intégrer une voie verte dans un projet rural ?"
""")

# 📚 Historique (FAQ interactive)
if st.session_state.qa_data:
    st.markdown("## 📚 Historique (FAQ interactive)")
    df = pd.DataFrame(st.session_state.qa_data)

    # 🎯 Filtrage par thème
    selected_theme = st.selectbox("🔎 Filtrer par thème :", ["Tous"] + sorted(df["Thème"].unique()))
    if selected_theme != "Tous":
        df = df[df["Thème"] == selected_theme]

    # 🔍 Affichage sous forme d'expander scrollable
    st.markdown("### 🔍 Questions & Réponses")
    for i, row in df.iterrows():
        with st.expander(f"❓ {row['Question']}"):
            st.markdown(f"""
                <div style="
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #ddd;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 16px;
                    line-height: 1.6;
                    max-height: 300px;
                    overflow-y: auto;
                    white-space: pre-wrap;
                ">
                    {row['Réponse'].replace("\n", "<br>")}
                </div>
            """, unsafe_allow_html=True)

    # 📥 Bouton de téléchargement
    csv = df.to_csv(index=False)
    st.download_button("📥 Télécharger l'historique (.csv)", data=csv, file_name="faq_chatbot.csv", mime="text/csv")

# 🗂️ Choix du thème avant la question
theme = st.selectbox("📂 Choisis le thème de ta question :", ["Énergie photovoltaïque", "Mobilité douce", "Autre"])

# 📝 Champ de saisie
user_input = st.text_input("💬 Pose ta question ici :", key="user_input")

# 🔁 Appel API Gemini
def call_gemini_api(prompt):
    api_key = st.secrets["GEMINI_API_KEY"]
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    response = requests.post(f"{url}?key={api_key}", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# 🤖 Génération de réponse
if user_input:
    with st.spinner("Réflexion de l'expert..."):
        response = call_gemini_api(user_input)
        try:
            assistant_reply = response["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            assistant_reply = "❌ Une erreur est survenue dans la réponse de l'API."

        # Limiter la réponse à 15 lignes
        assistant_reply = "\n".join(assistant_reply.strip().splitlines()[:15])

        # Affichage de la réponse
        st.markdown(f"🤖 **Expert :** {assistant_reply}")

        # 📥 Sauvegarder dans l'historique avec thème
        st.session_state.qa_data.append({
            "Question": user_input,
            "Réponse": assistant_reply,
            "Thème": theme
        })