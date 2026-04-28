import streamlit as st
import requests

# Configuració de la pàgina
st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

# Accés segur a la clau
try:
    api_key = st.secrets["LOTERIA_API_KEY"]
except:
    st.error("❌ Falta la clau LOTERIA_API_KEY als Secrets.")
    st.stop()

# URL CORREGIDA: Hem tret l'error de format i forcem HTTPS
# L'estructura correcta sol ser: ://loteriasapi.com
URL = f"https://loteriasapi.com"
params = {
    "key": api_key,
    "last": 100
}

@st.cache_data(ttl=3600)
def carregar_dades_reals():
    try:
        response = requests.get(URL, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"L'API ha respost amb error {response.status_code}. Revisa la clau.")
            return None
    except Exception as e:
        st.error(f"Error de xarxa: {e}")
        return None

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

dades = carregar_dades_reals()

if dades:
    st.success("✅ Connexió amb èxit!")
    
    # Visualització ràpida per confirmar
    st.subheader("📅 Últims sorteigs detectats")
    
    # L'API de LoteriasAPI sol tornar una llista de sorteigs
    # Mostrem els 4 primers
    for i in range(min(4, len(dades))):
        s = dades[i]
        # Intentem treure la data i combinació segons el format típic de l'API
        data_sorteig = s.get('fecha', 'Desconeguda')
        combinacio = s.get('combinacion', 'No disponible')
        reintegre = s.get('reintegro', '-')
        
        st.write(f"**{data_sorteig}** — {combinacio} (R:{reintegre})")
    
    st.divider()
    st.info("Pots procedir a generar combinacions un cop vegis les dades a sobre.")
else:
    st.warning("Encara no hi ha dades. Si l'error persisteix, revisa que la clau sigui exactament la que t'ha donat loteriasapi.com.")
