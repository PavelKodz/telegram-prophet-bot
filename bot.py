import json
import asyncio
import random
import os
import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Токен
TOKEN = os.environ.get("TOKEN")

# Загрузка пророчеств из JSON-файла
with open("prophecies.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

# Хранилище для отслеживания времени последнего обращения к "Тьма"
last_access = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Я — Шёпот сквозь века. Выбери, в какой главе искать знамение:\n\n"
        "Каждое пророчество — это фраза из бездны времён.\n"
        "Нажми на нужный раздел — и строки, как эхо, пробудятся…"
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
    user_id = query.from_user.id

    # Ограничение для раздела "Тьма" — раз в сутки
    if topic == "тьма":
        now = datetime.datetime.utcnow()
        if user_id in last_access:
            last_time = last_access[user_id]
            if (now - last_time).total_seconds() < 86400:  # 24 часа = 86400 секунд
                await query.edit_message_text("Тьма ещё не пробудилась. Возвратись позже…")
                return
        last_access[user_id] = now

    if topic not in pages:
        await query.edit_message_text("Неверная глава. Попробуй /start.")
        return

    await query.edit_message_text("Оракул ищет знамение...")
    await asyncio.sleep(0.8)
    await query.edit_message_text(random.choice(pages[topic]))

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()