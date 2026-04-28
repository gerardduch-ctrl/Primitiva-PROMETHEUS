import streamlit as st
import requests

st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

# 1. Obtenir la clau dels Secrets
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA")
    st.stop()

api_key = st.secrets["LOTERIA_API_KEY"].strip()

# 2. Configuració de l'URL i Headers (Protocol millorat)
URL = "https://loteriasapi.com"
HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

@st.cache_data(ttl=60)
def carregar_dades_vFinal():
    try:
        # Fem la petició
        response = requests.get(URL, headers=HEADERS, timeout=15)
        
        # Si ens dona 200 (OK), intentem llegir el JSON
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.reason}"
    except Exception as e:
        return f"Error de xarxa: {str(e)}"

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

resultat = carregar_dades_vFinal()

if isinstance(resultat, dict) and resultat.get('success'):
    st.success("✅ CONECTAT AMB ÈXIT!")
    data = resultat.get('data', {})
    
    st.subheader(f"📅 Últim sorteig: {data.get('drawDate')}")
    st.write(f"**Combinació:** {data.get('combination')}")
    st.write(f"**Reintegre:** {data.get('resultData', {}).get('reintegro')}")
    
    st.divider()
    st.info("💡 Connexió OK. Ja podem injectar el motor de càlcul amb els 11 filtres.")
else:
    st.error("❌ El servidor encara no envia dades vàlides.")
    st.write("Detall del servidor:", resultat)
    st.info("Si surt 'Error 401', la clau dels Secrets és incorrecta. Si surt '403', l'API ens està bloquejant.")
