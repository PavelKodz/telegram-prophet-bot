import json
import asyncio
import random
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Получение токена из переменной окружения
TOKEN = os.environ.get("TOKEN")

# Загрузка пророчеств из JSON-файла
with open("prophecies.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "*Я — Шёпот сквозь века.*\n\n"
        "Здесь ты найдёшь знамения, забытые временем.\n"
        "Каждая глава — ключ к твоей внутренней тьме, вдохновению или философии.\n\n"
        "Новая рукопись пророчеств — страницы, в которых строки скоро пробудятся...\n"
        "_Слушай. Внимай. Каждый зов несёт след._\n\n"
        "Выбери, в какой главе искать знамение:"
    )

    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# Команда /prophecy
async def prophecy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        topic = context.args[0].lower()
        if topic not in pages:
            await update.message.reply_text("Такой главы нет. Попробуй: философия, вдохновение, тьма, булгаков.")
            return

        await update.message.reply_text("Оракул ищет знамение...")
        await asyncio.sleep(0.8)
        await update.message.reply_text(random.choice(pages[topic]))
    except Exception:
        await update.message.reply_text("Неправильный формат. Напиши, например: /prophecy философия")

# Обработка нажатия кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    topic = query.data
    if topic in pages:
        await query.message.reply_text("Оракул ищет знамение...")
        await asyncio.sleep(0.8)
        await query.message.reply_text(random.choice(pages[topic]))
    else:
        await query.message.reply_text("Неизвестная глава.")

# Запуск приложения
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prophecy", prophecy))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()