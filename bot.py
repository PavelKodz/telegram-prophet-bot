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
with open("tarot.json", "r", encoding="utf-8") as file:
    tarot_cards = json.load(file)

# Храним временные лимиты
user_limits = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")],
        [InlineKeyboardButton("Карта Таро", callback_data="таро")],
    ]
    welcome = (
        "Я — *Шёпот сквозь века*.\n\n"
        "Выбери, в какой главе искать знамение:\n"
        "_(одно пророчество или карта из каждой категории доступно раз в сутки)_"
    )
    await update.message.reply_text(welcome, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    topic = query.data
    await query.answer()

    now = datetime.now()
    if user_id not in user_limits:
        user_limits[user_id] = {}

    last_used = user_limits[user_id].get(topic)
    if last_used and now - last_used < timedelta(days=1):
        await query.message.reply_text("Сегодня ты уже заглядывал в эту главу. Возвратись завтра.")
        return

    user_limits[user_id][topic] = now

    if topic == "таро":
        card = random.choice(tarot_cards)
        await query.message.reply_photo(
            photo=card["image_url"],
            caption=f"*{card['name']}*\n_{card['description']}_",
            parse_mode="Markdown"
        )
    elif topic in pages:
        await query.message.reply_text("Оракул ищет знамение...")
        await asyncio.sleep(1.2)
        prophecy = random.choice(pages[topic])
        await query.message.reply_text(prophecy)
    else:
        await query.message.reply_text("Неизвестная категория.")

async def prophecy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        topic = context.args[0].lower()
        if topic not in pages:
            await update.message.reply_text("Такой главы нет. Попробуй философия, тьма, вдохновение, булгаков.")
            return

        await update.message.reply_text("Оракул обращается к древним записям...")
        await asyncio.sleep(0.8)
        await update.message.reply_text(random.choice(pages[topic]))

    except Exception:
        await update.message.reply_text("Неправильный формат. Пример: /prophecy философия")

async def resetme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_limits:
        del user_limits[user_id]
    await update.message.reply_text("Ограничения сброшены. Можно снова заглядывать в каждую главу.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "*Как пользоваться Шёпотом сквозь века:*\n"
        "— Нажми /start, чтобы открыть главы.\n"
        "— Выбери одну из кнопок: _Философия_, _Вдохновение_, _Тьма_, _Булгаков_, _Карта Таро_.\n"
        "— Ты получишь пророчество или карту.\n"
        "⚠️ *Ограничение:* каждую из кнопок можно использовать только раз в сутки.\n"
        "— Для тестов есть команда /resetme\n"
        "_Пусть слова откроют путь..._"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prophecy", prophecy_command))
    app.add_handler(CommandHandler("resetme", resetme))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.run_polling()