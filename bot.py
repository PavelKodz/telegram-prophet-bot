import json
import asyncio
import random
import os
import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Токен из переменных среды
TOKEN = os.environ.get("TOKEN")

# Загрузка пророчеств
with open("prophecies.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

# Хранилище для ограничения доступа к "Тьма"
last_access = {}

# Приветствие
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "*Я — Шёпот сквозь века.*\n\n"
        "Этот бот принесёт тебе пророчество из глубины — философии, вдохновения, тьмы и слов Булгакова.\n"
        "Нажми на раздел, чтобы услышать знамение:"
    )

    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    topic = query.data.lower()
    user_id = query.from_user.id

    # Ограничение на "Тьма" раз в сутки
    if topic == "тьма":
        now = datetime.datetime.utcnow()
        if user_id in last_access:
            last_time = last_access[user_id]
            if (now - last_time).total_seconds() < 86400:
                await query.message.reply_text("Тьма уже говорила с тобой сегодня. Возвратись завтра.")
                return
        last_access[user_id] = now

    if topic not in pages:
        await query.message.reply_text("Такой главы нет.")
        return

    await query.message.reply_text("Оракул ищет знамение...")
    await asyncio.sleep(1)
    await query.message.reply_text(random.choice(pages[topic]))

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()