import streamlit as st
import requests

st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

# 1. Verificació de la clau
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ Falta la clau 'LOTERIA_API_KEY' als Secrets.")
    st.stop()

api_key = st.secrets["LOTERIA_API_KEY"]

# 2. CONFIGURACIÓ SEGONS MANUAL '://loteriasapi.com'
# Hem d'usar el subdomini 'api.' i la ruta '/v1/results/'
URL = "https://://loteriasapi.com/api/v1/results/primitiva"
HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

def carregar_dades_v1():
    try:
        # Demanem l'històric (limit=50)
        response = requests.get(f"{URL}?limit=50", headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            json_data = response.json()
            # Les dades en la v1 solen estar dins de 'data' o 'results'
            if 'data' in json_data:
                return json_data['data']
            return json_data
        else:
            st.error(f"Error {response.status_code}: {response.reason}")
            return None
    except Exception as e:
        st.error(f"Error de connexió: {str(e)}")
        return None

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

dades = carregar_dades_v1()

if dades:
    st.success("✅ CONECTAT! Dades rebudes de l'API v1.")
    
    st.subheader("📅 Últims 4 Sorteigs")
    cols = st.columns(4)
    
    # Adaptem els noms dels camps al format de la v1 (drawDate i combination)
    for i in range(min(4, len(dades))):
        s = dades[i]
        with cols[i]:
            data_s = s.get('drawDate', s.get('fecha', 'N/A'))
            comb = s.get('combination', s.get('combinacion', []))
            # Si és una llista [1,2,3], la convertim a text
            if isinstance(comb, list):
                num_text = "-".join(map(str, comb))
            else:
                num_text = str(comb)
            
            # El reintegre sol estar dins de resultData en la v1
            res_data = s.get('resultData', {})
            reint = res_data.get('reintegro', s.get('reintegro', '?'))
            
            st.metric(label=data_s, value=f"R: {reint}")
            st.write(f"**{num_text}**")
    
    st.divider()
    st.info("💡 Connexió OK. Motor de filtres a punt per ser activat.")
else:
    st.warning("🔄 Verificant protocol de dades... Si surt error 401, revisa la Key.")
