import streamlit as st
import json
import os
from datetime import datetime

FILE_DATI = "flotta.json"

def carica_dati():
    if not os.path.exists(FILE_DATI):
        return {}
    with open(FILE_DATI, "r") as f:
        return json.load(f)

def salva_dati(dati):
    with open(FILE_DATI, "w") as f:
        json.dump(dati, f, indent=4)

st.set_page_config(page_title="Gestione Flotta", layout="wide")
st.title("🚛 Gestione Automezzi e Scadenze")

# Inizializziamo i dati in session_state per un aggiornamento fluido dell'interfaccia
if 'flotta' not in st.session_state:
    st.session_state.flotta = carica_dati()

dati_flotta = st.session_state.flotta

# --- SIDEBAR: Menu di Navigazione ---
st.sidebar.header("Menu")
# Costruiamo la lista delle opzioni dinamicamente
opzioni_menu = ["➕ Aggiungi Nuovo", "🗑️ Elimina Automezzo"] + [f"🚛 {targa}" for targa in dati_flotta.keys()]

azione = st.sidebar.radio("Scegli un'operazione:", opzioni_menu)

# --- MAIN: Aggiunta Nuovo Mezzo ---
if azione == "➕ Aggiungi Nuovo":
    st.subheader("Crea Scheda Automezzo")
    
    with st.form("form_nuovo_mezzo"):
        targa = st.text_input("Targa Automezzo*").upper()
        
        # Marca e Modello affiancati su due colonne
        col_marca, col_modello = st.columns(2)
        marca = col_marca.text_input("Marca (es. Fiat)")
        modello = col_modello.text_input("Modello (es. Ducato)")
        
        # Immatricolazione e Tipologia di Possesso affiancati
        col_imm, col_prop = st.columns(2)
        immatricolazione = col_imm.date_input("Data di Immatricolazione")
        # radio in orizzontale fa risparmiare spazio verticale
        possesso = col_prop.radio("Tipologia di possesso", ["Di Proprietà", "In Leasing"], horizontal=True) 
        
        email_referente = st.text_input("Email Referente per Avvisi*")
        
        st.markdown("### Scadenze Documentali")
        col1, col2 = st.columns(2)
        scadenza_assicurazione = col1.date_input("Scadenza Assicurazione")
        scadenza_bollo = col2.date_input("Scadenza Bollo")
        scadenza_tagliando = col1.date_input("Scadenza Tagliando")
        scadenza_ztl = col2.date_input("Scadenza Permesso ZTL")
        
        submit = st.form_submit_button("Salva Automezzo")
        
        if submit and targa and email_referente:
            if targa in dati_flotta:
                st.error("Una scheda con questa targa esiste già!")
            else:
                # La data di creazione viene generata automaticamente e cristallizzata qui
                data_odierna = datetime.now().strftime("%d/%m/%Y")
                
                dati_flotta[targa] = {
                    "data_creazione": data_odierna,
                    "marca": marca,
                    "modello": modello,
                    "immatricolazione": str(immatricolazione),
                    "possesso": possesso,
                    "email": email_referente,
                    "assicurazione": str(scadenza_assicurazione),
                    "bollo": str(scadenza_bollo),
                    "tagliando": str(scadenza_tagliando),
                    "ztl": str(scadenza_ztl)
                }
                salva_dati(dati_flotta)
                st.success(f"Mezzo {targa} salvato con successo!")
                st.rerun()

# --- MAIN: Eliminazione Mezzo ---
elif azione == "🗑️ Elimina Automezzo":
    st.subheader("Cancella Automezzo")
    
    if not dati_flotta:
        st.info("Nessun automezzo presente in flotta.")
    else:
        mezzo_da_eliminare = st.selectbox("Seleziona la targa da eliminare:", list(dati_flotta.keys()))
        
        # Area di warning visivamente distinta
        st.warning(f"⚠️ **ATTENZIONE:** Stai per eliminare definitivamente la scheda del mezzo **{mezzo_da_eliminare}**. L'operazione è irreversibile e disattiverà gli avvisi email per questa targa.")
        
        # Checkbox di conferma obbligatorio per abilitare il tasto di cancellazione
        conferma = st.checkbox(f"Confermo di voler eliminare la targa {mezzo_da_eliminare}")
        
        if st.button("Elimina Definitivamente", type="primary", disabled=not conferma):
            del dati_flotta[mezzo_da_eliminare]
            salva_dati(dati_flotta)
            st.success(f"Automezzo {mezzo_da_eliminare} rimosso dalla flotta.")
            st.rerun()

# --- MAIN: Consultazione Mezzo Esistente ---
else:
    # Rimuoviamo l'icona del camioncino dalla stringa per ritrovare la chiave corretta
    targa_selezionata = azione.replace("🚛 ", "")
    mezzo = dati_flotta[targa_selezionata]
    
    st.subheader(f"Scheda Automezzo: {targa_selezionata}")
    st.caption(f"Scheda creata nel sistema il: **{mezzo.get('data_creazione', 'Data non disponibile')}**")
    
    st.markdown("---")
    
    # Mostriamo i dati su due colonne per migliore leggibilità
    col_dati1, col_dati2 = st.columns(2)
    
    with col_dati1:
        st.markdown(f"**Marca:** {mezzo.get('marca', '-')}")
        st.markdown(f"**Modello:** {mezzo.get('modello', '-')}")
        st.markdown(f"**Tipologia:** {mezzo.get('possesso', '-')}")
        
    with col_dati2:
        st.markdown(f"**Data Immatricolazione:** {mezzo.get('immatricolazione', '-')}")
        st.markdown(f"**Email Avvisi:** {mezzo.get('email', '-')}")
        
    st.markdown("---")
    st.markdown("### Scadenze Programmate")
    
    # Tabella riassuntiva
    st.table({
        "Documento": ["Assicurazione", "Bollo", "Tagliando", "Permesso ZTL"],
        "Data di Scadenza": [
            mezzo.get('assicurazione', '-'), 
            mezzo.get('bollo', '-'), 
            mezzo.get('tagliando', '-'), 
            mezzo.get('ztl', '-')
        ]
    })
