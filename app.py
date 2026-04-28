import streamlit as st
import requests
import random

# Configuració de pàgina per a mòbil
st.set_page_config(page_title="Prometeus Primitiva", page_icon="🔥", layout="centered")

# --- ESTILS PERSONALITZATS ---
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0px 2px 5px rgba(0,0,0,0.1); }
    .stButton>button { height: 60px; font-size: 20px; border-radius: 15px; background-color: #FF4B4B; color: white; }
    [data-testid="stExpander"] { border: none; box-shadow: none; background-color: transparent; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CONNEXIÓ OFICIAL LOTERIAS API V1 ---
def get_api_data():
    try:
        api_key = st.secrets["LOTERIA_API_KEY"]
        url = "https://loteriasapi.com"
        headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
        
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            res = r.json()
            if res.get("success"):
                d = res["data"]
                return {
                    "data": d.get("drawDate", "N/A"),
                    "numeros": ", ".join(map(str, d.get("combination", []))),
                    "bote": d.get("jackpotFormatted", "No disponible")
                }
        return {"data": "Error", "numeros": "Revisa API Key", "bote": "---"}
    except Exception as e:
        return {"data": "Error connexió", "numeros": str(e), "bote": "---"}

api_info = get_api_data()

# --- PANTALLA PRINCIPAL (MINIMALISTA) ---
st.title("🔥 Prometeus Primitiva")

# Dades API
st.metric("BOTE PRÒXIM SORTEIG", api_info['bote'])
st.write(f"📅 **Últim sorteig ({api_info['data']}):**")
st.code(api_info['numeros'], language="text")

st.divider()

# --- SELECTORS (UN SOTA L'ALTRE) ---
st.subheader("⚙️ Configuració de Criba")

sel_decena_koixa = st.selectbox("S. DECENAS (Desena amb només 1 número):", 
                               ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"])

sel_un_rep = st.multiselect("S. UNITAT REPETIDA (Max 2)", list(range(10)), max_selections=2)

sel_un_vet = st.multiselect("S. UNITAT VETADA (Max 4)", list(range(10)), max_selections=4)

col_a, col_b = st.columns(2)
with col_a:
    sel_mellizos = st.toggle("S. MELLIZOS")
with col_b:
    sel_clumps = st.toggle("S. CLUMPS")

st.divider()

# --- MOTOR DE LÒGICA (BLOQUEJAT) ---
def validar_terminacions(nums, sel_rep):
    units = [n % 10 for n in nums]
    counts = {x: units.count(x) for x in set(units)}
    reps_reals = [u for u, c in counts.items() if c > 1]
    if sel_rep:
        if not all(r in reps_reals for r in sel_rep): return False
        if not all(r in sel_rep for r in reps_reals): return False
    else:
        if len(reps_reals) > 1: return False
    return all(c <= 2 for c in counts.values())

def generar_apostes():
    resultats = []
    # Perfils de 7 números pactats
    perfils_base = [[2,1,1,2,1], [2,1,2,1,1], [2,2,1,1,1], [1,1,2,2,1], [1,2,1,2,1], [1,2,2,1,1], [1,1,1,2,2], [1,1,2,1,2], [1,2,1,1,2], [2,1,1,1,2]]
    
    for i in range(1, 7):
        success = False
        paritat_parells = 3 if i in [1, 3, 5] else 4
        intentos_max = 5000
        
        while not success and intentos_max > 0:
            intentos_max -= 1
            comb = []
            perfil = random.choice(perfils_base)
            
            # Filtre Selector Decenes
            dec_map = {"1-10":0, "11-20":1, "21-30":2, "31-40":3, "41-49":4}
            if sel_decena_koixa != "Cap" and perfil[dec_map[sel_decena_koixa]] != 1: continue

            # Construcció números
            blocs = [list(range(1,11)), list(range(11,21)), list(range(21,31)), list(range(31,41)), list(range(41,50))]
            for idx, qty in enumerate(perfil):
                pool = [n for n in blocs[idx] if n % 10 not in sel_un_vet]
                if len(pool) < qty: break
                comb.extend(random.sample(pool, qty))
            
            if len(comb) != 7: continue
            
            # Mellizos (Apostes 1-4)
            mells = [11, 22, 33, 44]
            present_mells = [n for n in comb if n in mells]
            if sel_mellizos and i <= 4:
                if len(present_mells) != 1: continue
            elif not sel_mellizos and len(present_mells) > 0: continue
            
            # Clumps (Apostes 3-6)
            comb.sort()
            seguits = sum(1 for j in range(len(comb)-1) if comb[j+1] == comb[j]+1)
            if sel_clumps and i >= 3:
                if seguits != 1: continue
            elif not sel_clumps and seguits > 0: continue
            
            # Paritat i Unitats
            if sum(1 for n in comb if n % 2 == 0) != paritat_parells: continue
            if not validar_terminacions(comb, sel_un_rep): continue
            
            # FILTRE CREUAT: No més de 2 iguals entre apostes
            if any(len(set(comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(comb)
            success = True
            
    return resultats

# --- BOTÓ GENERAR ---
if st.button("🚀 GENERAR APOSTES"):
    apostes = generar_apostes()
    if len(apostes) < 6:
        st.error("⚠️ Filtres massa estrictes. Prova de treure algun veto.")
    else:
        for i, a in enumerate(apostes):
            st.markdown(f"### Aposta {i+1}")
            st.info(" - ".join(map(str, a)))

