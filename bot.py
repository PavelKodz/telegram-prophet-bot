import json
import asyncio
import random
import os
import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Загружаем токен
TOKEN = os.environ.get("TOKEN")

# Загружаем пророчества
with open("prophecies.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

# Файл для хранения информации о пользователях
USERS_FILE = "users_data.json"

# Функция загрузки
def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Функция сохранения
def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Приветствие
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "*Я — Шёпот сквозь века.*\n\n"
        "Ты можешь получить одно знамение из каждой главы в сутки.\n"
        "Выбери тему пророчества:"
    )

    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    topic = query.data.lower()
    user_id = str(query.from_user.id)
    today = str(datetime.date.today())

    users = load_users()

    if user_id not in users:
        users[user_id] = {}

    if topic in users[user_id] and users[user_id][topic] == today:
        await query.message.reply_text(f"Ты уже получил знамение из главы «{topic.title()}» сегодня. Попробуй завтра.")
        return

    users[user_id][topic] = today
    save_users(users)

    if topic not in pages:
        await query.message.reply_text("Такой главы нет.")
        return

    await query.message.reply_text("Оракул ищет знамение...")
    await asyncio.sleep(1)
    await query.message.reply_text(random.choice(pages[topic]))

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()