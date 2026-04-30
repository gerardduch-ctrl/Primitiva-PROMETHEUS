import streamlit as st
import random
from collections import Counter

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Prometeus Ultra V1.2", page_icon="🔥", layout="centered")

# --- ESTILS VISUALS ---
st.markdown("""
    <style>
    .stButton>button { height: 75px; font-size: 24px; font-weight: bold; border-radius: 15px; background-color: #FF4B4B; color: white; margin-top: 25px; box-shadow: 0px 4px 10px rgba(0,0,0,0.2); }
    h3 { margin-top: 25px; color: #1E1E1E; border-bottom: 2px solid #FF4B4B; width: 100%; padding-bottom: 8px; }
    .desc-text { font-size: 14px; color: #555; margin-bottom: 15px; font-style: italic; line-height: 1.4; }
    div.row-widget.stRadio > div{ flex-direction:row; justify-content: center; gap: 8px; flex-wrap: wrap; }
    .stSuccess { font-size: 22px !important; font-weight: bold; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 PROMETEUS ULTRA")
st.write("FULMINANT ULTIMATE EDITION. V.1.2 (Hierarchy Fixed)")

# --- PANELLS DE CONFIGURACIÓ ---

st.markdown("### 1. Parrilla de Favorits (Màx. 12)")
st.markdown("<p class='desc-text'>S'inclourà 1 per aposta (màx. 2 repeticions). ATENCIÓ: Els vetos i el filtre Bessons tenen prioritat i poden anul·lar aquests números.</p>", unsafe_allow_html=True)
fav_nums_input = st.multiselect("Selecciona els teus números:", list(range(1, 50)), max_selections=12, label_visibility="collapsed")

st.markdown("### 2. Desenes")
sel_decena_koixa = st.radio("Limitació Desena (Perfil 1):", ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"], horizontal=True)

st.markdown("### 3. Unitats Repe")
c1, c2 = st.columns(2)
with c1: sel_un_rep1 = st.radio("Repetició 1:", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True)
with c2: sel_un_rep2 = st.radio("Repetició 2:", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True)

st.markdown("### 4. Unitats Vetades")
vetos_raw = st.multiselect("Veta terminacions (tenen prioritat total):", list(range(0, 10)), max_selections=4)

st.markdown("### 5. Filtre BESSONS")
sel_m_status = st.radio("Bessons (11, 22, 33, 44):", ["OFF", "ON"], horizontal=True)

st.divider()

# --- MOTOR DE CÀLCUL ---

def validar_terminacions(nums, reps_demanades):
    units = [n % 10 for n in nums]
    counts = Counter(units)
    reps_reals = [u for u, c in counts.items() if c > 1]
    if not (all(r in reps_reals for r in reps_demanades) and all(r in reps_demanades for r in reps_reals)): return False
    return all(c <= 2 for c in counts.values())

def generar_sistema():
    resultats = []
    global_favs_used = []
    perfils_base = [[2,1,1,2,1],[2,1,2,1,1],[2,2,1,1,1],[1,1,2,2,1],[1,2,1,2,1],[1,2,2,1,1],[1,1,1,2,2],[1,1,2,1,2],[1,2,1,1,2],[2,1,1,1,2]]
    reps_demanades = [r for r in [sel_un_rep1, sel_un_rep2] if r != "Cap"]
    mells_nums = [11, 22, 33, 44]
    primos_impares = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    dec_map = {"1-10":0, "11-20":1, "21-30":2, "31-40":3, "41-49":4}

    # FILTRADO PREVIO DE FAVORITOS SEGÚN JERARQUÍA
    fav_filtrados = [n for n in fav_nums_input if (n % 10 not in vetos_raw)]
    if sel_m_status == "OFF":
        fav_filtrados = [n for n in fav_filtrados if n not in mells_nums]

    if not fav_filtrados: return "ERROR_FAVS_EMPTY"

    for i in range(1, 7):
        success = False
        p_target = 3 if i in [1,3,5] else 4 # Pares: Apuestas 1,3,5 -> 3P/4I | 2,4,6 -> 4P/3I
        primos_target = 3 if i in [1,3,5] else 2
        intentos = 80000 
        
        while not success and intentos > 0:
            intentos -= 1
            perfil = random.choice(perfils_base)
            if sel_decena_koixa != "Cap" and perfil[dec_map[sel_decena_koixa]] != 1: continue

            # Seleccionar favorito disponible (máx 2 usos)
            counts_favs = Counter(global_favs_used)
            favs_compatibles = [n for n in fav_filtrados if counts_favs[n] < 2]
            if not favs_compatibles: favs_compatibles = fav_filtrados
            
            chosen_fav = random.choice(favs_compatibles)
            dec_fav = (chosen_fav - 1) // 10 if chosen_fav < 50 else 4
            if dec_fav > 4: dec_fav = 4
            
            temp_comb = [chosen_fav]
            blocs = [list(range(1,11)), list(range(11,21)), list(range(21,31)), list(range(31,41)), list(range(41,50))]
            possible = True
            
            for idx, qty in enumerate(perfil):
                needed = qty - 1 if idx == dec_fav else qty
                if needed < 0: possible = False; break
                
                pool = [n for n in blocs[idx] if n % 10 not in vetos_raw and n != chosen_fav]
                if sel_m_status == "OFF":
                    pool = [n for n in pool if n not in mells_nums]
                
                if len(pool) < needed: possible = False; break
                temp_comb.extend(random.sample(pool, needed))
            
            if not possible: continue
            
            # Filtros de validación
            if sum(1 for n in temp_comb if n % 2 == 0) != p_target: continue
            if sum(1 for n in temp_comb if n in primos_impares) != primos_target: continue
            if not validar_terminacions(temp_comb, reps_demanades): continue

            # Filtro Bessons (para el resto de la combinación)
            if sel_m_status == "ON" and i <= 4:
                if sum(1 for n in temp_comb if n in mells_nums) < 1: continue
            
            temp_comb.sort()
            
            # Filtro Seguits, Rango y Suma
            seguits = sum(1 for j in range(len(temp_comb)-1) if temp_comb[j+1] == temp_comb[j]+1)
            if seguits != 1: continue
            if not (temp_comb[0] <= 15 and temp_comb[-1] >= 38): continue
            if not (140 <= sum(temp_comb) <= 200): continue
            
            if any(len(set(temp_comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(temp_comb)
            global_favs_used.append(chosen_fav)
            success = True
            
    return resultats

# --- ACCIÓ I RESULTATS ---
if st.button("🚀 GENERAR 6 APOSTES PROMETEUS"):
    if not fav_nums_input:
        st.warning("⚠️ Selecciona números a la parrilla de favorits.")
    else:
        with st.spinner('Calculant amb jerarquia estricta...'):
            apostes = generar_sistema()
            
        if apostes == "ERROR_FAVS_EMPTY":
            st.error("❌ Els teus números favorits han estat anul·lats pels Vetos o el filtre Bessons. Canvia la selecció.")
        elif len(apostes) < 6:
            st.error("⚠️ Combinació de filtres massa estricta. Revisa els Vetos o la Suma.")
        else:
            for idx, a in enumerate(apostes):
                par_txt = "3P/4I" if (idx+1) in [1,3,5] else "4P/3I"
                st.markdown(f"**Aposta {idx+1} ({par_txt})**")
                st.success(" - ".join(map(str, a)))
