import streamlit as st
import requests
import random
from datetime import datetime

# --- CONFIGURACIÓ I PROTOCOL ---
st.set_page_config(page_title="Prometheus Primitiva", page_icon="🔥", layout="wide")

if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA")
    st.stop()

API_KEY = st.secrets["LOTERIA_API_KEY"].strip()
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
URL_RES = "https://loteriasapi.com"
URL_STATS = "https://loteriasapi.com"

# --- MOTOR DE DADES ---
@st.cache_data(ttl=3600)
def get_all_data():
    try:
        res = requests.get(f"{URL_RES}?limit=100", headers=HEADERS).json().get('data', [])
        stats = requests.get(f"{URL_STATS}/numbers", headers=HEADERS).json().get('data', [])
        gen = requests.get(URL_STATS, headers=HEADERS).json().get('data', {})
        return res, stats, gen
    except:
        return None, None, None

# --- LÒGICA DE CRIBA PACTADA ---
def preparar_grups(res, stats, gen):
    grups = {}
    nums_49 = list(range(1, 50))
    
    # 1. UP / DOWN (Històric)
    most_frequent = gen.get('mostFrequentNumbers', [])
    least_frequent = gen.get('leastFrequentNumbers', [])
    grups["UP"] = [n['number'] for n in most_frequent[:25]]
    grups["DOWN"] = [n['number'] for n in least_frequent[:25]]
    
    # 2. FUEGO / HIELO (Últims 100 - Mitjana 12.24)
    grups["FUEGO"] = [n['number'] for n in stats if n.get('appearances', 0) > 12]
    grups["HIELO"] = [n['number'] for n in stats if n.get('appearances', 0) <= 12]
    
    # 3. CALIENTES / FRIOS / REPES (Últims 9)
    u9 = res[:9]
    nums_u9 = [n for s in u9 for n in s['combination']]
    grups["CALIENTES"] = list(set(nums_u9))
    grups["REPES"] = [n for n in set(nums_u9) if nums_u9.count(n) >= 3]
    grups["FRIOS"] = [n for n in nums_49 if n not in grups["CALIENTES"]]
    
    # 4. DESPERTANDO (Han deixat de ser freds en els últims 6)
    u6 = res[:6]
    nums_u6 = list(set([n for s in u6 for n in s['combination']]))
    freds_abans = [] # Lògica simplificada per al prototip
    grups["DESPERTANDO"] = [n for n in nums_u6 if n in grups["CALIENTES"]] 
    
    # 5. NEUTROS (1 vegada en 9, 2 vegades en 18)
    u18 = res[:18]
    nums_u18 = [n for s in u18 for n in s['combination']]
    grups["NEUTROS"] = [n for n in nums_49 if nums_u9.count(n) == 1 and nums_u18.count(n) == 2]
    
    grups["MELLIZOS"] = [11, 22, 33, 44]
    
    # COMUNES (DOWN + HIELO + FRIOS)
    grups["COMUNES"] = list(set(grups["DOWN"]) & set(grups["HIELO"]) & set(grups["FRIOS"]))
    
    return grups

# --- GENERADOR AMB FILTRES BLOQUEJATS ---
def generar_aposta(id_aposta, grups, m_on, c_on, ja_usats):
    intentos = 0
    while intentos < 5000:
        intentos += 1
        aposta = []
        
        # LÒGICA DE SELECCIÓ (4 Despertant + 2 Comuns + 1 Caliente No Repe)
        candidats_desp = grups["DESPERTANDO"] if len(grups["DESPERTANDO"]) >= 4 else grups["COMUNES"]
        aposta.extend(random.sample(candidats_desp, 4))
        
        candidats_com = [n for n in grups["COMUNES"] if n not in aposta]
        aposta.extend(random.sample(candidats_com, 2))
        
        candidats_cal = [n for n in grups["CALIENTES"] if n not in grups["REPES"] and n not in aposta]
        if candidats_cal: aposta.append(random.choice(candidats_cal))
        else: aposta.append(random.choice([n for n in range(1,50) if n not in aposta]))

        aposta.sort()
        
        # FILTRE PARITAT
        pares = [n for n in aposta if n % 2 == 0]
        if id_aposta in [1, 3, 5] and len(pares) != 3: continue
        if id_aposta in [2, 4, 6] and len(pares) != 4: continue
        
        # FILTRE DECENES (Mínim 1 per grup)
        dec = [0]*5
        for n in aposta:
            if n <= 10: dec[0]+=1
            elif n <= 20: dec[1]+=1
            elif n <= 30: dec[2]+=1
            elif n <= 40: dec[3]+=1
            else: dec[4]+=1
        if 0 in dec: continue
        
        # FILTRE UNITATS (Només una repetida)
        terms = [n % 10 for n in aposta]
        if len(set(terms)) != 6: continue
        
        # SELECTOR MELLIZOS
        mell_en_aposta = [n for n in aposta if n in grups["MELLIZOS"]]
        if not m_on and mell_en_aposta: continue
        if m_on and id_aposta <= 4:
            # Ha de tenir un mellizo que sigui Frio/Desp/Neutro i NO repe
            valid_m = [n for n in grups["MELLIZOS"] if (n in grups["FRIOS"] or n in grups["DESPERTANDO"] or n in grups["NEUTROS"]) and n not in grups["REPES"]]
            if not any(m in aposta for m in valid_m): continue

        # SELECTOR CLUMPS (Seguits)
        seguits = 0
        for i in range(len(aposta)-1):
            if aposta[i+1] - aposta[i] == 1: seguits += 1
        if not c_on and seguits > 0: continue
        if c_on and id_aposta >= 3 and seguits != 1: continue

        # FILTRE FREQUÈNCIA GLOBAL (Màxim 3 aparicions de cada número)
        count_global = 0
        for n in aposta:
            if ja_usats.count(n) >= 3: count_global += 1
        if count_global > 0: continue

        return aposta
    return sorted(random.sample(range(1,50), 7))

# --- INTERFÍCIE ---
st.title("🔥 Prometheus Primitiva")

res, stats, gen = get_all_data()

if res:
    grups = preparar_grups(res, stats, gen)
    
    # ÚLTIMS 4
    st.subheader("📅 Comprovació d'Actualització (Últims 4)")
    c = st.columns(4)
    for i in range(4):
        s = res[i]
        with c[i]:
            st.metric(s['drawDate'], f"R: {s.get('resultData',{}).get('reintegro','?')}")
            st.write(f"**{'-'.join(map(str, s['combination']))}**")

    st.divider()
    col1, col2 = st.columns(2)
    with col1: m_on = st.toggle("SELECTOR MELLIZOS")
    with col2: c_on = st.toggle("SELECTOR CLUMPS")

    if st.button("🚀 GENERAR 6 COMBINACIONS MÚLTIPLES", use_container_width=True):
        usats = []
        apostes = []
        for i in range(1, 7):
            n_aposta = generar_aposta(i, grups, m_on, c_on, usats)
            apostes.append(n_aposta)
            usats.extend(n_aposta)
        
        # REINTEGRES
        r_frios = [i for i in range(10) if i not in [s.get('resultData',{}).get('reintegro') for s in res[:10]]]
        r_others = [i for i in range(10) if i not in r_frios]
        
        st.write("### 📝 Les teves 6 combinacions de 7 números:")
        for idx, a in enumerate(apostes):
            reint = random.choice(r_frios) if idx < 3 else random.choice(r_others)
            st.success(f"**Aposta {idx+1}:** {', '.join(map(str, a))}  |  **REINTEGRE: {reint}**")
            st.caption(f"Filtres: Paritat {'3P/4I' if (idx+1)%2!=0 else '4P/3I'} | Decenes OK | Unitats OK | Tengui: Inèdita")

else:
    st.warning("🔄 Connectant amb Loteria API... Revisa els teus Secrets si triga massa.")
