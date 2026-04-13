import streamlit as st
import requests
import pandas as pd

# Configuration des URL
API_URL_PREDICT = "http://localhost:8000/predict"
API_URL_RECO = "http://localhost:8000/recommend"

st.set_page_config(page_title="Agritech Predictor", layout="wide")

st.title("🌾 Système de Recommandation Agricole")

# Dictionnaire des infos mape à afficher dans l'encart
infos_mape = {
    "Maize": "18,45%",
    "Potatoes": "13,77%",
    "Rice": "13,07%",
    "Wheat": "16,79%",
    "Sorghum": "22,50%",
    "Soybean": "20,23%",
    "Cassava": "16,35%",
    "Yams": "28,40%",
    "Sweet potatoes": "17,24%",
    "Plantains and others": "17,46%"
}
# Dictionnaire des infos de perte économqiue à afficher dans l'encart
infos_economic = {
    "Maize": "137.09 $",
    "Potatoes": "547.61 $",
    "Rice": "123.23 $",
    "Wheat": "71.89 $",
    "Sorghum": "71.33 $",
    "Soybean": "88.31 $",
    "Cassava": "316.57 $",
    "Yams": "1244.71 $",
    "Sweet potatoes": "278.97 $",
    "Plantains and others": "325.10 $"
}

# Utilisation d'onglets
tab1, tab2 = st.tabs(["🔮 Prédiction de Rendement", "💡 Recommandation de Culture"])

# --- ONGLET 1 : PRÉDICTION ---
with tab1:
    st.header("Estimer le rendement d'une culture précise")

    # 2 colonnes : gauche formulaire / droite encart
    left_col, right_col = st.columns([3, 1])

    with left_col:
        with st.form("form_prediction"):
            col1, col2 = st.columns(2)

            with col1:
                item = st.selectbox(
                    "Culture",
                    ['Maize', 'Potatoes', 'Rice', 'Wheat', 'Sorghum', 'Soybean',
                     'Cassava', 'Yams', 'Sweet potatoes', 'Plantains and others'],
                    key="item_p"
                )
                region = st.selectbox(
                    "Région",
                    ['Southern Asia', 'Southern Europe', 'Northern Africa', 'Polynesia',
                     'Sub-Saharan Africa', 'Latin America and the Caribbean',
                     'Western Asia', 'Australia and New Zealand', 'Western Europe',
                     'Eastern Europe', 'Northern America', 'South-eastern Asia', 'Eastern Asia',
                     'Northern Europe', 'Melanesia', 'Micronesia', 'Central Asia'],
                    key="reg_p"
                )

            with col2:
                avg_temp = st.slider("Température Moyenne (°C)", -5.0, 45.0, 15.0, key="temp_p")
                rainfall = st.slider("Précipitations (mm)", min_value=0, value=3500, key="rain_p")
                pesticides = st.slider("Pesticides (tonnes)", min_value=0.0, value=1850000.0, key="pest_p")

            submit_p = st.form_submit_button("Lancer la prédiction")

    with right_col:
        st.markdown("### Taux d'erreur en %")
        st.info(infos_mape.get(st.session_state.get("item_p", "Maize"), "Aucune info disponible."))
        st.markdown("### Perte économique en dollars (par tonne par hectar)")
        st.info(infos_economic.get(st.session_state.get("item_p", "Maize"), "Aucune info disponible."))

    if submit_p:
        payload = {
            "region": region,
            "item": item,
            "avg_temp": avg_temp,
            "rainfall_mm": rainfall,
            "pesticides_tonnes": pesticides
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

                # Préparation des données pour le graphique
                df_reco = pd.DataFrame(data['ranking'])
                df_reco = df_reco.set_index('crop')
                df_reco = df_reco.sort_values(by='predicted_yield', ascending=False)

                st.success(f"🏆 La meilleure culture est : **{data['best_crop']}**")
                # Afficher le classement
                st.write("Classement complet :")
                st.table(data['ranking'])

                # Affichage du graphique 
                st.subheader("📊 Comparaison des rendements (kg/ha)")
                st.bar_chart(df_reco)

        except Exception as e:
            st.error(f"Erreur : {e}")

