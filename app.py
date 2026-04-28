import streamlit as st
import requests
import pandas as pd

# Configuració de la pàgina
st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

# Intentem obtenir la clau del secret
try:
    API_KEY = st.secrets["LOTERIA_API_KEY"]
except:
    st.error("❌ No s'ha trobat la clau LOTERIA_API_KEY als Secrets de Streamlit.")
    st.stop()

# URL de l'API (loteriasapi.com sol fer servir aquest format)
BASE_URL = f"https://loteriasapi.com{API_KEY}"

@st.cache_data(ttl=3600)
def carregar_dades_reals():
    try:
        # Demanem els últims 100 per tenir prou dades per als filtres FUEGO/HIELO
        response = requests.get(f"{BASE_URL}&last=100")
        if response.status_code == 200:
            dades = response.json()
            # Si l'API retorna una llista directa, la tornem. 
            # Si és un diccionari, busquem la clau on són els resultats.
            if isinstance(dades, list):
                return dades
            elif isinstance(dades, dict):
                # Provem claus comunes on solen anar les dades
                for clau in ['results', 'data', 'sorteos']:
                    if clau in dades: return dades[clau]
            return dades
        else:
            st.error(f"Error de l'API: Codi {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error en la connexió: {e}")
        return None

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

dades = carregar_dades_reals()

if dades and len(dades) > 0:
    st.success("✅ Connexió establerta amb Loterias API")
    
    # 1. VISUALITZACIÓ DELS ÚLTIMS 4 SORTEIGS
    st.subheader("📅 Últims 4 Sortejos Realitzats")
    cols = st.columns(4)
    
    for i in range(min(4, len(dades))):
        sorteig = dades[i]
        with cols[i]:
            # Adaptem segons el nom de les claus que sol fer servir aquesta API
            fecha = sorteig.get('fecha', 'Data NP')
            comb = sorteig.get('combinacion', '0-0-0-0-0-0')
            reint = sorteig.get('reintegro', '?')
            
            st.metric(label=fecha, value=f"R: {reint}")
            st.write(f"**{comb}**")
            st.caption("Anàlisi grups: OK")

    st.divider()
    
    # 2. SELECTORS
    c1, c2 = st.columns(2)
    with c1:
        mellizos_on = st.toggle("SELECTOR MELLIZOS")
    with c2:
        clumps_on = st.toggle("SELECTOR CLUMPS")

    if st.button("🚀 GENERAR 6 COMBINACIONS MÚLTIPLES"):
        st.info("Preparant el motor de criba amb els 11 filtres bloquejats...")
        # Aquí anirà el motor de càlcul final que estem construint
else:
    st.warning("⚠️ No s'han pogut carregar dades. Revisa si l'API Key és activa o si l'URL és correcta.")
    # Debug per a tu:
    if dades is not None:
        st.write("Resposta de l'API per a diagnòstic:", dades)
