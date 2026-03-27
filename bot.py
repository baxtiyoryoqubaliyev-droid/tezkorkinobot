import telebot
from telebot import types
import json
import os
import time

TOKEN = "8257995780:AAHzzCV5BFFBhDQ6pzov5D5xBiuYgwwrwkM"
ADMIN_IDS = [6776237234, 7361497094 ]    #Telegram user ID

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

DATA_FILE = "kinolar.json"

# Adminning hozirgi yuklash holatini saqlash uchun
admin_states = {}


# =========================
# JSON bilan ishlash
# =========================
def load_movies():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_movies(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


kinolar = load_movies()


# =========================
# Menyu
# =========================
def main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🆕 Yangi kinolar", "⭐ Top kinolar")
    keyboard.add("ℹ️ Yordam")
    return keyboard


# =========================
# Yordamchi funksiyalar
# =========================
def is_admin(user_id):
    return user_id in ADMIN_IDS


def get_next_code():
    if not kinolar:
        return "1001"

    max_code = 1000
    for code in kinolar.keys():
        if str(code).isdigit():
            max_code = max(max_code, int(code))

    return str(max_code + 1)


def get_new_movies_text():
    if not kinolar:
        return "🆕 Hozircha kinolar yo‘q."

    sorted_movies = sorted(
        kinolar.items(),
        key=lambda x: x[1].get("created_at", 0),
        reverse=True
    )[:5]

    text = "🆕 Oxirgi yuklangan 5 ta kino:\n\n"
    for code, info in sorted_movies:
        text += f"🎬 {info.get('nom', 'Noma’lum')}\n"
        text += f"🔢 Kod: {code}\n\n"
    return text


def get_top_movies_text():
    if not kinolar:
        return "⭐ Hozircha kinolar yo‘q."

    sorted_movies = sorted(
        kinolar.items(),
        key=lambda x: x[1].get("yuklash", 0),
        reverse=True
    )[:3]

    medals = ["🥇", "🥈", "🥉"]
    text = "⭐ Eng ko‘p yuklangan top 3 kino:\n\n"

    for i, (code, info) in enumerate(sorted_movies):
        text += f"{medals[i]} {info.get('nom', 'Noma’lum')}\n"
        text += f"🔢 Kod: {code}\n"
        text += f"📥 Yuklash: {info.get('yuklash', 0)}\n\n"

    return text


# =========================
# Start
# =========================
@bot.message_handler(commands=["start"])
def start_handler(message):
    first_name = message.from_user.first_name or "foydalanuvchi"
    text = (
        f"👋 Assalomu alaykum, <b>{first_name}</b>!\n\n"
        f"🎬 Botimizga xush kelibsiz.\n"
        f"📩 Kino kodini yuboring."
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu())


# =========================
# Admin ID ko'rish
# =========================
@bot.message_handler(commands=["id"])
def id_handler(message):
    bot.reply_to(message, f"Sizning ID: <code>{message.from_user.id}</code>")


# =========================
# Admin yangi kino qo'shish
# =========================
@bot.message_handler(commands=["addkino"])
def add_movie_handler(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Siz admin emassiz.")
        return

    admin_states[message.from_user.id] = {
        "step": "waiting_file"
    }

    bot.reply_to(
        message,
        "🎬 Yangi kino qo‘shish boshlandi.\n\n"
        "Avval kinoni video yoki document qilib yuboring.\n"
        "Bekor qilish uchun: /cancel"
    )


@bot.message_handler(commands=["cancel"])
def cancel_handler(message):
    if message.from_user.id in admin_states:
        del admin_states[message.from_user.id]
        bot.reply_to(message, "❌ Jarayon bekor qilindi.")
    else:
        bot.reply_to(message, "Hozir faol jarayon yo‘q.")


# =========================
# Admin video yuborsa
# =========================
@bot.message_handler(content_types=["video"])
def video_handler(message):
    user_id = message.from_user.id

    # 1) Agar admin oddiy video yuborsa -> file_id ko'rsatadi
    if is_admin(user_id):
        bot.reply_to(
            message,
            f"🎬 VIDEO FILE_ID:\n\n<code>{message.video.file_id}</code>"
        )

    # 2) Agar admin addkino jarayonida bo'lsa -> saqlash jarayonini davom ettiradi
    if user_id in admin_states and admin_states[user_id].get("step") == "waiting_file":
        admin_states[user_id]["file_id"] = message.video.file_id
        admin_states[user_id]["file_type"] = "video"
        admin_states[user_id]["step"] = "waiting_name"

        bot.reply_to(
            message,
            "✅ Video qabul qilindi.\n\n"
            "Endi kino nomini yuboring."
        )


# =========================
# Admin document yuborsa
# =========================
@bot.message_handler(content_types=["document"])
def document_handler(message):
    user_id = message.from_user.id

    if is_admin(user_id):
        bot.reply_to(
            message,
            f"📁 DOCUMENT FILE_ID:\n\n<code>{message.document.file_id}</code>"
        )

    if user_id in admin_states and admin_states[user_id].get("step") == "waiting_file":
        admin_states[user_id]["file_id"] = message.document.file_id
        admin_states[user_id]["file_type"] = "document"
        admin_states[user_id]["step"] = "waiting_name"

        bot.reply_to(
            message,
            "✅ Fayl qabul qilindi.\n\n"
            "Endi kino nomini yuboring."
        )


# =========================
# Matnli xabarlar
# =========================
@bot.message_handler(func=lambda message: True, content_types=["text"])
def text_handler(message):
    user_id = message.from_user.id
    text = message.text.strip()

    # =========================
    # Admin qo'shish jarayoni
    # =========================
    if user_id in admin_states:
        step = admin_states[user_id].get("step")

        if step == "waiting_file":
            bot.reply_to(
                message,
                "Avval kinoni video yoki document qilib yuboring.\nBekor qilish uchun: /cancel"
            )
            return

        elif step == "waiting_name":
            admin_states[user_id]["nom"] = text
            admin_states[user_id]["step"] = "waiting_genre"
            bot.reply_to(message, "📂 Endi kino janrini yuboring.")
            return

        elif step == "waiting_genre":
            admin_states[user_id]["janr"] = text
            admin_states[user_id]["step"] = "waiting_year"
            bot.reply_to(message, "📅 Endi kino yilini yuboring.")
            return

        elif step == "waiting_year":
            movie_data = admin_states[user_id]

            code = get_next_code()

            kinolar[code] = {
                "nom": movie_data["nom"],
                "janr": movie_data["janr"],
                "yil": text,
                "yuklash": 0,
                "created_at": int(time.time()),
                "file_id": movie_data["file_id"],
                "file_type": movie_data["file_type"]
            }

            save_movies(kinolar)
            del admin_states[user_id]

            bot.reply_to(
                message,
                f"✅ Kino saqlandi.\n\n"
                f"🎬 Nomi: {kinolar[code]['nom']}\n"
                f"📂 Janr: {kinolar[code]['janr']}\n"
                f"📅 Yil: {kinolar[code]['yil']}\n"
                f"🔢 Kod: {code}"
            )
            return

    # =========================
    # Menyu tugmalari
    # =========================
    if text == "🆕 Yangi kinolar":
        bot.send_message(message.chat.id, get_new_movies_text())
        return

    if text == "⭐ Top kinolar":
        bot.send_message(message.chat.id, get_top_movies_text())
        return

    if text == "ℹ️ Yordam":
        bot.send_message(message.chat.id, "Admin: @bakhtiyor_of")
        return

    # =========================
    # Kino kodi bilan qidirish
    # =========================
    if text in kinolar:
        kino = kinolar[text]
        kino["yuklash"] = kino.get("yuklash", 0) + 1
        save_movies(kinolar)

        caption = (
            f"🎬 Kino: {kino.get('nom', 'Noma’lum')}\n"
            f"📂 Janr: {kino.get('janr', 'Noma’lum')}\n"
            f"📅 Yil: {kino.get('yil', 'Noma’lum')}\n"
            f"📥 Yuklash: {kino.get('yuklash', 0)}"
        )

        file_type = kino.get("file_type", "video")

        if file_type == "document":
            bot.send_document(
                message.chat.id,
                kino["file_id"],
                caption=caption,
                protect_content=True
            )
        else:
            bot.send_video(
                message.chat.id,
                kino["file_id"],
                caption=caption,
                protect_content=True
            )
        return

    bot.send_message(message.chat.id, "❌ Bunday kodli kino topilmadi.")


# =========================
# Ishga tushirish
# =========================
bot.remove_webhook()
print("Bot ishga tushdi...")
bot.infinity_polling(skip_pending=True)
