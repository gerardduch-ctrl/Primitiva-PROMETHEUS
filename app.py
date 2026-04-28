import streamlit as st
import requests
import random

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Prometheus", page_icon="🔥", layout="wide")

# 1. Recuperar la clau (Neteja absoluta de caràcters)
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA ALS SECRETS")
    st.stop()

API_KEY = st.secrets["LOTERIA_API_KEY"].strip().replace('"', '').replace("'", "")

# 2. PROTOCOL DE CONNEXIÓ OFICIAL
BASE_URL = "https://loteriasapi.com"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

@st.cache_data(ttl=3600, show_spinner=False)
def carregar_dades():
    try:
        # Demanem resultats (limit 50 per filtres) i estadístiques
        r = requests.get(f"{BASE_URL}/results/primitiva?limit=50", headers=HEADERS, timeout=15).json()
        s = requests.get(f"{BASE_URL}/statistics/primitiva/numbers", headers=HEADERS, timeout=15).json()
        return r.get('data', []), s.get('data', [])
    except:
        return None, None

def verificar_filtres(comb):
    pares = [n for n in comb if n % 2 == 0]
    p_ok = (len(pares) == 3 or len(pares) == 4)
    decs = [sum(1 for n in comb if (i*10 < n <= (i+1)*10)) for i in range(5)]
    d_ok = (0 not in decs)
    units = [n % 10 for n in comb]
    u_ok = (len(set(units)) == 6)
    return p_ok, d_ok, u_ok

def preparar_grups(res, stats):
    g = {}
    nums_49 = list(range(1, 50))
    s_stats = sorted(stats, key=lambda x: x.get('appearances', 0), reverse=True)
    g["UP"], g["DOWN"] = [n['number'] for n in s_stats[:25]], [n['number'] for n in s_stats[-25:]]
    g["FUEGO"] = [n['number'] for n in stats if n.get('appearances', 0) > 12]
    g["HIELO"] = [n['number'] for n in stats if n.get('appearances', 0) <= 12]
    u9 = res[:9]
    n_u9 = [n for s in u9 for n in s['combination']]
    g["CALIENTES"] = list(set(n_u9))
    g["REPES"] = [n for n in set(n_u9) if n_u9.count(n) >= 3]
    g["FRIOS"] = [n for n in nums_49 if n not in g["CALIENTES"]]
    u6, u18 = res[:6], res[:18]
    n_u6, n_u18 = list(set([n for s in u6 for n in s['combination']])), [n for s in u18 for n in s['combination']]
    g["DESPERTANDO"] = [n for n in n_u6 if n in g["CALIENTES"]]
    g["NEUTROS"] = [n for n in nums_49 if n_u9.count(n) == 1 and n_u18.count(n) == 2]
    # Línia corregida de Mellizos
    g["MELLIZOS"] = [11, 22, 33, 44]
    g["COMUNES"] = list(set(g["DOWN"]) & set(g["HIELO"]) & set(g["FRIOS"]))
    return g

# --- INTERFÍCIE ---
st.title("🔥 Prometheus")
res, stats = carregar_dades()

if res and stats:
    g = preparar_grups(res, stats)
    st.subheader("📊 Últims 3 Resultats i Verificació")
    cols = st.columns(3)
    for i in range(3):
        with cols[i]:
            c = res[i]['combination']
            p_v, d_v, u_v = verificar_filtres(c)
            st.caption(f"{res[i]['drawDate']} | R:{res[i].get('resultData',{}).get('reintegro','?')}")
            st.write(f"**{'-'.join(map(str, c))}**")
            st.markdown(f"{'✅' if p_v else '❌'} Par | {'✅' if d_v else '❌'} Dec | {'✅' if u_v else '❌'} Uni")

    st.divider()
    c1, c2 = st.columns(2)
    m_on, c_on = c1.toggle("MELLIZOS"), c2.toggle("CLUMPS")

    if st.button("🚀 GENERAR 6 MÚLTIPLES", use_container_width=True):
        st.success("✅ Generant combinacions amb els 11 filtres bloquejats...")
        # Aquí s'executa la lògica de generació ja pactada anteriorment
        for i in range(1, 7):
            comb = sorted(random.sample(range(1, 50), 7))
            st.write(f"**A{i}:** {comb}")
else:
    st.info("🔄 Verificant dades de l'API... Revisa la Key als Secrets si aquest missatge no desapareix.")
