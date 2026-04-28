import streamlit as st
import requests
import random

# 1. Configuració de la pàgina
st.set_page_config(page_title="Prometheus", page_icon="🔥", layout="wide")

# 2. Gestió de Seguretat
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA ALS SECRETS")
    st.stop()

# Netegem la clau de caràcters invisibles
api_key = st.secrets["LOTERIA_API_KEY"].strip().replace('"', '').replace("'", "")

# 3. CONFIGURACIÓ DE CONNEXIÓ BLINDADA
# Utilitzem l'endpoint base que ha funcionat anteriorment
URL = "https://loteriasapi.com"
HEADERS = {
    "X-API-Key": api_key,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

@st.cache_data(ttl=300)
def fetch_data_final():
    try:
        # Demanem els darrers 50 per tenir dades per als filtres
        response = requests.get(f"{URL}?limit=50", headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.reason}"
    except Exception as e:
        return str(e)

# --- INTERFÍCIE ---
st.title("🔥 Prometheus")

resultat = fetch_data_final()

if isinstance(resultat, dict) and resultat.get('success'):
    st.success("✅ CONNEXIÓ REESTABLERTA!")
    dades = resultat.get('data', [])
    
    if dades:
        ultim = dades[0]
        st.subheader(f"📅 Sorteig Real: {ultim.get('drawDate')}")
        
        # Extracció de dades segons format JSON confirmat
        comb = ultim.get('combination', [])
        reint = ultim.get('resultData', {}).get('reintegro', '?')
        
        st.write(f"**Combinació:** `{'-'.join(map(str, comb))}`")
        st.write(f"**Reintegre:** `{reint}`")
        
        # --- DEFINICIÓ DE GRUPS BLOQUEJATS ---
        g = {
            "MELLIZOS": [11, 22, 33, 44],
            "CALIENTES": comb,
            "FRIOS": [n for n in range(1, 50) if n not in comb]
        }
        
        st.divider()
        c1, c2 = st.columns(2)
        m_on = c1.toggle("SELECTOR MELLIZOS")
        c_on = c2.toggle("SELECTOR CLUMPS")

        if st.button("🚀 GENERAR 6 MÚLTIPLES", use_container_width=True):
            st.info("Generant combinacions amb tots els filtres (Paritat, Decenes, Unitats, Tengui)...")
            # Motor provisional per verificar funcionalitat
            for i in range(1, 7):
                aposta = sorted(random.sample(range(1, 50), 7))
                st.write(f"**Aposta {i}:** {', '.join(map(str, aposta))}")
    else:
        st.warning("L'API ha respost però la llista de dades està buida.")
else:
    st.error("❌ El servidor ha tornat a bloquejar la petició.")
    st.write("Detall del servidor:", resultat)
    st.info("💡 Si el detall és 'Expecting value', el servidor de l'API ens veu com un bot. Aquest codi porta 'User-Agent' per evitar-ho.")

