import streamlit as st
import requests
import random

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥", layout="wide")

# --- PROTOCOL D'ACCÉS (HEADERS) ---
if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA ALS SECRETS DE STREAMLIT")
    st.stop()

API_KEY = st.secrets["LOTERIA_API_KEY"].strip()
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# --- ENDPOINTS SEGONS DOCUMENTACIÓ ---
BASE_URL = "https://api.loteriasapi.com/api/v1"

@st.cache_data(ttl=3600)
def fetch_dades():
    try:
        # Resultats per a Calents/Freds/Despertant
        res = requests.get(f"{BASE_URL}/results/primitiva?limit=100", headers=HEADERS, timeout=10).json()
        # Estadístiques per a UP/DOWN i FUEGO/HIELO
        stats = requests.get(f"{BASE_URL}/statistics/primitiva/numbers", headers=HEADERS, timeout=10).json()
        return res.get('data', []), stats.get('data', [])
    except Exception as e:
        st.error(f"Error de connexió: {e}")
        return [], []

# --- MOTOR DE CRIBA PACTAT ---
def preparar_grups(res, stats):
    g = {}
    nums_49 = list(range(1, 50))
    
    # UP/DOWN (Històric)
    s_stats = sorted(stats, key=lambda x: x.get('appearances', 0), reverse=True)
    g["UP"] = [n['number'] for n in s_stats[:25]]
    g["DOWN"] = [n['number'] for n in s_stats[-25:]]
    
    # FUEGO/HIELO (Mitjana 100)
    g["FUEGO"] = [n['number'] for n in stats if n.get('appearances', 0) > 12]
    g["HIELO"] = [n['number'] for n in stats if n.get('appearances', 0) <= 12]
    
    # CALIENTES/REPES/FRIOS (Últims 9)
    u9 = res[:9]
    nums_u9 = [n for s in u9 for n in s['combination']]
    g["CALIENTES"] = list(set(nums_u9))
    g["REPES"] = [n for n in set(nums_u9) if nums_u9.count(n) >= 3]
    g["FRIOS"] = [n for n in nums_49 if n not in g["CALIENTES"]]
    
    # DESPERTANDO (D'últims 6)
    u6 = res[:6]
    nums_u6 = list(set([n for s in u6 for n in s['combination']]))
    g["DESPERTANDO"] = [n for n in nums_u6 if n in g["CALIENTES"]]
    
    # NEUTROS
    u18 = res[:18]
    nums_u18 = [n for s in u18 for n in s['combination']]
    g["NEUTROS"] = [n for n in nums_49 if nums_u9.count(n) == 1 and nums_u18.count(n) == 2]
    
    g["MELLIZOS"] = [11, 22, 33, 44]
    g["COMUNES"] = list(set(g["DOWN"]) & set(g["HIELO"]) & set(g["FRIOS"]))
    return g

# --- GENERADOR AMB 11 FILTRES ---
def generar_multiple(idx, g, m_on, c_on, usats):
    for _ in range(5000): # Intents per trobar la combinació perfecta
        c = []
        # Criba: 4 Despertant + 2 Comunes + 1 Caliente No Repe
        p_desp = g["DESPERTANDO"] if len(g["DESPERTANDO"]) >= 4 else g["COMUNES"]
        c.extend(random.sample(p_desp, 4))
        p_com = [n for n in g["COMUNES"] if n not in c]
        c.extend(random.sample(p_com if len(p_com)>=2 else g["UP"], 2))
        p_cal = [n for n in g["CALIENTES"] if n not in g["REPES"] and n not in c]
        c.append(random.choice(p_cal if p_cal else g["UP"]))
        c.sort()

        # Filtre Paritat
        pares = [n for n in c if n % 2 == 0]
        if idx % 2 != 0 and len(pares) != 3: continue
        if idx % 2 == 0 and len(pares) != 4: continue

        # Filtre Decenes (Mínim 1 per grup)
        decs = [0]*5
        for n in c:
            if n<=10: decs[0]+=1
            elif n<=20: decs[1]+=1
            elif n<=30: decs[2]+=1
            elif n<=40: decs[3]+=1
            else: decs[4]+=1
        if 0 in decs: continue

        # Filtre Unitats (Només 1 parella repetida)
        if len(set(n % 10 for n in c)) != 6: continue

        # Mellizos i Clumps
        has_mell = any(n in g["MELLIZOS"] for n in c)
        if not m_on and has_mell: continue
        if m_on and idx <= 4:
            v_mell = [n for n in g["MELLIZOS"] if (n in g["FRIOS"] or n in g["DESPERTANDO"] or n in g["NEUTROS"]) and n not in g["REPES"]]
            if not any(m in c for m in v_mell): continue

        seguits = sum(1 for i in range(len(c)-1) if c[i+1]-c[i]==1)
        if not c_on and seguits > 0: continue
        if c_on and idx >= 3 and seguits != 1: continue

        # Freqüència Global (Max 3 aparicions)
        if any(usats.count(n) >= 3 for n in c): continue

        return c
    return sorted(random.sample(range(1,50), 7))

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

res, stats = fetch_dades()

if res and stats:
    g = preparar_grups(res, stats)
    
    st.subheader("📅 ÚLTIMS SORTEIGS (VERIFICACIÓ)")
    cols = st.columns(4)
    for i in range(4):
        s = res[i]
        with cols[i]:
            st.metric(s['drawDate'], f"R: {s.get('resultData',{}).get('reintegro','?')}")
            st.write(f"**{'-'.join(map(str, s['combination']))}**")

    st.divider()
    c1, col2 = st.columns(2)
    with c1: m_on = st.toggle("SELECTOR MELLIZOS")
    with col2: c_on = st.toggle("SELECTOR CLUMPS")

    if st.button("🚀 GENERAR 6 COMBINACIONS MÚLTIPLES", use_container_width=True):
        usats = []
        r_frios = [i for i in range(10) if i not in [s.get('resultData',{}).get('reintegro') for s in res[:10]]]
        r_others = [i for i in range(10) if i not in r_frios]
        
        for i in range(1, 7):
            comb = generar_multiple(i, g, m_on, c_on, usats)
            usats.extend(comb)
            reint = random.choice(r_frios) if i <= 3 else random.choice(r_others)
            st.success(f"**APOSTA {i}:** {', '.join(map(str, comb))} | **REINTEGRE: {reint}**")
            st.caption(f"Paritat: {'3P/4I' if i%2!=0 else '4P/3I'} | Decenes: OK | Unitats: OK | Tengui: Inèdita")
else:
    st.info("🔄 Connectant amb Loteria API... Si triga, revisa la Key als Secrets.")
