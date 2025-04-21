import json
import asyncio
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, timedelta

TOKEN = os.environ.get("TOKEN")

with open("prophecies.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

user_limits = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Я — *Шёпот сквозь века*. \n"
        "Выбери, в какой главе искать знамение:\n"
    )
    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def prophecy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = context.args[0].lower() if context.args else None
    if topic not in pages:
        await update.message.reply_text("Такой главы нет. Попробуй: философия, вдохновение, тьма, булгаков.")
        return
    await update.message.reply_text("Оракул ищет знамение...")
    await asyncio.sleep(0.8)
    await update.message.reply_text(random.choice(pages[topic]))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = query.data
    user_id = query.from_user.id
    now = datetime.now()
    last_used = user_limits.get((user_id, topic))

    if last_used and now - last_used < timedelta(days=1):
        await query.edit_message_text("Ты уже спрашивал это сегодня. Возвращайся завтра.")
        return

    user_limits[(user_id, topic)] = now
    await query.edit_message_text("Оракул ищет знамение...")
    await asyncio.sleep(0.8)
    await query.message.reply_text(random.choice(pages[topic]))

async def reset_limits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    for key in list(user_limits):
        if key[0] == user_id:
            del user_limits[key]
    await update.message.reply_text("Ограничения сброшены.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "*Как пользоваться Шёпотом сквозь века:*\n"
        "— Нажми /start, чтобы открыть главы.\n"
        "— Нажми на одну из кнопок: _Философия_, _Вдохновение_, _Тьма_, _Булгаков_.\n"
        "— Ты получишь пророчество из выбранной главы.\n"
        "⚠️ *Ограничение:* каждую из глав можно выбрать только раз в сутки.\n"
        "Для тестов доступна команда /resetme.\n"
        "_Пусть слова откроют путь..._"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prophecy", prophecy))
    app.add_handler(CommandHandler("resetme", reset_limits))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()