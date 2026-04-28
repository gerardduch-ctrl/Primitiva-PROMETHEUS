"
headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

@st.cache_data(ttl=3600)
def obtenir_tres_ultims():
    try:
        # Demanem només els últims 3 resultats
        response = requests.get(f"{url}?limit=3", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get('data', [])
        return None
    except Exception:
        return None

st.title("🎰 Últims 3 Resultats")

dades = obtenir_tres_ultims()

if dades:
    for i, sorteig in enumerate(dades):
        data = sorteig.get('drawDate', 'Data no disponible')
        nums = "-".join(map(str, sorteig.get('combination', [])))
        reint = sorteig.get('resultData', {}).get('reintegro', '?')
        
        # Mostrem cada resultat en una targeta visual
        with st.container():
            st.subheader(f"Sorteig del {data}")
            st.markdown(f"### `{nums}`  |  **R: {reint}**")
            if i < 2: st.divider() # Separa els resultats menys l'últim
else:
    st.warning("🔄 No s'han pogut carregar els resultats. Revisa la teva connexió o API Key.")
