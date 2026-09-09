import streamlit as st
import json
import os
import gspread
from datetime import datetime
from fpdf import FPDF

st.set_page_config(page_title="Gestione Flotta", layout="wide")

# --- PERSONALIZZAZIONE GRAFICA SIDEBAR ---
st.markdown(
    """
    <style>
    /* Spazio tra i singoli automezzi nell'elenco */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        margin-bottom: 12px !important; 
    }
    
    /* Spazio extra e linea di separazione sotto "Aggiungi Nuovo" (la prima voce) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label:first-child {
        margin-bottom: 30px !important;
        padding-bottom: 15px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True
)

FILE_LOGO = "logo.png"

# --- 1. CONNESSIONE GOOGLE SHEETS ---
@st.cache_resource
def get_sheet():
    creds = json.loads(st.secrets["GCP_CREDENTIALS"])
    client = gspread.service_account_from_dict(creds)
    return client.open("Database_Flotta").worksheet("Dati")

# --- 2. LETTURA DATI A PROVA DI ERRORE ---
def leggi_flotta():
    sheet = get_sheet()
    # Scarica tutto il foglio come testo grezzo per evitare errori di formato
    tutti_i_dati = sheet.get_all_values()
    
    flotta = {}
    if len(tutti_i_dati) > 1:
        # Pulisce e formatta le intestazioni della riga 1
        intestazioni = [str(x).strip().upper() for x in tutti_i_dati[0]]
        
        # Cerca dinamicamente le colonne (non importa l'ordine)
        colonne_richieste = ["TARGA", "MARCA", "MODELLO", "IMMATRICOLAZIONE", "POSSESSO", 
                             "EMAIL", "ASSICURAZIONE", "BOLLO", "TAGLIANDO", "ZTL", "DATA_CREAZIONE"]
        
        # Controllo di sicurezza: verifichiamo che ci siano tutte le colonne
        for col in colonne_richieste:
            if col not in intestazioni:
                st.error(f"⚠️ ERRORE GOOGLE SHEETS: Manca la colonna '{col}'. Controlla la prima riga del tuo foglio!")
                return {}
                
        # Estrazione dati
        idx = {col: intestazioni.index(col) for col in colonne_richieste}
        
        for riga in tutti_i_dati[1:]:
            # Se la riga è più corta delle intestazioni, la riempiamo di vuoti per non far crashare l'app
            while len(riga) < len(intestazioni):
                riga.append("")
                
            targa = str(riga[idx["TARGA"]]).strip().upper()
            if targa:
                flotta[targa] = {
                    "marca": str(riga[idx["MARCA"]]),
                    "modello": str(riga[idx["MODELLO"]]),
                    "immatricolazione": str(riga[idx["IMMATRICOLAZIONE"]]),
                    "possesso": str(riga[idx["POSSESSO"]]),
                    "email": str(riga[idx["EMAIL"]]),
                    "assicurazione": str(riga[idx["ASSICURAZIONE"]]),
                    "bollo": str(riga[idx["BOLLO"]]),
                    "tagliando": str(riga[idx["TAGLIANDO"]]),
                    "ztl": str(riga[idx["ZTL"]]),
                    "data_creazione": str(riga[idx["DATA_CREAZIONE"]])
                }
    return flotta

# --- 3. GENERAZIONE PDF ---
def genera_pdf_scheda(targa, mezzo):
    pdf = FPDF()
    pdf.add_page()
    
    if os.path.exists(FILE_LOGO):
        try:
            pdf.image(FILE_LOGO, x=10, y=10, w=190)
            pdf.set_y(70)
        except Exception:
            pass # Ignora errori logo
    else:
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "LOGO AZIENDA NON TROVATO", ln=True, align="C")
        pdf.ln(10)
        
    pdf.set_font("helvetica", "B", 18)
    pdf.cell(0, 10, f"Scheda Automezzo: {targa}", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Data creazione: {mezzo.get('data_creazione', '-')}", ln=True)
    pdf.cell(0, 10, f"Marca: {mezzo.get('marca', '-')}", ln=True)
    pdf.cell(0, 10, f"Modello: {mezzo.get('modello', '-')}", ln=True)
    pdf.cell(0, 10, f"Immatricolazione: {mezzo.get('immatricolazione', '-')}", ln=True)
    pdf.cell(0, 10, f"Tipologia: {mezzo.get('possesso', '-')}", ln=True)
    pdf.cell(0, 10, f"Email: {mezzo.get('email', '-')}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Scadenze", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Assicurazione: {mezzo.get('assicurazione', '-')}", ln=True)
    pdf.cell(0, 10, f"Bollo: {mezzo.get('bollo', '-')}", ln=True)
    pdf.cell(0, 10, f"Tagliando: {mezzo.get('tagliando', '-')}", ln=True)
    pdf.cell(0, 10, f"Permesso ZTL: {mezzo.get('ztl', '-')}", ln=True)
    
    try:
        # Se usi la nuova libreria fpdf2 (Quella attualmente sul tuo GitHub)
        return bytes(pdf.output())
    except TypeError:
        # Metodo di riserva se Streamlit usa la vecchia libreria fpdf
        return pdf.output(dest='S').encode('latin-1')

# --- 4. INTERFACCIA UTENTE ---
if os.path.exists(FILE_LOGO):
    st.image(FILE_LOGO, use_container_width=True)

st.title("🚛 Gestione Automezzi")

# Lettura dati diretta (Senza Cache!)
dati_flotta = leggi_flotta()

st.sidebar.header("I tuoi Automezzi")
opzioni_menu = ["➕ Aggiungi Nuovo"] + [f"🚛 {t}" for t in dati_flotta.keys()]
azione = st.sidebar.radio("Seleziona:", opzioni_menu)

# --- INSERIMENTO ---
if azione == "➕ Aggiungi Nuovo":
    st.subheader("Crea Scheda")
    
    with st.form("form_nuovo_mezzo"):
        targa = st.text_input("Targa*").upper()
        col_marca, col_modello = st.columns(2)
        marca = col_marca.text_input("Marca")
        modello = col_modello.text_input("Modello")
        
        col_imm, col_prop = st.columns(2)
        immatricolazione = col_imm.date_input("Immatricolazione")
        possesso = col_prop.radio("Possesso", ["Di Proprietà", "In Leasing"], horizontal=True)
        
        email_referente = st.text_input("Email Avvisi (vuoto = usa mittente base)")
        
        st.markdown("### Scadenze")
        col1, col2 = st.columns(2)
        scadenza_assicurazione = col1.date_input("Assicurazione")
        scadenza_bollo = col2.date_input("Bollo")
        scadenza_tagliando = col1.date_input("Tagliando")
        scadenza_ztl = col2.date_input("Permesso ZTL")
        
        submit = st.form_submit_button("Salva Automezzo")
        
        if submit and targa:
            if targa in dati_flotta:
                st.error("Targa già esistente!")
            else:
                try:
                    data_odierna = datetime.now().strftime("%d/%m/%Y")
                    sheet = get_sheet()
                    
                    # Cerca l'ordine esatto delle colonne sul foglio per non sbagliare incastri
                    intestazioni_attuali = sheet.row_values(1)
                    nuova_riga = [""] * len(intestazioni_attuali)
                    
                    # Inserisce ogni dato esattamente nella sua colonna corrispondente
                    dati_da_salvare = {
                        "TARGA": targa, "MARCA": marca, "MODELLO": modello, 
                        "IMMATRICOLAZIONE": str(immatricolazione), "POSSESSO": possesso, 
                        "EMAIL": email_referente, "ASSICURAZIONE": str(scadenza_assicurazione), 
                        "BOLLO": str(scadenza_bollo), "TAGLIANDO": str(scadenza_tagliando), 
                        "ZTL": str(scadenza_ztl), "DATA_CREAZIONE": data_odierna
                    }
                    
                    for i, nome_colonna in enumerate(intestazioni_attuali):
                        col_upper = str(nome_colonna).strip().upper()
                        if col_upper in dati_da_salvare:
                            nuova_riga[i] = dati_da_salvare[col_upper]
                            
                    sheet.append_row(nuova_riga)
                    st.success("Salvato su Google Sheets! Ricarico...")
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore durante il salvataggio: {e}")

# --- CONSULTAZIONE ---
# --- CONSULTAZIONE ED ELIMINAZIONE ---
else:
    targa_selezionata = azione.replace("🚛 ", "")
    mezzo = dati_flotta[targa_selezionata]
    
    st.subheader(f"Scheda: {targa_selezionata}")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Marca:** {mezzo.get('marca', '-')}")
        st.markdown(f"**Modello:** {mezzo.get('modello', '-')}")
    with col2:
        st.markdown(f"**Immatricolazione:** {mezzo.get('immatricolazione', '-')}")
        st.markdown(f"**Email:** {mezzo.get('email', '-')}")
        
    st.table({
        "Documento": ["Assicurazione", "Bollo", "Tagliando", "ZTL"],
        "Scadenza": [mezzo.get('assicurazione'), mezzo.get('bollo'), mezzo.get('tagliando'), mezzo.get('ztl')]
    })
    
    # --- MODIFICA SCADENZE ---
    with st.expander("✏️ Modifica Scadenze"):
        # Converte le stringhe salvate in oggetti "Data" per precompilare i campi
        def leggi_data(data_str):
            try:
                return datetime.strptime(data_str, "%Y-%m-%d").date()
            except:
                return datetime.now().date()

        with st.form("form_modifica"):
            mc1, mc2 = st.columns(2)
            nuova_ass = mc1.date_input("Assicurazione", value=leggi_data(mezzo.get('assicurazione')))
            nuovo_bollo = mc2.date_input("Bollo", value=leggi_data(mezzo.get('bollo')))
            nuovo_tagl = mc1.date_input("Tagliando", value=leggi_data(mezzo.get('tagliando')))
            nuova_ztl = mc2.date_input("Permesso ZTL", value=leggi_data(mezzo.get('ztl')))
            
            if st.form_submit_button("Aggiorna Scadenze"):
                sheet = get_sheet()
                cell = sheet.find(targa_selezionata, in_column=1)
                
                if cell:
                    row_idx = cell.row
                    intestazioni = [str(x).strip().upper() for x in sheet.row_values(1)]
                    
                    # Sovrascrive le singole celle calcolando la colonna esatta (+1 perché Google Sheets parte da colonna 1)
                    sheet.update_cell(row_idx, intestazioni.index("ASSICURAZIONE") + 1, str(nuova_ass))
                    sheet.update_cell(row_idx, intestazioni.index("BOLLO") + 1, str(nuovo_bollo))
                    sheet.update_cell(row_idx, intestazioni.index("TAGLIANDO") + 1, str(nuovo_tagl))
                    sheet.update_cell(row_idx, intestazioni.index("ZTL") + 1, str(nuova_ztl))
                    
                    st.success("Scadenze aggiornate con successo!")
                    st.rerun()
    
    st.divider()
    c_pdf, c_del = st.columns(2)
    
    with c_pdf:
        pdf_bytes = genera_pdf_scheda(targa_selezionata, mezzo)
        st.download_button("📄 Scarica PDF", pdf_bytes, f"Scheda_{targa_selezionata}.pdf", "application/pdf", type="primary")
        
    with c_del:
        with st.expander("🗑️ Elimina"):
            if st.button("Conferma Eliminazione Definitiva", type="primary"):
                sheet = get_sheet()
                cell = sheet.find(targa_selezionata, in_column=1)
                if cell:
                    sheet.delete_rows(cell.row)
                st.rerun()

