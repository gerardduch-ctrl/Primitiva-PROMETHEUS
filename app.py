import streamlit as st
import requests

st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

# Verificació de la clau
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ No s'ha trobat la clau 'LOTERIA_API_KEY' als Secrets.")
    st.stop()

api_key = st.secrets["LOTERIA_API_KEY"]

# SEGONS LA TEVA DOCUMENTACIÓ:
# L'URL base per a les peticions és aquesta:
URL_BASE = "https://loteriasapi.com"

def carregar_dades_v2():
    # Segons la teva imatge, la key es passa com a paràmetre '?key=...'
    params = {"key": api_key, "last": 50} 
    try:
        response = requests.get(URL_BASE, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.reason}")
            return None
    except Exception as e:
        st.error(f"Error de connexió: {str(e)}")
        return None

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

dades = carregar_dades_v2()

if dades and isinstance(dades, list):
    st.success(f"✅ Dades rebudes! {len(dades)} sorteigs detectats.")
    
    cols = st.columns(4)
    for i in range(min(4, len(dades))):
        s = dades[i]
        with cols[i]:
            # En aquesta API els camps solen ser 'fecha', 'combinacion' i 'reintegro'
            data_s = s.get('fecha', 'N/A')
            nums = s.get('combinacion', '0-0-0-0-0-0')
            reint = s.get('reintegro', '?')
            st.metric(label=data_s, value=f"R: {reint}")
            st.write(f"**{nums}**")
    
    st.divider()
    st.info("💡 Connexió OK. Esperant ordres per injectar els 11 filtres de criba.")
elif dades is not None:
    st.warning("⚠️ La resposta no té el format de llista esperat.")
    st.write(dades)
else:
    st.info("🔄 Verificant credencials...")
