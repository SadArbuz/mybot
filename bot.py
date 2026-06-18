import os
import threading
import requests
import time
import re

from flask import Flask
from telegram import Update, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

from groq import Groq

# =========================
# 🔐 ENV VARIABLES
# =========================
TOKEN = os.getenv("TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
RENDER_URL = os.getenv("RENDER_URL")
if not RENDER_URL:
    print("⚠️ WARNING: RENDER_URL is not set (keep-alive will not work)")

if not TOKEN:
    raise ValueError("TOKEN is not set")
if not GROQ_KEY:
    raise ValueError("GROQ_KEY is not set")

# =========================
# 🌐 FLASK (KEEP ALIVE SERVER)
# =========================
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is alive"

def run_web():
    web_app.run(
        host="0.0.0.0",
        port=10000,
        debug=False,
        use_reloader=False
    )

def keep_alive_ping():
    while True:
        try:
            if RENDER_URL:
                requests.get(RENDER_URL, timeout=10)
                print("🔄 Keep-alive ping sent")
        except Exception as e:
            print(f"Ping error: {e}")

        time.sleep(240)

# =========================
# 🤖 GROQ AI CLIENT
# =========================
client = Groq(api_key=GROQ_KEY)

def normalize(text: str):
    text = text.lower()
    text = re.sub(r"[^\wа-я0-9]", "", text)
    return text

# =========================
# 🤖 /ai COMMAND
# =========================
import asyncio  # если ещё не добавил сверху файла

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("Напиши так: /ai привет")
        return

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                client.chat.completions.create,
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": text}],
            ),
            timeout=15
        )

        await update.message.reply_text(response.choices[0].message.content)

    except asyncio.TimeoutError:
        await update.message.reply_text("⏳ AI не успел ответить за 15 секунд")

    except Exception as e:
        await update.message.reply_text(f"Ошибка ИИ: {e}")

# =========================
# 📜 /rules COMMAND (ТВОИ ПРАВИЛА 1 В 1)
# =========================
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 ПРАВИЛА ЧАТА RED DEAD REDEMPTION 2 FANDOM CHAT 📌\n\n"
        "1. Запрещается спам в любом виде.\n"
        "Наказание — мут\n\n"
        "2. Запрещается 18+ контент\n"
        "Наказание — бан без права разбана\n\n"
        "3. Оскорбления запрещены\n"
        "Наказание — мут\n\n"
        "4. Оскорбления админов запрещены\n"
        "Наказание — мут/бан\n\n"
        "5. Реклама запрещена\n"
        "Наказание — бан\n\n"
        "6. Треш-контент запрещён\n"
        "Наказание — бан\n\n"
        "7. Не выпрашивать админку\n"
        "Наказание — мут\n\n"
        "8. Запрещено использование юзера владельца (упоминание, тег, спам)\n"
        "Наказание — мут/бан\n\n"
        "📌 В случае бана можно попросить разбан 1 раз,\n"
        "разбан действует всегда, кроме пунктов 2, 4 и 5, а также при серьёзных или массовых нарушениях."
    )

# =========================
# 🍉 /arbuz COMMAND
# =========================
async def arbuz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я❤️Арбуза")

# =========================
# 👑 /ovner COMMAND
# =========================
async def ovner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("овелкэодмэн я❤️тебя")

# =========================
# 🚫 AUTO MODERATION
# =========================
BAD_TRIGGER = "dsweroo"

async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = normalize(update.message.text)
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id

    try:
        if BAD_TRIGGER in text:

            await update.message.delete()

            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_add_web_page_previews=False,
                    can_invite_users=False
                )
            )

            await context.bot.send_message(
                chat_id=chat_id,
                text="🚫 Сообщение удалено. Пользователь получил мут."
            )

    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Ошибка: {e}"
        )

# =========================
# 🤖 BOT SETUP
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("ai", ai))
app.add_handler(CommandHandler("rules", rules))
app.add_handler(CommandHandler("arbuz", arbuz))
app.add_handler(CommandHandler("ovner", ovner))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

print("🤖 Bot started")

# =========================
# 🚀 RUN (RENDER)
# =========================
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    threading.Thread(target=keep_alive_ping).start()

    app.run_polling(drop_pending_updates=True)
