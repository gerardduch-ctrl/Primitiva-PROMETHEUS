import streamlit as st
import requests

st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

# 1. Verificació i NETEJA de la clau
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ Falta la clau 'LOTERIA_API_KEY' als Secrets de Streamlit.")
    st.stop()

# Netegem la clau per si hi ha espais o caràcters invisibles
api_key = st.secrets["LOTERIA_API_KEY"].strip()

# 2. CONFIGURACIÓ DE L'URL (CORREGIDA)
# Fem servir la versió més directa que coneixem de l'API
URL_API = "https://loteriasapi.com"
HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

def carregar_dades():
    try:
        # Fem la petició corregint el format de l'URL
        response = requests.get(f"{URL_API}?limit=50", headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            json_data = response.json()
            # L'API sol retornar una llista dins de 'data'
            return json_data.get('data', [])
        else:
            st.error(f"⚠️ Error {response.status_code}: {response.reason}")
            if response.status_code == 401:
                st.info("Revisa la teva API Key als Secrets; el servidor diu que no és vàlida.")
            return None
    except Exception as e:
        st.error(f"❌ Error de connexió: {str(e)}")
        return None

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

dades = carregar_dades()

if dades:
    st.success(f"✅ CONECTAT! Dades rebudes correctament.")
    
    st.subheader("📅 Últims 4 Sorteigs")
    cols = st.columns(4)
    
    for i in range(min(4, len(dades))):
        s = dades[i]
        with cols[i]:
            # Adaptem drawDate i combination que són els noms de la v1
            data_s = s.get('drawDate', 'N/A')
            comb_llista = s.get('combination', [])
            num_text = "-".join(map(str, comb_llista))
            
            # El reintegre sol estar dins de resultData
            reint = s.get('resultData', {}).get('reintegro', '?')
            
            st.metric(label=data_s, value=f"R: {reint}")
            st.write(f"**{num_text}**")
    
    st.divider()
    st.info("💡 Connexió establerta. Llest per injectar el motor de càlcul.")
else:
    st.warning("🔄 Esperant dades vàlides... Comprova que l'API Key sigui la correcta.")
