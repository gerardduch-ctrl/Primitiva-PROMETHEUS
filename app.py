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

# --- CONFIGURACIÓ API SEGONS DOCUMENTACIÓ ---
URL_API = "https://loteriasapi.com"
# Afegim 100 sorteigs per tenir prou dades pels teus filtres
URL_HISTORIC = "https://loteriasapi.com"

HEADERS = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

@st.cache_data(ttl=3600)
def carregar_dades():
    try:
        # Fem la petició a l'històric per tenir dades de criba
        response = requests.get(URL_HISTORIC, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            json_data = response.json()
            # Segons el teu exemple, les dades solen anar dins de 'data'
            return json_data.get('data', [])
        else:
            st.error(f"Error d'autenticació: {response.status_code}. Revisa la teva API Key.")
            return None
    except Exception as e:
        st.error(f"Error de xarxa: {e}")
        return None

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

dades = carregar_dades()

if dades:
    st.success("✅ Connexió establerta correctament amb X-API-Key!")
    
    st.subheader("📅 Últims 4 sorteigs detectats")
    cols = st.columns(4)
    
    # Mostrem els últims 4 de la llista
    for i in range(min(4, len(dades))):
        s = dades[i]
        with cols[i]:
            data_sorteig = s.get('drawDate', 'Desconeguda')
            comb_llista = s.get('combination', [])
            reintegre = s.get('resultData', {}).get('reintegro', '?')
            
            # Convertim la llista [1, 2, 3...] en text "1-2-3..."
            comb_text = "-".join(map(str, comb_llista))
            
            st.metric(label=data_sorteig, value=f"R: {reintegre}")
            st.write(f"**{comb_text}**")
            st.caption("✅ Grups analitzats")

    st.divider()
    
    # Selectors pactats
    c1, c2 = st.columns(2)
    with c1:
        st.toggle("SELECTOR MELLIZOS", key="mellizos")
    with c2:
        st.toggle("SELECTOR CLUMPS", key="clumps")

    if st.button("🚀 GENERAR 6 COMBINACIONS MÚLTIPLES"):
        st.warning("Motor de criba en preparació: Ara ja podem processar les dades reals!")
else:
    st.info("🔄 Connectant amb el servidor de loteries... Si triga massa, verifica que l'API Key als Secrets sigui l'original.")
