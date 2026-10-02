import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup,
    InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Tokeningiz
TOKEN = "8866545271:AAGcXV2z4di-InBp53ZT13vO839mgN79rGM"

# ⚠️ O'ZINGIZNING TELEGRAM ID RAQAMINGIZNI SHU YERGA YOZING (Asosiy admin uchun)
OWNER_ID = 512345678  # Buni o'z ID raqamingizga o'zgartiring!

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Xotirada guruh ID / username ni saqlash uchun
CONFIG = {
    "target_group": None
}


# FSM holatlari
class MurojaatForm(StatesGroup):
    turi = State()
    mfy = State()
    phone = State()
    details = State()


class AdminStates(StatesGroup):
    waiting_for_group = State()


# --- ADMIN PANEL ---
@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Kechirasiz, bu buyruq faqat asosiy admin uchun!")
        return

    current_group = CONFIG.get("target_group", "Hali ulanmagan ❌")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Maxfiy guruhni ulash/o'zgartirish", callback_data="set_group")],
        [InlineKeyboardButton(text="📊 Holatni tekshirish", callback_data="check_status")]
    ])

    await message.answer(
        f"👑 **Admin Panelga Xush Kelibsiz!**\n\n"
        f"Joriy murojaat yuboriladigan guruh: `{current_group}`\n\n"
        f"Kerakli amalni tanlang:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "set_group")
async def ask_group(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != OWNER_ID:
        return
    await callback.message.answer(
        "Iltimos, maxfiy guruhning **usernameni** yuboring (masalan: `@maxfiy_guruh_uz`):\n\n"
        "*(Eslatma: Bot o'sha guruhda bo'lishi va admin huquqiga ega bo'lishi shart!)*"
    )
    await state.set_state(AdminStates.waiting_for_group)
    await callback.answer()


@dp.message(AdminStates.waiting_for_group)
async def save_group(message: Message, state: FSMContext):
    if message.from_user.id != OWNER_ID:
        return

    group_input = message.text.strip()
    CONFIG["target_group"] = group_input

    await message.answer(f"✅ Muvaffaqiyatli saqlandi!\n\nEndi barcha murojaatlar **{group_input}** ga yuboriladi.")
    await state.clear()


@dp.callback_query(F.data == "check_status")
async def check_status(callback: CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        return
    group = CONFIG.get("target_group", "Ulanmagan")
    await callback.answer(f"Hozirgi guruh: {group}", show_alert=True)


# --- FOYDALANUVCHI QISMI (Murojaat jarayoni) ---

@dp.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔹 So'rovnoma", callback_data="turi_Sorovnoma")],
        [InlineKeyboardButton(text="🔹 Vasiylik / homiylik", callback_data="turi_Vasiylik")]
    ])
    await message.answer(
        "🔒 **Sizning shaxsingiz sir saqlanishini kafolatlaymiz**\n\n"
        "Murojaat turini tanlang:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await state.set_state(MurojaatForm.turi)


@dp.callback_query(MurojaatForm.turi, F.data.startswith("turi_"))
async def process_turi(callback: CallbackQuery, state: FSMContext):
    turi = callback.data.replace("turi_", "")
    if turi == "Sorovnoma":
        turi = "So'rovnoma"
    elif turi == "Vasiylik":
        turi = "Vasiylik / homiylik"

    await state.update_data(murojaat_turi=turi)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Bobur MFY", callback_data="mfy_Bobur MFY")],
        [InlineKeyboardButton(text="Yoshlik MFY", callback_data="mfy_Yoshlik MFY")],
        [InlineKeyboardButton(text="Gulzor MFY", callback_data="mfy_Gulzor MFY")],
        [InlineKeyboardButton(text="Istiqlol MFY", callback_data="mfy_Istiqlol MFY")]
    ])

    await callback.message.edit_text(
        f"📌 **Murojaat turi:** {turi}\n\n📍 **MFYni (hududni) tanlang:**",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await state.set_state(MurojaatForm.mfy)
    await callback.answer()


@dp.callback_query(MurojaatForm.mfy)
async def process_mfy(callback: CallbackQuery, state: FSMContext):
    mfy = callback.data.replace("mfy_", "")
    await state.update_data(mfy=mfy)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await callback.message.answer(
        f"📍 **Tanlangan MFY:** {mfy}\n\n"
        f"📲 Iltimos, bog'lanishimiz uchun pastdagi **'Telefon raqamni yuborish'** tugmasini bosing:",
        reply_markup=keyboard
    )
    await state.set_state(MurojaatForm.phone)
    await callback.answer()


@dp.message(MurojaatForm.phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await state.update_data(phone=phone_number)

    await message.answer("✅ Raqam qabul qilindi.", reply_markup=ReplyKeyboardRemove())
    await message.answer(
        "📝 Endi voqea yoki murojaat tafsilotlarini batafsil matn ko'rinishida yuboring:"
    )
    await state.set_state(MurojaatForm.details)


@dp.message(MurojaatForm.details)
async def process_details(message: Message, state: FSMContext):
    details = message.text
    data = await state.get_data()

    murojaat_turi = data.get("murojaat_turi")
    mfy = data.get("mfy")
    phone = data.get("phone")

    user = message.from_user
    user_link = f"<a href='tg://user?id={user.id}'>{user.full_name}</a>"
    username = f"@{user.username}" if user.username else "Mavjud emas"

    report_text = (
        f"🚨 **Yangi Murojaat Keldi!**\n\n"
        f"📌 **Murojaat yo'nalishi:** {murojaat_turi}\n"
        f"📍 **Hudud (MFY):** {mfy}\n"
        f"📞 **Telefon raqami:** +{phone}\n"
        f"📝 **Murojaat matni / Voqea tafsiloti:** \n{details}\n\n"
        f"👤 **Foydalanuvchi:** {user_link}\n"
        f"🔗 **Username:** {username}"
    )

    target_group = CONFIG.get("target_group")

    if not target_group:
        await message.answer(
            "⚠️ Hali admin tomonidan maxfiy guruh ulanmagani uchun murojaat vaqtincha yuborilmadi. Iltimos keyinroq urinib ko'ring.")
        await state.clear()
        return

    try:
        await bot.send_message(
            chat_id=target_group,
            text=report_text,
            parse_mode="HTML"
        )
        await message.answer("✅ Murojaatingiz muvaffaqiyatli qabul qilindi va mas'ul guruhga yuborildi!")
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: Guruhga xabar yuborib bo'lmadi.")
        print(f"Xato: {e}")

    await state.clear()


async def main():
    logging.basicConfig(level=logging.INFO)
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())s