import streamlit as st
import requests

# Configuration des URL
API_URL_PREDICT = "http://localhost:8000/predict"
API_URL_RECO = "http://localhost:8000/recommend"

st.set_page_config(page_title="Agritech Predictor", layout="wide")

st.title("🌾 Système de Recommandation Agricole")

# Utilisation d'onglets pour séparer les deux fonctions proprement
tab1, tab2 = st.tabs(["🔮 Prédiction de Rendement", "💡 Recommandation de Culture"])

# --- ONGLET 1 : PRÉDICTION ---
with tab1:
    st.header("Estimer le rendement d'une culture précise")
    with st.form("form_prediction"):
        col1, col2 = st.columns(2)
        with col1:
            item = st.selectbox("Culture", ['Maize', 'Potatoes', 'Rice', 'Wheat', 'Sorghum', 'Soybean',
                                            'Cassava', 'Yams', 'Sweet potatoes', 'Plantains and others'], key="item_p")
            region = st.selectbox("Région", ['Southern Asia', 'Southern Europe', 'Northern Africa', 'Polynesia',
                                                 'Sub-Saharan Africa', 'Latin America and the Caribbean',
                                                 'Western Asia', 'Australia and New Zealand', 'Western Europe',
                                                 'Eastern Europe', 'Northern America', 'South-eastern Asia','Eastern Asia',
                                                 'Northern Europe', 'Melanesia', 'Micronesia','Central Asia'], key="reg_p")
        
        with col2:
            avg_temp = st.slider("Température Moyenne (°C)", -5.0, 45.0, 15.0, key="temp_r")
            rainfall = st.slider("Précipitations (mm)", min_value=0, value=3500, key="rain_r")
            pesticides = st.slider("Pesticides (tonnes)", min_value=0.0, value=1850000.0, key="pest_r")
        
        submit_p = st.form_submit_button("Lancer la prédiction")

    if submit_p:
        payload = {
            "region": region, "item": item,
            "avg_temp": avg_temp, "rainfall_mm": rainfall, "pesticides_tonnes": pesticides
        }
        try:
            with st.spinner("Calcul en cours..."):
                res = requests.post(API_URL_PREDICT, json=payload)
                res.raise_for_status()
                data = res.json()
                st.success(f"### Résultat : {data['prediction']:.2f} kg/ha")
        except Exception as e:
            st.error(f"Erreur : {e}")

# --- ONGLET 2 : RECOMMANDATION ---
with tab2:
    st.header("Quelle culture est la plus adaptée ?")
    st.info("Cette fonction testera toutes les cultures pour vos conditions climatiques.")
    with st.form("form_reco"):
        col1, col2 = st.columns(2)
        with col1:
            region_r = st.selectbox("Région", ['Southern Asia', 'Southern Europe', 'Northern Africa', 'Polynesia',
                                                 'Sub-Saharan Africa', 'Latin America and the Caribbean',
                                                 'Western Asia', 'Australia and New Zealand', 'Western Europe',
                                                 'Eastern Europe', 'Northern America', 'South-eastern Asia','Eastern Asia',
                                                 'Northern Europe', 'Melanesia', 'Micronesia','Central Asia'], key="reg_r")
        
        with col2:
            avg_temp_r = st.slider("Température Moyenne (°C)", -5.0, 45.0, 15.0, key="temp_r")
            rainfall_r = st.slider("Précipitations (mm)", min_value=0, value=3500, key="rain_r")
            pesticides_r = st.slider("Pesticides (tonnes)", min_value=0.0, value=1850000.0, key="pest_r")
        
        submit_r = st.form_submit_button("Trouver la meilleure culture")

    if submit_r:
        payload_r = {
            "region": region_r,
            "avg_temp": avg_temp_r, "rainfall_mm": rainfall_r, "pesticides_tonnes": pesticides_r
        }
        try:
            with st.spinner("Analyse des cultures..."):
                res = requests.post(API_URL_RECO, json=payload_r)
                res.raise_for_status()
                data = res.json()
                st.success(f"🏆 La meilleure culture est : **{data['best_crop']}**")
                # Optionnel : afficher le classement
                st.write("Classement complet :")
                st.table(data['ranking'])
        except Exception as e:
            st.error(f"Erreur : {e}")