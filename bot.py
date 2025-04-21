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
    tarot_cards = json.load(file)["tarot"]

# Храним временные лимиты
user_limits = {}

# Обновлённая клавиатура
keyboard = [
    [InlineKeyboardButton("Философия", callback_data="философия")],
    [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
    [InlineKeyboardButton("Тьма", callback_data="тьма")],
    [InlineKeyboardButton("Булгаков", callback_data="булгаков")],
    [InlineKeyboardButton("Карта Таро", callback_data="таро")],
    [InlineKeyboardButton("Помощь", callback_data="help")]
]

# Проверка лимита 1 раз в сутки
def can_use(user_id, category):
    now = datetime.now()
    if user_id not in user_limits:
        user_limits[user_id] = {}
    last_used = user_limits[user_id].get(category)
    if not last_used or now - last_used > timedelta(days=1):
        user_limits[user_id][category] = now
        return True
    return False

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "*Я — Шёпот сквозь века.*\n\n"
        "Выбери, в какой главе искать знамение или карту.\n"
        "_Каждая кнопка доступна раз в сутки._\n\n"
        "_Пусть слова откроют путь..._"
    )
    await update.message.reply_text(
        welcome,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Обработка кнопок
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    category = query.data

    if category == "help":
        help_text = (
            "*Как пользоваться Шёпотом сквозь века:*\n\n"
            "— Нажми /start или кнопку снизу, чтобы выбрать главу.\n"
            "— Пророчество доступно *раз в сутки* по каждой теме.\n"
            "— Кнопка 'Карта Таро' выдаёт случайную карту и её значение.\n"
            "— Для сброса лимитов — /resetme\n\n"
            "_Пусть слова откроют путь..._"
        )
        await query.message.reply_text(help_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if category == "таро":
        if not can_use(user_id, "таро"):
            await query.message.reply_text("Карта Таро доступна раз в сутки.", reply_markup=InlineKeyboardMarkup(keyboard))
            return
        card = random.choice(tarot_cards)
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=card["image"],
            caption=f"*{card['name']}*\n{card['description']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if not can_use(user_id, category):
        await query.message.reply_text("Ты уже получал пророчество из этой главы сегодня.", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if category not in pages:
        await query.message.reply_text("Нет такой главы.", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    text = f"_Оракул шепчет:_\n\n{random.choice(pages[category])}"
    await query.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# Сброс лимитов
async def resetme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_limits[user_id] = {}
    await update.message.reply_text("Все лимиты сброшены.")

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resetme", resetme))
    app.add_handler(CallbackQueryHandler(handle_button))

    print("Бот запущен...")
    app.run_polling()