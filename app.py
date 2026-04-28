import streamlit as st
import requests
import random

# --- CONFIGURACIÓ ---
st.set_page_config(page_title="Prometheus", page_icon="🔥", layout="wide")

if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ Falta la clau als Secrets")
    st.stop()

API_KEY = st.secrets["LOTERIA_API_KEY"].strip()
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
BASE_URL = "https://loteriasapi.com"

# --- FUNCIONS DE DADES ---
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_dades():
    try:
        r = requests.get(f"{BASE_URL}/results/primitiva?limit=100", headers=HEADERS, timeout=10).json().get('data', [])
        s = requests.get(f"{BASE_URL}/statistics/primitiva/numbers", headers=HEADERS, timeout=10).json().get('data', [])
        return r, s
    except: return [], []

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
    g["MELLIZOS"] = [11, 22, 33, 44]
    g["COMUNES"] = list(set(g["DOWN"]) & set(g["HIELO"]) & set(g["FRIOS"]))
    return g

# --- GENERADOR AMB 11 FILTRES ---
def generar_aposta(idx, g, m_on, c_on, usats):
    for _ in range(5000):
        c = []
        p_desp = g["DESPERTANDO"] if len(g["DESPERTANDO"]) >= 4 else g["COMUNES"]
        c.extend(random.sample(p_desp if p_desp else g["UP"], 4))
        p_com = [n for n in g["COMUNES"] if n not in c]
        c.extend(random.sample(p_com if len(p_com)>=2 else g["UP"], 2))
        p_cal = [n for n in g["CALIENTES"] if n not in g["REPES"] and n not in c]
        c.append(random.choice(p_cal if p_cal else g["UP"]))
        c.sort()
        
        p_ok, d_ok, u_ok = verificar_filtres(c)
        pares = [n for n in c if n % 2 == 0]
        if idx % 2 != 0 and len(pares) != 3: continue
        if idx % 2 == 0 and len(pares) != 4: continue
        if not d_ok or not u_ok: continue

        if not m_on and any(n in g["MELLIZOS"] for n in c): continue
        if m_on and idx <= 4:
            v_m = [n for n in g["MELLIZOS"] if (n in g["FRIOS"] or n in g["DESPERTANDO"] or n in g["NEUTROS"]) and n not in g["REPES"]]
            if not any(m in c for m in v_m): continue
        seg = sum(1 for i in range(len(c)-1) if c[i+1]-c[i]==1)
        if not c_on and seg > 0: continue
        if c_on and idx >= 3 and seg != 1: continue
        if any(usats.count(n) >= 3 for n in c): continue
        return c
    return sorted(random.sample(range(1,50), 7))

# --- INTERFÍCIE ---
st.title("🔥 Prometheus")
res, stats = fetch_dades()

if res and stats:
    g = preparar_grups(res, stats)
    st.subheader("📊 Anàlisi Últims Sorteigs")
    cols = st.columns(4)
    for i in range(4):
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
        usats = []
        r_f = [i for i in range(10) if i not in [s.get('resultData',{}).get('reintegro') for s in res[:10]]]
        for i in range(1, 7):
            comb = generar_aposta(i, g, m_on, c_on, usats)
            usats.extend(comb)
            reint = random.choice(r_f) if i <= 3 else random.choice(range(10))
            st.success(f"**A{i}:** {', '.join(map(str, comb))} | R: {reint}")
else: st.info("🔄 Carregant dades...")
