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
    # Fissiamo la soglia a 7 giorni da oggi
    soglia_avviso = oggi + timedelta(days=7)
    
    for targa, info in dati.items():
        for doc in ["assicurazione", "bollo", "tagliando", "ztl"]:
            # Saltiamo il documento se la data non è stata inserita correttamente
            if not info.get(doc) or info[doc] == "None":
                continue
                
            data_scadenza = datetime.strptime(info[doc], "%Y-%m-%d").date()
            
            # Se la scadenza è uguale o minore a 7 giorni da oggi (incluso se è nel passato)
            if data_scadenza <= soglia_avviso:
                
                # Logica email: usa quella specificata, altrimenti l'amministratore
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
