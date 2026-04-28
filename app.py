import streamlit as st
import requests
import random

# Config d'estil i icona
st.set_page_config(page_title="Prometeus Primitiva", page_icon="🔥", layout="centered")

# --- 1. OBTENCIÓ DE DADES REALS (LOTERIA API) ---
def get_loterias_api_data():
    try:
        # Utilitzem l'endpoint de Primitiva de LoteriasAPI.com
        api_key = st.secrets["LOTERIA_API_KEY"]
        url = f"https://loteriasapi.com{api_key}"
        r = requests.get(url, timeout=5)
        data = r.json()
        return {
            "data": data.get('fecha', 'Desconeguda'),
            "numeros": data.get('combinacion', 'N/A'),
            "bote": data.get('bote_proximo', 'Consultant...')
        }
    except:
        return {"data": "Error API", "numeros": "0-0-0-0-0-0", "bote": "No disponible"}

api_info = get_loterias_api_data()

# --- INTERFÍCIE ---
st.title("🔥 Prometeus Primitiva")
st.metric("BOTE PRÒXIM SORTEIG", api_info['bote'])
st.write(f"Darrer sorteig ({api_info['data']}): **{api_info['numeros']}**")
st.divider()

# --- 2. SELECTORS (CONFIGURACIÓ PACTADA) ---
with st.sidebar:
    st.header("⚙️ CONFIGURACIÓ")
    
    # SELECTOR DECENAS
    sel_decena_koixa = st.radio("S. DECENAS (Desena amb NOMÉS 1 número):", 
                               ["Cap", "1-10", "11-20", "21-30", "31-40", "41-49"])
    
    # SELECTOR UNITATS
    sel_un_rep = st.multiselect("S. UNITAT REPETIDA (Max 2)", list(range(10)), max_selections=2)
    sel_un_vet = st.multiselect("S. UNITAT VETADA (Max 4)", list(range(10)), max_selections=4)
    
    # ALTRES SELECTORS
    sel_mellizos = st.toggle("S. MELLIZOS (11, 22, 33, 44)")
    sel_clumps = st.toggle("S. CLUMPS (2 Seguits)")

# --- 3. LÒGICA DE CRIBATGE ---
def validar_terminacions(nums, sel_rep):
    units = [n % 10 for n in nums]
    counts = {x: units.count(x) for x in set(units)}
    reps_reals = [u for u, c in counts.items() if c > 1]
    
    # Si demanem unitats repetides específiques
    if sel_rep:
        if not all(r in reps_reals for r in sel_rep): return False
        if not all(r in sel_rep for r in reps_reals): return False
    else:
        if len(reps_reals) > 1: return False # Per defecte només 1 repetida
        
    return all(c <= 2 for c in counts.values()) # Màxim 2 de cada unitat

def generar_apostes():
    resultats = []
    # Perfils de 7 números segons la teva llista
    perfils_base = [
        [2,1,1,2,1], [2,1,2,1,1], [2,2,1,1,1], 
        [1,1,2,2,1], [1,2,1,2,1], [1,2,2,1,1]
    ]
    
    for i in range(1, 7):
        success = False
        paritat_parells = 3 if i in [1, 3, 5] else 4
        
        while not success:
            comb = []
            perfil = random.choice(perfils_base)
            
            # Filtre "Selector Decenas": Si s'ha triat una desena "koixa", el perfil ha de tenir un 1 allà
            dec_map = {"1-10":0, "11-20":1, "21-30":2, "31-40":3, "41-49":4}
            if sel_decena_koixa != "Cap":
                idx_v = dec_map[sel_decena_koixa]
                if perfil[idx_v] != 1: continue

            # Construcció
            blocs = [list(range(1,11)), list(range(11,21)), list(range(21,31)), list(range(31,41)), list(range(41,50))]
            for idx, qty in enumerate(perfil):
                pool = [n for n in blocs[idx] if n % 10 not in sel_un_vet]
                if len(pool) < qty: break
                comb.extend(random.sample(pool, qty))
            
            if len(comb) != 7: continue
            
            # Filtres Mellizos i Clumps
            mells = [11, 22, 33, 44]
            present_mells = [n for n in comb if n in mells]
            if sel_mellizos and i <= 4:
                if len(present_mells) != 1: continue
            elif not sel_mellizos and len(present_mells) > 0: continue
            
            comb.sort()
            seguits = sum(1 for j in range(len(comb)-1) if comb[j+1] == comb[j]+1)
            if sel_clumps and i >= 3:
                if seguits != 1: continue
            elif not sel_clumps and seguits > 0: continue
            
            # Paritat i Unitats
            if sum(1 for n in comb if n % 2 == 0) != paritat_parells: continue
            if not validar_terminacions(comb, sel_un_rep): continue
            
            # FILTRE CREUAT: No més de 2 iguals amb les anteriors
            if any(len(set(comb) & set(res)) > 2 for res in resultats): continue
            
            resultats.append(comb)
            success = True
            
    return resultats

if st.button("GENERAR 6 COMBINACIONS"):
    apostes = generar_apostes()
    for i, a in enumerate(apostes):
        st.subheader(f"Aposta {i+1}")
        st.code(" - ".join(map(str, a)))
