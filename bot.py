import os
import threading
from flask import Flask

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from telegram.constants import ChatPermissions

from groq import Groq

# =========================
# 🔐 ENV VARIABLES
# =========================
TOKEN = os.getenv("TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

# =========================
# 🌐 FLASK SERVER (Render)
# =========================
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is alive"

# =========================
# 🤖 GROQ AI CLIENT
# =========================
client = Groq(api_key=GROQ_KEY)

# =========================
# 🤖 /ai COMMAND
# =========================
async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("Напиши так: /ai привет")
        return

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": text}
            ]
        )

        answer = response.choices[0].message.content
        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"Ошибка ИИ: {e}")

# =========================
# 📜 /rules COMMAND
# =========================
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 ПРАВИЛА ЧАТА RED DEAD REDEMPTION 2 FANDOM CHAT 📌\n\n"
        "1. Запрещается спам в любом виде.\n"
        "Наказание — мут (время зависит от ситуации)\n\n"
        "2. Запрещается 18+ контент (порно/расчлененка)\n"
        "Наказание — бан без права разбана\n\n"
        "3. Запрещены оскорбления религии, семьи, нации\n"
        "Наказание — мут\n\n"
        "4. Запрещены оскорбления админов\n"
        "Наказание — мут или бан\n\n"
        "5. Запрещена реклама без согласования с администрацией\n"
        "Наказание — бан\n\n"
        "6. Запрещён треш-контент\n"
        "Наказание — бан или мут\n\n"
        "7. Не выпрашивать админку\n"
        "Наказание — мут/бан\n\n"
        "8. Запрещено злоупотребление упоминанием владельца\n"
        "Наказание — мут/бан\n\n"
        "📌 В случае бана можно попросить разбан 1 раз,\n"
        "разбан действует всегда, кроме пунктов 2, 4 и 5."
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
# 🚫 AUTO MUTE SYSTEM
# =========================
BAD_TRIGGER = "@dsweroo"

async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    if BAD_TRIGGER in text:
        try:
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=False
                )
            )

            await update.message.reply_text(
                "🚫 Пользователь получил мут за запрещённое слово."
            )

        except Exception as e:
            await update.message.reply_text(f"Ошибка мутa: {e}")

# =========================
# 🤖 BOT SETUP
# =========================
app = Application.builder().token(TOKEN).build()

# commands
app.add_handler(CommandHandler("ai", ai))
app.add_handler(CommandHandler("rules", rules))
app.add_handler(CommandHandler("arbuz", arbuz))
app.add_handler(CommandHandler("ovner", ovner))

# auto mute handler
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

print("🤖 Bot started")

# =========================
# 🚀 RUN (Render friendly)
# =========================
if __name__ == "__main__":
    threading.Thread(
        target=lambda: web_app.run(host="0.0.0.0", port=10000)
    ).start()

    app.run_polling(drop_pending_updates=True)
