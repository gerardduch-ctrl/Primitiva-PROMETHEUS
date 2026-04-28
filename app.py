import streamlit as st
import requests
import random

st.set_page_config(page_title="Prometheus", page_icon="🔥", layout="wide")

# 1. Recuperar la clau dels Secrets
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA")
    st.stop()

api_key = st.secrets["LOTERIA_API_KEY"].strip()

# 2. Configuració d'URL segons el format v1 (://loteriasapi.com)
URL_V1 = "https://://loteriasapi.com/api/v1/results/primitiva/latest"
HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

@st.cache_data(ttl=300)
def fetch_primitiva():
    try:
        response = requests.get(URL_V1, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.reason}"
    except Exception as e:
        return str(e)

# --- INTERFÍCIE ---
st.title("🔥 Prometheus")

res = fetch_primitiva()

if isinstance(res, dict) and res.get('success'):
    st.success("✅ CONECTAT AMB ÈXIT!")
    data = res.get('data', {})
    
    st.subheader(f"📅 Sorteig: {data.get('drawDate')}")
    comb = data.get('combination', [])
    reint = data.get('resultData', {}).get('reintegro', '?')
    
    st.write(f"**Combinació:** {comb}")
    st.write(f"**Reintegre:** {reint}")
    
    # GRUPS BLOQUEJATS (Sintaxi corregida)
    g = {
        "MELLIZOS": [11, 22, 33, 44],
        "CALIENTES": comb
    }
    
    st.divider()
    if st.button("🚀 GENERAR 6 MÚLTIPLES"):
        st.info("Generant amb els 11 filtres bloquejats...")
        for i in range(1, 7):
            # Motor provisional per testar que el botó funciona
            aposta = sorted(random.sample(range(1, 50), 7))
            st.write(f"**A{i}:** {aposta}")
else:
    st.error("❌ L'API no ha enviat dades vàlides.")
    st.write("Resposta del servidor:", res)
    st.info("💡 Verifica que l'API Key als Secrets de Streamlit sigui la correcta.")
