import streamlit as st
import random

# Configuració de la pàgina
st.set_page_config(page_title="Prometeus Primitiva", page_icon="🔥", layout="centered")

# --- ESTILS ---
st.markdown("""
    <style>
    .stButton>button { height: 60px; font-size: 20px; font-weight: bold; border-radius: 15px; background-color: #FF4B4B; color: white; }
    .panel-box { padding: 20px; border: 1px solid #ddd; border-radius: 10px; margin-bottom: 20px; background-color: #fafafa; }
    h3 { margin-bottom: 15px; color: #333; border-bottom: 2px solid #FF4B4B; width: fit-content; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 Prometeus Primitiva")
st.write("Generador robust amb filtres bloquejats.")

# --- PANELLS DE CONFIGURACIÓ (TOT DESPLEGAT) ---

st.markdown("### 1. Selector de Decenes")
st.write("Tria quina desena vols forçar que tingui NOMÉS 1 número:")
sel_decena_koixa = st.radio("", ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"], horizontal=True, label_visibility="collapsed")

st.divider()

st.markdown("### 2. Selector d'Unitats Repetides")
st.write("Tria quines terminacions (0-9) vols que apareguin repetides (Max 2):")
sel_un_rep = st.multiselect("Terminacions forçades:", list(range(10)), max_selections=2, label_visibility="collapsed")

st.divider()

st.markdown("### 3. Selector d'Unitats Vetades")
st.write("Tria fins a 4 terminacions que NO vols que apareguin:")
sel_un_vet = st.multiselect("Terminacions prohibides:", list(range(10)), max_selections=4, label_visibility="collapsed")

st.divider()

st.markdown("### 4. Selectors Especials")
col1, col2 = st.columns(2)
with col1:
    sel_mellizos = st.toggle("ACTIVA MELLIZOS (Apostes 1-4)", value=False)
with col2:
    sel_clumps = st.toggle("ACTIVA CLUMPS (Apostes 3-6)", value=False)

st.divider()

# --- MOTOR DE CÀLCUL ROBUST ---

def validar_terminacions(nums, sel_rep):
    units = [n % 10 for n in nums]
    counts = {x: units.count(x) for x in set(units)}
    reps_reals = [u for u, c in counts.items() if c > 1]
    
    if sel_rep:
        # Ha de tenir les repetides demanades i NOMÉS aquestes
        if not all(r in reps_reals for r in sel_rep): return False
        if not all(r in sel_rep for r in reps_reals): return False
    else:
        # Si no hi ha selecció, màxim una parella de terminacions repetides
        if len(reps_reals) > 1: return False
        
    return all(c <= 2 for c in counts.values()) # Màxim 2 números per terminació

def generar_sistema():
    resultats = []
    # Perfils de 7 números (sumen 7)
    perfils_base = [
        [2,1,1,2,1], [2,1,2,1,1], [2,2,1,1,1], [1,1,2,2,1], [1,2,1,2,1],
        [1,2,2,1,1], [1,1,1,2,2], [1,1,2,1,2], [1,2,1,1,2], [2,1,1,1,2]
    ]
    
    dec_map = {"1-10":0, "11-20":1, "21-30":2, "31-40":3, "41-49":4}
    mells_nums = [11, 22, 33, 44]

    for i in range(1, 7): # Generem 6 apostes
        success = False
        intentos = 0
        paritat_parells = 3 if i in [1, 3, 5] else 4
        
        while not success and intentos < 10000:
            intentos += 1
            comb = []
            perfil = random.choice(perfils_base)
            
            # Filtre Selector Decenes
            if sel_decena_koixa != "Cap":
                if perfil[dec_map[sel_decena_koixa]] != 1: continue

            # Generació per blocs
            blocs = [list(range(1,11)), list(range(11,21)), list(range(21,31)), list(range(31,41)), list(range(41,50))]
            possible = True
            for idx, qty in enumerate(perfil):
                pool = [n for n in blocs[idx] if n % 10 not in sel_un_vet]
                if len(pool) < qty:
                    possible = False
                    break
                comb.extend(random.sample(pool, qty))
            
            if not possible or len(comb) != 7: continue
            
            # Filtre Mellizos (Apostes 1-4)
            present_mells = [n for n in comb if n in mells_nums]
            if sel_mellizos and i <= 4:
                if len(present_mells) != 1: continue
            elif not sel_mellizos and len(present_mells) > 0: continue
            
            # Filtre Clumps (Seguits - Apostes 3-6)
            comb.sort()
            seguits = sum(1 for j in range(len(comb)-1) if comb[j+1] == comb[j]+1)
            if sel_clumps and i >= 3:
                if seguits != 1: continue
            elif not sel_clumps and seguits > 0: continue
            
            # Paritat (Parells/Senars)
            if sum(1 for n in comb if n % 2 == 0) != paritat_parells: continue
            
            # Unitats repetides
            if not validar_terminacions(comb, sel_un_rep): continue
            
            # FILTRE CREUAT: No més de 2 iguals amb les apostes ja generades
            if any(len(set(comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(comb)
            success = True
            
    return resultats

# --- ACCIÓ I RESULTATS ---

if st.button("🚀 GENERAR 6 COMBINACIONS MÚLTIPLES"):
    final_apostes = generar_sistema()
    
    if len(final_apostes) < 6:
        st.error("⚠️ Impossible trobar combinacions amb aquests filtres. Relaxa els vetos d'unitats.")
    else:
        for idx, aposta in enumerate(final_apostes):
            paritat_txt = "3P/4S" if (idx+1) in [1,3,5] else "4P/3S"
            st.markdown(f"**Aposta {idx+1} ({paritat_txt})**")
            st.success(" - ".join(map(str, aposta)))

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Dissenyat per a ús personal. Filtres de criba bloquejats segons especificacions.")
