import streamlit as st
import random

# Configuració de la pàgina
st.set_page_config(page_title="Prometeus Primitiva", page_icon="🔥", layout="centered")

# --- ESTILS ---
st.markdown("""
    <style>
    .stButton>button { height: 70px; font-size: 22px; font-weight: bold; border-radius: 15px; background-color: #FF4B4B; color: white; margin-top: 20px; }
    h3 { margin-top: 25px; color: #333; border-bottom: 2px solid #FF4B4B; width: 100%; }
    /* Estil per als radio buttons horitzontals */
    div.row-widget.stRadio > div{ flex-direction:row; justify-content: center; gap: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 Prometeus Primitiva")

# --- PANELLS DE CONFIGURACIÓ (ESTIL BOTONS HORITZONTALS) ---

st.markdown("### 1. Selector de Decenes")
st.write("Desena amb NOMÉS 1 número:")
sel_decena_koixa = st.radio("D", ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"], horizontal=True, label_visibility="collapsed")

st.markdown("### 2. Selector d'Unitat Repetida (1)")
st.write("Tria la primera terminació que vols que es repeteixi:")
sel_un_rep1 = st.radio("U1", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, label_visibility="collapsed")

st.markdown("### 3. Selector d'Unitat Repetida (2)")
st.write("Tria la segona terminació (opcional):")
sel_un_rep2 = st.radio("U2", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, label_visibility="collapsed")

st.markdown("### 4. Selector d'Unitat Vetada")
st.write("Terminació que vols PROHIBIR en aquesta generació:")
sel_un_vet = st.radio("V", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], horizontal=True, label_visibility="collapsed")

st.markdown("### 5. Selectors Especials")
col1, col2 = st.columns(2)
with col1:
    sel_mellizos = st.toggle("ACTIVA MELLIZOS", value=False)
with col2:
    sel_clumps = st.toggle("ACTIVA CLUMPS", value=False)

st.divider()

# --- LÒGICA DE CÀLCUL ---

def validar_terminacions(nums, reps_demanades):
    units = [n % 10 for n in nums]
    counts = {x: units.count(x) for x in set(units)}
    reps_reals = [u for u, c in counts.items() if c > 1]
    
    # Comprovar que les repetides són exactament les demanades
    if not all(r in reps_reals for r in reps_demanades): return False
    if not all(r in reps_demanades for r in reps_reals): return False
    # Màxim 2 cops cada unitat
    return all(c <= 2 for c in counts.values())

def generar_sistema():
    resultats = []
    perfils_base = [[2,1,1,2,1],[2,1,2,1,1],[2,2,1,1,1],[1,1,2,2,1],[1,2,1,2,1],[1,2,2,1,1],[1,1,1,2,2],[1,1,2,1,2],[1,2,1,1,2],[2,1,1,1,2]]
    
    # Processar unitats repetides
    reps_demanades = []
    if sel_un_rep1 != "Cap": reps_demanades.append(sel_un_rep1)
    if sel_un_rep2 != "Cap": reps_demanades.append(sel_un_rep2)
    
    for i in range(1, 7):
        success = False
        paritat_parells = 3 if i in [1,3,5] else 4
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
                # Filtre veto (ara només 1 veto per simplificar l'estil radio, però robust)
                pool = [n for n in blocs[idx] if (sel_un_vet == "Cap" or n % 10 != sel_un_vet)]
                if len(pool) < qty: possible = False; break
                comb.extend(random.sample(pool, qty))
            
            if not possible or len(comb) != 7: continue
            
            # Mellizos (1-4)
            present_mells = [n for n in comb if n in [11, 22, 33, 44]]
            if sel_mellizos and i <= 4:
                if len(present_mells) != 1: continue
            elif not sel_mellizos and len(present_mells) > 0: continue
            
            # Clumps (3-6)
            comb.sort()
            seguits = sum(1 for j in range(len(comb)-1) if comb[j+1] == comb[j]+1)
            if sel_clumps and i >= 3:
                if seguits != 1: continue
            elif not sel_clumps and seguits > 0: continue
            
            # Paritat i Terminacions
            if sum(1 for n in comb if n % 2 == 0) != paritat_parells: continue
            if not validar_terminacions(comb, reps_demanades): continue
            
            # Filtre Creuat (max 2 iguals)
            if any(len(set(comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(comb)
            success = True
    return resultats

# --- BOTÓ I RESULTATS ---

if st.button("🚀 GENERAR 6 COMBINACIONS"):
    apostes = generar_sistema()
    if len(apostes) < 6:
        st.error("⚠️ Filtres massa estrictes. Prova de canviar els selectors.")
    else:
        for idx, a in enumerate(apostes):
            st.markdown(f"**Aposta {idx+1}**")
            st.success(" - ".join(map(str, a)))
