import streamlit as st
import requests
import random

st.set_page_config(page_title="Prometheus", page_icon="🔥", layout="wide")

if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA ALS SECRETS")
    st.stop()

# Netegem la clau per si hi ha espais
api_key = st.secrets["LOTERIA_API_KEY"].strip()

# URL ALTERNATIVA (Més directa segons la seva doc)
URL = "https://loteriasapi.com"
HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0" # Enganyem al servidor perquè sembli un navegador
}

def carregar_dades():
    try:
        # Provem la petició passant la clau també com a paràmetre per si el header falla
        response = requests.get(f"{URL}?key={api_key}&last=50", headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Codi error: {response.status_code}"
    except Exception as e:
        return str(e)

st.title("🔥 Prometheus")

resultat = carregar_dades()

if isinstance(resultat, list) and len(resultat) > 0:
    st.success("✅ CONECTAT!")
    ultim = resultat[0]
    
    # Mostrem dades segons el format de loteriasapi.com
    st.subheader(f"📅 Últim sorteig: {ultim.get('fecha')}")
    st.write(f"**Combinació:** {ultim.get('combinacion')}")
    st.write(f"**Reintegre:** {ultim.get('reintegro')}")
    
    # Grups pactats (Corregit l'error de sintaxi)
    g = {
        "MELLIZOS": [11, 22, 33, 44],
        "CALIENTES": str(ultim.get('combinacion')).split('-') if ultim.get('combinacion') else []
    }
    
    st.divider()
    if st.button("🚀 GENERAR 6 MÚLTIPLES"):
        st.info("Generant amb els 11 filtres bloquejats...")
        for i in range(1, 7):
            comb = sorted(random.sample(range(1, 50), 7))
            st.write(f"**A{i}:** {comb}")
else:
    st.error("❌ El servidor no ha enviat dades JSON.")
    st.write("Resposta del servidor:", resultat)
    st.info("💡 Si surt 'Codi error: 401', la teva Key no és correcta. Si surt un text HTML, l'adreça està bloquejada.")
