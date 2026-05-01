import streamlit as st
import random
from collections import Counter

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Prometeus Ultra Final", page_icon="🔥", layout="centered")

# --- ESTILS VISUALS ---
st.markdown("""
    <style>
    .section-header { background-color: #F0F2F6; color: #1E1E1E; padding: 12px; border-radius: 10px; border-left: 6px solid #FF4B4B; font-weight: bold; margin-top: 25px; }
    .desc-text { font-size: 14px; color: #444; margin-bottom: 15px; font-style: italic; }
    .stButton>button { height: 80px; font-size: 24px; font-weight: bold; border-radius: 20px; background-color: #FF4B4B; color: white; width: 100%; box-shadow: 0px 5px 15px rgba(255,75,75,0.4); }
    div[data-testid="stCheckbox"] > label { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 PROMETEUS ULTRA V.2.9")
st.write("SISTEMA 7-NÚMEROS | ESTRUCTURA ORIGINAL RESTAURADA")

# --- 1. FAVORITS ---
st.markdown('<div class="section-header">🎯 1. NÚMEROS FAVORITS (MÀX 1 PER APOSTA)</div>', unsafe_allow_html=True)
fav_nums = []
for row in range(0, 50, 5):
    cols = st.columns(5)
    for i in range(5):
        n = row + i + 1
        if n <= 49:
            with cols[i]:
                if st.checkbox(f"{n}", key=f"fav_{n}"): fav_nums.append(n)

# --- 2. UNITATS VETADES ---
st.markdown('<div class="section-header">🚫 2. UNITATS VETADES</div>', unsafe_allow_html=True)
vetos = []
for row in range(0, 10, 5):
    cols = st.columns(5)
    for i in range(5):
        v = row + i
        with cols[i]:
            if st.checkbox(f"U-{v}", key=f"v_{v}"): vetos.append(v)

# --- 3. UNITATS REPES ---
st.markdown('<div class="section-header">👯 3. UNITATS REPES</div>', unsafe_allow_html=True)
reps_sel = []
for row in range(0, 10, 5):
    cols = st.columns(5)
    for i in range(5):
        r = row + i
        with cols[i]:
            if st.checkbox(f"R-{r}", key=f"rep_{r}"): reps_sel.append(r)

# --- 4. CONFIGURACIÓ FINAL ---
st.markdown('<div class="section-header">📊 4. CONFIGURACIÓ EXTRA</div>', unsafe_allow_html=True)
sel_decena = st.radio("Limitar desena a 1 número:", ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"], horizontal=True)
bessons_on = st.radio("Filtre Bessons (11, 22, 33, 44):", ["OFF", "ON"], horizontal=True)

# --- MOTOR DE CÀLCUL ---
def generar_sistema():
    resultats = []
    global_favs_used = []
    # PERFILS ORIGINALS (sumen 7)
    perfils_base = [[2,1,1,2,1],[2,1,2,1,1],[2,2,1,1,1],[1,1,2,2,1],[1,2,1,2,1],[1,2,2,1,1],[1,1,1,2,2],[1,1,2,1,2],[1,2,1,1,2],[2,1,1,1,2]]
    primos_impares = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    mells_nums = [11, 22, 33, 44]
    dec_map = {"1-10":0, "11-20":1, "21-30":2, "31-40":3, "41-49":4}

    fav_disponibles = [n for n in fav_nums if (n % 10 not in vetos)]
    if bessons_on == "OFF": fav_disponibles = [n for n in fav_disponibles if n not in mells_nums]
    if not fav_disponibles and len(fav_nums) > 0: return "ERROR_FAV"

    for i in range(1, 7):
        p_target = 3 if i in [1,3,5] else 4
        pri_target = 3 if i in [1,3,5] else 2
        success, intentos = False, 1000000 
        
        while not success and intentos > 0:
            intentos -= 1
            perfil = random.choice(perfils_base)
            if sel_decena != "Cap" and perfil[dec_map[sel_decena]] != 1: continue

            c_favs = Counter(global_favs_used)
            candidats = [n for n in fav_disponibles if c_favs[n] < 2]
            if not candidats: candidats = fav_disponibles
            chosen_fav = random.choice(candidats)
            
            dec_idx = (chosen_fav-1)//10 if chosen_fav < 50 else 4
            if dec_idx > 4: dec_idx = 4

            temp_comb = [chosen_fav]
            blocs = [list(range(1,11)), list(range(11,21)), list(range(21,31)), list(range(31,41)), list(range(41,50))]
            
            possible = True
            for idx, qty in enumerate(perfil):
                needed = qty - 1 if idx == dec_idx else qty
                if needed < 0: possible = False; break
                pool = [n for n in blocs[idx] if n % 10 not in vetos and n != chosen_fav and n not in fav_nums]
                if bessons_on == "OFF": pool = [n for n in pool if n not in mells_nums]
                if len(pool) < needed: possible = False; break
                temp_comb.extend(random.sample(pool, needed))
            
            if not possible: continue
            if sum(1 for n in temp_comb if n % 2 == 0) != p_target: continue
            if sum(1 for n in temp_comb if n in primos_impares) != pri_target: continue
            
            u_temp = [n % 10 for n in temp_comb]
            if not all(u_temp.count(r) == 2 for r in reps_sel[:2]): continue
            
            n_mells = sum(1 for n in temp_comb if n in mells_nums)
            if bessons_on == "ON" and i <= 4:
                if n_mells != 1: continue
            elif n_mells > 0: continue

            temp_comb.sort()
            seguits = sum(1 for j in range(len(temp_comb)-1) if temp_comb[j+1] == temp_comb[j]+1)
            
            if i >= 3: 
                if seguits != 1: continue
            else: 
                if seguits != 0: continue
            
            if not (temp_comb[0] <= 15 and temp_comb[-1] >= 38): continue
            if not (140 <= sum(temp_comb) <= 200): continue
            if any(len(set(temp_comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(temp_comb)
            global_favs_used.append(chosen_fav)
            success = True
            
    return resultats

if st.button("🚀 GENERAR 6 APOSTES PROMETEUS"):
    if not fav_nums: st.error("⚠️ Tria favorits.")
    else:
        with st.spinner('Força bruta amb perfils originals...'):
            apostes = generar_sistema()
        if len(apostes) < 6: st.error("⚠️ No s'ha trobat combinació. Relaxa els filtres.")
        else:
            for idx, a in enumerate(apostes): st.success(f"Aposta {idx+1}: {' - '.join(map(str, a))}")
