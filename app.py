import streamlit as st
import requests
import random

# Configuració de la pàgina i Icona de Prometeu
st.set_page_config(page_title="Prometeus Primitiva", page_icon="🔥", layout="centered")

# --- ESTILS MINIMALISTES ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #333; color: white; }
    .reportview-container .main .footer{ visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- DADES API (Exemple d'estructura) ---
def get_api_data():
    api_key = st.secrets["LOTERIA_API_KEY"]
    # Nota: Aquí adaptarem l'URL segons la documentació específica de la teva API
    # Per ara, simulem la càrrega de dades
    return {
        "ultims_sortejos": [
            {"data": "2024-05-18", "numeros": "04 - 12 - 21 - 33 - 40 - 48", "bote": "15.500.000 €"},
            {"data": "2024-05-16", "numeros": "02 - 15 - 28 - 31 - 42 - 45", "bote": "12.000.000 €"}
        ]
    }

data = get_api_data()

# --- CAPÇALERA ---
st.title("🔥 Prometeus Primitiva")
st.subheader(f"Bote Pròxim Sorteig: {data['ultims_sortejos'][0]['bote']}")
col1, col2 = st.columns(2)
with col1:
    st.write(f"📅 {data['ultims_sortejos'][0]['data']}: {data['ultims_sortejos'][0]['numeros']}")
with col2:
    st.write(f"📅 {data['ultims_sortejos'][1]['data']}: {data['ultims_sortejos'][1]['numeros']}")

st.divider()

# --- SELECTORS (INTERFÍCIE) ---
with st.expander("⚙️ CONFIGURACIÓ DE FILTRES"):
    sel_decena_unica = st.selectbox("SELECTOR DECENAS (Només 1 número en:)", 
                                  ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"])
    
    sel_un_rep = st.multiselect("SELECTOR UNIDAD REPETIDA (Max 2)", list(range(10)), max_selections=2)
    
    sel_un_vet = st.multiselect("SELECTOR UNIDAD VETADA (Max 4)", list(range(10)), max_selections=4)
    
    sel_mellizos = st.toggle("SELECTOR MELLIZOS (Apostes 1-4)")
    
    sel_clumps = st.toggle("SELECTOR CLUMPS (Apostes 3-6: 2 seguits)")

# --- LÒGICA DE GENERACIÓ (BLOQUEJADA) ---
def generar_combinacio(id_aposta, decenes_perfil, units_rep, units_vet, mellizos_on, clumps_on, paritat):
    # paritat: '3P4S' o '4P2S' (adaptat a 7 números)
    intentos = 0
    while intentos < 5000:
        intentos += 1
        nums = []
        
        # 1. Gestionar Decenes segons perfil
        # Perfils ex: [2, 1, 1, 2, 1] per a les 5 franges
        pools = [list(range(1,11)), list(range(11,21)), list(range(21,31)), list(range(31,41)), list(range(41,50))]
        
        # Filtre veto unitat
        for i in range(5):
            pools[i] = [n for n in pools[i] if n % 10 not in units_vet]
            
        final_nums = []
        for i, qty in enumerate(decenes_perfil):
            if len(pools[i]) < qty: continue
            final_nums.extend(random.sample(pools[i], qty))
            
        if len(final_nums) != 7: continue
        
        # 2. Filtre Mellizos (11, 22, 33, 44)
        mells = [11, 22, 33, 44]
        mells_in_comb = [n for n in final_nums if n in mells]
        if mellizos_on and id_aposta <= 4:
            if len(mells_in_comb) != 1: continue
        else:
            if len(mells_in_comb) > 0: continue
            
        # 3. Filtre Clumps (Seguits)
        final_nums.sort()
        seguits = sum(1 for i in range(len(final_nums)-1) if final_nums[i+1] == final_nums[i]+1)
        if clumps_on and id_aposta >= 3:
            if seguits != 1: continue
        else:
            if seguits > 0: continue
            
        # 4. Filtre Paritat
        parells = [n for n in final_nums if n % 2 == 0]
        if paritat == "3P4S" and len(parells) != 3: continue
        if paritat == "4P3S" and len(parells) != 4: continue
        
        # 5. Filtre Unitats Repetides
        unitats = [n % 10 for n in final_nums]
        counts = {x: unitats.count(x) for x in set(unitats)}
        reps = [k for k, v in counts.items() if v > 1]
        
        if len(units_rep) > 0:
            if not all(r in units_rep for r in reps): continue
        if any(v > 2 for v in counts.values()): continue # Max 2 repetits de la mateixa unitat
        
        return sorted(final_nums)
    return ["Error de paràmetres"]

# --- ACCIÓ GENERAR ---
if st.button("GENERAR 6 APUESTAS MÚLTIPLES"):
    perfils = [
        [2,1,1,2,1], [2,1,2,1,1], [2,2,1,1,1], 
        [1,1,2,2,1], [1,2,1,2,1], [1,2,2,1,1]
    ]
    
    for i in range(1, 7):
        paritat = "3P4S" if i in [1, 3, 5] else "4P3S"
        res = generar_combinacio(i, perfils[i-1], sel_un_rep, sel_un_vet, sel_mellizos, sel_clumps, paritat)
        st.write(f"**Aposta {i} ({paritat}):** {res}")

