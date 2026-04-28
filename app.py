import streamlit as st
import requests

st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

# 1. Obtenir i netejar la clau dels Secrets
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA")
    st.stop()

# Netegem la clau per si hi ha espais o caràcters invisibles
api_key = st.secrets["LOTERIA_API_KEY"].strip()

# 2. Configuració exacta segons el teu manual
URL_PRIMITIVA = "https://api.loteriasapi.com/api/v1/results/primitiva"
HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

@st.cache_data(ttl=300)
def carregar_dades_api():
    try:
        # Demanem els darrers resultats (per defecte en portarà uns quants)
        response = requests.get(URL_PRIMITIVA, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.reason}"
    except Exception as e:
        return f"Error de connexió: {str(e)}"

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

resultat = carregar_dades_api()

if isinstance(resultat, dict) and resultat.get('success'):
    st.success("✅ CONECTAT AMB ÈXIT!")
    # L'API retorna una llista dins de 'data'
    dades = resultat.get('data', [])
    
    if dades:
        ultim = dades[0] # Agafem el més recent
        st.subheader(f"📅 Últim sorteig: {ultim.get('drawDate')}")
        st.write(f"**Combinació:** {ultim.get('combination')}")
        st.write(f"**Reintegre:** {ultim.get('resultData', {}).get('reintegro')}")
        
        st.divider()
        st.info("💡 Connexió establerta. Llest per injectar el motor amb els 11 filtres.")
    else:
        st.warning("No s'han trobat sorteigs a la resposta.")
else:
    st.error("❌ El servidor encara no envia dades vàlides.")
    st.write("Detall del servidor:", resultat)
