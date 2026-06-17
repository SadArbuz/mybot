import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from groq import Groq

# =========================
# 🔐 ENV VARIABLES
# =========================
TOKEN = os.getenv("TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

# =========================
# 🌐 FLASK SERVER
# =========================
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is alive"

# =========================
# 🤖 AI CLIENT
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

        await update.message.reply_text(response.choices[0].message.content)

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
# 🍉 /arbuz
# =========================
async def arbuz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я❤️Арбуза")

# =========================
# 👑 /ovner
# =========================
async def ovner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("овелкэодмэн я❤️тебя")

# =========================
# BOT SETUP
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("ai", ai))
app.add_handler(CommandHandler("rules", rules))
app.add_handler(CommandHandler("arbuz", arbuz))
app.add_handler(CommandHandler("ovner", ovner))

print("🤖 Bot started")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    import asyncio

    def run_flask():
        web_app.run(host="0.0.0.0", port=10000)

    threading.Thread(target=run_flask).start()

    print("🤖 Bot is running...")
    app.run_polling(drop_pending_updates=True)
