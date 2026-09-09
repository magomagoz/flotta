import json
import smtplib
from datetime import datetime, timedelta
import os
from email.message import EmailMessage

FILE_DATI = "flotta.json"
EMAIL_MITTENTE = os.environ.get("EMAIL_MITTENTE")
PASSWORD_MITTENTE = os.environ.get("EMAIL_PASSWORD") # Usa una Password per le App se usi Gmail

def controlla_e_invia():
    with open(FILE_DATI, "r") as f:
        dati = json.load(f)
        
    oggi = datetime.now().date()
    target_date = oggi + timedelta(days=7)
    
    for targa, info in dati.items():
        for doc in ["assicurazione", "bollo", "tagliando", "ztl"]:
            data_scadenza = datetime.strptime(info[doc], "%Y-%m-%d").date()
            
            if data_scadenza == target_date:
                # LOGICA DI FALLBACK: Se l'email non c'è o è vuota, usa quella dei Secrets
                email_destinatario = info.get('email', '').strip()
                if not email_destinatario:
                    email_destinatario = EMAIL_MITTENTE
                
                invia_email(email_destinatario, targa, doc, data_scadenza)

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
