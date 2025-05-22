import smtplib
import os
from email.message import EmailMessage
from datetime import datetime
import json
import logging

# Konfiguráció beolvasása
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

felado = config['email_felado']
jelszo = config['email_jelszo']


def kuld_email(cimzett, file_data, file_name, mime_type):
    if not file_data:
        logging.info("Nincs adat, email nem kerül kiküldésre.")
        return

    msg = EmailMessage()
    today = datetime.now().strftime("%Y-%m-%d")
    msg['Subject'] = f'CNC Adatszűrés - {today}'
    msg['From'] = felado
    msg['To'] = cimzett
    msg.set_content('Csatolva találod a frissített megmunkálási adatokat.')

    if mime_type:
        maintype, subtype = mime_type.split('/', 1)
    else:
        maintype, subtype = 'application', 'octet-stream'
        
    msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)

    try:
        with smtplib.SMTP('smtp.freemail.hu', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(felado, jelszo)
            smtp.send_message(msg)
        logging.info("Email sikeresen elküldve.")
    except Exception as e:
        logging.error(f"Hiba az email küldésnél: {str(e)}")
