import telebot
import sqlite3
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

#
