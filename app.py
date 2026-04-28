import streamlit as st
import requests
import random

# --- CONFIGURACIÓ ---
st.set_page_config(page_title="Prometheus", page_icon="🔥")

if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ Falta API KEY")
    st.stop()

API_KEY = st.secrets["LOTERIA_API_KEY"].strip()
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
BASE_URL = "https://loteriasapi.com"

# --- CÀRREGA ULTRA-RÀPIDA ---
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data_fast():
    try:
        # Demanem només els últims 30 per anar més ràpid (suficient pels filtres de 9 i 18)
        res = requests.get(f"{BASE_URL}/results/primitiva?limit=30", headers=HEADERS, timeout=5).json().get('data', [])
        # Estadístiques ja calculades per l'API
        stats = requests.get(f"{BASE_URL}/statistics/primitiva/numbers", headers=HEADERS, timeout=5).json().get('data', [])
        return res, stats
    except:
        return [], []

def preparar_grups(res, stats):
    g = {}
    nums_49 = list(range(1, 50))
    s_stats = sorted(stats, key=lambda x: x.get('appearances', 0), reverse=True)
    g["UP"], g["DOWN"] = [n['number'] for n in s_stats[:25]], [n['number'] for n in s_stats[-25:]]
    g["FUEGO"] = [n['number'] for n in stats if n.get('appearances', 0) > 12]
    g["HIELO"] = [n['number'] for n in stats if n.get('appearances', 0) <= 12]
    u9 = res[:9]
    n_u9 = [n for s in u9 for n in s['combination']]
    g["CALIENTES"], g["REPES"] = list(set(n_u9)), [n for n in set(n_u9) if n_u9.count(n) >= 3]
    g["FRIOS"] = [n for n in nums_49 if n not in g["CALIENTES"]]
    u6 = res[:6]
    n_u6 = list(set([n for s in u6 for n in s['combination']]))
    g["DESPERTANDO"] = [n for n in n_u6 if n in g["CALIENTES"]]
    u18 = res[:18]
    n_u18 = [n for s in u18 for n in s['combination']]
    g["NEUTROS"] = [n for n in nums_49 if n_u9.count(n) == 1 and n_u18.count(n) == 2]
    g["MELLIZOS"] = [11, 22, 33, 44]
    g["COMUNES"] = list(set(g["DOWN"]) & set(g["HIELO"]) & set(g["FRIOS"]))
    return g

# --- MOTOR DE GENERACIÓ OPTIMITZAT ---
def generar_aposta_fast(idx, g, m_on, c_on, usats):
    for _ in range(2000): # Menys intents per no bloquejar
        c = []
        p_desp = g["DESPERTANDO"] if len(g["DESPERTANDO"]) >= 4 else g["COMUNES"]
        if not p_desp: p_desp = g["UP"]
        c.extend(random.sample(p_desp, 4))
        p_com = [n for n in g["COMUNES"] if n not in c]
        c.extend(random.sample(p_com if len(p_com)>=2 else g["UP"], 2))
        p_cal = [n for n in g["CALIENTES"] if n not in g["REPES"] and n not in c]
        c.append(random.choice(p_cal if p_cal else g["UP"]))
        c.sort()
        pares = [n for n in c if n % 2 == 0]
        if idx % 2 != 0 and len(pares) != 3: continue
        if idx % 2 == 0 and len(pares) != 4: continue
        if len(set(n % 10 for n in c)) != 6: continue
        seguits = sum(1 for i in range(len(c)-1) if c[i+1]-c[i]==1)
        if not c_on and seguits > 0: continue
        if c_on and idx >= 3 and seguits != 1: continue
        if any(usats.count(n) >= 3 for n in c): continue
        return c
    return sorted(random.sample(range(1,50), 7))

# --- INTERFÍCIE ---
st.title("🔥 Prometheus")

res, stats = fetch_data_fast()

if res and stats:
    g = preparar_grups(res, stats)
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            st.caption(f"{res[i]['drawDate']} | R:{res[i].get('resultData',{}).get('reintegro','?')}")
            st.write(f"**{'-'.join(map(str, res[i]['combination']))}**")

    st.divider()
    c1, c2 = st.columns(2)
    m_on = c1.toggle("MELLIZOS")
    c_on = c2.toggle("CLUMPS")

    if st.button("🚀 GENERAR", use_container_width=True):
        usats_global = []
        r_frios = [i for i in range(10) if i not in [s.get('resultData',{}).get('reintegro') for s in res[:10]]]
        for i in range(1, 7):
            comb = generar_aposta_fast(i, g, m_on, c_on, usats_global)
            usats_global.extend(comb)
            st.success(f"**A{i}:** {', '.join(map(str, comb))} | R: {random.choice(r_frios) if i<=3 else random.choice(range(10))}")
else:
    st.error("Error dades. Revisa API Key.")
