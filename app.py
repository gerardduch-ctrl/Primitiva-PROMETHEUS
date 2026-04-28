import streamlit as st
import requests

st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

# Verificació de la clau als Secrets
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ No s'ha trobat la clau 'LOTERIA_API_KEY' als Secrets.")
    st.stop()

api_key = st.secrets["LOTERIA_API_KEY"]

# --- CONFIGURACIÓ DE L'URL ---
URL = "https://loteriasapi.com"
HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

@st.cache_data(ttl=3600)
def carregar_dades_netes():
    try:
        response = requests.get(f"{URL}?limit=10", headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            try:
                return response.json()
            except:
                st.error("El servidor ha respost OK, però NO és un JSON.")
                st.text_area("Contingut rebut:", response.text[:500])
                return None
        else:
            st.error(f"Error {response.status_code}: {response.reason}")
            return None
    except Exception as e:
        st.error(f"Error de xarxa: {str(e)}")
        return None

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

respost = carregar_dades_netes()

if respost and 'data' in respost:
    dades = respost['data']
    st.success(f"✅ Dades rebudes! {len(dades)} sorteigs detectats.")
    
    cols = st.columns(4)
    for i in range(min(4, len(dades))):
        s = dades[i]
        with cols[i]:
            data_s = s.get('drawDate', 'N/A')
            nums = "-".join(map(str, s.get('combination', [])))
            reint = s.get('resultData', {}).get('reintegro', '?')
            st.metric(label=data_s, value=f"R: {reint}")
            st.write(f"**{nums}**")
    
    st.divider()
    st.button("🚀 GENERAR SEGONS PACTE")
else:
    st.info("🔄 Verificant dades... Si veus un error de format, revisarem el 'slug' de l'URL.")
