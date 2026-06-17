import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from groq import Groq

# 🔐 ключи из Render
TOKEN = os.getenv("TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")

# 🤖 Groq клиент
client = Groq(api_key=GROQ_KEY)

# 🤖 ИИ команда
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

# 📜 правила
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Правила чата Red Dead Redemption 2 fandom chat 🇷🇺📌\n\n"
        "1. Запрещается спам в любом виде.\n"
        "Наказание — мут (время зависит от ситуации)\n\n"
        "2. Запрещается 18+ контент (порно/расчлененка)\n"
        "Наказание — бан (без права разбана)\n\n"
        "3. Запрещены оскорбления религии, семьи, нации\n"
        "Наказание — мут\n\n"
        "4. Запрещены оскорбления админов\n"
        "Наказание — мут/бан\n\n"
        "5. Запрещена реклама без согласования\n"
        "Наказание — бан\n\n"
        "6. Запрещён треш-контент\n"
        "Наказание — бан (иногда мут)\n\n"
        "7. Не выпрашивать админку\n"
        "Наказание — мут/бан\n\n"
        "8. Запрещено злоупотребление упоминанием владельца\n"
        "Наказание — мут/бан\n\n"
        "📌 В случае бана можно попросить разбан 1 раз,\n"
        "если ошибки не повторяются."
    )

# 🍉 арбуз
async def arbuz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я❤️Арбуза")

# 🚀 запуск бота
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("ai", ai))
app.add_handler(CommandHandler("rules", rules))
app.add_handler(CommandHandler("arbuz", arbuz))

print("🤖 Бот запущен")
app.run_polling()