import json
import os
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")

# Загружаем пророчества
with open("prophecies.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

# Загружаем карты Таро
with open("tarot_cards_full.json", "r", encoding="utf-8") as file:
    tarot_cards = json.load(file)["tarot"]

# Храним временные лимиты
user_limits = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="Философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="Вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="Тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="Булгаков")],
        [InlineKeyboardButton("Карта Таро", callback_data="таро")],
        [InlineKeyboardButton("Помощь", callback_data="помощь")]
    ]

    welcome_text = """*Шёпот сквозь века*

_Выбери главу или карту. Пророчество доступно раз в сутки._
"""
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Команда /resetme
async def reset_limits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_limits:
        del user_limits[user_id]
    await update.message.reply_text("Лимиты сброшены. Можешь попробовать снова.")

# Обработка кнопок
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.lower()
    user_id = query.from_user.id
    now = datetime.now()

    await query.answer()

    if data == "помощь":
        help_text = """*Как пользоваться Шёпотом сквозь века:*

— Нажми /start или кнопку снизу, чтобы выбрать главу.
— Пророчество доступно *раз в сутки* по каждой теме.
— Кнопка 'Карта Таро' выдаёт случайную карту и её значение.
— Для сброса лимитов — /resetme.

_Пусть слова откроют путь..._"""
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=help_text,
            parse_mode="Markdown"
        )
        return

    elif data == "таро":
        if user_id in user_limits and "таро" in user_limits[user_id]:
            if now < user_limits[user_id]["таро"] + timedelta(days=1):
                await context.bot.send_message(
                    chat_id=query.message.chat.id,
                    text="Оракул молчит. Возвращайся завтра."
                )
                return

        card = random.choice(tarot_cards)
        caption = f"*{card['name']}*\n{card['description']}"
        if user_id not in user_limits:
            user_limits[user_id] = {}
        user_limits[user_id]["таро"] = now

        await context.bot.send_photo(
            chat_id=query.message.chat.id,
            photo=card["image"],
            caption=caption,
            parse_mode="Markdown"
        )
        return

    # Пророчества
    if data in pages:
        if user_id in user_limits and data in user_limits[user_id]:
            if now < user_limits[user_id][data] + timedelta(days=1):
                await context.bot.send_message(
                    chat_id=query.message.chat.id,
                    text="Оракул молчит. Возвращайся завтра."
                )
                return

        phrase = random.choice(pages[data])
        if user_id not in user_limits:
            user_limits[user_id] = {}
        user_limits[user_id][data] = now

        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"*Оракул шепчет:*\n\n{phrase}",
            parse_mode="Markdown"
        )
    else:
        available = ", ".join(pages.keys())
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"Такой главы нет.Попробуй: {available}."
        )

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resetme", reset_limits))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    print("Бот запущен.")
    app.run_polling()