import streamlit as st
import requests
import random

# --- CONFIGURACIÓ ---
st.set_page_config(page_title="Prometeus Primitiva", page_icon="🔥", layout="centered")

def get_api_data():
    try:
        # 1. Comprova que la Key existeix als Secrets
        if "LOTERIA_API_KEY" not in st.secrets:
            return {"data": "Falta Key", "numeros": "Configura els Secrets a Streamlit Cloud", "bote": "---"}
        
        api_key = st.secrets["LOTERIA_API_KEY"]
        url = "https://loteriasapi.com"
        
        # 2. Headers exactes segons la teva documentació
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        
        r = requests.get(url, headers=headers, timeout=10)
        
        # 3. Gestió d'errors segons l'estat de la resposta
        if r.status_code == 200:
            res = r.json()
            if res.get("success") and "data" in res:
                d = res["data"]
                # Adaptem el mapeig al format JSON que has passat
                return {
                    "data": d.get("drawDate", "N/A"),
                    "numeros": ", ".join(map(str, d.get("combination", []))),
                    "bote": d.get("jackpotFormatted", "Consultant...")
                }
            else:
                error_msg = res.get("error", {}).get("message", "Error desconegut")
                return {"data": "Error API", "numeros": error_msg, "bote": "---"}
        elif r.status_code == 401:
            return {"data": "401", "numeros": "API Key invàlida o expirada", "bote": "---"}
        else:
            return {"data": str(r.status_code), "numeros": "Error en la petició", "bote": "---"}
            
    except Exception as e:
        return {"data": "Excepció", "numeros": str(e), "bote": "---"}

# --- EXPLICACIÓ PER A TU ---
# Si et continua sortint "Error connexió", revisa que a Streamlit Cloud (Settings > Secrets) 
# hagis escrit la Key exactament així:
# LOTERIA_API_KEY = "la_teva_llarga_cadena_de_caracters"

api_info = get_api_data()

# --- INTERFÍCIE (SOTA L'ALTRE, SENSE SIDEBAR) ---
st.title("🔥 Prometeus Primitiva")

st.metric("BOTE PRÒXIM SORTEIG", api_info['bote'])
st.write(f"📅 **Últim sorteig ({api_info['data']}):**")
st.code(api_info['numeros'], language="text")

st.divider()

# [AQUÍ CONTINUARIA LA RESTA DEL CODI DELS SELECTORS I EL MOTOR QUE HEM PACTAT]
