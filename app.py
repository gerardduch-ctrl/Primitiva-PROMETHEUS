import streamlit as st
import requests

st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA")
    st.stop()

api_key = st.secrets["LOTERIA_API_KEY"].strip()
headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

# Segons el manual, provem la ruta de l'últim resultat primer
URL_PROVA = "https://loteriasapi.com"

@st.cache_data(ttl=600)
def carregar_test():
    try:
        response = requests.get(URL_PROVA, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return str(e)

st.title("🔥 Prometheus: Connexió Directa")

resultat = carregar_test()

if isinstance(resultat, dict) and resultat.get('success'):
    st.success("✅ CONECTAT! L'API ha respost correctament.")
    data = resultat.get('data', {})
    
    # Mostrem les dades tal com venen de l'API per confirmar noms
    st.write("### Últim sorteig detectat:")
    st.write(f"**Data:** {data.get('drawDate')}")
    st.write(f"**Combinació:** {data.get('combination')}")
    st.write(f"**Reintegre:** {data.get('resultData', {}).get('reintegro')}")
    
    st.divider()
    st.info("💡 Ara que veiem la ruta bona, puc escriure el motor amb els 11 filtres.")
else:
    st.error("❌ La ruta '/primitiva/latest' no ha funcionat.")
    st.write("Resposta del servidor:", resultat)
    st.info("Provant de localitzar el nom correcte del joc...")
