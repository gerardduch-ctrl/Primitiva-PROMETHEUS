import streamlit as st
import requests
import random

# --- CONFIGURACIÓ ---
st.set_page_config(page_title="Prometheus", page_icon="🔥", layout="wide")

if "LOTERIA_API_KEY" not in st.secrets:
    st.error("❌ CLAU NO TROBADA ALS SECRETS")
    st.stop()

API_KEY = st.secrets["LOTERIA_API_KEY"].strip()
# Protocol de capçaleres oficial
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Provem l'URL base directa
URL_BASE = "https://loteriasapi.com"

def fetch_dades_diagnostico():
    try:
        r = requests.get(f"{URL_BASE}/results/primitiva?limit=40", headers=HEADERS, timeout=10)
        s = requests.get(f"{URL_BASE}/statistics/primitiva/numbers", headers=HEADERS, timeout=10)
        
        if r.status_code == 200 and s.status_code == 200:
            return r.json().get('data', []), s.json().get('data', [])
        else:
            st.error(f"⚠️ Error del servidor: Codi {r.status_code}. Revisa la teva Key.")
            return None, None
    except Exception as e:
        st.error(f"❌ Error de connexió: {str(e)}")
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
    g["MELLIZOS"] = [11, 22, 33, 44]
    g["COMUNES"] = list(set(g["DOWN"]) & set(g["HIELO"]) & set(g["FRIOS"]))
    return g

# --- INTERFÍCIE ---
st.title("🔥 Prometheus")
res, stats = fetch_dades_diagnostico()

if res and stats:
    g = preparar_grups(res, stats)
    st.subheader("📊 Últims Sorteigs Reals")
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
    m_on = c1.toggle("MELLIZOS")
    c_on = c2.toggle("CLUMPS")

    if st.button("🚀 GENERAR 6 MÚLTIPLES", use_container_width=True):
        usats = []
        r_f = [i for i in range(10) if i not in [s.get('resultData',{}).get('reintegro') for s in res[:10]]]
        for i in range(1, 7):
            comb = sorted(random.sample(range(1,50), 7)) # Càlcul ràpid per prova
            st.success(f"**A{i}:** {', '.join(map(str, comb))} | R: {random.choice(r_f) if i<=3 else random.choice(range(10))}")
else:
    st.info("🔄 Esperant resposta del servidor de Loteries...")
