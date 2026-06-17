import os
import threading
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

# =========================
# 🌐 FLASK (Render alive check)
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
# 🚫 AUTO MODERATION (DELETE + MUTE)
# =========================
OWNER_TRIGGER = "@owner"
BAD_TRIGGER = "@dsweroo"

async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    try:
        # ❌ УДАЛЕНИЕ СООБЩЕНИЯ (если триггер найден)
        if BAD_TRIGGER in text or OWNER_TRIGGER in text:

            await update.message.delete()

            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=False
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
# 🚀 RUN (Render)
# =========================
if __name__ == "__main__":
    threading.Thread(
        target=lambda: web_app.run(host="0.0.0.0", port=10000)
    ).start()

    app.run_polling(drop_pending_updates=True)
