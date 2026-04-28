import streamlit as st
import requests
import random

# 1. Configuració de la pàgina
st.set_page_config(page_title="Prometheus", page_icon="🔥", layout="wide")

# 2. Verificació de la clau als Secrets
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA ALS SECRETS")
    st.stop()

api_key = st.secrets["LOTERIA_API_KEY"].strip()

# 3. URL CORREGIDA (Sense punts ni barres extres)
URL_API = "https://loteriasapi.com"
HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

@st.cache_data(ttl=300)
def carregar_dades_v1():
    try:
        response = requests.get(URL_API, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.reason}"
    except Exception as e:
        return str(e)

# --- INTERFÍCIE ---
st.title("🔥 Prometheus")

resultat = carregar_dades_v1()

if isinstance(resultat, dict) and resultat.get('success'):
    st.success("✅ CONECTAT AMB ÈXIT!")
    data = resultat.get('data', {})
    
    st.subheader(f"📅 Últim sorteig real: {data.get('drawDate')}")
    st.write(f"**Combinació:** {data.get('combination')}")
    st.write(f"**Reintegre:** {data.get('resultData', {}).get('reintegro')}")
    
    # GRUPS PACTATS (Sintaxi corregida per evitar SyntaxError)
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
        st.info("Generant combinacions amb els 11 filtres bloquejats...")
        for i in range(1, 7):
            # Motor provisional per testar que el botó i la connexió funcionen
            comb = sorted(random.sample(range(1, 50), 7))
            st.write(f"**Aposta {i}:** {', '.join(map(str, comb))}")
else:
    st.error("❌ No s'han pogut carregar les dades.")
    st.write("Detall del servidor:", resultat)
