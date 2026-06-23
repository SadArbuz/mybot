import os
import threading
import requests
import time
import re
import asyncio
COOLDOWN = 40

from datetime import datetime, timedelta
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
web_app = Flask(name)

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
# 🤖 AI COOLDOWN SYSTEM
# =========================
user_cooldown = {}
COOLDOWN = 40
COOLDOWN_LIFETIME = 60  # через сколько удалять запись

def clean_cooldowns():
    now = time.time()
    to_delete = []

    for user_id, last_time in user_cooldown.items():
        if now - last_time > COOLDOWN_LIFETIME:
            to_delete.append(user_id)

    for user_id in to_delete:
        del user_cooldown[user_id]


# =========================
# 🤖 /ai COMMAND
# =========================
async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clean_cooldowns()

    if not update.message:
        return

    user = update.effective_user
    if not user:
        return

    user_id = user.id
    now = time.time()

    # cooldown check per user
    last_used = user_cooldown.get(user_id)

    if last_used and (now - last_used < COOLDOWN):
        remaining = int(COOLDOWN - (now - last_used))
        await update.message.reply_text(
            f"⏳ Подожди {remaining} сек перед следующим запросом"
        )
        return

    user_cooldown[user_id] = now

    text = " ".join(context.args).strip()

    if not text:
        await update.message.reply_text("Напиши так: /ai привет")
        return

    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": text}
            ],
        )

        answer = response.choices[0].message.content
        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка ИИ: {e}")

# =========================
# 📜 /rules COMMAND (ТВОИ ПРАВИЛА 1 В 1)
# =========================
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
    "📌 Правила чата Red Dead Redemption 2 fandom chat 🇷🇺📌\n\n"
    "1. Запрещается спам в любом виде. \n"
    "Наказание — Мут (время зависит от ситуации)\n\n"
    "2. Запрещается порно/расчлененка\n"
    "Наказание — Бан (без права разбана)\n\n"
    "3. Запрещается оскорбление религии, семьи, нации\n"
    "Наказание — Мут ( время зависит от ситуации)\n\n"
    "4. Запрещается оскорбление админов ( легкие, шуточные не учитываются)\n"

"Наказание — Мут/Бан (зависит от ситуации)\n\n"
    "5. Запрещается реклама (в любом виде) без согласования с владельцем чата \n"
    "Наказание — Бан\n\n"
    "6. Запрещается отправка треш кружочков (не стоит отправлять расчлененку илм свои/чужие гениталии)\n"
    "Наказние — Бан (в редких случаях мут)\n\n"
    "7. Не рекомендуется выпрашивать админку у администрации\n"
    "Наказание — 5 предупреждений в виде мута, после бан на определенный срок\n\n"
    "8. Запрещается отправка юза владельца чата.\n"
    "Наказание — Мут/Бан (зависит от ситуации)\n\n"
    "\nВ случаи бана одного из участников, его друзья могут попросить разбана только 1 раз при условии, что участник получивший бан не будет повторять своих ошибок\n\n"
    "(правило работает всегда кроме пунктов: 2;5;6)"
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
# 🎬 /z VIDEO COMMAND
# =========================
async def z(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_video(
        video=open("video_2026-06-18_21-17-27.mp4", "rb")
    )

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
                    can_send_polls=False,
                    can_send_other_messages=False,
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
# 🔇 /mute COMMAND
# =========================
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):

    admins = await context.bot.get_chat_administrators(
        update.effective_chat.id
    )

    admin_ids = [admin.user.id for admin in admins]

    if update.effective_user.id not in admin_ids:
        await update.message.reply_text(
            "❌ Команда доступна только администраторам."
        )
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❌ Ответь на сообщение пользователя.\nПример: /mute 10m"
        )
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Укажи время.\nПример: /mute 10m"
        )
        return

    target = update.message.reply_to_message.from_user
    duration = context.args[0].lower()

    try:
        if duration.endswith("m"):
            delta = timedelta(minutes=int(duration[:-1]))

        elif duration.endswith("h"):
            delta = timedelta(hours=int(duration[:-1]))

        elif duration.endswith("d"):
            delta = timedelta(days=int(duration[:-1]))

        else:
            await update.message.reply_text(
                "❌ Используй:\n10m = минуты\n2h = часы\n7d = дни"
            )
            return

        until_date = datetime.now() + delta

target_member = await context.bot.get_chat_member(
            update.effective_chat.id,
            target.id
        )

        if target_member.status in ["administrator", "creator"]:
            await update.message.reply_text(
                "❌ Нельзя замутить администратора."
            )
            return

        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target.id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_invite_users=False
            ),
            until_date=until_date
        )

        await update.message.reply_text(
            f"🔇 {target.first_name} получил мут на {duration}"
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка: {e}"
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

# =========================
# 🚀 RUN (RENDER)
# =========================
if name == "main":
    threading.Thread(target=run_web).start()
    threading.Thread(target=keep_alive_ping).start()

    app.run_polling(drop_pending_updates=True)