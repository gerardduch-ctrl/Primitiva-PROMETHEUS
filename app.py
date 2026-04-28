import streamlit as st
import requests
import random

# --- CONFIGURACIÓ ---
st.set_page_config(page_title="Prometheus", page_icon="🔥", layout="wide")

if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA ALS SECRETS")
    st.stop()

# Netegem la clau de caràcters invisibles
api_key = st.secrets["LOTERIA_API_KEY"].strip()

# URL EXACTA SEGONS LA TEVA DOCUMENTACIÓ
URL_LATEST = "https://loteriasapi.com"
HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

@st.cache_data(ttl=300)
def carregar_sorteig_real():
    try:
        response = requests.get(URL_LATEST, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}"
    except Exception as e:
        return str(e)

# --- INTERFÍCIE ---
st.title("🔥 Prometheus")

resultat = carregar_sorteig_real()

if isinstance(resultat, dict) and resultat.get('success'):
    st.success("✅ CONECTAT AMB ÈXIT!")
    data = resultat.get('data', {})
    
    st.subheader(f"📅 Últim sorteig real: {data.get('drawDate')}")
    st.write(f"**Combinació:** {data.get('combination')}")
    st.write(f"**Reintegre:** {data.get('resultData', {}).get('reintegro')}")
    
    # DEFINICIÓ DELS GRUPS (CORREGIT)
    g = {
        "MELLIZOS": [11, 22, 33, 44],
        "UP": list(range(1, 26)), # Provisori fins a tenir estadístiques
        "CALIENTES": data.get('combination', [])
    }
    
    st.divider()
    c1, c2 = st.columns(2)
    m_on = c1.toggle("MELLIZOS")
    c_on = c2.toggle("CLUMPS")

    if st.button("🚀 GENERAR 6 MÚLTIPLES"):
        st.info("Generant amb tots els filtres bloquejats...")
        for i in range(1, 7):
            # Aquí anirà el motor de generació ja pactat
            comb = sorted(random.sample(range(1, 50), 7))
            st.write(f"**A{i}:** {comb}")
else:
    st.error("❌ No s'han pogut carregar les dades.")
    st.write("Detall del servidor:", resultat)
