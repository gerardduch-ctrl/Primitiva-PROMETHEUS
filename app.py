import streamlit as st
import requests
import random

# --- CONFIGURACIÓ ---
st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥", layout="wide")

if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA ALS SECRETS")
    st.stop()

# Netegem la clau per si hi ha caràcters invisibles
API_KEY = st.secrets["LOTERIA_API_KEY"].strip()

# CONFIGURACIÓ SEGONS MANUAL OFICIAL
URL_BASE = "https://loteriasapi.com"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def carregar_dades_robust():
    try:
        # Provem de carregar els últims 50 sorteigs
        response = requests.get(f"{URL_BASE}/results/primitiva?limit=50", headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            try:
                return response.json().get('data', [])
            except:
                st.error("⚠️ El servidor ha respost OK, però no és un JSON.")
                st.text_area("Contingut del servidor (Debug):", response.text[:500])
                return []
        else:
            st.error(f"⚠️ Error {response.status_code}: {response.reason}")
            return []
    except Exception as e:
        st.error(f"❌ Error de xarxa: {str(e)}")
        return []

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

dades = carregar_dades_robust()

if dades:
    st.success(f"✅ Connexió amb èxit! Detectats {len(dades)} sorteigs.")
    
    st.subheader("📅 Comprovació de dades reals")
    cols = st.columns(4)
    for i in range(min(4, len(dades))):
        s = dades[i]
        with cols[i]:
            data_s = s.get('drawDate', 'Data NP')
            num_llista = s.get('combination', [])
            num_text = "-".join(map(str, num_llista))
            reint = s.get('resultData', {}).get('reintegro', '?')
            
            st.metric(label=data_s, value=f"R: {reint}")
            st.write(f"**{num_text}**")
            
    st.divider()
    if st.button("🚀 GENERAR SEGONS PACTE"):
        st.info("Calculant grups i aplicant els 11 filtres bloquejats...")
else:
    st.info("🔄 Verificant dades... Revisa que la Key als Secrets sigui l'original de Loteria API.")
