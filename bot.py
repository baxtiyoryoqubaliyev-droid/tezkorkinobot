import telebot
from telebot import types
import threading
import os
from flask import Flask

TOKEN = "8257995780:AAHzzCV5BFFBhDQ6pzov5D5xBiuYgwwrwkM"
ADMIN_ID = 6776237234  #Telegram user ID
ADMIN_ID = 7361497094  #admin user ID

bot = telebot.TeleBot(TOKEN)

#RENDER UCHUN FLASK PORT
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot ishlayapti!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# ====== KINO BAZASI ======
kinolar = {
    "101": {
        "nom": "Parijdagi sayohat",
        "janr": "Jangari ",
        "yil": "2019",
        "yuklash": 342,
        "created_at": 299,
        "file_id": "BAACAgIAAxkBAAMJaaw_8bTGL46oTQkalHZNLhA6lMAAAjGRAALzjWBJhp58qavQ0-I6BA"
    },
    "102":{
        "nom": "O\'rgimchak odam 2",
        "janr": "Jangari ",
        "yil": "2001",
        "yuklash": 242,
        "created_at": 211,
        "file_id": "BAACAgIAAxkBAAMhaaxFD_T9b7AYWqyGgqHVoVOZuWsAAnyRAALzjWBJfihoWUEx00o6BA"
    }
}

# ====== MENYU ======
def menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🆕 Yangi kinolar", "⭐ Top kinolar")
    keyboard.add("ℹ️ Yordam")
    return keyboard

# ====== START ======
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user.first_name or "foydalanuvchi"
    bot.send_message(
        message.chat.id,
        f"👋 Assalomu alaykum {user}!\n\nKino kodini yuboring.",
        reply_markup=menu()
    )

# ====== ADMIN VIDEO YUBORSA FILE_ID CHIQARISH ======
@bot.message_handler(content_types=['video', 'document'])
def get_file_id(message):
    if message.from_user.id == ADMIN_ID:

        if message.video:
            fid = message.video.file_id
        else:
            fid = message.document.file_id

        bot.reply_to(
            message,
            f"📁 FILE_ID:\n\n{fid}\n\n"
            f"Yangi kino qo‘shish uchun bazaga shu ID ni yozing."
        )

# ====== YANGI KINOLAR ======
def yangi_kinolar():
    sort = sorted(
        kinolar.items(),
        key=lambda x: x[1]["created_at"],
        reverse=True
    )[:5]

    text = "🆕 Oxirgi yuklangan kinolar:\n\n"

    for kod, info in sort:
        text += f"🎬 {info['nom']}\n"
        text += f"🔢 Kod: {kod}\n\n"

    return text

# ====== TOP KINOLAR ======
def top_kinolar():
    sort = sorted(
        kinolar.items(),
        key=lambda x: x[1]["yuklash"],
        reverse=True
    )[:3]

    medals = ["🥇", "🥈", "🥉"]
    text = "⭐ Eng mashhur kinolar:\n\n"

    for i, (kod, info) in enumerate(sort):
        text += f"{medals[i]} {info['nom']}\n"
        text += f"🔢 Kod: {kod}\n"
        text += f"📥 Yuklash: {info['yuklash']}\n\n"

    return text

# ====== XABARLAR ======
@bot.message_handler(func=lambda message: True)
def messages(message):
    text = message.text.strip()

    if text == "🆕 Yangi kinolar":
        bot.send_message(message.chat.id, yangi_kinolar())

    elif text == "⭐ Top kinolar":
        bot.send_message(message.chat.id, top_kinolar())

    elif text == "ℹ️ Yordam":
        bot.send_message(message.chat.id, "Admin: @baxtiyor_off")

    elif text in kinolar:
        kino = kinolar[text]
        kino["yuklash"] += 1

        caption = (
            f"🎬 Kino: {kino['nom']}\n"
            f"📂 Janr: {kino['janr']}\n"
            f"📅 Yil: {kino['yil']}\n"
            f"📥 Yuklash: {kino['yuklash']}"
        )

        bot.send_video(
            message.chat.id,
            kino["file_id"],
            caption=caption,
            protect_content=True
        )

    else:
        bot.send_message(message.chat.id, "❌ Bunday kodli kino topilmadi")

# ====== BOTNI ISHGA TUSHIRISH ======
bot.remove_webhook()
print("Bot ishga tushdi...")
bot.infinity_polling(skip_pending=True)
