import streamlit as st
import requests

st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

# Verificació de la clau als Secrets
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ No s'ha trobat la clau 'LOTERIA_API_KEY' als Secrets de Streamlit.")
    st.stop()

api_key = st.secrets["LOTERIA_API_KEY"]

# --- CONFIGURACIÓ SEGONS LA TEVA DOCUMENTACIÓ ---
# L'adreça real de l'API és api.loteriasapi.com (amb el prefix 'api.')
URL_API = "https://loteriasapi.com"

HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

@st.cache_data(ttl=3600)
def carregar_dades_reals():
    try:
        # Demanem els últims 50 sorteigs per als filtres
        response = requests.get(f"{URL_API}?limit=50", headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            json_data = response.json()
            # Les dades solen venir dins d'una llista anomenada 'data'
            return json_data.get('data', [])
        else:
            st.error(f"⚠️ Error del servidor: Codi {response.status_code}")
            if response.status_code == 401:
                st.info("El codi 401 indica que l'API Key no és vàlida o està mal escrita als Secrets.")
            return None
    except Exception as e:
        st.error(f"❌ Error de connexió: {str(e)}")
        return None

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

dades = carregar_dades_reals()

if dades:
    st.success(f"✅ CONECTAT! Hem rebut els últims {len(dades)} sorteigs.")
    
    st.subheader("📅 Últims 4 Sorteigs")
    cols = st.columns(4)
    for i in range(min(4, len(dades))):
        s = dades[i]
        with cols[i]:
            # Adaptem els noms dels camps segons la resposta de l'API
            data_s = s.get('drawDate', 'N/A')
            # Si combination és una llista [1,2,3...], la convertim a text
            nums = s.get('combination', [])
            num_text = "-".join(map(str, nums))
            # El reintegre sol estar a resultData o directament
            reint = s.get('resultData', {}).get('reintegro', '?')
            
            st.metric(label=data_s, value=f"R: {reint}")
            st.write(f"**{num_text}**")
    
    st.divider()
    st.button("🚀 GENERAR COMBINACIONS (MOTOR PACTAT)")
else:
    st.warning("🔄 Intentant connectar amb el servidor de dades...")
