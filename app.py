import streamlit as st
import random

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Prometeus Primitiva", page_icon="🔥", layout="centered")

# --- ESTILS ---
st.markdown("""
    <style>
    .stButton>button { height: 75px; font-size: 24px; font-weight: bold; border-radius: 15px; background-color: #FF4B4B; color: white; margin-top: 25px; }
    h3 { margin-top: 25px; color: #333; border-bottom: 2px solid #FF4B4B; width: 100%; padding-bottom: 5px; }
    div.row-widget.stRadio > div{ flex-direction:row; justify-content: center; gap: 8px; flex-wrap: wrap; }
    .veto-label { font-size: 11px; color: #999; text-align: center; margin-bottom: 10px; }
    .stSuccess { font-size: 20px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 Prometeus Primitiva")

# --- PANELLS DE SELECTORS ---
st.markdown("### 1. Selector de Decenes")
sel_decena_koixa = st.radio("D", ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"], horizontal=True, label_visibility="collapsed")

st.markdown("### 2. Unitats Repetides (Max 2)")
sel_un_rep1 = st.radio("U1", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="u1", label_visibility="collapsed")
sel_un_rep2 = st.radio("U2", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="u2", label_visibility="collapsed")

st.markdown("### 3. Unitats Vetades (Fins a 4)")
v1 = st.radio("V1", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="v1", label_visibility="collapsed")
v2 = st.radio("V2", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="v2", label_visibility="collapsed")
v3 = st.radio("V3", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="v3", label_visibility="collapsed")
v4 = st.radio("V4", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="v4", label_visibility="collapsed")
st.markdown("<p class='veto-label'>Fins a 4 terminacions prohibides</p>", unsafe_allow_html=True)

st.markdown("### 4. Selectors Especialitzats")
col1, col2 = st.columns(2)
with col1:
    sel_m_status = st.radio("Mellizos (1-4)", ["OFF", "ON"], horizontal=True)
with col2:
    sel_c_status = st.radio("Clumps (3-6)", ["OFF", "ON"], horizontal=True)

# --- MOTOR DE CÀLCUL ULTRA-ROBUST ---
def generar_sistema():
    resultats = []
    # Perfils de 7 números (pactats: 2/1/1/2/1, etc.)
    perfils_base = [
        [2,1,1,2,1], [2,1,2,1,1], [2,2,1,1,1], [1,1,2,2,1], [1,2,1,2,1],
        [1,2,2,1,1], [1,1,1,2,2], [1,1,2,1,2], [1,2,1,1,2], [2,1,1,1,2]
    ]
    reps_demanades = [r for r in [sel_un_rep1, sel_un_rep2] if r != "Cap"]
    vetos = [v for v in [v1, v2, v3, v4] if v != "Cap"]
    mells_nums = [11, 22, 33, 44]
    
    dec_map = {"1-10":0, "11-20":1, "21-30":2, "31-40":3, "41-49":4}

    for i in range(1, 7):
        success = False
        p_target = 3 if i in [1, 3, 5] else 4
        intentos_restants = 100000  # Límit augmentat a 100k per aposta
        
        while not success and intentos_restants > 0:
            intentos_restants -= 1
            perfil = random.choice(perfils_base)
            
            # Filtre Selector Decenes
            if sel_decena_koixa != "Cap" and perfil[dec_map[sel_decena_koixa]] != 1: continue

            # Construcció per blocs
            temp_comb = []
            blocs = [list(range(1,11)), list(range(11,21)), list(range(21,31)), list(range(31,41)), list(range(41,50))]
            possible = True
            for idx, qty in enumerate(perfil):
                pool = [n for n in blocs[idx] if n % 10 not in vetos]
                if len(pool) < qty: possible = False; break
                temp_comb.extend(random.sample(pool, qty))
            
            if not possible: continue
            
            # 1. Filtre Paritat
            if sum(1 for n in temp_comb if n % 2 == 0) != p_target: continue
            
            # 2. Filtre Unitats Repetides (Estricte)
            units = [n % 10 for n in temp_comb]
            counts = {x: units.count(x) for x in set(units)}
            reps_reals = [u for u, c in counts.items() if c > 1]
            if not (all(r in reps_reals for r in reps_demanades) and all(r in reps_demanades for r in reps_reals)): continue
            if any(v > 2 for v in counts.values()): continue

            # 3. Mellizos (Apostes 1-4)
            present_mells = [n for n in temp_comb if n in mells_nums]
            if sel_m_status == "ON" and i <= 4:
                if len(present_mells) != 1: continue
                if present_mells[0] % 10 in vetos: continue # Seguretat extra
            elif len(present_mells) > 0: continue
            
            # 4. Clumps (Apostes 3-6)
            temp_comb.sort()
            seguits = sum(1 for j in range(len(temp_comb)-1) if temp_comb[j+1] == temp_comb[j]+1)
            if sel_c_status == "ON" and i >= 3:
                if seguits != 1: continue
            elif seguits > 0: continue
            
            # 5. Filtre Creuat (No més de 2 números iguals entre les apostes generades)
            if any(len(set(temp_comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(temp_comb)
            success = True
            
    return resultats

# --- BOTÓ I ACCIÓ ---
if st.button("🚀 GENERAR 6 COMBINACIONS MÚLTIPLES"):
    with st.spinner('Pescant combinacions òptimes...'):
        apostes = generar_sistema()
        
    if len(apostes) < 6:
        st.error("⚠️ Filtres matemàticament massa estrets. Prova de reduir els vetos d'unitat.")
    else:
        for idx, a in enumerate(apostes):
            par_txt = "3P/4S" if (idx+1) in [1, 3, 5] else "4P/3S"
            st.markdown(f"**Aposta {idx+1} ({par_txt})**")
            st.success(" - ".join(map(str, a)))

st.markdown("<br><br>", unsafe_allow_html=True)
