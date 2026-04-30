import streamlit as st
import random
from collections import Counter

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Prometeus Ultra Final", page_icon="🔥", layout="centered")

# --- ESTILS VISUALS CORREGITS PER A MÒBIL ---
st.markdown("""
    <style>
    /* Títols amb contrast alt */
    .section-header {
        background-color: #F0F2F6;
        color: #1E1E1E;
        padding: 12px;
        border-radius: 10px;
        border-left: 6px solid #FF4B4B;
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 10px;
    }
    .desc-text { font-size: 14px; color: #444; margin-bottom: 15px; font-style: italic; line-height: 1.4; }
    
    /* Botó principal gegant */
    .stButton>button { 
        height: 80px; font-size: 24px; font-weight: bold; border-radius: 20px; 
        background-color: #FF4B4B; color: white; width: 100%; box-shadow: 0px 5px 15px rgba(255,75,75,0.4);
    }

    /* Forçar graella de 5 columnes real per a mòbil */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 PROMETEUS ULTRA V.2.1")
st.write("EDICIÓ FINAL OPTIMITZADA PER A MÒBIL")

# --- 1. FAVORITS ---
st.markdown('<div class="section-header">🎯 1. NÚMEROS FAVORITS (PARRILLA)</div>', unsafe_allow_html=True)
st.markdown("<p class='desc-text'>Tria fins a 12 números. S'inclourà un per cada aposta. El sistema vigila que no es repeteixin més de 2 vegades. Atenció: Els vetos i bessons tenen prioritat.</p>", unsafe_allow_html=True)

fav_nums = []
cols_fav = st.columns(5)
for n in range(1, 50):
    with cols_fav[(n-1)%5]:
        if st.checkbox(f"{n}", key=f"fav_{n}"):
            fav_nums.append(n)

# --- 2. UNITATS VETADES ---
st.markdown('<div class="section-header">🚫 2. UNITATS VETADES</div>', unsafe_allow_html=True)
st.markdown("<p class='desc-text'>Criba de terminacions prohibides. Elimina totalment les terminacions que no vulguis. Afecta també als teus favorits.</p>", unsafe_allow_html=True)

vetos = []
cols_veto = st.columns(5)
for v in range(10):
    with cols_veto[v%5]:
        if st.checkbox(f"U-{v}", key=f"v_{v}"):
            vetos.append(v)

# --- 3. UNITATS REPES ---
st.markdown('<div class="section-header">👯 3. UNITATS REPES</div>', unsafe_allow_html=True)
st.markdown("<p class='desc-text'>Força terminacions dobles. Tria quines unitats vols que apareguin exactament dues vegades en la combinació.</p>", unsafe_allow_html=True)

reps_demanades = []
cols_rep = st.columns(5)
for r in range(10):
    with cols_rep[r%5]:
        if st.checkbox(f"R-{r}", key=f"rep_{r}"):
            reps_demanades.append(r)

# --- 4. DESENES ---
st.markdown('<div class="section-header">📊 4. DESENES</div>', unsafe_allow_html=True)
st.markdown("<p class='desc-text'>Controla la densitat per grup. Tria quina desena vols que quedi limitada a un sol número (Perfil 1).</p>", unsafe_allow_html=True)
sel_decena = st.radio("D", ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"], horizontal=True, label_visibility="collapsed")

# --- 5. BESSONS ---
st.markdown('<div class="section-header">💎 5. FILTRE BESSONS</div>', unsafe_allow_html=True)
st.markdown("<p class='desc-text'>Activa la presència de números bessons (11, 22, 33, 44) per a les apostes 1 a 4. Si està OFF, s'eliminen totalment.</p>", unsafe_allow_html=True)
bessons_on = st.radio("M", ["OFF", "ON"], horizontal=True, label_visibility="collapsed")

st.divider()

# --- MOTOR DE CÀLCUL ---
def generar_sistema():
    resultats = []
    global_favs_used = []
    perfils_base = [[2,1,1,2,1],[2,1,2,1,1],[2,2,1,1,1],[1,1,2,2,1],[1,2,1,2,1],[1,2,2,1,1],[1,1,1,2,2],[1,1,2,1,2],[1,2,1,1,2],[2,1,1,1,2]]
    primos_impares = [3,5,7,11,13,17,19,23,29,31,37,41,43,47]
    mells_nums = [11, 22, 33, 44]
    dec_map = {"1-10":0, "11-20":1, "21-30":2, "31-40":3, "41-49":4}

    # Jerarquia de filtres aplicada a favorits
    fav_disponibles = [n for n in fav_nums if (n % 10 not in vetos)]
    if bessons_on == "OFF":
        fav_disponibles = [n for n in fav_disponibles if n not in mells_nums]
    
    if not fav_disponibles and len(fav_nums) > 0: return "ERROR_FAV"

    for i in range(1, 7):
        p_target = 3 if i in [1,3,5] else 4 # 3P/4I o 4P/3I
        pri_target = 3 if i in [1,3,5] else 2
        success = False
        intentos = 1000000 
        
        while not success and intentos > 0:
            intentos -= 1
            perfil = random.choice(perfils_base)
            if sel_decena != "Cap" and perfil[dec_map[sel_decena]] != 1: continue

            c_favs = Counter(global_favs_used)
            candidats = [n for n in fav_disponibles if c_favs[n] < 2]
            if not candidats: candidats = fav_disponibles
            chosen_fav = random.choice(candidats)
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
            if sum(1 for n in temp_comb if n in primos_impares) != pri_target: continue
            
            # Validar Repetides
            u_temp = [n % 10 for n in temp_comb]
            c_u = Counter(u_temp)
            r_reals = [u for u, c in c_u.items() if c > 1]
            if not (all(r in r_reals for r in reps_demanades[:2]) and all(r in reps_demanades[:2] for r in r_reals)): continue
            if any(c > 2 for c in c_u.values()): continue

            # Bessons en apostes 1-4
            if bessons_on == "ON" and i <= 4:
                if sum(1 for n in temp_comb if n in mells_nums) < 1: continue
            
            temp_comb.sort()
            # Filtre Seguits (Sempre ON)
            seguits = sum(1 for j in range(len(temp_comb)-1) if temp_comb[j+1] == temp_comb[j]+1)
            if seguits != 1: continue
            # Rang i Suma
            if not (temp_comb[0] <= 15 and temp_comb[-1] >= 38): continue
            if not (140 <= sum(temp_comb) <= 200): continue
            
            if any(len(set(temp_comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(temp_comb)
            global_favs_used.append(chosen_fav)
            success = True
            
    return resultats

# --- ACCIÓ ---
if st.button("🚀 GENERAR 6 APOSTES PROMETEUS"):
    if not fav_nums:
        st.error("⚠️ Tria almenys 1 número favorit.")
    else:
        with st.spinner('Força bruta en marxa...'):
            apostes = generar_sistema()
        if apostes == "ERROR_FAV":
            st.error("❌ Favorits bloquejats per vetos/bessons.")
        elif len(apostes) < 6:
            st.error("⚠️ Massa restriccions. Revisa els vetos.")
        else:
            for idx, a in enumerate(apostes):
                st.success(f"Aposta {idx+1}: {' - '.join(map(str, a))}")
