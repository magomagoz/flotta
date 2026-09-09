import gspread
import json
import smtplib
import os
from datetime import datetime, timedelta
from email.message import EmailMessage

EMAIL_MITTENTE = os.environ.get("EMAIL_MITTENTE")
PASSWORD_MITTENTE = os.environ.get("EMAIL_PASSWORD")

def parse_data(data_str):
    # Prova a leggere la data in tutti i formati possibili (Americano e Italiano)
    formati = ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"]
    for fmt in formati:
        try:
            return datetime.strptime(data_str, fmt).date()
        except ValueError:
            continue
    return None

def controlla_e_invia():
    print("Avvio controllo scadenze...")
    creds_json = os.environ.get("GCP_CREDENTIALS")
    
    if not creds_json:
        print("ERRORE CRITICO: Il file JSON di Google (GCP_CREDENTIALS) non è presente nei Secrets!")
        return
        
    creds_dict = json.loads(creds_json)
    client = gspread.service_account_from_dict(creds_dict)
    sheet = client.open("Database_Flotta").worksheet("Dati")
    
    records = sheet.get_all_records()
    print(f"Trovati {len(records)} automezzi nel foglio Google.")
    
    oggi = datetime.now().date()
    soglia_avviso = oggi + timedelta(days=7)
    
    for row in records:
        targa = str(row.get("Targa", "")).strip()
        if not targa:
            continue
            
        email_referente = str(row.get("Email", "")).strip()
        print(f"\n--- Analisi Mezzo: {targa} ---")
        
        for doc in ["Assicurazione", "Bollo", "Tagliando", "ZTL"]:
            data_str = str(row.get(doc, "")).strip()
            if not data_str or data_str == "None":
                continue
                
            data_scadenza = parse_data(data_str)
            
            if not data_scadenza:
                print(f"[{doc}] IGNOTO: Il formato della data '{data_str}' non è riconosciuto.")
                continue
            
            if data_scadenza <= soglia_avviso:
                print(f"[{doc}] IN SCADENZA il {data_scadenza}! Preparo invio email...")
                email_destinatario = email_referente if email_referente else EMAIL_MITTENTE
                invia_email(email_destinatario, targa, doc, data_scadenza)
            else:
                print(f"[{doc}] REGOLARE: Scade il {data_scadenza}")

def invia_email(destinatario, targa, documento, data):
    if not EMAIL_MITTENTE or not PASSWORD_MITTENTE:
        print("ERRORE INVIO: Variabili EMAIL_MITTENTE o EMAIL_PASSWORD mancanti nei Secrets.")
        return

    msg = EmailMessage()
    msg.set_content(f"Attenzione: la scadenza per {documento.upper()} del mezzo {targa} è {data.strftime('%d/%m/%Y')}.")
    msg['Subject'] = f"Avviso Scadenza {documento.capitalize()} - {targa}"
    msg['From'] = EMAIL_MITTENTE
    msg['To'] = destinatario

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_MITTENTE, PASSWORD_MITTENTE)
            server.send_message(msg)
        print(f"-> Email spedita con successo a {destinatario}")
    except Exception as e:
        print(f"-> ERRORE durante la spedizione a {destinatario}: {e}")

if __name__ == "__main__":
    controlla_e_invia()
