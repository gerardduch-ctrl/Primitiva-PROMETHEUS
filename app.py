import streamlit as st
import requests

# 1. Configuració de la pantalla
st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

# 2. Verificació de la clau (ha d'estar als Secrets de Streamlit)
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ No s'ha trobat la clau LOTERIA_API_KEY als Secrets.")
    st.stop()

api_key = st.secrets["LOTERIA_API_KEY"]

# 3. Configuració de la connexió
# Hem d'usar l'URL de la API v1 que hem pactat
URL_API = "https://loteriasapi.com"
HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

@st.cache_data(ttl=3600)
def carregar_dades():
    try:
        # Demanem els últims 50 sorteigs per poder analitzar els teus filtres
        response = requests.get(f"{URL_API}?limit=50", headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            st.error(f"⚠️ Error del servidor: Codi {response.status_code}")
            return None
    except Exception as e:
        st.error(f"❌ Error de connexió: {str(e)}")
        return None

# 4. Interfície Visual
st.title("🔥 Prometheus: La Primitiva")

dades = carregar_dades()

if dades:
    st.success("✅ Connexió establerta! Ja veiem les dades.")
    
    st.subheader("📅 Últims 4 Sorteigs")
    cols = st.columns(4)
    for i in range(min(4, len(dades))):
        s = dades[i]
        with cols[i]:
            data_s = s.get('drawDate', 'N/A')
            nums = "-".join(map(str, s.get('combination', [])))
            reint = s.get('resultData', {}).get('reintegro', '?')
            st.metric(label=data_s, value=f"R: {reint}")
            st.write(f"**{nums}**")
else:
    st.info("🔄 Esperant dades reals... Verifica que hagis posat la API Key als Secrets de Streamlit.")
