import streamlit as st
import random
from collections import Counter

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Prometeus Ultra Mobile", page_icon="🔥", layout="centered")

# --- ESTILS VISUALS OPTIMITZATS PER MÒBIL ---
st.markdown("""
    <style>
    .stButton>button { height: 70px; font-size: 22px; font-weight: bold; border-radius: 15px; background-color: #FF4B4B; color: white; margin-top: 20px; }
    .stCheckbox { margin-bottom: 5px; }
    h3 { background-color: #f0f2f6; padding: 10px; border-radius: 8px; border-left: 5px solid #FF4B4B; font-size: 18px; margin-top: 20px; }
    /* Forçar graella de 5 per a mòbil */
    [data-testid="column"] { min-width: 18% !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 PROMETEUS V.2 MOBILE")

# --- 1. FAVORITS (GRAELLA 5 COLUMNES) ---
st.markdown("### 🎯 1. FAVORITS (OBLIGATORI 1)")
fav_nums = []
cols_fav = st.columns(5)
for n in range(1, 50):
    with cols_fav[(n-1)%5]:
        if st.checkbox(f"{n}", key=f"fav_{n}"):
            fav_nums.append(n)

# --- 2. VETOS (GRAELLA 5 COLUMNES) ---
st.markdown("### 🚫 2. UNITATS VETADES")
vetos = []
cols_veto = st.columns(5)
for v in range(10):
    with cols_veto[v%5]:
        if st.checkbox(f"U-{v}", key=f"v_{v}"):
            vetos.append(v)

# --- 3. UNITATS REPES (DESPLEGAT) ---
st.markdown("### 👯 3. UNITATS REPES")
st.write("Tria fins a 2 terminacions que vols que surtin dobles:")
reps_demanades = []
cols_rep = st.columns(5)
for r in range(10):
    with cols_rep[r%5]:
        if st.checkbox(f"R-{r}", key=f"rep_{r}"):
            reps_demanades.append(r)

# --- 4. ALTRES FILTRES ---
st.markdown("### 📊 4. DESENA LIMITADA (PERFIL 1)")
sel_decena = st.radio("Tria desena:", ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"], horizontal=True, label_visibility="collapsed")

st.markdown("### 💎 5. FILTRE BESSONS")
bessons_on = st.radio("Estat Bessons:", ["OFF", "ON"], horizontal=True, label_visibility="collapsed")

st.divider()

# --- MOTOR DE CÀLCUL (FUERZA BRUTA 1M) ---
def generar_sistema():
    resultats = []
    global_favs_used = []
    perfils_base = [[2,1,1,2,1],[2,1,2,1,1],[2,2,1,1,1],[1,1,2,2,1],[1,2,1,2,1],[1,2,2,1,1],[1,1,1,2,2],[1,1,2,1,2],[1,2,1,1,2],[2,1,1,1,2]]
    primos_impares = [3,5,7,11,13,17,19,23,29,31,37,41,43,47]
    mells_nums = [11, 22, 33, 44]
    dec_map = {"1-10":0, "11-20":1, "21-30":2, "31-40":3, "41-49":4}

    # Jerarquia: Neteja de favorits
    fav_disponibles = [n for n in fav_nums if (n % 10 not in vetos)]
    if bessons_on == "OFF":
        fav_disponibles = [n for n in fav_disponibles if n not in mells_nums]
    
    if not fav_disponibles and len(fav_nums) > 0: return "ERROR_FAV"

    for i in range(1, 7):
        p_target = 3 if i in [1,3,5] else 4 
        primos_target = 3 if i in [1,3,5] else 2
        success = False
        intentos = 1000000 
        
        while not success and intentos > 0:
            intentos -= 1
            perfil = random.choice(perfils_base)
            if sel_decena != "Cap" and perfil[dec_map[sel_decena]] != 1: continue

            # Selecció de favorit
            c_favs = Counter(global_favs_used)
            fav_candidats = [n for n in fav_disponibles if c_favs[n] < 2]
            if not fav_candidats: fav_candidats = fav_disponibles
            chosen_fav = random.choice(fav_candidats)
            dec_idx = (chosen_fav-1)//10 if chosen_fav < 41 else 4
            
            temp_comb = [chosen_fav]
            blocs = [list(range(1,11)), list(range(11,21)), list(range(21,31)), list(range(31,41)), list(range(41,50))]
            
            possible = True
            for idx, qty in enumerate(perfil):
                qty_act = qty - 1 if idx == dec_idx else qty
                if qty_act < 0: possible = False; break
                pool = [n for n in blocs[idx] if n % 10 not in vetos and n != chosen_fav]
                if bessons_on == "OFF": pool = [n for n in pool if n not in mells_nums]
                if len(pool) < qty_act: possible = False; break
                temp_comb.extend(random.sample(pool, qty_act))
            
            if not possible: continue
            if sum(1 for n in temp_comb if n % 2 == 0) != p_target: continue
            if sum(1 for n in temp_comb if n in primos_impares) != primos_target: continue
            
            # Repetició terminacions
            u_temp = [n % 10 for n in temp_comb]
            c_u = Counter(u_temp)
            r_reals = [u for u, c in c_u.items() if c > 1]
            if not (all(r in r_reals for r in reps_demanades[:2]) and all(r in reps_demanades[:2] for r in r_reals)): continue
            if any(c > 2 for c in c_u.values()): continue

            if bessons_on == "ON" and i <= 4:
                if sum(1 for n in temp_comb if n in mells_nums) < 1: continue
            
            temp_comb.sort()
            seguits = sum(1 for j in range(len(temp_comb)-1) if temp_comb[j+1] == temp_comb[j]+1)
            if seguits != 1: continue
            if not (temp_comb[0] <= 15 and temp_comb[-1] >= 38): continue
            if not (140 <= sum(temp_comb) <= 200): continue
            if any(len(set(temp_comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(temp_comb)
            global_favs_used.append(chosen_fav)
            success = True
            
    return resultats

if st.button("🚀 GENERAR 6 APOSTES PROMETEUS"):
    if not fav_nums:
        st.error("⚠️ Tria almenys 1 número favorit.")
    elif len(reps_demanades) > 2:
        st.error("⚠️ Màxim 2 unitats repetides.")
    else:
        with st.spinner('Calculant...'):
            apostes = generar_sistema()
        if apostes == "ERROR_FAV":
            st.error("❌ Favorits bloquejats per vetos.")
        elif len(apostes) < 6:
            st.error("⚠️ No s'han trobat combinacions. Relaxa els filtres.")
        else:
            for idx, a in enumerate(apostes):
                st.success(f"Aposta {idx+1}: {' - '.join(map(str, a))}")
