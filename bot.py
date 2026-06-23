import os
import time
import re
import asyncio
from datetime import datetime, timedelta

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

if not TOKEN:
    raise ValueError("TOKEN is not set")
if not GROQ_KEY:
    raise ValueError("GROQ_KEY is not set")

# =========================
# 🤖 GROQ AI CLIENT
# =========================
client = Groq(api_key=GROQ_KEY)

# =========================
# ⏳ COOLDOWN SYSTEM
# =========================
COOLDOWN = 40
user_cooldown = {}

def clean_cooldowns():
    now = time.time()
    for user_id in list(user_cooldown.keys()):
        if now - user_cooldown[user_id] > 60:
            del user_cooldown[user_id]

# =========================
# 🧹 TEXT NORMALIZE
# =========================
def normalize(text: str):
    text = text.lower()
    return re.sub(r"[^\wа-я0-9]", "", text)

# =========================
# 🤖 /ai COMMAND
# =========================
async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    clean_cooldowns()

    user = update.effective_user
    if not user:
        return

    now = time.time()
    last = user_cooldown.get(user.id)

    # cooldown check (ОДИН РАЗ!)
    if last and now - last < COOLDOWN:
        remaining = int(COOLDOWN - (now - last))
        await update.message.reply_text(
            f"⏳ Подожди {remaining} сек перед следующим запросом"
        )
        return

    text = " ".join(context.args).strip()

    if not text:
        await update.message.reply_text("Напиши: /ai привет")
        return

    user_cooldown[user.id] = now

    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": text}],
        )

        await update.message.reply_text(
            response.choices[0].message.content
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
        
# =========================
# 📜 /rules COMMAND (ПОЛНЫЕ ПРАВИЛА)
# =========================
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 ПРАВИЛА ЧАТА 📌\n\n"

        "1. Запрещается спам в любом виде.\n"
        "Наказание: мут (время зависит от ситуации)\n\n"

        "2. Запрещается порно, расчленёнка, шок-контент.\n"
        "Наказание: бан без права разбана\n\n"

        "3. Запрещаются оскорбления религии, нации, семьи.\n"
        "Наказание: мут или бан\n\n"

        "4. Запрещаются оскорбления администраторов.(шуточные не считаются.) \n"
        "Наказание: мут или бан\n\n"

        "5. Запрещена реклама без согласования с владельцем.\n"
        "Наказание: бан\n\n"

        "6. Запрещён шок-контент (расчленёнка, гениталии и т.д.).\n"
        "Наказание: бан\n\n"

        "7. Запрещено выпрашивать админку.\n"
        "Наказание: мут → затем бан\n\n"

        "8. Запрещено упоминать юз владельца чата.\n"
        "Наказание: мут или бан\n\n"

        "9. В случае бана можно попросить разбан 1 раз, если нарушение не повторяется.(кроме пунктов 2,5,6.)"
    )

# =========================
# 🍉 /arbuz COMMAND
# =========================
async def arbuz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я ❤️ Арбуза")

# =========================
# 👑 /ovner COMMAND
# =========================
async def ovner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Овнер, я ❤️ тебя")

# =========================
# 🎬 /z VIDEO COMMAND
# =========================
async def z(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("video_2026-06-18_21-17-27.mp4", "rb") as v:
        await update.message.reply_video(video=v)

# =========================
# 🚫 AUTO MODERATION
# =========================
BAD_TRIGGER = "dsweroo"

async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = normalize(update.message.text)

    if BAD_TRIGGER in text:
        await update.message.delete()

        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=update.message.from_user.id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_invite_users=False
            )
        )

        await context.bot.send_message(
            update.effective_chat.id,
            "🚫 Сообщение удалено. Пользователь получил мут."
        )

# =========================
# 🔇 /mute COMMAND
# =========================
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):

    admins = await context.bot.get_chat_administrators(update.effective_chat.id)
    admin_ids = [a.user.id for a in admins]

    if update.effective_user.id not in admin_ids:
        await update.message.reply_text("❌ Только админы могут использовать.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Ответь на пользователя.")
        return

    if not context.args:
        await update.message.reply_text("Пример: /mute 10m")
        return

    target = update.message.reply_to_message.from_user
    duration = context.args[0]

    if duration.endswith("m"):
        delta = timedelta(minutes=int(duration[:-1]))
    elif duration.endswith("h"):
        delta = timedelta(hours=int(duration[:-1]))
    elif duration.endswith("d"):
        delta = timedelta(days=int(duration[:-1]))
    else:
        await update.message.reply_text("10m / 2h / 1d")
        return

    until = datetime.now() + delta

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        target.id,
        ChatPermissions(
            can_send_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_invite_users=False
        ),
        until_date=until
    )

    await update.message.reply_text(
        f"🔇 {target.first_name} замучен на {duration}"
    )

# =========================
# 🤖 BOT SETUP
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("ai", ai))
app.add_handler(CommandHandler("rules", rules))
app.add_handler(CommandHandler("arbuz", arbuz))
app.add_handler(CommandHandler("ovner", ovner))
app.add_handler(CommandHandler("z", z))
app.add_handler(CommandHandler("mute", mute))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

print("🤖 Bot started")

if __name__ == "__main__":
    app.run_polling()