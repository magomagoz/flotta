import streamlit as st
import json
import os
from datetime import datetime

FILE_DATI = "flotta.json"

# Inizializzazione file dati
if not os.path.exists(FILE_DATI):
    with open(FILE_DATI, "w") as f:
        json.dump({}, f)

def carica_dati():
    with open(FILE_DATI, "r") as f:
        return json.load(f)

def salva_dati(dati):
    with open(FILE_DATI, "w") as f:
        json.dump(dati, f, indent=4)

st.set_page_config(page_title="Gestione Flotta", layout="wide")
st.title("🚛 Gestione Automezzi e Scadenze")

dati_flotta = carica_dati()

# --- SIDEBAR: Elenco Automezzi ---
st.sidebar.header("I tuoi Automezzi")
mezzo_selezionato = st.sidebar.radio(
    "Seleziona una targa per i dettagli:",
    ["➕ Aggiungi Nuovo"] + list(dati_flotta.keys())
)

# --- MAIN: Dettagli o Form di inserimento ---
if mezzo_selezionato == "➕ Aggiungi Nuovo":
    st.subheader("Crea Scheda Automezzo")
    with st.form("form_nuovo_mezzo"):
        targa = st.text_input("Targa Automezzo*").upper()
        modello = st.text_input("Modello (es. Fiat Ducato)")
        email_referente = st.text_input("Email Referente per Avvisi*")
        
        col1, col2 = st.columns(2)
        scadenza_assicurazione = col1.date_input("Scadenza Assicurazione")
        scadenza_bollo = col2.date_input("Scadenza Bollo")
        scadenza_tagliando = col1.date_input("Scadenza Tagliando")
        scadenza_ztl = col2.date_input("Scadenza Permesso ZTL")
        
        submit = st.form_submit_button("Salva Automezzo")
        
        if submit and targa and email_referente:
            dati_flotta[targa] = {
                "modello": modello,
                "email": email_referente,
                "assicurazione": str(scadenza_assicurazione),
                "bollo": str(scadenza_bollo),
                "tagliando": str(scadenza_tagliando),
                "ztl": str(scadenza_ztl)
            }
            salva_dati(dati_flotta)
            st.success(f"Mezzo {targa} salvato con successo!")
            st.rerun()

else:
    st.subheader(f"Dettagli Automezzo: {mezzo_selezionato}")
    mezzo = dati_flotta[mezzo_selezionato]
    
    st.markdown(f"**Modello:** {mezzo['modello']}")
    st.markdown(f"**Email Avvisi:** {mezzo['email']}")
    
    # Tabella riassuntiva scadenze
    st.table({
        "Documento": ["Assicurazione", "Bollo", "Tagliando", "ZTL"],
        "Data di Scadenza": [mezzo['assicurazione'], mezzo['bollo'], mezzo['tagliando'], mezzo['ztl']]
    })
    
    if st.button("Elimina Automezzo"):
        del dati_flotta[mezzo_selezionato]
        salva_dati(dati_flotta)
        st.rerun()
