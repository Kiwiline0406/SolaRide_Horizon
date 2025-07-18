import streamlit as st
import requests


# Charger les variables d'environnement
api_key = st.secrets["GEMINI_API_KEY"]

# Créer le client Gemini
def call_gemini_api(prompt):
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

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
st.set_page_config(page_title="Chatbot Énergie & Mobilité Douce", page_icon="🌞")
st.title("♻️ Expert Photovoltaïque et Pistes Cyclables")

# Afficher l’avatar expert
st.image("C:/Users/pujad\OneDrive - APS Consult/Documents/FORMATION/Wild Code School/Projet 3/SolaRide Horizon/chatbot/ChatGPT Image 3 juil. 2025, 17_03_12.png", width=120)

# ✅ INTRO visible pour l’utilisateur
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

# ✅ MÉMOIRE : initialisation du prompt system
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "Tu es un expert en énergie photovoltaïque (panneaux bifaciaux, ombrières solaires) "
                "et en aménagement des pistes cyclables et voies vertes en France. "
                "Tu réponds de manière claire, concise factuelle, contextualisée pour le public français. "
                "Soit précis, pragmatique , utile et professionnel, même face à des demandes techniques."
            )
        }
    ]


# 🧠 Champ pour question utilisateur
user_input = st.text_input("💬 Pose ta question ici :", key="user_input")

# 🧠 Traitement & affichage de la réponse
if user_input:
    with st.spinner("Réflexion de l'expert..."):
        response = call_gemini_api(user_input)


    assistant_reply = assistant_reply = response["candidates"][0]["content"]["parts"][0]["text"]
    st.markdown(f"🤖 **Expert :** {assistant_reply}")