import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()
api_key = os.getenv("api_key")

# Créer le client OpenAI
client = OpenAI(api_key = api_key)

st.title("🔆🚲 Expert Photovoltaïque & Pistes Cyclables")

st.markdown("""
Pose une question à un expert spécialisé en :
- Énergie photovoltaïque (panneaux bifaciaux, ombrières solaires)
- Pistes cyclables et voies vertes en France

_Exemples_ :
- "Quels sont les avantages des panneaux bifaciaux ?"
- "Comment intégrer des pistes cyclables dans un projet rural ?"
""")

user_prompt = st.text_input("Tu es un expert en production d'énergie photovoltaïque pour les panneaux bifaciaux ET en ombrières ET sur le sujet des pistes cyclables ET l'amènagement des voies vertes en France. "
        "Réponds de manière claire, factuelle et adaptée au contexte français.")

if user_prompt:
    with st.spinner("Réponse en cours..."):
        response = client.chat.completions.create(
            model="gpt-4o",  # ou gpt-4o-mini
            messages=[
                {"role": "system", "content": (
                    "Tu es un expert en énergie photovoltaïque (notamment les panneaux bifaciaux, les ombrières solaires), "
                    "ainsi qu'en aménagement des pistes cyclables et voies vertes en France. "
                    "Tu donnes des réponses factuelles, précises, claires et contextualisées pour la France."
                )},
                {"role": "user", "content": user_prompt}
            ]
        )

        answer = response.choices[0].message.content
        st.success("Réponse de l'expert :")
        st.markdown(answer)