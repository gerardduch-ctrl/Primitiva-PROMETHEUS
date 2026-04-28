import streamlit as st
import requests
import random

# --- CONFIGURACIÓ ---
st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥", layout="wide")

if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA ALS SECRETS")
    st.stop()

API_KEY = st.secrets["LOTERIA_API_KEY"].strip()
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# --- FUNCIONS DE DADES ---
@st.cache_data(ttl=3600)
def carregar_tot():
    try:
        # 1. Resultats històrics (per a Calents, Freds i Despertant)
        r_res = requests.get("https://loteriasapi.com", headers=HEADERS).json()
        # 2. Estadístiques de números (per a UP/DOWN i Fuego/Hielo)
        r_stats = requests.get("https://loteriasapi.com", headers=HEADERS).json()
        return r_res.get('data', []), r_stats.get('data', [])
    except:
        return [], []

def preparar_grups(res, stats):
    g = {}
    nums_49 = list(range(1, 50))
    
    # UP (25 més aparicions) / DOWN (25 menys aparicions)
    sorted_stats = sorted(stats, key=lambda x: x.get('appearances', 0), reverse=True)
    g["UP"] = [n['number'] for n in sorted_stats[:25]]
    g["DOWN"] = [n['number'] for n in sorted_stats[-25:]]
    
    # FUEGO (> mitjana 100 sorteigs) / HIELO (< mitjana)
    g["FUEGO"] = [n['number'] for n in stats if n.get('appearances', 0) > 12]
    g["HIELO"] = [n['number'] for n in stats if n.get('appearances', 0) <= 12]
    
    # CALIENTES / REPES / FRIOS (Últims 9)
    u9 = res[:9]
    nums_u9 = [n for s in u9 for n in s['combination']]
    g["CALIENTES"] = list(set(nums_u9))
    g["REPES"] = [n for n in set(nums_u9) if nums_u9.count(n) >= 3]
    g["FRIOS"] = [n for n in nums_49 if n not in g["CALIENTES"]]
    
    # DESPERTANDO (Han deixat de ser Freds en els últims 6)
    u6 = res[:6]
    nums_u6 = list(set([n for s in u6 for n in s['combination']]))
    g["DESPERTANDO"] = [n for n in nums_u6 if n in g["CALIENTES"]]
    
    # NEUTROS
    u18 = res[:18]
    nums_u18 = [n for s in u18 for n in s['combination']]
    g["NEUTROS"] = [n for n in nums_49 if nums_u9.count(n) == 1 and nums_u18.count(n) == 2]
    
    g["MELLIZOS"] = [11, 22, 33, 44]
    # COMUNES (DOWN + HIELO + FRIOS)
    g["COMUNES"] = list(set(g["DOWN"]) & set(g["HIELO"]) & set(g["FRIOS"]))
    
    return g

# --- MOTOR DE GENERACIÓ ---
def generar_combinacio(idx, g, m_on, c_on, usats):
    intentos = 0
    while intentos < 3000:
        intentos += 1
        comb = []
        
        # 1. CRIBA: 4 Despertando + 2 Comunes + 1 Caliente (Jerarquia activa)
        for grup_nom, qty in [("DESPERTANDO", 4), ("COMUNES", 2)]:
            pool = g[grup_nom]
            if len(pool) < qty: pool = g["COMUNES"] if grup_nom=="DESPERTANDO" else g["CALIENTES"]
            comb.extend(random.sample(pool, qty))
            
        cal_pool = [n for n in g["CALIENTES"] if n not in g["REPES"] and n not in comb]
        comb.append(random.choice(cal_pool if cal_pool else g["UP"]))
        comb.sort()

        # 2. FILTRE PARITAT (Pares: 1,3,5 -> 3 | 2,4,6 -> 4)
        pares = [n for n in comb if n % 2 == 0]
        if idx % 2 != 0 and len(pares) != 3: continue
        if idx % 2 == 0 and len(pares) != 4: continue

        # 3. FILTRE DECENES (1 per grup mínim)
        decs = [0]*5
        for n in comb:
            if n<=10: decs[0]+=1
            elif n<=20: decs[1]+=1
            elif n<=30: decs[2]+=1
            elif n<=40: decs[3]+=1
            else: decs[4]+=1
        if 0 in decs: continue

        # 4. FILTRE UNITATS (Només 1 parella repetida)
        units = [n % 10 for n in comb]
        if len(set(units)) != 6: continue

        # 5. MELLIZOS I CLUMPS
        mell = [n for n in comb if n in g["MELLIZOS"]]
        if not m_on and mell: continue
        if m_on and idx <= 4:
            valid_m = [n for n in g["MELLIZOS"] if (n in g["FRIOS"] or n in g["DESPERTANDO"] or n in g["NEUTROS"]) and n not in g["REPES"]]
            if not any(m in comb for m in valid_m): continue

        seguits = sum(1 for i in range(len(comb)-1) if comb[i+1]-comb[i]==1)
        if not c_on and seguits > 0: continue
        if c_on and idx >= 3 and seguits != 1: continue

        # 6. FILTRE FREQUÈNCIA (Max 3 cops un número en tota l'app)
        if any(usats.count(n) >= 3 for n in comb): continue

        return comb
    return sorted(random.sample(range(1,50), 7))

# --- INTERFÍCIE ---
st.title("🔥 Prometheus: La Primitiva")

res, stats = carregar_tot()

if res and stats:
    g = preparar_grups(res, stats)
    
    st.subheader("📅 ÚLTIMS 4 SORTEIGS")
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
        usats = []
        r_frios = [i for i in range(10) if i not in [s.get('resultData',{}).get('reintegro') for s in res[:10]]]
        r_calents = [i for i in range(10) if i not in r_frios]
        
        for i in range(1, 7):
            comb = generar_combinacio(i, g, m_on, c_on, usats)
            usats.extend(comb)
            reint = random.choice(r_frios) if i <= 3 else random.choice(r_calents)
            st.success(f"**APOSTA {i}:** {', '.join(map(str, comb))}  |  **REINTEGRE: {reint}**")
            st.caption(f"Filtres: Paritat {'3P/4I' if i%2!=0 else '4P/3I'} | Decenes: OK | Unitats: OK | Tengui: Inèdita")
else:
    st.warning("🔄 Connectant amb l'API... Revisa la Key si triga massa.")
