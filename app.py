import streamlit as st
import requests

st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

# Accés segur a la clau
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ Falta la clau LOTERIA_API_KEY als Secrets.")
    st.stop()

api_key = st.secrets["LOTERIA_API_KEY"]

# --- PROVA DE DUES RUTES POSSIBLES ---
# Provem la ruta estàndard de resultats per a la Primitiva
URL_V1 = "https://loteriasapi.com"

HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

@st.cache_data(ttl=3600)
def carregar_dades_diagnosi():
    try:
        # Intentem obtenir els últims 50 resultats
        response = requests.get(f"{URL_V1}?limit=50", headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            st.error(f"Error del servidor: Codi {response.status_code}")
            # Si dona 404, potser el slug 'primitiva' és diferent
            return None
    except Exception as e:
        st.error(f"Error de connexió: {str(e)}")
        return None

st.title("🔥 Prometheus: La Primitiva")

dades = carregar_dades_diagnosi()

if dades:
    st.success(f"✅ Connectat! Detectats {len(dades)} sorteigs.")
    
    # Mostrem el primer sorteig per veure com són les dades per dins
    ultim = dades[0]
    st.write("### Últim sorteig real:")
    st.json(ultim) # Això ens ensenyarà els noms reals dels camps (drawDate, combination, etc.)
    
    st.divider()
    if st.button("🚀 TOT A PUNT: GENERAR MOTOR DE CRIBA"):
        st.balloons()
        st.info("Perfecte! Ara que veiem les dades, ja puc escriure els filtres definitius.")
else:
    st.warning("⚠️ No s'han rebut dades. Verifica que el 'slug' de la loteria sigui 'primitiva' o que la clau estigui activa.")
