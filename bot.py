import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from flask import Flask, request

# Bot tokeningiz
TOKEN = "8866545271:AAGcXV2z4di-InBp53ZT13vO839mgN79rGM"

# Asosiy admin ID raqami
OWNER_ID = 8372285180

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Xotirada ma'lumotlarni saqlash uchun
CONFIG = {
    "target_group": None
}
user_data = {}

@app.route('/')
def home():
    return "Bot is running with Flask and Webhooks!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


# --- ADMIN PANEL ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != OWNER_ID:
        bot.send_message(message.chat.id, "❌ Kechirasiz, bu buyruq faqat asosiy admin uchun!")
        return
    
    current_group = CONFIG.get("target_group", "Hali ulanmagan ❌")
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Maxfiy guruh usernamesini ulash", callback_data="set_group"))
    markup.add(InlineKeyboardButton("📊 Holatni tekshirish", callback_data="check_status"))
    
    bot.send_message(
        message.chat.id,
        f"👑 **Admin Panel**\n\n"
        f"Joriy maxfiy guruh: `{current_group}`\n\n"
        f"Kerakli amalni tanlang:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "set_group")
def ask_group(call):
    if call.from_user.id != OWNER_ID:
        return
    msg = bot.send_message(
        call.message.chat.id,
        "Iltimos, maxfiy guruhning **usernameni** yuboring (masalan: `@maxfiy_guruh_uz`):\n\n"
        "*(Eslatma: Bot o'sha guruhda bo'lishi va xabar yoza oladigan admin bo'lishi shart!)*",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, save_group)

def save_group(message):
    if message.from_user.id != OWNER_ID:
        return
    group_input = message.text.strip()
    CONFIG["target_group"] = group_input
    bot.send_message(message.chat.id, f"✅ Muvaffaqiyatli saqlandi!\n\nEndi barcha murojaatlar **{group_input}** ga yuboriladi.")

@bot.callback_query_handler(func=lambda call: call.data == "check_status")
def check_status(call):
    if call.from_user.id != OWNER_ID:
        return
    group = CONFIG.get("target_group", "Ulanmagan")
    bot.answer_callback_query(call.id, f"Hozirgi guruh: {group}", show_alert=True)


# --- MUROJAAT JARAYONI (/start va /murojaat) ---

@bot.message_handler(commands=['start', 'murojaat'])
def start_command(message):
    user_data[message.from_user.id] = {}
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔹 So'rovnoma", callback_data="turi_Sorovnoma"))
    markup.add(InlineKeyboardButton("🔹 Vasiylik / homiylik", callback_data="turi_Vasiylik"))
    
    bot.send_message(
        message.chat.id,
        "🔒 **Sizning shaxsingiz sir saqlanishini kafolatlaymiz**\n\n"
        "Murojaat turini tanlang:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("turi_"))
def process_turi(call):
    turi = call.data.replace("turi_", "")
    if turi == "Sorovnoma":
        turi = "So'rovnoma"
    elif turi == "Vasiylik":
        turi = "Vasiylik / homiylik"
        
    user_data[call.from_user.id]["murojaat_turi"] = turi
    
    # O'zbekistonning barcha viloyatlari va respublika tugmalari
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Toshkent shahri", callback_data="vil_Toshkent shahri"),
        InlineKeyboardButton("Toshkent viloyati", callback_data="vil_Toshkent viloyati"),
        InlineKeyboardButton("Farg'ona viloyati", callback_data="vil_Farg'ona viloyati"),
        InlineKeyboardButton("Andijon viloyati", callback_data="vil_Andijon viloyati"),
        InlineKeyboardButton("Namangan viloyati", callback_data="vil_Namangan viloyati"),
        InlineKeyboardButton("Samarqand viloyati", callback_data="vil_Samarqand viloyati"),
        InlineKeyboardButton("Buxoro viloyati", callback_data="vil_Buxoro viloyati"),
        InlineKeyboardButton("Xorazm viloyati", callback_data="vil_Xorazm viloyati"),
        InlineKeyboardButton("Qashqadaryo viloyati", callback_data="vil_Qashqadaryo viloyati"),
        InlineKeyboardButton("Surxondaryo viloyati", callback_data="vil_Surxondaryo viloyati"),
        InlineKeyboardButton("Jizzax viloyati", callback_data="vil_Jizzax viloyati"),
        InlineKeyboardButton("Sirdaryo viloyati", callback_data="vil_Sirdaryo viloyati"),
        InlineKeyboardButton("Navoiy viloyati", callback_data="vil_Navoiy viloyati"),
        InlineKeyboardButton("Qoraqalpog'iston Resp.", callback_data="vil_Qoraqalpog'iston Respublikasi")
    )
    
    bot.edit_message_text(
        f"📌 **Murojaat turi:** {turi}\n\n🌍 **Viloyatni tanlang:**",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("vil_"))
def process_viloyat(call):
    viloyat = call.data.replace("vil_", "")
    user_data[call.from_user.id]["viloyat"] = viloyat
    
    msg = bot.send_message(
        call.message.chat.id,
        f"🌍 **Viloyat:** {viloyat}\n\n"
        f"🏙 **Tumaningiz (yoki shahringiz) nomini matn ko'rinishida yuboring** (masalan: *Chilonzor tumani*):",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_tuman)

def process_tuman(message):
    tuman = message.text
    user_data[message.from_user.id]["tuman"] = tuman
    
    msg = bot.send_message(
        message.chat.id,
        f"🏙 **Tuman:** {tuman}\n\n"
        f"📍 **Mahallangiz (MFY) nomini matn ko'rinishida yuboring** (masalan: *Bunyodkor MFY*):",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_mfy)

def process_mfy(message):
    mfy = message.text
    user_data[message.from_user.id]["mfy"] = mfy
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))
    
    bot.send_message(
        message.chat.id,
        f"📍 **Mahalla (MFY):** {mfy}\n\n"
        f"📲 Bog'lanishimiz uchun pastdagi **'Telefon raqamni yuborish'** tugmasini bosing:",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, process_phone)

def process_phone(message):
    if not message.contact:
        bot.send_message(message.chat.id, "Iltimos, pastdagi tugmani bosib telefon raqamingizni yuboring.")
        bot.register_next_step_handler(message, process_phone)
        return
        
    phone_number = message.contact.phone_number
    user_data[message.from_user.id]["phone"] = phone_number
    
    bot.send_message(
        message.chat.id,
        "✅ Raqam qabul qilindi.\n\n📝 Endi voqea yoki murojaat tafsilotlarini batafsil matn ko'rinishida yuboring:",
        reply_markup=ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(message, process_details)

def process_details(message):
    details = message.text
    user_id = message.from_user.id
    
    if user_id not in user_data:
        user_data[user_id] = {}
        
    user_data[user_id]["details"] = details
    data = user_data[user_id]
    
    murojaat_turi = data.get("murojaat_turi", "Noma'lum")
    viloyat = data.get("viloyat", "Noma'lum")
    tuman = data.get("tuman", "Noma'lum")
    mfy = data.get("mfy", "Noma'lum")
    phone = data.get("phone", "Noma'lum")
    
    user = message.from_user
    user_link = f"<a href='tg://user?id={user.id}'>{user.full_name}</a>"
    username = f"@{user.username}" if user.username else "Mavjud emas"

    report_text = (
        f"🚨 **Yangi Murojaat Keldi!**\n\n"
        f"📌 **Murojaat yo'nalishi:** {murojaat_turi}\n"
        f"🌍 **Viloyat:** {viloyat}\n"
        f"🏙 **Tuman / Shahar:** {tuman}\n"
        f"📍 **Mahalla (MFY):** {mfy}\n"
        f"📞 **Telefon raqami:** +{phone}\n"
        f"📝 **Murojaat tafsiloti:** \n{details}\n\n"
        f"👤 **Foydalanuvchi:** {user_link}\n"
        f"🔗 **Username:** {username}"
    )
    
    target_group = CONFIG.get("target_group")
    
    if not target_group:
        bot.send_message(message.chat.id, "⚠️ Hali admin tomonidan maxfiy guruh ulanmagani uchun murojaat vaqtincha yuborilmadi.")
        return

    try:
        bot.send_message(
            chat_id=target_group,
            text=report_text,
            parse_mode="HTML"
        )
        bot.send_message(message.chat.id, "✅ Murojaatingiz muvaffaqiyatli qabul qilindi va mas'ul guruhga yuborildi!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Xatolik yuz berdi: Guruhga xabar yuborib bo'lmadi.")
        print(f"Xato: {e}")

if __name__ == "__main__":
    RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
    if RENDER_EXTERNAL_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{TOKEN}")
        print(f"Webhook o'rnatildi: {RENDER_EXTERNAL_URL}/{TOKEN}")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
