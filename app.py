import streamlit as st
import random

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Prometeus Primitiva", page_icon="🔥", layout="centered")

# --- ESTILS VISUALS ---
st.markdown("""
    <style>
    .stButton>button { height: 75px; font-size: 24px; font-weight: bold; border-radius: 15px; background-color: #FF4B4B; color: white; margin-top: 25px; box-shadow: 0px 4px 10px rgba(0,0,0,0.2); }
    h3 { margin-top: 25px; color: #1E1E1E; border-bottom: 2px solid #FF4B4B; width: 100%; padding-bottom: 8px; font-family: 'Helvetica', sans-serif; }
    .desc-text { font-size: 14px; color: #555; margin-bottom: 15px; font-style: italic; line-height: 1.4; }
    div.row-widget.stRadio > div{ flex-direction:row; justify-content: center; gap: 8px; flex-wrap: wrap; }
    .stSuccess { font-size: 22px !important; font-weight: bold; border-radius: 10px; }
    .veto-sub { font-size: 12px; color: #888; text-align: center; margin-top: -10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 PROMETEUS ULTRA")
st.write("FULMINANT ULTIMATE EDITION.")

# --- PANELLS DE CONFIGURACIÓ AMB DESCRIPCIONS ---

st.markdown("### 1. Desenes")
st.markdown("<p class='desc-text'>Controla la densitat per grup. Tria quina desena vols que quedi limitada a un sol número seguint els perfils 2/1/1/2/1.</p>", unsafe_allow_html=True)
sel_decena_koixa = st.radio("D", ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"], horizontal=True, label_visibility="collapsed")

st.markdown("### 2. Unitats Repe")
st.markdown("<p class='desc-text'>Força terminacions dobles. Pots triar fins a 2 unitats (0-9) perquè apareguin exactament dues vegades cada una en la combinació.</p>", unsafe_allow_html=True)
sel_un_rep1 = st.radio("U1", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="u1", label_visibility="collapsed")
sel_un_rep2 = st.radio("U2", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="u2", label_visibility="collapsed")

st.markdown("### 3. Unitats Vetades")
st.markdown("<p class='desc-text'>Criba de terminacions prohibides. Elimina totalment de les teves apostes fins a 4 terminacions que no vulguis que surtin.</p>", unsafe_allow_html=True)
v1 = st.radio("V1", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="v1", label_visibility="collapsed")
st.markdown("<p class='veto-sub'>Veto 1</p>", unsafe_allow_html=True)
v2 = st.radio("V2", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="v2", label_visibility="collapsed")
st.markdown("<p class='veto-sub'>Veto 2</p>", unsafe_allow_html=True)
v3 = st.radio("V3", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="v3", label_visibility="collapsed")
st.markdown("<p class='veto-sub'>Veto 3</p>", unsafe_allow_html=True)
v4 = st.radio("V4", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="v4", label_visibility="collapsed")
st.markdown("<p class='veto-sub'>Veto 4</p>", unsafe_allow_html=True)

st.markdown("### 4. Filtre Mellizos")
st.markdown("<p class='desc-text'>Activa la presència de números bessons (11, 22, 33, 44) exclusivament per a les apostes 1, 2, 3 i 4.</p>", unsafe_allow_html=True)
sel_m_status = st.radio("M", ["OFF", "ON"], horizontal=True, label_visibility="collapsed")

st.markdown("### 5. Filtre Clumps")
st.markdown("<p class='desc-text'>Força l'aparició d'una única parella de números seguits (consecutius) en les apostes 3, 4, 5 i 6.</p>", unsafe_allow_html=True)
sel_c_status = st.radio("C", ["OFF", "ON"], horizontal=True, label_visibility="collapsed")

st.divider()

# --- MOTOR DE CÀLCUL (AMB 100k INTENTS) ---
def validar_terminacions(nums, reps_demanades):
    units = [n % 10 for n in nums]
    counts = {x: units.count(x) for x in set(units)}
    reps_reals = [u for u, c in counts.items() if c > 1]
    if not (all(r in reps_reals for r in reps_demanades) and all(r in reps_demanades for r in reps_reals)): return False
    return all(c <= 2 for c in counts.values())

def generar_sistema():
    resultats = []
    perfils_base = [[2,1,1,2,1],[2,1,2,1,1],[2,2,1,1,1],[1,1,2,2,1],[1,2,1,2,1],[1,2,2,1,1],[1,1,1,2,2],[1,1,2,1,2],[1,2,1,1,2],[2,1,1,1,2]]
    reps_demanades = [r for r in [sel_un_rep1, sel_un_rep2] if r != "Cap"]
    vetos = [v for v in [v1, v2, v3, v4] if v != "Cap"]
    mells_nums = [11, 22, 33, 44]
    dec_map = {"1-10":0, "11-20":1, "21-30":2, "31-40":3, "41-49":4}

    for i in range(1, 7):
        success = False
        p_target = 3 if i in [1,3,5] else 4
        intentos = 100000 
        
        while not success and intentos > 0:
            intentos -= 1
            perfil = random.choice(perfils_base)
            if sel_decena_koixa != "Cap" and perfil[dec_map[sel_decena_koixa]] != 1: continue

            temp_comb = []
            blocs = [list(range(1,11)), list(range(11,21)), list(range(21,31)), list(range(31,41)), list(range(41,50))]
            possible = True
            for idx, qty in enumerate(perfil):
                pool = [n for n in blocs[idx] if n % 10 not in vetos]
                if len(pool) < qty: possible = False; break
                temp_comb.extend(random.sample(pool, qty))
            
            if not possible: continue
            if sum(1 for n in temp_comb if n % 2 == 0) != p_target: continue
            if not validar_terminacions(temp_comb, reps_demanades): continue

            present_mells = [n for n in temp_comb if n in mells_nums]
            if sel_m_status == "ON" and i <= 4:
                if len(present_mells) != 1: continue
            elif len(present_mells) > 0: continue
            
            temp_comb.sort()
            seguits = sum(1 for j in range(len(temp_comb)-1) if temp_comb[j+1] == temp_comb[j]+1)
            if sel_c_status == "ON" and i >= 3:
                if seguits != 1: continue
            elif seguits > 0: continue
            
            if any(len(set(temp_comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(temp_comb)
            success = True
            
    return resultats

# --- ACCIÓ I RESULTATS ---
if st.button("🚀 GENERAR 6 APOSTES PROMETEUS"):
    with st.spinner('Aplicant cribratge...'):
        apostes = generar_sistema()
        
    if len(apostes) < 6:
        st.error("⚠️ Filtres massa estrictes. Prova de reduir els vetos.")
    else:
        for idx, a in enumerate(apostes):
            par_txt = "3P/4S" if (idx+1) in [1,3,5] else "4P/3S"
            st.markdown(f"**Aposta {idx+1} ({par_txt})**")
            st.success(" - ".join(map(str, a)))

st.markdown("<br><br>", unsafe_allow_html=True)
