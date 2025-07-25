# 🌞 SolaRide Horizon

**Étude et simulation du potentiel solaire des voies vertes en France, inspirée du projet Solar Horizon de Genève.**

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

## 🔍 Données utilisées

- **Voies vertes en France (AF3V)** : [https://www.af3v.org/](https://www.af3v.org/)
- **Modèle solaire suisse (SIG Genève)** :
  - Piste cyclable solaire (SIG) : [https://solarchitecture.ch/fr/la-premiere-piste-cyclable-solaire-de-suisse/](https://solarchitecture.ch/fr/la-premiere-piste-cyclable-solaire-de-suisse/)
  - Modèle détaillé Solarchitecture.ch : [https://ww2.sig-ge.ch/actualites/sig-et-letat-de-geneve-devoilent-la-premiere-piste-cyclable-solaire-de-suisse](https://ww2.sig-ge.ch/actualites/sig-et-letat-de-geneve-devoilent-la-premiere-piste-cyclable-solaire-de-suisse)
- **Météo historique** : Open-Meteo API
- **Modélisation énergétique** : Rendement basé sur 860 m² de panneaux bifaciaux

## 🛠️ Technologies utilisées

| Technologie | Usage |
|-------------|-------|
| **Python** | Web scraping, transformation, API, GeoPandas |
| **Pandas** | Traitement et agrégation des données |
| **Plotly.express** | Visualisations |
| **Streamlit** | Application interactive et visualisation |
| **Open-Meteo API** | Données météo historiques |
| **Folium** | Cartographie interactive |
| **Scikit-learn** | Prémices d'intégration IA (prédictions) |
| **OpenAI** | Intégration d'un LLM pour le ChatBot |

## ⚙️ Fonctionnalités de l'application

### 🗺️ Carte interactive
- Visualisation des voies vertes référencées par AF3V
- Filtrage par piste cyclable, rendement solaire, surface estimée

### ☀️ Calcul de rendement énergétique
- Application du modèle genevois : 860 m² → extrapolation sur la base AF3V
- Utilisation des données météo historiques

### 📈 Tableaux de bord analytiques
- Nombre total de km exploitables
- Production d'énergie par piste cyclable, régions / mois
- Exemples concrets d'équivalence énergétique
- Création d'un **SolarScore** (indicateur de rentabilité)
  
  <img width="384" height="256" alt="image" src="https://github.com/user-attachments/assets/f02fb7f4-8a94-4ec4-a105-b4e6868aa18e" />


### 🤖 Intégration IA
- Prédiction des données météos + rendement mensuel glissant (M+12) basé sur historique météorologique
- Analyse des zones à fort potentiel futur
- ChatBot

## 🖼️ Captures d'écran de l'application

*(À intégrer ici)*

- 🗺️ Carte des voies vertes
- ☀️ Simulation du rendement
- 📊 Tableau de bord régional

## 📦 Installation & Exécution

### 🔧 Prérequis
- Python 3.10+
- Environnement virtuel (recommandé)
- Clé API Open-Meteo (facultatif pour taux limités)
- Clé API Gemini (Gratuit avec limites)

### ⚙️ Setup

```bash
git clone https://github.com/votre-utilisateur/solaRide-horizon.git
cd solaRide-horizon
python -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\activate sur Windows
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Structure du projet

```
solaRide-horizon/                    # Dossier racine du projet
├── .devcontainer/                   # Configuration environnement de développement
├── .streamlit/                      # Configuration Streamlit
├── Notebooks/                       # Notebooks Jupyter pour R&D et prototypage
│   ├── essai_webscrap.ipynb             # Premiers essais de web scraping (AF3V)
│   ├── extract_meteo_mensuel.ipynb      # Extraction données météo mensuelles
│   ├── extract_meteov4.ipynb            # Version optimisée extraction météo
│   ├── modele_ml_v3.ipynb               # Développement modèle ML
│   ├── notebook.ipynb                   # Extraction météo annuelle
│   ├── notebook_ctrlv.ipynb             # Fonction extraction météo annuelle
│   ├── simulation_production.ipynb      # Étude rendement énergétique
│   └── simulator_function.ipynb         # Développement fonctions simulateur
├── datasets/                        # Données intermédiaires et finales
│   ├── df_analysesFinal.csv             # Dataframe consolidé résultats
│   ├── df_solarscore.csv                # Score solaire par voie verte
│   └── df_voies_vertes.csv              # Données de base voies vertes
├── images/                          # Ressources visuelles
│   └── icones/                          # Icônes pour l'application
├── pages/                           # Pages secondaires Streamlit
│   ├── 1_Projet.py                      # Présentation du projet
│   ├── 2_En France.py                   # Cartographie et analyses France
│   ├── 3_Simulateur.py                  # Simulateur production solaire
│   └── 4_Expert IA.py                   # Chatbot IA
├── .gitignore                       # Fichiers à ignorer par Git
├── Accueil.py                       # Point d'entrée principal
├── README.md                        # Documentation principale
├── pyproject.toml                   # Configuration dépendances Python
├── requirements.txt                 # Liste des dépendances
├── style.css                        # Personnalisation CSS
└── uv.lock                          # Fichier de verrouillage uv
```

## 🔄 Méthodologie

Nous avons suivi une approche itérative sur **7 semaines**, avec un focus collaboratif :

- **Semaine 1-2** : Cadrage, collecte des données AF3V
- **Semaine 3-4** : Enrichissement avec météo + premiers calculs, chatbot
- **Semaine 5-6** : Visualisation, design application, version bêta
- **Semaine 7** : Polish, IA, exportation, débogage, mise en production

## 💬 Équipe & Crédits

Projet développé par une équipe d'étudiants dans le cadre de la formation **Data Analyst - Wild Code School 2025**.

### Contributeurs :
- **Aurélie Pujado** – Data Analyst
- **Angéline Tavares** – Data Analyst
- **Yanis Ruel** – Data Analyst

## 📄 Licence

Ce projet est open-source sous **licence MIT**. Vous êtes libre de l'utiliser, modifier ou partager à condition d'en citer l'origine.

## ✨ Perspectives

- 📦 **Packaging SaaS** possible pour les collectivités locales
- 🤝 **Collaboration** avec l'équipe du projet de Genève
- 💰 **Analyse Financière** du rendement des installations
- ⚡ **Déploiement** dans des communes tests en France
- 🌍 **Extension** à d'autres pays européens (Suisse, Belgique...)
