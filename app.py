import streamlit as st
import requests

# 1. Configuració de la pàgina
st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

# 2. Gestió de la Key (Secrets de Streamlit)
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ Falta la clau LOTERIA_API_KEY als Secrets.")
    st.stop()

# Netegem la clau per si hi ha espais o caràcters invisibles
api_key = st.secrets["LOTERIA_API_KEY"].strip()

# 3. Configuració de l'API (Segons el manual que has passat)
URL_LATEST = "https://loteriasapi.com"
HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

@st.cache_data(ttl=300)
def carregar_ultim_resultat():
    try:
        response = requests.get(URL_LATEST, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"⚠️ Error {response.status_code}: {response.reason}")
            return None
    except Exception as e:
        st.error(f"❌ Error de xarxa: {str(e)}")
        return None

# --- INTERFÍCIE VISUAL ---
st.title("🔥 Prometheus: La Primitiva")

res = carregar_ultim_resultat()

if res and res.get('success'):
    data = res.get('data', {})
    st.success("✅ Connexió establerta! Dades rebudes.")
    
    # Mostrem l'últim sorteig segons el format JSON que has passat
    st.subheader(f"📅 Sorteig del {data.get('drawDate')}")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        nums = "-".join(map(str, data.get('combination', [])))
        st.markdown(f"### Combinació: `{nums}`")
    with col2:
        reint = data.get('resultData', {}).get('reintegro', '?')
        st.metric("Reintegre", reint)
        
    st.divider()
    st.info("💡 L'API ja respon. Estic llest per programar el motor de 6 combinacions amb els 11 filtres.")
else:
    st.warning("🔄 Esperant dades... Revisa que la Key sigui l'original del teu panell.")
