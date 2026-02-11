import telebot
import sqlite3
import imaplib
import email
import re
import time
import threading


import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")


bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 7162087861

# ================== BASE DE DATOS ==================

conn = sqlite3.connect("usuarios.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    chat_id INTEGER PRIMARY KEY,
    autorizado INTEGER DEFAULT 0
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS correos (
    correo TEXT PRIMARY KEY,
    chat_id INTEGER
)
""")
conn.commit()

# ================== REGISTRO ==================

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    cursor.execute("SELECT * FROM usuarios WHERE chat_id=?", (chat_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO usuarios (chat_id, autorizado) VALUES (?, 0)", (chat_id,))
        conn.commit()

        bot.send_message(chat_id,
        "✅ Registrado correctamente\n\n"
        "Tu solicitud fue enviada.\n"
        "Habla con tu distribuidor para ser autorizado.")

    else:
        bot.send_message(chat_id, "Ya estás registrado.")

# ================== INFO CLIENTE ==================

@bot.message_handler(commands=['info'])
def info(message):
    chat_id = message.chat.id

    cursor.execute("SELECT autorizado FROM usuarios WHERE chat_id=?", (chat_id,))
    user = cursor.fetchone()

    if user:
        estado = "Autorizado ✅" if user[0] == 1 else "No autorizado ❌"

        bot.send_message(chat_id,
        f"👤 Tu información\n\n"
        f"🆔 ID: {chat_id}\n"
        f"🔐 Estado: {estado}")
    else:
        bot.send_message(chat_id, "No estás registrado. Usa /start")


# ================== ASIGNAR CORREOS (ADMIN) ==================

@bot.message_handler(commands=['asignar'])
def asignar(message):
    if message.chat.id != ADMIN_ID:
        bot.reply_to(message, "No tienes permiso para usar este comando.")
        return

    try:
        partes = message.text.split()
        correo = partes[1].lower()
        user_id = int(partes[2])

        cursor.execute("INSERT OR REPLACE INTO correos (correo, chat_id) VALUES (?, ?)", (correo, user_id))
        conn.commit()

        bot.send_message(user_id, f"📩 Se te ha asignado el correo:\n{correo}\n\nRecibirás los códigos automáticamente.")
        bot.reply_to(message, f"Correo {correo} asignado correctamente.")

    except:
        bot.reply_to(message, "Uso correcto:\n/asignar correo ID")

# ================== PEDIR CODIGO ==================

def extraer_codigo_de_email(destinatario_buscado):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASS)
        mail.select("inbox")

        result, data = mail.search(None, "ALL")
        ids = data[0].split()

        ultimos = ids[-15:]

        for num in reversed(ultimos):
            result, msg_data = mail.fetch(num, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            recibido = msg.get("Delivered-To")
            if not recibido:
                continue

            if destinatario_buscado.lower() not in recibido.lower():
                continue

            cuerpo = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        cuerpo = part.get_payload(decode=True).decode(errors="ignore")
            else:
                cuerpo = msg.get_payload(decode=True).decode(errors="ignore")

            codigo = re.findall(r"\b\d{4,8}\b", cuerpo)

            if codigo:
                mail.logout()
                return codigo[0]

        mail.logout()
        return None

    except Exception as e:
        print("Error:", e)
        return None


@bot.message_handler(commands=['code'])
def pedir_codigo(message):
    chat_id = message.chat.id

    partes = message.text.split()

    if len(partes) < 2:
        bot.reply_to(message, "Uso:\n/code correo@dominio.com")
        return

    correo = partes[1].lower()

    # verificar usuario autorizado
    cursor.execute("SELECT autorizado FROM usuarios WHERE chat_id=?", (chat_id,))
    user = cursor.fetchone()

    if not user or user[0] == 0:
        bot.reply_to(message, "No estás autorizado.")
        return

    # verificar que el correo sea suyo
    cursor.execute("SELECT chat_id FROM correos WHERE correo=?", (correo,))
    dueño = cursor.fetchone()

    if not dueño or dueño[0] != chat_id:
        bot.reply_to(message, "Ese correo no te pertenece.")
        return

    bot.reply_to(message, "⏳ Buscando código...")

    codigo = extraer_codigo_de_email(correo)

    if codigo:
        bot.send_message(chat_id, f"🔑 Tu código es:\n{codigo}")
    else:
        bot.send_message(chat_id, "No encontré ningún código reciente.")

print("Bot iniciado correctamente...")
bot.infinity_polling()



#
