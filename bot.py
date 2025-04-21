import json
import os
import asyncio
import random
from datetime import datetime, timedelta
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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

# Время блокировки — 24 часа
LIMIT_TIME = timedelta(hours=24)

# Универсальное меню
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")],
        [InlineKeyboardButton("Карта Таро", callback_data="таро")],
        [InlineKeyboardButton("Помощь", callback_data="help")]
    ])

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*Я — Шёпот сквозь века.*\n\n"
        "Выбери, в какой главе искать знамение.\n"
        "_Каждая кнопка доступна раз в сутки._"
    )
    await update.message.reply_text(
        text,
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

# Обработка нажатий на кнопки
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    topic = query.data
    now = datetime.now()

    await query.answer()

    if topic == "help":
        await query.edit_message_text(
            "*Как пользоваться Шёпотом сквозь века:*\n\n"
            "— Нажми /start или кнопку снизу, чтобы выбрать главу.\n"
            "— Пророчество доступно *раз в сутки* по каждой теме.\n"
            "— Кнопка 'Карта Таро' выдаёт случайную карту и её значение.\n\n"
            "_Пусть слова откроют путь..._",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
        return

    # Проверка лимитов
    if user_id not in user_limits:
        user_limits[user_id] = {}
    last_used = user_limits[user_id].get(topic)
    if last_used and now - last_used < LIMIT_TIME:
        remaining = LIMIT_TIME - (now - last_used)
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        await query.edit_message_text(
            f"Ты уже получил пророчество из «{topic}».\n"
            f"Попробуй снова через {hours} ч {minutes} мин.",
            reply_markup=get_main_menu()
        )
        return

    user_limits[user_id][topic] = now

    # Обработка кнопки Таро
    if topic == "таро":
        card = random.choice(tarot_cards)
        text = f"*{card['name']}*\n_{card['description']}_"
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=get_main_menu()
        )
        return

    # Пророчество
    if topic in pages:
        phrase = random.choice(pages[topic])
        await query.edit_message_text(
            f"_Оракул шепчет:_\n\n{phrase}",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
    else:
        await query.edit_message_text(
            "Эта глава пока пуста.",
            reply_markup=get_main_menu()
        )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Как пользоваться Шёпотом сквозь века:*\n\n"
        "— Нажми /start, чтобы открыть меню.\n"
        "— Каждую главу можно использовать *раз в сутки*.\n"
        "— Кнопка 'Карта Таро' выдаёт одну карту.\n"
        "— Для сброса лимитов — /resetme.",
        parse_mode="Markdown"
    )

# Сброс лимитов
async def resetme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_limits[user_id] = {}
    await update.message.reply_text("Лимиты сброшены.")

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("resetme", resetme))
    app.add_handler(CallbackQueryHandler(handle_button))

    app.run_polling()