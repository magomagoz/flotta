import json
import smtplib
from datetime import datetime, timedelta
import os
from email.message import EmailMessage

FILE_DATI = "flotta.json"
EMAIL_MITTENTE = os.environ.get("magostinienrico@gmail.com")
PASSWORD_MITTENTE = os.environ.get("Infini@@@y") # Usa una Password per le App se usi Gmail

def controlla_e_invia():
    with open(FILE_DATI, "r") as f:
        dati = json.load(f)
        
    oggi = datetime.now().date()
    target_date = oggi + timedelta(days=7)
    
    for targa, info in dati.items():
        for doc in ["assicurazione", "bollo", "tagliando", "ztl"]:
            data_scadenza = datetime.strptime(info[doc], "%Y-%m-%d").date()
            
            # Se la scadenza è esattamente tra 7 giorni
            if data_scadenza == target_date:
                invia_email(info['email'], targa, doc, data_scadenza)

def invia_email(destinatario, targa, documento, data):
    msg = EmailMessage()
    msg.set_content(f"Attenzione: la scadenza per {documento.upper()} del mezzo {targa} è prevista per il {data.strftime('%d/%m/%Y')}.")
    msg['Subject'] = f"Avviso Scadenza {documento.capitalize()} - {targa}"
    msg['From'] = EMAIL_MITTENTE
    msg['To'] = destinatario

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_MITTENTE, PASSWORD_MITTENTE)
            server.send_message(msg)
        print(f"Email inviata per {targa} ({documento})")
    except Exception as e:
        print(f"Errore invio email: {e}")

if __name__ == "__main__":
    controlla_e_invia()
