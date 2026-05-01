import streamlit as st
import random
from collections import Counter

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Prometeus Ultra V.3", page_icon="🔥", layout="centered")

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

st.title("🔥 PROMETEUS ULTRA V.3")
st.write("6/49 Sistem. | 7 NÚMEROS | FULMINANT ULTIMATE EDITION.")

# --- 1. FAVORITS (DESPLEGAT) ---
st.markdown('<div class="section-header">🎯 1. NÚMEROS FAVORITS (MÀX 1 PER APOSTA)</div>', unsafe_allow_html=True)
fav_nums = []
for row in range(0, 50, 5):
    cols = st.columns(5)
    for i in range(5):
        n = row + i + 1
        if n <= 49:
            with cols[i]:
                if st.checkbox(f"{n}", key=f"fav_{n}"): fav_nums.append(n)

# --- 2. UNITATS VETADES (DESPLEGAT) ---
st.markdown('<div class="section-header">🚫 2. UNITATS VETADES</div>', unsafe_allow_html=True)
vetos = []
cols_v = st.columns(5)
for v in range(10):
    with cols_v[v % 5]:
        if st.checkbox(f"U-{v}", key=f"v_{v}"): vetos.append(v)

# --- 3. UNITAT REPE (DESPLEGAT) ---
st.markdown('<div class="section-header">👯 3. SELECTOR UNITAT REPETIDA</div>', unsafe_allow_html=True)
st.markdown("<p class='desc-text'>Tria la unitat que vols que surti 2 cops. Les altres 5 terminacions seran úniques.</p>", unsafe_allow_html=True)
reps_sel = []
cols_r = st.columns(5)
for r in range(10):
    with cols_r[r % 5]:
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
    if len(reps_sel) > 1: return "ERROR_MULTIREP"
    
    resultats = []
    global_favs_used = []
    # Perfils base ajustats per a 7 números
    perfils_base = [[2,1,1,2,1],[2,1,2,1,1],[2,2,1,1,1],[1,1,2,2,1],[1,2,1,2,1],[1,2,2,1,1],[1,1,1,2,2],[1,1,2,1,2],[1,2,1,1,2],[2,1,1,1,2]]
    primos_impares = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    mells_nums = [11, 22, 33, 44]
    dec_map = {"1-10":0, "11-20":1, "21-30":2, "31-40":3, "41-49":4}

    fav_disponibles = [n for n in fav_nums if (n % 10 not in vetos)]
    if not fav_disponibles and len(fav_nums) > 0: return "ERROR_FAV"

    for i in range(1, 7):
        p_target = 3 if i in [1,3,5] else 4
        pri_target = 3 if i in [1,3,5] else 2
        
        success, intentos = False, 2000000 
        
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

            temp_comb = [chosen_fav]
            blocs = [list(range(1,11)), list(range(11,21)), list(range(21,31)), list(range(31,41)), list(range(41,50))]
            
            possible = True
            for idx, qty in enumerate(perfil):
                needed = qty - 1 if idx == dec_idx_fav else qty
                if needed < 0: possible = False; break
                pool = [n for n in blocs[idx] if n % 10 not in vetos and n != chosen_fav and n not in fav_nums]
                if bessons_on == "OFF": pool = [n for n in pool if n not in mells_nums]
                if len(pool) < needed: possible = False; break
                temp_comb.extend(random.sample(pool, needed))
            
            if not possible: continue
            
            # --- FILTRE UNITATS (LÒGICA 7 NÚMEROS) ---
            u_temp = [n % 10 for n in temp_comb]
            counts_u = Counter(u_temp)
            if len(counts_u) != 6: continue
            if reps_sel and counts_u[reps_sel[0]] != 2: continue
            if any(c > 2 for c in counts_u.values()): continue

            if sum(1 for n in temp_comb if n % 2 == 0) != p_target: continue
            if sum(1 for n in temp_comb if n in primos_impares) != pri_target: continue
            
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
            
            # MODIFICACIÓ RANG SUMA: 135-220
            if not (135 <= sum(temp_comb) <= 220): continue
            
            if any(len(set(temp_comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(temp_comb)
            global_favs_used.append(chosen_fav)
            success = True
            
    return resultats

# --- ACCIÓ ---
if st.button("🚀 GENERAR 6 APOSTES PROMETEUS"):
    if not fav_nums:
        st.error("⚠️ Selecciona almenys un número favorit.")
    else:
        with st.spinner('Executant 2.000.000 d\'intents...'):
            apostes = generar_sistema()
        if apostes == "ERROR_FAV":
            st.error("❌ Favorits bloquejats.")
        elif apostes == "ERROR_MULTIREP":
            st.error("❌ Selecciona només UNA unitat repetida.")
        elif len(apostes) < 6:
            st.error("⚠️ No s'han trobat combinacions. Relaxa els filtres.")
        else:
            for idx, a in enumerate(apostes):
                st.success(f"Aposta {idx+1}: {' - '.join(map(str, a))}")
