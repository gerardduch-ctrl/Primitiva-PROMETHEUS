import streamlit as st
import random
from collections import Counter

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Prometeus Ultra V.3.", page_icon="🔥", layout="centered")

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

st.title("🔥 PROMETEUS ULTRA V.3.")
st.write("6/49 SISTEM | FULMINANT ULTIMATE EDITION.")

# --- 1. FAVORITS ---
st.markdown('<div class="section-header">🎯 1. NÚMEROS FAVORITS (1 PER APOSTA)</div>', unsafe_allow_html=True)
fav_nums = []
cols_fav = st.columns(7)
for i in range(1, 50):
    with cols_fav[(i-1)%7]:
        if st.checkbox(f"{i}", key=f"fav_{i}"): fav_nums.append(i)

# --- 2. UNITATS VETADES ---
st.markdown('<div class="section-header">🚫 2. UNITATS VETADES (MÀX 4)</div>', unsafe_allow_html=True)
vetos = []
cols_v = st.columns(5)
for i in range(10):
    with cols_v[i%5]:
        if st.checkbox(f"U-{i}", key=f"v_{i}"): vetos.append(i)

# --- 3. UNITAT REPETIDA ---
st.markdown('<div class="section-header">👯 3. SELECTOR UNITAT REPETIDA</div>', unsafe_allow_html=True)
st.markdown("<p class='desc-text'>Aquesta unitat sortirà 2 cops. Les altres 5 terminacions seran totes diferents.</p>", unsafe_allow_html=True)
sel_un_repe = st.selectbox("Tria la unitat que vols repetir:", ["Cap", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

# --- 4. FILTRE BESSONS ---
st.markdown('<div class="section-header">💎 4. FILTRE BESSONS (11, 22, 33, 44)</div>', unsafe_allow_html=True)
bessons_on = st.radio("Estat Bessons:", ["OFF", "ON"], horizontal=True, label_visibility="collapsed")

# --- 5. CONFIGURACIÓ DESENES ---
st.markdown('<div class="section-header">📊 5. ESTRUCTURA DE DESENES</div>', unsafe_allow_html=True)
col_d1, col_d2 = st.columns(2)
with col_d1:
    sel_decena_koixa = st.selectbox("Desena Koixa (Limitada a 1):", ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"])
with col_d2:
    sel_decena_repe = st.selectbox("Desena Repe (Forçada a 2):", ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"])

st.divider()

# --- MOTOR DE CÀLCUL ---
def generar_sistema():
    resultats = []
    global_favs_used = []
    # Perfils per a 7 números (sumen 7)
    perfils_base = [[2,1,1,2,1], [1,2,2,1,1], [2,2,1,1,1], [1,1,2,1,2], [1,2,1,2,1]]
    primos_impares = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    mells_nums = [11, 22, 33, 44]
    dec_map = {"1-10":0, "11-20":1, "21-30":2, "31-40":3, "41-49":4}

    fav_disponibles = [n for n in fav_nums if (n % 10 not in vetos)]
    if not fav_disponibles and len(fav_nums) > 0: return "ERROR_FAV"

    for i in range(1, 7):
        p_target = 3 if i in [1,3,5] else 4 # Parells
        pri_target = 3 if i in [1,3,5] else 2 # Prims
        
        success, intentos = False, 2000000 
        
        while not success and intentos > 0:
            intentos -= 1
            perfil = random.choice(perfils_base)
            
            if sel_decena_koixa != "Cap" and perfil[dec_map[sel_decena_koixa]] != 1: continue
            if sel_decena_repe != "Cap" and perfil[dec_map[sel_decena_repe]] != 2: continue

            # Selecció de favorit
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
            
            # FILTRE UNITATS (La teva petició clau)
            u_temp = [n % 10 for n in temp_comb]
            counts_u = Counter(u_temp)
            if len(counts_u) != 6: continue # 7 números, 6 terminacions = 1 parella i 5 úniques
            if sel_un_repe != "Cap" and counts_u[sel_un_repe] != 2: continue
            if any(c > 2 for c in counts_u.values()): continue

            # Filtres estadístics
            if sum(1 for n in temp_comb if n % 2 == 0) != p_target: continue
            if sum(1 for n in temp_comb if n in primos_impares) != pri_target: continue
            
            # Filtre Bessons
            n_mells = sum(1 for n in temp_comb if n in mells_nums)
            if bessons_on == "ON" and i <= 4:
                if n_mells != 1: continue
            elif n_mells > 0: continue

            temp_comb.sort()

            # Seguits i Suma
            seguits = sum(1 for j in range(len(temp_comb)-1) if temp_comb[j+1] == temp_comb[j]+1)
            if i >= 3:
                if seguits != 1: continue
            else:
                if seguits != 0: continue
            
            if not (temp_comb[0] <= 15 and temp_comb[-1] >= 38): continue
            if not (140 <= sum(temp_comb) <= 220): continue # Rang ampliat per a 7 números
            
            if any(len(set(temp_comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(temp_comb)
            global_favs_used.append(chosen_fav)
            success = True
            
    return resultats

# --- ACCIÓ ---
if st.button("🚀 GENERAR 6 APOSTES PROMETEUS V.3."):
    if not fav_nums:
        st.error("⚠️ Tria almenys un favorit.")
    else:
        with st.spinner('Calculant amb 2 milions d\'intents...'):
            apostes = generar_sistema()
        if apostes == "ERROR_FAV":
            st.error("❌ Favorit bloquejat.")
        elif len(apostes) < 6:
            st.error("⚠️ Filtres massa exigents. Relaxa els vetos.")
        else:
            for idx, a in enumerate(apostes):
                st.success(f"Aposta {idx+1}: {' - '.join(map(str, a))}")
