import json
import random
import asyncio
import os
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")

# Загрузка пророчеств из файла
with open("prophecies.json", "r", encoding="utf-8") as file:
    pages = json.load(file)

# Хранилище лимитов (в памяти, при перезапуске очищается)
user_limits = {}

# Время блокировки (сутки)
LIMIT_DURATION = timedelta(hours=24)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Я — Шёпот сквозь века. Выбери, в какой главе искать знамение:"
    )
    keyboard = [
        [InlineKeyboardButton("Философия", callback_data="философия")],
        [InlineKeyboardButton("Вдохновение", callback_data="вдохновение")],
        [InlineKeyboardButton("Тьма", callback_data="тьма")],
        [InlineKeyboardButton("Булгаков", callback_data="булгаков")],
        [InlineKeyboardButton("Карта Таро", callback_data="таро")],
        [InlineKeyboardButton("Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Обработка нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = query.data
    user_id = str(query.from_user.id)

    now = datetime.now()
    last_used = user_limits.get(user_id, {}).get(topic)

    if topic == "help":
        await query.message.reply_text(
            "*Как пользоваться Шёпотом сквозь века:*
"
            "— Нажми /start, чтобы открыть главы
"
            "— Нажми на одну из кнопок: _Философия_, _Вдохновение_, _Тьма_, _Булгаков_, _Карта Таро_
"
            "— Ты получишь пророчество или карту
"
            "⚠️ *Ограничение:* каждую главу можно вызывать раз в 24 часа
"
            "_Пусть слова откроют путь..._", parse_mode="Markdown")
        return

    if topic not in pages:
        await query.message.reply_text("Такой главы нет.")
        return

    if last_used and now - last_used < LIMIT_DURATION:
        hours_left = int((LIMIT_DURATION - (now - last_used)).total_seconds() // 3600)
        await query.message.reply_text(f"Ты уже обращался к этой главе. Попробуй снова через {hours_left} ч.")
        return

    user_limits.setdefault(user_id, {})[topic] = now

    # Таро особый случай
    if topic == "таро":
        card = random.choice(pages["таро"])
        await query.message.reply_photo(photo=card["image"], caption=card["text"])
    else:
        await query.message.reply_text(random.choice(pages[topic]))

# Сброс лимитов
async def reset_limits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_limits[user_id] = {}
    await update.message.reply_text("Лимиты сброшены.")

# Основной запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resetme", reset_limits))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()