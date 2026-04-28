import streamlit as st
import requests

st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

# 1. Verificació de la clau als Secrets
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ Falta la clau 'LOTERIA_API_KEY' als Secrets de Streamlit.")
    st.stop()

api_key = st.secrets["LOTERIA_API_KEY"]

# 2. Configuració de la petició
# L'adreça segons documentació oficial
URL = "https://loteriasapi.com"

# Afegim headers per "forçar" el format JSON
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def carregar_dades_final():
    # Enviem la key i el límit de 100 sorteigs per als filtres
    params = {"key": api_key, "last": 100}
    try:
        response = requests.get(URL, params=params, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            # Verifiquem si és realment un JSON abans de carregar-lo
            try:
                return response.json()
            except:
                st.error("El servidor ha respost, però el format no és correcte.")
                return None
        else:
            st.error(f"Error {response.status_code}: {response.reason}")
            return None
    except Exception as e:
        st.error(f"Error de xarxa: {str(e)}")
        return None

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

dades = carregar_dades_final()

if dades and isinstance(dades, list):
    st.success(f"✅ CONECTAT! Detectats {len(dades)} sorteigs.")
    
    st.subheader("📅 Últims 4 Sorteigs")
    cols = st.columns(4)
    for i in range(min(4, len(dades))):
        s = dades[i]
        with cols[i]:
            # En aquesta API els camps solen ser 'fecha', 'combinacion' i 'reintegro'
            data_s = s.get('fecha', 'N/A')
            comb = s.get('combinacion', '?-?-?-?-?-?')
            reint = s.get('reintegro', '?')
            st.metric(label=data_s, value=f"R: {reint}")
            st.write(f"**{comb}**")
    
    st.divider()
    st.info("💡 Connexió estable. Llest per activar el motor de càlcul.")
else:
    st.warning("🔄 Verificant dades... Revisa que la Key sigui correcta.")
