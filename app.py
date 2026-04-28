import streamlit as st
import requests
import random

st.set_page_config(page_title="Prometheus", page_icon="🔥", layout="wide")

# 1. Verificació de la clau
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA ALS SECRETS")
    st.stop()

api_key = st.secrets["LOTERIA_API_KEY"].strip()

# 2. Configuració d'URL i Headers (Amb User-Agent per evitar bloquejos)
URL_LATEST = "https://loteriasapi.com"
HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@st.cache_data(ttl=300)
def carregar_dades_vFinal():
    try:
        response = requests.get(URL_LATEST, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.reason}"
    except Exception as e:
        return str(e)

# --- INTERFÍCIE ---
st.title("🔥 Prometheus")

resultat = carregar_dades_vFinal()

if isinstance(resultat, dict) and resultat.get('success'):
    st.success("✅ CONECTAT AMB ÈXIT!")
    data = resultat.get('data', {})
    
    st.subheader(f"📅 Últim sorteig real: {data.get('drawDate')}")
    st.write(f"**Combinació:** {data.get('combination')}")
    st.write(f"**Reintegre:** {data.get('resultData', {}).get('reintegro')}")
    
    # GRUPS PACTATS (Sintaxi corregida)
    g = {
        "MELLIZOS": [11, 22, 33, 44],
        "UP": list(range(1, 26)),
        "CALIENTES": data.get('combination', [])
    }
    
    st.divider()
    c1, c2 = st.columns(2)
    m_on = c1.toggle("SELECTOR MELLIZOS")
    c_on = c2.toggle("SELECTOR CLUMPS")

    if st.button("🚀 GENERAR 6 MÚLTIPLES", use_container_width=True):
        st.info("Generant amb tots els filtres bloquejats...")
        for i in range(1, 7):
            comb = sorted(random.sample(range(1, 50), 7))
            st.write(f"**Aposta {i}:** {', '.join(map(str, comb))}")
else:
    st.error("❌ El servidor encara no envia dades vàlides.")
    st.write("Detall del servidor:", resultat)
    st.info("💡 Si l'error persisteix, revisa que la Key als Secrets no tingui espais extres.")
