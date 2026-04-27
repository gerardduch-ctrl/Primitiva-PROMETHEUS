import streamlit as st

st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥")

st.title("🔥 Prometheus: La Primitiva")
st.write("Configuració inicial completada.")

# Botons que hem pactat
col1, col2 = st.columns(2)
with col1:
    selector_mellizos = st.toggle("SELECTOR MELLIZOS")
with col2:
    selector_clumps = st.toggle("SELECTOR CLUMPS")

if st.button("GENERAR COMBINACIONS"):
    st.warning("El motor de filtres s'està configurant segons el pacte.")

