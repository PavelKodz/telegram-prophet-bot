import json
import os
import asyncio
import random
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
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
    tarot_cards = json.load(file)

# Храним временные лимиты
user_limits = {}

def is_limited(user_id, topic):
    if user_id not in user_limits:
        user_limits[user_id] = {}
    last_time = user_limits[user_id].get(topic)
    if last_time and datetime.now() - last_time < timedelta(days=1):
        return True
    user_limits[user_id][topic] = datetime.now()
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")],
        [InlineKeyboardButton("Карта Таро", callback_data="таро")],
        [InlineKeyboardButton("Помощь", callback_data="help")],
    ]
    welcome = (
        "*Как пользоваться Шёпотом сквозь века:*\n\n"
        "— Нажми /start или кнопку снизу, чтобы выбрать главу.\n"
        "— Пророчество доступно *раз в сутки* по каждой теме.\n"
        "— Кнопка 'Карта Таро' выдаёт случайную карту и её значение.\n"
        "— Для сброса лимитов — /resetme.\n\n"
        "_Пусть слова откроют путь..._"
    )
    await update.message.reply_text(
        welcome,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def prophecy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = query.data.lower()
    user_id = query.from_user.id

    if topic == "help":
        return await help_command(update, context)

    if topic == "таро":
        if is_limited(user_id, "таро"):
            return await query.message.reply_text("Карта Таро уже выдана сегодня. Возвратись завтра.")
        card = random.choice(tarot_cards)
        await query.message.reply_photo(
            photo=card["image_url"],
            caption=f"*{card['name']}*\n{card['description']}",
            parse_mode="Markdown"
        )
        return

    if topic in pages:
        if is_limited(user_id, topic):
            return await query.message.reply_text("Ты уже получал знамение по этой теме сегодня.")
        phrase = random.choice(pages[topic])
        await query.message.reply_text(f"_Оракул шепчет:_\n\n{phrase}")
    else:
        await query.message.reply_text("Неизвестная тема. Попробуй /start.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "*Как пользоваться Шёпотом сквозь века:*\n\n"
        "— Нажми /start, чтобы открыть меню.\n"
        "— Каждую главу можно использовать *раз в сутки*.\n"
        "— Кнопка 'Карта Таро' выдаёт одну карту.\n"
        "— Для сброса лимитов — /resetme.\n"
    )
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(help_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(help_text, parse_mode="Markdown")

async def reset_limits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_limits:
        user_limits[user_id] = {}
    await update.message.reply_text("Лимиты сброшены. Можешь снова искать пророчество.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resetme", reset_limits))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(prophecy))

    app.run_polling()

if __name__ == "__main__":
    main()