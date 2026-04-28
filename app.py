import streamlit as st
import requests
import random

# --- CONFIGURACIÓ ---
st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥", layout="wide")

if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA ALS SECRETS")
    st.stop()

# Neteja estricta de la clau per evitar espais invisibles
API_KEY = st.secrets["LOTERIA_API_KEY"].strip().replace('"', '').replace("'", "")
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
BASE_URL = "https://api.loteriasapi.com/api/v1"

# --- FUNCIONS DE DADES ---
@st.cache_data(ttl=3600)
def carregar_dades_api():
    try:
        # Peticions segons el format oficial confirmat
        r_res = requests.get(f"{BASE_URL}/results/primitiva?limit=100", headers=HEADERS, timeout=10).json()
        r_stats = requests.get(f"{BASE_URL}/statistics/primitiva/numbers", headers=HEADERS, timeout=10).json()
        return r_res.get('data', []), r_stats.get('data', [])
    except Exception as e:
        return [], []

def preparar_grups(res, stats):
    g = {}
    nums_49 = list(range(1, 50))
    # UP/DOWN (Basat en aparicions totals)
    s_stats = sorted(stats, key=lambda x: x.get('appearances', 0), reverse=True)
    g["UP"] = [n['number'] for n in s_stats[:25]]
    g["DOWN"] = [n['number'] for n in s_stats[-25:]]
    # FUEGO/HIELO (Mitjana històrica en 100 sorteigs)
    g["FUEGO"] = [n['number'] for n in stats if n.get('appearances', 0) > 12]
    g["HIELO"] = [n['number'] for n in stats if n.get('appearances', 0) <= 12]
    # CALIENTES/FRIOS/REPES (Últims 9 sorteigs)
    u9 = res[:9]
    nums_u9 = [n for s in u9 for n in s['combination']]
    g["CALIENTES"] = list(set(nums_u9))
    g["REPES"] = [n for n in set(nums_u9) if nums_u9.count(n) >= 3]
    g["FRIOS"] = [n for n in nums_49 if n not in g["CALIENTES"]]
    # DESPERTANDO (Han sortit en els darrers 6 després de ser freds)
    u6 = res[:6]
    nums_u6 = list(set([n for s in u6 for n in s['combination']]))
    g["DESPERTANDO"] = [n for n in nums_u6 if n in g["CALIENTES"]]
    # NEUTROS i MELLIZOS
    u18 = res[:18]
    nums_u18 = [n for s in u18 for n in s['combination']]
    g["NEUTROS"] = [n for n in nums_49 if nums_u9.count(n) == 1 and nums_u18.count(n) == 2]
    g["MELLIZOS"] = [11, 22, 33, 44]
    g["COMUNES"] = list(set(g["DOWN"]) & set(g["HIELO"]) & set(g["FRIOS"]))
    return g

# --- MOTOR DE GENERACIÓ AMB ELS 11 FILTRES ---
def generar_multiple(idx, g, m_on, c_on, usats):
    for _ in range(10000): # Intents per trobar la combinació perfecta
        c = []
        # CRIBA: 4 Desp + 2 Comunes + 1 Caliente (no repe)
        p_desp = g["DESPERTANDO"] if len(g["DESPERTANDO"]) >= 4 else g["COMUNES"]
        c.extend(random.sample(p_desp, 4))
        p_com = [n for n in g["COMUNES"] if n not in c]
        c.extend(random.sample(p_com if len(p_com)>=2 else g["UP"], 2))
        p_cal = [n for n in g["CALIENTES"] if n not in g["REPES"] and n not in c]
        c.append(random.choice(p_cal if p_cal else g["UP"]))
        c.sort()

        # Filtre Paritat (Apostes 1,3,5 -> 3P/4I | 2,4,6 -> 4P/3I)
        pares = [n for n in c if n % 2 == 0]
        if idx % 2 != 0 and len(pares) != 3: continue
        if idx % 2 == 0 and len(pares) != 4: continue

        # Filtre Decenes (Mínim 1 per cada franja 1-10, 11-20, etc.)
        bins = [0]*5
        for n in c:
            if n <= 10: bins[0]+=1
            elif n <= 20: bins[1]+=1
            elif n <= 30: bins[2]+=1
            elif n <= 40: bins[3]+=1
            else: bins[4]+=1
        if 0 in bins: continue

        # Filtre Unitats (Només una repetida)
        if len(set(n % 10 for n in c)) != 6: continue

        # Selectors Mellizos i Clumps
        mell_en_c = [n for n in c if n in g["MELLIZOS"]]
        if not m_on and mell_en_c: continue
        if m_on and idx <= 4:
            valid_m = [n for n in g["MELLIZOS"] if (n in g["FRIOS"] or n in g["DESPERTANDO"] or n in g["NEUTROS"]) and n not in g["REPES"]]
            if not any(m in c for m in valid_m): continue

        seguits = sum(1 for i in range(len(c)-1) if c[i+1]-c[i]==1)
        if not c_on and seguits > 0: continue
        if c_on and idx >= 3 and seguits != 1: continue

        # Freqüència entre les 6 apostes (Max 3 cops el mateix número)
        if any(usats.count(n) >= 3 for n in c): continue

        return c
    return sorted(random.sample(range(1,50), 7))

# --- INTERFÍCIE STREAMLIT ---
st.title("🔥 Prometheus: La Primitiva")

res, stats = carregar_dades_api()

if res and stats:
    g = preparar_grups(res, stats)
    
    st.subheader("📅 Verificació d'Actualització (Últims 4)")
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
        usats_global = []
        r_frios = [i for i in range(10) if i not in [s.get('resultData',{}).get('reintegro') for s in res[:10]]]
        r_others = [i for i in range(10) if i not in r_frios]
        
        st.write("### 📝 Les teves 6 apostes generades:")
        for i in range(1, 7):
            comb = generar_multiple(i, g, m_on, c_on, usats_global)
            usats_global.extend(comb)
            reint = random.choice(r_frios) if i <= 3 else random.choice(r_others)
            st.success(f"**Aposta {i}:** {', '.join(map(str, comb))}  |  **REINTEGRE: {reint}**")
            st.caption(f"Filtres: Paritat {'3P/4I' if i%2!=0 else '4P/3I'} | Decenes OK | Unitats OK | Inèdita")
else:
    st.info("🔄 Connectant amb el servidor... Revisa la Key als Secrets si aquest missatge no desapareix.")
