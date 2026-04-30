import streamlit as st
import random
from collections import Counter

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Prometeus Ultra V2", page_icon="🔥", layout="wide")

# --- ESTILS VISUALS ---
st.markdown("""
    <style>
    .stButton>button { height: 60px; font-size: 20px; font-weight: bold; border-radius: 12px; background-color: #FF4B4B; color: white; width: 100%; }
    .number-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 5px; margin-bottom: 20px; }
    .status-box { padding: 15px; border-radius: 10px; background-color: #f0f2f6; border-left: 5px solid #FF4B4B; }
    h3 { border-bottom: 2px solid #FF4B4B; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 PROMETEUS ULTRA V.2")
st.write("SISTEMA DE FORÇA BRUTA (1M) - 7 NÚMEROS")

# --- INTERFÍCIE DE SELECCIÓ (PARRILLES DESPLEGADES) ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🎯 PARRILLA DE FAVORITS (OBLIGATORI 1)")
    st.write("Tria fins a 12 números. Es forçarà 1 per cada aposta (màx. 2 repeticions).")
    fav_nums = []
    # Generar parrilla de botones para favoritos
    cols_fav = st.columns(10)
    for n in range(1, 50):
        with cols_fav[(n-1)%10]:
            if st.checkbox(f"{n}", key=f"fav_{n}"):
                fav_nums.append(n)

with col2:
    st.markdown("### 🚫 UNITATS VETADES")
    st.write("Tria terminacions (Prioritat total).")
    vetos = []
    cols_veto = st.columns(5)
    for v in range(10):
        with cols_veto[v%5]:
            if st.checkbox(f"U-{v}", key=f"v_{v}"):
                vetos.append(v)

st.divider()

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown("### 📊 DESENA KOIXA")
    sel_decena = st.radio("Limitar a 1 número:", ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"], horizontal=True)
with col_b:
    st.markdown("### 👯 UNITATS REPE")
    rep1 = st.selectbox("Repe 1:", ["Cap"] + list(range(10)))
    rep2 = st.selectbox("Repe 2:", ["Cap"] + list(range(10)))
with col_c:
    st.markdown("### 💎 BESSONS")
    bessons_on = st.radio("Activar Filtre:", ["OFF", "ON"], horizontal=True)

# --- MOTOR DE CÀLCUL (FUERZA BRUTA) ---

def generar_sistema():
    resultats = []
    global_favs_used = []
    
    # Configuracions fixes
    perfils_base = [[2,1,1,2,1],[2,1,2,1,1],[2,2,1,1,1],[1,1,2,2,1],[1,2,1,2,1],[1,2,2,1,1],[1,1,1,2,2],[1,1,2,1,2],[1,2,1,1,2],[2,1,1,1,2]]
    primos_impares = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    mells_nums = [11, 22, 33, 44]
    dec_map = {"1-10":0, "11-20":1, "21-30":2, "31-40":3, "41-49":4}
    reps_demanades = [r for r in [rep1, rep2] if r != "Cap"]

    # 1. Filtrat de favorits per jerarquia (Vetos i Bessons manen)
    fav_disponibles = [n for n in fav_nums if (n % 10 not in vetos)]
    if bessons_on == "OFF":
        fav_disponibles = [n for n in fav_disponibles if n not in mells_nums]
    
    if not fav_disponibles: return "ERROR_FAV"

    for i in range(1, 7):
        # Configuració aposta segons paritat i primos
        p_target = 3 if i in [1,3,5] else 4 # Pares: 3 (4 Impares) o 4 (3 Impares)
        primos_target = 3 if i in [1,3,5] else 2
        
        success = False
        intentos = 1000000 # FUERZA BRUTA
        
        while not success and intentos > 0:
            intentos -= 1
            perfil = random.choice(perfils_base)
            if sel_decena != "Cap" and perfil[dec_map[sel_decena]] != 1: continue

            # Selecció del favorit (màx 2 vegades al sistema)
            c_favs = Counter(global_favs_used)
            fav_candidats = [n for n in fav_disponibles if c_favs[n] < 2]
            if not fav_candidats: fav_candidats = fav_disponibles
            
            chosen_fav = random.choice(fav_candidats)
            dec_idx = (chosen_fav-1)//10 if chosen_fav < 41 else 4
            
            # Construir combinació
            temp_comb = [chosen_fav]
            blocs = [list(range(1,11)), list(range(11,21)), list(range(21,31)), list(range(31,41)), list(range(41,50))]
            possible = True
            
            for idx, qty in enumerate(perfil):
                qty_actual = qty - 1 if idx == dec_idx else qty
                if qty_actual < 0: possible = False; break
                
                pool = [n for n in blocs[idx] if n % 10 not in vetos and n != chosen_fav]
                if bessons_on == "OFF":
                    pool = [n for n in pool if n not in mells_nums]
                
                if len(pool) < qty_actual: possible = False; break
                temp_comb.extend(random.sample(pool, qty_actual))
            
            if not possible: continue
            
            # FILTRES OBLIGATORIS
            if sum(1 for n in temp_comb if n % 2 == 0) != p_target: continue
            if sum(1 for n in temp_comb if n in primos_impares) != primos_target: continue
            
            # Repetició d'unitats
            u_temp = [n % 10 for n in temp_comb]
            c_u = Counter(u_temp)
            r_reals = [u for u, c in c_u.items() if c > 1]
            if not (all(r in r_reals for r in reps_demanades) and all(r in reps_demanades for r in r_reals)): continue
            if any(c > 2 for c in c_u.values()): continue

            # Bessons obligatoris en 1-4 (si ON)
            if bessons_on == "ON" and i <= 4:
                if sum(1 for n in temp_comb if n in mells_nums) < 1: continue
            
            temp_comb.sort()
            
            # Seguits (Obligatoris), Rang i Suma
            seguits = sum(1 for j in range(len(temp_comb)-1) if temp_comb[j+1] == temp_comb[j]+1)
            if seguits != 1: continue
            if not (temp_comb[0] <= 15 and temp_comb[-1] >= 38): continue
            if not (140 <= sum(temp_comb) <= 200): continue
            
            # Coincidència entre apostes
            if any(len(set(temp_comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(temp_comb)
            global_favs_used.append(chosen_fav)
            success = True
            
    return resultats

# --- ACCIÓ ---
if st.button("🚀 EXECUTAR MOTOR PROMETEUS ULTRA"):
    if len(fav_nums) == 0:
        st.error("⚠️ Has de seleccionar almenys 1 favorit a la parrilla.")
    elif len(fav_nums) > 12:
        st.error("⚠️ Màxim 12 favorits.")
    else:
        with st.spinner('Força bruta en procés (1.000.000 intents)...'):
            apostes = generar_sistema()
        
        if apostes == "ERROR_FAV":
            st.error("❌ Favorits anul·lats per Vetos o Bessons. Revisa la selecció.")
        elif len(apostes) < 6:
            st.error("⚠️ El motor no ha trobat prou combinacions. Relaxa els Vetos o la Suma.")
        else:
            cols_res = st.columns(2)
            for idx, a in enumerate(apostes):
                c_idx = idx % 2
                with cols_res[c_idx]:
                    txt_p = "3P/4I" if (idx+1) in [1,3,5] else "4P/3I"
                    st.markdown(f"**Aposta {idx+1} ({txt_p})**")
                    st.success(f"**{' - '.join(map(str, a))}**")
