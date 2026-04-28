import streamlit as st
import requests

st.set_page_config(page_title="Prometheus Diagnòstic", page_icon="🔍")

if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA ALS SECRETS")
    st.stop()

api_key = st.secrets["LOTERIA_API_KEY"]
headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

st.title("🔍 Diagnòstic de Connexió")

# Provarem les dues rutes més comunes per a la Primitiva
rutes = [
    "https://loteriasapi.com",
    "https://loteriasapi.com"
]

for url in rutes:
    st.write(f"Provant ruta: `{url}`...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        st.write(f"Codi de resposta: `{response.status_code}`")
        
        if response.status_code == 200:
            st.success(f"✅ CONECTAT A: {url}")
            dades = response.json()
            st.write("Dades rebudes correctament!")
            st.json(dades.get('data', [])[:1]) # Mostra només el primer sorteig
            st.stop() # Si una funciona, parem aquí
        else:
            st.warning(f"Ruta fallida amb codi {response.status_code}")
            st.write("Resposta del servidor:", response.text[:100]) # Veurem si és HTML o text
            
    except Exception as e:
        st.error(f"Error en aquesta ruta: {e}")

st.error("❌ Cap de les rutes ha funcionat. Revisa que la API Key sigui l'actual del teu panell.")
