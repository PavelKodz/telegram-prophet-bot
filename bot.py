Pavel, [21.04.2025 2:48]
import json
import random
import asyncio
import os
import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Загружаем токен
TOKEN = os.environ.get("TOKEN")

# Загружаем пророчества
with open("prophecies.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

# Загружаем карты Таро
with open("tarot_cards.json", "r", encoding="utf-8") as f:
    tarot_cards = json.load(f)["tarot"]

# Словари для отслеживания лимитов
user_limits = {}
tarot_limits = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "*Я — Шёпот сквозь века.*\n\n"
        "Ты можешь получить одно знамение из каждой главы и одну карту Таро в сутки.\n"
        "Выбери путь:"
    )

    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")],
        [InlineKeyboardButton("Карта Таро", callback_data="таро")]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = query.data
    user_id = str(query.from_user.id)
    now = datetime.datetime.utcnow()
    today = now.date()

    # === Таро ===
    if topic == "таро":
        last_tarot = tarot_limits.get(user_id)
        if last_tarot == today:
            await query.message.reply_text("Карта Таро уже была открыта сегодня. Возвратись завтра.")
            return

        tarot_limits[user_id] = today
        card = random.choice(tarot_cards)
        await query.message.reply_photo(
            photo=card["image"],
            caption=f"*{card['name']}*\n{card['description']}",
            parse_mode="Markdown"
        )
        return

    # === Пророчества ===
    last_used = user_limits.get(user_id, {}).get(topic)
    if last_used == today:
        await query.message.reply_text(f"Ты уже получал знамение из главы «{topic.title()}» сегодня.")
        return

    user_limits.setdefault(user_id, {})[topic] = today

    if topic not in pages:
        await query.message.reply_text("Такой главы не существует.")
        return

    await query.message.reply_text("Оракул ищет знамение...")
    await asyncio.sleep(1)
    await query.message.reply_text(random.choice(pages[topic]))

# Сброс лимитов для тестов
async def resetme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_limits.pop(user_id, None)
    tarot_limits.pop(user_id, None)
    await update.message.reply_text("Все лимиты сброшены.")

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*Как пользоваться Шёпотом сквозь века:*\n"
        "— Используй /start для выбора главы.\n"
        "— Доступна 1 карта Таро и 1 знамение по каждой главе в сутки.\n"
        "— /resetme сбрасывает ограничения (для тестов).\n"
        "— /help — это ты уже и так знаешь.\n"
        "_Пусть сужденное отзовётся..._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# Запуск бота
if name == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resetme", resetme))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

Pavel, [21.04.2025 2:52]
import json
import random
import asyncio
import os
import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Токен из переменной окружения
TOKEN = os.environ.get("TOKEN")

# Загрузка пророчеств
with open("prophecies.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

# Загрузка карт Таро
with open("tarot_cards.json", "r", encoding="utf-8") as f:
    tarot_cards = json.load(f)["tarot"]

# Словари лимитов
user_limits = {}
tarot_limits = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "*Я — Шёпот сквозь века.*\n\n"
        "Ты можешь получить одно знамение из каждой главы и одну карту Таро в сутки.\n"
        "Выбери путь:"
    )
    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")],
        [InlineKeyboardButton("Карта Таро", callback_data="таро")],
        [InlineKeyboardButton("Помощь", callback_data="help")]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = query.data
    user_id = str(query.from_user.id)
    now = datetime.datetime.utcnow()
    today = now.date()

    # Помощь
    if topic == "help":
        help_text = (
            "*Как пользоваться Шёпотом сквозь века:*\n"
            "— Выбери главу и получи пророчество.\n"
            "— Нажми «Карта Таро» для случайной карты (раз в сутки).\n"
            "— Команда /resetme сбрасывает лимиты (для тестов).\n"
            "— Команда /help показывает это объяснение.\n"
            "_Слушай и внимай знамениям._"
        )
        await query.message.reply_text(help_text, parse_mode="Markdown")
        return

    # Таро
    if topic == "таро":
        last_tarot = tarot_limits.get(user_id)
        if last_tarot == today:
            await query.message.reply_text("Карта Таро уже была открыта сегодня. Возвратись завтра.")
            return

        tarot_limits[user_id] = today
        card = random.choice(tarot_cards)
        await query.message.reply_photo(
            photo=card["image"],
            caption=f"*{card['name']}*\n{card['description']}",
            parse_mode="Markdown"
        )
        return

    # Пророчества
    last_used = user_limits.get(user_id, {}).get(topic)
    if last_used == today:
        await query.message.reply_text(f"Ты уже получал знамение из главы «{topic.title()}» сегодня.")
        return

    user_limits.setdefault(user_id, {})[topic] = today

    if topic not in pages:
        await query.message.reply_text("Такой главы не существует.")
        return

    await query.message.reply_text("Оракул ищет знамение...")
    await asyncio.sleep(1)
    await query.message.reply_text(random.choice(pages[topic]))

# /resetme — сброс лимитов
async def resetme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_limits.pop(user_id, None)
    tarot_limits.pop(user_id, None)
    await update.message.reply_text("Все лимиты сброшены.")

# /help — текст
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*Как пользоваться Шёпотом сквозь века:*\n"
        "— Используй /start для выбора главы.\n"
        "— Доступна 1 карта Таро и 1 знамение по каждой главе в сутки.\n"
        "— /resetme — сбрасывает ограничения.\n"
        "_Пусть сужденное отзовётся..._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.

Pavel, [21.04.2025 2:52]
add_handler(CommandHandler("resetme", resetme))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()