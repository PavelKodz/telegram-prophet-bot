import json
import os
import asyncio
import random
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

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
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")],
        [InlineKeyboardButton("Карта Таро", callback_data="таро")],
        [InlineKeyboardButton("Помощь", callback_data="помощь")]
    ]
    welcome = (
        "*Я — Шёпот сквозь века.*\n\n"
        "Выбери, в какой главе искать знамение.\n"
        "_Для пророчеств или карт из каждой категории доступен 1 выбор раз в сутки._"
    )
    await update.message.reply_text(
        welcome,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Помощь
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "*Как пользоваться Шёпотом сквозь века:*\n\n"
        "— Нажми /start или кнопку снизу, чтобы выбрать главу.\n"
        "— Пророчество доступно *раз в сутки* по каждой теме.\n"
        "— Кнопка 'Карта Таро' выдаёт случайную карту и её значение.\n\n"
        "_Пусть слова откроют путь..._"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Сброс лимитов
async def resetme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_limits[user_id] = {}
    await update.message.reply_text("Лимиты сброшены. Можешь попробовать снова.")

# Обработка кнопок
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = query.data
    user_id = str(query.from_user.id)

    now = datetime.utcnow()
    user_data = user_limits.get(user_id, {})

    if topic == "помощь":
        help_text = (
            "*Как пользоваться Шёпотом сквозь века:*\n\n"
            "— Нажми /start или кнопку снизу, чтобы выбрать главу.\n"
            "— Пророчество доступно *раз в сутки* по каждой теме.\n"
            "— Кнопка 'Карта Таро' выдаёт случайную карту и её значение.\n"
            "— Для сброса лимитов — /resetme.\n\n"
            "_Пусть слова откроют путь..._"
        )
        await query.message.reply_text(help_text, parse_mode="Markdown")
        return

    last_time = user_data.get(topic)
    if last_time and now - last_time < timedelta(days=1):
        await query.message.reply_text("Оракул молчит. Возвращайся завтра.")
        return

    user_data[topic] = now
    user_limits[user_id] = user_data

    if topic == "таро":
        card = random.choice(tarot_cards)
        image = card["image"]
        text = f"*{card['name']}*\n{card['description']}"
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=image,
            caption=text,
            parse_mode="Markdown"
        )
    elif topic in pages:
        phrase = random.choice(pages[topic])
        await query.message.reply_text(f"_Оракул шепчет:_\n\n{phrase}", parse_mode="Markdown")
    else:
        await query.message.reply_text("Неизвестная глава.")

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("resetme", resetme))
    app.add_handler(CallbackQueryHandler(handle_button))

    app.run_polling()