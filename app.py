import streamlit as st
import random

# Configuració de la pàgina
st.set_page_config(page_title="Prometeus Primitiva", page_icon="🔥", layout="centered")

# --- ESTILS ---
st.markdown("""
    <style>
    .stButton>button { height: 70px; font-size: 22px; font-weight: bold; border-radius: 15px; background-color: #FF4B4B; color: white; margin-top: 20px; }
    h3 { margin-top: 25px; color: #333; border-bottom: 2px solid #FF4B4B; width: 100%; padding-bottom: 5px; }
    div.row-widget.stRadio > div{ flex-direction:row; justify-content: center; gap: 10px; }
    .info-text { font-size: 14px; color: #666; margin-bottom: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 Prometeus Primitiva")

# --- PANELLS DE CONFIGURACIÓ TOTALMENT DESPLEGATS ---

st.markdown("### 1. Selector de Decenes")
st.write("Tria la desena que vols que tingui NOMÉS 1 número:")
sel_decena_koixa = st.radio("D", ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"], horizontal=True, label_visibility="collapsed")

st.markdown("### 2. Selector d'Unitat Repetida (1)")
st.write("Primera terminació a repetir (apareixerà 2 cops):")
sel_un_rep1 = st.radio("U1", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="u1", label_visibility="collapsed")

st.markdown("### 3. Selector d'Unitat Repetida (2)")
st.write("Segona terminació a repetir (opcional):")
sel_un_rep2 = st.radio("U2", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="u2", label_visibility="collapsed")

st.markdown("### 4. Selector d'Unitat Vetada")
st.write("Terminació que vols PROHIBIR totalment:")
sel_un_vet = st.radio("V", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, key="v1", label_visibility="collapsed")

st.markdown("### 5. Selector Mellizos (11, 22, 33, 44)")
st.write("Estat actual del filtre de números bessons:")
sel_m_status = st.radio("M", ["OFF (Cap)", "ON (Apostes 1 a 4)"], horizontal=True, label_visibility="collapsed")
st.markdown("<p class='info-text'>Si està ON, les primeres 4 apostes tindran un número bessó (excepte si la unitat està vetada).</p>", unsafe_allow_html=True)

st.markdown("### 6. Selector Clumps (Números seguits)")
st.write("Estat actual del filtre de consecutius:")
sel_c_status = st.radio("C", ["OFF (Cap)", "ON (Apostes 3 a 6)"], horizontal=True, label_visibility="collapsed")
st.markdown("<p class='info-text'>Si està ON, de l'aposta 3 a la 6 hi haurà exactament UNA parella de números seguits.</p>", unsafe_allow_html=True)

st.divider()

# --- LÒGICA DE CÀLCUL (BLOQUEJADA) ---

def validar_terminacions(nums, reps_demanades):
    units = [n % 10 for n in nums]
    counts = {x: units.count(x) for x in set(units)}
    reps_reals = [u for u, c in counts.items() if c > 1]
    if not all(r in reps_reals for r in reps_demanades): return False
    if not all(r in reps_demanades for r in reps_reals): return False
    return all(c <= 2 for c in counts.values())

def generar_sistema():
    resultats = []
    perfils_base = [[2,1,1,2,1],[2,1,2,1,1],[2,2,1,1,1],[1,1,2,2,1],[1,2,1,2,1],[1,2,2,1,1],[1,1,1,2,2],[1,1,2,1,2],[1,2,1,1,2],[2,1,1,1,2]]
    reps_demanades = [r for r in [sel_un_rep1, sel_un_rep2] if r != "Cap"]
    mells_nums = [11, 22, 33, 44]
    
    for i in range(1, 7):
        success = False
        p_parells = 3 if i in [1, 3, 5] else 4
        intentos = 0
        
        while not success and intentos < 5000:
            intentos += 1
            comb = []
            perfil = random.choice(perfils_base)
            
            # Filtre Decena Koixa
            dec_map = {"1-10":0, "11-20":1, "21-30":2, "31-40":3, "41-49":4}
            if sel_decena_koixa != "Cap" and perfil[dec_map[sel_decena_koixa]] != 1: continue

            # Generació
            blocs = [list(range(1,11)), list(range(11,21)), list(range(21,31)), list(range(31,41)), list(range(41,50))]
            possible = True
            for idx, qty in enumerate(perfil):
                pool = [n for n in blocs[idx] if (sel_un_vet == "Cap" or n % 10 != sel_un_vet)]
                if len(pool) < qty: possible = False; break
                comb.extend(random.sample(pool, qty))
            
            if not possible or len(comb) != 7: continue
            
            # Mellizos
            present_mells = [n for n in comb if n in mells_nums]
            if "ON" in sel_m_status and i <= 4:
                if len(present_mells) != 1: continue
            elif len(present_mells) > 0: continue
            
            # Clumps
            comb.sort()
            seguits = sum(1 for j in range(len(comb)-1) if comb[j+1] == comb[j]+1)
            if "ON" in sel_c_status and i >= 3:
                if seguits != 1: continue
            elif seguits > 0: continue
            
            # Paritat i Terminacions
            if sum(1 for n in comb if n % 2 == 0) != p_parells: continue
            if not validar_terminacions(comb, reps_demanades): continue
            
            # Filtre Creuat (max 2 iguals)
            if any(len(set(comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(comb)
            success = True
    return resultats

# --- BOTÓ I RESULTATS ---

if st.button("🚀 GENERAR LES 6 APOSTES"):
    apostes = generar_sistema()
    if len(apostes) < 6:
        st.error("⚠️ Filtres massa estrictes. Prova de canviar els selectors.")
    else:
        for idx, a in enumerate(apostes):
            par_info = "3P/4S" if (idx+1) in [1, 3, 5] else "4P/3S"
            st.markdown(f"**Aposta {idx+1} ({par_info})**")
            st.success(" - ".join(map(str, a)))

st.markdown("<br><br>", unsafe_allow_html=True)
