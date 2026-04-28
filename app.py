import streamlit as st
import requests

# 1. Configuració de la pàgina
st.set_page_config(page_title="Últims 3 Sorteigs", page_icon="🎰")

# 2. Gestió de la Key (Secrets de Streamlit)
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ Falta la clau LOTERIA_API_KEY als Secrets.")
    st.stop()

api_key = st.secrets["LOTERIA_API_KEY"].strip()
url = "https://loteriasapi.com"
headers = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

@st.cache_data(ttl=3600)
def obtenir_dades():
    try:
        # Demanem els últims 3 resultats
        response = requests.get(f"{url}?limit=3", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get('data', [])
        return None
    except Exception:
        return None

# --- INTERFÍCIE ---
st.title("🎰 Últims 3 Resultats")

dades = obtenir_dades()

if dades:
    for i, sorteig in enumerate(dades):
        data = sorteig.get('drawDate', 'Data no disponible')
        nums = sorteig.get('combination', [])
        # Convertim la llista de números en text "01-02-03..."
        nums_text = "-".join(map(str, nums))
        reint = sorteig.get('resultData', {}).get('reintegro', '?')
        
        with st.container():
            st.subheader(f"Sorteig del {data}")
            st.markdown(f"### `{nums_text}`  |  **R: {reint}**")
            if i < 2: st.divider()
else:
    st.warning("🔄 No s'han pogut carregar els resultats. Revisa la Key als Secrets.")
