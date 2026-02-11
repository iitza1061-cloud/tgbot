import telebot
import imaplib
import email
import re
import time
import threading

TOKEN = "8317770610:AAHDKymWIBHegGaOtANgZ5ixtDmlKYOYBEo"
GMAIL_USER = "itzishpp@gmail.com"
GMAIL_PASS = "oxarribadfeudelepdlp​​​"
CHAT_ID = 123456789

bot = telebot.TeleBot(TOKEN)

def buscar_codigo():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASS)
        mail.select("inbox")

        result, data = mail.search(None, "UNSEEN")

        for num in data[0].split():
            result, msg_data = mail.fetch(num, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            cuerpo = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        cuerpo = part.get_payload(decode=True).decode(errors="ignore")
            else:
                cuerpo = msg.get_payload(decode=True).decode(errors="ignore")

            codigo = re.findall(r"\b\d{4,6}\b", cuerpo)

            if codigo:
                return codigo[0]

        return None
    except:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 Sistema de códigos activo")

def monitorear():
    ultimo = None
    while True:
        codigo = buscar_codigo()
        if codigo and codigo != ultimo:
            bot.send_message(CHAT_ID, f"🔑 Código: {codigo}")
            ultimo = codigo
        time.sleep(10)

threading.Thread(target=monitorear).start()

print("Bot corriendo...")
bot.infinity_polling()
