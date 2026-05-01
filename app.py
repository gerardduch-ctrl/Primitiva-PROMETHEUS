import streamlit as st
import random
from collections import Counter

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Prometeus Ultra V.3.1", page_icon="🔥", layout="centered")

# --- ESTILS VISUALS ---
st.markdown("""
    <style>
    .section-header { 
        background-color: #F0F2F6; color: #1E1E1E; padding: 12px; border-radius: 10px; 
        border-left: 6px solid #FF4B4B; font-weight: bold; margin-top: 25px; 
    }
    .desc-text { font-size: 14px; color: #444; margin-bottom: 15px; font-style: italic; line-height: 1.4; }
    .stButton>button { 
        height: 80px; font-size: 24px; font-weight: bold; border-radius: 20px; 
        background-color: #FF4B4B; color: white; width: 100%; box-shadow: 0px 5px 15px rgba(255,75,75,0.4); 
    }
    div[data-testid="stCheckbox"] > label { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 PROMETEUS ULTRA V.3.1")
st.write("SISTEMA 7-NÚMEROS | VERSIÓ FINAL CORREGIDA")

# --- 1. FAVORITS ---
st.markdown('<div class="section-header">🎯 1. NÚMEROS FAVORITS (MÀX 1 PER APOSTA)</div>', unsafe_allow_html=True)
st.markdown("<p class='desc-text'>S'inclourà exactament 1 favorit per aposta. Aquest filtre té prioritat sobre els Prims.</p>", unsafe_allow_html=True)
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

# --- 4. FILTRE BESSONS ---
st.markdown('<div class="section-header">💎 4. FILTRE BESSONS</div>', unsafe_allow_html=True)
bessons_on = st.radio("Filtre Bessons (11, 22, 33, 44):", ["OFF", "ON"], horizontal=True, label_visibility="collapsed")

# --- 5. DESENA KOIXA ---
st.markdown('<div class="section-header">📊 5. DESENA KOIXA (LIMITADA A 1)</div>', unsafe_allow_html=True)
sel_decena_koixa = st.radio("D1", ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"], horizontal=True, label_visibility="collapsed")

# --- 6. DESENA REPE ---
st.markdown('<div class="section-header">📈 6. DESENA REPE (FORÇADA A 2)</div>', unsafe_allow_html=True)
sel_decena_repe = st.radio("D2", ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"], horizontal=True, label_visibility="collapsed")

st.divider()

# --- MOTOR DE CÀLCUL ---
def generar_sistema():
    resultats = []
    global_favs_used = []
    perfils_base = [[2,1,1,2,1],[2,1,2,1,1],[2,2,1,1,1],[1,1,2,2,1],[1,2,1,2,1],[1,2,2,1,1],[1,1,1,2,2],[1,1,2,1,2],[1,2,1,1,2],[2,1,1,1,2]]
    primos_impares = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    mells_nums = [11, 22, 33, 44]
    dec_map = {"1-10":0, "11-20":1, "21-30":2, "31-40":3, "41-49":4}

    fav_disponibles = [n for n in fav_nums if (n % 10 not in vetos)]
    if bessons_on == "OFF": fav_disponibles = [n for n in fav_disponibles if n not in mells_nums]
    if not fav_disponibles and len(fav_nums) > 0: return "ERROR_FAV"

    for i in range(1, 7):
        # Paritat: 1,3,5 -> 3P/4I | 2,4,6 -> 4P/3I
        p_target = 3 if i in [1,3,5] else 4
        # Prims: 1,3,5 -> 3 prims | 2,4,6 -> 2 prims
        pri_target = 3 if i in [1,3,5] else 2
        
        success, intentos = False, 1000000 
        
        while not success and intentos > 0:
            intentos -= 1
            perfil = random.choice(perfils_base)
            
            if sel_decena_koixa != "Cap" and perfil[dec_map[sel_decena_koixa]] != 1: continue
            if sel_decena_repe != "Cap" and perfil[dec_map[sel_decena_repe]] != 2: continue

            c_favs = Counter(global_favs_used)
            candidats = [n for n in fav_disponibles if c_favs[n] < 2]
            if not candidats: candidats = fav_disponibles
            chosen_fav = random.choice(candidats)
            
            dec_idx_fav = (chosen_fav-1)//10 if chosen_fav < 50 else 4
            if dec_idx_fav > 4: dec_idx_fav = 4

            temp_comb = [chosen_fav]
            blocs = [list(range(1,11)), list(range(11,21)), list(range(21,31)), list(range(31,41)), list(range(41,50))]
            
            possible = True
            for idx, qty in enumerate(perfil):
                needed = qty - 1 if idx == dec_idx_fav else qty
                if needed < 0: possible = False; break
                
                # Pool: sense altres favorits, respectant vetos i bessons OFF
                pool = [n for n in blocs[idx] if n % 10 not in vetos and n != chosen_fav and n not in fav_nums]
                if bessons_on == "OFF": pool = [n for n in pool if n not in mells_nums]
                
                if len(pool) < needed: possible = False; break
                temp_comb.extend(random.sample(pool, needed))
            
            if not possible: continue
            
            # Filtre Paritat i Prims
            if sum(1 for n in temp_comb if n % 2 == 0) != p_target: continue
            if sum(1 for n in temp_comb if n in primos_impares) != pri_target: continue
            
            # Validar Repeticions d'Unitats
            u_temp = [n % 10 for n in temp_comb]
            counts_u = Counter(u_temp)
            if not all(counts_u[r] == 2 for r in reps_sel[:2]): continue
            
            # Filtre Bessons (Strictament 1 si ON en apostes 1-4)
            n_mells = sum(1 for n in temp_comb if n in mells_nums)
            if bessons_on == "ON" and i <= 4:
                if n_mells != 1: continue
            elif n_mells > 0: continue

            # ORDENACIÓ NECESSÀRIA PER A RANG I SEGUITS
            temp_comb.sort()

            # Filtre Seguits (Original: 1-2 OFF, 3-6 ON)
            seguits = sum(1 for j in range(len(temp_comb)-1) if temp_comb[j+1] == temp_comb[j]+1)
            if i >= 3:
                if seguits != 1: continue
            else:
                if seguits != 0: continue
            
            # Filtre Rang (SOLUCIÓ AL TYPEERROR)
            if not (temp_comb[0] <= 15 and temp_comb[-1] >= 38): continue
            
            # Filtre Suma (140-200)
            if not (140 <= sum(temp_comb) <= 200): continue
            
            # Evitar coincidència excessiva
            if any(len(set(temp_comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(temp_comb)
            global_favs_used.append(chosen_fav)
            success = True
            
    return resultats

# --- ACCIÓ ---
if st.button("🚀 GENERAR 6 APOSTES PROMETEUS"):
    if not fav_nums:
        st.error("⚠️ Selecciona almenys un número favorit a la parrilla.")
    else:
        with st.spinner('Força bruta Prometeus en marxa...'):
            apostes = generar_sistema()
        if apostes == "ERROR_FAV":
            st.error("❌ Favorits bloquejats per vetos o besson OFF.")
        elif len(apostes) < 6:
            st.error("⚠️ No s'han trobat prou combinacions. Relaxa els vetos o canvia favorits.")
        else:
            for idx, a in enumerate(apostes):
                st.success(f"Aposta {idx+1}: {' - '.join(map(str, a))}")
