import streamlit as st
import requests
import random

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥", layout="wide")

if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA ALS SECRETS")
    st.stop()

API_KEY = st.secrets["LOTERIA_API_KEY"].strip()
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
BASE_URL = "https://loteriasapi.com"

# --- OBTENCIÓ DE DADES REALS ---
@st.cache_data(ttl=3600)
def fetch_all_data():
    try:
        res = requests.get(f"{BASE_URL}/results/primitiva?limit=100", headers=HEADERS, timeout=15).json().get('data', [])
        stats = requests.get(f"{BASE_URL}/statistics/primitiva/numbers", headers=HEADERS, timeout=15).json().get('data', [])
        return res, stats
    except:
        return [], []

# --- CREACIÓ DELS 10 GRUPS DE CRIBA ---
def preparar_grups(res, stats):
    g = {}
    nums_49 = list(range(1, 50))
    
    # UP / DOWN
    s_stats = sorted(stats, key=lambda x: x.get('appearances', 0), reverse=True)
    g["UP"] = [n['number'] for n in s_stats[:25]]
    g["DOWN"] = [n['number'] for n in s_stats[-25:]]
    
    # FUEGO / HIELO
    g["FUEGO"] = [n['number'] for n in stats if n.get('appearances', 0) > 12]
    g["HIELO"] = [n['number'] for n in stats if n.get('appearances', 0) <= 12]
    
    # CALIENTES / REPES / FRIOS
    u9 = res[:9]
    n_u9 = [n for s in u9 for n in s['combination']]
    g["CALIENTES"] = list(set(n_u9))
    g["REPES"] = [n for n in set(n_u9) if n_u9.count(n) >= 3]
    g["FRIOS"] = [n for n in nums_49 if n not in g["CALIENTES"]]
    
    # DESPERTANDO
    u6 = res[:6]
    n_u6 = list(set([n for s in u6 for n in s['combination']]))
    g["DESPERTANDO"] = [n for n in n_u6 if n in g["CALIENTES"]]
    
    # NEUTROS
    u18 = res[:18]
    n_u18 = [n for s in u18 for n in s['combination']]
    g["NEUTROS"] = [n for n in nums_49 if n_u9.count(n) == 1 and n_u18.count(n) == 2]
    
    g["MELLIZOS"] = [11, 22, 33, 44]
    g["COMUNES"] = list(set(g["DOWN"]) & set(g["HIELO"]) & set(g["FRIOS"]))
    return g

# --- MOTOR DE GENERACIÓ ---
def generar_aposta(idx, g, m_on, c_on, usats):
    for _ in range(5000):
        comb = []
        p_desp = g["DESPERTANDO"] if len(g["DESPERTANDO"]) >= 4 else g["COMUNES"]
        comb.extend(random.sample(p_desp, 4))
        p_com = [n for n in g["COMUNES"] if n not in comb]
        comb.extend(random.sample(p_com if len(p_com)>=2 else g["UP"], 2))
        p_cal = [n for n in g["CALIENTES"] if n not in g["REPES"] and n not in comb]
        comb.append(random.choice(p_cal if p_cal else g["UP"]))
        comb.sort()

        pares = [n for n in comb if n % 2 == 0]
        if idx % 2 != 0 and len(pares) != 3: continue
        if idx % 2 == 0 and len(pares) != 4: continue

        decs = [sum(1 for n in comb if (i*10 < n <= (i+1)*10)) for i in range(5)]
        if 0 in decs: continue
        if len(set(n % 10 for n in comb)) != 6: continue

        if not m_on and any(n in g["MELLIZOS"] for n in comb): continue
        if m_on and idx <= 4:
            v_mell = [n for n in g["MELLIZOS"] if (n in g["FRIOS"] or n in g["DESPERTANDO"] or n in g["NEUTROS"]) and n not in g["REPES"]]
            if not any(m in comb for m in v_mell): continue

        seguits = sum(1 for i in range(len(comb)-1) if comb[i+1]-comb[i]==1)
        if not c_on and seguits > 0: continue
        if c_on and idx >= 3 and seguits != 1: continue

        if any(usats.count(n) >= 3 for n in comb): continue
        return comb
    return sorted(random.sample(range(1,50), 7))

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

res, stats = fetch_all_data()

if res and stats:
    g = preparar_grups(res, stats)
    
    st.subheader("📅 ÚLTIMS SORTEIGS")
    cols = st.columns(4)
    for i in range(4):
        s = res[i]
        with cols[i]:
            st.metric(s['drawDate'], f"R: {s.get('resultData',{}).get('reintegro','?')}")
            st.write(f"**{'-'.join(map(str, s['combination']))}**")

    st.divider()
    c1, c2 = st.columns(2)
    with c1: m_on = st.toggle("SELECTOR MELLIZOS")
    with c2: c_on = st.toggle("SELECTOR CLUMPS")

    if st.button("🚀 GENERAR 6 COMBINACIONS MÚLTIPLES", use_container_width=True):
        usats_global = []
        r_frios = [i for i in range(10) if i not in [s.get('resultData',{}).get('reintegro') for s in res[:10]]]
        r_others = [i for i in range(10) if i not in r_frios]
        
        for i in range(1, 7):
            comb = generar_aposta(i, g, m_on, c_on, usats_global)
            usats_global.extend(comb)
            reint = random.choice(r_frios) if i <= 3 else random.choice(r_others)
            st.success(f"**APOSTA {i}:** {', '.join(map(str, comb))}  |  **REINTEGRE: {reint}**")
else:
    st.info("🔄 Carregant motor estadístic...")
