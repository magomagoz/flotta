import streamlit as st
import json
import os
import gspread
from datetime import datetime
from fpdf import FPDF

# Configurazione pagina
st.set_page_config(page_title="Gestione Flotta", layout="wide")

FILE_LOGO = "logo.png"

# Connessione a Google Sheets (usiamo cache_resource per non ricaricare ad ogni clic)
@st.cache_resource
def get_sheet():
    # Legge il JSON segreto dai secrets di Streamlit
    creds_json = st.secrets["GCP_CREDENTIALS"]
    creds_dict = json.loads(creds_json)
    client = gspread.service_account_from_dict(creds_dict)
    return client.open("Database_Flotta").worksheet("Dati")

def carica_dati():
    sheet = get_sheet()
    records = sheet.get_all_records()
    dati_flotta = {}
    for row in records:
        targa = str(row.get("Targa", ""))
        if targa:
            dati_flotta[targa] = {
                "marca": str(row.get("Marca", "")),
                "modello": str(row.get("Modello", "")),
                "immatricolazione": str(row.get("Immatricolazione", "")),
                "possesso": str(row.get("Possesso", "")),
                "email": str(row.get("Email", "")),
                "assicurazione": str(row.get("Assicurazione", "")),
                "bollo": str(row.get("Bollo", "")),
                "tagliando": str(row.get("Tagliando", "")),
                "ztl": str(row.get("ZTL", "")),
                "data_creazione": str(row.get("Data_Creazione", ""))
            }
    return dati_flotta

# Generazione PDF
def genera_pdf_scheda(targa, mezzo):
    pdf = FPDF()
    pdf.add_page()
    
    if os.path.exists(FILE_LOGO):
        try:
            pdf.image(FILE_LOGO, x=10, y=10, w=190)
            pdf.set_y(70) # Abbassato per non coprire il logo
        except Exception:
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(0, 10, "[Impossibile caricare il logo. Verifica che sia un file PNG valido]", ln=True, align="C")
            pdf.ln(10)
    else:
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "LOGO AZIENDA NON TROVATO", ln=True, align="C")
        pdf.ln(10)
        
    pdf.set_font("helvetica", "B", 18)
    pdf.cell(0, 10, f"Scheda Automezzo: {targa}", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Data creazione scheda: {mezzo.get('data_creazione', '-')}", ln=True)
    pdf.cell(0, 10, f"Marca: {mezzo.get('marca', '-')}", ln=True)
    pdf.cell(0, 10, f"Modello: {mezzo.get('modello', '-')}", ln=True)
    pdf.cell(0, 10, f"Data Immatricolazione: {mezzo.get('immatricolazione', '-')}", ln=True)
    pdf.cell(0, 10, f"Tipologia: {mezzo.get('possesso', '-')}", ln=True)
    pdf.cell(0, 10, f"Email Referente: {mezzo.get('email', '-')}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Scadenze Programmate", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Assicurazione: {mezzo.get('assicurazione', '-')}", ln=True)
    pdf.cell(0, 10, f"Bollo: {mezzo.get('bollo', '-')}", ln=True)
    pdf.cell(0, 10, f"Tagliando: {mezzo.get('tagliando', '-')}", ln=True)
    pdf.cell(0, 10, f"Permesso ZTL: {mezzo.get('ztl', '-')}", ln=True)
    
    # Restituisce i byte formattati correttamente per Streamlit
    return pdf.output(dest='S').encode('latin-1')

# --- LOGICA APPLICAZIONE ---
if 'refresh' not in st.session_state:
    st.session_state.refresh = True

if st.session_state.refresh:
    st.session_state.flotta = carica_dati()
    st.session_state.refresh = False

dati_flotta = st.session_state.flotta

if os.path.exists(FILE_LOGO):
    st.image(FILE_LOGO, use_container_width=True)

st.title("🚛 Gestione Automezzi e Scadenze")

st.sidebar.header("I tuoi Automezzi")
opzioni_menu = ["➕ Aggiungi Nuovo"] + [f"🚛 {targa}" for targa in dati_flotta.keys()]
azione = st.sidebar.radio("Seleziona:", opzioni_menu)

# INSERIMENTO NUOVO
if azione == "➕ Aggiungi Nuovo":
    st.subheader("Crea Scheda Automezzo")
    
    with st.form("form_nuovo_mezzo"):
        targa = st.text_input("Targa Automezzo*").upper()
        col_marca, col_modello = st.columns(2)
        marca = col_marca.text_input("Marca")
        modello = col_modello.text_input("Modello")
        
        col_imm, col_prop = st.columns(2)
        immatricolazione = col_imm.date_input("Data di Immatricolazione")
        possesso = col_prop.radio("Tipologia di possesso", ["Di Proprietà", "In Leasing"], horizontal=True)
        
        email_referente = st.text_input("Email Referente (lascia vuoto per inviare all'amministrazione)")
        
        st.markdown("### Scadenze Documentali")
        col1, col2 = st.columns(2)
        scadenza_assicurazione = col1.date_input("Scadenza Assicurazione")
        scadenza_bollo = col2.date_input("Scadenza Bollo")
        scadenza_tagliando = col1.date_input("Scadenza Tagliando")
        scadenza_ztl = col2.date_input("Scadenza Permesso ZTL")
        
        submit = st.form_submit_button("Salva Automezzo")
        
        if submit and targa:
            if targa in dati_flotta:
                st.error("Scheda con questa targa già esistente!")
            else:
                data_odierna = datetime.now().strftime("%d/%m/%Y")
                sheet = get_sheet()

                
                # ... codice precedente ...
                nuova_riga = [targa, marca, modello, str(immatricolazione), possesso, email_referente, 
                              str(scadenza_assicurazione), str(scadenza_bollo), str(scadenza_tagliando), 
                              str(scadenza_ztl), data_odierna]
                sheet.append_row(nuova_riga)
                
                # MODIFICA DA QUI:
                st.success(f"Mezzo salvato! Aggiornamento...")
                
                # Questa riga cancella la cache, costringendo Streamlit a riscaricare dal Foglio
                get_sheet.clear() 
                
                st.session_state.refresh = True
                st.rerun()
                
# CONSULTAZIONE ED ELIMINAZIONE
else:
    targa_selezionata = azione.replace("🚛 ", "")
    mezzo = dati_flotta[targa_selezionata]
    
    st.subheader(f"Scheda Automezzo: {targa_selezionata}")
    col_dati1, col_dati2 = st.columns(2)
    with col_dati1:
        st.markdown(f"**Marca:** {mezzo.get('marca', '-')}")
        st.markdown(f"**Modello:** {mezzo.get('modello', '-')}")
    with col_dati2:
        st.markdown(f"**Data Immatricolazione:** {mezzo.get('immatricolazione', '-')}")
        st.markdown(f"**Email Avvisi:** {mezzo.get('email', '-')}")
        
    st.table({
        "Documento": ["Assicurazione", "Bollo", "Tagliando", "Permesso ZTL"],
        "Data di Scadenza": [mezzo.get('assicurazione'), mezzo.get('bollo'), mezzo.get('tagliando'), mezzo.get('ztl')]
    })
    
    st.divider()
    col_pdf, col_elimina = st.columns(2)
    
    with col_pdf:
        pdf_bytes = genera_pdf_scheda(targa_selezionata, mezzo)
        st.download_button("📄 Scarica Scheda in PDF", data=pdf_bytes, file_name=f"Scheda_{targa_selezionata}.pdf", mime="application/pdf", type="primary")
        
    with col_elimina:
        with st.expander("🗑️ Elimina Automezzo"):
            conferma = st.checkbox("Confermo eliminazione")

            if st.button("Elimina Definitivamente", disabled=not conferma):
                sheet = get_sheet()
                # Cerca la riga che contiene la targa ed eliminala
                cell = sheet.find(targa_selezionata, in_column=1)
                if cell:
                    sheet.delete_rows(cell.row)
                st.success("Automezzo rimosso!")
                
                # MODIFICA DA QUI:
                get_sheet.clear() # Svuota la cache anche quando elimini
                
                st.session_state.refresh = True
                st.rerun()







