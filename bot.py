import json
import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Твой токен
import os
TOKEN = os.environ.get("TOKEN")

# Загрузка пророчеств из JSON-файла
with open("prophecies.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Я — Шёпот сквозь века. Выбери, в какой главе искать знамение:",
        reply_markup=reply_markup
    )

# Команда /prophecy <глава>
async def prophecy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        topic = context.args[0].lower()
        if topic not in pages:
            await update.message.reply_text("Такой главы нет. Попробуй: философия, вдохновение, тьма, булгаков.")
            return

        await update.message.reply_text("Оракул взывает к древним записям...")
        await asyncio.sleep(0.8)
        await update.message.reply_text(random.choice(pages[topic]))

    except Exception:
        await update.message.reply_text("Неправильный формат. Напиши, например: /prophecy философия")

# Обработка нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    topic = query.data.lower()
    if topic not in pages:
        await query.edit_message_text("Неизвестная глава.")
        return

    await query.edit_message_text("Оракул ищет знамение...")
    await asyncio.sleep(0.8)
    await query.message.reply_text(random.choice(pages[topic]))

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prophecy", prophecy))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()