import streamlit as st
import json
import os
from datetime import datetime
from fpdf import FPDF

FILE_DATI = "flotta.json"
FILE_LOGO = "logo.png"

def carica_dati():
    if not os.path.exists(FILE_DATI):
        return {}
    with open(FILE_DATI, "r") as f:
        return json.load(f)

def salva_dati(dati):
    with open(FILE_DATI, "w") as f:
        json.dump(dati, f, indent=4)

# Funzione per generare il PDF con fpdf2
def genera_pdf_scheda(targa, mezzo):
    pdf = FPDF()
    pdf.add_page()
    
    # Inserimento Banner/Logo nel PDF (se esiste)
    if os.path.exists(FILE_LOGO):
        # Aggiusta la larghezza (w) in base alle proporzioni del tuo logo
        pdf.image(FILE_LOGO, x=10, y=10, w=190)
        pdf.ln(40) # Spazio dopo il logo
    else:
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "LOGO AZIENDA NON TROVATO", ln=True, align="C")
        pdf.ln(10)
        
    # Titolo Scheda
    pdf.set_font("helvetica", "B", 18)
    pdf.cell(0, 10, f"Scheda Automezzo: {targa}", ln=True, align="C")
    pdf.ln(5)
    
    # Dati Generali
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Data creazione scheda: {mezzo.get('data_creazione', '-')}", ln=True)
    pdf.cell(0, 10, f"Marca: {mezzo.get('marca', '-')}", ln=True)
    pdf.cell(0, 10, f"Modello: {mezzo.get('modello', '-')}", ln=True)
    pdf.cell(0, 10, f"Data Immatricolazione: {mezzo.get('immatricolazione', '-')}", ln=True)
    pdf.cell(0, 10, f"Tipologia: {mezzo.get('possesso', '-')}", ln=True)
    pdf.cell(0, 10, f"Email Referente: {mezzo.get('email', '-')}", ln=True)
    pdf.ln(10)
    
    # Dati Scadenze
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Scadenze Programmate", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Assicurazione: {mezzo.get('assicurazione', '-')}", ln=True)
    pdf.cell(0, 10, f"Bollo: {mezzo.get('bollo', '-')}", ln=True)
    pdf.cell(0, 10, f"Tagliando: {mezzo.get('tagliando', '-')}", ln=True)
    pdf.cell(0, 10, f"Permesso ZTL: {mezzo.get('ztl', '-')}", ln=True)
    
    # Ritorna il PDF in formato byte per Streamlit
    return bytes(pdf.output())

st.set_page_config(page_title="Gestione Flotta", layout="wide")

# --- BANNER IN CIMA ALL'APP ---
if os.path.exists(FILE_LOGO):
    # use_container_width adatta il logo alla larghezza della pagina
    st.image(FILE_LOGO, use_container_width=True)

st.title("🚛 Gestione Automezzi e Scadenze")

if 'flotta' not in st.session_state:
    st.session_state.flotta = carica_dati()

dati_flotta = st.session_state.flotta

# --- SIDEBAR: Menu di Navigazione pulito ---
st.sidebar.header("I tuoi Automezzi")
opzioni_menu = ["➕ Aggiungi Nuovo"] + [f"🚛 {targa}" for targa in dati_flotta.keys()]
azione = st.sidebar.radio("Seleziona:", opzioni_menu)

# --- MAIN: Aggiunta Nuovo Mezzo ---
if azione == "➕ Aggiungi Nuovo":
    st.subheader("Crea Scheda Automezzo")
    
    with st.form("form_nuovo_mezzo"):
        targa = st.text_input("Targa Automezzo*").upper()
        
        col_marca, col_modello = st.columns(2)
        marca = col_marca.text_input("Marca (es. Fiat)")
        modello = col_modello.text_input("Modello (es. Ducato)")
        
        col_imm, col_prop = st.columns(2)
        immatricolazione = col_imm.date_input("Data di Immatricolazione")
        possesso = col_prop.radio("Tipologia di possesso", ["Di Proprietà", "In Leasing"], horizontal=True)
                
        # Cambiamo l'etichetta per renderlo chiaro all'utente
        email_referente = st.text_input("Email Referente (lascia vuoto per inviare all'amministrazione)")
        
        st.markdown("### Scadenze Documentali")
        col1, col2 = st.columns(2)
        scadenza_assicurazione = col1.date_input("Scadenza Assicurazione")
        scadenza_bollo = col2.date_input("Scadenza Bollo")
        scadenza_tagliando = col1.date_input("Scadenza Tagliando")
        scadenza_ztl = col2.date_input("Scadenza Permesso ZTL")
        
        submit = st.form_submit_button("Salva Automezzo")
        
        # Rimuoviamo 'email_referente' dai requisiti obbligatori per il salvataggio
        if submit and targa: 
            if targa in dati_flotta:
                st.error("Una scheda con questa targa esiste già!")
            else:
                data_odierna = datetime.now().strftime("%d/%m/%Y")
                dati_flotta[targa] = {
                    "data_creazione": data_odierna,
                    "marca": marca,
                    "modello": modello,
                    "immatricolazione": str(immatricolazione),
                    "possesso": possesso,
                    "email": email_referente, # Salverà una stringa vuota se non compili il campo
                    "assicurazione": str(scadenza_assicurazione),
                    "bollo": str(scadenza_bollo),
                    "tagliando": str(scadenza_tagliando),
                    "ztl": str(scadenza_ztl)
                }
                salva_dati(dati_flotta)
                st.success(f"Mezzo {targa} salvato con successo!")
                st.rerun()
        
# --- MAIN: Consultazione Mezzo Esistente ---
else:
    targa_selezionata = azione.replace("🚛 ", "")
    mezzo = dati_flotta[targa_selezionata]
    
    st.subheader(f"Scheda Automezzo: {targa_selezionata}")
    st.caption(f"Scheda creata nel sistema il: **{mezzo.get('data_creazione', 'Data non disponibile')}**")
    
    st.markdown("---")
    
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
    
    st.table({
        "Documento": ["Assicurazione", "Bollo", "Tagliando", "Permesso ZTL"],
        "Data di Scadenza": [
            mezzo.get('assicurazione', '-'), 
            mezzo.get('bollo', '-'), 
            mezzo.get('tagliando', '-'), 
            mezzo.get('ztl', '-')
        ]
    })
    
    st.divider() # Linea di separazione visiva per le azioni in basso
    
    # --- PULSANTI AZIONE IN BASSO ---
    col_pdf, col_elimina = st.columns(2)
    
    with col_pdf:
        # Generiamo il PDF al volo quando la pagina viene caricata
        pdf_bytes = genera_pdf_scheda(targa_selezionata, mezzo)
        st.download_button(
            label="📄 Scarica Scheda in PDF",
            data=pdf_bytes,
            file_name=f"Scheda_{targa_selezionata}.pdf",
            mime="application/pdf",
            type="primary"
        )
        
    with col_elimina:
        with st.expander("🗑️ Opzioni Pericolose (Elimina Automezzo)"):
            st.warning("Stai per eliminare questo automezzo. L'operazione è irreversibile.")
            conferma = st.checkbox("Confermo l'eliminazione")
            
            if st.button("Elimina Definitivamente", disabled=not conferma):
                del dati_flotta[targa_selezionata]
                salva_dati(dati_flotta)
                st.success("Automezzo rimosso. Aggiornamento in corso...")
                st.rerun()
