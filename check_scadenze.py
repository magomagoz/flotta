import gspread
import json
import smtplib
import os
from datetime import datetime, timedelta
from email.message import EmailMessage

EMAIL_MITTENTE = os.environ.get("EMAIL_MITTENTE")
PASSWORD_MITTENTE = os.environ.get("EMAIL_PASSWORD")

def controlla_e_invia():
    # Legge le credenziali e si collega a Google
    creds_json = os.environ.get("GCP_CREDENTIALS")
    creds_dict = json.loads(creds_json)
    client = gspread.service_account_from_dict(creds_dict)
    sheet = client.open("Database_Flotta").worksheet("Dati")
    
    records = sheet.get_all_records()
    
    oggi = datetime.now().date()
    soglia_avviso = oggi + timedelta(days=7) # Avvisa da 7 giorni prima in poi
    
    for row in records:
        targa = str(row.get("Targa", ""))
        if not targa:
            continue
            
        email_referente = str(row.get("Email", "")).strip()
        
        for doc in ["Assicurazione", "Bollo", "Tagliando", "ZTL"]:
            data_str = str(row.get(doc, ""))
            if not data_str or data_str == "None":
                continue
                
            try:
                data_scadenza = datetime.strptime(data_str, "%Y-%m-%d").date()
            except ValueError:
                continue
            
            # Se la scadenza è a 7 giorni, o già passata
            if data_scadenza <= soglia_avviso:
                # Logica email: se vuoto, usa il mittente
                email_destinatario = email_referente if email_referente else EMAIL_MITTENTE
                invia_email(email_destinatario, targa, doc, data_scadenza)

def invia_email(destinatario, targa, documento, data):
    msg = EmailMessage()
    msg.set_content(f"Attenzione: la scadenza per {documento.upper()} del mezzo {targa} è {data.strftime('%d/%m/%Y')}.")
    msg['Subject'] = f"Avviso Scadenza {documento.capitalize()} - {targa}"
    msg['From'] = EMAIL_MITTENTE
    msg['To'] = destinatario

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_MITTENTE, PASSWORD_MITTENTE)
            server.send_message(msg)
        print(f"Inviato per {targa} ({documento}) a {destinatario}")
    except Exception as e:
        print(f"Errore invio: {e}")

if __name__ == "__main__":
    controlla_e_invia()
