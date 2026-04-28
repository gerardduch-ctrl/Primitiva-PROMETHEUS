import streamlit as st
import requests
import random

st.set_page_config(page_title="Prometeus Primitiva", page_icon="🔥")

# --- 1. CONNEXIÓ REAL API ---
def get_real_data():
    try:
        # Intentem obtenir dades reals de l'API de El País (molt comuna per Primitiva)
        r = requests.get("https://elpais.com")
        data = r.json()
        return {
            "data": data['fecha'],
            "numeros": data['combinacion'],
            "bote": data['proximo_bote']
        }
    except:
        return {"data": "No disponible", "numeros": "0-0-0-0-0-0", "bote": "Consultant..."}

api_data = get_real_data()

st.title("🔥 Prometeus Primitiva")
st.metric("BOTE PRÒXIM SORTEIG", api_data['bote'])
st.write(f"Darrer sorteig ({api_data['data']}): **{api_data['numeros']}**")
st.divider()

# --- 2. SELECTORS ---
with st.expander("⚙️ CONFIGURACIÓ BLOQUEJADA"):
    sel_un_rep = st.multiselect("UNITAT REPETIDA (Max 2)", list(range(10)), max_selections=2)
    sel_un_vet = st.multiselect("UNITAT VETADA (Max 4)", list(range(10)), max_selections=4)
    sel_mellizos = st.toggle("ACTIVA MELLIZOS (11, 22, 33, 44)")
    sel_clumps = st.toggle("ACTIVA CLUMPS (Seguits)")

# --- 3. MOTOR DE GENERACIÓ AMB FILTRE CREUAT ---
def validar_terminacions(nums, sel_rep):
    unitats = [n % 10 for n in nums]
    counts = {x: unitats.count(x) for x in set(unitats)}
    reps_trobades = [u for u, c in counts.items() if c > 1]
    
    # Si no hem triat res, només pot haver-hi 1 unitat repetida (màxim 2 cops)
    if not sel_rep:
        return len(reps_trobades) <= 1 and all(c <= 2 for c in counts.values())
    
    # Si hem triat unitats, han de ser aquestes i no unes altres
    if not all(r in sel_rep for r in reps_trobades): return False
    # Ha de contenir les repetides que hem demanat
    if not all(r in counts and counts[r] >= 2 for r in sel_rep): return False
    # Màxim 2 números per unitat
    return all(c <= 2 for c in counts.values())

def generar_6_apostes():
    resultats = []
    perfils = [
        [2,1,1,2,1], [2,1,2,1,1], [2,2,1,1,1], 
        [1,1,2,2,1], [1,2,1,2,1], [1,2,2,1,1]
    ]
    mells = [11, 22, 33, 44]
    
    for i in range(1, 7):
        paritat_parells = 3 if i in [1, 3, 5] else 4
        success = False
        intentos_locals = 0
        
        while not success and intentos_locals < 10000:
            intentos_locals += 1
            comb = []
            
            # Construcció per desenes segons perfil
            blocs = [list(range(1,11)), list(range(11,21)), list(range(21,31)), list(range(31,41)), list(range(41,50))]
            for idx, qty in enumerate(perfils[i-1]):
                valid_pool = [n for n in blocs[idx] if n % 10 not in sel_un_vet]
                if len(valid_pool) < qty: break
                comb.extend(random.sample(valid_pool, qty))
            
            if len(comb) != 7: continue
            
            # Filtre Paritat (3P/4S o 4P/3S segons aposta)
            if sum(1 for n in comb if n % 2 == 0) != paritat_parells: continue
            
            # Filtre Mellizos
            mells_present = [n for n in comb if n in mells]
            if sel_mellizos and i <= 4:
                if len(mells_present) != 1: continue
            else:
                if len(mells_present) > 0: continue
            
            # Filtre Clumps (Seguits)
            comb.sort()
            seguits = sum(1 for j in range(len(comb)-1) if comb[j+1] == comb[j]+1)
            if sel_clumps and i >= 3:
                if seguits != 1: continue
            else:
                if seguits > 0: continue
            
            # Filtre Terminacions (Selector Unitat Repetida)
            if not validar_terminacions(comb, sel_un_rep): continue
            
            # --- FILTRE DE SEGURETAT: NO MÉS DE 2 IGUALS AMB APOSTES ANTERIORS ---
            coincidencies_riques = False
            for anterior in resultats:
                comuns = len(set(comb) & set(anterior))
                if comuns > 2:
                    coincidencies_riques = True
                    break
            if coincidencies_riques: continue
            
            resultats.append(comb)
            success = True
            
    return resultats

if st.button("GENERAR APOSTES PROMETEUS"):
    final_list = generar_6_apostes()
    if len(final_list) < 6:
        st.error("Els filtres són massa restrictius. Prova a vetar menys unitats.")
    for idx, res in enumerate(final_list):
        st.write(f"**Aposta {idx+1}:** `{res}`")
